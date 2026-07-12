"""Transaction-safe artifact ingest and reconciliation orchestration."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.interfaces.artifacts import (
    ArtifactOperationResult,
    ArtifactStatus,
    ArtifactInputMismatchError,
    ArtifactIntegrityError,
    ArtifactNotFoundError,
    ArtifactStore,
    ArtifactStoreError,
    IdempotencyIdentity,
    OperationReceipt,
    ReceiptOutcome,
    StoreArtifactRequest,
    StoredArtifact,
)
from app.modules.artifacts.models import (
    ArtifactContent,
    ArtifactOperationReceipt,
    ArtifactReplica,
    ArtifactUploadItem,
    ArtifactUploadSession,
)
from app.modules.artifacts.repository import ArtifactRepository
from app.modules.audit.repository import AuditRepository
from app.modules.tasks.models import AuditEvent

RECONCILER_ACTOR_ID = "workstream.artifact.reconciler"
RECONCILER_ISSUER = "https://workstream.internal"


class ArtifactIngestStateError(Exception):
    """Raised when an artifact item cannot perform the requested transition."""


@dataclass(frozen=True, slots=True)
class ProviderAttemptFence:
    """Committed item/session CAS values fencing one provider attempt."""

    item_cas: int
    session_cas: int


class ArtifactIngestService:
    """Coordinate Workstream transactions around provider artifact I/O."""

    def __init__(self, session: AsyncSession, store: ArtifactStore, *, adapter_name: str) -> None:
        """Create an ingest coordinator.

        Args:
            session: Database session owned by this ingest operation.
            store: Provider-neutral artifact store.
            adapter_name: Stable configured adapter name.
        """
        self._session = session
        self._store = store
        self._adapter_name = adapter_name
        self._repo = ArtifactRepository(session)
        self._audit_repo = AuditRepository(session)

    async def ingest_reserved_item(
        self,
        item_id: str,
        stream: AsyncIterable[bytes],
        request: StoreArtifactRequest,
    ) -> StoredArtifact:
        """Commit intent, call provider outside a transaction, then persist facts.

        Args:
            item_id: Reserved upload-item identifier.
            stream: Exact bytes to store or replay.
            request: Provider request matching the persisted item commitment.

        Returns:
            Provider-neutral stored artifact result.

        Raises:
            ArtifactIngestStateError: If the persisted intent is incompatible.
            ArtifactStoreError: If provider ingest or verification fails.
        """
        attempt_cas = await self._start_provider_operation(item_id, request)
        try:
            stored = await self._store.store(stream, request)
        except asyncio.CancelledError:
            await asyncio.shield(
                self._mark_provider_recovery_required(
                    item_id, request, attempt_cas, provider_commit_confirmed=False
                )
            )
            raise
        except ArtifactStoreError as exc:
            if exc.retryable:
                await self._mark_provider_recovery_required(
                    item_id, request, attempt_cas, provider_commit_confirmed=False
                )
            else:
                await self._fail_pre_finalization(item_id, exc.code, attempt_cas)
            raise
        try:
            await self._finalize_provider_operation(item_id, request, stored, attempt_cas)
        except asyncio.CancelledError:
            await asyncio.shield(
                self._mark_provider_recovery_required(
                    item_id, request, attempt_cas, provider_commit_confirmed=True
                )
            )
            raise
        except (ArtifactIntegrityError, ArtifactInputMismatchError) as exc:
            await self._fail_pre_finalization(item_id, exc.code, attempt_cas)
            raise
        except Exception:
            await self._mark_provider_recovery_required(
                item_id, request, attempt_cas, provider_commit_confirmed=True
            )
            raise
        return stored

    async def reconcile_committed_item(
        self, item_id: str, request: StoreArtifactRequest
    ) -> StoredArtifact:
        """Finalize a committed provider effect without replaying client bytes."""
        attempt_cas = await self._resume_provider_committed(item_id, request)
        try:
            stored = await self._store.recover_committed_store(request)
            observed_sha256, observed_size = await self._hash_provider_object(
                stored.provider_artifact_id, request.maximum_bytes
            )
            if observed_sha256 != stored.sha256 or observed_size != stored.byte_count:
                raise ArtifactIntegrityError("recovered provider bytes changed")
            await self._finalize_provider_operation(item_id, request, stored, attempt_cas)
            return stored
        except (ArtifactIntegrityError, ArtifactInputMismatchError) as exc:
            await self._fail_pre_finalization(item_id, exc.code, attempt_cas)
            raise
        except ArtifactNotFoundError:
            await self._mark_provider_recovery_required(
                item_id, request, attempt_cas, provider_commit_confirmed=False
            )
            raise
        except BaseException:
            await asyncio.shield(
                self._mark_provider_recovery_required(
                    item_id, request, attempt_cas, provider_commit_confirmed=True
                )
            )
            raise

    async def _hash_provider_object(
        self, provider_artifact_id: str, maximum_bytes: int
    ) -> tuple[str, int]:
        """Independently hash and count complete provider bytes."""
        import hashlib

        digest = hashlib.sha256()
        byte_count = 0
        async for chunk in self._store.open(provider_artifact_id):
            digest.update(chunk)
            byte_count += len(chunk)
            if byte_count > maximum_bytes:
                raise ArtifactIntegrityError("recovered provider bytes exceed the request limit")
        return f"sha256:{digest.hexdigest()}", byte_count

    async def _resume_provider_committed(
        self, item_id: str, request: StoreArtifactRequest
    ) -> ProviderAttemptFence:
        """Fence one receipt-based recovery attempt for a committed provider effect."""
        async with self._session.begin():
            item = await self._repo.lock_upload_item(item_id)
            if item is None or item.state != "provider_committed":
                raise ArtifactIngestStateError("artifact item is not provider committed")
            if (
                item.request_digest != request.idempotency.request_digest
                or item.idempotency_key != request.idempotency.key
                or item.expected_sha256 != request.expected_sha256
                or item.expected_size != request.expected_size
            ):
                raise ArtifactIngestStateError("artifact recovery commitment changed")
            item.state = "uploading"
            item.error_code = None
            item.cas_version += 1
            upload_session = await self._repo.lock_upload_session(item.session_id)
            if upload_session is None or upload_session.state != "open":
                raise ArtifactIngestStateError("artifact upload session is not open")
            upload_session.cas_version += 1
            return ProviderAttemptFence(item.cas_version, upload_session.cas_version)

    async def _start_provider_operation(
        self, item_id: str, request: StoreArtifactRequest
    ) -> ProviderAttemptFence:
        """Transaction A: lock and commit the exact provider intent."""
        async with self._session.begin():
            item = await self._repo.lock_upload_item(item_id)
            if item is None:
                raise ArtifactIngestStateError("artifact upload item does not exist")
            upload_session = await self._repo.lock_upload_session(item.session_id)
            if upload_session is None or upload_session.state != "open":
                raise ArtifactIngestStateError("artifact upload session is not open")
            if item.state not in {"reserved", "replay_required"}:
                raise ArtifactIngestStateError("artifact upload item cannot be ingested")
            if item.request_digest != request.idempotency.request_digest:
                raise ArtifactIngestStateError("artifact upload request digest changed")
            if item.idempotency_key != request.idempotency.key:
                raise ArtifactIngestStateError("artifact upload idempotency key changed")
            if item.expected_sha256 != request.expected_sha256 or item.expected_size != request.expected_size:
                raise ArtifactIngestStateError("artifact upload commitment changed")
            if request.maximum_bytes > item.reserved_bytes:
                raise ArtifactIngestStateError("artifact upload maximum exceeds its reservation")
            if request.expected_size is not None and request.expected_size > item.reserved_bytes:
                raise ArtifactIngestStateError("artifact expected size exceeds its reservation")
            if (
                upload_session.current_bytes + upload_session.reserved_bytes
                > upload_session.maximum_bytes
                or upload_session.current_items + upload_session.reserved_items
                > upload_session.maximum_items
                or upload_session.reserved_bytes < item.reserved_bytes
                or upload_session.reserved_items < 1
            ):
                raise ArtifactIngestStateError("artifact upload reservation is inconsistent")
            item.state = "uploading"
            item.cas_version += 1
            upload_session.cas_version += 1
            return ProviderAttemptFence(item.cas_version, upload_session.cas_version)

    async def _finalize_provider_operation(
        self,
        item_id: str,
        request: StoreArtifactRequest,
        stored: StoredArtifact,
        attempt_cas: ProviderAttemptFence,
    ) -> None:
        """Transaction B: verify provider facts and persist immutable records."""
        if stored.sha256 != stored.receipt.sha256 or stored.byte_count != stored.receipt.byte_count:
            raise ArtifactIntegrityError("provider receipt disagrees with stored artifact")
        if stored.receipt.identity != request.idempotency:
            raise ArtifactIntegrityError("provider receipt identity disagrees with request")
        if (
            stored.receipt.outcome != ReceiptOutcome.STORED
            or stored.receipt.provider_artifact_id != stored.provider_artifact_id
            or stored.byte_count > request.maximum_bytes
        ):
            raise ArtifactIntegrityError("provider result disagrees with the store operation")
        if (
            request.expected_sha256 is not None
            and stored.sha256 != request.expected_sha256
        ) or (
            request.expected_size is not None
            and stored.byte_count != request.expected_size
        ):
            raise ArtifactIntegrityError("provider result violates the persisted commitment")
        async with self._session.begin():
            item = await self._repo.lock_upload_item(item_id)
            if (
                item is None
                or item.state != "uploading"
                or item.cas_version != attempt_cas.item_cas
            ):
                raise ArtifactIngestStateError("artifact upload item is not awaiting finalization")
            upload_session = await self._repo.lock_upload_session(item.session_id)
            if upload_session is None or upload_session.state != "open":
                raise ArtifactIngestStateError("artifact upload session changed during ingest")
            if upload_session.cas_version != attempt_cas.session_cas:
                raise ArtifactIngestStateError("artifact upload session CAS changed during ingest")
            if (
                item.request_digest != request.idempotency.request_digest
                or item.idempotency_key != request.idempotency.key
                or item.expected_sha256 != request.expected_sha256
                or item.expected_size != request.expected_size
                or stored.byte_count > item.reserved_bytes
                or upload_session.reserved_bytes < item.reserved_bytes
                or upload_session.reserved_items < 1
            ):
                raise ArtifactIngestStateError("artifact upload intent changed during ingest")
            existing_receipt = await self._repo.get_receipt(
                self._adapter_name,
                request.idempotency.service_principal,
                request.idempotency.operation.value,
                request.idempotency.key,
            )
            if existing_receipt is not None:
                if existing_receipt.request_digest != request.idempotency.request_digest:
                    raise ArtifactIntegrityError("stored operation receipt request digest changed")
                if (
                    existing_receipt.response_digest != stored.receipt.response_digest
                    or existing_receipt.provider_receipt_id != stored.receipt.receipt_id
                    or existing_receipt.outcome != ReceiptOutcome.STORED.value
                    or existing_receipt.provider_operation_reference
                    != stored.receipt.provider_operation_reference
                ):
                    raise ArtifactIntegrityError("stored operation receipt facts changed")
                existing_replica = await self._repo.get_replica_by_provider_id(
                    self._adapter_name, stored.provider_artifact_id
                )
                if existing_replica is None:
                    raise ArtifactIntegrityError("stored operation receipt has no replica")
                item.state = "ready"
                item.provider_operation_reference = stored.receipt.provider_operation_reference
                item.content_id = existing_replica.content_id
                item.cas_version += 1
                self._apply_ready_accounting(upload_session, item, stored.byte_count)
                return
            content = await self._repo.get_or_create_content(
                ArtifactContent(
                    id=str(uuid4()),
                    sha256=stored.sha256,
                    byte_count=stored.byte_count,
                    media_type=stored.media_type,
                    normalized_display_name=item.display_name,
                )
            )
            replica = await self._repo.add_replica(
                ArtifactReplica(
                    id=str(uuid4()),
                    content_id=content.id,
                    adapter=self._adapter_name,
                    provider_artifact_id=stored.provider_artifact_id,
                    verification_state="pending",
                    retention_state="unretained",
                    availability_state="available",
                    integrity_state="valid",
                )
            )
            await self._repo.add_receipt(
                self._operation_receipt_model(
                    stored.receipt,
                    adapter=self._adapter_name,
                    upload_item_id=item.id,
                    replica_id=replica.id,
                    retention_owner=(
                        request.idempotency.service_principal
                        if stored.receipt.retention_reference is not None
                        else None
                    ),
                )
            )
            item.state = "ready"
            item.content_id = content.id
            item.provider_operation_reference = stored.receipt.provider_operation_reference
            item.cas_version += 1
            self._apply_ready_accounting(upload_session, item, stored.byte_count)

    @staticmethod
    def _apply_ready_accounting(
        upload_session: ArtifactUploadSession,
        item: ArtifactUploadItem,
        byte_count: int,
    ) -> None:
        """Move one committed item reservation into exact session totals."""
        upload_session.reserved_bytes -= item.reserved_bytes
        upload_session.reserved_items -= 1
        upload_session.current_bytes += byte_count
        upload_session.current_items += 1
        upload_session.cas_version += 1

    async def _mark_provider_recovery_required(
        self,
        item_id: str,
        request: StoreArtifactRequest,
        expected_fence: ProviderAttemptFence,
        *,
        provider_commit_confirmed: bool,
    ) -> None:
        """Record a provider effect that Workstream could not yet finalize."""
        await self._session.rollback()
        async with self._session.begin():
            item = await self._repo.lock_upload_item(item_id)
            if (
                item is None
                or item.state != "uploading"
                or item.cas_version != expected_fence.item_cas
            ):
                return
            item.state = (
                "provider_committed"
                if provider_commit_confirmed
                and request.expected_sha256 is not None
                and request.expected_size is not None
                else "replay_required"
            )
            item.error_code = "artifact_finalization_pending"
            item.cas_version += 1

    async def _fail_pre_finalization(
        self,
        item_id: str,
        error_code: str,
        expected_fence: ProviderAttemptFence,
    ) -> None:
        """Fail an unpromoted item without creating content, replica, or binding."""
        await self._session.rollback()
        async with self._session.begin():
            item = await self._repo.lock_upload_item(item_id)
            if (
                item is None
                or item.state != "uploading"
                or item.cas_version != expected_fence.item_cas
            ):
                return
            upload_session = await self._repo.lock_upload_session(item.session_id)
            item.state = "failed"
            item.error_code = error_code
            item.cas_version += 1
            if upload_session is not None:
                upload_session.reserved_bytes = max(
                    0, upload_session.reserved_bytes - item.reserved_bytes
                )
                upload_session.reserved_items = max(0, upload_session.reserved_items - 1)
                upload_session.cas_version += 1

    async def quarantine_existing_replica(
        self,
        adapter: str,
        provider_artifact_id: str,
        *,
        reason: str,
    ) -> None:
        """Record provider quarantine and audit it without mutating content facts."""
        async with self._session.begin():
            current = await self._repo.lock_replica_by_provider_id(
                adapter, provider_artifact_id
            )
            if current is None or current.integrity_state == "quarantined":
                return
            previous_integrity_state = current.integrity_state
            current.integrity_state = "quarantined"
            current.availability_state = "unavailable"
            current.last_reconciled_at = datetime.now(UTC)
            await self._audit_repo.add_audit_event(
                self._service_audit_event(
                    current.id,
                    "artifact_replica_quarantined",
                    previous_integrity_state,
                    "quarantined",
                    RECONCILER_ACTOR_ID,
                    {"adapter": current.adapter},
                    reason=reason,
                )
            )

    async def retain_replica(
        self,
        adapter: str,
        provider_artifact_id: str,
        retention_reference: str,
        retention_class: str,
        identity: IdempotencyIdentity,
    ) -> ArtifactOperationResult:
        """Retain one replica and copy provider evidence into Workstream."""
        result = await self._store.retain(
            provider_artifact_id,
            retention_reference,
            retention_class,
            identity,
        )
        await self._record_retention_result(adapter, result, identity, retained=True)
        return result

    async def release_replica(
        self,
        adapter: str,
        provider_artifact_id: str,
        retention_reference: str,
        identity: IdempotencyIdentity,
    ) -> ArtifactOperationResult:
        """Release one owned reference and audit the Workstream transition."""
        result = await self._store.release(
            provider_artifact_id,
            retention_reference,
            identity,
        )
        status = await self._store.stat(provider_artifact_id)
        await self._record_retention_result(
            adapter,
            result,
            identity,
            retained=bool(status.active_retentions),
            audit_release=True,
        )
        return result

    async def reconcile_replica(
        self, adapter: str, provider_artifact_id: str
    ) -> ArtifactStatus:
        """Copy current provider observations and audit any state correction."""
        status = await self._store.stat(provider_artifact_id)
        async with self._session.begin():
            replica = await self._repo.lock_replica_by_provider_id(
                adapter, provider_artifact_id
            )
            if replica is None:
                raise ArtifactIngestStateError("artifact replica does not exist")
            before = {
                "verification_state": replica.verification_state,
                "retention_state": replica.retention_state,
                "availability_state": replica.availability_state,
                "integrity_state": replica.integrity_state,
            }
            after = {
                "verification_state": status.verification_state.value,
                "retention_state": status.retention_state.value,
                "availability_state": status.availability_state.value,
                "integrity_state": status.integrity_state.value,
            }
            provider_observation = dict(after)
            if before["integrity_state"] == "quarantined":
                after["integrity_state"] = "quarantined"
                after["availability_state"] = "unavailable"
            for field_name, value in after.items():
                setattr(replica, field_name, value)
            replica.last_reconciled_at = datetime.now(UTC)
            if before != after:
                await self._audit_repo.add_audit_event(
                    self._service_audit_event(
                        replica.id,
                        "artifact_replica_reconciled",
                        before["integrity_state"],
                        after["integrity_state"],
                        RECONCILER_ACTOR_ID,
                        {
                            "adapter": adapter,
                            "before": before,
                            "after": after,
                            "provider_observation": provider_observation,
                        },
                    )
                )
        return status

    async def _record_retention_result(
        self,
        adapter: str,
        result: ArtifactOperationResult,
        identity: IdempotencyIdentity,
        *,
        retained: bool,
        audit_release: bool = False,
    ) -> None:
        """Persist one provider retention receipt and matching replica state."""
        receipt = result.receipt
        if (
            receipt.identity != identity
            or receipt.provider_artifact_id is None
            or receipt.retention_reference is None
            or (
                identity.operation.value == "retain"
                and receipt.outcome != ReceiptOutcome.RETAINED
            )
            or (
                identity.operation.value == "release"
                and receipt.outcome != ReceiptOutcome.RELEASED
            )
        ):
            raise ArtifactIntegrityError("provider retention receipt is inconsistent")
        async with self._session.begin():
            replica = await self._repo.lock_replica_by_provider_id(
                adapter, receipt.provider_artifact_id
            )
            if replica is None:
                raise ArtifactIngestStateError("artifact replica does not exist")
            existing = await self._repo.get_receipt(
                adapter,
                identity.service_principal,
                identity.operation.value,
                identity.key,
            )
            receipt_created = existing is None
            if existing is None:
                await self._repo.add_receipt(
                    self._operation_receipt_model(
                        receipt,
                        adapter=adapter,
                        replica_id=replica.id,
                        retention_owner=identity.service_principal,
                    )
                )
            elif (
                existing.request_digest != identity.request_digest
                or existing.response_digest != receipt.response_digest
                or existing.provider_receipt_id != receipt.receipt_id
                or existing.provider_operation_reference
                != receipt.provider_operation_reference
                or existing.outcome != receipt.outcome.value
                or existing.retention_reference != receipt.retention_reference
                or existing.retention_class != receipt.retention_class
                or existing.retention_owner != identity.service_principal
            ):
                raise ArtifactIntegrityError("Workstream retention receipt changed")
            previous = replica.retention_state
            replica.retention_state = "retained" if retained else "released"
            replica.last_reconciled_at = datetime.now(UTC)
            if audit_release and receipt_created:
                await self._audit_repo.add_audit_event(
                    self._service_audit_event(
                        replica.id,
                        "artifact_retention_released",
                        previous,
                        replica.retention_state,
                        identity.service_principal,
                        {"retention_reference": receipt.retention_reference},
                    )
                )

    @staticmethod
    def _operation_receipt_model(
        receipt: OperationReceipt,
        *,
        adapter: str,
        replica_id: str,
        upload_item_id: str | None = None,
        retention_owner: str | None = None,
    ) -> ArtifactOperationReceipt:
        """Project one provider receipt into the append-only Workstream record."""
        return ArtifactOperationReceipt(
            id=str(uuid4()),
            upload_item_id=upload_item_id,
            replica_id=replica_id,
            adapter=adapter,
            service_principal=receipt.identity.service_principal,
            operation=receipt.identity.operation.value,
            idempotency_key=receipt.identity.key,
            request_digest=receipt.identity.request_digest,
            response_digest=receipt.response_digest,
            provider_receipt_id=receipt.receipt_id,
            provider_operation_reference=receipt.provider_operation_reference,
            outcome=receipt.outcome.value,
            attempt_number=1,
            correlation_id=str(uuid4()),
            retention_reference=receipt.retention_reference,
            retention_class=receipt.retention_class,
            retention_owner=retention_owner,
            provider_recorded_at=receipt.recorded_at,
            details=[
                {"name": detail.name, "value": detail.value}
                for detail in receipt.details
            ],
        )

    @staticmethod
    def _service_audit_event(
        replica_id: str,
        event_type: str,
        from_status: str,
        to_status: str,
        service_principal: str,
        payload: dict[str, object],
        *,
        reason: str | None = None,
    ) -> AuditEvent:
        """Build audit evidence attributed to an internal service principal."""
        return AuditEvent(
            id=str(uuid4()),
            entity_type="artifact_replica",
            entity_id=replica_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            actor_id=service_principal,
            external_subject=service_principal,
            external_issuer=RECONCILER_ISSUER,
            actor_roles=["service"],
            claim_snapshot={"service_principal": service_principal},
            auth_source="service",
            is_dev_auth=False,
            reason=reason,
            event_payload=payload,
        )
