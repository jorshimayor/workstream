from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.adapters.artifacts import resolve_artifact_store
from app.core.config import Settings
from app.interfaces.artifacts import ArtifactConfigurationError


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


@pytest.mark.parametrize("environment", ["staging", "preview", "prod", "production"])
def test_settings_reject_local_artifacts_outside_development(environment: str) -> None:
    """Keep filesystem storage out of production-like deployments."""
    with pytest.raises(ValidationError, match="local artifact storage"):
        Settings(
            environment=environment,
            artifact_store_backend="local",
            artifact_local_root="/tmp/workstream-artifacts",
            artifact_retention_policy_version="retention-v1",
        )


def test_settings_require_retention_policy_for_enabled_artifacts() -> None:
    """Fail construction when enabled storage lacks approved retention."""
    with pytest.raises(ValidationError, match="retention policy"):
        Settings(environment="test", artifact_store_backend="flow_node")


def test_local_artifact_settings_and_resolver(tmp_path) -> None:
    """Resolve local storage only from complete development configuration."""
    settings = Settings(
        environment="test",
        artifact_store_backend="local",
        artifact_local_root=tmp_path / "artifacts",
        artifact_retention_policy_version="retention-v1",
        artifact_stream_buffer_bytes=64,
    )
    assert resolve_artifact_store(settings).adapter_name == "local"


def test_flow_node_resolver_fails_until_adapter_chunk() -> None:
    """Do not imply that the reserved Flow Node backend is implemented."""
    settings = Settings(
        environment="production",
        artifact_store_backend="flow_node",
        artifact_retention_policy_version="retention-v1",
    )
    with pytest.raises(ArtifactConfigurationError, match="not available"):
        resolve_artifact_store(settings)
