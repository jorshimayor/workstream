"""Authentication utility routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import (
    actor_registry_http_error,
    actor_registry_unavailable_error,
    get_canonical_actor,
    get_registered_actor,
)
from app.db.session import get_db_session
from app.modules.actors.schemas import ActorProfileSelfResponse, ActorProfileUpdateRequest
from app.modules.actors.service import ActorRegistryError, ActorService, ResolvedActor
from app.schemas.auth import ActorContext, ActorResponse

router = APIRouter(prefix="/auth", tags=["auth"])
actors_router = APIRouter(prefix="/actors", tags=["actors"])


@router.get("/me", response_model=ActorResponse)
async def read_current_actor(
    actor: Annotated[ActorContext, Depends(get_registered_actor)],
) -> ActorResponse:
    """Return the actor context derived from the current bearer token.

    Args:
        actor: Verified actor resolved by auth dependencies.

    Returns:
        Public actor response including audit context.
    """
    return ActorResponse.from_actor(actor)


@actors_router.get("/me", response_model=ActorProfileSelfResponse)
async def read_current_actor_profile(
    resolved: Annotated[ResolvedActor, Depends(get_canonical_actor)],
) -> ActorProfileSelfResponse:
    """Return the caller's canonical Contributor-domain profile."""
    try:
        return ActorService.self_response(resolved.profile)
    except ActorRegistryError as exc:
        raise actor_registry_http_error(exc) from exc


@actors_router.patch("/me", response_model=ActorProfileSelfResponse)
async def update_current_actor_profile(
    payload: ActorProfileUpdateRequest,
    resolved: Annotated[ResolvedActor, Depends(get_canonical_actor)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ActorProfileSelfResponse:
    """Update only the caller-owned canonical display fields."""
    try:
        return await ActorService(session).update_self(resolved, payload)
    except ActorRegistryError as exc:
        await session.rollback()
        raise actor_registry_http_error(exc) from exc
    except SQLAlchemyError as exc:
        await session.rollback()
        raise actor_registry_unavailable_error() from exc
