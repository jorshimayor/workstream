"""Queue boundary for automatic post-submit checker gates."""

from __future__ import annotations

from typing import Any

from celery.exceptions import CeleryError
from kombu.exceptions import KombuError

from app.core.config import get_settings
from app.workers.errors import CeleryConfigurationError


class PreReviewGateQueueError(RuntimeError):
    """Raised when Workstream cannot enqueue the pre-review checker gate."""


def enqueue_pre_review_gate(
    *,
    checker_run_id: str,
    requester_provenance: dict[str, Any],
) -> str:
    """Enqueue automatic post-submit checker execution for one submission.

    Args:
        checker_run_id: Queued checker run claim to execute.
        requester_provenance: Minimal audit-safe requester provenance for the
            actor whose request caused the automatic gate.

    Returns:
        Celery task id.

    Raises:
        PreReviewGateQueueError: If the broker cannot accept the job, or eager
            local execution fails before the dispatch boundary returns.
    """
    settings = get_settings()
    try:
        from app.workers.checkers import run_pre_review_gate

        _sync_task_settings()
        result = run_pre_review_gate.apply_async(
            args=(checker_run_id, requester_provenance),
            task_id=f"pre-review-gate:{checker_run_id}",
        )
    except (CeleryConfigurationError, CeleryError, KombuError, OSError) as exc:
        raise PreReviewGateQueueError("pre-review gate could not be enqueued") from exc
    except Exception as exc:
        if settings.celery_task_always_eager:
            raise PreReviewGateQueueError("pre-review gate could not be enqueued") from exc
        raise
    return result.id


def _sync_task_settings() -> None:
    """Sync mutable Celery task settings from the current test/runtime config."""
    from app.workers.checkers import run_pre_review_gate

    settings = get_settings()
    if settings.celery_broker_url is not None:
        run_pre_review_gate.app.conf.broker_url = settings.celery_broker_url
    elif settings.celery_task_always_eager:
        run_pre_review_gate.app.conf.broker_url = "memory://"
    run_pre_review_gate.app.conf.result_backend = settings.celery_result_backend_url
    run_pre_review_gate.app.conf.task_always_eager = settings.celery_task_always_eager
    run_pre_review_gate.app.conf.task_eager_propagates = True
