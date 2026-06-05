from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from app.core.config import Settings
from app.interfaces.auth import AuthVerificationError
from app.schemas.auth import ActorContext

DEVELOPMENT_ENVIRONMENTS = {"local", "dev", "development", "test"}


def parse_roles(raw_roles: str) -> tuple[str, ...]:
    return tuple(role.strip() for role in raw_roles.split(",") if role.strip())


def actor_id_from_external_identity(external_issuer: str, external_subject: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{external_issuer}:{external_subject}"))


class DevelopmentAuthVerifier:
    """Local development verifier. It must never be enabled in production."""

    def __init__(self, settings: Settings) -> None:
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
