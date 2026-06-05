from __future__ import annotations

from typing import Protocol

from app.schemas.auth import ActorContext


class AuthVerificationError(Exception):
    """Raised when a bearer token cannot be verified."""


class AuthVerifier(Protocol):
    async def verify(self, token: str) -> ActorContext:
        """Verify a bearer token and return the trusted actor context."""
