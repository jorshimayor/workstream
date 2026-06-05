from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth import get_auth_verifier
from app.interfaces.auth import AuthVerificationError, AuthVerifier
from app.schemas.auth import ActorContext

bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_actor(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    verifier: Annotated[AuthVerifier, Depends(get_auth_verifier)],
) -> ActorContext:
    if credentials is None:
        raise unauthorized("Missing bearer token")

    try:
        return await verifier.verify(credentials.credentials)
    except AuthVerificationError as exc:
        raise unauthorized("Invalid bearer token") from exc
