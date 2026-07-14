"""Unattached FastAPI dependencies for future protected mutations."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request, status

from app.api.deps.auth import get_auth_verification_result
from app.core.api_controls import StructuredHTTPException
from app.modules.api_controls.service import (
    ADMIN_MUTATION_SCOPE,
    FIRST_ACCESS_SCOPE,
    RateControlService,
    RateControlUnavailableError,
)
from app.schemas.auth import AuthVerificationResult


def get_rate_control_service() -> RateControlService:
    """Return a limiter whose consumption owns a dedicated database session."""
    return RateControlService()


def _unavailable() -> StructuredHTTPException:
    return StructuredHTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Service unavailable",
        error_code="service_unavailable",
        error_message="Service unavailable",
        retryable=True,
    )


async def _enforce(
    *,
    request: Request,
    result: AuthVerificationResult,
    service: RateControlService,
    control_scope: str,
    limit: int,
    window_seconds: int,
) -> None:
    try:
        decision = await service.consume(
            control_scope=control_scope,
            issuer=result.token.issuer,
            subject=result.token.subject,
            limit=limit,
            window_seconds=window_seconds,
            secret=request.app.state.settings.api_rate_limit_key_secret,
        )
    except RateControlUnavailableError as exc:
        raise _unavailable() from exc
    if not decision.allowed:
        raise StructuredHTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            error_code="rate_limit_exceeded",
            error_message="Rate limit exceeded",
            retryable=True,
            headers={"Retry-After": str(decision.retry_after)},
        )


async def enforce_first_access_rate_limit(
    request: Request,
    result: Annotated[AuthVerificationResult, Depends(get_auth_verification_result)],
    service: Annotated[RateControlService, Depends(get_rate_control_service)],
) -> None:
    """Consume the future first-access mutation allowance."""
    settings = request.app.state.settings
    await _enforce(
        request=request,
        result=result,
        service=service,
        control_scope=FIRST_ACCESS_SCOPE,
        limit=settings.api_first_access_rate_limit,
        window_seconds=settings.api_first_access_rate_window_seconds,
    )


async def enforce_admin_mutation_rate_limit(
    request: Request,
    result: Annotated[AuthVerificationResult, Depends(get_auth_verification_result)],
    service: Annotated[RateControlService, Depends(get_rate_control_service)],
) -> None:
    """Consume the future authority-management mutation allowance."""
    settings = request.app.state.settings
    await _enforce(
        request=request,
        result=result,
        service=service,
        control_scope=ADMIN_MUTATION_SCOPE,
        limit=settings.api_admin_mutation_rate_limit,
        window_seconds=settings.api_admin_mutation_rate_window_seconds,
    )
