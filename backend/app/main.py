"""FastAPI application factory for Workstream."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the Workstream FastAPI application.

    Args:
        settings: Optional settings override for tests or embedded use.

    Returns:
        Configured FastAPI application.
    """
    settings = settings or get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    app.include_router(api_router)
    return app


app = create_app()
