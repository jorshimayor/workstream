from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from aiobotocore.credentials import (
    AioAssumeRoleWithWebIdentityProvider,
    AioContainerProvider,
    AioInstanceMetadataProvider,
)

from app.adapters.artifacts import s3_compatible
from app.core.config import Settings
from app.interfaces.artifacts import ArtifactConfigurationError


def _aws_settings(tmp_path: Path, method: str = "container-role") -> Settings:
    return Settings(
        environment="production",
        artifact_store_backend="s3_compatible",
        artifact_scratch_root=tmp_path / "scratch",
        artifact_s3_provider_profile="aws_s3",
        artifact_s3_region="us-east-1",
        artifact_s3_bucket="workstream-artifacts-prod",
        artifact_s3_private_prefix="workstream/artifacts",
        artifact_s3_addressing_style="virtual",
        artifact_s3_credential_mode="aws_workload_identity",
        artifact_s3_aws_workload_identity_method=method,  # type: ignore[arg-type]
    )


def _container_environment(tmp_path: Path, **overrides: str) -> dict[str, str]:
    environment = {
        "HOME": str(tmp_path),
        "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI": "/v2/credentials/workstream-runtime",
    }
    environment.update(overrides)
    return environment


def _web_identity_environment(tmp_path: Path, **overrides: str) -> dict[str, str]:
    token = tmp_path / "web-identity-token"
    token.write_text("token", encoding="utf-8")
    environment = {
        "HOME": str(tmp_path),
        "AWS_ROLE_ARN": "arn:aws:iam::123456789012:role/workstream-runtime",
        "AWS_ROLE_SESSION_NAME": "workstream-artifact-runtime",
        "AWS_WEB_IDENTITY_TOKEN_FILE": str(token),
    }
    environment.update(overrides)
    return environment


def _iam_environment(tmp_path: Path, **overrides: str) -> dict[str, str]:
    environment = {
        "HOME": str(tmp_path),
        "AWS_EC2_METADATA_V1_DISABLED": "true",
    }
    environment.update(overrides)
    return environment


def _assert_rejects_before_session_construction(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    environment: dict[str, str],
    match: str,
) -> None:
    events: list[str] = []

    def session_must_not_construct(*_args: object, **_kwargs: object) -> object:
        events.append("session")
        raise AssertionError("SDK session constructed before isolation rejection")

    monkeypatch.setattr(s3_compatible, "AioSession", session_must_not_construct)

    with pytest.raises(ArtifactConfigurationError, match=match):
        s3_compatible.create_isolated_aws_workload_identity_session(
            settings,
            environ=environment,
        )

    assert events == []


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("AWS_ACCESS_KEY", "legacy-access"),
        ("AWS_ACCESS_KEY_ID", "explicit-access"),
        ("AWS_SECRET_ACCESS_KEY", "explicit-secret"),
        ("AWS_SESSION_TOKEN", "explicit-session-token"),
        ("AWS_SECRET_KEY", "legacy-secret"),
        ("AWS_SECURITY_TOKEN", "legacy-security-token"),
        ("AWS_PROFILE", "prod"),
        ("AWS_DEFAULT_PROFILE", "prod"),
        ("AWS_SHARED_CREDENTIALS_FILE", "/tmp/credentials"),
        ("AWS_CONFIG_FILE", "/tmp/config"),
        ("AWS_CREDENTIAL_FILE", "/tmp/legacy-credentials"),
        ("AWS_LOGIN_CACHE_DIRECTORY", "/tmp/aws-login-cache"),
        ("BOTO_CONFIG", "/tmp/boto.cfg"),
    ],
)
def test_forbidden_ambient_aws_sources_fail_before_resolver_loading(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    name: str,
    value: str,
) -> None:
    _assert_rejects_before_session_construction(
        monkeypatch,
        _aws_settings(tmp_path, "container-role"),
        _container_environment(tmp_path, **{name: value}),
        "ambient AWS credential source is forbidden",
    )


@pytest.mark.parametrize(
    ("relative_path", "contents"),
    [
        (".aws/credentials", "[default]\naws_access_key_id = poison\n"),
        (".aws/config", "[profile prod]\ncredential_process = /bin/false\n"),
        (".aws/config", "[profile prod]\nsso_start_url = https://example.test/start\n"),
        (".boto", "[Credentials]\naws_access_key_id = poison\n"),
    ],
)
def test_default_credential_files_fail_before_resolver_loading(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    relative_path: str,
    contents: str,
) -> None:
    poison = tmp_path / relative_path
    poison.parent.mkdir(parents=True, exist_ok=True)
    poison.write_text(contents, encoding="utf-8")

    _assert_rejects_before_session_construction(
        monkeypatch,
        _aws_settings(tmp_path, "container-role"),
        _container_environment(tmp_path),
        "ambient AWS credential file is forbidden",
    )


