"""Local demo route helpers for exercising local-only flows."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from app.core.config import Settings

DEMO_ENVIRONMENTS = {"local", "dev", "development", "test"}

router = APIRouter(prefix="/demo", tags=["demo"])


def ensure_demo_routes_enabled(settings: Settings) -> None:
    """Fail closed unless local demo routes are explicitly enabled.

    Args:
        settings: Runtime settings.

    Raises:
        HTTPException: If demo routes are disabled or used outside local/test.
    """
    if not settings.enable_demo_routes:
        raise HTTPException(status_code=404, detail="demo routes are disabled")
    if settings.environment.strip().lower() not in DEMO_ENVIRONMENTS:
        raise HTTPException(status_code=404, detail="demo routes are disabled")
