"""Queue boundary for automatic project setup jobs."""

from __future__ import annotations

from celery.exceptions import CeleryError
from kombu.exceptions import KombuError

from app.core.config import get_settings
from app.workers.errors import CeleryConfigurationError


class ProjectSetupQueueError(RuntimeError):
    """Raised when Workstream cannot enqueue project setup automation."""


def ensure_pre_submit_setup_pipeline_queue_ready() -> None:
    """Validate that the project setup queue can accept work.

    Raises:
        ProjectSetupQueueError: If the queue is not configured or reachable.
    """
    try:
        from app.workers.project_setup import run_pre_submit_setup_pipeline

        _sync_task_settings()
        settings = get_settings()
        if settings.celery_task_always_eager:
            return
        if settings.celery_broker_url is None:
            raise CeleryConfigurationError(
                "WORKSTREAM_CELERY_BROKER_URL must be set for project setup queue"
            )
        with run_pre_submit_setup_pipeline.app.connection_for_write() as connection:
            connection.ensure_connection(max_retries=0)
    except (CeleryConfigurationError, CeleryError, KombuError, OSError) as exc:
        raise ProjectSetupQueueError("project setup pipeline queue is unavailable") from exc


def enqueue_pre_submit_setup_pipeline(
    *,
    project_id: str,
    guide_id: str,
    source_snapshot_id: str,
) -> str:
    """Enqueue the Celery project setup pipeline.

    Args:
        project_id: Project that owns the guide.
        guide_id: Guide whose source snapshot should be processed.
        source_snapshot_id: Immutable source snapshot to analyze.

    Returns:
        Celery task id.

    Raises:
        ProjectSetupQueueError: If the broker cannot accept the job.
    """
    try:
        from app.workers.project_setup import run_pre_submit_setup_pipeline

        _sync_task_settings()
        result = run_pre_submit_setup_pipeline.apply_async(
            args=(project_id, guide_id, source_snapshot_id)
        )
    except (CeleryConfigurationError, CeleryError, KombuError, OSError) as exc:
        raise ProjectSetupQueueError("project setup pipeline could not be enqueued") from exc
    return result.id


def _sync_task_settings() -> None:
    """Sync mutable Celery task settings from the current test/runtime config."""
    from app.workers.project_setup import run_pre_submit_setup_pipeline

    settings = get_settings()
    if settings.celery_broker_url is not None:
        run_pre_submit_setup_pipeline.app.conf.broker_url = settings.celery_broker_url
    elif settings.celery_task_always_eager:
        run_pre_submit_setup_pipeline.app.conf.broker_url = "memory://"
    run_pre_submit_setup_pipeline.app.conf.result_backend = settings.celery_result_backend_url
    run_pre_submit_setup_pipeline.app.conf.task_always_eager = settings.celery_task_always_eager
    run_pre_submit_setup_pipeline.app.conf.task_eager_propagates = True
