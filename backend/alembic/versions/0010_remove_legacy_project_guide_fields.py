"""remove legacy project guide structured fields

Revision ID: 0010_guide_cleanup
Revises: 0009_evaluation_pending_status
Create Date: 2026-07-05
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0010_guide_cleanup"
down_revision = "0009_evaluation_pending_status"
branch_labels = None
depends_on = None


LEGACY_COLUMNS = (
    "required_task_fields",
    "required_submission_fields",
    "task_instructions",
    "output_requirements",
    "acceptance_criteria",
    "rejection_criteria",
    "reviewer_rubric",
    "forbidden_actions",
    "required_skills",
    "difficulty_scale",
    "estimated_time_policy",
    "common_rejection_reasons",
    "evidence_policy",
    "unacceptable_work_policy",
)


def _pre_cleanup_guide_snapshots_exist() -> bool:
    """Return whether setup snapshots exist before this destructive cleanup.

    This migration is intentionally safe only when no guide-source snapshots
    exist. Any guide-source snapshot captured before the guide-field cleanup
    must be rebuilt under the current content-markdown-only guide contract.
    """
    bind = op.get_bind()
    count = bind.scalar(sa.text("select count(*) from guide_source_snapshots"))
    return bool(count)


def upgrade() -> None:
    """Remove stale guide fields and project-owned payment duplicates."""
    if _pre_cleanup_guide_snapshots_exist():
        raise RuntimeError(
            "0010_guide_cleanup is safe only when no guide source snapshots exist; "
            "pre-cleanup guide source snapshots exist and must be recreated "
            "under the current content_markdown-only guide contract"
        )
    op.drop_column("projects", "base_amount")
    op.drop_column("projects", "currency")
    for column_name in LEGACY_COLUMNS:
        op.drop_column("project_guides", column_name)


def downgrade() -> None:
    """Restore the previous construction-state project and guide columns."""
    op.add_column(
        "projects",
        sa.Column("base_amount", sa.Numeric(12, 2), nullable=True),
    )
    op.add_column("projects", sa.Column("currency", sa.String(length=20), nullable=True))
    op.add_column(
        "project_guides",
        sa.Column("required_task_fields", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "project_guides",
        sa.Column("required_submission_fields", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column("project_guides", sa.Column("task_instructions", sa.Text(), nullable=True))
    op.add_column("project_guides", sa.Column("output_requirements", sa.Text(), nullable=True))
    op.add_column("project_guides", sa.Column("acceptance_criteria", sa.Text(), nullable=True))
    op.add_column("project_guides", sa.Column("rejection_criteria", sa.Text(), nullable=True))
    op.add_column("project_guides", sa.Column("reviewer_rubric", sa.Text(), nullable=True))
    op.add_column("project_guides", sa.Column("forbidden_actions", sa.Text(), nullable=True))
    op.add_column(
        "project_guides",
        sa.Column("required_skills", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "project_guides",
        sa.Column("difficulty_scale", sa.JSON(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "project_guides",
        sa.Column("estimated_time_policy", sa.JSON(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "project_guides",
        sa.Column("common_rejection_reasons", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column("project_guides", sa.Column("evidence_policy", sa.JSON(), nullable=True))
    op.add_column(
        "project_guides",
        sa.Column("unacceptable_work_policy", sa.Text(), nullable=True),
    )
