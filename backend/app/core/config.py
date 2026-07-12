"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
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
    project_agent_openai_agent_sdk_model: str | None = None
    project_agent_run_timeout_seconds: float = Field(default=1800.0, gt=0.0, le=7200.0)
    project_agent_max_prompt_bytes: int = Field(default=2_000_000, gt=0, le=10_000_000)
    project_setup_pipeline_autostart: bool = True
    celery_broker_url: str | None = None
    celery_result_backend_url: str | None = None
    celery_task_always_eager: bool = False
    actor_registry_refresh_interval_seconds: int = Field(default=300, ge=0, le=86_400)
    artifact_store_backend: Literal["disabled", "local", "flow_node"] = "disabled"
    artifact_local_root: Path | None = None
    artifact_retention_policy_version: str | None = None
    artifact_maximum_bytes: int = Field(default=512 * 1024 * 1024, gt=0)
    artifact_stream_buffer_bytes: int = Field(default=1024 * 1024, gt=0, le=1024 * 1024)

    model_config = SettingsConfigDict(
        env_prefix="WORKSTREAM_",
        env_file=".env",
        extra="ignore",
    )

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
