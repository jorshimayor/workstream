"""SQLAlchemy models for verified actor identity and profile metadata."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

ACTOR_PROFILE_TYPES = ("worker", "reviewer", "admin", "project_manager", "project_owner")
ACTOR_PROFILE_STATUSES = ("observed", "active", "disabled")
GLOBAL_PROFILE_SCOPE_TYPE = "global"
GLOBAL_PROFILE_SCOPE_ID = "global"
_PROFILE_TYPE_CHECK_VALUES = ", ".join(f"'{profile_type}'" for profile_type in ACTOR_PROFILE_TYPES)
_PROFILE_STATUS_CHECK_VALUES = ", ".join(f"'{status}'" for status in ACTOR_PROFILE_STATUSES)


class ActorIdentity(Base):
    """Local registry row for a verified external Flow actor."""

    __tablename__ = "actor_identities"
    __table_args__ = (
        UniqueConstraint(
            "external_issuer",
            "external_subject",
            name="uq_actor_identities_external_identity",
        ),
    )

    actor_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    external_subject: Mapped[str] = mapped_column(String(200), nullable=False)
    external_issuer: Mapped[str] = mapped_column(String(200), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320))
    last_seen_roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    last_claim_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    auth_source: Mapped[str] = mapped_column(String(50), nullable=False)
    is_dev_auth: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    profiles: Mapped[list[ActorProfile]] = relationship(
        back_populates="identity",
        cascade="all, delete-orphan",
    )


class ActorProfile(Base):
    """Shared workflow metadata and eligibility profile for an actor."""

    __tablename__ = "actor_profiles"
    __table_args__ = (
        CheckConstraint(
            f"profile_type in ({_PROFILE_TYPE_CHECK_VALUES})",
            name="ck_actor_profiles_profile_type",
        ),
        CheckConstraint(
            f"status in ({_PROFILE_STATUS_CHECK_VALUES})",
            name="ck_actor_profiles_status",
        ),
        UniqueConstraint(
            "actor_id",
            "profile_type",
            "scope_type",
            "scope_id",
            name="uq_actor_profiles_actor_type_scope",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor_id: Mapped[str] = mapped_column(
        ForeignKey("actor_identities.actor_id"),
        nullable=False,
        index=True,
    )
    profile_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="observed", index=True)
    skill_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    scope_type: Mapped[str] = mapped_column(String(50), nullable=False, default=GLOBAL_PROFILE_SCOPE_TYPE)
    scope_id: Mapped[str] = mapped_column(String(100), nullable=False, default=GLOBAL_PROFILE_SCOPE_ID)
    profile_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    identity: Mapped[ActorIdentity] = relationship(back_populates="profiles")
