"""Application settings loaded from environment variables."""

from __future__ import annotations

import base64
import binascii
import json
import os
import re
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Literal, Self
from urllib.parse import urlsplit

from dotenv import dotenv_values
from pydantic import Field, PrivateAttr, SecretStr, model_validator
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


_ARTIFACT_S3_SECRET_FIELDS = frozenset(
    {
        "artifact_s3_access_key_id",
        "artifact_s3_secret_access_key",
        "artifact_s3_session_token",
    }
)
_S3_REGION = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
_S3_BUCKET = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
_S3_PREFIX_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


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
    api_first_access_rate_limit: int = Field(default=10, ge=1, le=10_000)
    api_first_access_rate_window_seconds: int = Field(default=60, ge=1, le=3_600)
    api_admin_mutation_rate_limit: int = Field(default=30, ge=1, le=10_000)
    api_admin_mutation_rate_window_seconds: int = Field(default=60, ge=1, le=3_600)
    artifact_store_backend: Literal["disabled", "local", "s3_compatible"] = "disabled"
    artifact_local_root: Path | None = None
    artifact_s3_provider_profile: Literal["aws_s3", "minio"] | None = None
    artifact_s3_region: str | None = None
    artifact_s3_endpoint_url: str | None = None
    artifact_s3_bucket: str | None = None
    artifact_s3_private_prefix: str = "workstream/artifacts"
    artifact_s3_addressing_style: Literal["path", "virtual"] = "virtual"
    artifact_s3_credential_mode: Literal[
        "aws_workload_identity",
        "local_static",
    ] | None = None
    artifact_s3_aws_workload_identity_method: Literal[
        "assume-role-with-web-identity",
        "container-role",
        "iam-role",
    ] | None = None
    artifact_s3_connect_timeout_seconds: float = Field(default=5.0, gt=0.0, le=60.0)
    artifact_s3_read_timeout_seconds: float = Field(default=60.0, gt=0.0, le=1800.0)
    artifact_s3_write_timeout_seconds: float = Field(default=1800.0, gt=0.0, le=3600.0)
    artifact_s3_pool_timeout_seconds: float = Field(default=5.0, gt=0.0, le=60.0)
    artifact_s3_operation_total_timeout_seconds: float = Field(
        default=1800.0,
        gt=0.0,
        le=3600.0,
    )
    artifact_s3_max_pool_connections: int = Field(default=16, ge=1, le=256)
    artifact_maximum_bytes: int = Field(default=512 * 1024 * 1024, gt=0)
    artifact_stream_buffer_bytes: int = Field(default=1024 * 1024, gt=0, le=1024 * 1024)
    artifact_operation_lock_timeout_seconds: float = Field(
        default=1800.0,
        gt=0.0,
        le=7200.0,
    )
    artifact_scratch_root: Path | None = None
    artifact_scratch_aggregate_reserved_bytes: int = Field(
        default=4 * 512 * 1024 * 1024,
        ge=512 * 1024 * 1024,
    )
    artifact_scratch_maximum_files: int = Field(default=8, ge=1, le=1024)
    artifact_scratch_maximum_concurrency: int = Field(default=4, ge=1, le=1024)
    artifact_scratch_minimum_free_bytes: int = Field(
        default=512 * 1024 * 1024,
        ge=0,
    )
    artifact_scratch_reservation_ttl_seconds: float = Field(
        default=2400.0,
        gt=0.0,
        le=86_400.0,
    )
    artifact_preparation_total_deadline_seconds: float = Field(
        default=1800.0,
        gt=0.0,
        le=7200.0,
    )
    artifact_scratch_cleanup_margin_seconds: float = Field(
        default=300.0,
        gt=0.0,
        le=3600.0,
    )
    artifact_scratch_cleanup_interval_seconds: int = Field(
        default=300,
        gt=0,
        le=86_400,
    )

    model_config = SettingsConfigDict(
        env_prefix="WORKSTREAM_",
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )

    _api_rate_limit_key_secret: SecretStr | None = PrivateAttr(default=None)
    _artifact_s3_access_key_id: SecretStr | None = PrivateAttr(default=None)
    _artifact_s3_secret_access_key: SecretStr | None = PrivateAttr(default=None)
    _artifact_s3_session_token: SecretStr | None = PrivateAttr(default=None)

    def __init__(self, **values: object) -> None:
        """Remove rate-control secret material before structured validation."""
        secret = _extract_api_rate_limit_key_secret(values)
        s3_secrets = _extract_artifact_s3_static_secrets(values)
        super().__init__(**values)
        self._api_rate_limit_key_secret = secret
        self._set_artifact_s3_static_secrets(s3_secrets)
        self._validate_artifact_s3_secret_contract()

    @classmethod
    def model_validate(cls, obj: object, **kwargs: object) -> Self:
        """Sanitize secret-bearing mappings before Pydantic retains input."""
        if isinstance(obj, Mapping) and (
            "api_rate_limit_key_secret" in obj
            or _ARTIFACT_S3_SECRET_FIELDS.intersection(obj)
        ):
            sanitized = dict(obj)
            secret = (
                _extract_api_rate_limit_key_secret(sanitized)
                if "api_rate_limit_key_secret" in sanitized
                else None
            )
            s3_secrets = _extract_artifact_s3_static_secrets(sanitized)
            if secret is not None:
                sanitized["api_rate_limit_key_secret"] = None
            for field_name in _ARTIFACT_S3_SECRET_FIELDS:
                if field_name in obj:
                    sanitized[field_name] = None
            settings = super().model_validate(sanitized, **kwargs)
            if secret is not None:
                settings._api_rate_limit_key_secret = secret
            settings._set_artifact_s3_static_secrets(s3_secrets)
            settings._validate_artifact_s3_secret_contract()
            return settings
        return super().model_validate(obj, **kwargs)

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        **kwargs: object,
    ) -> Self:
        """Sanitize JSON secret input before Pydantic retains the document."""
        malformed = False
        try:
            parsed = json.loads(json_data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            malformed = True
            parsed = None
        if malformed:
            raise ValueError("invalid settings JSON")
        if isinstance(parsed, Mapping) and (
            "api_rate_limit_key_secret" in parsed
            or _ARTIFACT_S3_SECRET_FIELDS.intersection(parsed)
        ):
            return cls.model_validate(parsed, **kwargs)
        return super().model_validate_json(json_data, **kwargs)

    @classmethod
    def model_validate_strings(cls, obj: object, **kwargs: object) -> Self:
        """Sanitize string-mapping secret input before structured validation."""
        if isinstance(obj, Mapping) and (
            "api_rate_limit_key_secret" in obj
            or _ARTIFACT_S3_SECRET_FIELDS.intersection(obj)
        ):
            sanitized = dict(obj)
            secret = (
                _extract_api_rate_limit_key_secret(sanitized)
                if "api_rate_limit_key_secret" in sanitized
                else None
            )
            s3_secrets = _extract_artifact_s3_static_secrets(sanitized)
            if secret is not None:
                sanitized["api_rate_limit_key_secret"] = None
            for field_name in _ARTIFACT_S3_SECRET_FIELDS:
                if field_name in obj:
                    sanitized[field_name] = None
            settings = super().model_validate_strings(sanitized, **kwargs)
            if secret is not None:
                settings._api_rate_limit_key_secret = secret
            settings._set_artifact_s3_static_secrets(s3_secrets)
            settings._validate_artifact_s3_secret_contract()
            return settings
        return super().model_validate_strings(obj, **kwargs)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Keep the manually resolved rate key out of dotenv validation input."""
        if isinstance(dotenv_settings, DotEnvSettingsSource):
            dotenv_settings.env_vars.pop("workstream_api_rate_limit_key_secret", None)
            for field_name in _ARTIFACT_S3_SECRET_FIELDS:
                dotenv_settings.env_vars.pop(f"workstream_{field_name}", None)
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    @property
    def api_rate_limit_key_secret(self) -> SecretStr | None:
        """Return the validated, redacted rate-control key setting."""
        return self._api_rate_limit_key_secret

    @property
    def artifact_s3_access_key_id(self) -> SecretStr | None:
        """Return the local/CI MinIO access-key identifier."""
        return self._artifact_s3_access_key_id

    @property
    def artifact_s3_secret_access_key(self) -> SecretStr | None:
        """Return the local/CI MinIO secret access key."""
        return self._artifact_s3_secret_access_key

    @property
    def artifact_s3_session_token(self) -> SecretStr | None:
        """Return the optional local/CI MinIO session token."""
        return self._artifact_s3_session_token

    def _set_artifact_s3_static_secrets(
        self,
        secrets: tuple[SecretStr | None, SecretStr | None, SecretStr | None],
    ) -> None:
        """Retain static MinIO credentials only as redacted private values."""
        (
            self._artifact_s3_access_key_id,
            self._artifact_s3_secret_access_key,
            self._artifact_s3_session_token,
        ) = secrets

    def _validate_artifact_s3_secret_contract(self) -> None:
        """Reject static credentials outside a complete local MinIO profile."""
        secrets = (
            self.artifact_s3_access_key_id,
            self.artifact_s3_secret_access_key,
            self.artifact_s3_session_token,
        )
        if self.artifact_store_backend != "s3_compatible" and any(
            value is not None for value in secrets
        ):
            raise ValueError("static artifact credentials require MinIO storage")
        if self.artifact_s3_provider_profile == "minio" and (
            self.artifact_s3_access_key_id is None
            or self.artifact_s3_secret_access_key is None
        ):
            raise ValueError("MinIO artifact storage requires complete static credentials")
        if self.artifact_s3_provider_profile == "aws_s3" and any(
            value is not None for value in secrets
        ):
            raise ValueError("native AWS S3 rejects static credentials")

    @model_validator(mode="after")
    def validate_artifact_storage(self) -> Settings:
        """Reject unsafe or incomplete artifact-storage combinations.

        Returns:
            Validated settings instance.

        Raises:
            ValueError: If enabled artifact storage is unsafe or incomplete.
        """
        if self.artifact_scratch_maximum_concurrency > self.artifact_scratch_maximum_files:
            raise ValueError("artifact scratch concurrency cannot exceed its file limit")
        if (
            self.artifact_preparation_total_deadline_seconds
            + self.artifact_scratch_cleanup_margin_seconds
            >= self.artifact_scratch_reservation_ttl_seconds
        ):
            raise ValueError("artifact preparation deadline must expire before scratch TTL")
        if self.artifact_scratch_root is not None and self.artifact_local_root is not None:
            scratch_root = self.artifact_scratch_root.resolve(strict=False)
            local_root = self.artifact_local_root.resolve(strict=False)
            if (
                scratch_root == local_root
                or scratch_root.is_relative_to(local_root)
                or local_root.is_relative_to(scratch_root)
            ):
                raise ValueError(
                    "artifact scratch and durable local storage roots must be separate"
                )
        if self.artifact_store_backend == "disabled":
            return self
        if self.artifact_scratch_root is None:
            raise ValueError("enabled artifact storage requires an artifact scratch root")
        if self.artifact_store_backend == "local":
            if self.environment not in {"local", "dev", "development", "test"}:
                raise ValueError("local artifact storage is restricted to development and test")
            if self.artifact_local_root is None:
                raise ValueError("local artifact storage requires an artifact root")
            return self
        self._validate_s3_compatible_storage()
        return self

    def _validate_s3_compatible_storage(self) -> None:
        """Require one closed MinIO or native AWS configuration profile."""
        if self.artifact_s3_provider_profile is None:
            raise ValueError("S3-compatible artifact storage requires a provider profile")
        if not _is_canonical_s3_region(self.artifact_s3_region):
            raise ValueError("S3-compatible artifact storage requires a canonical region")
        if not _is_canonical_s3_bucket(self.artifact_s3_bucket):
            raise ValueError("S3-compatible artifact storage requires a canonical bucket")
        if not _is_canonical_s3_prefix(self.artifact_s3_private_prefix):
            raise ValueError("S3-compatible artifact storage private prefix is invalid")
        if self.artifact_maximum_bytes > 512 * 1024 * 1024:
            raise ValueError("S3-compatible artifact maximum exceeds 512 MiB")
        if self.artifact_s3_provider_profile == "minio":
            self._validate_minio_storage()
            return
        self._validate_native_aws_storage()

    def _validate_minio_storage(self) -> None:
        """Keep static MinIO credentials and endpoints local to development/CI."""
        if self.environment not in {"local", "dev", "development", "test"}:
            raise ValueError("MinIO artifact storage is restricted to development and test")
        if self.artifact_s3_credential_mode != "local_static":
            raise ValueError("MinIO artifact storage requires local static credentials")
        if self.artifact_s3_aws_workload_identity_method is not None:
            raise ValueError("MinIO artifact storage cannot select AWS workload identity")
        _validate_minio_endpoint(self.artifact_s3_endpoint_url)

    def _validate_native_aws_storage(self) -> None:
        """Validate native AWS configuration without activating its runtime."""
        if self.artifact_s3_endpoint_url is not None:
            raise ValueError("native AWS S3 does not accept a configured endpoint")
        if self.artifact_s3_credential_mode != "aws_workload_identity":
            raise ValueError("native AWS S3 requires workload identity")
        if self.artifact_s3_aws_workload_identity_method is None:
            raise ValueError("native AWS S3 requires one workload identity method")


@lru_cache
def get_settings() -> Settings:
    """Load and cache application settings.

    Returns:
        Settings resolved from environment variables and optional ``.env``.
    """
    return Settings()


def _extract_api_rate_limit_key_secret(values: dict[str, object]) -> SecretStr | None:
    """Resolve and validate the key without entering Pydantic's input graph."""
    missing = object()
    raw_value = values.pop("api_rate_limit_key_secret", missing)
    if raw_value is missing:
        raw_value = os.environ.get("WORKSTREAM_API_RATE_LIMIT_KEY_SECRET", missing)
    if raw_value is missing:
        env_file = values.get("_env_file", ".env")
        if env_file is not None:
            env_encoding = values.get("_env_file_encoding", "utf-8")
            env_files = (env_file,) if isinstance(env_file, (str, os.PathLike)) else tuple(env_file)
            for path in env_files:
                dotenv = dotenv_values(path, encoding=env_encoding)
                raw_value = dotenv.get("WORKSTREAM_API_RATE_LIMIT_KEY_SECRET", raw_value)
    if raw_value is missing or raw_value is None:
        return None
    if isinstance(raw_value, SecretStr):
        secret = raw_value
    elif isinstance(raw_value, str):
        secret = SecretStr(raw_value)
    else:
        raise ValueError("invalid API rate limit key secret")
    decode_api_rate_limit_key_secret(secret)
    return secret


def _extract_artifact_s3_static_secrets(
    values: dict[str, object],
) -> tuple[SecretStr | None, SecretStr | None, SecretStr | None]:
    """Remove optional MinIO credentials from structured settings input."""
    return tuple(
        _extract_optional_secret(
            values,
            field_name=field_name,
            environment_name=f"WORKSTREAM_{field_name.upper()}",
        )
        for field_name in (
            "artifact_s3_access_key_id",
            "artifact_s3_secret_access_key",
            "artifact_s3_session_token",
        )
    )  # type: ignore[return-value]


def _extract_optional_secret(
    values: dict[str, object],
    *,
    field_name: str,
    environment_name: str,
) -> SecretStr | None:
    """Resolve one bounded secret without retaining it in Pydantic input."""
    missing = object()
    raw_value = values.pop(field_name, missing)
    if raw_value is missing:
        raw_value = os.environ.get(environment_name, missing)
    if raw_value is missing:
        env_file = values.get("_env_file", ".env")
        if env_file is not None:
            env_encoding = values.get("_env_file_encoding", "utf-8")
            env_files = (env_file,) if isinstance(env_file, (str, os.PathLike)) else tuple(env_file)
            for path in env_files:
                dotenv = dotenv_values(path, encoding=env_encoding)
                raw_value = dotenv.get(environment_name, raw_value)
    if raw_value is missing or raw_value is None:
        return None
    if isinstance(raw_value, SecretStr):
        secret = raw_value
    elif isinstance(raw_value, str):
        secret = SecretStr(raw_value)
    else:
        raise ValueError("invalid artifact storage secret")
    revealed = secret.get_secret_value()
    if (
        not revealed
        or len(revealed) > 4096
        or any(ord(character) < 32 or ord(character) == 127 for character in revealed)
    ):
        raise ValueError("invalid artifact storage secret")
    return secret


def _is_canonical_s3_region(value: str | None) -> bool:
    """Return whether one region is bounded and canonical."""
    return isinstance(value, str) and _S3_REGION.fullmatch(value) is not None


def _is_canonical_s3_bucket(value: str | None) -> bool:
    """Return whether one dedicated bucket name is DNS-compatible."""
    if not isinstance(value, str) or _S3_BUCKET.fullmatch(value) is None:
        return False
    return ".." not in value and not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", value)


def _is_canonical_s3_prefix(value: str) -> bool:
    """Return whether one private object prefix has canonical path segments."""
    if not isinstance(value, str) or not value or len(value) > 512:
        return False
    segments = value.split("/")
    return all(_S3_PREFIX_SEGMENT.fullmatch(segment) is not None for segment in segments)


def _validate_minio_endpoint(value: str | None) -> None:
    """Require one canonical noncredentialed HTTP(S) MinIO origin."""
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise ValueError("MinIO artifact storage requires an endpoint")
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
        or value.endswith("/")
    ):
        raise ValueError("MinIO artifact storage endpoint is invalid")


def decode_api_rate_limit_key_secret(value: SecretStr) -> bytes:
    """Decode one canonical padded Base64 rate-control key."""
    secret = value.get_secret_value()
    if not secret.isascii():
        raise ValueError("invalid API rate limit key secret")
    invalid = False
    try:
        encoded = secret.encode("ascii")
        decoded = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        invalid = True
        encoded = b""
        decoded = b""
    if invalid:
        raise ValueError("invalid API rate limit key secret")
    if not 32 <= len(decoded) <= 64 or base64.b64encode(decoded) != encoded:
        raise ValueError("invalid API rate limit key secret")
    return decoded
