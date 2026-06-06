"""Flow auth verifier boundary for external authentication tokens."""

from __future__ import annotations

from app.core.config import Settings
from app.interfaces.auth import AuthVerificationError
from app.schemas.auth import ActorContext


class FlowAuthVerifier:
    """Production Flow token verifier boundary.

    Chunk 2 defines the adapter boundary without adding network verification. The
    concrete Flow verification client is added when Flow auth details are wired.
    """

    def __init__(self, settings: Settings) -> None:
        """Create the Flow verifier boundary from application settings.

        Args:
            settings: Application settings containing Flow auth configuration.
        """
        self._issuer = settings.flow_auth_issuer

    async def verify(self, token: str) -> ActorContext:
        """Verify a Flow bearer token.

        Args:
            token: Bearer token from the incoming request.

        Raises:
            AuthVerificationError: Always raised until Flow verification is
                configured in a later chunk.
        """
        raise AuthVerificationError(
            f"Flow token verification is not configured for issuer {self._issuer}"
        )
