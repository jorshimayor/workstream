"""Focused LocalStorage regression proof for the private write refactor."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import replace
import hashlib
from pathlib import Path
import threading

import pytest

from app.adapters.artifacts.local import LocalStorageAdapter
from app.interfaces.artifacts import (
    ArtifactIntegrityError,
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


@pytest.mark.asyncio
async def test_private_io_finishes_after_repeated_cancellation(tmp_path: Path) -> None:
    """Do not leave one blocking LocalStorage operation running unowned."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    started = threading.Event()
    finish = threading.Event()
    completed = threading.Event()

    def blocking_io() -> None:
        started.set()
        finish.wait(timeout=5)
        completed.set()

    task = asyncio.create_task(adapter._run_io(blocking_io))
    assert await asyncio.to_thread(started.wait, 5)
    task.cancel()
    await asyncio.sleep(0)
    task.cancel()
    await asyncio.sleep(0)
    finish.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert completed.is_set()
    adapter.close()


@pytest.mark.asyncio
async def test_private_io_preserves_cancellation_after_late_failure(tmp_path: Path) -> None:
    """Keep active-v1 cancellation semantics when blocking I/O later fails."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    started = threading.Event()
    finish = threading.Event()

    def failing_io() -> None:
        started.set()
        finish.wait(timeout=5)
        raise OSError("late filesystem failure")

    task = asyncio.create_task(adapter._run_io(failing_io))
    assert await asyncio.to_thread(started.wait, 5)
    task.cancel()
    await asyncio.sleep(0)
    task.cancel()
    finish.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    adapter.close()


@pytest.mark.asyncio
async def test_private_lock_releases_after_repeated_cancellation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Release a thread-acquired LocalStorage lock before propagating cancellation."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    acquired = threading.Event()
    finish_acquire = threading.Event()
    release_started = threading.Event()
    finish_release = threading.Event()
    released = threading.Event()
    original_acquire = adapter._acquire_lock
    original_release = adapter._release_lock

    def delayed_acquire(scope: str) -> tuple[object, int]:
        lock = original_acquire(scope)
        acquired.set()
        finish_acquire.wait(timeout=5)
        return lock

    def delayed_release(lock: tuple[object, int]) -> None:
        release_started.set()
        finish_release.wait(timeout=5)
        original_release(lock)
        released.set()

    monkeypatch.setattr(adapter, "_acquire_lock", delayed_acquire)
    monkeypatch.setattr(adapter, "_release_lock", delayed_release)
    task = asyncio.create_task(adapter._acquire_lock_async("repeated-cancellation"))
    assert await asyncio.to_thread(acquired.wait, 5)
    task.cancel()
    finish_acquire.set()
    assert await asyncio.to_thread(release_started.wait, 5)
    task.cancel()
    await asyncio.sleep(0)
    finish_release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert released.is_set()
    adapter.close()


@pytest.mark.asyncio
async def test_store_cleanup_survives_repeated_cancellation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Complete public-store cleanup and lock release before cancellation escapes."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    request = store_request()
    write_started = asyncio.Event()
    never = asyncio.Event()
    cleanup_started = asyncio.Event()
    finish_cleanup = asyncio.Event()
    original_write_stream = adapter._write_stream
    original_cleanup = adapter._cleanup_unpublished

    async def blocked_write(*_: object) -> tuple[str, int]:
        write_started.set()
        await never.wait()
        raise AssertionError("blocked write unexpectedly resumed")

    async def delayed_cleanup(scope: str) -> None:
        cleanup_started.set()
        await finish_cleanup.wait()
        await original_cleanup(scope)

    monkeypatch.setattr(adapter, "_write_stream", blocked_write)
    monkeypatch.setattr(adapter, "_cleanup_unpublished", delayed_cleanup)
    task = asyncio.create_task(adapter.store(byte_stream(b"hello"), request))
    await asyncio.wait_for(write_started.wait(), timeout=1)
    task.cancel()
    await asyncio.wait_for(cleanup_started.wait(), timeout=1)
    task.cancel()
    await asyncio.sleep(0)
    finish_cleanup.set()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert list((tmp_path / "artifacts" / "tmp").iterdir()) == []
    monkeypatch.setattr(adapter, "_write_stream", original_write_stream)
    stored = await adapter.store(byte_stream(b"hello"), request)
    assert stored.sha256 == request.expected_sha256
    adapter.close()


@pytest.mark.asyncio
async def test_store_preserves_cancellation_during_final_lock_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Finish final lock release without converting cancellation into success."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    request = store_request()
    release_started = threading.Event()
    finish_release = threading.Event()
    released = threading.Event()
    original_release = adapter._release_lock

    def delayed_release(lock: tuple[object, int]) -> None:
        release_started.set()
        finish_release.wait(timeout=5)
        original_release(lock)
        released.set()

    monkeypatch.setattr(adapter, "_release_lock", delayed_release)
    task = asyncio.create_task(adapter.store(byte_stream(b"hello"), request))
    assert await asyncio.to_thread(release_started.wait, 5)
    task.cancel()
    await asyncio.sleep(0)
    task.cancel()
    finish_release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert released.is_set()

    monkeypatch.setattr(adapter, "_release_lock", original_release)
    replay = await adapter.store(byte_stream(b"hello"), request)
    assert replay.replayed
    adapter.close()


@pytest.mark.asyncio
async def test_object_only_recovery_still_requires_exact_replay_without_commitment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Preserve active-v1 exact replay when no client commitment exists."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    committed_request = store_request()
    request = replace(committed_request, expected_sha256=None, expected_size=None)
    request = replace(
        request,
        idempotency=replace(
            request.idempotency,
            request_digest=canonical_store_request_digest(request),
        ),
    )
    original_write_json = adapter._write_json_exclusive
    interrupted = False

    async def cancel_before_metadata(path: Path, value: dict[str, object]) -> None:
        nonlocal interrupted
        if path.parent.name == "metadata" and not interrupted:
            interrupted = True
            raise asyncio.CancelledError
        await original_write_json(path, value)

    monkeypatch.setattr(adapter, "_write_json_exclusive", cancel_before_metadata)
    with pytest.raises(asyncio.CancelledError):
        await adapter.store(byte_stream(b"hello"), request)
    assert interrupted

    monkeypatch.setattr(adapter, "_write_json_exclusive", original_write_json)
    with pytest.raises(ArtifactIntegrityError, match="recovery commitment failed"):
        await adapter.store(byte_stream(b"wrong"), request)
    assert list((tmp_path / "artifacts" / "objects").iterdir()) == []
    assert len(list((tmp_path / "artifacts" / "quarantine").iterdir())) == 1
    adapter.close()
