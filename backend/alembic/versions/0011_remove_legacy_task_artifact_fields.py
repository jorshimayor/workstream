"""remove legacy task artifact requirement fields

Revision ID: 0011_task_artifact_cleanup
Revises: 0010_guide_cleanup
Create Date: 2026-07-05
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0011_task_artifact_cleanup"
down_revision = "0010_guide_cleanup"
branch_labels = None
depends_on = None


LEGACY_TASK_ARTIFACT_COLUMNS = ("required_files", "required_evidence")


def upgrade() -> None:
    """Remove task-owned artifact requirement fields."""
    for column_name in LEGACY_TASK_ARTIFACT_COLUMNS:
        op.drop_column("workstream_tasks", column_name)


def downgrade() -> None:
    """Restore the previous construction-state task artifact columns."""
    op.add_column(
        "workstream_tasks",
        sa.Column("required_files", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "workstream_tasks",
        sa.Column("required_evidence", sa.JSON(), nullable=False, server_default="[]"),
    )
