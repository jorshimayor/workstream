from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import stat as stat_module
import threading
from uuid import uuid4

from alembic import command
from alembic.config import Config
from jsonschema import Draft202012Validator
import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.adapters.artifacts.local import LocalStorageAdapter
from app.core.hashing import canonical_json_hash
from app.interfaces.artifacts import (
    ArtifactByteRange,
    ArtifactIdempotencyMismatchError,
    ArtifactInputMismatchError,
    ArtifactIntegrityError,
    ArtifactLimitExceededError,
    ArtifactNotFoundError,
    ArtifactRetentionConflictError,
    ArtifactOperation,
    ArtifactMalformedRequestError,
    ArtifactStoreUnavailableError,
    ArtifactThrottledError,
    IdempotencyIdentity,
    IntegrityState,
    StoreArtifactRequest,
    canonical_release_request_digest,
    canonical_retain_request_digest,
    canonical_store_request_digest,
    canonical_verify_request_digest,
)
from app.modules.artifacts.models import (
    ArtifactBinding,
    ArtifactContent,
    ArtifactOperationReceipt,
    ArtifactReplica,
    ArtifactUploadItem,
    ArtifactUploadSession,
)
from app.modules.artifacts.service import ArtifactIngestService
from app.modules.projects.models import Project
from app.modules.tasks.models import AuditEvent


async def byte_stream(*chunks: bytes) -> AsyncIterator[bytes]:
    """Yield exact byte chunks for adapter tests."""
    for chunk in chunks:
        yield chunk


def store_request(
    *,
    key: str = "store-1",
    request_value: str = "same",
    expected_sha256: str | None = None,
    expected_size: int | None = None,
    maximum_bytes: int = 64,
) -> StoreArtifactRequest:
    """Build one canonical store request."""
    identity = IdempotencyIdentity(
        service_principal="workstream.artifact.ingest",
        operation=ArtifactOperation.STORE,
        key=key,
        request_digest="sha256:" + "0" * 64,
    )
    request = StoreArtifactRequest(
        expected_sha256=expected_sha256,
        expected_size=expected_size,
        maximum_bytes=maximum_bytes,
        media_type="application/octet-stream",
        metadata={"request": request_value},
        idempotency=identity,
    )
    return replace(
        request,
        idempotency=replace(identity, request_digest=canonical_store_request_digest(request)),
    )


def verify_identity(
    provider_artifact_id: str,
    expected_sha256: str,
    expected_size: int,
    *,
    key: str = "verify-1",
    principal: str = "workstream.artifact.ingest",
) -> IdempotencyIdentity:
    """Build one canonical verify identity."""
    return IdempotencyIdentity(
        principal,
        ArtifactOperation.VERIFY,
        key,
        canonical_verify_request_digest(provider_artifact_id, expected_sha256, expected_size),
    )


def retain_identity(
    provider_artifact_id: str,
    reference: str,
    retention_class: str,
    *,
    key: str = "retain-1",
    principal: str = "workstream.artifact.ingest",
) -> IdempotencyIdentity:
    """Build one canonical retain identity."""
    return IdempotencyIdentity(
        principal,
        ArtifactOperation.RETAIN,
        key,
        canonical_retain_request_digest(provider_artifact_id, reference, retention_class),
    )


def release_identity(
    provider_artifact_id: str,
    reference: str,
    *,
    key: str = "release-1",
    principal: str = "workstream.artifact.ingest",
) -> IdempotencyIdentity:
    """Build one canonical release identity."""
    return IdempotencyIdentity(
        principal,
        ArtifactOperation.RELEASE,
        key,
        canonical_release_request_digest(provider_artifact_id, reference),
    )


def test_versioned_contract_fixtures_validate() -> None:
    """Validate every positive and negative JSON Schema vector."""
    root = Path(__file__).resolve().parents[2] / "contracts" / "artifact-store" / "version_1"
    schema = json.loads((root / "schema" / "contract.schema.json").read_text())
    valid = json.loads((root / "fixtures" / "valid.json").read_text())
    invalid = json.loads((root / "fixtures" / "invalid.json").read_text())
    for fixture in valid["fixtures"]:
        definition = schema["$defs"][fixture["schema_ref"].rsplit("/", 1)[-1]]
        Draft202012Validator({**schema, **definition}).validate(fixture["instance"])
    for fixture in invalid["fixtures"]:
        definition = schema["$defs"][fixture["schema_ref"].rsplit("/", 1)[-1]]
        errors = list(Draft202012Validator({**schema, **definition}).iter_errors(fixture["instance"]))
        assert errors, fixture["name"]
        assert any(error.validator == fixture["expected_keyword"] for error in errors)

    error_types = {
        "malformed": ArtifactMalformedRequestError,
        "oversized": ArtifactLimitExceededError,
        "input_mismatch": ArtifactInputMismatchError,
        "integrity": ArtifactIntegrityError,
        "not_found": ArtifactNotFoundError,
        "replay_conflict": ArtifactIdempotencyMismatchError,
        "throttled": ArtifactThrottledError,
        "provider_unavailable": ArtifactStoreUnavailableError,
    }
    for vector in invalid["error_vectors"]:
        error_type = error_types[vector["name"]]
        assert error_type.code == vector["code"]
        assert error_type.category == vector["category"]
        assert error_type.retryable is vector["retryable"]


def test_canonical_digest_vectors_use_shared_hashing() -> None:
    """Prove contract digests use Workstream's shared canonical helper."""
    fixture = (
        Path(__file__).resolve().parents[2]
        / "contracts"
        / "artifact-store"
        / "version_1"
        / "fixtures"
        / "canonical-digests.json"
    )
    for vector in json.loads(fixture.read_text())["vectors"]:
        assert canonical_json_hash(vector["input"]) == vector["digest"]


@pytest.mark.asyncio
async def test_executable_conformance_vectors(tmp_path: Path) -> None:
    """Execute every named provider conformance vector against the local adapter."""
    fixture_path = (
        Path(__file__).resolve().parents[2]
        / "contracts"
        / "artifact-store"
        / "version_1"
        / "fixtures"
        / "conformance.json"
    )
    vectors = {vector["name"]: vector for vector in json.loads(fixture_path.read_text())["vectors"]}
    executed: set[str] = set()

    adapter = LocalStorageAdapter(root=tmp_path / "store", buffer_bytes=2)
    request = store_request(key="conformance-store", maximum_bytes=4)
    stored = await adapter.store(byte_stream(b""), request)
    replay = await adapter.store(byte_stream(b""), request)
    assert replay.replayed and replay.receipt.receipt_id == stored.receipt.receipt_id
    executed.add("store_exact_replay")

    consumed = False

    async def untouched() -> AsyncIterator[bytes]:
        nonlocal consumed
        consumed = True
        yield b""

    with pytest.raises(ArtifactIdempotencyMismatchError) as mismatch:
        await adapter.store(
            untouched(), store_request(key="conformance-store", request_value="changed")
        )
    assert mismatch.value.code == vectors["store_request_digest_mismatch"]["expected_error"]
    assert consumed is vectors["store_request_digest_mismatch"]["consume_replay_stream"]
    executed.add("store_request_digest_mismatch")

    with pytest.raises(ArtifactIntegrityError) as replay_mismatch:
        await adapter.store(byte_stream(b"x"), request)
    assert replay_mismatch.value.code == vectors["store_replay_byte_mismatch"]["expected_error"]
    executed.add("store_replay_byte_mismatch")

    recovery_adapter = LocalStorageAdapter(root=tmp_path / "conformance-recovery", buffer_bytes=2)
    recovery_request = store_request(
        key="conformance-recovery",
        expected_sha256="sha256:" + hashlib.sha256(b"data").hexdigest(),
        expected_size=4,
        maximum_bytes=4,
    )
    recovery_stored = await recovery_adapter.store(byte_stream(b"data"), recovery_request)
    next((tmp_path / "conformance-recovery" / "metadata").iterdir()).unlink()
    next((tmp_path / "conformance-recovery" / "receipts").iterdir()).unlink()
    recovered = await recovery_adapter.recover_committed_store(recovery_request)
    assert recovered.provider_artifact_id == recovery_stored.provider_artifact_id
    assert recovered.replayed is True
    executed.add("recover_confirmed_store")

    range_adapter = LocalStorageAdapter(root=tmp_path / "ranges", buffer_bytes=2)
    ranged = await range_adapter.store(
        byte_stream(b"data"), store_request(key="ranges", maximum_bytes=4)
    )
    assert b"".join(
        [chunk async for chunk in range_adapter.open(ranged.provider_artifact_id, ArtifactByteRange(4))]
    ) == b""
    executed.add("open_offset_at_eof")
    with pytest.raises(ArtifactMalformedRequestError) as malformed:
        b"".join(
            [
                chunk
                async for chunk in range_adapter.open(
                    ranged.provider_artifact_id, ArtifactByteRange(5)
                )
            ]
        )
    assert malformed.value.code == vectors["open_offset_past_eof"]["expected_error"]
    executed.add("open_offset_past_eof")
    assert b"".join(
        [
            chunk
            async for chunk in range_adapter.open(
                ranged.provider_artifact_id, ArtifactByteRange(1, 2)
            )
        ]
    ) == b"at"
    executed.add("open_exclusive_end")

    release_request_identity = release_identity(
        ranged.provider_artifact_id,
        "unknown",
        key="conformance-release",
    )
    with pytest.raises(ArtifactRetentionConflictError) as retention_conflict:
        await range_adapter.release(
            ranged.provider_artifact_id, "unknown", release_request_identity
        )
    assert retention_conflict.value.code == vectors["release_requires_exact_reference"][
        "expected_error"
    ]
    executed.add("release_requires_exact_reference")

    receipt = await adapter.get_operation_receipt(
        request.idempotency.service_principal,
        ArtifactOperation.STORE,
        request.idempotency.key,
    )
    assert receipt is not None and receipt.receipt_id == stored.receipt.receipt_id
    executed.add("receipt_lookup_full_identity")

    truncated = store_request(
        key="truncated", expected_size=4, maximum_bytes=4
    )
    with pytest.raises(ArtifactInputMismatchError) as truncated_store:
        await adapter.store(byte_stream(b"abc"), truncated)
    assert truncated_store.value.code == vectors["truncated_store_stream"]["expected_error"]
    executed.add("truncated_store_stream")

    object_path = next((tmp_path / "ranges" / "objects").iterdir())
    object_path.write_bytes(b"abc")
    with pytest.raises(ArtifactIntegrityError) as truncated_open:
        b"".join([chunk async for chunk in range_adapter.open(ranged.provider_artifact_id)])
    assert truncated_open.value.code == vectors["truncated_open_stream"]["expected_error"]
    executed.add("truncated_open_stream")

    assert executed == set(vectors)