@pytest.mark.parametrize(
    ("selected_method", "environment"),
    [
        (
            "assume-role-with-web-identity",
            lambda tmp_path: _web_identity_environment(
                tmp_path,
                AWS_CONTAINER_CREDENTIALS_RELATIVE_URI="/v2/credentials/poison",
            ),
        ),
        (
            "container-role",
            lambda tmp_path: _container_environment(
                tmp_path,
                AWS_ROLE_ARN="arn:aws:iam::123456789012:role/unselected",
                AWS_WEB_IDENTITY_TOKEN_FILE=str(tmp_path / "unselected-token"),
            ),
        ),
        (
            "iam-role",
            lambda tmp_path: _iam_environment(
                tmp_path,
                AWS_CONTAINER_CREDENTIALS_FULL_URI="http://127.0.0.1:9/credentials",
            ),
        ),
    ],
)
def test_unselected_workload_identity_sources_fail_before_resolver_loading(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    selected_method: str,
    environment: Any,
) -> None:
    _assert_rejects_before_session_construction(
        monkeypatch,
        _aws_settings(tmp_path, selected_method),
        environment(tmp_path),
        "unselected AWS workload source is configured",
    )


@pytest.mark.parametrize(
    ("method", "environment", "provider_type", "sdk_method"),
    [
        (
            "assume-role-with-web-identity",
            _web_identity_environment,
            AioAssumeRoleWithWebIdentityProvider,
            "assume-role-with-web-identity",
        ),
        ("container-role", _container_environment, AioContainerProvider, "container-role"),
        ("iam-role", _iam_environment, AioInstanceMetadataProvider, "iam-role"),
    ],
)
def test_isolated_session_contains_exactly_one_selected_provider(
    tmp_path: Path,
    method: str,
    environment: Any,
    provider_type: type[object],
    sdk_method: str,
) -> None:
    session = s3_compatible.create_isolated_aws_workload_identity_session(
        _aws_settings(tmp_path, method),
        environ=environment(tmp_path),
    )

    resolver = session.get_component("credential_provider")

    assert len(resolver.providers) == 1
    provider = resolver.providers[0]
    assert type(provider) is provider_type
    assert provider.METHOD == sdk_method
    if method == "assume-role-with-web-identity":
        assert provider._disable_env_vars is True
        assert provider._load_config() == {
            "profiles": {
                "workstream-isolated": {
                    "role_arn": "arn:aws:iam::123456789012:role/workstream-runtime",
                    "role_session_name": "workstream-artifact-runtime",
                    "web_identity_token_file": str(tmp_path / "web-identity-token"),
                }
            }
        }
    if method == "container-role":
        assert provider._environ == {
            "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI": (
                "/v2/credentials/workstream-runtime"
            )
        }
        assert (
            provider._fetcher._session._proxy_config.proxy_url_for(
                "http://169.254.170.2/v2/credentials/workstream-runtime"
            )
            is None
        )
    if method == "iam-role":
        assert provider._role_fetcher._imds_v1_disabled is True
        assert (
            provider._role_fetcher._session._proxy_config.proxy_url_for(
                "http://169.254.169.254/latest/meta-data/"
            )
            is None
        )


@pytest.mark.parametrize(
    ("method", "environment", "message"),
    [
        (
            "assume-role-with-web-identity",
            lambda tmp_path: {"HOME": str(tmp_path), "AWS_ROLE_ARN": "arn"},
            "web identity configuration is incomplete",
        ),
        (
            "assume-role-with-web-identity",
            lambda tmp_path: {
                "HOME": str(tmp_path),
                "AWS_ROLE_ARN": "arn",
                "AWS_WEB_IDENTITY_TOKEN_FILE": "relative-token",
            },
            "web identity token path is invalid",
        ),
        (
            "container-role",
            lambda tmp_path: {"HOME": str(tmp_path)},
            "container identity location is invalid",
        ),
        (
            "container-role",
            lambda tmp_path: {
                "HOME": str(tmp_path),
                "AWS_CONTAINER_CREDENTIALS_FULL_URI": "https://credentials.example.test",
            },
            "container full credential URI is forbidden",
        ),
        (
            "container-role",
            lambda tmp_path: {
                "HOME": str(tmp_path),
                "AWS_CONTAINER_CREDENTIALS_FULL_URI": "http://127.0.0.1:9/full",
                "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI": (
                    "/v2/credentials/workstream-runtime"
                ),
            },
            "container full credential URI is forbidden",
        ),
        (
            "container-role",
            lambda tmp_path: {
                "HOME": str(tmp_path),
                "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI": (
                    "/v2/credentials/workstream-runtime"
                ),
                "AWS_CONTAINER_AUTHORIZATION_TOKEN": "token",
            },
            "container identity token is forbidden",
        ),
        (
            "container-role",
            lambda tmp_path: {
                "HOME": str(tmp_path),
                "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI": (
                    "/v2/credentials/workstream-runtime"
                ),
                "AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE": str(tmp_path / "token"),
            },
            "container identity token is forbidden",
        ),
        (
            "iam-role",
            lambda tmp_path: {
                "HOME": str(tmp_path),
                "AWS_EC2_METADATA_DISABLED": "true",
                "AWS_EC2_METADATA_V1_DISABLED": "true",
            },
            "instance identity metadata is disabled",
        ),
        (
            "iam-role",
            lambda tmp_path: {"HOME": str(tmp_path)},
            "instance identity requires IMDSv2",
        ),
        (
            "iam-role",
            lambda tmp_path: {
                "HOME": str(tmp_path),
                "AWS_EC2_METADATA_V1_DISABLED": "false",
            },
            "instance identity requires IMDSv2",
        ),
        (
            "iam-role",
            lambda tmp_path: {
                "HOME": str(tmp_path),
                "AWS_EC2_METADATA_SERVICE_ENDPOINT": (
                    "https://metadata.example.test/latest"
                ),
            },
            "custom AWS metadata endpoint is forbidden",
        ),
    ],
)
def test_selected_workload_identity_source_must_be_complete(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    method: str,
    environment: Any,
    message: str,
) -> None:
    _assert_rejects_before_session_construction(
        monkeypatch,
        _aws_settings(tmp_path, method),
        environment(tmp_path),
        message,
    )


