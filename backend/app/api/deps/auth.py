"""FastAPI dependencies for bearer-token actor resolution."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_auth_verifier
from app.db.session import get_db_session
from app.interfaces.auth import (
    AuthVerificationError,
    AuthVerificationUnavailableError,
    AuthVerifier,
)
from app.modules.actors.service import ActorRegistryError, ActorService
from app.schemas.auth import ActorContext, AuthVerificationResult, VerifiedIssuerToken

bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized(detail: str) -> HTTPException:
    """Build a bearer-auth unauthorized response.

    Args:
        detail: Public error detail to return to the client.

    Returns:
        HTTP exception with the bearer challenge header.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_auth_verification_result(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    verifier: Annotated[AuthVerifier, Depends(get_auth_verifier)],
) -> AuthVerificationResult:
    """Verify the request bearer token once for derived auth dependencies.

    Args:
        credentials: Parsed HTTP bearer credentials, when supplied.
        verifier: Configured auth verifier dependency.

    Returns:
        Canonical and bounded compatibility verification result.

    Raises:
        HTTPException: If the bearer token is missing or invalid.
    """
    if credentials is None:
        raise unauthorized("Missing bearer token")

    try:
        return await verifier.verify(credentials.credentials)
    except AuthVerificationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Identity verification unavailable",
        ) from exc
    except AuthVerificationError as exc:
        raise unauthorized("Invalid bearer token") from exc


async def get_current_actor(
    result: Annotated[AuthVerificationResult, Depends(get_auth_verification_result)],
) -> VerifiedIssuerToken:
    """Expose only canonical identity and coarse-access claims."""
    return result.token


async def get_registered_actor(
    result: Annotated[AuthVerificationResult, Depends(get_auth_verification_result)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ActorContext:
    """Resolve the current actor and refresh local registry metadata.

    Args:
        result: Verified token result from the pure auth boundary.
        session: Database session for registry persistence.

    Returns:
        The same verified actor context. Route authorization must still use
        this token-derived context, not persisted profile rows.
    """
    if result.token.subject_kind != "human" or result.legacy is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unsupported subject kind",
        )
    actor = result.legacy_actor()
    try:
        await ActorService(session).register_actor(actor)
    except ActorRegistryError as exc:
        await session.rollback()
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Actor registry unavailable",
        ) from exc
    return actor
