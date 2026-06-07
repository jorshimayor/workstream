"""Database access methods for tasks, assignments, profiles, and audit events."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tasks.models import (
    AuditEvent,
    ReviewerProfile,
    TaskAssignment,
    WorkerProfile,
    WorkstreamTask,
)


class TaskRepository:
    """Wraps SQLAlchemy persistence for task queue operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Create a repository bound to one database session.

        Args:
            session: Async SQLAlchemy session for the current unit of work.
        """
        self._session = session

    async def add_task(self, task: WorkstreamTask) -> WorkstreamTask:
        """Persist a new task and refresh generated database fields.

        Args:
            task: Task model to persist.

        Returns:
            Persisted task model.
        """
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def get_task(self, task_id: str) -> WorkstreamTask | None:
        """Load one task by primary key.

        Args:
            task_id: Task id to load.

        Returns:
            Task model when found; otherwise ``None``.
        """
        return await self._session.get(WorkstreamTask, task_id)

    async def add_assignment(self, assignment: TaskAssignment) -> TaskAssignment:
        """Persist an assignment and refresh generated database fields.

        Args:
            assignment: Assignment model to persist.

        Returns:
            Persisted assignment model.
        """
        self._session.add(assignment)
        await self._session.flush()
        await self._session.refresh(assignment)
        return assignment

    async def get_active_assignment(self, task_id: str) -> TaskAssignment | None:
        """Load the active assignment for a task.

        Args:
            task_id: Task id whose active assignment should be loaded.

        Returns:
            Active assignment when present; otherwise ``None``.
        """
        result = await self._session.execute(
            select(TaskAssignment).where(
                TaskAssignment.task_id == task_id,
                TaskAssignment.status == "active",
            )
        )
        return result.scalar_one_or_none()

    async def get_worker_profile(self, actor_id: str) -> WorkerProfile | None:
        """Load a worker profile by actor id.

        Args:
            actor_id: Stable Workstream actor id.

        Returns:
            Worker profile when found; otherwise ``None``.
        """
        result = await self._session.execute(
            select(WorkerProfile).where(WorkerProfile.actor_id == actor_id)
        )
        return result.scalar_one_or_none()

    async def upsert_worker_profile(self, profile: WorkerProfile) -> WorkerProfile:
        """Create or update a worker profile from trusted actor claims.

        Args:
            profile: Worker profile carrying latest actor metadata.

        Returns:
            Persisted worker profile.
        """
        existing = await self.get_worker_profile(profile.actor_id)
        if existing is None:
            self._session.add(profile)
            await self._session.flush()
            await self._session.refresh(profile)
            return profile
        existing.external_subject = profile.external_subject
        existing.external_issuer = profile.external_issuer
        existing.display_name = profile.display_name
        existing.email = profile.email
        existing.skill_tags = profile.skill_tags
        await self._session.flush()
        await self._session.refresh(existing)
        return existing

    async def get_reviewer_profile(self, actor_id: str) -> ReviewerProfile | None:
        """Load a reviewer profile by actor id.

        Args:
            actor_id: Stable Workstream actor id.

        Returns:
            Reviewer profile when found; otherwise ``None``.
        """
        result = await self._session.execute(
            select(ReviewerProfile).where(ReviewerProfile.actor_id == actor_id)
        )
        return result.scalar_one_or_none()

    async def upsert_reviewer_profile(self, profile: ReviewerProfile) -> ReviewerProfile:
        """Create or update a reviewer profile from trusted actor claims.

        Args:
            profile: Reviewer profile carrying latest actor metadata.

        Returns:
            Persisted reviewer profile.
        """
        existing = await self.get_reviewer_profile(profile.actor_id)
        if existing is None:
            self._session.add(profile)
            await self._session.flush()
            await self._session.refresh(profile)
            return profile
        existing.external_subject = profile.external_subject
        existing.external_issuer = profile.external_issuer
        existing.display_name = profile.display_name
        existing.email = profile.email
        existing.skill_tags = profile.skill_tags
        await self._session.flush()
        await self._session.refresh(existing)
        return existing

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

    async def list_audit_events(self, entity_type: str, entity_id: str) -> Sequence[AuditEvent]:
        """List audit events for one entity in creation order.

        Args:
            entity_type: Entity type recorded in audit events.
            entity_id: Entity id recorded in audit events.

        Returns:
            Matching audit events ordered by creation time.
        """
        result = await self._session.execute(
            select(AuditEvent)
            .where(AuditEvent.entity_type == entity_type, AuditEvent.entity_id == entity_id)
            .order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc())
        )
        return result.scalars().all()
