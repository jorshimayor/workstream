"""Tests for the shared external service adapter construction convention."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import cast

import pytest

from app.interfaces.external_services import (
    AdapterConstructor,
    DuplicateExternalServiceProviderError,
    ExternalServiceAdapterError,
    ExternalServiceAdapterFactory,
    ExternalServiceAdapterIdentity,
    ExternalServiceAdapterIdentityMismatchError,
    ExternalServiceConfigurationError,
    ExternalServiceProtocolError,
    ExternalServiceUnavailableError,
    UnknownExternalServiceProviderError,
)


class ExampleAdapter:
    """Minimal typed capability adapter used by the focused factory tests."""

    def __init__(self, capability_key: str, provider_key: str) -> None:
        """Create an adapter under one immutable identity."""
        self._identity = ExternalServiceAdapterIdentity(capability_key, provider_key)

    @property
    def identity(self) -> ExternalServiceAdapterIdentity:
        """Return the adapter identity."""
        return self._identity


def test_adapter_identity_is_immutable_and_canonical() -> None:
    """Identity accepts bounded lowercase keys and cannot drift after creation."""
    identity = ExternalServiceAdapterIdentity("artifact_store", "s3_compatible")

    assert identity.capability_key == "artifact_store"
    assert identity.provider_key == "s3_compatible"
    with pytest.raises(FrozenInstanceError):
        identity.provider_key = "local"  # type: ignore[misc]

    for invalid_key in ("", "Uppercase", "has-dash", " has_space", "a" * 65, 7):
        with pytest.raises(ExternalServiceConfigurationError) as error:
            ExternalServiceAdapterIdentity(cast(str, invalid_key), "local")
        assert str(error.value) == "external_service_configuration_invalid"
        assert error.value.identity is None


def test_root_errors_are_stable_bounded_and_secret_safe() -> None:
    """Shared errors expose only stable facts and sanitized adapter identity."""
    identity = ExternalServiceAdapterIdentity("artifact_store", "local")
    errors = (
        ExternalServiceAdapterError(identity),
        ExternalServiceConfigurationError(identity),
        ExternalServiceUnavailableError(identity),
        ExternalServiceProtocolError(identity),
    )

    assert [(error.code, error.category, error.retryable) for error in errors] == [
        ("external_service_error", "external_service", False),
        ("external_service_configuration_invalid", "configuration", False),
        ("external_service_unavailable", "availability", True),
        ("external_service_protocol_invalid", "protocol", False),
    ]
    for error in errors:
        assert error.identity == identity
        assert str(error) == error.code
        assert set(vars(error)) == {"identity"}


def test_root_errors_drop_noncanonical_identity_without_retaining_it() -> None:
    """Runtime misuse cannot attach a secret-bearing object to a shared error."""
    secret = "token=do-not-retain"

    class SecretBearingIdentity:
        def __repr__(self) -> str:
            return secret

    for malformed_identity in (secret, SecretBearingIdentity()):
        error = ExternalServiceConfigurationError(
            cast(ExternalServiceAdapterIdentity, malformed_identity)
        )

        assert error.identity is None
        assert secret not in str(error)
        assert secret not in repr(error)
        assert set(vars(error)) == {"identity"}


def test_factory_registers_and_constructs_one_typed_provider() -> None:
    """An explicit provider registration constructs an identity-matched adapter."""
    factory = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")
    factory.register("local", lambda: ExampleAdapter("artifact_store", "local"))

    first = factory.create("local")
    second = factory.create("local")

    assert factory.capability_key == "artifact_store"
    assert first.identity == ExternalServiceAdapterIdentity("artifact_store", "local")
    assert second.identity == first.identity
    assert second is not first


def test_factories_are_instance_local() -> None:
    """Registration in one capability factory never creates global state."""
    first = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")
    second = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")
    first.register("local", lambda: ExampleAdapter("artifact_store", "local"))

    assert first.create("local").identity.provider_key == "local"
    with pytest.raises(UnknownExternalServiceProviderError):
        second.create("local")


def test_duplicate_and_unknown_providers_fail_closed() -> None:
    """Duplicate ownership and unknown selection have stable configuration errors."""
    factory = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")

    def constructor() -> ExampleAdapter:
        return ExampleAdapter("artifact_store", "local")

    factory.register("local", constructor)

    with pytest.raises(DuplicateExternalServiceProviderError) as duplicate:
        factory.register("local", constructor)
    with pytest.raises(UnknownExternalServiceProviderError) as unknown:
        factory.create("s3_compatible")

    assert duplicate.value.identity == ExternalServiceAdapterIdentity("artifact_store", "local")
    assert duplicate.value.code == "external_service_provider_duplicate"
    assert unknown.value.identity == ExternalServiceAdapterIdentity(
        "artifact_store", "s3_compatible"
    )
    assert unknown.value.code == "external_service_provider_unknown"


def test_factory_rejects_invalid_registration_without_retaining_input() -> None:
    """Malformed capability/provider inputs never enter the registry or an error."""
    with pytest.raises(ExternalServiceConfigurationError) as capability_error:
        ExternalServiceAdapterFactory[ExampleAdapter]("invalid provider")
    assert capability_error.value.identity is None

    factory = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")
    with pytest.raises(ExternalServiceConfigurationError) as provider_error:
        factory.register("secret=value", lambda: ExampleAdapter("artifact_store", "local"))
    with pytest.raises(ExternalServiceConfigurationError):
        factory.register(
            "local",
            cast(AdapterConstructor[ExampleAdapter], None),
        )
    with pytest.raises(ExternalServiceConfigurationError) as create_error:
        factory.create("secret=value")
    assert provider_error.value.identity is None
    assert create_error.value.identity is None


def test_factory_rejects_identity_mismatch() -> None:
    """A constructor cannot register one provider and return another identity."""
    factory = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")
    factory.register("local", lambda: ExampleAdapter("artifact_store", "s3_compatible"))

    with pytest.raises(ExternalServiceAdapterIdentityMismatchError) as error:
        factory.create("local")

    assert error.value.identity == ExternalServiceAdapterIdentity("artifact_store", "local")
    assert str(error.value) == "external_service_adapter_identity_mismatch"


def test_factory_maps_untrusted_constructor_failure_without_retaining_it() -> None:
    """Unexpected constructor errors become stable errors without secret chaining."""
    secret = "access_key=do-not-retain"

    def broken_constructor() -> ExampleAdapter:
        raise RuntimeError(secret)

    factory = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")
    factory.register("local", broken_constructor)

    with pytest.raises(ExternalServiceConfigurationError) as captured:
        factory.create("local")

    error = captured.value
    assert error.identity == ExternalServiceAdapterIdentity("artifact_store", "local")
    assert secret not in str(error)
    assert secret not in repr(error)
    assert error.__cause__ is None
    assert error.__context__ is None
    assert set(vars(error)) == {"identity"}


def test_factory_maps_identity_validation_failure_without_retaining_it() -> None:
    """Secret-bearing identity access failures cannot escape factory construction."""
    secret = "password=do-not-retain"

    class BrokenIdentityAdapter:
        @property
        def identity(self) -> ExternalServiceAdapterIdentity:
            raise RuntimeError(secret)

    factory = ExternalServiceAdapterFactory[BrokenIdentityAdapter]("artifact_store")
    factory.register("local", BrokenIdentityAdapter)

    with pytest.raises(ExternalServiceConfigurationError) as captured:
        factory.create("local")

    error = captured.value
    assert error.identity == ExternalServiceAdapterIdentity("artifact_store", "local")
    assert secret not in str(error)
    assert secret not in repr(error)
    assert error.__cause__ is None
    assert error.__context__ is None
    assert set(vars(error)) == {"identity"}


def test_factory_preserves_already_sanitized_root_errors() -> None:
    """Capability constructors may return one stable shared failure unchanged."""
    identity = ExternalServiceAdapterIdentity("artifact_store", "local")
    expected = ExternalServiceUnavailableError(identity)

    def unavailable_constructor() -> ExampleAdapter:
        raise expected

    factory = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")
    factory.register("local", unavailable_constructor)

    with pytest.raises(ExternalServiceUnavailableError) as captured:
        factory.create("local")
    assert captured.value is expected


def test_factory_preserves_root_error_only_after_identity_is_sanitized() -> None:
    """A malformed shared error cannot smuggle constructor secrets through the factory."""
    secret = "credential=do-not-retain"
    expected = ExternalServiceConfigurationError(
        cast(ExternalServiceAdapterIdentity, secret)
    )

    def invalid_configuration() -> ExampleAdapter:
        raise expected

    factory = ExternalServiceAdapterFactory[ExampleAdapter]("artifact_store")
    factory.register("local", invalid_configuration)

    with pytest.raises(ExternalServiceConfigurationError) as captured:
        factory.create("local")

    assert captured.value is expected
    assert captured.value.identity is None
    assert secret not in str(captured.value)
    assert secret not in repr(captured.value)
