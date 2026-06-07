"""Task lifecycle constants and transition guards."""

from __future__ import annotations

TASK_STATUS_DRAFT = "draft"
TASK_STATUS_SCREENING = "screening"
TASK_STATUS_READY = "ready"
TASK_STATUS_CLAIMED = "claimed"
TASK_STATUS_IN_PROGRESS = "in_progress"

ALLOWED_CHUNK4_TRANSITIONS = {
    (TASK_STATUS_DRAFT, TASK_STATUS_SCREENING),
    (TASK_STATUS_SCREENING, TASK_STATUS_READY),
    (TASK_STATUS_READY, TASK_STATUS_CLAIMED),
    (TASK_STATUS_CLAIMED, TASK_STATUS_IN_PROGRESS),
}


class InvalidTaskTransition(ValueError):
    """Raised when a task lifecycle transition is not allowed."""


def ensure_allowed_transition(from_status: str, to_status: str) -> None:
    """Validate a task status transition implemented by Chunk 4.

    Args:
        from_status: Current task status.
        to_status: Desired next task status.

    Raises:
        InvalidTaskTransition: If the transition is not supported.
    """
    if (from_status, to_status) not in ALLOWED_CHUNK4_TRANSITIONS:
        raise InvalidTaskTransition(f"invalid task transition: {from_status} -> {to_status}")
