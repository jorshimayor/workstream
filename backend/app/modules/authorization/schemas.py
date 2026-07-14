"""Strict privacy-bounded types for authority mutation idempotency."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
import json
import re
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from app.core.hashing import canonical_json_hash
from app.modules.audit.schemas import ActorReferenceKind

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_MODEL_CONFIG = ConfigDict(extra="forbid", frozen=True, strict=True, hide_input_in_errors=True)


class AuthorityOperation(StrEnum):
    """Closed authority mutations that require a client idempotency key."""

    SERVICE_ACTOR_CREATE = "service_actor.create"
    ADMIN_ROLE_GRANT_ISSUE = "admin_role_grant.issue"
    ADMIN_ROLE_GRANT_REVOKE = "admin_role_grant.revoke"
    PROJECT_ROLE_GRANT_ISSUE = "project_role_grant.issue"
    PROJECT_ROLE_GRANT_REVOKE = "project_role_grant.revoke"
    ACTOR_PROFILE_SUSPEND = "actor_profile.suspend"
    ACTOR_PROFILE_REACTIVATE = "actor_profile.reactivate"
    ACTOR_PROFILE_DEACTIVATE = "actor_profile.deactivate"
    ACTOR_IDENTITY_LINK_REVOKE = "actor_identity_link.revoke"
    ACTOR_IDENTITY_LINK_REACTIVATE = "actor_identity_link.reactivate"


class AuthorityResourceType(StrEnum):
    """Resource types that an authority mutation can return and invalidate."""

    ACTOR_PROFILE = "actor_profile"
    ACTOR_IDENTITY_LINK = "actor_identity_link"
    ADMIN_ROLE_GRANT = "admin_role_grant"
    PROJECT_ROLE_GRANT = "project_role_grant"


class AdminRole(StrEnum):
    """Closed administrative role tokens."""

    ACCESS_ADMINISTRATOR = "access_administrator"
    OPERATOR = "operator"
    PROJECT_MANAGER = "project_manager"
    FINANCE_AUTHORITY = "finance_authority"
    AUDIT_AUTHORITY = "audit_authority"


class AdminScope(StrEnum):
    """Administrative grant scope tokens."""

    SYSTEM = "system"
    PROJECT = "project"


class ProjectRole(StrEnum):
    """Exact-project contributor role tokens."""

    SUBMITTER = "submitter"
    REVIEWER = "reviewer"
    BOTH = "both"


Digest = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]


class CanonicalAuthorityRequest(BaseModel):
    """Frozen scalar-only base for one canonical mutation request."""

    model_config = _MODEL_CONFIG

    operation: AuthorityOperation


class ServiceActorCreateRequest(CanonicalAuthorityRequest):
    """Canonical server-derived facts for manual service-actor creation."""

    operation: Literal[AuthorityOperation.SERVICE_ACTOR_CREATE]
    identity_reference_digest: Digest
    profile_payload_digest: Digest


class AdminRoleGrantIssueRequest(CanonicalAuthorityRequest):
    """Canonical request facts for issuing one administrative role grant."""

    operation: Literal[AuthorityOperation.ADMIN_ROLE_GRANT_ISSUE]
    target_actor_id: UUID
    role: AdminRole
    scope_type: AdminScope
    scope_project_id: UUID | None = None
    reason_digest: Digest

    @model_validator(mode="after")
    def validate_scope(self):
        """Require role-compatible system or exact-project scope."""

        system_only = self.role in {AdminRole.ACCESS_ADMINISTRATOR, AdminRole.OPERATOR}
        if system_only and self.scope_type != AdminScope.SYSTEM:
            raise ValueError("invalid authority mutation request")
        if (self.scope_type == AdminScope.PROJECT) != (self.scope_project_id is not None):
            raise ValueError("invalid authority mutation request")
        return self


class AdminRoleGrantRevokeRequest(CanonicalAuthorityRequest):
    """Canonical request facts for revoking one administrative role grant."""

    operation: Literal[AuthorityOperation.ADMIN_ROLE_GRANT_REVOKE]
    grant_id: UUID
    reason_digest: Digest


class ProjectRoleGrantIssueRequest(CanonicalAuthorityRequest):
    """Canonical request facts for issuing or replacing one project role grant."""

    operation: Literal[AuthorityOperation.PROJECT_ROLE_GRANT_ISSUE]
    project_id: UUID
    target_actor_id: UUID
    role: ProjectRole
    replaced_grant_id: UUID | None = None
    reason_digest: Digest


class ProjectRoleGrantRevokeRequest(CanonicalAuthorityRequest):
    """Canonical request facts for revoking one project role grant."""

    operation: Literal[AuthorityOperation.PROJECT_ROLE_GRANT_REVOKE]
    project_id: UUID
    grant_id: UUID
    reason_digest: Digest


class ActorProfileSuspendRequest(CanonicalAuthorityRequest):
    """Canonical request facts for suspending one actor profile."""

    operation: Literal[AuthorityOperation.ACTOR_PROFILE_SUSPEND]
    actor_profile_id: UUID
    reason_digest: Digest


class ActorProfileReactivateRequest(CanonicalAuthorityRequest):
    """Canonical request facts for reactivating one actor profile."""

    operation: Literal[AuthorityOperation.ACTOR_PROFILE_REACTIVATE]
    actor_profile_id: UUID
    reason_digest: Digest


class ActorProfileDeactivateRequest(CanonicalAuthorityRequest):
    """Canonical request facts for permanently deactivating one actor profile."""

    operation: Literal[AuthorityOperation.ACTOR_PROFILE_DEACTIVATE]
    actor_profile_id: UUID
    reason_digest: Digest


class ActorIdentityLinkRevokeRequest(CanonicalAuthorityRequest):
    """Canonical request facts for revoking one actor identity link."""

    operation: Literal[AuthorityOperation.ACTOR_IDENTITY_LINK_REVOKE]
    identity_link_id: UUID
    reason_digest: Digest


class ActorIdentityLinkReactivateRequest(CanonicalAuthorityRequest):
    """Canonical request facts for reactivating one actor identity link."""

    operation: Literal[AuthorityOperation.ACTOR_IDENTITY_LINK_REACTIVATE]
    identity_link_id: UUID
    reason_digest: Digest


AuthorityMutationRequest = Annotated[
    ServiceActorCreateRequest
    | AdminRoleGrantIssueRequest
    | AdminRoleGrantRevokeRequest
    | ProjectRoleGrantIssueRequest
    | ProjectRoleGrantRevokeRequest
    | ActorProfileSuspendRequest
    | ActorProfileReactivateRequest
    | ActorProfileDeactivateRequest
    | ActorIdentityLinkRevokeRequest
    | ActorIdentityLinkReactivateRequest,
    Field(discriminator="operation"),
]
_REQUEST_ADAPTER = TypeAdapter(AuthorityMutationRequest)


def parse_authority_request(value: object) -> AuthorityMutationRequest:
    """Readmit an untrusted request without retaining rejected input."""
    admitted = None
    try:
        candidate = dict(value) if isinstance(value, Mapping) else None
        admitted = _REQUEST_ADAPTER.validate_python(candidate, strict=True)
        encoded = json.dumps(
            admitted.model_dump(mode="json", exclude_none=True),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        if len(encoded) > 2048:
            admitted = None
    except Exception:  # noqa: BLE001 - Mapping and rejected values are untrusted
        admitted = None
    if admitted is None:
        raise TypeError("invalid authority mutation request")
    return admitted


def derive_reason_digest(reason: object) -> str:
    """Derive an internal digest from one bounded human mutation reason."""
    valid = isinstance(reason, str) and 1 <= len(reason.encode("utf-8")) <= 500
    if not valid:
        raise TypeError("invalid authority reason")
    return canonical_json_hash({"reason": reason})


def derive_service_identity_digest(issuer: object, subject: object) -> str:
    """Derive an internal identity reference from verified normalized facts."""
    valid = (
        isinstance(issuer, str)
        and issuer.startswith("https://")
        and 1 <= len(issuer.encode("utf-8")) <= 500
        and isinstance(subject, str)
        and 1 <= len(subject.encode("utf-8")) <= 200
    )
    if not valid:
        raise TypeError("invalid verified service identity")
    return canonical_json_hash({"issuer": issuer, "subject": subject})


def derive_service_profile_digest(display_name: object, grant_reason: object) -> str:
    """Derive an internal digest from bounded service profile request facts."""
    valid = (
        isinstance(display_name, str)
        and 1 <= len(display_name.encode("utf-8")) <= 200
        and isinstance(grant_reason, str)
        and 1 <= len(grant_reason.encode("utf-8")) <= 500
    )
    if not valid:
        raise TypeError("invalid service profile request")
    return canonical_json_hash({"display_name": display_name, "grant_reason": grant_reason})


class AuthorityResponseReference(BaseModel):
    """Internal typed reference returned for a committed mutation."""

    model_config = _MODEL_CONFIG

    resource_type: AuthorityResourceType
    resource_id: UUID
    version: Annotated[int, Field(gt=0)] | None = None
    http_status: Literal[200, 201]


class AuthorityClaimHandle(BaseModel):
    """Opaque single-use proof of a reservation claimed by this transaction."""

    model_config = _MODEL_CONFIG

    record_id: UUID
    idempotency_key: UUID
    actor_ref_kind: ActorReferenceKind
    actor_ref: Annotated[str, Field(max_length=100)]
    operation: AuthorityOperation
    request_digest: Digest


class ClaimedReservation(BaseModel):
    """A new reservation owned by the caller's current transaction."""

    model_config = _MODEL_CONFIG
    outcome: Literal["claimed"] = "claimed"
    claim: AuthorityClaimHandle


