"""Caller-transaction persistence for authority mutation idempotency."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.authorization.models import AuthorityIdempotencyRecord
from app.modules.authorization.schemas import (
    AuthorityClaimHandle,
    AuthorityOperation,
    AuthorityReservationResult,
    AuthorityResourceType,
    AuthorityResponseReference,
    ClaimedReservation,
    InvalidAuthorityClaimError,
    MismatchedReservation,
    PendingAuthorityReservationError,
    ReplayedReservation,
)
from app.modules.audit.schemas import ActorReferenceKind


class AuthorityIdempotencyRepository:
    """Reserve, lock, and complete records without transaction ownership."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind persistence operations to the caller-owned session."""

        self._session = session

    async def reserve(
        self,
        *,
        idempotency_key: UUID,
        actor_ref_kind: ActorReferenceKind,
        actor_ref: str,
        operation: AuthorityOperation,
        request_digest: str,
    ) -> AuthorityReservationResult:
        """Claim a new namespace or return its committed replay disposition."""
        values = {
            "id": uuid4(),
            "idempotency_key": idempotency_key,
            "actor_ref_kind": actor_ref_kind.value,
            "actor_ref": actor_ref,
            "operation": operation.value,
            "request_digest": request_digest,
            "status": "pending",
        }
        record_id = await self._session.scalar(
            insert(AuthorityIdempotencyRecord)
            .values(**values)
            .on_conflict_do_nothing(
                index_elements=[
                    AuthorityIdempotencyRecord.actor_ref_kind,
                    AuthorityIdempotencyRecord.actor_ref,
                    AuthorityIdempotencyRecord.operation,
                    AuthorityIdempotencyRecord.idempotency_key,
                ]
            )
            .returning(AuthorityIdempotencyRecord.id)
        )
        if record_id is not None:
            return ClaimedReservation(
                claim=AuthorityClaimHandle(
                    record_id=record_id,
                    idempotency_key=idempotency_key,
                    actor_ref_kind=actor_ref_kind,
                    actor_ref=actor_ref,
                    operation=operation,
                    request_digest=request_digest,
                )
            )

        record = await self._session.scalar(
            select(AuthorityIdempotencyRecord)
            .where(
                AuthorityIdempotencyRecord.actor_ref_kind == actor_ref_kind.value,
                AuthorityIdempotencyRecord.actor_ref == actor_ref,
                AuthorityIdempotencyRecord.operation == operation.value,
                AuthorityIdempotencyRecord.idempotency_key == idempotency_key,
            )
            .with_for_update()
        )
        if record is None:
            raise RuntimeError("authority reservation conflict was not visible")
        if record.request_digest != request_digest:
            return MismatchedReservation()
        if record.status == "pending":
            raise PendingAuthorityReservationError("authority reservation is pending")
        return ReplayedReservation(
            response=AuthorityResponseReference(
                resource_type=AuthorityResourceType(record.response_resource_type),
                resource_id=record.response_resource_id,
                version=record.response_resource_version,
                http_status=record.response_http_status,
            )
        )

    async def complete(
        self,
        claim: AuthorityClaimHandle,
        response: AuthorityResponseReference,
    ) -> None:
        """Atomically complete exactly the pending row owned by a claim handle."""
        result = await self._session.execute(
            update(AuthorityIdempotencyRecord)
            .where(
                AuthorityIdempotencyRecord.id == claim.record_id,
                AuthorityIdempotencyRecord.idempotency_key == claim.idempotency_key,
                AuthorityIdempotencyRecord.actor_ref_kind == claim.actor_ref_kind.value,
                AuthorityIdempotencyRecord.actor_ref == claim.actor_ref,
                AuthorityIdempotencyRecord.operation == claim.operation.value,
                AuthorityIdempotencyRecord.request_digest == claim.request_digest,
                AuthorityIdempotencyRecord.status == "pending",
            )
            .values(
                status="committed",
                response_resource_type=response.resource_type.value,
                response_resource_id=response.resource_id,
                response_resource_version=response.version,
                response_http_status=response.http_status,
            )
            .returning(AuthorityIdempotencyRecord.id)
        )
        if result.scalar_one_or_none() is None:
            raise InvalidAuthorityClaimError("invalid authority claim")
