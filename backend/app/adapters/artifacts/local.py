"""Private development artifact storage with provider-contract parity."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable, AsyncIterator
from contextlib import contextmanager
from datetime import UTC, datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat as stat_module
import time
from typing import Any, BinaryIO, Iterator
from uuid import uuid4

from app.core.hashing import canonical_json_hash
from app.interfaces.artifacts import (
    ArtifactByteRange,
    ArtifactIdempotencyMismatchError,
    ArtifactInputMismatchError,
    ArtifactIntegrityError,
    ArtifactLimitExceededError,
    ArtifactMalformedRequestError,
    ArtifactNotFoundError,
    ArtifactOperation,
    ArtifactOperationResult,
    ArtifactRetentionConflictError,
    ArtifactStatus,
    ArtifactStoreUnavailableError,
    AvailabilityState,
    IdempotencyIdentity,
    IntegrityState,
    OperationReceipt,
    ReceiptDetail,
    ReceiptOutcome,
    RetentionState,
    RetentionSummary,
    StoreArtifactRequest,
    StoredArtifact,
    VerificationState,
    canonical_release_request_digest,
    canonical_retain_request_digest,
    canonical_store_request_digest,
    canonical_verify_request_digest,
)

_OPAQUE_ID = re.compile(r"^art_[0-9a-f]{32}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_OPERATION_REF = re.compile(r"^op_[0-9a-f]{32}$")


class LocalStorageAdapter:
    """Filesystem-backed artifact provider for development and CI only."""

    adapter_name = "local"

    def __init__(self, *, root: Path, buffer_bytes: int = 1024 * 1024) -> None:
        """Initialize a private storage root.

        Args:
            root: Dedicated non-symlink storage directory.
            buffer_bytes: Maximum bytes used by one filesystem read or write.

        Raises:
            ValueError: If the root or buffer is unsafe.
        """
        if buffer_bytes <= 0 or buffer_bytes > 1024 * 1024:
            raise ValueError("artifact buffer must be between 1 byte and 1 MiB")
        self._root = root.resolve(strict=False)
        self._buffer_bytes = buffer_bytes
        self._initialize_root(root)
        self._root_fd = os.open(
            self._root,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        self._cleanup_abandoned_temporary_files()

    def close(self) -> None:
        """Release the pinned local storage root descriptor."""
        descriptor = getattr(self, "_root_fd", -1)
        if descriptor >= 0:
            os.close(descriptor)
            self._root_fd = -1

    def __del__(self) -> None:
        """Best-effort descriptor cleanup when an adapter leaves scope."""
        try:
            self.close()
        except OSError:
            pass

    async def store(
        self,
        stream: AsyncIterable[bytes],
        request: StoreArtifactRequest,
    ) -> StoredArtifact:
        """Store a stream or prove an exact replay without duplicating bytes."""
        self._validate_store_request(request)
        scope = self._scope_key(request.idempotency)
        lock: tuple[Any, int] | None = None
        try:
            lock = await self._acquire_lock_async(scope)
            intent = await self._read_json_optional(self._path("intents", scope, ".json"))
            if intent is not None:
                self._assert_same_request(intent, request.idempotency)
                provider_id = self._validated_provider_id(intent["provider_artifact_id"])
                artifact_lock = await self._acquire_lock_async(
                    self._artifact_lock_scope(provider_id)
                )
                try:
                    return await self._recover_or_replay(stream, request, intent, scope)
                finally:
                    await self._run_io(self._release_lock, artifact_lock)

            provider_artifact_id = f"art_{uuid4().hex}"
            operation_reference = f"op_{uuid4().hex}"
            intent = {
                "service_principal": request.idempotency.service_principal,
                "operation": request.idempotency.operation.value,
                "idempotency_key": request.idempotency.key,
                "request_digest": request.idempotency.request_digest,
                "provider_artifact_id": provider_artifact_id,
                "provider_operation_reference": operation_reference,
                "expected_sha256": request.expected_sha256,
                "expected_size": request.expected_size,
                "media_type": request.media_type,
            }
            await self._write_json_exclusive(self._path("intents", scope, ".json"), intent)
            sha256, byte_count = await self._write_stream(stream, provider_artifact_id, request)
            metadata = self._new_metadata(
                provider_artifact_id=provider_artifact_id,
                sha256=sha256,
                byte_count=byte_count,
                media_type=request.media_type,
            )
            await self._write_json_exclusive(
                self._path("metadata", provider_artifact_id, ".json"), metadata
            )
            receipt = self._make_receipt(
                identity=request.idempotency,
                operation_reference=operation_reference,
                outcome=ReceiptOutcome.STORED,
                provider_artifact_id=provider_artifact_id,
                sha256=sha256,
                byte_count=byte_count,
            )
            await self._write_json_exclusive(
                self._path("receipts", scope, ".json"), self._receipt_to_json(receipt)
            )
            return StoredArtifact(
                provider_artifact_id=provider_artifact_id,
                sha256=sha256,
                byte_count=byte_count,
                media_type=request.media_type,
                receipt=receipt,
                replayed=False,
            )
        except asyncio.CancelledError:
            if lock is not None:
                await self._cleanup_unpublished(scope)
            raise
        except (
            ArtifactInputMismatchError,
            ArtifactIntegrityError,
            ArtifactIdempotencyMismatchError,
            ArtifactLimitExceededError,
        ):
            raise
        except OSError as exc:
            raise ArtifactStoreUnavailableError("local artifact operation failed") from exc
        finally:
            if lock is not None:
                await self._run_io(self._release_lock, lock)

    async def _recover_or_replay(
        self,
        stream: AsyncIterable[bytes],
        request: StoreArtifactRequest,
        intent: dict[str, Any],
        scope: str,
    ) -> StoredArtifact:
        """Recover committed bytes or validate a no-commitment exact replay."""
        provider_id = self._validated_provider_id(intent["provider_artifact_id"])
        receipt_json = await self._read_json_optional(self._path("receipts", scope, ".json"))
        metadata = await self._read_json_optional(self._path("metadata", provider_id, ".json"))
        expected = intent.get("expected_sha256")
        if metadata is None and not await self._object_exists(provider_id):
            if receipt_json is not None:
                self._receipt_from_json(receipt_json)
                raise ArtifactIntegrityError("artifact receipt has no committed object")
            replay_sha256, replay_size = await self._write_stream(
                stream, provider_id, request
            )
            metadata = self._new_metadata(
                provider_artifact_id=provider_id,
                sha256=replay_sha256,
                byte_count=replay_size,
                media_type=intent["media_type"],
            )
            await self._write_json_exclusive(
                self._path("metadata", provider_id, ".json"), metadata
            )
        else:
            replay_sha256, replay_size = await self._consume_stream(
                stream, request.maximum_bytes
            )
        if expected is not None and replay_sha256 != expected:
            await self._quarantine_provider_object(provider_id, "replay_commitment_mismatch")
            raise ArtifactIntegrityError("artifact replay does not match its commitment")
        if intent.get("expected_size") is not None and replay_size != intent["expected_size"]:
            await self._quarantine_provider_object(provider_id, "replay_size_mismatch")
            raise ArtifactIntegrityError("artifact replay size does not match its commitment")

        if metadata is None:
            observed_sha256, observed_size = await self._hash_object(provider_id)
            if observed_sha256 != replay_sha256 or observed_size != replay_size:
                await self._quarantine_provider_object(provider_id, "recovery_mismatch")
                raise ArtifactIntegrityError("artifact recovery commitment failed")
            if intent.get("expected_size") is not None and observed_size != intent["expected_size"]:
                await self._quarantine_provider_object(provider_id, "recovery_size_mismatch")
                raise ArtifactIntegrityError("artifact recovery size commitment failed")
            metadata = self._new_metadata(
                provider_artifact_id=provider_id,
                sha256=observed_sha256,
                byte_count=observed_size,
                media_type=intent.get("media_type"),
            )
            await self._write_json_exclusive(
                self._path("metadata", provider_id, ".json"), metadata
            )

        if replay_sha256 != metadata.get("sha256") or replay_size != metadata.get("byte_count"):
            await self._quarantine_provider_object(provider_id, "replay_mismatch")
            raise ArtifactIntegrityError("artifact replay does not match persisted bytes")

        await self._assert_metadata_matches_object(provider_id, metadata)
        if receipt_json is None:
            receipt = self._make_receipt(
                identity=request.idempotency,
                operation_reference=intent["provider_operation_reference"],
                outcome=ReceiptOutcome.STORED,
                provider_artifact_id=provider_id,
                sha256=metadata["sha256"],
                byte_count=metadata["byte_count"],
            )
            await self._write_json_exclusive(
                self._path("receipts", scope, ".json"), self._receipt_to_json(receipt)
            )
        else:
            try:
                receipt = self._receipt_from_json(receipt_json)
                self._assert_receipt_matches(receipt, request.idempotency, metadata)
            except ArtifactIntegrityError:
                await self._quarantine_provider_object(provider_id, "receipt_mismatch")
                raise
        return StoredArtifact(
            provider_artifact_id=provider_id,
            sha256=metadata["sha256"],
            byte_count=metadata["byte_count"],
            media_type=metadata.get("media_type"),
            receipt=receipt,
            replayed=True,
        )

    async def recover_committed_store(self, request: StoreArtifactRequest) -> StoredArtifact:
        """Recover a committed local object from a persisted client commitment."""
        self._validate_store_request(request)
        if request.expected_sha256 is None or request.expected_size is None:
            raise ArtifactInputMismatchError("artifact recovery requires an exact commitment")
        scope = self._scope_key(request.idempotency)
        lock: tuple[Any, int] | None = None
        try:
            lock = await self._acquire_lock_async(scope)
            intent = await self._read_json_optional(self._path("intents", scope, ".json"))
            if intent is None:
                raise ArtifactIntegrityError("committed artifact recovery intent is missing")
            self._assert_same_request(intent, request.idempotency)
            provider_id = self._validated_provider_id(intent["provider_artifact_id"])
            artifact_lock = await self._acquire_lock_async(
                self._artifact_lock_scope(provider_id)
            )
            try:
                return await self._recover_without_replay(request, intent, scope)
            finally:
                await self._run_io(self._release_lock, artifact_lock)
        except OSError as exc:
            raise ArtifactStoreUnavailableError("local artifact recovery failed") from exc
        finally:
            if lock is not None:
                await self._run_io(self._release_lock, lock)

    async def _recover_without_replay(
        self,
        request: StoreArtifactRequest,
        intent: dict[str, Any],
        scope: str,
    ) -> StoredArtifact:
        """Reconstruct metadata and receipt after independently hashing an object."""
        provider_id = self._validated_provider_id(intent["provider_artifact_id"])
        if not await self._object_exists(provider_id):
            raise ArtifactIntegrityError("committed artifact object is missing")
        observed_sha256, observed_size = await self._hash_object(provider_id)
        if observed_sha256 != request.expected_sha256 or observed_size != request.expected_size:
            await self._quarantine_provider_object(provider_id, "recovery_mismatch")
            raise ArtifactIntegrityError("artifact recovery commitment failed")
        metadata_path = self._path("metadata", provider_id, ".json")
        metadata = await self._read_json_optional(metadata_path)
        if metadata is None:
            metadata = self._new_metadata(
                provider_artifact_id=provider_id,
                sha256=observed_sha256,
                byte_count=observed_size,
                media_type=intent.get("media_type"),
            )
            await self._write_json_exclusive(metadata_path, metadata)
        else:
            await self._assert_metadata_matches_object(provider_id, metadata)
        receipt_path = self._path("receipts", scope, ".json")
        receipt_payload = await self._read_json_optional(receipt_path)
        if receipt_payload is None:
            receipt = self._make_receipt(
                identity=request.idempotency,
                operation_reference=intent["provider_operation_reference"],
                outcome=ReceiptOutcome.STORED,
                provider_artifact_id=provider_id,
                sha256=observed_sha256,
                byte_count=observed_size,
            )
            await self._write_json_exclusive(receipt_path, self._receipt_to_json(receipt))
        else:
            receipt = self._receipt_from_json(receipt_payload)
            self._assert_receipt_matches(receipt, request.idempotency, metadata)
        return StoredArtifact(
            provider_artifact_id=provider_id,
            sha256=observed_sha256,
            byte_count=observed_size,
            media_type=metadata.get("media_type"),
            receipt=receipt,
            replayed=True,
        )

    def open(
        self,
        provider_artifact_id: str,
        byte_range: ArtifactByteRange | None = None,
    ) -> AsyncIterator[bytes]:
        """Stream an available object using bounded reads."""

        async def iterator() -> AsyncIterator[bytes]:
            """Yield the selected object range and close its file deterministically."""
            try:
                provider_id = self._validated_provider_id(provider_artifact_id)
                metadata = await self._load_available_metadata(provider_id)
                size = int(metadata["byte_count"])
                selected = byte_range or ArtifactByteRange()
                if selected.offset > size:
                    raise ArtifactMalformedRequestError("artifact range starts past object end")
                remaining = size - selected.offset
                if selected.length is not None:
                    remaining = min(remaining, selected.length)
                handle = await self._run_io(self._open_regular_object, provider_id)
                try:
                    await self._run_io(handle.seek, selected.offset)
                    while remaining > 0:
                        chunk = await self._run_io(
                            handle.read, min(self._buffer_bytes, remaining)
                        )
                        if not chunk:
                            raise ArtifactIntegrityError("artifact ended before recorded size")
                        remaining -= len(chunk)
                        yield chunk
                finally:
                    await self._run_io(handle.close)
            except OSError as exc:
                raise ArtifactStoreUnavailableError("local artifact read failed") from exc

        return iterator()

    async def stat(self, provider_artifact_id: str) -> ArtifactStatus:
        """Return provider observations without exposing filesystem paths."""
        provider_id = self._validated_provider_id(provider_artifact_id)
        artifact_lock = await self._acquire_lock_async(self._artifact_lock_scope(provider_id))
        try:
            try:
                metadata = await self._read_json_required(
                    self._path("metadata", provider_id, ".json")
                )
            except ArtifactIntegrityError as exc:
                try:
                    await self._quarantine_provider_object(provider_id, "metadata_invalid")
                except (ArtifactIntegrityError, OSError):
                    pass
                raise exc
            if metadata.get("integrity_state") == "quarantined":
                try:
                    await self._run_io(
                        self._assert_regular_file,
                        self._path("quarantine", provider_id, ".blob"),
                    )
                except FileNotFoundError:
                    metadata = {
                        **metadata,
                        "availability_state": "missing",
                        "integrity_state": "unknown",
                    }
            else:
                if not await self._object_exists(provider_id):
                    metadata = {
                        **metadata,
                        "availability_state": "missing",
                        "integrity_state": "unknown",
                    }
                else:
                    await self._assert_metadata_matches_object(provider_id, metadata)
            try:
                return self._status_from_metadata(metadata)
            except ArtifactIntegrityError:
                await self._quarantine_provider_object(provider_id, "metadata_invalid")
                raise
        finally:
            await self._run_io(self._release_lock, artifact_lock)

    async def verify(
        self,
        provider_artifact_id: str,
        expected_sha256: str,
        expected_size: int,
        idempotency: IdempotencyIdentity,
    ) -> ArtifactOperationResult:
        """Independently hash and count a complete provider object."""
        self._validate_identity(idempotency, ArtifactOperation.VERIFY)
        self._validate_digest(expected_sha256)
        if expected_size < 0:
            raise ArtifactMalformedRequestError("expected artifact size must be nonnegative")
        provider_id = self._validated_provider_id(provider_artifact_id)
        if idempotency.request_digest != canonical_verify_request_digest(
            provider_id, expected_sha256, expected_size
        ):
            raise ArtifactIdempotencyMismatchError("verify request digest is not canonical")
        scope = self._scope_key(idempotency)
        lock: tuple[Any, int] | None = None
        artifact_lock: tuple[Any, int] | None = None
        try:
            lock = await self._acquire_lock_async(scope)
            artifact_lock = await self._acquire_lock_async(
                self._artifact_lock_scope(provider_id)
            )
            existing = await self._read_json_optional(self._path("receipts", scope, ".json"))
            if existing is not None:
                try:
                    receipt = self._receipt_from_json(existing)
                    self._assert_operation_receipt(
                        receipt,
                        idempotency,
                        provider_id,
                        ReceiptOutcome.VERIFIED,
                    )
                    return ArtifactOperationResult(receipt=receipt, replayed=True)
                except ArtifactIntegrityError:
                    await self._quarantine_provider_object(provider_id, "receipt_mismatch")
                    raise
            observed_sha256, observed_size = await self._hash_object(provider_id)
            if observed_sha256 != expected_sha256 or observed_size != expected_size:
                await self._quarantine_provider_object(provider_id, "verify_mismatch")
                raise ArtifactIntegrityError("artifact verification failed")
            await self._update_metadata(provider_id, verification_state="verified")
            receipt = self._make_receipt(
                identity=idempotency,
                operation_reference=f"op_{uuid4().hex}",
                outcome=ReceiptOutcome.VERIFIED,
                provider_artifact_id=provider_id,
                sha256=observed_sha256,
                byte_count=observed_size,
            )
            await self._write_json_exclusive(
                self._path("receipts", scope, ".json"), self._receipt_to_json(receipt)
            )
            return ArtifactOperationResult(receipt=receipt, replayed=False)
        except FileNotFoundError as exc:
            raise ArtifactNotFoundError("artifact is unavailable") from exc
        except OSError as exc:
            raise ArtifactStoreUnavailableError("local artifact verification failed") from exc
        finally:
            if artifact_lock is not None:
                await self._run_io(self._release_lock, artifact_lock)
            if lock is not None:
                await self._run_io(self._release_lock, lock)

    async def retain(
        self,
        provider_artifact_id: str,
        retention_reference: str,
        retention_class: str,
        idempotency: IdempotencyIdentity,
    ) -> ArtifactOperationResult:
        """Add one exact retention reference idempotently."""
        self._validate_identity(idempotency, ArtifactOperation.RETAIN)
        self._validate_opaque(retention_reference, "retention reference")
        self._validate_retention_class(retention_class)
        provider_id = self._validated_provider_id(provider_artifact_id)
        if idempotency.request_digest != canonical_retain_request_digest(
            provider_id, retention_reference, retention_class
        ):
            raise ArtifactIdempotencyMismatchError("retain request digest is not canonical")
        return await self._change_retention(
            provider_artifact_id,
            retention_reference,
            retention_class,
            idempotency,
            releasing=False,
        )

    async def release(
        self,
        provider_artifact_id: str,
        retention_reference: str,
        idempotency: IdempotencyIdentity,
    ) -> ArtifactOperationResult:
        """Release only the exact retention reference supplied."""
        self._validate_identity(idempotency, ArtifactOperation.RELEASE)
        self._validate_opaque(retention_reference, "retention reference")
        provider_id = self._validated_provider_id(provider_artifact_id)
        if idempotency.request_digest != canonical_release_request_digest(
            provider_id, retention_reference
        ):
            raise ArtifactIdempotencyMismatchError("release request digest is not canonical")
        return await self._change_retention(
            provider_artifact_id,
            retention_reference,
            None,
            idempotency,
            releasing=True,
        )

    async def _change_retention(
        self,
        provider_artifact_id: str,
        retention_reference: str,
        retention_class: str | None,
        identity: IdempotencyIdentity,
        *,
        releasing: bool,
    ) -> ArtifactOperationResult:
        """Apply one locked, reference-counted retention change."""
        provider_id = self._validated_provider_id(provider_artifact_id)
        scope = self._scope_key(identity)
        operation_lock: tuple[Any, int] | None = None
        artifact_lock: tuple[Any, int] | None = None
        try:
            operation_lock = await self._acquire_lock_async(scope)
            artifact_lock = await self._acquire_lock_async(
                self._artifact_lock_scope(provider_id)
            )
            existing = await self._read_json_optional(self._path("receipts", scope, ".json"))
            if existing is not None:
                try:
                    receipt = self._receipt_from_json(existing)
                    self._assert_operation_receipt(
                        receipt,
                        identity,
                        provider_id,
                        ReceiptOutcome.RELEASED if releasing else ReceiptOutcome.RETAINED,
                        retention_reference=retention_reference,
                    )
                    return ArtifactOperationResult(receipt=receipt, replayed=True)
                except ArtifactIntegrityError:
                    await self._quarantine_provider_object(provider_id, "receipt_mismatch")
                    raise
            metadata = await self._load_available_metadata(provider_id)
            references = dict(metadata.get("retention_references", {}))
            intent_path = self._path("intents", scope, ".json")
            mutation_intent = await self._read_json_optional(intent_path)
            if mutation_intent is not None:
                self._assert_retention_intent(
                    mutation_intent,
                    identity,
                    provider_id,
                    retention_reference,
                    retention_class,
                    releasing=releasing,
                )
            if releasing:
                recorded = references.get(retention_reference)
                if recorded is None and mutation_intent is None:
                    raise ArtifactRetentionConflictError("retention reference is not active")
                if recorded is not None and recorded.get("owner") != identity.service_principal:
                    raise ArtifactRetentionConflictError("retention reference owner changed")
                recorded_class = (
                    recorded["retention_class"]
                    if recorded is not None
                    else mutation_intent["retention_class"]
                )
            else:
                recorded_class = retention_class
                existing_reference = references.get(retention_reference)
                if existing_reference is not None and existing_reference != {
                    "retention_class": retention_class,
                    "owner": identity.service_principal,
                }:
                    raise ArtifactIdempotencyMismatchError("retention reference class changed")

            if mutation_intent is None:
                mutation_intent = {
                    "service_principal": identity.service_principal,
                    "operation": identity.operation.value,
                    "idempotency_key": identity.key,
                    "request_digest": identity.request_digest,
                    "provider_artifact_id": provider_id,
                    "provider_operation_reference": f"op_{uuid4().hex}",
                    "retention_reference": retention_reference,
                    "retention_class": recorded_class,
                }
                await self._write_json_exclusive(intent_path, mutation_intent)

            if releasing:
                references.pop(retention_reference, None)
            else:
                references[retention_reference] = {
                    "retention_class": retention_class,
                    "owner": identity.service_principal,
                }
            retention_state = "retained" if references else "released"
            await self._update_metadata(
                provider_id,
                retention_references=references,
                retention_state=retention_state,
            )
            receipt = self._make_receipt(
                identity=identity,
                operation_reference=mutation_intent["provider_operation_reference"],
                outcome=(ReceiptOutcome.RELEASED if releasing else ReceiptOutcome.RETAINED),
                provider_artifact_id=provider_id,
                sha256=metadata["sha256"],
                byte_count=metadata["byte_count"],
                retention_reference=retention_reference,
                retention_class=recorded_class,
            )
            await self._write_json_exclusive(
                self._path("receipts", scope, ".json"), self._receipt_to_json(receipt)
            )
            return ArtifactOperationResult(receipt=receipt, replayed=False)
        except OSError as exc:
            raise ArtifactStoreUnavailableError("local artifact retention failed") from exc
        finally:
            if artifact_lock is not None:
                await self._run_io(self._release_lock, artifact_lock)
            if operation_lock is not None:
                await self._run_io(self._release_lock, operation_lock)

    async def get_operation_receipt(
        self,
        service_principal: str,
        operation: ArtifactOperation,
        idempotency_key: str,
    ) -> OperationReceipt | None:
        """Load the authoritative receipt for a complete operation identity."""
        identity = IdempotencyIdentity(
            service_principal=service_principal,
            operation=operation,
            key=idempotency_key,
            request_digest="sha256:" + "0" * 64,
        )
        self._validate_service_principal(service_principal)
        self._validate_opaque(idempotency_key, "idempotency key")
        payload = await self._read_json_optional(
            self._path("receipts", self._scope_key(identity), ".json")
        )
        return None if payload is None else self._receipt_from_json(payload)

    def _initialize_root(self, configured_root: Path) -> None:
        """Create and verify the private local layout."""
        if configured_root.is_symlink():
            raise ValueError("artifact root must not be a symlink")
        configured_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if configured_root.resolve() != self._root or not configured_root.is_dir():
            raise ValueError("artifact root must be a dedicated directory")
        os.chmod(self._root, 0o700)
        for name in ("objects", "metadata", "receipts", "intents", "locks", "tmp", "quarantine"):
            path = self._root / name
            path.mkdir(mode=0o700, exist_ok=True)
            if path.is_symlink() or not path.is_dir():
                raise ValueError("artifact storage layout is unsafe")
            os.chmod(path, 0o700)

    def _cleanup_abandoned_temporary_files(self) -> None:
        """Remove unpublished local temporary files left by interrupted writes."""
        intents: dict[str, str] = {}
        intent_directory = self._open_directory_fd(self._root / "intents")
        try:
            for name in os.listdir(intent_directory):
                match = re.fullmatch(r"([0-9a-f]{64})\.json", name)
                if match is None:
                    continue
                try:
                    intent = self._read_json_sync(
                        self._path("intents", match.group(1), ".json")
                    )
                except (ArtifactIntegrityError, OSError, ValueError, json.JSONDecodeError):
                    continue
                provider_id = intent.get("provider_artifact_id")
                if isinstance(provider_id, str) and _OPAQUE_ID.fullmatch(provider_id):
                    intents[provider_id] = match.group(1)
        finally:
            os.close(intent_directory)

        directory = self._open_directory_fd(self._root / "tmp")
        try:
            for name in os.listdir(directory):
                match = re.fullmatch(r"(art_[0-9a-f]{32})_[0-9a-f]{32}\.part", name)
                if match is None or match.group(1) not in intents:
                    continue
                details = os.stat(name, dir_fd=directory, follow_symlinks=False)
                if time.time() - details.st_mtime < 3600:
                    continue
                lock = self._acquire_lock(intents[match.group(1)])
                try:
                    details = os.stat(name, dir_fd=directory, follow_symlinks=False)
                    if time.time() - details.st_mtime >= 3600:
                        os.unlink(name, dir_fd=directory)
                except FileNotFoundError:
                    continue
                finally:
                    self._release_lock(lock)
            os.fsync(directory)
        finally:
            os.close(directory)

    def _path(self, directory: str, opaque: str, suffix: str) -> Path:
        """Return a contained private path from a validated internal token."""
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", opaque):
            raise ArtifactInputMismatchError("artifact identifier is invalid")
        path = self._root / directory / f"{opaque}{suffix}"
        if path.parent.parent != self._root:
            raise ArtifactInputMismatchError("artifact identifier is invalid")
        return path

    def _scope_key(self, identity: IdempotencyIdentity) -> str:
        """Derive a private stable filename key from operation identity."""
        material = f"{identity.service_principal}\0{identity.operation.value}\0{identity.key}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    @staticmethod
    def _artifact_lock_scope(provider_id: str) -> str:
        """Derive the shared metadata-mutation lock for one provider object."""
        return hashlib.sha256(f"artifact\0{provider_id}".encode()).hexdigest()

    def _validate_store_request(self, request: StoreArtifactRequest) -> None:
        """Validate bounded store metadata before filesystem work."""
        self._validate_identity(request.idempotency, ArtifactOperation.STORE)
        if request.maximum_bytes < 0:
            raise ArtifactMalformedRequestError("maximum artifact bytes must be nonnegative")
        if request.expected_size is not None and request.expected_size < 0:
            raise ArtifactMalformedRequestError("expected artifact size must be nonnegative")
        if request.expected_sha256 is not None:
            self._validate_digest(request.expected_sha256)
        if (
            not request.media_type
            or len(request.media_type) > 255
            or any(ord(character) < 32 or ord(character) == 127 for character in request.media_type)
        ):
            raise ArtifactMalformedRequestError("artifact media type is invalid")
        if len(request.metadata) > 32:
            raise ArtifactMalformedRequestError("artifact metadata exceeds its item limit")
        for name, value in request.metadata.items():
            if (
                not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name)
                or not isinstance(value, str)
                or len(value) > 256
            ):
                raise ArtifactMalformedRequestError("artifact metadata is invalid")
        if request.idempotency.request_digest != canonical_store_request_digest(request):
            raise ArtifactIdempotencyMismatchError("store request digest is not canonical")

    def _validate_identity(
        self, identity: IdempotencyIdentity, expected_operation: ArtifactOperation
    ) -> None:
        """Validate operation identity and request commitment."""
        if identity.operation != expected_operation:
            raise ArtifactMalformedRequestError("artifact operation identity is invalid")
        self._validate_service_principal(identity.service_principal)
        self._validate_opaque(identity.key, "idempotency key")
        self._validate_digest(identity.request_digest)

    @staticmethod
    def _validate_opaque(value: str, label: str) -> None:
        """Require one bounded provider-neutral opaque identifier."""
        if not re.fullmatch(r"(?!\.{1,2}$)[A-Za-z0-9][A-Za-z0-9._~-]{0,127}", value):
            raise ArtifactMalformedRequestError(f"{label} is invalid")

    @staticmethod
    def _validate_service_principal(value: str) -> None:
        """Require one bounded provider-neutral service principal."""
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9._-]{1,126}[a-z0-9])", value) or len(
            value
        ) > 100:
            raise ArtifactMalformedRequestError("service principal is invalid")

    @staticmethod
    def _validate_retention_class(value: str) -> None:
        """Require the provider-neutral retention-class grammar."""
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", value):
            raise ArtifactMalformedRequestError("retention class is invalid")

    @staticmethod
    def _validate_digest(value: str) -> None:
        """Require canonical lower-case SHA-256 values."""
        if not _DIGEST.fullmatch(value):
            raise ArtifactMalformedRequestError("artifact digest is invalid")

    @staticmethod
    def _validated_provider_id(value: str) -> str:
        """Require an opaque provider artifact identifier."""
        if not _OPAQUE_ID.fullmatch(value):
            raise ArtifactNotFoundError("artifact is unavailable")
        return value

    async def _write_stream(
        self,
        stream: AsyncIterable[bytes],
        provider_id: str,
        request: StoreArtifactRequest,
    ) -> tuple[str, int]:
        """Write and publish an independently hashed bounded stream."""
        temporary = self._path("tmp", f"{provider_id}_{uuid4().hex}", ".part")
        final = self._path("objects", provider_id, ".blob")
        handle = await self._run_io(self._open_exclusive, temporary)
        write_complete = False
        try:
            sha256, total = await self._write_bounded_stream_to_private_file(
                stream,
                handle,
                request.maximum_bytes,
            )
            write_complete = True
        finally:
            await self._run_io(os.close, handle)
            if not write_complete:
                await self._run_io(self._unlink_optional, temporary)
        if request.expected_sha256 is not None and sha256 != request.expected_sha256:
            await self._run_io(self._unlink_optional, temporary)
            raise ArtifactInputMismatchError("artifact bytes do not match expected digest")
        if request.expected_size is not None and total != request.expected_size:
            await self._run_io(self._unlink_optional, temporary)
            raise ArtifactInputMismatchError("artifact bytes do not match expected size")
        try:
            await self._run_io(self._publish_exclusive, temporary, final)
        except BaseException:
            await self._run_io(self._unlink_optional, temporary)
            raise
        return sha256, total

    async def _write_bounded_stream_to_private_file(
        self,
        stream: AsyncIterable[bytes],
        descriptor: int,
        maximum_bytes: int,
    ) -> tuple[str, int]:
        """Hash and write one bounded stream to an already-private file."""
        digest = hashlib.sha256()
        total = 0
        async for source_chunk in stream:
            if not isinstance(source_chunk, bytes):
                raise ArtifactInputMismatchError("artifact stream must yield bytes")
            view = memoryview(source_chunk)
            for offset in range(0, len(view), self._buffer_bytes):
                chunk = view[offset : offset + self._buffer_bytes]
                total += len(chunk)
                if total > maximum_bytes:
                    raise ArtifactLimitExceededError("artifact exceeds maximum bytes")
                digest.update(chunk)
                await self._run_io(self._write_all, descriptor, chunk)
        await self._run_io(os.fsync, descriptor)
        return f"sha256:{digest.hexdigest()}", total

    async def _consume_stream(
        self, stream: AsyncIterable[bytes], maximum_bytes: int
    ) -> tuple[str, int]:
        """Fully hash and count a replay without storing a second object."""
        digest = hashlib.sha256()
        total = 0
        async for source_chunk in stream:
            if not isinstance(source_chunk, bytes):
                raise ArtifactInputMismatchError("artifact stream must yield bytes")
            view = memoryview(source_chunk)
            for offset in range(0, len(view), self._buffer_bytes):
                chunk = view[offset : offset + self._buffer_bytes]
                total += len(chunk)
                if total > maximum_bytes:
                    raise ArtifactLimitExceededError("artifact exceeds maximum bytes")
                digest.update(chunk)
        return f"sha256:{digest.hexdigest()}", total

    async def _hash_object(self, provider_id: str) -> tuple[str, int]:
        """Independently hash and count one regular provider object."""
        handle = await self._run_io(self._open_regular_object, provider_id)
        digest = hashlib.sha256()
        total = 0
        try:
            while True:
                chunk = await self._run_io(handle.read, self._buffer_bytes)
                if not chunk:
                    break
                digest.update(chunk)
                total += len(chunk)
        finally:
            await self._run_io(handle.close)
        return f"sha256:{digest.hexdigest()}", total

    async def _assert_metadata_matches_object(
        self, provider_id: str, metadata: dict[str, Any]
    ) -> None:
        """Quarantine any object that differs from provider metadata."""
        observed_sha256, observed_size = await self._hash_object(provider_id)
        if observed_sha256 != metadata.get("sha256") or observed_size != metadata.get("byte_count"):
            await self._quarantine_provider_object(provider_id, "object_metadata_mismatch")
            raise ArtifactIntegrityError("artifact provider facts are inconsistent")

    async def _load_available_metadata(self, provider_id: str) -> dict[str, Any]:
        """Load metadata only for an available integrity-valid object."""
        metadata = await self._read_json_required(self._path("metadata", provider_id, ".json"))
        if metadata.get("integrity_state") != "valid" or metadata.get("availability_state") != "available":
            raise ArtifactNotFoundError("artifact is unavailable")
        await self._run_io(self._assert_regular_file, self._path("objects", provider_id, ".blob"))
        return metadata

    async def _update_metadata(self, provider_id: str, **changes: Any) -> dict[str, Any]:
        """Atomically update mutable provider observations."""
        path = self._path("metadata", provider_id, ".json")
        metadata = await self._read_json_required(path)
        metadata.update(changes)
        await self._replace_json(path, metadata)
        return metadata

    async def _quarantine_provider_object(self, provider_id: str, reason: str) -> None:
        """Durably make a corrupt provider object unavailable."""
        source = self._path("objects", provider_id, ".blob")
        target = self._path("quarantine", provider_id, ".blob")
        observed: tuple[str, int] | None = None
        try:
            observed = await self._hash_object(provider_id)
        except FileNotFoundError:
            pass
        try:
            await self._run_io(self._move_to_quarantine, source, target)
        except FileNotFoundError:
            pass
        metadata_path = self._path("metadata", provider_id, ".json")
        try:
            persisted_metadata = await self._read_json_optional(metadata_path)
            metadata_exists = persisted_metadata is not None
            metadata = persisted_metadata or {}
        except ArtifactIntegrityError:
            metadata_exists = True
            metadata = {}
        if observed is not None:
            metadata.update(
                provider_artifact_id=provider_id,
                sha256=observed[0],
                byte_count=observed[1],
            )
        media_type = metadata.get("media_type")
        if not isinstance(media_type, str) or not media_type:
            metadata["media_type"] = "application/octet-stream"
        metadata.update(
            verification_state="failed",
            retention_state="unretained",
            retention_references={},
            integrity_state="quarantined",
            availability_state="unavailable",
            quarantine_reason=reason,
        )
        if metadata_exists:
            await self._replace_json(metadata_path, metadata)
        else:
            await self._write_json_exclusive(metadata_path, metadata)

    async def _object_exists(self, provider_id: str) -> bool:
        """Return whether a regular immutable object exists."""
        try:
            await self._run_io(self._assert_regular_file, self._path("objects", provider_id, ".blob"))
            return True
        except FileNotFoundError:
            return False

    async def _cleanup_unpublished(self, scope: str) -> None:
        """Remove only temporary state for an uncommitted operation."""
        intent = await self._read_json_optional(self._path("intents", scope, ".json"))
        if intent is None:
            return
        provider_id = intent.get("provider_artifact_id")
        if isinstance(provider_id, str) and _OPAQUE_ID.fullmatch(provider_id):
            await self._run_io(self._cleanup_provider_temporary_files, provider_id)

    def _cleanup_provider_temporary_files(self, provider_id: str) -> None:
        """Remove matching temporary files through a verified directory descriptor."""
        directory = self._open_directory_fd(self._root / "tmp")
        try:
            prefix = f"{provider_id}_"
            for name in os.listdir(directory):
                if name.startswith(prefix) and name.endswith(".part"):
                    os.unlink(name, dir_fd=directory)
            os.fsync(directory)
        finally:
            os.close(directory)

    def _new_metadata(
        self,
        *,
        provider_artifact_id: str,
        sha256: str,
        byte_count: int,
        media_type: str | None,
    ) -> dict[str, Any]:
        """Build provider-owned object metadata."""
        return {
            "provider_artifact_id": provider_artifact_id,
            "sha256": sha256,
            "byte_count": byte_count,
            "media_type": media_type,
            "verification_state": "pending",
            "retention_state": "unretained",
            "availability_state": "available",
            "integrity_state": "valid",
            "retention_references": {},
        }

    def _make_receipt(
        self,
        *,
        identity: IdempotencyIdentity,
        operation_reference: str,
        outcome: ReceiptOutcome,
        provider_artifact_id: str,
        sha256: str,
        byte_count: int,
        retention_reference: str | None = None,
        retention_class: str | None = None,
    ) -> OperationReceipt:
        """Build a bounded receipt and its canonical response digest."""
        receipt_id = f"receipt_{uuid4().hex}"
        response = self._receipt_response_payload(
            receipt_id=receipt_id,
            operation_reference=operation_reference,
            provider_artifact_id=provider_artifact_id,
            sha256=sha256,
            byte_count=byte_count,
            outcome=outcome,
            retention_reference=retention_reference,
            retention_class=retention_class,
        )
        return OperationReceipt(
            receipt_id=receipt_id,
            provider_operation_reference=operation_reference,
            identity=identity,
            response_digest=canonical_json_hash(response),
            outcome=outcome,
            provider_artifact_id=provider_artifact_id,
            sha256=sha256,
            byte_count=byte_count,
            recorded_at=datetime.now(UTC),
            retention_reference=retention_reference,
            retention_class=retention_class,
        )

    @staticmethod
    def _receipt_response_payload(
        *,
        receipt_id: str,
        operation_reference: str,
        provider_artifact_id: str | None,
        sha256: str | None,
        byte_count: int | None,
        outcome: ReceiptOutcome,
        retention_reference: str | None,
        retention_class: str | None,
    ) -> dict[str, Any]:
        """Build the one canonical operation-response payload."""
        response: dict[str, Any] = {
            "receipt_id": receipt_id,
            "provider_operation_id": operation_reference,
            "provider_artifact_id": provider_artifact_id,
            "sha256": sha256,
            "byte_count": byte_count,
            "outcome": outcome.value,
        }
        if retention_reference is not None:
            response["retention_reference"] = retention_reference
        if retention_class is not None:
            response["retention_class"] = retention_class
        return response

    @classmethod
    def _receipt_response_digest(cls, receipt: OperationReceipt) -> str:
        """Recompute the canonical operation response commitment."""
        response = cls._receipt_response_payload(
            receipt_id=receipt.receipt_id,
            operation_reference=receipt.provider_operation_reference,
            provider_artifact_id=receipt.provider_artifact_id,
            sha256=receipt.sha256,
            byte_count=receipt.byte_count,
            outcome=receipt.outcome,
            retention_reference=receipt.retention_reference,
            retention_class=receipt.retention_class,
        )
        return canonical_json_hash(response)

    @staticmethod
    def _receipt_to_json(receipt: OperationReceipt) -> dict[str, Any]:
        """Serialize a receipt for private provider persistence."""
        return {
            "receipt_id": receipt.receipt_id,
            "provider_operation_reference": receipt.provider_operation_reference,
            "service_principal": receipt.identity.service_principal,
            "operation": receipt.identity.operation.value,
            "idempotency_key": receipt.identity.key,
            "request_digest": receipt.identity.request_digest,
            "response_digest": receipt.response_digest,
            "outcome": receipt.outcome.value,
            "provider_artifact_id": receipt.provider_artifact_id,
            "sha256": receipt.sha256,
            "byte_count": receipt.byte_count,
            "recorded_at": receipt.recorded_at.isoformat(),
            "retention_reference": receipt.retention_reference,
            "retention_class": receipt.retention_class,
            "details": [
                {"name": detail.name, "value": detail.value} for detail in receipt.details
            ],
        }

    def _receipt_from_json(self, payload: dict[str, Any]) -> OperationReceipt:
        """Parse and validate private provider receipt evidence."""
        try:
            identity = IdempotencyIdentity(
                service_principal=payload["service_principal"],
                operation=ArtifactOperation(payload["operation"]),
                key=payload["idempotency_key"],
                request_digest=payload["request_digest"],
            )
            self._validate_identity(identity, identity.operation)
            provider_id = self._validated_provider_id(payload["provider_artifact_id"])
            self._validate_digest(payload["response_digest"])
            self._validate_digest(payload["sha256"])
            if not _OPERATION_REF.fullmatch(payload["provider_operation_reference"]):
                raise ValueError
            byte_count = int(payload["byte_count"])
            details_payload = payload.get("details", [])
            if (
                byte_count < 0
                or not isinstance(details_payload, list)
                or len(details_payload) > 16
            ):
                raise ValueError
            details = tuple(
                ReceiptDetail(name=detail["name"], value=detail["value"])
                for detail in details_payload
            )
            if any(
                set(detail) != {"name", "value"}
                or not isinstance(detail["name"], str)
                or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", detail["name"])
                or not isinstance(detail["value"], str)
                or len(detail["value"]) > 512
                for detail in details_payload
            ):
                raise ValueError
            receipt = OperationReceipt(
                receipt_id=payload["receipt_id"],
                provider_operation_reference=payload["provider_operation_reference"],
                identity=identity,
                response_digest=payload["response_digest"],
                outcome=ReceiptOutcome(payload["outcome"]),
                provider_artifact_id=provider_id,
                sha256=payload["sha256"],
                byte_count=byte_count,
                recorded_at=datetime.fromisoformat(payload["recorded_at"]),
                retention_reference=payload.get("retention_reference"),
                retention_class=payload.get("retention_class"),
                details=details,
            )
            if not re.fullmatch(r"receipt_[0-9a-f]{32}", receipt.receipt_id):
                raise ValueError
            if receipt.response_digest != self._receipt_response_digest(receipt):
                raise ValueError
            return receipt
        except (
            ArtifactInputMismatchError,
            ArtifactMalformedRequestError,
            ArtifactNotFoundError,
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise ArtifactIntegrityError("artifact operation receipt is invalid") from exc

    def _assert_same_request(
        self, intent: dict[str, Any], identity: IdempotencyIdentity
    ) -> None:
        """Reject reuse of one operation identity with changed request content."""
        if intent.get("request_digest") != identity.request_digest:
            raise ArtifactIdempotencyMismatchError("artifact operation request changed")

    def _assert_retention_intent(
        self,
        intent: dict[str, Any],
        identity: IdempotencyIdentity,
        provider_artifact_id: str,
        retention_reference: str,
        retention_class: str | None,
        *,
        releasing: bool,
    ) -> None:
        """Validate a durable retention intent before completing recovery."""
        expected_class = None if releasing else retention_class
        if (
            intent.get("service_principal") != identity.service_principal
            or intent.get("operation") != identity.operation.value
            or intent.get("idempotency_key") != identity.key
            or intent.get("request_digest") != identity.request_digest
            or intent.get("provider_artifact_id") != provider_artifact_id
            or intent.get("retention_reference") != retention_reference
            or (not releasing and intent.get("retention_class") != expected_class)
            or not _OPERATION_REF.fullmatch(
                str(intent.get("provider_operation_reference", ""))
            )
        ):
            raise ArtifactIdempotencyMismatchError("artifact retention intent changed")

    def _assert_receipt_identity(
        self, receipt: OperationReceipt, identity: IdempotencyIdentity
    ) -> None:
        """Require exact operation identity and request digest."""
        if receipt.identity != identity:
            raise ArtifactIdempotencyMismatchError("artifact operation request changed")

    def _assert_operation_receipt(
        self,
        receipt: OperationReceipt,
        identity: IdempotencyIdentity,
        provider_artifact_id: str,
        outcome: ReceiptOutcome,
        *,
        retention_reference: str | None = None,
    ) -> None:
        """Require replay evidence to describe the requested provider effect."""
        self._assert_receipt_identity(receipt, identity)
        if (
            receipt.provider_artifact_id != provider_artifact_id
            or receipt.outcome != outcome
            or receipt.retention_reference != retention_reference
        ):
            raise ArtifactIntegrityError("artifact receipt facts do not match the operation")

    def _assert_receipt_matches(
        self,
        receipt: OperationReceipt,
        identity: IdempotencyIdentity,
        metadata: dict[str, Any],
    ) -> None:
        """Reject altered receipt facts and quarantine through caller."""
        self._assert_receipt_identity(receipt, identity)
        if (
            receipt.outcome != ReceiptOutcome.STORED
            or receipt.provider_artifact_id != metadata.get("provider_artifact_id")
            or receipt.sha256 != metadata.get("sha256")
            or receipt.byte_count != metadata.get("byte_count")
            or receipt.retention_reference is not None
            or receipt.retention_class is not None
        ):
            raise ArtifactIntegrityError("artifact receipt does not match provider metadata")

    def _status_from_metadata(self, metadata: dict[str, Any]) -> ArtifactStatus:
        """Convert private metadata into a provider-neutral status."""
        try:
            media_type = metadata["media_type"]
            if not isinstance(media_type, str) or not media_type:
                raise ValueError
            self._validate_digest(metadata["sha256"])
            byte_count = int(metadata["byte_count"])
            if byte_count < 0:
                raise ValueError
            return ArtifactStatus(
                provider_artifact_id=self._validated_provider_id(
                    metadata["provider_artifact_id"]
                ),
                sha256=metadata["sha256"],
                byte_count=byte_count,
                media_type=media_type,
                verification_state=VerificationState(metadata["verification_state"]),
                retention_state=RetentionState(metadata["retention_state"]),
                availability_state=AvailabilityState(metadata["availability_state"]),
                integrity_state=IntegrityState(metadata["integrity_state"]),
                active_retentions=tuple(
                    RetentionSummary(
                        retention_reference=reference,
                        retention_class=value["retention_class"],
                        state="active",
                    )
                    for reference, value in sorted(
                        metadata.get("retention_references", {}).items()
                    )
                ),
            )
        except (
            ArtifactMalformedRequestError,
            ArtifactNotFoundError,
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise ArtifactIntegrityError("artifact provider metadata is invalid") from exc

    async def _read_json_optional(self, path: Path) -> dict[str, Any] | None:
        """Read a regular private JSON file when it exists."""
        try:
            return await self._run_io(self._read_json_sync, path)
        except FileNotFoundError:
            return None
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise ArtifactIntegrityError("artifact provider metadata is invalid") from exc

    async def _read_json_required(self, path: Path) -> dict[str, Any]:
        """Read required private JSON without leaking its path."""
        value = await self._read_json_optional(path)
        if value is None:
            raise ArtifactNotFoundError("artifact is unavailable")
        return value

    async def _write_json_exclusive(self, path: Path, value: dict[str, Any]) -> None:
        """Atomically publish one immutable private JSON record."""
        await self._run_io(self._write_json_sync, path, value, True)

    async def _replace_json(self, path: Path, value: dict[str, Any]) -> None:
        """Atomically replace one mutable provider observation record."""
        await self._run_io(self._write_json_sync, path, value, False)

    async def _run_io(self, function: Any, *args: Any) -> Any:
        """Complete one blocking filesystem call before propagating cancellation."""
        task = asyncio.create_task(asyncio.to_thread(function, *args))
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            try:
                await task
            finally:
                raise

    async def _acquire_lock_async(self, scope: str) -> tuple[Any, int]:
        """Acquire a lock without leaking it when task cancellation wins the race."""
        task = asyncio.create_task(asyncio.to_thread(self._acquire_lock, scope))
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            lock = await task
            await asyncio.to_thread(self._release_lock, lock)
            raise

    @contextmanager
    def _locked_file(self, path: Path) -> Iterator[int]:
        """Open and exclusively lock one private regular file."""
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        directory = self._open_directory_fd(path.parent)
        descriptor: int | None = None
        try:
            descriptor = os.open(path.name, flags, 0o600, dir_fd=directory)
            self._assert_private_descriptor(descriptor)
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield descriptor
        finally:
            if descriptor is not None:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
                os.close(descriptor)
            os.close(directory)

    def _acquire_lock(self, scope: str) -> tuple[Any, int]:
        """Acquire a cross-process operation lock."""
        manager = self._locked_file(self._path("locks", scope, ".lock"))
        descriptor = manager.__enter__()
        return manager, descriptor

    @staticmethod
    def _release_lock(lock: tuple[Any, int]) -> None:
        """Release a cross-process operation lock."""
        manager, _ = lock
        manager.__exit__(None, None, None)

    def _open_exclusive(self, path: Path) -> int:
        """Open a new no-follow private file."""
        directory = self._open_directory_fd(path.parent)
        try:
            descriptor = os.open(
                path.name,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=directory,
            )
            self._assert_private_descriptor(descriptor)
            return descriptor
        finally:
            os.close(directory)

    @staticmethod
    def _write_all(descriptor: int, chunk: memoryview) -> None:
        """Write one bounded memory view completely."""
        remaining = chunk
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:
                raise OSError("short artifact write")
            remaining = remaining[written:]

    def _publish_exclusive(self, temporary: Path, final: Path) -> None:
        """Publish without overwriting an immutable object."""
        source_directory = self._open_directory_fd(temporary.parent)
        target_directory = self._open_directory_fd(final.parent)
        try:
            os.link(
                temporary.name,
                final.name,
                src_dir_fd=source_directory,
                dst_dir_fd=target_directory,
                follow_symlinks=False,
            )
            os.unlink(temporary.name, dir_fd=source_directory)
            os.fsync(source_directory)
            os.fsync(target_directory)
        finally:
            os.close(source_directory)
            os.close(target_directory)

    def _unlink_optional(self, path: Path) -> None:
        """Remove a private temporary file when present."""
        directory = self._open_directory_fd(path.parent)
        try:
            try:
                os.unlink(path.name, dir_fd=directory)
            except FileNotFoundError:
                pass
        finally:
            os.close(directory)

    def _open_regular_object(self, provider_id: str) -> BinaryIO:
        """Open one no-follow regular object with exactly one link."""
        path = self._path("objects", provider_id, ".blob")
        directory = self._open_directory_fd(path.parent)
        try:
            descriptor = os.open(
                path.name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory,
            )
        finally:
            os.close(directory)
        self._assert_private_descriptor(descriptor)
        return os.fdopen(descriptor, "rb", buffering=0)

    def _assert_regular_file(self, path: Path) -> None:
        """Require a no-follow regular file with one hard link."""
        directory = self._open_directory_fd(path.parent)
        descriptor: int | None = None
        try:
            descriptor = os.open(
                path.name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory,
            )
            self._assert_private_descriptor(descriptor)
        finally:
            if descriptor is not None:
                os.close(descriptor)
            os.close(directory)

    def _read_json_sync(self, path: Path) -> dict[str, Any]:
        """Read bounded JSON from a no-follow regular file."""
        directory = self._open_directory_fd(path.parent)
        descriptor: int | None = None
        try:
            descriptor = os.open(
                path.name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory,
            )
            self._assert_private_descriptor(descriptor)
            raw = os.read(descriptor, 65_537)
            if len(raw) > 65_536 or os.read(descriptor, 1):
                raise ValueError("provider metadata exceeds limit")
        finally:
            if descriptor is not None:
                os.close(descriptor)
            os.close(directory)
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("provider metadata must be an object")
        return value

    def _write_json_sync(self, path: Path, value: dict[str, Any], exclusive: bool) -> None:
        """Atomically publish and synchronize one private JSON file."""
        raw = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
        if len(raw) > 65_536:
            raise ValueError("provider metadata exceeds limit")
        temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        descriptor = self._open_exclusive(temporary)
        try:
            self._write_all(descriptor, memoryview(raw))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        try:
            if exclusive:
                source_directory = self._open_directory_fd(temporary.parent)
                target_directory = self._open_directory_fd(path.parent)
                try:
                    os.link(
                        temporary.name,
                        path.name,
                        src_dir_fd=source_directory,
                        dst_dir_fd=target_directory,
                        follow_symlinks=False,
                    )
                    os.unlink(temporary.name, dir_fd=source_directory)
                    os.fsync(source_directory)
                    os.fsync(target_directory)
                finally:
                    os.close(source_directory)
                    os.close(target_directory)
            else:
                self._assert_regular_file(path)
                source_directory = self._open_directory_fd(temporary.parent)
                target_directory = self._open_directory_fd(path.parent)
                try:
                    os.replace(
                        temporary.name,
                        path.name,
                        src_dir_fd=source_directory,
                        dst_dir_fd=target_directory,
                    )
                    os.fsync(source_directory)
                    os.fsync(target_directory)
                finally:
                    os.close(source_directory)
                    os.close(target_directory)
        except BaseException:
            self._unlink_optional(temporary)
            raise

    def _fsync_directory(self, path: Path) -> None:
        """Synchronize one directory entry update."""
        descriptor = self._open_directory_fd(path)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _move_to_quarantine(self, source: Path, target: Path) -> None:
        """Move a provider object to private quarantine without overwriting."""
        try:
            source_directory = self._open_directory_fd(source.parent)
            target_directory = self._open_directory_fd(target.parent)
            try:
                os.link(
                    source.name,
                    target.name,
                    src_dir_fd=source_directory,
                    dst_dir_fd=target_directory,
                    follow_symlinks=False,
                )
                os.unlink(source.name, dir_fd=source_directory)
                os.fsync(source_directory)
                os.fsync(target_directory)
            finally:
                os.close(source_directory)
                os.close(target_directory)
        except FileNotFoundError:
            try:
                self._assert_regular_file(target)
            except FileNotFoundError:
                raise

    def _open_directory_fd(self, path: Path) -> int:
        """Open a verified storage subdirectory relative to the pinned root."""
        if path.parent != self._root or path.name not in {
            "objects",
            "metadata",
            "receipts",
            "intents",
            "locks",
            "tmp",
            "quarantine",
        }:
            raise ArtifactIntegrityError("artifact provider directory is invalid")
        descriptor = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=self._root_fd,
        )
        details = os.fstat(descriptor)
        if not stat_module.S_ISDIR(details.st_mode):
            os.close(descriptor)
            raise ArtifactIntegrityError("artifact provider directory is invalid")
        return descriptor

    @staticmethod
    def _assert_private_descriptor(descriptor: int) -> None:
        """Require an opened provider file to be regular and single-linked."""
        details = os.fstat(descriptor)
        if not stat_module.S_ISREG(details.st_mode) or details.st_nlink != 1:
            raise ArtifactIntegrityError("artifact provider file is invalid")
