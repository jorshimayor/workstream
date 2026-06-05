"""Development-only auth verifier for local and test environments."""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from app.core.config import Settings
from app.interfaces.auth import AuthVerificationError
from app.schemas.auth import ActorContext

DEVELOPMENT_ENVIRONMENTS = {"local", "dev", "development", "test"}


def parse_roles(raw_roles: str) -> tuple[str, ...]:
    """Parse comma-separated role settings into normalized role names.

    Args:
        raw_roles: Comma-separated role string from configuration.

    Returns:
        Tuple of non-empty role names.
    """
    return tuple(role.strip() for role in raw_roles.split(",") if role.strip())


def actor_id_from_external_identity(external_issuer: str, external_subject: str) -> str:
    """Build a stable internal actor id from external identity claims.

    Args:
        external_issuer: Issuer that provided the external subject.
        external_subject: Subject claim from the external identity provider.

    Returns:
        Deterministic actor id for the issuer and subject pair.
    """
    return str(uuid5(NAMESPACE_URL, f"{external_issuer}:{external_subject}"))


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
        if not settings.dev_auth_subject:
            raise RuntimeError("WORKSTREAM_DEV_AUTH_SUBJECT must be set for development auth")
        if not settings.dev_auth_issuer:
            raise RuntimeError("WORKSTREAM_DEV_AUTH_ISSUER must be set for development auth")
        self._settings = settings

    async def verify(self, token: str) -> ActorContext:
        """Verify a local bearer token and return the configured actor.

        Args:
            token: Bearer token from the incoming request.

        Returns:
            Actor context built from development settings.

        Raises:
            AuthVerificationError: If the token does not match the configured
                development token.
        """
        if token != self._settings.dev_auth_token:
            raise AuthVerificationError("invalid development auth token")

        roles = parse_roles(self._settings.dev_auth_roles)
        actor_id = actor_id_from_external_identity(
            self._settings.dev_auth_issuer,
            self._settings.dev_auth_subject,
        )
        claim_snapshot = {
            "roles": roles,
            "claim_source": "workstream_dev_settings",
        }

        return ActorContext(
            actor_id=actor_id,
            external_subject=self._settings.dev_auth_subject,
            external_issuer=self._settings.dev_auth_issuer,
            email=self._settings.dev_auth_email,
            display_name=self._settings.dev_auth_display_name,
            roles=roles,
            claim_snapshot=claim_snapshot,
            auth_source="dev_mock",
            is_dev_auth=True,
        )
