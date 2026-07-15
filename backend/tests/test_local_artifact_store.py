"""Focused LocalStorage regression proof for the private write refactor."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import replace
import hashlib
from pathlib import Path

import pytest

from app.adapters.artifacts.local import LocalStorageAdapter
from app.interfaces.artifacts import (
    ArtifactOperation,
    IdempotencyIdentity,
    StoreArtifactRequest,
    canonical_store_request_digest,
)


async def byte_stream(*chunks: bytes) -> AsyncIterator[bytes]:
    """Yield exact LocalStorage test bytes."""
    for chunk in chunks:
        yield chunk


def store_request() -> StoreArtifactRequest:
    """Build one canonical active-v1 store request."""
    identity = IdempotencyIdentity(
        service_principal="workstream.artifact.ingest",
        operation=ArtifactOperation.STORE,
        key="private-helper-regression",
        request_digest="sha256:" + "0" * 64,
    )
    request = StoreArtifactRequest(
        expected_sha256="sha256:" + hashlib.sha256(b"hello").hexdigest(),
        expected_size=5,
        maximum_bytes=5,
        media_type="text/plain",
        metadata={},
        idempotency=identity,
    )
    return replace(
        request,
        idempotency=replace(
            identity,
            request_digest=canonical_store_request_digest(request),
        ),
    )


@pytest.mark.asyncio
async def test_private_write_refactor_preserves_active_v1_behavior(tmp_path: Path) -> None:
    """Keep store, replay, bounded chunks, and read behavior unchanged."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    request = store_request()
    stored = await adapter.store(byte_stream(b"hel", b"lo"), request)
    replay = await adapter.store(byte_stream(b"hello"), request)
    assert stored.sha256 == request.expected_sha256
    assert stored.byte_count == 5
    assert replay.provider_artifact_id == stored.provider_artifact_id
    assert replay.replayed is True
    chunks = [chunk async for chunk in adapter.open(stored.provider_artifact_id)]
    assert chunks == [b"he", b"ll", b"o"]
    assert list((tmp_path / "artifacts" / "tmp").iterdir()) == []
    adapter.close()
