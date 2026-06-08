"""Local demo routes for exercising Week 1 flows from the frontend."""

from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_actor
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.modules.tasks.models import WorkerProfile
from app.modules.tasks.repository import TaskRepository
from app.schemas.auth import ActorContext

DEMO_ENVIRONMENTS = {"local", "dev", "development", "test"}

router = APIRouter(prefix="/demo", tags=["demo"])


class DemoWorkerProfileRequest(BaseModel):
    """Request schema for local demo worker profile activation."""

    skill_tags: list[str] = Field(default_factory=lambda: ["stem", "proofs"])


class DemoWorkerProfileResponse(BaseModel):
    """Response schema for a local demo worker profile."""

    id: str
    actor_id: str
    external_subject: str
    external_issuer: str
    display_name: str | None
    email: str | None
    skill_tags: list[str]
    status: str


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


@router.post("/worker-profile", response_model=DemoWorkerProfileResponse, status_code=201)
async def activate_demo_worker_profile(
    payload: DemoWorkerProfileRequest,
    actor: Annotated[ActorContext, Depends(get_current_actor)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DemoWorkerProfileResponse:
    """Create or update the current actor's local demo worker profile.

    Args:
        payload: Demo worker profile fields.
        actor: Current Flow-authenticated actor.
        session: Database session for the request.
        settings: Runtime settings.

    Returns:
        Persisted worker profile for the current actor.
    """
    ensure_demo_routes_enabled(settings)
    if "worker" not in actor.roles:
        raise HTTPException(status_code=403, detail="worker role required")

    profile = await TaskRepository(session).upsert_worker_profile(
        WorkerProfile(
            id=str(uuid4()),
            actor_id=actor.actor_id,
            external_subject=actor.external_subject,
            external_issuer=actor.external_issuer,
            display_name=actor.display_name,
            email=actor.email,
            skill_tags=payload.skill_tags,
            status="active",
        )
    )
    await session.commit()
    return DemoWorkerProfileResponse(
        id=profile.id,
        actor_id=profile.actor_id,
        external_subject=profile.external_subject,
        external_issuer=profile.external_issuer,
        display_name=profile.display_name,
        email=profile.email,
        skill_tags=profile.skill_tags,
        status=profile.status,
    )
