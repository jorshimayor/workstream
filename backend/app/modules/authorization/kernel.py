"""Deny-by-default request-scoped authorization kernel."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.schemas import (
    ActorReferenceKind,
    AuthorityAuditEventInput,
    AuthorityEventType,
)
from app.modules.audit.service import AuditService
from app.modules.authorization.catalogue import (
    ACTION_BY_ID,
    ActionAvailability,
    ActionId,
)
from app.modules.authorization.runtime import (
    ActorKind,
    ActorSelfResourceContext,
    ActorStatus,
    AuthorizationContext,
    AuthorizationDecision,
    AuthorizationDenied,
    AuthorizationDenialCode,
    AuthorizationResourceContext,
    IdentityLinkStatus,
    MatchedAuthorityKind,
)

ContextRevalidator = Callable[
    [AuthorizationContext, ActorSelfResourceContext], Awaitable[AuthorizationContext]
]


class AuthorizationService:
    """Evaluate one request against closed action definitions and stage evidence."""

    def __init__(
        self,
        session: AsyncSession,
        context: AuthorizationContext,
        *,
        revalidate_actor_self: ContextRevalidator | None = None,
    ) -> None:
        self._audit = AuditService(session)
        self._context = context
        self._revalidate_actor_self = revalidate_actor_self
        self._pending_denial: AuthorizationDecision | None = None

    async def require(
        self,
        action_id: ActionId,
        resource_context: AuthorizationResourceContext,
    ) -> AuthorizationDecision:
        """Return an allowed decision or raise one bounded, evidenced denial."""
        self._pending_denial = None
        action = ACTION_BY_ID.get(action_id) if isinstance(action_id, ActionId) else None
        context = self._context
        revalidated = False
        if (
            action is not None
            and action.action_id is ActionId.ACTOR_PROFILE_UPDATE_SELF
            and isinstance(resource_context, ActorSelfResourceContext)
            and self._revalidate_actor_self is not None
        ):
            context = await self._revalidate_actor_self(context, resource_context)
            revalidated = True

        denial = self._denial(action_id, action, resource_context, context, revalidated)
        decision = AuthorizationDecision(
            decision_id=uuid4(),
            action_id=action.action_id if action is not None else None,
            permission_id=action.permission_id if action is not None else None,
            allowed=denial is None,
            denial_code=denial,
            resource_type=resource_context.resource_type,
            resource_id=resource_context.resource_id,
            matched_authority_kind=MatchedAuthorityKind.ACTOR_SELF if denial is None else None,
            revalidated=revalidated,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
        )
        await self._stage_decision(decision, context.actor_profile_id)
        if not decision.allowed:
            self._pending_denial = decision
            raise AuthorizationDenied(decision)
        return decision

    async def _restage_denial(self, decision: AuthorizationDecision) -> None:
        """Restage the exact pending denial after composition-root rollback."""
        if (
            decision.allowed
            or decision is not self._pending_denial
            or decision.request_id != self._context.request_id
            or decision.correlation_id != self._context.correlation_id
        ):
            raise TypeError("invalid authorization denial evidence")
        await self._stage_decision(decision, self._context.actor_profile_id)
        self._pending_denial = None

    @staticmethod
    def _denial(
        requested_action: object,
        action,
        resource: AuthorizationResourceContext,
        context: AuthorizationContext,
        revalidated: bool,
    ) -> AuthorizationDenialCode | None:
        """Apply the closed lifecycle, availability, guard, and candidate order."""
        if context.identity_link_status is IdentityLinkStatus.REVOKED:
            return AuthorizationDenialCode.IDENTITY_LINK_REVOKED
        if context.actor_status is ActorStatus.DEACTIVATED:
            return AuthorizationDenialCode.ACTOR_DEACTIVATED
        if (
            requested_action is ActionId.ACTOR_PROFILE_UPDATE_SELF
            and context.actor_status is ActorStatus.SUSPENDED
        ):
            return AuthorizationDenialCode.ACTOR_SUSPENDED
        if action is None:
            return AuthorizationDenialCode.UNKNOWN_ACTION
        if action.availability is not ActionAvailability.ACTIVE:
            return AuthorizationDenialCode.ACTION_UNAVAILABLE
        if action.action_id not in {
            ActionId.ACTOR_PROFILE_READ_SELF,
            ActionId.ACTOR_PROFILE_UPDATE_SELF,
        }:
            return AuthorizationDenialCode.ACTION_UNAVAILABLE
        if not isinstance(resource, ActorSelfResourceContext):
            return AuthorizationDenialCode.RESOURCE_GUARD_DENIED
        if resource.resource_id != context.actor_profile_id:
            return AuthorizationDenialCode.RESOURCE_GUARD_DENIED
        if action.action_id is ActionId.ACTOR_PROFILE_READ_SELF and resource.requested_fields:
            return AuthorizationDenialCode.RESOURCE_GUARD_DENIED
        if action.action_id is ActionId.ACTOR_PROFILE_UPDATE_SELF and not resource.requested_fields:
            return AuthorizationDenialCode.RESOURCE_GUARD_DENIED
        if context.actor_kind is not ActorKind.HUMAN:
            return AuthorizationDenialCode.PERMISSION_NOT_GRANTED
        if action.action_id is ActionId.ACTOR_PROFILE_UPDATE_SELF and not revalidated:
            return AuthorizationDenialCode.RESOURCE_GUARD_DENIED
        return None

    async def _stage_decision(
        self,
        decision: AuthorizationDecision,
        actor_profile_id,
    ) -> None:
        """Write one privacy-bounded event without taking transaction ownership."""
        if decision.action_id is None or decision.permission_id is None:
            return
        denial_code = decision.denial_code
        stored_denial = None
        if denial_code in {
            AuthorizationDenialCode.UNKNOWN_ACTION,
            AuthorizationDenialCode.ACTION_UNAVAILABLE,
        }:
            stored_denial = AuthorizationDenialCode.PERMISSION_NOT_GRANTED.value
        elif denial_code is not None:
            stored_denial = denial_code.value
        target_is_actor = decision.resource_type == "actor_profile"
        await self._audit.add_authority_event(
            AuthorityAuditEventInput(
                event_id=decision.decision_id,
                event_type=(
                    AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED
                    if decision.allowed
                    else AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED
                ),
                entity_type="authorization_decision",
                entity_id=str(decision.decision_id),
                actor_ref_kind=ActorReferenceKind.ACTOR_PROFILE,
                actor_ref=str(actor_profile_id),
                request_id=decision.request_id,
                correlation_id=decision.correlation_id,
                target_actor_ref_kind=(
                    ActorReferenceKind.ACTOR_PROFILE if target_is_actor else None
                ),
                target_actor_ref=str(decision.resource_id) if target_is_actor else None,
                permission_id=decision.permission_id,
                action_id=decision.action_id,
                resource_type=decision.resource_type if target_is_actor else None,
                resource_id=str(decision.resource_id) if target_is_actor else None,
                target_ref_kind=decision.resource_type if target_is_actor else None,
                target_ref_id=str(decision.resource_id) if target_is_actor else None,
                reason="authorization_evaluation",
                denial_code=stored_denial,
                after_facts={"allowed": decision.allowed},
            )
        )
