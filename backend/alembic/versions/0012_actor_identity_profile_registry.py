"""actor identity profile registry

Revision ID: 0012_actor_identity_profiles
Revises: 0011_task_artifact_cleanup
Create Date: 2026-07-06
"""

from __future__ import annotations

from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0012_actor_identity_profiles"
down_revision = "0011_task_artifact_cleanup"
branch_labels = None
depends_on = None


actor_identities_table = sa.table(
    "actor_identities",
    sa.column("actor_id", sa.String),
    sa.column("external_subject", sa.String),
    sa.column("external_issuer", sa.String),
    sa.column("display_name", sa.String),
    sa.column("email", sa.String),
    sa.column("last_seen_roles", sa.JSON),
    sa.column("last_claim_snapshot", sa.JSON),
    sa.column("auth_source", sa.String),
    sa.column("is_dev_auth", sa.Boolean),
    sa.column("last_seen_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)

actor_profiles_table = sa.table(
    "actor_profiles",
    sa.column("id", sa.String),
    sa.column("actor_id", sa.String),
    sa.column("profile_type", sa.String),
    sa.column("status", sa.String),
    sa.column("skill_tags", sa.JSON),
    sa.column("scope_type", sa.String),
    sa.column("scope_id", sa.String),
    sa.column("profile_metadata", sa.JSON),
    sa.column("updated_at", sa.DateTime),
)


def upgrade() -> None:
    """Create actor registry tables and migrate old profile stores."""
    op.create_table(
        "actor_identities",
        sa.Column("actor_id", sa.String(length=100), nullable=False),
        sa.Column("external_subject", sa.String(length=200), nullable=False),
        sa.Column("external_issuer", sa.String(length=200), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("last_seen_roles", sa.JSON(), nullable=False),
        sa.Column("last_claim_snapshot", sa.JSON(), nullable=False),
        sa.Column("auth_source", sa.String(length=50), nullable=False),
        sa.Column("is_dev_auth", sa.Boolean(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("actor_id", name=op.f("pk_actor_identities")),
        sa.UniqueConstraint(
            "external_issuer",
            "external_subject",
            name="uq_actor_identities_external_identity",
        ),
    )
    op.create_table(
        "actor_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=100), nullable=False),
        sa.Column("profile_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("skill_tags", sa.JSON(), nullable=False),
        sa.Column("scope_type", sa.String(length=50), nullable=False),
        sa.Column("scope_id", sa.String(length=100), nullable=False),
        sa.Column("profile_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "profile_type in ('worker', 'reviewer', 'admin', 'project_manager', 'project_owner')",
            name="ck_actor_profiles_profile_type",
        ),
        sa.CheckConstraint(
            "status in ('observed', 'active', 'disabled')",
            name="ck_actor_profiles_status",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["actor_identities.actor_id"],
            name=op.f("fk_actor_profiles_actor_id_actor_identities"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_actor_profiles")),
        sa.UniqueConstraint(
            "actor_id",
            "profile_type",
            "scope_type",
            "scope_id",
            name="uq_actor_profiles_actor_type_scope",
        ),
    )
    op.create_index(op.f("ix_actor_profiles_actor_id"), "actor_profiles", ["actor_id"], unique=False)
    op.create_index(op.f("ix_actor_profiles_profile_type"), "actor_profiles", ["profile_type"], unique=False)
    op.create_index(op.f("ix_actor_profiles_status"), "actor_profiles", ["status"], unique=False)

    connection = op.get_bind()
    _backfill_legacy_profiles(connection, "worker_profiles", "worker")
    _backfill_legacy_profiles(connection, "reviewer_profiles", "reviewer")

    op.drop_index(op.f("ix_reviewer_profiles_status"), table_name="reviewer_profiles")
    op.drop_table("reviewer_profiles")
    op.drop_index(op.f("ix_worker_profiles_status"), table_name="worker_profiles")
    op.drop_table("worker_profiles")


def downgrade() -> None:
    """Restore legacy profile tables from actor profiles, then drop registry tables."""
    op.create_table(
        "worker_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=100), nullable=False),
        sa.Column("external_subject", sa.String(length=200), nullable=False),
        sa.Column("external_issuer", sa.String(length=200), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("skill_tags", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_worker_profiles")),
        sa.UniqueConstraint("actor_id", name=op.f("uq_worker_profiles_actor_id")),
    )
    op.create_index(op.f("ix_worker_profiles_status"), "worker_profiles", ["status"], unique=False)
    op.create_table(
        "reviewer_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=100), nullable=False),
        sa.Column("external_subject", sa.String(length=200), nullable=False),
        sa.Column("external_issuer", sa.String(length=200), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("skill_tags", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reviewer_profiles")),
        sa.UniqueConstraint("actor_id", name=op.f("uq_reviewer_profiles_actor_id")),
    )
    op.create_index(op.f("ix_reviewer_profiles_status"), "reviewer_profiles", ["status"], unique=False)

    connection = op.get_bind()
    _restore_legacy_profiles(connection, "worker_profiles", "worker")
    _restore_legacy_profiles(connection, "reviewer_profiles", "reviewer")

    op.drop_index(op.f("ix_actor_profiles_status"), table_name="actor_profiles")
    op.drop_index(op.f("ix_actor_profiles_profile_type"), table_name="actor_profiles")
    op.drop_index(op.f("ix_actor_profiles_actor_id"), table_name="actor_profiles")
    op.drop_table("actor_profiles")
    op.drop_table("actor_identities")


def _backfill_legacy_profiles(connection, table_name: str, profile_type: str) -> None:
    """Backfill one legacy profile table into actor identities and profiles."""
    rows = (
        connection.execute(
            sa.text(
                f"""
                select
                    id,
                    actor_id,
                    external_subject,
                    external_issuer,
                    display_name,
                    email,
                    skill_tags,
                    status,
                    created_at,
                    updated_at
                from {table_name}
                """
            )
        )
        .mappings()
        .all()
    )
    for row in rows:
        roles = [profile_type]
        connection.execute(
            postgresql.insert(actor_identities_table)
            .values(
                actor_id=row["actor_id"],
                external_subject=row["external_subject"],
                external_issuer=row["external_issuer"],
                display_name=row["display_name"],
                email=row["email"],
                last_seen_roles=roles,
                last_claim_snapshot={"legacy_profile_backfill": table_name},
                auth_source="legacy_profile_backfill",
                is_dev_auth=False,
            )
            .on_conflict_do_update(
                index_elements=["actor_id"],
                set_={
                    "external_subject": row["external_subject"],
                    "external_issuer": row["external_issuer"],
                    "display_name": row["display_name"],
                    "email": row["email"],
                    "last_seen_roles": roles,
                    "last_claim_snapshot": {"legacy_profile_backfill": table_name},
                    "auth_source": "legacy_profile_backfill",
                    "is_dev_auth": False,
                    "last_seen_at": sa.func.now(),
                    "updated_at": sa.func.now(),
                },
            )
        )
        connection.execute(
            postgresql.insert(actor_profiles_table)
            .values(
                id=row["id"],
                actor_id=row["actor_id"],
                profile_type=profile_type,
                status=row["status"],
                skill_tags=row["skill_tags"] or [],
                scope_type="global",
                scope_id="global",
                profile_metadata={"legacy_profile_backfill": table_name},
            )
            .on_conflict_do_update(
                index_elements=["actor_id", "profile_type", "scope_type", "scope_id"],
                set_={
                    "status": row["status"],
                    "skill_tags": row["skill_tags"] or [],
                    "profile_metadata": {"legacy_profile_backfill": table_name},
                    "updated_at": sa.func.now(),
                },
            )
        )


def _restore_legacy_profiles(connection, table_name: str, profile_type: str) -> None:
    """Restore a legacy profile table from actor profile rows during downgrade."""
    legacy_profiles_table = _legacy_profile_table(table_name)
    rows = (
        connection.execute(
            sa.text(
                """
                select
                    p.id,
                    p.actor_id,
                    i.external_subject,
                    i.external_issuer,
                    i.display_name,
                    i.email,
                    p.skill_tags,
                    p.status
                from actor_profiles p
                join actor_identities i on i.actor_id = p.actor_id
                where p.profile_type = :profile_type
                  and p.scope_type = 'global'
                  and p.scope_id = 'global'
                """
            ),
            {"profile_type": profile_type},
        )
        .mappings()
        .all()
    )
    for row in rows:
        connection.execute(
            sa.insert(legacy_profiles_table).values(
                id=row["id"] or str(uuid4()),
                actor_id=row["actor_id"],
                external_subject=row["external_subject"],
                external_issuer=row["external_issuer"],
                display_name=row["display_name"],
                email=row["email"],
                skill_tags=row["skill_tags"] or [],
                status=row["status"],
            )
        )


def _legacy_profile_table(table_name: str) -> sa.TableClause:
    """Return a typed table clause for restored legacy profile rows."""
    return sa.table(
        table_name,
        sa.column("id", sa.String),
        sa.column("actor_id", sa.String),
        sa.column("external_subject", sa.String),
        sa.column("external_issuer", sa.String),
        sa.column("display_name", sa.String),
        sa.column("email", sa.String),
        sa.column("skill_tags", sa.JSON),
        sa.column("status", sa.String),
    )