@pytest.mark.asyncio
async def test_local_adapter_store_open_range_replay_and_restart(tmp_path: Path) -> None:
    """Store once, stream ranges, replay exactly, and survive adapter restart."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    request = store_request(maximum_bytes=5)
    stored = await adapter.store(byte_stream(b"hello"), request)

    assert stored.byte_count == 5
    assert stored.sha256 == "sha256:" + hashlib.sha256(b"hello").hexdigest()
    assert stored.receipt.response_digest == canonical_json_hash(
        {
            "byte_count": stored.byte_count,
            "outcome": "stored",
            "provider_artifact_id": stored.provider_artifact_id,
            "provider_operation_id": stored.receipt.provider_operation_reference,
            "receipt_id": stored.receipt.receipt_id,
            "sha256": stored.sha256,
        }
    )
    read_chunks = [chunk async for chunk in adapter.open(stored.provider_artifact_id)]
    assert b"".join(read_chunks) == b"hello"
    assert max(map(len, read_chunks)) <= 2
    assert b"".join(
        [
            chunk
            async for chunk in adapter.open(
                stored.provider_artifact_id, ArtifactByteRange(offset=1, length=2)
            )
        ]
    ) == b"el"
    assert b"".join(
        [
            chunk
            async for chunk in adapter.open(
                stored.provider_artifact_id, ArtifactByteRange(offset=5)
            )
        ]
    ) == b""
    with pytest.raises(ArtifactMalformedRequestError):
        b"".join(
            [
                chunk
                async for chunk in adapter.open(
                    stored.provider_artifact_id, ArtifactByteRange(offset=6)
                )
            ]
        )

    replay = await adapter.store(byte_stream(b"hello"), request)
    restarted = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    restarted_replay = await restarted.store(byte_stream(b"hello"), request)
    assert replay.provider_artifact_id == stored.provider_artifact_id
    assert restarted_replay.receipt.provider_operation_reference == (
        stored.receipt.provider_operation_reference
    )
    assert len(list((tmp_path / "artifacts" / "objects").iterdir())) == 1


@pytest.mark.asyncio
async def test_no_commitment_replay_is_fully_consumed_and_mismatch_quarantines(
    tmp_path: Path,
) -> None:
    """Require complete no-commitment replay and quarantine changed bytes."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    request = store_request(maximum_bytes=8)
    stored = await adapter.store(byte_stream(b"abcd"), request)
    consumed: list[bytes] = []

    async def changed_replay() -> AsyncIterator[bytes]:
        for chunk in (b"ab", b"XY"):
            consumed.append(chunk)
            yield chunk

    with pytest.raises(ArtifactIntegrityError):
        await adapter.store(changed_replay(), request)
    assert consumed == [b"ab", b"XY"]
    status = await adapter.stat(stored.provider_artifact_id)
    assert status.integrity_state == IntegrityState.QUARANTINED
    with pytest.raises(ArtifactNotFoundError, match="unavailable"):
        b"".join([chunk async for chunk in adapter.open(stored.provider_artifact_id)])


@pytest.mark.asyncio
async def test_request_digest_conflict_does_not_consume_or_duplicate(tmp_path: Path) -> None:
    """Reject changed request metadata before reading replay bytes."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    await adapter.store(byte_stream(b"same"), store_request(key="one"))
    consumed = False

    async def should_not_run() -> AsyncIterator[bytes]:
        nonlocal consumed
        consumed = True
        yield b"same"

    with pytest.raises(ArtifactIdempotencyMismatchError):
        await adapter.store(
            should_not_run(), store_request(key="one", request_value="changed")
        )
    assert consumed is False
    assert len(list((tmp_path / "artifacts" / "objects").iterdir())) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("payload", "maximum", "fails"),
    [(b"", 0, False), (b"abcd", 4, False), (b"abcde", 4, True)],
)
async def test_local_adapter_empty_boundary_and_oversize_cleanup(
    tmp_path: Path, payload: bytes, maximum: int, fails: bool
) -> None:
    """Apply exact byte limits and remove every oversized temporary file."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    request = store_request(key=f"limit-{len(payload)}", maximum_bytes=maximum)
    if fails:
        with pytest.raises(ArtifactLimitExceededError):
            await adapter.store(byte_stream(payload), request)
        assert list((tmp_path / "artifacts" / "objects").iterdir()) == []
    else:
        stored = await adapter.store(byte_stream(payload), request)
        assert stored.byte_count == len(payload)
    assert list((tmp_path / "artifacts" / "tmp").iterdir()) == []


