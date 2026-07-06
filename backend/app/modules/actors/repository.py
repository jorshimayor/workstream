"""Database access methods for actor identities and profiles."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.actors.models import ActorIdentity, ActorProfile


class ActorRepository:
    """Wraps SQLAlchemy persistence for actor registry operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Create a repository bound to one database session.

        Args:
            session: Async SQLAlchemy session for the current unit of work.
        """
        self._session = session

    async def get_identity(self, actor_id: str) -> ActorIdentity | None:
        """Load an actor identity by stable Workstream actor id.

        Args:
            actor_id: Stable actor id.

        Returns:
            Actor identity when present; otherwise ``None``.
        """
        return await self._session.get(ActorIdentity, actor_id)

    async def upsert_identity(self, identity: ActorIdentity) -> ActorIdentity:
        """Create or refresh an actor identity from trusted token claims.

        Args:
            identity: Actor identity carrying the latest trusted claim snapshot.

        Returns:
            Persisted actor identity.
        """
        await self._session.execute(
            insert(ActorIdentity)
            .values(
                actor_id=identity.actor_id,
                external_subject=identity.external_subject,
                external_issuer=identity.external_issuer,
                display_name=identity.display_name,
                email=identity.email,
                last_seen_roles=identity.last_seen_roles,
                last_claim_snapshot=identity.last_claim_snapshot,
                auth_source=identity.auth_source,
                is_dev_auth=identity.is_dev_auth,
            )
            .on_conflict_do_update(
                index_elements=[ActorIdentity.actor_id],
                set_={
                    "external_subject": identity.external_subject,
                    "external_issuer": identity.external_issuer,
                    "display_name": identity.display_name,
                    "email": identity.email,
                    "last_seen_roles": identity.last_seen_roles,
                    "last_claim_snapshot": identity.last_claim_snapshot,
                    "auth_source": identity.auth_source,
                    "is_dev_auth": identity.is_dev_auth,
                    "last_seen_at": func.now(),
                    "updated_at": func.now(),
                },
            )
        )
        await self._session.flush()
        persisted = await self.get_identity(identity.actor_id)
        if persisted is None:
            raise RuntimeError("actor identity upsert did not return a persisted row")
        return persisted

    async def get_profile(
        self,
        actor_id: str,
        profile_type: str,
        scope_type: str,
        scope_id: str,
    ) -> ActorProfile | None:
        """Load one actor profile by actor, type, and scope.

        Args:
            actor_id: Stable actor id.
            profile_type: Profile type such as ``worker`` or ``project_manager``.
            scope_type: Scope namespace, usually ``global``.
            scope_id: Scope identifier, usually ``global``.

        Returns:
            Actor profile when present; otherwise ``None``.
        """
        result = await self._session.execute(
            select(ActorProfile)
            .where(
                ActorProfile.actor_id == actor_id,
                ActorProfile.profile_type == profile_type,
                ActorProfile.scope_type == scope_type,
                ActorProfile.scope_id == scope_id,
            )
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    async def list_profiles(self, actor_id: str) -> Sequence[ActorProfile]:
        """List profiles for one actor.

        Args:
            actor_id: Stable actor id.

        Returns:
            Actor profiles ordered by type and scope.
        """
        result = await self._session.execute(
            select(ActorProfile)
            .where(ActorProfile.actor_id == actor_id)
            .order_by(ActorProfile.profile_type.asc(), ActorProfile.scope_type.asc())
        )
        return result.scalars().all()

    async def insert_profile_if_absent(self, profile: ActorProfile) -> None:
        """Insert a profile without overwriting existing scoped profile state.

        Args:
            profile: Actor profile to insert when absent.
        """
        await self._session.execute(
            insert(ActorProfile)
            .values(
                id=profile.id,
                actor_id=profile.actor_id,
                profile_type=profile.profile_type,
                status=profile.status,
                skill_tags=profile.skill_tags,
                scope_type=profile.scope_type,
                scope_id=profile.scope_id,
                profile_metadata=profile.profile_metadata,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    ActorProfile.actor_id,
                    ActorProfile.profile_type,
                    ActorProfile.scope_type,
                    ActorProfile.scope_id,
                ]
            )
        )
        await self._session.flush()

