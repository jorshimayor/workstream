"""Strict request-scoped authorization runtime contracts."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.authorization.catalogue import ActionId, PermissionId

_STRICT_FROZEN = ConfigDict(extra="forbid", frozen=True, strict=True)


class ActorKind(StrEnum):
    """Canonical actor kinds visible to authorization."""

    HUMAN = "human"
    SERVICE = "service"


class ActorStatus(StrEnum):
    """Canonical actor lifecycle states visible to authorization."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class IdentityLinkStatus(StrEnum):
    """Canonical identity-link lifecycle states visible to authorization."""

    ACTIVE = "active"
    REVOKED = "revoked"


class AuthorizationContext(BaseModel):
    """Bounded canonical identity state for one request only."""

    model_config = _STRICT_FROZEN

    actor_profile_id: UUID
    actor_kind: ActorKind
    actor_status: ActorStatus
    identity_link_id: UUID
    identity_link_status: IdentityLinkStatus
    request_id: UUID
    correlation_id: UUID


class ActorSelfResourceContext(BaseModel):
    """Server-composed facts for the caller's own actor profile."""

    model_config = _STRICT_FROZEN

    resource_type: Literal["actor_profile"]
    resource_id: UUID
    requested_fields: tuple[Literal["display_name", "contact_email"], ...]

    @model_validator(mode="after")
    def require_unique_fields(self):
        """Reject ambiguous duplicate update-field facts."""
        if len(set(self.requested_fields)) != len(self.requested_fields):
            raise ValueError("requested fields must be unique")
        return self


class SystemResourceContext(BaseModel):
    """Non-authoritative placeholder for later fixed system actions."""

    model_config = _STRICT_FROZEN

    resource_type: Literal["system"]
    resource_id: Literal["workstream:system"]


AuthorizationResourceContext = ActorSelfResourceContext | SystemResourceContext


class AuthorizationDenialCode(StrEnum):
    """Closed internal authorization outcomes."""

    UNKNOWN_ACTION = "unknown_action"
    ACTION_UNAVAILABLE = "action_unavailable"
    IDENTITY_LINK_REVOKED = "identity_link_revoked"
    ACTOR_DEACTIVATED = "actor_deactivated"
    ACTOR_SUSPENDED = "actor_suspended"
    RESOURCE_GUARD_DENIED = "resource_guard_denied"
    PERMISSION_NOT_GRANTED = "permission_not_granted"


class MatchedAuthorityKind(StrEnum):
    """Privacy-bounded authority source classifications."""

    ACTOR_SELF = "actor_self"


class AuthorizationDecision(BaseModel):
    """Frozen decision safe for feature code, evidence, and error mapping."""

    model_config = _STRICT_FROZEN

    decision_id: UUID
    action_id: ActionId | None
    permission_id: PermissionId | None
    allowed: bool
    denial_code: AuthorizationDenialCode | None
    resource_type: Literal["actor_profile", "system"]
    resource_id: UUID | Literal["workstream:system"]
    matched_authority_kind: MatchedAuthorityKind | None
    revalidated: bool
    request_id: UUID
    correlation_id: UUID

    @model_validator(mode="after")
    def validate_outcome(self):
        """Keep allow and deny fields mutually coherent."""
        if self.allowed != (self.denial_code is None):
            raise ValueError("authorization outcome is inconsistent")
        if self.allowed != (self.matched_authority_kind is not None):
            raise ValueError("authorization authority match is inconsistent")
        if (self.action_id is None) != (self.permission_id is None):
            raise ValueError("action and permission must be present together")
        if self.allowed and self.action_id is None:
            raise ValueError("allowed decisions require action and permission")
        return self


class AuthorizationDenied(Exception):
    """Fail-closed control flow carrying only one bounded decision."""

    def __init__(self, decision: AuthorizationDecision) -> None:
        if decision.allowed or decision.denial_code is None:
            raise TypeError("authorization denial requires a denied decision")
        self.decision = decision
        super().__init__("Authorization denied")

    @property
    def public_code(self) -> str:
        """Map internal catalogue outcomes to the stable public denial."""
        if self.decision.denial_code in {
            AuthorizationDenialCode.UNKNOWN_ACTION,
            AuthorizationDenialCode.ACTION_UNAVAILABLE,
        }:
            return AuthorizationDenialCode.PERMISSION_NOT_GRANTED.value
        return self.decision.denial_code.value
