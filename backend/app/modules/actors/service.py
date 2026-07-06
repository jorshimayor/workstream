"""Service layer for actor identity registration and profile eligibility."""

from __future__ import annotations

from collections.abc import Iterable
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_any_role
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
from app.modules.tasks.repository import TaskRepository
from app.schemas.auth import ActorContext

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
        self._audit_repo = TaskRepository(session)

    async def register_actor(self, actor: ActorContext) -> ActorIdentity:
        """Create or refresh identity and observed profiles for a verified actor.

        Args:
            actor: Trusted actor context returned by Flow token verification.

        Returns:
            Persisted actor identity.
        """
        identity = await self._repo.upsert_identity(self._identity_from_actor(actor))
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
            await self._repo.insert_profile_if_absent(
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
            existing.updated_at = func.now()
            return existing

        next_metadata = profile_metadata or existing.profile_metadata
        existing.updated_at = func.now()
        if existing.profile_metadata != next_metadata:
            previous_metadata = dict(existing.profile_metadata or {})
            existing.profile_metadata = next_metadata
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
    ) -> ActorProfileResponse:
        """Activate or refresh the current actor's worker profile.

        Args:
            actor: Trusted actor context.
            payload: Worker-owned profile fields.

        Returns:
            Profile response joined with trusted identity metadata.

        Raises:
            ActorProfileDisabled: If the worker profile has been disabled.
        """
        require_any_role(actor, {"worker"})
        identity = await self._repo.upsert_identity(self._identity_from_actor(actor))
        profile = await self._repo.get_profile(
            actor.actor_id,
            "worker",
            GLOBAL_PROFILE_SCOPE_TYPE,
            GLOBAL_PROFILE_SCOPE_ID,
        )
        if profile is None:
            await self._repo.insert_profile_if_absent(
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

    def _identity_from_actor(self, actor: ActorContext) -> ActorIdentity:
        """Build an identity model from trusted actor claims."""
        return ActorIdentity(
            actor_id=actor.actor_id,
            external_subject=actor.external_subject,
            external_issuer=actor.external_issuer,
            display_name=actor.display_name,
            email=actor.email,
            last_seen_roles=list(actor.roles),
            last_claim_snapshot=actor.claim_snapshot,
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
        raw_profiles = actor.claim_snapshot.get("workstream_relationship_profiles", [])
        if not isinstance(raw_profiles, list):
            return []
        profiles: list[dict] = []
        for raw_profile in raw_profiles:
            if not isinstance(raw_profile, dict):
                continue
            if raw_profile.get("profile_type") != "project_owner":
                continue
            scope_type = raw_profile.get("scope_type")
            scope_id = raw_profile.get("scope_id")
            if not isinstance(scope_type, str) or not isinstance(scope_id, str):
                continue
            scope_type = scope_type.strip()
            scope_id = scope_id.strip()
            if not scope_type or not scope_id:
                continue
            profiles.append(
                {
                    "profile_type": "project_owner",
                    "scope_type": scope_type,
                    "scope_id": scope_id,
                    "profile_metadata": {
                        "source": "trusted_relationship_claim",
                        **(
                            raw_profile.get("profile_metadata")
                            if isinstance(raw_profile.get("profile_metadata"), dict)
                            else {}
                        ),
                    },
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
