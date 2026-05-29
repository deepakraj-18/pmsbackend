"""drop deprecated varchar automation fields across all tables

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-04-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6g7h8i9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6g7h8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ── projects ────────────────────────────────────────────────────────────
    op.drop_column("projects", "status")
    op.drop_column("projects", "priority")
    op.drop_column("projects", "previous_status")

    # ── milestones ──────────────────────────────────────────────────────────
    op.drop_column("milestones", "status")
    op.drop_column("milestones", "priority")
    op.drop_column("milestones", "previous_status")

    # ── tasks ──────────────────────────────────────────────────────────────
    op.drop_column("tasks", "status")
    op.drop_column("tasks", "priority")
    op.drop_column("tasks", "previous_status")

    # ── issues ─────────────────────────────────────────────────────────────
    op.drop_column("issues", "status")
    op.drop_column("issues", "priority")
    op.drop_column("issues", "previous_status")
    op.drop_column("issues", "severity")
    op.drop_column("issues", "classification")

    # ── timelogs ────────────────────────────────────────────────────────────
    op.add_column("timelogs", sa.Column("approval_status_id", sa.Integer(), nullable=True))
    op.add_column("timelogs", sa.Column("previous_approval_status_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_timelogs_approval_status_id", "timelogs", "master_lookups", ["approval_status_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_timelogs_prev_approval_status_id", "timelogs", "master_lookups", ["previous_approval_status_id"], ["id"], ondelete="SET NULL")
    
    op.drop_column("timelogs", "approval_status")
    op.drop_column("timelogs", "previous_approval_status")

    # ── project_members ─────────────────────────────────────────────────────
    op.add_column("project_members", sa.Column("invitation_status_id", sa.Integer(), nullable=True))
    op.add_column("project_members", sa.Column("previous_invitation_status_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_project_members_inv_status_id", "project_members", "master_lookups", ["invitation_status_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_project_members_prev_inv_status_id", "project_members", "master_lookups", ["previous_invitation_status_id"], ["id"], ondelete="SET NULL")

    op.drop_column("project_members", "invitation_status")
    op.drop_column("project_members", "previous_invitation_status")

def downgrade() -> None:
    # This is complex to restore correctly with original default values, skipping for now as it's a cleanup migration.
    pass
