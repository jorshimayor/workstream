"""Database access methods for checker runs and checker results."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.checkers.models import CheckerRun


class CheckerRepository:
    """Wraps SQLAlchemy persistence for checker records."""

    def __init__(self, session: AsyncSession) -> None:
        """Create a repository bound to one database session.

        Args:
            session: Async SQLAlchemy session for the current unit of work.
        """
        self._session = session

    async def add_run(self, checker_run: CheckerRun) -> CheckerRun:
        """Persist a checker run and its result rows.

        Args:
            checker_run: Checker run model with result rows attached.

        Returns:
            Persisted checker run with generated database fields refreshed.
        """
        self._session.add(checker_run)
        await self._session.flush()
        await self._session.refresh(checker_run)
        return checker_run

    async def get_run(self, checker_run_id: str) -> CheckerRun | None:
        """Load one checker run with result rows.

        Args:
            checker_run_id: Checker run id to load.

        Returns:
            Checker run when found; otherwise ``None``.
        """
        result = await self._session.execute(
            select(CheckerRun)
            .options(selectinload(CheckerRun.results))
            .where(CheckerRun.id == checker_run_id)
        )
        return result.scalar_one_or_none()

    async def list_runs_for_submission(self, submission_id: str) -> Sequence[CheckerRun]:
        """List checker runs for one submission.

        Args:
            submission_id: Submission id whose checker runs should be listed.

        Returns:
            Checker runs ordered by attempt number.
        """
        result = await self._session.execute(
            select(CheckerRun)
            .options(selectinload(CheckerRun.results))
            .where(CheckerRun.submission_id == submission_id)
            .order_by(CheckerRun.attempt_number.asc())
        )
        return result.scalars().all()

    async def get_current_run_for_submission(self, submission_id: str) -> CheckerRun | None:
        """Load the current checker run for one submission.

        Args:
            submission_id: Submission id whose current checker run should be loaded.

        Returns:
            Current checker run when present; otherwise ``None``.
        """
        result = await self._session.execute(
            select(CheckerRun)
            .options(selectinload(CheckerRun.results))
            .where(
                CheckerRun.submission_id == submission_id,
                CheckerRun.is_current_for_submission.is_(True),
            )
        )
        return result.scalar_one_or_none()

