"""Application settings loaded from environment variables."""

from __future__ import annotations

import base64
import binascii
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Workstream API."""

    app_name: str = "Workstream API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal[
        "local",
        "dev",
        "development",
        "test",
        "staging",
        "preview",
        "prod",
        "production",
    ] = "production"
    auth_provider: Literal["dev", "flow"] = "flow"
    database_url: str | None = None
    dev_auth_token: str | None = None
    dev_auth_subject: str | None = None
    dev_auth_issuer: str | None = None
    dev_auth_email: str | None = None
    dev_auth_display_name: str | None = None
    dev_auth_roles: str = ""
    flow_auth_issuer: str = "https://auth.flow.local"
    flow_auth_audience: str = "workstream-api"
    flow_auth_local_hmac_secret: str | None = None
    token_issuer: str | None = None
    token_audience: str = "workstream"
    token_jwks_url: str | None = None
    token_algorithms: str = ""
    required_human_scope: str = "workstream:access"
    required_service_scope: str = "workstream:service"
    token_clock_skew_seconds: int = Field(default=30, ge=0, le=300)
    token_max_bytes: int = Field(default=16_384, ge=512, le=32_768)
    token_header_max_bytes: int = Field(default=4_096, ge=128, le=8_192)
    token_payload_max_bytes: int = Field(default=12_288, ge=256, le=24_576)
    token_jwks_cache_ttl_seconds: int = Field(default=300, ge=30, le=3_600)
    token_jwks_max_response_bytes: int = Field(default=262_144, ge=1_024, le=1_048_576)
    token_jwks_max_keys: int = Field(default=20, ge=1, le=100)
    token_unknown_kid_cache_ttl_seconds: int = Field(default=30, ge=1, le=300)
    token_unknown_kid_cache_max_entries: int = Field(default=100, ge=1, le=1_000)
    token_jwks_connect_timeout_seconds: float = Field(default=2.0, ge=0.1, le=10.0)
    token_jwks_read_timeout_seconds: float = Field(default=3.0, ge=0.1, le=10.0)
    token_jwks_write_timeout_seconds: float = Field(default=3.0, ge=0.1, le=10.0)
    token_jwks_pool_timeout_seconds: float = Field(default=1.0, ge=0.1, le=10.0)
    token_jwks_total_timeout_seconds: float = Field(default=5.0, ge=0.5, le=15.0)
    token_introspection_mode: Literal["disabled", "required"] | None = None
    token_introspection_disabled_reason: str | None = None
    token_introspection_url: str | None = None
    token_introspection_client_id: str | None = None
    token_introspection_client_secret: str | None = None
    token_introspection_max_response_bytes: int = Field(default=65_536, ge=256, le=262_144)
    token_introspection_connect_timeout_seconds: float = Field(default=2.0, ge=0.1, le=10.0)
    token_introspection_read_timeout_seconds: float = Field(default=3.0, ge=0.1, le=10.0)
    token_introspection_write_timeout_seconds: float = Field(default=3.0, ge=0.1, le=10.0)
    token_introspection_pool_timeout_seconds: float = Field(default=1.0, ge=0.1, le=10.0)
    token_introspection_total_timeout_seconds: float = Field(default=5.0, ge=0.5, le=15.0)
    project_agent_openai_agent_sdk_model: str | None = None
    project_agent_run_timeout_seconds: float = Field(default=1800.0, gt=0.0, le=7200.0)
    project_agent_max_prompt_bytes: int = Field(default=2_000_000, gt=0, le=10_000_000)
    project_setup_pipeline_autostart: bool = True
    celery_broker_url: str | None = None
    celery_result_backend_url: str | None = None
    celery_task_always_eager: bool = False
    actor_registry_refresh_interval_seconds: int = Field(default=300, ge=0, le=86_400)
    api_rate_limit_key_secret: SecretStr | None = None
    api_first_access_rate_limit: int = Field(default=10, ge=1, le=10_000)
    api_first_access_rate_window_seconds: int = Field(default=60, ge=1, le=3_600)
    api_admin_mutation_rate_limit: int = Field(default=30, ge=1, le=10_000)
    api_admin_mutation_rate_window_seconds: int = Field(default=60, ge=1, le=3_600)
    artifact_store_backend: Literal["disabled", "local", "flow_node"] = "disabled"
    artifact_local_root: Path | None = None
    artifact_retention_policy_version: str | None = None
    artifact_maximum_bytes: int = Field(default=512 * 1024 * 1024, gt=0)
    artifact_stream_buffer_bytes: int = Field(default=1024 * 1024, gt=0, le=1024 * 1024)

    model_config = SettingsConfigDict(
        env_prefix="WORKSTREAM_",
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )

    def __init__(self, **values: object) -> None:
        """Validate secret material after Pydantic has discarded raw input."""
        super().__init__(**values)
        if self.api_rate_limit_key_secret is not None:
            decode_api_rate_limit_key_secret(self.api_rate_limit_key_secret)

    @model_validator(mode="after")
    def validate_artifact_storage(self) -> Settings:
        """Reject unsafe or incomplete artifact-storage combinations.

        Returns:
            Validated settings instance.

        Raises:
            ValueError: If enabled artifact storage is unsafe or incomplete.
        """
        if self.artifact_store_backend == "disabled":
            return self
        if not self.artifact_retention_policy_version or not (
            self.artifact_retention_policy_version.strip()
        ):
            raise ValueError("enabled artifact storage requires a retention policy version")
        if self.artifact_store_backend == "local":
            if self.environment not in {"local", "dev", "development", "test"}:
                raise ValueError("local artifact storage is restricted to development and test")
            if self.artifact_local_root is None:
                raise ValueError("local artifact storage requires an artifact root")
        return self


@lru_cache
def get_settings() -> Settings:
    """Load and cache application settings.

    Returns:
        Settings resolved from environment variables and optional ``.env``.
    """
    return Settings()


def decode_api_rate_limit_key_secret(value: SecretStr) -> bytes:
    """Decode one canonical padded Base64 rate-control key."""
    secret = value.get_secret_value()
    try:
        encoded = secret.encode("ascii")
        decoded = base64.b64decode(encoded, validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
        raise ValueError("invalid API rate limit key secret") from exc
    if not 32 <= len(decoded) <= 64 or base64.b64encode(decoded) != encoded:
        raise ValueError("invalid API rate limit key secret")
    return decoded