@pytest.mark.asyncio
async def test_local_adapter_disk_failure_cleans_temp_and_redacts_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Convert disk failure to a stable path-free error and remove partial bytes."""
    adapter = LocalStorageAdapter(root=tmp_path / "private-secret", buffer_bytes=2)

    def fail_write(descriptor: int, chunk: memoryview) -> None:
        raise OSError("disk full at /private-secret")

    monkeypatch.setattr(adapter, "_write_all", fail_write)
    with pytest.raises(ArtifactStoreUnavailableError) as raised:
        await adapter.store(byte_stream(b"data"), store_request())
    assert "/private-secret" not in str(raised.value)
    assert list((tmp_path / "private-secret" / "tmp").iterdir()) == []
    assert list((tmp_path / "private-secret" / "objects").iterdir()) == []


@pytest.mark.asyncio
async def test_local_adapter_cancellation_waits_for_io_then_cleans_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Wait for an in-flight thread write before cancellation cleanup."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    started = threading.Event()
    release = threading.Event()
    original_write = adapter._write_all

    def delayed_write(descriptor: int, chunk: memoryview) -> None:
        if bytes(chunk) == b"da":
            started.set()
            release.wait(timeout=5)
        original_write(descriptor, chunk)

    monkeypatch.setattr(adapter, "_write_all", delayed_write)
    task = asyncio.create_task(
        adapter.store(byte_stream(b"data"), store_request(key="cancelled"))
    )
    assert await asyncio.to_thread(started.wait, 5)
    task.cancel()
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert list((tmp_path / "artifacts" / "tmp").iterdir()) == []
    assert list((tmp_path / "artifacts" / "objects").iterdir()) == []
    monkeypatch.setattr(adapter, "_write_all", original_write)
    recovered = await adapter.store(
        byte_stream(b"data"), store_request(key="cancelled")
    )
    assert recovered.replayed is True
    assert recovered.byte_count == 4


@pytest.mark.asyncio
async def test_cancellation_while_waiting_for_lock_does_not_clean_another_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Do not clean provider state when cancellation happened before lock ownership."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    request = store_request(key="waiting-cancellation")
    scope = adapter._scope_key(request.idempotency)
    held_lock = adapter._acquire_lock(scope)
    cleanup_calls = 0
    original_cleanup = adapter._cleanup_unpublished

    async def track_cleanup(cleanup_scope: str) -> None:
        nonlocal cleanup_calls
        cleanup_calls += 1
        await original_cleanup(cleanup_scope)

    monkeypatch.setattr(adapter, "_cleanup_unpublished", track_cleanup)
    task = asyncio.create_task(adapter.store(byte_stream(b"data"), request))
    await asyncio.sleep(0.05)
    task.cancel()
    await asyncio.to_thread(adapter._release_lock, held_lock)
    with pytest.raises(asyncio.CancelledError):
        await task
    assert cleanup_calls == 0


@pytest.mark.asyncio
async def test_local_adapter_publish_failure_leaves_no_partial_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Remove the completed temporary object if exclusive publication fails."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)

    def fail_publish(temporary: Path, final: Path) -> None:
        raise OSError("publish failed at a private path")

    monkeypatch.setattr(adapter, "_publish_exclusive", fail_publish)
    with pytest.raises(ArtifactStoreUnavailableError, match="local artifact operation failed"):
        await adapter.store(byte_stream(b"data"), store_request(key="publish-failure"))
    assert list((tmp_path / "artifacts" / "tmp").iterdir()) == []
    assert list((tmp_path / "artifacts" / "objects").iterdir()) == []


@pytest.mark.asyncio
async def test_local_adapter_fsync_and_publication_fault_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recover deterministically from file, directory, metadata, and receipt faults."""
    file_root = tmp_path / "file-fsync"
    file_adapter = LocalStorageAdapter(root=file_root, buffer_bytes=2)
    original_fsync = os.fsync

    create_root = tmp_path / "create-fault"
    create_adapter = LocalStorageAdapter(root=create_root, buffer_bytes=2)

    def fail_create(path: Path) -> int:
        del path
        raise OSError("temporary create failed")

    monkeypatch.setattr(create_adapter, "_open_exclusive", fail_create)
    with pytest.raises(OSError, match="temporary create"):
        await create_adapter._write_stream(
            byte_stream(b"data"), "art_" + "2" * 32, store_request(key="create-fault")
        )
    assert list((create_root / "tmp").iterdir()) == []

    write_root = tmp_path / "bounded-write"
    write_adapter = LocalStorageAdapter(root=write_root, buffer_bytes=2)
    write_sizes: list[int] = []
    original_write = write_adapter._write_all

    def track_write(descriptor: int, chunk: memoryview) -> None:
        write_sizes.append(len(chunk))
        original_write(descriptor, chunk)

    monkeypatch.setattr(write_adapter, "_write_all", track_write)
    await write_adapter._write_stream(
        byte_stream(b"hello"), "art_" + "3" * 32, store_request(key="bounded-write")
    )
    assert write_sizes == [2, 2, 1]

    def fail_file_fsync(descriptor: int) -> None:
        if stat_module.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError("file fsync failed")
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_file_fsync)
    with pytest.raises(OSError, match="file fsync"):
        await file_adapter._write_stream(
            byte_stream(b"data"), "art_" + "1" * 32, store_request(key="file-fsync")
        )
    assert list((file_root / "tmp").iterdir()) == []
    assert list((file_root / "objects").iterdir()) == []
    monkeypatch.setattr(os, "fsync", original_fsync)

    directory_root = tmp_path / "directory-fsync"
    directory_adapter = LocalStorageAdapter(root=directory_root, buffer_bytes=2)
    directory_failed = False

    def fail_published_directory_fsync(descriptor: int) -> None:
        nonlocal directory_failed
        if (
            not directory_failed
            and stat_module.S_ISDIR(os.fstat(descriptor).st_mode)
            and any((directory_root / "objects").iterdir())
        ):
            directory_failed = True
            raise OSError("directory fsync failed")
        original_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_published_directory_fsync)
    directory_request = store_request(key="directory-fsync")
    with pytest.raises(ArtifactStoreUnavailableError):
        await directory_adapter.store(byte_stream(b"data"), directory_request)
    monkeypatch.setattr(os, "fsync", original_fsync)
    directory_recovered = await directory_adapter.store(
        byte_stream(b"data"), directory_request
    )
    assert directory_recovered.replayed is True

    for fault_directory in ("metadata", "receipts"):
        root = tmp_path / f"publish-{fault_directory}"
        adapter = LocalStorageAdapter(root=root, buffer_bytes=2)
        request = store_request(key=f"publish-{fault_directory}")
        original_publish = adapter._write_json_exclusive
        failed = False

        async def fail_publish_once(path: Path, value: dict) -> None:
            nonlocal failed
            if path.parent.name == fault_directory and not failed:
                failed = True
                raise OSError(f"{fault_directory} publication failed")
            await original_publish(path, value)

        monkeypatch.setattr(adapter, "_write_json_exclusive", fail_publish_once)
        with pytest.raises(ArtifactStoreUnavailableError):
            await adapter.store(byte_stream(b"data"), request)
        monkeypatch.setattr(adapter, "_write_json_exclusive", original_publish)
        recovered = await adapter.store(byte_stream(b"data"), request)
        assert recovered.replayed is True


@pytest.mark.asyncio
async def test_local_adapter_verify_read_and_quarantine_faults_are_typed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Return stable errors for verify-read and quarantine storage failures."""
    verify_root = tmp_path / "verify-read"
    verify_adapter = LocalStorageAdapter(root=verify_root, buffer_bytes=2)
    stored = await verify_adapter.store(byte_stream(b"data"), store_request())

    def fail_open(provider_id: str):
        del provider_id
        raise OSError("verify read failed")

    monkeypatch.setattr(verify_adapter, "_open_regular_object", fail_open)
    with pytest.raises(ArtifactStoreUnavailableError):
        await verify_adapter.verify(
            stored.provider_artifact_id,
            stored.sha256,
            stored.byte_count,
            verify_identity(stored.provider_artifact_id, stored.sha256, stored.byte_count),
        )

    quarantine_root = tmp_path / "quarantine-fault"
    quarantine_adapter = LocalStorageAdapter(root=quarantine_root, buffer_bytes=2)
    request = store_request(
        key="quarantine-fault",
        expected_sha256="sha256:" + hashlib.sha256(b"data").hexdigest(),
    )
    await quarantine_adapter.store(byte_stream(b"data"), request)
    next((quarantine_root / "objects").iterdir()).write_bytes(b"evil")
    original_move = quarantine_adapter._move_to_quarantine

    def fail_quarantine(source: Path, target: Path) -> None:
        del source, target
        raise OSError("quarantine failed")

    monkeypatch.setattr(quarantine_adapter, "_move_to_quarantine", fail_quarantine)
    with pytest.raises(ArtifactStoreUnavailableError):
        await quarantine_adapter.store(byte_stream(b"data"), request)
    monkeypatch.setattr(quarantine_adapter, "_move_to_quarantine", original_move)
    with pytest.raises(ArtifactIntegrityError):
        await quarantine_adapter.store(byte_stream(b"data"), request)


@pytest.mark.asyncio
async def test_reconciliation_hash_enforces_request_byte_ceiling(tmp_path: Path) -> None:
    """Stop provider reconciliation as soon as bytes exceed the persisted ceiling."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    stored = await adapter.store(byte_stream(b"data"), store_request())
    service = ArtifactIngestService(None, adapter, adapter_name="local")  # type: ignore[arg-type]
    observed_sha256, observed_size = await service._hash_provider_object(
        stored.provider_artifact_id, 4
    )
    assert (observed_sha256, observed_size) == (stored.sha256, stored.byte_count)
    with pytest.raises(ArtifactIntegrityError, match="exceed"):
        await service._hash_provider_object(stored.provider_artifact_id, 3)

    with pytest.raises(ArtifactInputMismatchError, match="exact commitment"):
        await adapter.recover_committed_store(store_request(key="recovery-without-commitment"))
    exact_request = store_request(
        key="recovery-without-intent",
        expected_sha256=stored.sha256,
        expected_size=stored.byte_count,
    )
    with pytest.raises(ArtifactIntegrityError, match="intent"):
        await adapter.recover_committed_store(exact_request)


