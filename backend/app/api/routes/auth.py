from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_actor
from app.schemas.auth import ActorContext, ActorResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=ActorResponse)
async def read_current_actor(
    actor: Annotated[ActorContext, Depends(get_current_actor)],
) -> ActorResponse:
    return ActorResponse.from_actor(actor)
