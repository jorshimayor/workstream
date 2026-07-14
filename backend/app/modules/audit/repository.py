"""Database access methods for shared audit records."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tasks.models import AuditEvent


class AuditRepository:
    """Wraps persistence for audit events independent of domain services."""

    def __init__(self, session: AsyncSession) -> None:
        """Create a repository bound to one database session.

        Args:
            session: Async SQLAlchemy session for the current unit of work.
        """
        self._session = session

    async def add_audit_event(self, event: AuditEvent) -> AuditEvent:
        """Persist an audit event.

        Args:
            event: Audit event model to persist.

        Returns:
            Persisted audit event model.
        """
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    async def list_audit_events(
        self, entity_type: str, entity_id: str
    ) -> Sequence[AuditEvent]:
        """List events for one entity in database creation order."""
        result = await self._session.execute(
            select(AuditEvent)
            .where(AuditEvent.entity_type == entity_type, AuditEvent.entity_id == entity_id)
            .order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc())
        )
        return result.scalars().all()
