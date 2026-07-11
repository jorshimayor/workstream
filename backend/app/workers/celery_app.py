"""Celery application configuration for Workstream workers."""

from __future__ import annotations

from celery import Celery

from app.core.config import get_settings
from app.workers.errors import CeleryConfigurationError


def create_celery_app() -> Celery:
    """Create the Celery application from Workstream settings.

    Returns:
        Configured Celery application for durable background jobs.
    """
    settings = get_settings()
    broker_url = settings.celery_broker_url
    if broker_url is None:
        if settings.celery_task_always_eager:
            broker_url = "memory://"
        else:
            raise CeleryConfigurationError(
                "WORKSTREAM_CELERY_BROKER_URL must be set for Celery workers"
            )
    celery_app = Celery(
        "workstream",
        broker=broker_url,
        backend=settings.celery_result_backend_url,
        include=["app.workers.checkers", "app.workers.project_setup"],
    )
    celery_app.conf.update(
        accept_content=["json"],
        result_serializer="json",
        task_always_eager=settings.celery_task_always_eager,
        task_eager_propagates=True,
        task_ignore_result=True,
        task_serializer="json",
        timezone="UTC",
    )
    return celery_app


celery_app = create_celery_app()
