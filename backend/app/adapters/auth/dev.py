"""Development-only auth verifier for local and test environments."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.core.config import Settings
from app.interfaces.auth import AuthVerificationError
from app.schemas.auth import (
    AuthVerificationResult,
    LegacyAuthorizationCompatibilityContext,
    MAX_VERIFIED_IDENTITY_ANCHOR_CHARACTERS,
    VerifiedIssuerToken,
    actor_id_from_external_identity,
    normalize_legacy_roles,
)

DEVELOPMENT_ENVIRONMENTS = {"local", "dev", "development", "test"}


class DevelopmentAuthVerifier:
    """Local development verifier. It must never be enabled in production."""

    def __init__(self, settings: Settings) -> None:
        """Create a dev verifier from explicit local/test settings.

        Args:
            settings: Application settings containing development auth values.

        Raises:
            RuntimeError: If dev auth is enabled outside an allowed environment
                or required dev auth settings are missing.
        """
        if settings.environment.strip().lower() not in DEVELOPMENT_ENVIRONMENTS:
            raise RuntimeError("development auth cannot run in production")
        if not settings.dev_auth_token:
            raise RuntimeError("WORKSTREAM_DEV_AUTH_TOKEN must be set for development auth")
        if (
            not settings.dev_auth_subject
            or len(settings.dev_auth_subject) > MAX_VERIFIED_IDENTITY_ANCHOR_CHARACTERS
        ):
            raise RuntimeError("WORKSTREAM_DEV_AUTH_SUBJECT must be set for development auth")
        if (
            not settings.dev_auth_issuer
            or len(settings.dev_auth_issuer) > MAX_VERIFIED_IDENTITY_ANCHOR_CHARACTERS
        ):
            raise RuntimeError("WORKSTREAM_DEV_AUTH_ISSUER must be set for development auth")
        self._settings = settings

    async def verify(self, token: str) -> AuthVerificationResult:
        """Verify a local bearer token and return canonical and legacy views.

        Args:
            token: Bearer token from the incoming request.

        Returns:
            Verification result built from development settings.

        Raises:
            AuthVerificationError: If the token does not match the configured
                development token.
        """
        if token != self._settings.dev_auth_token:
            raise AuthVerificationError("invalid development auth token")

        roles = normalize_legacy_roles(self._settings.dev_auth_roles)
        now = int(datetime.now(UTC).timestamp())
        return AuthVerificationResult(
            token=VerifiedIssuerToken(
                issuer=self._settings.dev_auth_issuer,
                subject=self._settings.dev_auth_subject,
                audience=("workstream",),
                expires_at=now + int(timedelta(days=1).total_seconds()),
                issued_at=now,
                token_id=actor_id_from_external_identity("workstream-dev-token", token),
                subject_kind="human",
                scopes=frozenset({"workstream:access"}),
            ),
            legacy=LegacyAuthorizationCompatibilityContext(
                roles=roles,
                auth_source="dev_mock",
                is_dev_auth=True,
            ),
        )