class ReplayedReservation(BaseModel):
    """The typed response reference from an exact committed retry."""

    model_config = _MODEL_CONFIG
    outcome: Literal["replay"] = "replay"
    response: AuthorityResponseReference


class MismatchedReservation(BaseModel):
    """A privacy-neutral signal that an existing request digest differs."""

    model_config = _MODEL_CONFIG
    outcome: Literal["mismatch"] = "mismatch"


AuthorityReservationResult = ClaimedReservation | ReplayedReservation | MismatchedReservation


class AuthorityInvalidationContext(BaseModel):
    """Caller-owned identifiers for one server-constructed invalidation event."""

    model_config = _MODEL_CONFIG

    event_id: UUID
    request_id: UUID
    correlation_id: UUID


class AuthorityMismatchContext(BaseModel):
    """Privacy-bounded context for mismatch denial evidence."""

    model_config = _MODEL_CONFIG

    event_id: UUID
    request_id: UUID
    correlation_id: UUID
    project_id: UUID | None = None


class AuthorityCompletionResult(BaseModel):
    """Internal result after success, invalidation, and completion flush."""

    model_config = _MODEL_CONFIG

    response: AuthorityResponseReference
    success_event_id: UUID
    invalidation_event_id: UUID


class PendingAuthorityReservationError(RuntimeError):
    """The caller attempted to replay its own uncommitted reservation."""


class InvalidAuthorityClaimError(RuntimeError):
    """A stale, forged, completed, or wrong-namespace claim was supplied."""
