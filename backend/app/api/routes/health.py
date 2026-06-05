"""Health-check route for the Workstream API."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return a lightweight API health response.

    Returns:
        Health response with an ``ok`` status.
    """
    return HealthResponse(status="ok")
