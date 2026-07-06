"""Auth actor schemas used by API dependencies and responses."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


def sanitized_claim_snapshot(claim_snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return the audit-safe claim snapshot allowed in Workstream storage.

    Args:
        claim_snapshot: Trusted token claims produced by the auth verifier.

    Returns:
        Claim snapshot with relationship claims reduced to scope identity only.
    """
    sanitized = dict(claim_snapshot)
    relationship_profiles = sanitized.get("workstream_relationship_profiles")
    if not isinstance(relationship_profiles, list):
        return sanitized

    sanitized_relationships: list[dict[str, str]] = []
    for raw_profile in relationship_profiles:
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
        sanitized_relationships.append(
            {
                "profile_type": "project_owner",
                "scope_type": scope_type,
                "scope_id": scope_id,
            }
        )
    sanitized["workstream_relationship_profiles"] = sanitized_relationships
    return sanitized


class ActorAuditContext(BaseModel):
    """Stable actor claims stored with auditable Workstream actions."""

    actor_id: str
    external_subject: str
    external_issuer: str
    actor_roles: tuple[str, ...]
    claim_snapshot: dict[str, Any]
    auth_source: Literal["flow", "dev_mock", "workstream_system"]
    is_dev_auth: bool


class ActorContext(BaseModel):
    """Trusted actor context resolved from an external Flow token."""

    actor_id: str
    external_subject: str
    external_issuer: str
    email: str | None = None
    display_name: str | None = None
    roles: tuple[str, ...] = ()
    claim_snapshot: dict[str, Any] = Field(default_factory=dict)
    auth_source: Literal["flow", "dev_mock", "workstream_system"]
    is_dev_auth: bool = False

    def audit_context(self) -> ActorAuditContext:
        """Build the audit-safe actor snapshot for persisted records.

        Returns:
            Actor audit context derived from the trusted actor claims.
        """
        return ActorAuditContext(
            actor_id=self.actor_id,
            external_subject=self.external_subject,
            external_issuer=self.external_issuer,
            actor_roles=self.roles,
            claim_snapshot=sanitized_claim_snapshot(self.claim_snapshot),
            auth_source=self.auth_source,
            is_dev_auth=self.is_dev_auth,
        )


class ActorResponse(BaseModel):
    """Public response schema for the current actor endpoint."""

    actor_id: str
    external_subject: str
    external_issuer: str
    email: str | None = None
    display_name: str | None = None
    roles: tuple[str, ...]
    auth_source: Literal["flow", "dev_mock", "workstream_system"]
    is_dev_auth: bool
    audit_context: ActorAuditContext

    @classmethod
    def from_actor(cls, actor: ActorContext) -> "ActorResponse":
        """Build an actor response from the trusted actor context.

        Args:
            actor: Trusted actor resolved by authentication.

        Returns:
            Public actor response with audit context included.
        """
        return cls(
            actor_id=actor.actor_id,
            external_subject=actor.external_subject,
            external_issuer=actor.external_issuer,
            email=actor.email,
            display_name=actor.display_name,
            roles=actor.roles,
            auth_source=actor.auth_source,
            is_dev_auth=actor.is_dev_auth,
            audit_context=actor.audit_context(),
        )
