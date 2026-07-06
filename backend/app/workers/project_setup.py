"""Celery tasks for automatic project guide setup."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

from celery.utils.log import get_task_logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.session import get_database_url
from app.modules.projects.service import ProjectService, ProjectServiceError
from app.schemas.auth import ActorContext
from app.workers.celery_app import celery_app

PROJECT_SETUP_PIPELINE_ACTOR_ID = "workstream-system:project-setup-pipeline"
PROJECT_SETUP_PIPELINE_TASK = "workstream.project_setup.run_pre_submit_setup_pipeline"

logger = get_task_logger(__name__)
T = TypeVar("T")


def project_setup_pipeline_actor() -> ActorContext:
    """Return the internal actor used for server-owned setup automation."""
    return ActorContext(
        actor_id=PROJECT_SETUP_PIPELINE_ACTOR_ID,
        external_subject=PROJECT_SETUP_PIPELINE_ACTOR_ID,
        external_issuer="workstream-internal",
        email=None,
        display_name="Workstream Project Setup Pipeline",
        roles=("admin", "project_manager"),
        claim_snapshot={"system_actor": True, "pipeline": "project_setup"},
        auth_source="workstream_system",
        is_dev_auth=False,
    )


@celery_app.task(name=PROJECT_SETUP_PIPELINE_TASK)
def run_pre_submit_setup_pipeline(
    project_id: str,
    guide_id: str,
    source_snapshot_id: str,
) -> dict[str, Any]:
    """Run guide sufficiency and policy derivation for a source snapshot.

    Args:
        project_id: Project that owns the guide.
        guide_id: Guide whose latest source snapshot should be processed.
        source_snapshot_id: Immutable source snapshot to analyze.

    Returns:
        Machine-readable terminal pipeline state.
    """
    return _run_async_task(
        lambda: _run_pre_submit_setup_pipeline(project_id, guide_id, source_snapshot_id)
    )


def _run_async_task(coro_factory: Callable[[], Awaitable[T]]) -> T:
    """Run an async task body from a synchronous Celery task boundary.

    Celery workers normally execute this with no running event loop. Eager test
    execution can happen inside an async API request, so that case runs the
    coroutine on a short-lived thread instead of nesting event loops.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro_factory())

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(lambda: asyncio.run(coro_factory())).result()


async def _run_pre_submit_setup_pipeline(
    project_id: str,
    guide_id: str,
    source_snapshot_id: str,
) -> dict[str, Any]:
    """Execute the project setup pipeline using async service contracts."""
    actor = project_setup_pipeline_actor()
    engine = create_async_engine(get_database_url(), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            service = ProjectService(session)
            try:
                sufficiency_report, _ = await service.run_guide_sufficiency_agent(
                    actor,
                    project_id,
                    guide_id,
                    source_snapshot_id,
                )
                if sufficiency_report.status == "blocked":
                    return {
                        "status": "sufficiency_blocked",
                        "guide_sufficiency_report_id": sufficiency_report.id,
                        "submission_artifact_policy_id": None,
                    }
                policy, _ = await service.run_submission_artifact_policy_derivation_agent(
                    actor,
                    project_id,
                    guide_id,
                    source_snapshot_id,
                )
                return {
                    "status": "policy_draft_ready",
                    "guide_sufficiency_report_id": sufficiency_report.id,
                    "submission_artifact_policy_id": policy.id,
                }
            except ProjectServiceError as exc:
                logger.warning(
                    "project setup pipeline stopped",
                    extra={
                        "project_id": project_id,
                        "guide_id": guide_id,
                        "source_snapshot_id": source_snapshot_id,
                        "error": str(exc),
                    },
                )
                return {
                    "status": "setup_blocked",
                    "error": str(exc),
                    "guide_sufficiency_report_id": None,
                    "submission_artifact_policy_id": None,
                }
    finally:
        await engine.dispose()