@pytest.mark.asyncio
async def test_local_adapter_retain_release_verify_and_permissions(tmp_path: Path) -> None:
    """Verify bytes, reference-count retention, and preserve private modes."""
    root = tmp_path / "artifacts"
    adapter = LocalStorageAdapter(root=root, buffer_bytes=2)
    stored = await adapter.store(byte_stream(b"data"), store_request())
    verify_request_identity = verify_identity(
        stored.provider_artifact_id, stored.sha256, stored.byte_count
    )
    await adapter.verify(
        stored.provider_artifact_id, stored.sha256, stored.byte_count, verify_request_identity
    )
    retain_request_identity = retain_identity(
        stored.provider_artifact_id, "ref-1", "evaluation"
    )
    await adapter.retain(
        stored.provider_artifact_id, "ref-1", "evaluation", retain_request_identity
    )
    replayed_retain = await adapter.retain(
        stored.provider_artifact_id, "ref-1", "evaluation", retain_request_identity
    )
    assert replayed_retain.receipt.provider_operation_reference is not None
    assert replayed_retain.replayed is True
    active = (await adapter.stat(stored.provider_artifact_id)).active_retentions
    assert [(item.retention_reference, item.retention_class, item.state) for item in active] == [
        ("ref-1", "evaluation", "active")
    ]
    release_request_identity = release_identity(stored.provider_artifact_id, "ref-1")
    await adapter.release(stored.provider_artifact_id, "ref-1", release_request_identity)
    assert (await adapter.stat(stored.provider_artifact_id)).active_retentions == ()
    assert os.stat(root).st_mode & 0o777 == 0o700
    assert all(path.stat().st_mode & 0o777 == 0o600 for path in (root / "objects").iterdir())


@pytest.mark.asyncio
async def test_concurrent_retention_preserves_ownership_and_all_references(
    tmp_path: Path,
) -> None:
    """Serialize retention changes per artifact and enforce the creating principal."""
    root = tmp_path / "artifacts"
    first = LocalStorageAdapter(root=root, buffer_bytes=2)
    second = LocalStorageAdapter(root=root, buffer_bytes=2)
    stored = await first.store(byte_stream(b"data"), store_request())

    def identity(principal: str, key: str, reference: str) -> IdempotencyIdentity:
        return retain_identity(
            stored.provider_artifact_id,
            reference,
            "evaluation" if reference == "ref-a" else "review",
            key=key,
            principal=principal,
        )

    await asyncio.gather(
        first.retain(
            stored.provider_artifact_id,
            "ref-a",
            "evaluation",
            identity("workstream.artifact.a", "retain-a", "ref-a"),
        ),
        second.retain(
            stored.provider_artifact_id,
            "ref-b",
            "review",
            identity("workstream.artifact.b", "retain-b", "ref-b"),
        ),
    )
    assert [item.retention_reference for item in (await first.stat(stored.provider_artifact_id)).active_retentions] == [
        "ref-a",
        "ref-b",
    ]
    wrong_owner = release_identity(
        stored.provider_artifact_id,
        "ref-a",
        key="release-a",
        principal="workstream.artifact.b",
    )
    with pytest.raises(ArtifactRetentionConflictError, match="owner"):
        await second.release(stored.provider_artifact_id, "ref-a", wrong_owner)


@pytest.mark.asyncio
async def test_verify_and_retain_serialize_without_losing_metadata(tmp_path: Path) -> None:
    """Preserve both verification and retention facts under concurrent mutation."""
    root = tmp_path / "artifacts"
    first = LocalStorageAdapter(root=root, buffer_bytes=2)
    second = LocalStorageAdapter(root=root, buffer_bytes=2)
    stored = await first.store(byte_stream(b"data"), store_request())
    await asyncio.gather(
        first.verify(
            stored.provider_artifact_id,
            stored.sha256,
            stored.byte_count,
            verify_identity(stored.provider_artifact_id, stored.sha256, stored.byte_count),
        ),
        second.retain(
            stored.provider_artifact_id,
            "concurrent-review",
            "review",
            retain_identity(stored.provider_artifact_id, "concurrent-review", "review"),
        ),
    )
    status = await first.stat(stored.provider_artifact_id)
    assert status.verification_state.value == "verified"
    assert [retention.retention_reference for retention in status.active_retentions] == [
        "concurrent-review"
    ]


@pytest.mark.asyncio
async def test_retention_retry_recovers_after_receipt_publication_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recover the same retention effect after metadata commits before its receipt."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    stored = await adapter.store(byte_stream(b"data"), store_request())
    identity = retain_identity(
        stored.provider_artifact_id,
        "ref-crash",
        "evaluation",
        key="retain-crash",
    )
    original = adapter._write_json_exclusive
    failed = False

    async def fail_receipt_once(path: Path, value: dict) -> None:
        nonlocal failed
        if path.parent.name == "receipts" and not failed:
            failed = True
            raise OSError("simulated receipt publication failure")
        await original(path, value)

    monkeypatch.setattr(adapter, "_write_json_exclusive", fail_receipt_once)
    with pytest.raises(ArtifactStoreUnavailableError):
        await adapter.retain(
            stored.provider_artifact_id, "ref-crash", "evaluation", identity
        )
    recovered = await adapter.retain(
        stored.provider_artifact_id, "ref-crash", "evaluation", identity
    )
    assert recovered.receipt.retention_reference == "ref-crash"
    assert len((await adapter.stat(stored.provider_artifact_id)).active_retentions) == 1


@pytest.mark.asyncio
async def test_expected_commitment_recovers_object_only_provider_state(tmp_path: Path) -> None:
    """Rebuild metadata and receipt only after hashing committed provider bytes."""
    root = tmp_path / "artifacts"
    adapter = LocalStorageAdapter(root=root, buffer_bytes=2)
    expected = "sha256:" + hashlib.sha256(b"data").hexdigest()
    request = store_request(expected_sha256=expected, expected_size=4)
    stored = await adapter.store(byte_stream(b"data"), request)
    next((root / "metadata").iterdir()).unlink()
    next((root / "receipts").iterdir()).unlink()

    restarted = LocalStorageAdapter(root=root, buffer_bytes=2)
    recovered = await restarted.recover_committed_store(request)
    assert recovered.provider_artifact_id == stored.provider_artifact_id
    assert recovered.sha256 == expected
    assert recovered.receipt.outcome.value == "stored"
    assert recovered.replayed is True


@pytest.mark.asyncio
async def test_altered_object_and_receipt_are_quarantined(tmp_path: Path) -> None:
    """Deny promotion and access when persisted provider facts are altered."""
    root = tmp_path / "artifacts"
    adapter = LocalStorageAdapter(root=root, buffer_bytes=2)
    request = store_request(expected_sha256="sha256:" + hashlib.sha256(b"data").hexdigest())
    await adapter.store(byte_stream(b"data"), request)
    object_path = next((root / "objects").iterdir())
    object_path.write_bytes(b"evil")
    with pytest.raises(ArtifactIntegrityError):
        await adapter.store(byte_stream(b"data"), request)
    assert (root / "quarantine" / object_path.name).exists()

    second_root = tmp_path / "receipt-artifacts"
    second = LocalStorageAdapter(root=second_root, buffer_bytes=2)
    second_request = store_request(key="receipt", expected_sha256=request.expected_sha256)
    second_stored = await second.store(byte_stream(b"data"), second_request)
    receipt_path = next((second_root / "receipts").iterdir())
    receipt_payload = json.loads(receipt_path.read_text())
    receipt_payload["response_digest"] = "sha256:" + "f" * 64
    receipt_path.write_text(json.dumps(receipt_payload))
    with pytest.raises(ArtifactIntegrityError):
        await second.store(byte_stream(b"data"), second_request)
    assert (await second.stat(second_stored.provider_artifact_id)).integrity_state == (
        IntegrityState.QUARANTINED
    )

    third_root = tmp_path / "receipt-identity-artifacts"
    third = LocalStorageAdapter(root=third_root, buffer_bytes=2)
    third_request = store_request(key="receipt-identity", expected_sha256=request.expected_sha256)
    third_stored = await third.store(byte_stream(b"data"), third_request)
    third_receipt_path = next((third_root / "receipts").iterdir())
    third_receipt = json.loads(third_receipt_path.read_text())
    third_receipt["receipt_id"] = "receipt_" + "a" * 32
    third_receipt_path.write_text(json.dumps(third_receipt))
    with pytest.raises(ArtifactIntegrityError, match="receipt is invalid"):
        await third.store(byte_stream(b"data"), third_request)
    assert (await third.stat(third_stored.provider_artifact_id)).integrity_state == (
        IntegrityState.QUARANTINED
    )

    fourth_root = tmp_path / "receipt-principal-artifacts"
    fourth = LocalStorageAdapter(root=fourth_root, buffer_bytes=2)
    fourth_request = store_request(key="receipt-principal")
    fourth_stored = await fourth.store(byte_stream(b"data"), fourth_request)
    fourth_receipt_path = next((fourth_root / "receipts").iterdir())
    fourth_receipt = json.loads(fourth_receipt_path.read_text())
    fourth_receipt["service_principal"] = "INVALID PRINCIPAL"
    fourth_receipt_path.write_text(json.dumps(fourth_receipt))
    with pytest.raises(ArtifactIntegrityError, match="receipt is invalid"):
        await fourth.store(byte_stream(b"data"), fourth_request)
    assert (await fourth.stat(fourth_stored.provider_artifact_id)).integrity_state == (
        IntegrityState.QUARANTINED
    )


