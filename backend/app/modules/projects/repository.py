"""Database access methods for project and project-guide records."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.models import (
    CheckerPolicy,
    PaymentPolicy,
    Project,
    ProjectGuide,
    RevisionPolicy,
    ReviewPolicy,
)


class ProjectRepositoryIntegrityError(RuntimeError):
    """Raised when persisted project data violates repository invariants."""


class ProjectRepository:
    """Wraps SQLAlchemy persistence for the project guide lifecycle."""

    def __init__(self, session: AsyncSession) -> None:
        """Create a repository bound to the current database session.

        Args:
            session: Async SQLAlchemy session for the current unit of work.
        """
        self._session = session

    async def add_project(self, project: Project) -> Project:
        """Persist a new project and refresh generated database fields.

        Args:
            project: Project model to add to the session.

        Returns:
            Persisted project model.
        """
        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def get_project(self, project_id: str) -> Project | None:
        """Load one project by primary key.

        Args:
            project_id: Project id to load.

        Returns:
            Project model when found; otherwise ``None``.
        """
        return await self._session.get(Project, project_id)

    async def add_guide(self, guide: ProjectGuide) -> ProjectGuide:
        """Persist a new project guide and refresh generated database fields.

        Args:
            guide: Project guide model to add to the session.

        Returns:
            Persisted project guide model.
        """
        self._session.add(guide)
        await self._session.flush()
        await self._session.refresh(guide)
        return guide

    async def get_guide(self, guide_id: str) -> ProjectGuide | None:
        """Load one project guide by primary key.

        Args:
            guide_id: Guide id to load.

        Returns:
            Project guide model when found; otherwise ``None``.
        """
        return await self._session.get(ProjectGuide, guide_id)

    async def get_active_guide(self, project_id: str) -> ProjectGuide | None:
        """Load the active guide for a project.

        Args:
            project_id: Project id whose active guide should be loaded.

        Returns:
            Active guide when present; otherwise ``None``.

        Raises:
            ProjectRepositoryIntegrityError: If more than one active guide is
                found for the project.
        """
        result = await self._session.execute(
            select(ProjectGuide).where(
                ProjectGuide.project_id == project_id,
                ProjectGuide.status == "active",
            )
        )
        active_guides = list(result.scalars().all())
        if not active_guides:
            return None
        if len(active_guides) > 1:
            raise ProjectRepositoryIntegrityError("multiple active guides found for project")
        return active_guides[0]

    async def list_active_guides(self, project_id: str) -> Sequence[ProjectGuide]:
        """List active guides for a project.

        Args:
            project_id: Project id whose active guides should be listed.

        Returns:
            Sequence of active guides, normally empty or one after DB constraints.
        """
        result = await self._session.execute(
            select(ProjectGuide).where(
                ProjectGuide.project_id == project_id,
                ProjectGuide.status == "active",
            )
        )
        return result.scalars().all()

    async def upsert_checker_policy(self, policy: CheckerPolicy) -> CheckerPolicy:
        """Create or replace a checker policy for one guide version.

        Args:
            policy: Checker policy model carrying the desired values.

        Returns:
            Persisted checker policy model.
        """
        existing = await self.get_checker_policy(policy.project_id, policy.guide_version)
        if existing is None:
            self._session.add(policy)
            await self._session.flush()
            await self._session.refresh(policy)
            return policy
        existing.required_checkers = policy.required_checkers
        existing.warning_checkers = policy.warning_checkers
        existing.blocking_severities = policy.blocking_severities
        await self._session.flush()
        await self._session.refresh(existing)
        return existing

    async def get_checker_policy(self, project_id: str, guide_version: str) -> CheckerPolicy | None:
        """Load a checker policy by project and guide version.

        Args:
            project_id: Project id that owns the policy.
            guide_version: Guide version the policy applies to.

        Returns:
            Checker policy when found; otherwise ``None``.
        """
        result = await self._session.execute(
            select(CheckerPolicy).where(
                CheckerPolicy.project_id == project_id,
                CheckerPolicy.guide_version == guide_version,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_review_policy(self, policy: ReviewPolicy) -> ReviewPolicy:
        """Create or replace a review policy for one guide version.

        Args:
            policy: Review policy model carrying the desired values.

        Returns:
            Persisted review policy model.
        """
        existing = await self.get_review_policy(policy.project_id, policy.guide_version)
        if existing is None:
            self._session.add(policy)
            await self._session.flush()
            await self._session.refresh(policy)
            return policy
        existing.requires_second_review = policy.requires_second_review
        existing.allowed_decisions = policy.allowed_decisions
        existing.minimum_finding_fields = policy.minimum_finding_fields
        existing.sla_hours = policy.sla_hours
        await self._session.flush()
        await self._session.refresh(existing)
        return existing

    async def get_review_policy(self, project_id: str, guide_version: str) -> ReviewPolicy | None:
        """Load a review policy by project and guide version.

        Args:
            project_id: Project id that owns the policy.
            guide_version: Guide version the policy applies to.

        Returns:
            Review policy when found; otherwise ``None``.
        """
        result = await self._session.execute(
            select(ReviewPolicy).where(
                ReviewPolicy.project_id == project_id,
                ReviewPolicy.guide_version == guide_version,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_revision_policy(self, policy: RevisionPolicy) -> RevisionPolicy:
        """Create or replace a revision policy for one guide version.

        Args:
            policy: Revision policy model carrying the desired values.

        Returns:
            Persisted revision policy model.
        """
        existing = await self.get_revision_policy(policy.project_id, policy.guide_version)
        if existing is None:
            self._session.add(policy)
            await self._session.flush()
            await self._session.refresh(policy)
            return policy
        existing.max_revision_rounds = policy.max_revision_rounds
        existing.revision_deadline_hours = policy.revision_deadline_hours
        existing.auto_reject_after_limit = policy.auto_reject_after_limit
        existing.allowed_resubmission_states = policy.allowed_resubmission_states
        existing.reviewer_reassignment_rule = policy.reviewer_reassignment_rule
        await self._session.flush()
        await self._session.refresh(existing)
        return existing

    async def get_revision_policy(
        self,
        project_id: str,
        guide_version: str,
    ) -> RevisionPolicy | None:
        """Load a revision policy by project and guide version.

        Args:
            project_id: Project id that owns the policy.
            guide_version: Guide version the policy applies to.

        Returns:
            Revision policy when found; otherwise ``None``.
        """
        result = await self._session.execute(
            select(RevisionPolicy).where(
                RevisionPolicy.project_id == project_id,
                RevisionPolicy.guide_version == guide_version,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_payment_policy(self, policy: PaymentPolicy) -> PaymentPolicy:
        """Create or replace a payment policy for one guide version.

        Args:
            policy: Payment policy model carrying the desired values.

        Returns:
            Persisted payment policy model.
        """
        existing = await self.get_payment_policy(policy.project_id, policy.guide_version)
        if existing is None:
            self._session.add(policy)
            await self._session.flush()
            await self._session.refresh(policy)
            return policy
        existing.base_amount = policy.base_amount
        existing.currency = policy.currency
        existing.payout_type = policy.payout_type
        existing.revision_payment_rule = policy.revision_payment_rule
        existing.rejection_payment_rule = policy.rejection_payment_rule
        existing.accepted_payment_rule = policy.accepted_payment_rule
        await self._session.flush()
        await self._session.refresh(existing)
        return existing

    async def get_payment_policy(self, project_id: str, guide_version: str) -> PaymentPolicy | None:
        """Load a payment policy by project and guide version.

        Args:
            project_id: Project id that owns the policy.
            guide_version: Guide version the policy applies to.

        Returns:
            Payment policy when found; otherwise ``None``.
        """
        result = await self._session.execute(
            select(PaymentPolicy).where(
                PaymentPolicy.project_id == project_id,
                PaymentPolicy.guide_version == guide_version,
            )
        )
        return result.scalar_one_or_none()
