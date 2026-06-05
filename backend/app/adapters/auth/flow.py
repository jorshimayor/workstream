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
        self._issuer = settings.flow_auth_issuer

    async def verify(self, token: str) -> ActorContext:
        raise AuthVerificationError(
            f"Flow token verification is not configured for issuer {self._issuer}"
        )
