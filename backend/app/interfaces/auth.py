"""Auth interface contracts used by verifier adapters."""

from __future__ import annotations

from typing import Protocol

from app.schemas.auth import AuthVerificationResult


class AuthVerificationError(Exception):
    """Raised when a bearer token cannot be verified."""


class AuthVerificationUnavailableError(AuthVerificationError):
    """Raised when trusted verification infrastructure is unavailable."""


class AuthVerifier(Protocol):
    """Protocol implemented by external auth verifier adapters."""

    async def verify(self, token: str) -> AuthVerificationResult:
        """Verify a bearer token and return canonical and compatibility views."""
