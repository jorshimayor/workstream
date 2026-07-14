"""Typed, privacy-bounded authority audit inputs."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
import json
from typing import Annotated, Any, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

_ENTITY_TYPES = frozenset(
    {
        "actor_profile",
        "actor_identity_link",
        "admin_role_grant",
        "qualification_snapshot",
        "project_role_grant",
        "authorization_decision",
        "authority_invalidation",
    }
)
_RESOURCE_TYPES = frozenset(
    """actor_profile actor_identity_link admin_role_grant project project_role_grant task
    submission review contribution compensation_award compensation_delivery operations
    audit_event""".split()
)
_UUID_TARGET_KINDS = frozenset(
    {"actor_profile", "actor_identity_link", "admin_role_grant", "qualification_snapshot", "project_role_grant"}
)
_PERMISSIONS = frozenset(
    """actor.profile.read_self actor.profile.update_self actor.profile.read_any
    actor.profile.suspend actor.profile.reactivate actor.profile.deactivate
    actor.identity_link.read actor.identity_link.revoke actor.identity_link.reactivate
    actor.service.provision admin_role.read admin_role.grant admin_role.revoke project.create
    project.read project.update project.archive project.guide.manage project.effective_policy.manage
    project.task.manage project.review_policy.manage project.role_grant.read
    project.role_grant.manage task.queue.read task.claim submission.create submission.read_own
    submission.read_for_review review.queue.read review.queue.inspect review.claim review.release
    review.decline_preference review.decision review.lease.force_release review.chain.read
    contribution.read_self contribution.read_project compensation.policy.manage
    compensation.adapter_binding.manage compensation.award.read compensation.delivery.reconcile
    operations.status.read operations.timer.run operations.reconcile.run operations.outbox.retry
    operations.projection.rebuild audit.read audit.export""".split()
)
_DENIAL_CODES = frozenset(
    """required_scope_missing unsupported_subject_kind service_actor_not_provisioned
    identity_link_revoked actor_suspended actor_deactivated permission_not_granted
    scope_not_authorized self_grant_forbidden self_role_revoke_forbidden resource_guard_denied
    actor_not_found grant_not_found resource_not_found actor_already_suspended actor_not_suspended
    actor_deactivated_terminal last_access_administrator admin_role_grant_exists
    project_role_grant_exists identity_link_conflict resource_project_mismatch idempotency_mismatch
    invalid_role_scope invalid_project_role qualification_snapshot_invalid""".split()
)
_ADMIN_ROLES = frozenset(
    {"access_administrator", "operator", "project_manager", "finance_authority", "audit_authority"}
)
_PROJECT_ROLES = frozenset({"submitter", "reviewer", "both"})
_FACT_VALUES: dict[str, frozenset[str]] = {
    "status": frozenset({"active", "suspended", "deactivated", "revoked", "captured"}),
    "subject_kind": frozenset({"human", "service"}),
    "provisioning_method": frozenset({"automatic_first_access", "manual_service_provisioning"}),
    "role": _ADMIN_ROLES | _PROJECT_ROLES,
    "scope_type": frozenset({"system", "project"}),
}


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


class ActorReferenceKind(StrEnum):
    """Stable namespaces usable before and after canonical actor migration."""

    LEGACY_ACTOR = "legacy_actor"
    ACTOR_PROFILE = "actor_profile"
    SYSTEM_PRINCIPAL = "system_principal"


_REASONS = {
    AuthorityEventType.ACTOR_PROFILE_PROVISIONED: {"automatic_first_access"},
    AuthorityEventType.SERVICE_ACTOR_PROVISIONED: {"manual_service_provisioning"},
    **dict.fromkeys(tuple(AuthorityEventType)[2:5], {"identity_lifecycle_change"}),
    AuthorityEventType.ACTOR_PROFILE_SUSPENDED: {"security_response", "administrative_correction"},
    AuthorityEventType.ACTOR_PROFILE_REACTIVATED: {"administrative_correction"},
    AuthorityEventType.ACTOR_PROFILE_DEACTIVATED: {"security_response", "administrative_correction"},
    AuthorityEventType.INITIAL_ACCESS_ADMIN_BOOTSTRAPPED: {"initial_access_bootstrap"},
    AuthorityEventType.ADMIN_ROLE_GRANT_ISSUED: {"authority_assignment"},
    AuthorityEventType.ADMIN_ROLE_GRANT_REVOKED: {"authority_revocation"},
    AuthorityEventType.ADMIN_ROLE_GRANT_ISSUE_DENIED: {"authorization_policy_denial"},
    AuthorityEventType.LAST_ACCESS_ADMIN_OPERATION_DENIED: {"authorization_policy_denial"},
    AuthorityEventType.PROJECT_ROLE_QUALIFICATION_CAPTURED: {"qualification_evidence_captured"},
    AuthorityEventType.PROJECT_ROLE_GRANT_ISSUED: {"authority_assignment"},
    AuthorityEventType.PROJECT_ROLE_GRANT_REPLACED: {"authority_replacement"},
    AuthorityEventType.PROJECT_ROLE_GRANT_REVOKED: {"authority_revocation"},
    AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED: {"authorization_evaluation"},
    AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED: {"authorization_evaluation"},
    AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED: {"authority_state_changed"},
}


def _enum_value(value: object, enum: type[StrEnum]) -> str | None:
    raw = value.value if isinstance(value, enum) else value
    return raw if isinstance(raw, str) and raw in {item.value for item in enum} else None


def _uuid(value: object) -> str | None:
    raw = str(value) if isinstance(value, UUID) else value
    try:
        return raw if isinstance(raw, str) and str(UUID(raw)) == raw else None
    except ValueError:
        return None


def _registered(value: object, values: frozenset[str] | set[str]) -> bool:
    return isinstance(value, str) and value in values


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError
    return value


def _facts(value: object) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping) or len(value) > 8:
        return None
    if not set(value).issubset(frozenset(_FACT_VALUES) | {"effective", "allowed", "scope_id"}):
        return None
    data = dict(value)
    for key, item in data.items():
        if key in {"effective", "allowed"} and type(item) is not bool:
            return None
        if key == "scope_id" and _uuid(item) is None:
            return None
        if key in _FACT_VALUES and (not isinstance(item, str) or item not in _FACT_VALUES[key]):
            return None
    if len(json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode()) > 4096:
        return None
    return data


def _grant_facts(facts: dict[str, object] | None, roles: frozenset[str], status: str, effective: bool) -> bool:
    if facts is None or facts.get("role") not in roles:
        return False
    scope = facts.get("scope_type")
    expected = {"status", "role", "scope_type", "effective"} | ({"scope_id"} if scope == "project" else set())
    return (
        set(facts) == expected
        and facts["status"] == status
        and facts["effective"] is effective
        and scope in {"system", "project"}
        and not (facts["role"] in {"access_administrator", "operator"} and scope != "system")
        and not (facts["role"] in _PROJECT_ROLES and scope != "project")
    )


def _event_facts_valid(event: AuthorityEventType, before: dict[str, object] | None, after: dict[str, object] | None) -> bool:
    exact = {
        AuthorityEventType.ACTOR_PROFILE_PROVISIONED: (None, {"status": "active", "subject_kind": "human", "provisioning_method": "automatic_first_access"}),
        AuthorityEventType.SERVICE_ACTOR_PROVISIONED: (None, {"status": "active", "subject_kind": "service", "provisioning_method": "manual_service_provisioning"}),
        AuthorityEventType.ACTOR_IDENTITY_LINK_REVOKED: ({"status": "active"}, {"status": "revoked"}),
        AuthorityEventType.ACTOR_IDENTITY_LINK_REACTIVATED: ({"status": "revoked"}, {"status": "active"}),
        AuthorityEventType.ACTOR_PROFILE_SUSPENDED: ({"status": "active"}, {"status": "suspended"}),
        AuthorityEventType.ACTOR_PROFILE_REACTIVATED: ({"status": "suspended"}, {"status": "active"}),
        AuthorityEventType.PROJECT_ROLE_QUALIFICATION_CAPTURED: (None, {"status": "captured"}),
        AuthorityEventType.ADMIN_ROLE_GRANT_ISSUE_DENIED: (None, None),
        AuthorityEventType.LAST_ACCESS_ADMIN_OPERATION_DENIED: (None, None),
        AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED: (None, {"allowed": True}),
        AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED: (None, {"allowed": False}),
        AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED: ({"effective": True}, {"effective": False}),
    }
    if event in exact:
        return (before, after) == exact[event]
    if event == AuthorityEventType.ACTOR_IDENTITY_LINKED:
        return before is None and after in ({"status": "active", "subject_kind": "human"}, {"status": "active", "subject_kind": "service"})
    if event == AuthorityEventType.ACTOR_PROFILE_DEACTIVATED:
        return before in ({"status": "active"}, {"status": "suspended"}) and after == {"status": "deactivated"}
    if event == AuthorityEventType.INITIAL_ACCESS_ADMIN_BOOTSTRAPPED:
        return before is None and _grant_facts(after, _ADMIN_ROLES, "active", True) and after["role"] == "access_administrator"
    roles, action = {
        AuthorityEventType.ADMIN_ROLE_GRANT_ISSUED: (_ADMIN_ROLES, "issued"),
        AuthorityEventType.ADMIN_ROLE_GRANT_REVOKED: (_ADMIN_ROLES, "revoked"),
        AuthorityEventType.PROJECT_ROLE_GRANT_ISSUED: (_PROJECT_ROLES, "issued"),
        AuthorityEventType.PROJECT_ROLE_GRANT_REPLACED: (_PROJECT_ROLES, "replaced"),
        AuthorityEventType.PROJECT_ROLE_GRANT_REVOKED: (_PROJECT_ROLES, "revoked"),
    }[event]
    if action == "issued":
        return before is None and _grant_facts(after, roles, "active", True)
    if action == "revoked":
        return (
            _grant_facts(before, roles, "active", True)
            and _grant_facts(after, roles, "revoked", False)
            and (before["role"], before["scope_type"], before.get("scope_id"))
            == (after["role"], after["scope_type"], after.get("scope_id"))
        )
    return _grant_facts(before, roles, "active", True) and _grant_facts(after, roles, "active", True)


class AuthorityAuditEventInput(BaseModel):
    """Validate one authority event without provider claims or request bodies."""

    model_config = ConfigDict(extra="forbid", strict=True)

    event_id: UUID
    event_type: AuthorityEventType
    entity_type: str
    entity_id: str
    actor_ref_kind: ActorReferenceKind
    actor_ref: Annotated[str, Field(max_length=120)]
    request_id: UUID
    correlation_id: UUID
    target_actor_ref_kind: ActorReferenceKind | None = None
    target_actor_ref: Annotated[str, Field(max_length=120)] | None = None
    matched_grant_id: str | None = None
    permission_id: str | None = None
    project_id: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    target_ref_kind: str | None = None
    target_ref_id: Annotated[str, Field(max_length=120)] | None = None
    reason: str
    denial_code: str | None = None
    idempotency_reference: UUID | None = None
    invalidation_cause_event_id: UUID | None = None
    invalidation_target_kind: str | None = None
    invalidation_target_ref: Annotated[str, Field(max_length=120)] | None = None
    before_facts: dict[str, str | bool] | None = None
    after_facts: dict[str, str | bool] | None = None

    @model_validator(mode="before")
    @classmethod
    def admit_privacy_safe_input(cls, value: object) -> object:
        """Reject unsafe input before Pydantic can retain rejected values."""
        try:
            admitted = cls._inspect_privacy_safe_input(value)
        except Exception:  # noqa: BLE001 - hostile Mapping methods are untrusted input
            admitted = None
        if admitted is None:
            raise TypeError("invalid authority audit input")
        return admitted

    @classmethod
    def _inspect_privacy_safe_input(cls, value: object) -> dict | None:
        if not isinstance(value, Mapping) or set(value) - cls.model_fields.keys():
            return None
        data = dict(value)
        event_raw = _enum_value(data.get("event_type"), AuthorityEventType)
        kind = _enum_value(data.get("actor_ref_kind"), ActorReferenceKind)
        event = AuthorityEventType(event_raw) if event_raw else None
        actor_ref = data.get("actor_ref")
        uuid_fields = (
            "event_id", "entity_id", "request_id", "correlation_id", "matched_grant_id",
            "project_id", "resource_id", "idempotency_reference", "invalidation_cause_event_id",
        )
        invalid = (
            event is None
            or not _registered(data.get("entity_type"), _ENTITY_TYPES)
            or any(data.get(key) is not None and _uuid(data[key]) is None for key in uuid_fields)
            or kind is None
            or (kind == "system_principal" and actor_ref != "workstream:system:bootstrap")
            or (kind != "system_principal" and _uuid(actor_ref) is None)
            or data.get("permission_id") is not None and not _registered(data["permission_id"], _PERMISSIONS)
            or data.get("denial_code") is not None and not _registered(data["denial_code"], _DENIAL_CODES)
            or data.get("resource_type") is not None and not _registered(data["resource_type"], _RESOURCE_TYPES)
            or data.get("target_ref_kind") is not None
            and not _registered(data["target_ref_kind"], _UUID_TARGET_KINDS | {"permission_registry"})
            or data.get("invalidation_target_kind") is not None
            and not _registered(data["invalidation_target_kind"], _UUID_TARGET_KINDS | {"permission_registry"})
            or event is not None and not _registered(data.get("reason"), _REASONS[event])
            or _facts(data.get("before_facts")) is None and data.get("before_facts") is not None
            or _facts(data.get("after_facts")) is None and data.get("after_facts") is not None
        )
        for prefix in ("target_ref", "invalidation_target"):
            ref_kind = data.get(f"{prefix}_kind")
            ref = data.get(f"{prefix}_ref" if prefix == "invalidation_target" else f"{prefix}_id")
            invalid |= (ref_kind is None) != (ref is None)
            invalid |= _registered(ref_kind, _UUID_TARGET_KINDS) and ref is not None and _uuid(ref) is None
            invalid |= ref_kind == "permission_registry" and not _registered(ref, _PERMISSIONS)
        target_kind, target_ref = data.get("target_actor_ref_kind"), data.get("target_actor_ref")
        invalid |= (target_kind is None) != (target_ref is None)
        invalid |= target_kind is not None and (
            _enum_value(target_kind, ActorReferenceKind) != "actor_profile" or _uuid(target_ref) is None
        )
        return None if invalid else data

    @classmethod
    def model_validate_json(cls, json_data: str | bytes | bytearray, **kwargs: Any) -> Self:
        """Parse JSON without retaining malformed or non-object input."""
        try:
            value = json.loads(json_data, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError):
            value = None
        if not isinstance(value, Mapping):
            raise TypeError("invalid authority audit input")
        return super().model_validate_json(json_data, **kwargs)

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        """Enforce event, reference, fact, and project-scope integrity."""
        if self.resource_id is not None and self.resource_type is None:
            raise ValueError("resource ID requires resource type")
        if self.entity_type in {"authorization_decision", "authority_invalidation"} and self.entity_id != str(self.event_id):
            raise ValueError("decision entity ID must equal event ID")
        if self.resource_type == "project" and self.resource_id is not None and self.resource_id != self.project_id:
            raise ValueError("project resource must match project scope")
        before, after = _facts(self.before_facts), _facts(self.after_facts)
        if not _event_facts_valid(self.event_type, before, after):
            raise ValueError("invalid authority event facts")
        for facts in (before, after):
            if facts and "scope_type" in facts:
                if facts["scope_type"] == "system" and self.project_id is not None:
                    raise ValueError("system grant cannot carry project scope")
                if facts["scope_type"] == "project" and facts.get("scope_id") != self.project_id:
                    raise ValueError("grant facts must match project scope")
        if before and after and "scope_id" in before and before.get("scope_id") != after.get("scope_id"):
            raise ValueError("replacement cannot change project scope")
        invalidation = self.invalidation_cause_event_id is not None or self.invalidation_target_kind
        if self.event_type == AuthorityEventType.SENSITIVE_AUTHORIZATION_ALLOWED:
            if self.permission_id is None or self.denial_code is not None or invalidation:
                raise ValueError("invalid allowed authorization evidence")
        elif self.event_type == AuthorityEventType.SENSITIVE_AUTHORIZATION_DENIED:
            if self.permission_id is None or self.denial_code is None or invalidation or self.idempotency_reference:
                raise ValueError("invalid denied authorization evidence")
        elif self.event_type in {
            AuthorityEventType.ADMIN_ROLE_GRANT_ISSUE_DENIED,
            AuthorityEventType.LAST_ACCESS_ADMIN_OPERATION_DENIED,
        }:
            if self.denial_code is None:
                raise ValueError("denied authority operation requires denial code")
        elif self.event_type == AuthorityEventType.AUTHORITY_INVALIDATION_REQUESTED:
            if self.invalidation_cause_event_id is None or self.invalidation_target_kind is None or self.denial_code:
                raise ValueError("invalid authority invalidation evidence")
        if self.invalidation_cause_event_id == self.event_id:
            raise ValueError("invalidation cannot reference its own event")
        return self
