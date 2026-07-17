"""Test-only activation helpers for the namespace-fenced local artifact store."""

from __future__ import annotations

from pathlib import Path

from app.adapters.artifacts.local import LocalStorageAdapter, LocalStorageBootstrap
from app.interfaces.artifacts import (
    ArtifactStoreNamespaceClaim,
    artifact_store_namespace_material,
)


def initialize_local_store(
    root: Path,
    *,
    buffer_bytes: int = 1024 * 1024,
    lock_timeout_seconds: float = 1800.0,
) -> LocalStorageAdapter:
    """Pre-provision, pin, claim, and initialize one test-only local store."""
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    bootstrap = LocalStorageBootstrap(
        LocalStorageAdapter(
            root=root,
            buffer_bytes=buffer_bytes,
            lock_timeout_seconds=lock_timeout_seconds,
        )
    )
    return bootstrap.initialize_after_namespace_claim(local_namespace_claim(bootstrap))


def local_namespace_claim(bootstrap: LocalStorageBootstrap) -> ArtifactStoreNamespaceClaim:
    """Mint the exact test-only namespace claim for one pinned adapter."""
    namespace_identity = bootstrap.namespace_identity
    _, fingerprint = artifact_store_namespace_material(
        backend="local",
        adapter_identity=bootstrap.identity,
        namespace_identity=namespace_identity,
    )
    return ArtifactStoreNamespaceClaim(
        adapter_identity=bootstrap.identity,
        namespace_identity=namespace_identity,
        namespace_fingerprint=fingerprint,
    )
