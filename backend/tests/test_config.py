from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.adapters.auth.flow import FlowAuthVerifier
from app.core.auth import clear_auth_verifier_cache, get_auth_verifier
from app.core.config import Settings, get_settings
from app.main import create_app


def test_default_settings_are_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WORKSTREAM_DATABASE_URL", raising=False)
    monkeypatch.delenv("WORKSTREAM_DEV_AUTH_TOKEN", raising=False)

    settings = Settings()

    assert settings.app_name == "Workstream API"
    assert settings.environment == "production"
    assert settings.auth_provider == "flow"
    assert settings.database_url is None
    assert settings.dev_auth_token is None


def test_settings_reject_unknown_environment() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="unknown")


def _flow_settings(**overrides) -> Settings:
    values = {
        "environment": "test",
        "auth_provider": "flow",
        "token_issuer": "https://issuer.example.test",
        "token_jwks_url": "https://issuer.example.test/jwks",
        "token_algorithms": "RS256",
        "token_introspection_mode": "disabled",
        "token_introspection_disabled_reason": "short-lived issuer tokens",
    }
    values.update(overrides)
    return Settings(**values)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"token_issuer": None}, "WORKSTREAM_TOKEN_ISSUER"),
        ({"token_jwks_url": "http://issuer.example.test/jwks"}, "canonical HTTPS"),
        ({"token_algorithms": "HS256"}, "unsupported algorithm"),
        ({"token_algorithms": "RS256,ES256"}, "mix key families"),
        ({"token_introspection_mode": None}, "INTROSPECTION_MODE"),
        ({"token_introspection_disabled_reason": None}, "DISABLED_REASON"),
        ({"token_header_max_bytes": 8_192, "token_max_bytes": 4_096}, "header limit"),
        ({"token_issuer": "https://auth.flow.local"}, "placeholder issuer"),
        ({"required_human_scope": "  "}, "HUMAN_SCOPE"),
        ({"required_service_scope": "two scopes"}, "SERVICE_SCOPE"),
    ],
)
def test_flow_verifier_rejects_incomplete_or_unsafe_configuration(
    overrides: dict,
    message: str,
) -> None:
    with pytest.raises(RuntimeError, match=message):
        FlowAuthVerifier(_flow_settings(**overrides))


def test_required_introspection_requires_endpoint_credentials() -> None:
    with pytest.raises(RuntimeError, match="INTROSPECTION_URL"):
        FlowAuthVerifier(
            _flow_settings(
                token_introspection_mode="required",
                token_introspection_disabled_reason=None,
            )
        )


@pytest.mark.parametrize(
    "field_name",
    ["token_introspection_client_id", "token_introspection_client_secret"],
)
def test_required_introspection_rejects_whitespace_credentials(field_name: str) -> None:
    values = {
        "token_introspection_mode": "required",
        "token_introspection_disabled_reason": None,
        "token_introspection_url": "https://introspection.example.test/introspect",
        "token_introspection_client_id": "client-id",
        "token_introspection_client_secret": "client-secret",
    }
    values[field_name] = "  "
    with pytest.raises(RuntimeError, match=field_name.removeprefix("token_").upper()):
        FlowAuthVerifier(_flow_settings(**values))


def test_numeric_security_bounds_are_validated() -> None:
    with pytest.raises(ValidationError):
        Settings(token_jwks_max_keys=101)


def test_production_flow_verifier_is_process_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKSTREAM_AUTH_PROVIDER", "flow")
    monkeypatch.setenv("WORKSTREAM_ENVIRONMENT", "production")
    monkeypatch.setenv("WORKSTREAM_TOKEN_ISSUER", "https://issuer.example.test")
    monkeypatch.setenv("WORKSTREAM_TOKEN_JWKS_URL", "https://issuer.example.test/jwks")
    monkeypatch.setenv("WORKSTREAM_TOKEN_ALGORITHMS", "RS256")
    monkeypatch.setenv("WORKSTREAM_TOKEN_INTROSPECTION_MODE", "disabled")
    monkeypatch.setenv(
        "WORKSTREAM_TOKEN_INTROSPECTION_DISABLED_REASON",
        "short-lived issuer tokens",
    )
    get_settings.cache_clear()
    clear_auth_verifier_cache()
    try:
        assert get_auth_verifier() is get_auth_verifier()
    finally:
        get_settings.cache_clear()
        clear_auth_verifier_cache()


async def test_invalid_production_auth_configuration_rejects_application_startup() -> None:
    app = create_app(Settings(environment="production", auth_provider="flow"))

    with pytest.raises(RuntimeError, match="WORKSTREAM_TOKEN_ISSUER"):
        async with app.router.lifespan_context(app):
            pass


async def test_valid_production_auth_configuration_allows_application_startup() -> None:
    app = create_app(
        _flow_settings(
            environment="production",
            token_introspection_mode="disabled",
            token_introspection_disabled_reason="short-lived issuer tokens",
        )
    )

    async with app.router.lifespan_context(app):
        pass