@pytest.mark.parametrize(
    "relative_uri",
    [
        "/relative",
        "/v2/credentials/",
        "/v2/credentials/workstream/runtime",
        "https://credentials.example.test/v2/credentials/runtime",
        "/v2/credentials/" + "a" * 513,
    ],
)
def test_container_role_rejects_noncanonical_relative_uri(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    relative_uri: str,
) -> None:
    _assert_rejects_before_session_construction(
        monkeypatch,
        _aws_settings(tmp_path, "container-role"),
        _container_environment(
            tmp_path,
            AWS_CONTAINER_CREDENTIALS_RELATIVE_URI=relative_uri,
        ),
        "container identity location is invalid",
    )


def test_iam_metadata_session_ignores_ambient_proxy_environment(tmp_path: Path) -> None:
    session = s3_compatible.create_isolated_aws_workload_identity_session(
        _aws_settings(tmp_path, "iam-role"),
        environ=_iam_environment(
            tmp_path,
            HTTP_PROXY="http://127.0.0.1:9",
            HTTPS_PROXY="http://127.0.0.1:9",
            ALL_PROXY="http://127.0.0.1:9",
        ),
    )
    provider = session.get_component("credential_provider").providers[0]

    assert (
        provider._role_fetcher._session._proxy_config.proxy_url_for(
            "http://169.254.169.254/latest/meta-data/"
        )
        is None
    )


def test_container_metadata_session_ignores_ambient_proxy_environment(
    tmp_path: Path,
) -> None:
    session = s3_compatible.create_isolated_aws_workload_identity_session(
        _aws_settings(tmp_path, "container-role"),
        environ=_container_environment(
            tmp_path,
            HTTP_PROXY="http://127.0.0.1:9",
            HTTPS_PROXY="http://127.0.0.1:9",
            ALL_PROXY="http://127.0.0.1:9",
        ),
    )
    provider = session.get_component("credential_provider").providers[0]

    assert provider._environ == {
        "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI": (
            "/v2/credentials/workstream-runtime"
        )
    }
    assert (
        provider._fetcher._session._proxy_config.proxy_url_for(
            "http://169.254.170.2/v2/credentials/workstream-runtime"
        )
        is None
    )


async def test_resolved_workload_identity_method_must_match() -> None:
    class FakeSession:
        def __init__(self, method: str | None) -> None:
            self._method = method

        async def get_credentials(self) -> object | None:
            if self._method is None:
                return None
            return SimpleNamespace(method=self._method)

    with pytest.raises(
        ArtifactConfigurationError,
        match="AWS workload identity method did not match",
    ):
        await s3_compatible.resolve_isolated_aws_workload_credentials(
            FakeSession("iam-role"),  # type: ignore[arg-type]
            expected_method="container-role",
        )

    with pytest.raises(
        ArtifactConfigurationError,
        match="AWS workload identity method did not match",
    ):
        await s3_compatible.resolve_isolated_aws_workload_credentials(
            FakeSession(None),  # type: ignore[arg-type]
            expected_method="container-role",
        )

    resolved = await s3_compatible.resolve_isolated_aws_workload_credentials(
        FakeSession("container-role"),  # type: ignore[arg-type]
        expected_method="container-role",
    )
    assert getattr(resolved, "method") == "container-role"
