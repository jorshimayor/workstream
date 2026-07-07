"""Service layer for actor identity registration and profile eligibility."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.permissions import require_any_role
from app.modules.audit.repository import AuditRepository
from app.modules.actors.models import (
    ACTOR_PROFILE_TYPES,
    GLOBAL_PROFILE_SCOPE_ID,
    GLOBAL_PROFILE_SCOPE_TYPE,
    ActorIdentity,
    ActorProfile,
)
from app.modules.actors.repository import ActorRepository
from app.modules.actors.schemas import ActorProfileActivationRequest, ActorProfileResponse
from app.modules.tasks.models import AuditEvent
from app.schemas.auth import ActorContext, normalized_relationship_profile_claims, sanitized_claim_snapshot

TOKEN_OBSERVED_PROFILE_TYPES = {"worker", "reviewer", "admin", "project_manager"}


class ActorRegistryError(Exception):
    """Base error for actor registry failures."""

    status_code = 400


class ActorProfileDisabled(ActorRegistryError):
    """Raised when an explicit profile workflow tries to use a disabled profile."""

    status_code = 403


class ActorService:
    """Coordinates actor identity and profile registry rules."""

    def __init__(self, session: AsyncSession) -> None:
        """Create a service instance bound to one database session.

        Args:
            session: Async SQLAlchemy session for the current request.
        """
        self._session = session
        self._repo = ActorRepository(session)
        self._audit_repo = AuditRepository(session)

    async def register_actor(self, actor: ActorContext) -> ActorIdentity:
        """Create or refresh identity and observed profiles for a verified actor.

        Args:
            actor: Trusted actor context returned by Flow token verification.

        Returns:
            Persisted actor identity.
        """
        incoming_identity = self._identity_from_actor(actor)
        existing_identity = await self._repo.get_identity(actor.actor_id, populate_existing=True)
        if await self._can_skip_registry_refresh(actor, incoming_identity, existing_identity):
            if existing_identity is None:
                raise RuntimeError("actor registry freshness check returned an empty identity")
            return existing_identity

        identity = await self._repo.upsert_identity(incoming_identity)
        for profile_type in self._observed_profile_types(actor.roles):
            await self.ensure_observed_profile(
                actor,
                profile_type=profile_type,
                scope_type=GLOBAL_PROFILE_SCOPE_TYPE,
                scope_id=GLOBAL_PROFILE_SCOPE_ID,
                profile_metadata={"source": "verified_token_role"},
                identity_already_refreshed=True,
            )
        for relationship in self._trusted_relationship_profiles(actor):
            await self.ensure_observed_profile(
                actor,
                profile_type=relationship["profile_type"],
                scope_type=relationship["scope_type"],
                scope_id=relationship["scope_id"],
                profile_metadata=relationship["profile_metadata"],
                identity_already_refreshed=True,
            )
        await self._session.commit()
        await self._session.refresh(identity)
        return identity

    async def ensure_observed_profile(
        self,
        actor: ActorContext,
        *,
        profile_type: str,
        scope_type: str,
        scope_id: str,
        profile_metadata: dict | None = None,
        identity_already_refreshed: bool = False,
    ) -> ActorProfile:
        """Create or refresh an observed profile without changing eligibility.

        Args:
            actor: Trusted actor context.
            profile_type: Profile type to observe.
            scope_type: Profile scope namespace.
            scope_id: Profile scope identifier.
            profile_metadata: Non-authoritative metadata to store.
            identity_already_refreshed: Whether the caller already refreshed
                the trusted identity in the current request.

        Returns:
            Persisted actor profile.
        """
        self._validate_profile_type(profile_type)
        if not identity_already_refreshed:
            await self._repo.upsert_identity(self._identity_from_actor(actor))
        existing = await self._repo.get_profile(actor.actor_id, profile_type, scope_type, scope_id)
        if existing is None:
            inserted = await self._repo.insert_profile_if_absent(
                ActorProfile(
                    id=str(uuid4()),
                    actor_id=actor.actor_id,
                    profile_type=profile_type,
                    status="observed",
                    skill_tags=[],
                    scope_type=scope_type,
                    scope_id=scope_id,
                    profile_metadata=profile_metadata or {},
                )
            )
            profile = await self._repo.get_profile(actor.actor_id, profile_type, scope_type, scope_id)
            if profile is None:
                raise RuntimeError("actor profile insert did not return a persisted row")
            if inserted:
                await self._write_profile_audit(
                    actor,
                    profile,
                    event_type="actor_profile_observed",
                    from_status=None,
                    to_status=profile.status,
                    event_payload={"profile_metadata": profile.profile_metadata},
                )
            return profile

        if existing.status != "observed":
            return existing

        next_metadata = existing.profile_metadata if profile_metadata is None else profile_metadata
        if existing.profile_metadata == next_metadata:
            return existing

        previous_metadata = dict(existing.profile_metadata or {})
        existing.profile_metadata = next_metadata
        existing.updated_at = func.now()
        await self._write_profile_audit(
            actor,
            existing,
            event_type="actor_profile_observation_refreshed",
            from_status=existing.status,
            to_status=existing.status,
            event_payload={
                "previous_profile_metadata": previous_metadata,
                "profile_metadata": existing.profile_metadata,
            },
        )
        return existing

    async def activate_worker_profile(
        self,
        actor: ActorContext,
        payload: ActorProfileActivationRequest,
        *,
        identity_already_refreshed: bool = False,
    ) -> ActorProfileResponse:
        """Activate or refresh the current actor's worker profile.

        Args:
            actor: Trusted actor context.
            payload: Worker-owned profile fields.
            identity_already_refreshed: Whether the request dependency already
                refreshed the identity row.

        Returns:
            Profile response joined with trusted identity metadata.

        Raises:
            ActorProfileDisabled: If the worker profile has been disabled.
        """
        require_any_role(actor, {"worker"})
        identity = await self._identity_for_profile_mutation(
            actor,
            identity_already_refreshed=identity_already_refreshed,
        )
        profile = await self._repo.get_profile(
            actor.actor_id,
            "worker",
            GLOBAL_PROFILE_SCOPE_TYPE,
            GLOBAL_PROFILE_SCOPE_ID,
        )
        if profile is None:
            inserted = await self._repo.insert_profile_if_absent(
                ActorProfile(
                    id=str(uuid4()),
                    actor_id=actor.actor_id,
                    profile_type="worker",
                    status="active",
                    skill_tags=payload.skill_tags,
                    scope_type=GLOBAL_PROFILE_SCOPE_TYPE,
                    scope_id=GLOBAL_PROFILE_SCOPE_ID,
                    profile_metadata={"source": "worker_profile_api"},
                )
            )
            profile = await self._repo.get_profile(
                actor.actor_id,
                "worker",
                GLOBAL_PROFILE_SCOPE_TYPE,
                GLOBAL_PROFILE_SCOPE_ID,
            )
            if profile is None:
                raise RuntimeError("worker actor profile insert did not return a persisted row")
            if inserted:
                await self._write_profile_audit(
                    actor,
                    profile,
                    event_type="actor_profile_activated",
                    from_status=None,
                    to_status="active",
                    event_payload={"skill_tags": profile.skill_tags},
                )
        else:
            if profile.status == "disabled":
                raise ActorProfileDisabled("worker profile is disabled")
            from_status = profile.status
            previous_tags = list(profile.skill_tags)
            profile.status = "active"
            profile.skill_tags = payload.skill_tags
            profile.profile_metadata = {
                **(profile.profile_metadata or {}),
                "source": "worker_profile_api",
            }
            if from_status != profile.status or previous_tags != profile.skill_tags:
                await self._write_profile_audit(
                    actor,
                    profile,
                    event_type="actor_profile_activated",
                    from_status=from_status,
                    to_status=profile.status,
                    event_payload={
                        "previous_skill_tags": previous_tags,
                        "skill_tags": profile.skill_tags,
                    },
                )
        await self._session.commit()
        await self._session.refresh(identity)
        await self._session.refresh(profile)
        return self._profile_response(profile, identity)

    async def get_active_profile(self, actor_id: str, profile_type: str) -> ActorProfile | None:
        """Load an active global profile when workflow eligibility requires it.

        Args:
            actor_id: Stable actor id.
            profile_type: Profile type required by the workflow.

        Returns:
            Active profile when present; otherwise ``None``.
        """
        profile = await self._repo.get_profile(
            actor_id,
            profile_type,
            GLOBAL_PROFILE_SCOPE_TYPE,
            GLOBAL_PROFILE_SCOPE_ID,
        )
        if profile is None or profile.status != "active":
            return None
        return profile

    async def _can_skip_registry_refresh(
        self,
        actor: ActorContext,
        incoming_identity: ActorIdentity,
        existing_identity: ActorIdentity | None,
    ) -> bool:
        """Return whether actor registry persistence can be skipped safely."""
        if existing_identity is None:
            return False
        interval_seconds = get_settings().actor_registry_refresh_interval_seconds
        if interval_seconds <= 0:
            return False
        if not self._identity_claims_match(existing_identity, incoming_identity):
            return False
        if not self._identity_seen_recently(existing_identity.last_seen_at, interval_seconds):
            return False
        required_profiles = [
            {
                "profile_type": profile_type,
                "scope_type": GLOBAL_PROFILE_SCOPE_TYPE,
                "scope_id": GLOBAL_PROFILE_SCOPE_ID,
                "profile_metadata": {"source": "verified_token_role"},
            }
            for profile_type in self._observed_profile_types(actor.roles)
        ]
        required_profiles.extend(self._trusted_relationship_profiles(actor))
        if not required_profiles:
            return True

        existing_profiles = {
            (profile.profile_type, profile.scope_type, profile.scope_id): profile
            for profile in await self._repo.list_profiles(actor.actor_id)
        }
        for required_profile in required_profiles:
            profile = existing_profiles.get(
                (
                    required_profile["profile_type"],
                    required_profile["scope_type"],
                    required_profile["scope_id"],
                )
            )
            if profile is None:
                return False
            if (
                profile.status == "observed"
                and profile.profile_metadata != required_profile.get("profile_metadata")
            ):
                return False
        return True

    def _identity_claims_match(
        self,
        existing_identity: ActorIdentity,
        incoming_identity: ActorIdentity,
    ) -> bool:
        """Return whether stored identity fields match the trusted actor claims."""
        return (
            existing_identity.external_subject == incoming_identity.external_subject
            and existing_identity.external_issuer == incoming_identity.external_issuer
            and existing_identity.display_name == incoming_identity.display_name
            and existing_identity.email == incoming_identity.email
            and existing_identity.last_seen_roles == incoming_identity.last_seen_roles
            and existing_identity.last_claim_snapshot == incoming_identity.last_claim_snapshot
            and existing_identity.auth_source == incoming_identity.auth_source
            and existing_identity.is_dev_auth == incoming_identity.is_dev_auth
        )

    def _identity_seen_recently(
        self,
        last_seen_at: datetime | None,
        interval_seconds: int,
    ) -> bool:
        """Return whether an identity row is still within the refresh window."""
        if last_seen_at is None:
            return False
        comparable_last_seen = last_seen_at
        if comparable_last_seen.tzinfo is None:
            comparable_last_seen = comparable_last_seen.replace(tzinfo=UTC)
        return datetime.now(UTC) - comparable_last_seen <= timedelta(seconds=interval_seconds)

    async def _identity_for_profile_mutation(
        self,
        actor: ActorContext,
        *,
        identity_already_refreshed: bool,
    ) -> ActorIdentity:
        """Return the current identity row for a profile mutation."""
        if not identity_already_refreshed:
            return await self._repo.upsert_identity(self._identity_from_actor(actor))

        identity = await self._repo.get_identity(actor.actor_id, populate_existing=True)
        if identity is not None:
            return identity
        return await self._repo.upsert_identity(self._identity_from_actor(actor))

    def _identity_from_actor(self, actor: ActorContext) -> ActorIdentity:
        """Build an identity model from trusted actor claims."""
        return ActorIdentity(
            actor_id=actor.actor_id,
            external_subject=actor.external_subject,
            external_issuer=actor.external_issuer,
            display_name=actor.display_name,
            email=actor.email,
            last_seen_roles=list(actor.roles),
            last_claim_snapshot=sanitized_claim_snapshot(actor.claim_snapshot),
            auth_source=actor.auth_source,
            is_dev_auth=actor.is_dev_auth,
        )

    def _profile_response(
        self,
        profile: ActorProfile,
        identity: ActorIdentity,
    ) -> ActorProfileResponse:
        """Build a profile response from profile and identity rows."""
        return ActorProfileResponse(
            id=profile.id,
            actor_id=profile.actor_id,
            profile_type=profile.profile_type,
            status=profile.status,
            skill_tags=profile.skill_tags,
            scope_type=profile.scope_type,
            scope_id=profile.scope_id,
            profile_metadata=profile.profile_metadata,
            external_subject=identity.external_subject,
            external_issuer=identity.external_issuer,
            display_name=identity.display_name,
            email=identity.email,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    def _observed_profile_types(self, roles: Iterable[str]) -> list[str]:
        """Return profile types that may be observed from verified token roles."""
        profile_types: list[str] = []
        for role in roles:
            if role in TOKEN_OBSERVED_PROFILE_TYPES and role not in profile_types:
                profile_types.append(role)
        return profile_types

    def _trusted_relationship_profiles(self, actor: ActorContext) -> list[dict]:
        """Extract trusted scoped relationship profiles from actor claims.

        Returns:
            Sanitized project-owner relationship profile claims.
        """
        profiles: list[dict] = []
        for raw_profile in normalized_relationship_profile_claims(actor.claim_snapshot):
            profiles.append(
                {
                    "profile_type": raw_profile["profile_type"],
                    "scope_type": raw_profile["scope_type"],
                    "scope_id": raw_profile["scope_id"],
                    "profile_metadata": {"source": "trusted_relationship_claim"},
                }
            )
        return profiles

    def _validate_profile_type(self, profile_type: str) -> None:
        """Validate profile type before persistence."""
        if profile_type not in ACTOR_PROFILE_TYPES:
            raise ValueError(f"unsupported actor profile type: {profile_type}")

    async def _write_profile_audit(
        self,
        actor: ActorContext,
        profile: ActorProfile,
        *,
        event_type: str,
        from_status: str | None,
        to_status: str | None,
        event_payload: dict,
    ) -> None:
        """Write audit evidence for profile eligibility changes."""
        audit = actor.audit_context()
        await self._audit_repo.add_audit_event(
            AuditEvent(
                id=str(uuid4()),
                entity_type="actor_profile",
                entity_id=profile.id,
                event_type=event_type,
                from_status=from_status,
                to_status=to_status,
                actor_id=audit.actor_id,
                external_subject=audit.external_subject,
                external_issuer=audit.external_issuer,
                actor_roles=list(audit.actor_roles),
                claim_snapshot=audit.claim_snapshot,
                auth_source=audit.auth_source,
                is_dev_auth=audit.is_dev_auth,
                reason=None,
                event_payload={
                    "actor_id": profile.actor_id,
                    "profile_type": profile.profile_type,
                    "scope_type": profile.scope_type,
                    "scope_id": profile.scope_id,
                    **event_payload,
                },
            )
        )