@pytest.mark.asyncio
async def test_verify_mismatch_and_invalid_retention_reference_fail_closed(tmp_path: Path) -> None:
    """Quarantine failed full verification and reject unknown release references."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    stored = await adapter.store(byte_stream(b"data"), store_request())
    missing_release_identity = release_identity(
        stored.provider_artifact_id,
        "missing",
        key="missing-release",
    )
    with pytest.raises(ArtifactRetentionConflictError, match="not active"):
        await adapter.release(stored.provider_artifact_id, "missing", missing_release_identity)

    bad_verify_identity = verify_identity(
        stored.provider_artifact_id,
        "sha256:" + "0" * 64,
        4,
        key="bad-verify",
    )
    with pytest.raises(ArtifactIntegrityError):
        await adapter.verify(
            stored.provider_artifact_id, "sha256:" + "0" * 64, 4, bad_verify_identity
        )
    assert (await adapter.stat(stored.provider_artifact_id)).integrity_state == (
        IntegrityState.QUARANTINED
    )


@pytest.mark.asyncio
async def test_receipt_lookup_and_request_validation(tmp_path: Path) -> None:
    """Scope receipt lookup fully and reject malformed requests before I/O."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    request = store_request()
    stored = await adapter.store(byte_stream(b"data"), request)
    receipt = await adapter.get_operation_receipt(
        request.idempotency.service_principal,
        ArtifactOperation.STORE,
        request.idempotency.key,
    )
    assert receipt is not None
    assert receipt.provider_operation_reference == stored.receipt.provider_operation_reference
    assert (
        await adapter.get_operation_receipt(
            request.idempotency.service_principal, ArtifactOperation.STORE, "unknown"
        )
        is None
    )
    with pytest.raises(ArtifactMalformedRequestError):
        await adapter.store(byte_stream(b"x"), store_request(maximum_bytes=-1))
    with pytest.raises(ArtifactMalformedRequestError):
        await adapter.store(
            byte_stream(b"x"),
            store_request(expected_sha256="SHA256:" + "0" * 64),
        )
    malformed = store_request(key="bad-digest")
    malformed = replace(
        malformed,
        idempotency=replace(malformed.idempotency, request_digest="sha256:" + "f" * 64),
    )
    with pytest.raises(ArtifactIdempotencyMismatchError, match="not canonical"):
        await adapter.store(byte_stream(b"x"), malformed)
    with pytest.raises(ArtifactMalformedRequestError, match="media type"):
        await adapter.store(
            byte_stream(b"x"), replace(store_request(key="bad-media"), media_type="")
        )
    with pytest.raises(ArtifactMalformedRequestError, match="metadata"):
        await adapter.store(
            byte_stream(b"x"),
            replace(store_request(key="bad-metadata"), metadata={"bad name": "value"}),
        )
    with pytest.raises(ArtifactNotFoundError):
        await adapter.stat("../private")
    missing_provider_id = "art_" + "0" * 32
    missing_verify = verify_identity(
        missing_provider_id,
        "sha256:" + "0" * 64,
        0,
        key="missing-verify",
    )
    with pytest.raises(ArtifactNotFoundError) as missing_error:
        await adapter.verify(missing_provider_id, "sha256:" + "0" * 64, 0, missing_verify)
    assert str(tmp_path) not in str(missing_error.value)


@pytest.mark.asyncio
async def test_recovery_missing_and_changed_provider_state_fails_closed(tmp_path: Path) -> None:
    """Reject receipt-only and changed object-only recovery states."""
    expected = "sha256:" + hashlib.sha256(b"data").hexdigest()

    missing_root = tmp_path / "missing"
    missing = LocalStorageAdapter(root=missing_root, buffer_bytes=2)
    missing_request = store_request(key="missing", expected_sha256=expected, expected_size=4)
    await missing.store(byte_stream(b"data"), missing_request)
    next((missing_root / "objects").iterdir()).unlink()
    next((missing_root / "metadata").iterdir()).unlink()
    with pytest.raises(ArtifactIntegrityError, match="receipt has no committed object"):
        await missing.store(byte_stream(b"data"), missing_request)

    status_root = tmp_path / "missing-status"
    status_adapter = LocalStorageAdapter(root=status_root, buffer_bytes=2)
    status_stored = await status_adapter.store(
        byte_stream(b"data"), store_request(key="missing-status")
    )
    next((status_root / "objects").iterdir()).unlink()
    status = await status_adapter.stat(status_stored.provider_artifact_id)
    assert status.availability_state.value == "missing"
    assert status.integrity_state.value == "unknown"

    replay_root = tmp_path / "replay-metadata"
    replay = LocalStorageAdapter(root=replay_root, buffer_bytes=2)
    replay_request = store_request(key="no-metadata")
    await replay.store(byte_stream(b"data"), replay_request)
    next((replay_root / "metadata").iterdir()).unlink()
    recovered = await replay.store(byte_stream(b"data"), replay_request)
    assert recovered.replayed is True
    assert recovered.sha256 == expected

    changed_root = tmp_path / "changed"
    changed = LocalStorageAdapter(root=changed_root, buffer_bytes=2)
    changed_request = store_request(key="changed", expected_sha256=expected, expected_size=4)
    stored = await changed.store(byte_stream(b"data"), changed_request)
    next((changed_root / "metadata").iterdir()).unlink()
    next((changed_root / "receipts").iterdir()).unlink()
    next((changed_root / "objects").iterdir()).write_bytes(b"evil")
    with pytest.raises(ArtifactIntegrityError, match="commitment"):
        await changed.store(byte_stream(b"data"), changed_request)
    assert (changed_root / "quarantine" / f"{stored.provider_artifact_id}.blob").exists()

    size_root = tmp_path / "changed-size"
    changed_size = LocalStorageAdapter(root=size_root, buffer_bytes=2)
    size_request = store_request(key="size", expected_sha256=expected, expected_size=4)
    size_stored = await changed_size.store(byte_stream(b"data"), size_request)
    next((size_root / "metadata").iterdir()).unlink()
    next((size_root / "receipts").iterdir()).unlink()
    intent_path = next((size_root / "intents").iterdir())
    intent = json.loads(intent_path.read_text())
    intent["expected_size"] = 5
    intent_path.write_text(json.dumps(intent))
    with pytest.raises(ArtifactIntegrityError, match="size does not match"):
        await changed_size.store(byte_stream(b"data"), size_request)
    assert (size_root / "quarantine" / f"{size_stored.provider_artifact_id}.blob").exists()


