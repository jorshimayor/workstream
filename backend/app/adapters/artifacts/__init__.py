"""Artifact-store adapter resolution."""

from __future__ import annotations

from app.core.config import Settings
from app.interfaces.artifacts import ArtifactConfigurationError, ArtifactStore


def resolve_artifact_store(settings: Settings) -> ArtifactStore:
    """Resolve the configured artifact provider without implying future support.

    Args:
        settings: Validated application settings.

    Returns:
        Configured artifact store.

    Raises:
        ArtifactConfigurationError: If storage is disabled or not implemented.
    """
    if settings.artifact_store_backend == "local":
        from app.adapters.artifacts.local import LocalStorageAdapter

        if settings.artifact_local_root is None:
            raise ArtifactConfigurationError("local artifact root is not configured")
        return LocalStorageAdapter(
            root=settings.artifact_local_root,
            buffer_bytes=settings.artifact_stream_buffer_bytes,
            lock_timeout_seconds=settings.artifact_operation_lock_timeout_seconds,
        )
    if settings.artifact_store_backend == "flow_node":
        raise ArtifactConfigurationError("configured artifact adapter is not available")
    raise ArtifactConfigurationError("artifact storage is disabled")
