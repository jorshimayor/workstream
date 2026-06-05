from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ActorAuditContext(BaseModel):
    actor_id: str
    external_subject: str
    external_issuer: str
    actor_roles: tuple[str, ...]
    claim_snapshot: dict[str, Any]
    auth_source: Literal["flow", "dev_mock"]
    is_dev_auth: bool


class ActorContext(BaseModel):
    actor_id: str
    external_subject: str
    external_issuer: str
    email: str | None = None
    display_name: str | None = None
    roles: tuple[str, ...] = ()
    claim_snapshot: dict[str, Any] = Field(default_factory=dict)
    auth_source: Literal["flow", "dev_mock"]
    is_dev_auth: bool = False

    def audit_context(self) -> ActorAuditContext:
        return ActorAuditContext(
            actor_id=self.actor_id,
            external_subject=self.external_subject,
            external_issuer=self.external_issuer,
            actor_roles=self.roles,
            claim_snapshot=self.claim_snapshot,
            auth_source=self.auth_source,
            is_dev_auth=self.is_dev_auth,
        )


class ActorResponse(BaseModel):
    actor_id: str
    external_subject: str
    external_issuer: str
    email: str | None = None
    display_name: str | None = None
    roles: tuple[str, ...]
    auth_source: Literal["flow", "dev_mock"]
    is_dev_auth: bool
    audit_context: ActorAuditContext

    @classmethod
    def from_actor(cls, actor: ActorContext) -> "ActorResponse":
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