@pytest.mark.asyncio
async def test_retention_class_conflict_and_verify_replay(tmp_path: Path) -> None:
    """Reject changed retention ownership and replay one verify receipt."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
    stored = await adapter.store(byte_stream(b"data"), store_request())
    first = retain_identity(
        stored.provider_artifact_id,
        "same-ref",
        "one",
        key="retain-a",
    )
    await adapter.retain(stored.provider_artifact_id, "same-ref", "one", first)
    conflicting = retain_identity(
        stored.provider_artifact_id,
        "same-ref",
        "two",
        key="retain-b",
    )
    with pytest.raises(ArtifactIdempotencyMismatchError, match="class changed"):
        await adapter.retain(stored.provider_artifact_id, "same-ref", "two", conflicting)

    verify_request_identity = verify_identity(
        stored.provider_artifact_id,
        stored.sha256,
        stored.byte_count,
        key="verify-replay",
    )
    first_result = await adapter.verify(
        stored.provider_artifact_id, stored.sha256, stored.byte_count, verify_request_identity
    )
    replay = await adapter.verify(
        stored.provider_artifact_id, stored.sha256, stored.byte_count, verify_request_identity
    )
    assert replay.receipt.provider_operation_reference == (
        first_result.receipt.provider_operation_reference
    )
    assert replay.replayed is True


@pytest.mark.asyncio
async def test_truncated_object_and_malformed_metadata_are_integrity_failures(
    tmp_path: Path,
) -> None:
    """Detect short object streams and non-object provider metadata."""
    root = tmp_path / "artifacts"
    adapter = LocalStorageAdapter(root=root, buffer_bytes=2)
    stored = await adapter.store(byte_stream(b"data"), store_request())
    next((root / "objects").iterdir()).write_bytes(b"d")
    with pytest.raises(ArtifactIntegrityError, match="ended"):
        b"".join([chunk async for chunk in adapter.open(stored.provider_artifact_id)])

    metadata_path = next((root / "metadata").iterdir())
    metadata_path.write_text("[]")
    with pytest.raises(ArtifactIntegrityError, match="metadata"):
        await adapter.stat(stored.provider_artifact_id)
    malformed_quarantine = await adapter.stat(stored.provider_artifact_id)
    assert malformed_quarantine.integrity_state == IntegrityState.QUARANTINED
    assert malformed_quarantine.availability_state.value == "unavailable"

    state_root = tmp_path / "invalid-state"
    state_adapter = LocalStorageAdapter(root=state_root, buffer_bytes=2)
    state_stored = await state_adapter.store(
        byte_stream(b"data"), store_request(key="invalid-state")
    )
    state_metadata_path = next((state_root / "metadata").iterdir())
    state_metadata = json.loads(state_metadata_path.read_text())
    state_metadata["verification_state"] = "corrupt"
    state_metadata_path.write_text(json.dumps(state_metadata))
    with pytest.raises(ArtifactIntegrityError, match="metadata"):
        await state_adapter.stat(state_stored.provider_artifact_id)
    quarantined = await state_adapter.stat(state_stored.provider_artifact_id)
    assert quarantined.integrity_state == IntegrityState.QUARANTINED


@pytest.mark.asyncio
async def test_stream_and_operation_validation_rejects_invalid_inputs(tmp_path: Path) -> None:
    """Reject invalid stream values, sizes, and operation identities."""
    adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)

    async def invalid_stream() -> AsyncIterator[bytes]:
        yield "not-bytes"  # type: ignore[misc]

    with pytest.raises(ArtifactInputMismatchError, match="yield bytes"):
        await adapter.store(invalid_stream(), store_request(key="invalid-stream"))
    with pytest.raises(ArtifactMalformedRequestError, match="expected artifact size"):
        await adapter.store(
            byte_stream(b"x"), store_request(key="negative-size", expected_size=-1)
        )
    wrong_operation = IdempotencyIdentity(
        "workstream.artifact.ingest",
        ArtifactOperation.RETAIN,
        "wrong-operation",
        canonical_json_hash({"wrong": True}),
    )
    invalid_request = StoreArtifactRequest(
        None, None, 4, "application/octet-stream", {}, wrong_operation
    )
    with pytest.raises(ArtifactMalformedRequestError, match="operation identity"):
        await adapter.store(byte_stream(b"x"), invalid_request)
    with pytest.raises(ValueError, match="nonnegative"):
        ArtifactByteRange(offset=-1)

    stored = await adapter.store(byte_stream(b"x"), store_request(key="validation-object"))
    negative_verify_identity = verify_identity(
        stored.provider_artifact_id,
        stored.sha256,
        -1,
        key="negative-verify",
    )
    with pytest.raises(ArtifactMalformedRequestError, match="size must be nonnegative"):
        await adapter.verify(
            stored.provider_artifact_id, stored.sha256, -1, negative_verify_identity
        )
    empty_retain_identity = retain_identity(
        stored.provider_artifact_id,
        "empty-placeholder",
        "evaluation",
        key="empty-reference",
    )
    with pytest.raises(ArtifactMalformedRequestError, match="reference is invalid"):
        await adapter.retain(
            stored.provider_artifact_id, "", "evaluation", empty_retain_identity
        )
    long_principal_identity = retain_identity(
        stored.provider_artifact_id,
        "long-principal",
        "evaluation",
        principal="a" * 101,
    )
    with pytest.raises(ArtifactMalformedRequestError, match="service principal"):
        await adapter.retain(
            stored.provider_artifact_id,
            "long-principal",
            "evaluation",
            long_principal_identity,
        )
    assert (await adapter.stat(stored.provider_artifact_id)).active_retentions == ()


def test_local_adapter_rejects_invalid_buffer(tmp_path: Path) -> None:
    """Keep configured local I/O inside the one MiB ceiling."""
    with pytest.raises(ValueError, match="1 MiB"):
        LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=0)


def test_local_adapter_rejects_symlink_root(tmp_path: Path) -> None:
    """Reject a configured root that redirects through a symlink."""
    real = tmp_path / "real"
    real.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(real, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        LocalStorageAdapter(root=linked)


@pytest.mark.asyncio
async def test_local_adapter_rejects_runtime_subdirectory_replacement(tmp_path: Path) -> None:
    """Keep operations under the pinned root after a subdirectory replacement."""
    root = tmp_path / "artifacts"
    adapter = LocalStorageAdapter(root=root, buffer_bytes=2)
    stored = await adapter.store(byte_stream(b"data"), store_request())
    metadata = root / "metadata"
    original = root / "metadata-original"
    metadata.rename(original)
    outside = tmp_path / "outside"
    outside.mkdir()
    metadata.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ArtifactIntegrityError):
        await adapter.stat(stored.provider_artifact_id)
    assert list(outside.iterdir()) == []


@pytest.mark.asyncio
async def test_local_adapter_startup_cleans_locked_abandoned_object_temp(tmp_path: Path) -> None:
    """Remove only stale object temporary files associated with durable intent."""
    root = tmp_path / "artifacts"
    adapter = LocalStorageAdapter(root=root, buffer_bytes=2)
    stored = await adapter.store(byte_stream(b"data"), store_request())
    temporary = root / "tmp" / f"{stored.provider_artifact_id}_{'a' * 32}.part"
    temporary.write_bytes(b"partial")
    old = datetime.now(UTC).timestamp() - 7200
    os.utime(temporary, (old, old))
    adapter.close()
    restarted = LocalStorageAdapter(root=root, buffer_bytes=2)
    assert not temporary.exists()
    restarted.close()


@pytest.fixture
def artifact_database_env(
    isolated_database_env: str,
    migration_lock,
) -> Iterator[str]:
    """Reset PostgreSQL around artifact coordinator integration tests."""
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    with migration_lock():
        command.downgrade(config, "base")
        command.upgrade(config, "head")
        yield isolated_database_env
        asyncio.run(_truncate_artifact_tables(isolated_database_env))
        command.downgrade(config, "base")


@pytest.mark.asyncio
async def test_ingest_service_promotes_only_verified_provider_result(
    artifact_database_env: str, tmp_path: Path
) -> None:
    """Prove transaction B creates one content/replica/receipt and no binding."""
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        request = store_request(
            expected_sha256="sha256:" + hashlib.sha256(b"data").hexdigest(),
            expected_size=4,
        )
        ids = await _seed_reserved_item(factory, request)
        async with factory() as session:
            service = ArtifactIngestService(
                session,
                LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2),
                adapter_name="local",
            )
            await service.ingest_reserved_item(ids["item"], byte_stream(b"data"), request)
        async with factory() as session:
            assert await session.scalar(select(func.count()).select_from(ArtifactContent)) == 1
            assert await session.scalar(select(func.count()).select_from(ArtifactReplica)) == 1
            assert (
                await session.scalar(select(func.count()).select_from(ArtifactOperationReceipt))
                == 1
            )
            assert await session.scalar(select(func.count()).select_from(ArtifactBinding)) == 0
            item = await session.get(ArtifactUploadItem, ids["item"])
            assert item is not None and item.state == "ready"
            replica = (await session.scalars(select(ArtifactReplica))).one()
            replica_adapter = replica.adapter
            replica_provider_id = replica.provider_artifact_id
            replica_content_id = replica.content_id
            binding_id = str(uuid4())
            secondary_replica_id = str(uuid4())
            await session.rollback()
            async with session.begin():
                session.add(
                    ArtifactBinding(
                        id=binding_id,
                        content_id=replica_content_id,
                        project_id=ids["project"],
                        resource_type="submission",
                        resource_id="submission-isolation",
                        logical_role="submission_packet",
                        scope_version=1,
                        actor_id="actor-1",
                        attribution_type="submitted_by",
                    )
                )
                session.add(
                    ArtifactReplica(
                        id=secondary_replica_id,
                        content_id=replica_content_id,
                        adapter="secondary",
                        provider_artifact_id="secondary-provider-copy",
                        verification_state="verified",
                        retention_state="retained",
                        availability_state="available",
                        integrity_state="valid",
                    )
                )
            binding = await session.get(ArtifactBinding, binding_id)
            secondary_replica = await session.get(ArtifactReplica, secondary_replica_id)
            assert binding is not None
            assert secondary_replica is not None
            binding_before = {
                column.name: getattr(binding, column.name)
                for column in ArtifactBinding.__table__.columns
            }
            secondary_replica_before = {
                column.name: getattr(secondary_replica, column.name)
                for column in ArtifactReplica.__table__.columns
            }
            await session.rollback()
            service = ArtifactIngestService(
                session,
                LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2),
                adapter_name="local",
            )
            retain_request_identity = retain_identity(
                replica_provider_id,
                "review-hold",
                "review",
                key="retain-coordinator",
                principal="workstream.artifact.lifecycle",
            )
            await service.retain_replica(
                replica_adapter,
                replica_provider_id,
                "review-hold",
                "review",
                retain_request_identity,
            )
            second_retain_identity = retain_identity(
                replica_provider_id,
                "payment-hold",
                "payment",
                key="retain-payment",
                principal="workstream.artifact.lifecycle",
            )
            await service.retain_replica(
                replica_adapter,
                replica_provider_id,
                "payment-hold",
                "payment",
                second_retain_identity,
            )
            release_request_identity = release_identity(
                replica_provider_id,
                "review-hold",
                key="release-coordinator",
                principal="workstream.artifact.lifecycle",
            )
            await service.release_replica(
                replica_adapter,
                replica_provider_id,
                "review-hold",
                release_request_identity,
            )
            async with session.begin():
                current_replica = await session.get(ArtifactReplica, replica.id)
                assert current_replica is not None
                current_replica.verification_state = "failed"
            retained_after_one_release = await service.reconcile_replica(
                replica_adapter, replica_provider_id
            )
            assert retained_after_one_release.retention_state.value == "retained"
            await service.reconcile_replica(replica_adapter, replica_provider_id)
            async with session.begin():
                current_replica = await session.get(ArtifactReplica, replica.id)
                assert current_replica is not None
                current_replica.integrity_state = "unknown"
            await service.quarantine_existing_replica(
                replica_adapter, replica_provider_id, reason="integrity mismatch"
            )
            await service.quarantine_existing_replica(
                replica_adapter, replica_provider_id, reason="integrity mismatch"
            )
            await service.reconcile_replica(replica_adapter, replica_provider_id)
        async with factory() as session:
            assert await session.scalar(select(func.count()).select_from(ArtifactContent)) == 1
            assert await session.scalar(select(func.count()).select_from(ArtifactBinding)) == 1
            assert await session.scalar(select(func.count()).select_from(ArtifactReplica)) == 2
            assert (
                await session.scalar(select(func.count()).select_from(ArtifactOperationReceipt))
                == 4
            )
            assert await session.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "artifact_replica_quarantined")
            ) == 1
            assert await session.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "artifact_retention_released")
            ) == 1
            reconciliation_event = (
                await session.scalars(
                    select(AuditEvent).where(
                        AuditEvent.event_type == "artifact_replica_reconciled"
                    )
                )
            ).one()
            assert len(reconciliation_event.from_status or "") <= 30
            assert len(reconciliation_event.to_status or "") <= 30
            assert reconciliation_event.event_payload["before"]["verification_state"] == (
                "failed"
            )
            quarantine_event = (
                await session.scalars(
                    select(AuditEvent).where(
                        AuditEvent.event_type == "artifact_replica_quarantined"
                    )
                )
            ).one()
            assert quarantine_event.from_status == "unknown"
            affected_replica = await session.scalar(
                select(ArtifactReplica).where(
                    ArtifactReplica.provider_artifact_id == replica_provider_id
                )
            )
            secondary_replica = await session.get(ArtifactReplica, secondary_replica_id)
            binding = await session.get(ArtifactBinding, binding_id)
            assert affected_replica is not None
            assert affected_replica.integrity_state == "quarantined"
            assert secondary_replica is not None
            assert binding is not None
            assert {
                column.name: getattr(binding, column.name)
                for column in ArtifactBinding.__table__.columns
            } == binding_before
            assert {
                column.name: getattr(secondary_replica, column.name)
                for column in ArtifactReplica.__table__.columns
            } == secondary_replica_before
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_ingest_service_input_failure_promotes_zero_facts(
    artifact_database_env: str, tmp_path: Path
) -> None:
    """Prove failed input commitment creates no immutable storage facts."""
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        request = store_request(expected_sha256="sha256:" + "0" * 64, expected_size=4)
        ids = await _seed_reserved_item(factory, request)
        async with factory() as session:
            service = ArtifactIngestService(
                session,
                LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2),
                adapter_name="local",
            )
            with pytest.raises(ArtifactInputMismatchError):
                await service.ingest_reserved_item(ids["item"], byte_stream(b"data"), request)
        async with factory() as session:
            assert await session.scalar(select(func.count()).select_from(ArtifactContent)) == 0
            assert await session.scalar(select(func.count()).select_from(ArtifactReplica)) == 0
            assert (
                await session.scalar(select(func.count()).select_from(ArtifactOperationReceipt))
                == 0
            )
            assert await session.scalar(select(func.count()).select_from(ArtifactBinding)) == 0
            item = await session.get(ArtifactUploadItem, ids["item"])
            assert item is not None and item.state == "failed"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_ingest_service_reconciles_provider_committed_gap(
    artifact_database_env: str, tmp_path: Path
) -> None:
    """Finalize from provider receipt after a committed effect misses transaction B."""
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    payload = b"recovery"
    request = store_request(
        key="provider-gap",
        expected_sha256="sha256:" + hashlib.sha256(payload).hexdigest(),
        expected_size=len(payload),
        maximum_bytes=len(payload),
    )
    try:
        ids = await _seed_reserved_item(factory, request)
        adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            fence = await service._start_provider_operation(ids["item"], request)
            stored = await adapter.store(byte_stream(payload), request)
            await service._mark_provider_recovery_required(
                ids["item"], request, fence, provider_commit_confirmed=True
            )
        async with factory() as session:
            item = await session.get(ArtifactUploadItem, ids["item"])
            assert item is not None and item.state == "provider_committed"
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            recovered = await service.reconcile_committed_item(ids["item"], request)
            assert recovered.provider_artifact_id == stored.provider_artifact_id
            assert recovered.replayed is True
        async with factory() as session:
            item = await session.get(ArtifactUploadItem, ids["item"])
            upload_session = await session.get(ArtifactUploadSession, ids["session"])
            assert item is not None and item.state == "ready"
            assert upload_session is not None
            assert upload_session.reserved_bytes == 0
            assert upload_session.current_bytes == len(payload)
            assert await session.scalar(select(func.count()).select_from(ArtifactContent)) == 1
            assert await session.scalar(select(func.count()).select_from(ArtifactReplica)) == 1
            assert (
                await session.scalar(select(func.count()).select_from(ArtifactOperationReceipt))
                == 1
            )
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_ingest_service_replays_ambiguous_provider_failure(
    artifact_database_env: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Recover a committed provider effect after the call reports retryable failure."""
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    payload = b"ambiguous-commit"
    request = store_request(
        key="ambiguous",
        expected_sha256="sha256:" + hashlib.sha256(payload).hexdigest(),
        expected_size=len(payload),
        maximum_bytes=len(payload),
    )
    try:
        ids = await _seed_reserved_item(factory, request)
        adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
        original_store = adapter.store

        async def commit_then_fail(
            stream: AsyncIterator[bytes], store_operation: StoreArtifactRequest
        ):
            await original_store(stream, store_operation)
            raise ArtifactStoreUnavailableError("provider acknowledgement was lost")

        monkeypatch.setattr(adapter, "store", commit_then_fail)
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            with pytest.raises(ArtifactStoreUnavailableError):
                await service.ingest_reserved_item(ids["item"], byte_stream(payload), request)
        async with factory() as session:
            item = await session.get(ArtifactUploadItem, ids["item"])
            assert item is not None and item.state == "replay_required"
        monkeypatch.setattr(adapter, "store", original_store)
        async with factory() as session:
            recovered = await ArtifactIngestService(
                session, adapter, adapter_name="local"
            ).ingest_reserved_item(ids["item"], byte_stream(payload), request)
            assert recovered.sha256 == request.expected_sha256
            assert recovered.replayed is True
        async with factory() as session:
            item = await session.get(ArtifactUploadItem, ids["item"])
            assert item is not None and item.state == "ready"
            assert await session.scalar(select(func.count()).select_from(ArtifactContent)) == 1
            assert await session.scalar(select(func.count()).select_from(ArtifactReplica)) == 1
            assert (
                await session.scalar(select(func.count()).select_from(ArtifactOperationReceipt))
                == 1
            )
            assert await session.scalar(select(func.count()).select_from(ArtifactBinding)) == 0
            assert await session.scalar(select(func.count()).select_from(AuditEvent)) == 0
            assert len(list((tmp_path / "artifacts" / "objects").iterdir())) == 1

        pre_effect_request = store_request(
            key="pre-effect-failure",
            expected_sha256=request.expected_sha256,
            expected_size=request.expected_size,
            maximum_bytes=len(payload),
        )
        pre_effect_ids = await _seed_reserved_item(factory, pre_effect_request)

        async def fail_before_effect(
            stream: AsyncIterator[bytes], store_operation: StoreArtifactRequest
        ):
            del stream, store_operation
            raise ArtifactStoreUnavailableError("provider was unavailable")

        monkeypatch.setattr(adapter, "store", fail_before_effect)
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            with pytest.raises(ArtifactStoreUnavailableError):
                await service.ingest_reserved_item(
                    pre_effect_ids["item"], byte_stream(payload), pre_effect_request
                )
        async with factory() as session:
            item = await session.get(ArtifactUploadItem, pre_effect_ids["item"])
            assert item is not None and item.state == "replay_required"

        sha_only_request = store_request(
            key="sha-only-confirmed",
            expected_sha256=request.expected_sha256,
            expected_size=None,
            maximum_bytes=len(payload),
        )
        sha_only_ids = await _seed_reserved_item(factory, sha_only_request)
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            fence = await service._start_provider_operation(sha_only_ids["item"], sha_only_request)
            await service._mark_provider_recovery_required(
                sha_only_ids["item"],
                sha_only_request,
                fence,
                provider_commit_confirmed=True,
            )
        async with factory() as session:
            item = await session.get(ArtifactUploadItem, sha_only_ids["item"])
            assert item is not None and item.state == "replay_required"

        finalize_cancel_request = store_request(
            key="finalize-cancelled",
            expected_sha256=request.expected_sha256,
            expected_size=request.expected_size,
            maximum_bytes=len(payload),
        )
        finalize_cancel_ids = await _seed_reserved_item(factory, finalize_cancel_request)
        monkeypatch.setattr(adapter, "store", original_store)
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")

            async def cancel_finalization(*args) -> None:
                del args
                raise asyncio.CancelledError

            monkeypatch.setattr(service, "_finalize_provider_operation", cancel_finalization)
            with pytest.raises(asyncio.CancelledError):
                await service.ingest_reserved_item(
                    finalize_cancel_ids["item"],
                    byte_stream(payload),
                    finalize_cancel_request,
                )
        async with factory() as session:
            item = await session.get(ArtifactUploadItem, finalize_cancel_ids["item"])
            assert item is not None and item.state == "provider_committed"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_reconciliation_rehashes_bytes_and_fails_corrupt_item(
    artifact_database_env: str, tmp_path: Path
) -> None:
    """Reject altered committed bytes and fail the unpromoted item."""
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    payload = b"trusted"
    request = store_request(
        key="altered-recovery",
        expected_sha256="sha256:" + hashlib.sha256(payload).hexdigest(),
        expected_size=len(payload),
        maximum_bytes=len(payload),
    )
    try:
        ids = await _seed_reserved_item(factory, request)
        root = tmp_path / "artifacts"
        adapter = LocalStorageAdapter(root=root, buffer_bytes=2)
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            fence = await service._start_provider_operation(ids["item"], request)
            await adapter.store(byte_stream(payload), request)
            await service._mark_provider_recovery_required(
                ids["item"], request, fence, provider_commit_confirmed=True
            )
        next((root / "objects").iterdir()).write_bytes(b"altered")
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            with pytest.raises(ArtifactIntegrityError):
                await service.reconcile_committed_item(ids["item"], request)
        async with factory() as session:
            item = await session.get(ArtifactUploadItem, ids["item"])
            assert item is not None and item.state == "failed"
            assert item.error_code == "artifact_integrity_failure"
            assert await session.scalar(select(func.count()).select_from(ArtifactContent)) == 0

        missing_request = store_request(
            key="missing-confirmed-recovery",
            expected_sha256=request.expected_sha256,
            expected_size=request.expected_size,
            maximum_bytes=request.maximum_bytes,
        )
        missing_ids = await _seed_reserved_item(factory, missing_request)
        missing_root = tmp_path / "missing-artifacts"
        missing_adapter = LocalStorageAdapter(root=missing_root, buffer_bytes=2)
        async with factory() as session:
            service = ArtifactIngestService(session, missing_adapter, adapter_name="local")
            fence = await service._start_provider_operation(
                missing_ids["item"], missing_request
            )
            await missing_adapter.store(byte_stream(payload), missing_request)
            await service._mark_provider_recovery_required(
                missing_ids["item"],
                missing_request,
                fence,
                provider_commit_confirmed=True,
            )
        next((missing_root / "objects").iterdir()).unlink()
        async with factory() as session:
            service = ArtifactIngestService(session, missing_adapter, adapter_name="local")
            with pytest.raises(ArtifactIntegrityError, match="missing"):
                await service.reconcile_committed_item(missing_ids["item"], missing_request)
        async with factory() as session:
            missing_item = await session.get(ArtifactUploadItem, missing_ids["item"])
            assert missing_item is not None and missing_item.state == "failed"
            assert missing_item.error_code == "artifact_integrity_failure"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_identical_content_creates_distinct_provider_replicas(
    artifact_database_env: str, tmp_path: Path
) -> None:
    """Deduplicate content facts without collapsing distinct physical replicas."""
    engine = create_async_engine(artifact_database_env)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    payload = b"shared-content"
    digest = "sha256:" + hashlib.sha256(payload).hexdigest()
    first_request = store_request(
        key="shared-first",
        expected_sha256=digest,
        expected_size=len(payload),
        maximum_bytes=len(payload),
    )
    second_request = store_request(
        key="shared-second",
        expected_sha256=digest,
        expected_size=len(payload),
        maximum_bytes=len(payload),
    )
    try:
        first_ids = await _seed_reserved_item(factory, first_request)
        second_ids = await _seed_reserved_item(factory, second_request)
        adapter = LocalStorageAdapter(root=tmp_path / "artifacts", buffer_bytes=2)
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            await service.ingest_reserved_item(
                first_ids["item"], byte_stream(payload), first_request
            )
        async with factory() as session:
            service = ArtifactIngestService(session, adapter, adapter_name="local")
            await service.ingest_reserved_item(
                second_ids["item"], byte_stream(payload), second_request
            )
        async with factory() as session:
            assert await session.scalar(select(func.count()).select_from(ArtifactContent)) == 1
            assert await session.scalar(select(func.count()).select_from(ArtifactReplica)) == 2
            provider_ids = set(await session.scalars(select(ArtifactReplica.provider_artifact_id)))
            assert len(provider_ids) == 2
    finally:
        await engine.dispose()


