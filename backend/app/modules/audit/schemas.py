"""Typed, privacy-bounded authority audit inputs."""

from __future__ import annotations

from enum import StrEnum
import json
import re
from typing import Annotated, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_FACT_KEY = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
_SYSTEM_REF = re.compile(r"^[a-z][a-z0-9_]*(?::[a-z][a-z0-9_-]*)+$")
_SAFE_REASON = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.,:;()!?-]{0,999}$")
_FACT_BOOL_KEYS = frozenset({"effective"})
_FACT_ID_KEYS = frozenset({"role_id", "scope_id"})
_FACT_TOKEN = re.compile(r"^[a-z][a-z0-9_]{0,79}$")
SafeRef100 = Annotated[str, Field(max_length=100, pattern=_SAFE_REF.pattern)]
SafeRef36 = Annotated[str, Field(max_length=36, pattern=_SAFE_REF.pattern)]
SafeToken = Annotated[str, Field(max_length=80, pattern=r"^[a-z][a-z0-9_.:-]*$")]
SafeToken32 = Annotated[str, Field(max_length=32, pattern=r"^[a-z][a-z0-9_.:-]*$")]


def _is_uuid(value: str) -> bool:
    """Return whether a value is a canonical local UUID."""
    try:
        return str(UUID(value)) == value
    except ValueError:
        return False


def _safe_fact_value(key: str, value: object) -> bool:
    """Accept only typed booleans or bounded local tokens in state facts."""
    if value is None:
        return True
    if key in _FACT_BOOL_KEYS:
        return type(value) is bool
    pattern = _SAFE_REF if key in _FACT_ID_KEYS else _FACT_TOKEN
    return (
        isinstance(value, str)
        and not value.startswith("eyJ")
        and pattern.fullmatch(value) is not None
    )


def _safe_actor_ref(kind: ActorReferenceKind, value: str) -> bool:
    """Validate one local or registered system actor reference."""
    return bool(_SYSTEM_REF.fullmatch(value)) if kind == ActorReferenceKind.SYSTEM_PRINCIPAL else _is_uuid(value)


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
    **dict.fromkeys(_EVENT_TYPES[17:19], frozenset({"status", "decision_code", "effective"})),
    _EVENT_TYPES[19]: frozenset({"status", "target_status", "effective"}),
}
_ALL_FACT_KEYS = frozenset().union(*_EVENT_FACT_KEYS.values())


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
    entity_type: SafeToken
    entity_id: SafeRef36
    actor_ref_kind: ActorReferenceKind
    actor_ref: SafeRef100
    request_id: UUID
    correlation_id: UUID
    target_actor_ref_kind: ActorReferenceKind | None = None
    target_actor_ref: SafeRef100 | None = None
    matched_grant_id: SafeRef100 | None = None
    permission_id: Annotated[str, Field(max_length=120, pattern=r"^[a-z][a-z0-9_.:-]*$")] | None = None
    project_id: SafeRef36 | None = None
    resource_type: SafeToken | None = None
    resource_id: SafeRef100 | None = None
    target_ref_kind: SafeToken32 | None = None
    target_ref_id: SafeRef100 | None = None
    reason: str | None = Field(default=None, max_length=1000, pattern=_SAFE_REASON.pattern)
    denial_code: Annotated[str, Field(max_length=80, pattern=r"^[a-z][a-z0-9_]*$")] | None = None
    idempotency_reference: UUID | None = None
    invalidation_cause_event_id: UUID | None = None
    invalidation_target_kind: SafeToken32 | None = None
    invalidation_target_ref: SafeRef100 | None = None
    before_facts: dict[str, str | bool | None] | None = None
    after_facts: dict[str, str | bool | None] | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_unknown_fields_without_echo(cls, value: object) -> object:
        """Reject unknown fields before Pydantic can retain their values."""
        if isinstance(value, dict) and value.keys() - cls.model_fields.keys():
            raise TypeError("unexpected authority audit fields")
        return value

    @field_validator("before_facts", "after_facts", mode="before")
    @classmethod
    def validate_facts(cls, value: object) -> object:
        """Reject nested, excessive, or oversized state facts."""
        if value is None:
            return None
        if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
            raise ValueError("invalid authority state facts")
        if len(value) > 16 or any(_FACT_KEY.fullmatch(key) is None for key in value):
            raise ValueError("invalid authority state facts")
        if not set(value).issubset(_ALL_FACT_KEYS):
            raise ValueError("authority state facts are not allowed for this event")
        if any(isinstance(item, (dict, list, tuple, set)) for item in value.values()):
            raise ValueError("invalid authority state facts")
        if len(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()) > 4096:
            raise ValueError("authority state facts exceed size limit")
        if any(not _safe_fact_value(key, item) for key, item in value.items()):
            raise ValueError("invalid authority state fact value")
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
        references = ((self.actor_ref_kind, self.actor_ref), (self.target_actor_ref_kind, self.target_actor_ref))
        if any(kind is not None and not _safe_actor_ref(kind, reference or "") for kind, reference in references):
            raise ValueError("actor references must use canonical local identifiers")
        if self.invalidation_cause_event_id == self.event_id:
            raise ValueError("invalidation cannot reference its own event")
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
