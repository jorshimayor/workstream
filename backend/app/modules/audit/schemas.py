"""Typed, privacy-bounded authority audit inputs."""

from __future__ import annotations

from enum import StrEnum
import json
import re
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_FACT_KEY = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class AuthorityEventType(StrEnum):
    """Closed authority event tokens from the adopted specification."""

    ACTOR_PROFILE_PROVISIONED = "ActorProfileProvisioned"
    SERVICE_ACTOR_PROVISIONED = "ServiceActorProvisioned"
    ACTOR_IDENTITY_LINKED = "ActorIdentityLinked"
    ACTOR_IDENTITY_LINK_REVOKED = "ActorIdentityLinkRevoked"
    ACTOR_IDENTITY_LINK_REACTIVATED = "ActorIdentityLinkReactivated"
    ACTOR_PROFILE_SUSPENDED = "ActorProfileSuspended"
    ACTOR_PROFILE_REACTIVATED = "ActorProfileReactivated"
    ACTOR_PROFILE_DEACTIVATED = "ActorProfileDeactivated"
    INITIAL_ACCESS_ADMIN_BOOTSTRAPPED = "InitialAccessAdministratorBootstrapped"
    ADMIN_ROLE_GRANT_ISSUED = "AdminRoleGrantIssued"
    ADMIN_ROLE_GRANT_REVOKED = "AdminRoleGrantRevoked"
    ADMIN_ROLE_GRANT_ISSUE_DENIED = "AdminRoleGrantIssueDenied"
    LAST_ACCESS_ADMIN_OPERATION_DENIED = "LastAccessAdministratorOperationDenied"
    PROJECT_ROLE_QUALIFICATION_CAPTURED = "ProjectRoleQualificationSnapshotCaptured"
    PROJECT_ROLE_GRANT_ISSUED = "ProjectRoleGrantIssued"
    PROJECT_ROLE_GRANT_REPLACED = "ProjectRoleGrantReplaced"
    PROJECT_ROLE_GRANT_REVOKED = "ProjectRoleGrantRevoked"
    SENSITIVE_AUTHORIZATION_ALLOWED = "SensitiveAuthorizationAllowed"
    SENSITIVE_AUTHORIZATION_DENIED = "SensitiveAuthorizationDenied"
    AUTHORITY_INVALIDATION_REQUESTED = "AuthorityInvalidationRequested"


# Specification categories are contiguous in the closed enum above.
_EVENT_TYPES = tuple(AuthorityEventType)
_EVENT_FACT_KEYS = {
    **dict.fromkeys(
        _EVENT_TYPES[:8],
        frozenset({"status", "subject_kind", "provisioning_method", "link_status"}),
    ),
    **dict.fromkeys(
        _EVENT_TYPES[8:17],
        frozenset(
            {"status", "role_id", "scope_type", "scope_id", "effective", "qualification_status"}
        ),
    ),
    **dict.fromkeys(
        _EVENT_TYPES[17:19], frozenset({"status", "decision_code", "effective"})
    ),
    _EVENT_TYPES[19]: frozenset({"status", "target_status", "effective"}),
}


class ActorReferenceKind(StrEnum):
    """Stable namespaces usable before and after canonical actor migration."""

    LEGACY_ACTOR = "legacy_actor"
    ACTOR_PROFILE = "actor_profile"
    SYSTEM_PRINCIPAL = "system_principal"


class AuthorityAuditEventInput(BaseModel):
    """Validate one authority event without provider claims or request bodies."""

    model_config = ConfigDict(extra="forbid", strict=True)

    event_id: UUID = Field(default_factory=uuid4)
    event_type: AuthorityEventType
    entity_type: str = Field(min_length=1, max_length=80, pattern=r"^[a-z][a-z0-9_.:-]*$")
    entity_id: str = Field(min_length=1, max_length=36)
    actor_ref_kind: ActorReferenceKind
    actor_ref: str = Field(min_length=1, max_length=100)
    request_id: UUID
    correlation_id: UUID
    target_actor_ref_kind: ActorReferenceKind | None = None
    target_actor_ref: str | None = Field(default=None, min_length=1, max_length=100)
    matched_grant_id: str | None = Field(default=None, min_length=1, max_length=100)
    permission_id: str | None = Field(
        default=None, min_length=1, max_length=120, pattern=r"^[a-z][a-z0-9_.:-]*$"
    )
    project_id: str | None = Field(default=None, min_length=1, max_length=36)
    resource_type: str | None = Field(
        default=None, min_length=1, max_length=80, pattern=r"^[a-z][a-z0-9_.:-]*$"
    )
    resource_id: str | None = Field(default=None, min_length=1, max_length=100)
    target_ref_kind: str | None = Field(
        default=None, min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_.:-]*$"
    )
    target_ref_id: str | None = Field(default=None, min_length=1, max_length=100)
    reason: str | None = Field(default=None, max_length=1000)
    denial_code: str | None = Field(
        default=None, min_length=1, max_length=80, pattern=r"^[a-z][a-z0-9_]*$"
    )
    idempotency_reference: UUID | None = None
    invalidation_cause_event_id: UUID | None = None
    invalidation_target_kind: str | None = Field(
        default=None, min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_.:-]*$"
    )
    invalidation_target_ref: str | None = Field(default=None, min_length=1, max_length=100)
    before_facts: dict[str, str | int | bool | None] | None = None
    after_facts: dict[str, str | int | bool | None] | None = None

    @field_validator("before_facts", "after_facts", mode="before")
    @classmethod
    def validate_facts(cls, value: object) -> object:
        """Reject nested, excessive, or oversized state facts."""
        if value is None:
            return None
        if not isinstance(value, dict) or any(
            not isinstance(key, str) for key in value
        ):
            raise ValueError("invalid authority state facts")
        if len(value) > 16 or any(_FACT_KEY.fullmatch(key) is None for key in value):
            raise ValueError("invalid authority state facts")
        if any(isinstance(item, (dict, list, tuple, set)) for item in value.values()):
            raise ValueError("invalid authority state facts")
        if len(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()) > 4096:
            raise ValueError("authority state facts exceed size limit")
        return value

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        """Enforce paired references and foundation event-specific fields."""
        for left, right in (
            (self.target_actor_ref_kind, self.target_actor_ref),
            (self.resource_type, self.resource_id),
            (self.target_ref_kind, self.target_ref_id),
            (self.invalidation_target_kind, self.invalidation_target_ref),
        ):
            if (left is None) != (right is None):
                raise ValueError("authority reference fields must be paired")
        invalidation = self.invalidation_cause_event_id is not None or self.invalidation_target_kind
        allowed_fact_keys = _EVENT_FACT_KEYS[self.event_type]
        if any(
            facts is not None and not set(facts).issubset(allowed_fact_keys)
            for facts in (self.before_facts, self.after_facts)
        ):
            raise ValueError("authority state facts are not allowed for this event")
        if self.event_type == AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED:
            if self.permission_id is None or self.denial_code is not None or invalidation:
                raise ValueError("invalid allowed authorization evidence")
        elif self.event_type == AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED:
            if self.permission_id is None or self.denial_code is None or invalidation:
                raise ValueError("invalid denied authorization evidence")
            if self.idempotency_reference is not None:
                raise ValueError("denial cannot reference committed idempotency")
        elif self.event_type == AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED:
            if self.invalidation_cause_event_id is None or self.invalidation_target_kind is None:
                raise ValueError("invalid authority invalidation evidence")
            if self.denial_code is not None:
                raise ValueError("invalidation cannot carry denial code")
        return self