async def _seed_reserved_item(
    factory: async_sessionmaker, request: StoreArtifactRequest
) -> dict[str, str]:
    """Create one project, upload session, and reserved upload item."""
    ids = {name: str(uuid4()) for name in ("project", "session", "item")}
    async with factory() as session, session.begin():
        session.add(Project(id=ids["project"], name="Artifact test", slug=f"artifact-{uuid4()}"))
        await session.flush()
        session.add(
            ArtifactUploadSession(
                id=ids["session"],
                actor_id="actor-1",
                project_id=ids["project"],
                permitted_roles=["submission_packet"],
                state="open",
                maximum_bytes=max(64, request.maximum_bytes),
                current_bytes=0,
                reserved_bytes=request.maximum_bytes,
                maximum_items=4,
                current_items=0,
                reserved_items=1,
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                cas_version=0,
            )
        )
        await session.flush()
        session.add(
            ArtifactUploadItem(
                id=ids["item"],
                session_id=ids["session"],
                logical_role="submission_packet",
                display_name="packet.bin",
                media_type="application/octet-stream",
                reserved_bytes=request.maximum_bytes,
                expected_sha256=request.expected_sha256,
                expected_size=request.expected_size,
                idempotency_key=request.idempotency.key,
                request_digest=request.idempotency.request_digest,
                state="reserved",
                cas_version=0,
            )
        )
    return ids


async def _truncate_artifact_tables(database_url: str) -> None:
    """Clear additive artifact rows before exercising the guarded downgrade."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.exec_driver_sql(
                """
                truncate table
                    artifact_operation_receipts,
                    artifact_replicas,
                    artifact_bindings,
                    artifact_upload_items,
                    artifact_contents,
                    artifact_upload_sessions
                cascade
                """
            )
    finally:
        await engine.dispose()
