"""Feature-neutral shared outbox append participant."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.hashing import canonical_json_hash
from app.modules.outbox.models import OutboxEvent
from app.modules.outbox.repository import OutboxRepository
from app.modules.outbox.schemas import (
    OutboxAppendDisposition,
    OutboxAppendInput,
    OutboxAppendResult,
    OutboxIdempotencyConflict,
    OutboxInputError,
    OutboxPersistenceError,
)


def _validated_input(value: object) -> OutboxAppendInput:
    """Revalidate a typed input without reflecting payload details in failures."""
    validated: OutboxAppendInput | None = None
    try:
        fields = dict(object.__getattribute__(value, "__dict__"))
        validated = OutboxAppendInput.model_validate(fields)
    except Exception:  # noqa: BLE001 - rejected values must not escape diagnostics
        pass
    if validated is None:
        raise OutboxInputError("outbox_invalid_input")
    return validated.model_copy(deep=True)


def _matches(record: OutboxEvent, value: OutboxAppendInput, digest: str) -> bool:
    """Compare every immutable caller fact while ignoring operational metadata."""
    return (
        record.event_id == value.event_id
        and record.event_type == value.event_type
        and record.event_version == value.event_version
        and record.producer == "workstream"
        and record.aggregate_type == value.aggregate_type
        and record.aggregate_id == value.aggregate_id
        and record.project_id == str(value.project_id)
        and record.correlation_id == value.correlation_id
        and record.causation_event_id == value.causation_event_id
        and record.idempotency_key == value.idempotency_key
        and record.payload_digest == digest
        and record.payload == value.payload
    )


class OutboxService:
    """Append immutable events by flushing only the caller-owned transaction."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the participant to one caller session; never commit or publish."""
        self._repository = OutboxRepository(session)

    async def append(self, value: OutboxAppendInput) -> OutboxAppendResult:
        """Create one event or return its exact idempotent replay."""
        validated = _validated_input(value)
        digest: str | None = None
        try:
            digest = canonical_json_hash(validated.payload)
        except (TypeError, ValueError):
            pass
        if digest is None:
            raise OutboxInputError("outbox_invalid_input")
        reservation = None
        try:
            reservation = await self._repository.reserve(validated, payload_digest=digest)
        except SQLAlchemyError:
            pass
        if reservation is None:
            raise OutboxPersistenceError("outbox_persistence_failed")
        if len(reservation.records) != 1 or not _matches(
            reservation.records[0], validated, digest
        ):
            raise OutboxIdempotencyConflict("outbox_idempotency_conflict")
        record = reservation.records[0]
        return OutboxAppendResult(
            event_id=record.event_id,
            disposition=(
                OutboxAppendDisposition.CREATED
                if reservation.created
                else OutboxAppendDisposition.REPLAYED
            ),
            payload_digest=record.payload_digest,
            occurred_at=record.occurred_at,
        )
