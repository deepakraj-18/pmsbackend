"""restore id-based automation fields: status_id, priority_id, previous_status_id for projects, milestones and issues

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-20

Restores foreign keys to master_lookups for status and priority management.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ── projects ────────────────────────────────────────────────────────────
    op.add_column("projects", sa.Column("status_id", sa.Integer(), nullable=True))
    op.add_column("projects", sa.Column("priority_id", sa.Integer(), nullable=True))
    op.add_column("projects", sa.Column("previous_status_id", sa.Integer(), nullable=True))
    
    op.create_foreign_key("fk_projects_status_id", "projects", "master_lookups", ["status_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_projects_priority_id", "projects", "master_lookups", ["priority_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_projects_previous_status_id", "projects", "master_lookups", ["previous_status_id"], ["id"], ondelete="SET NULL")

    # ── milestones ──────────────────────────────────────────────────────────
    op.add_column("milestones", sa.Column("status_id", sa.Integer(), nullable=True))
    op.add_column("milestones", sa.Column("priority_id", sa.Integer(), nullable=True))
    op.add_column("milestones", sa.Column("previous_status_id", sa.Integer(), nullable=True))
    
    op.create_foreign_key("fk_milestones_status_id", "milestones", "master_lookups", ["status_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_milestones_priority_id", "milestones", "master_lookups", ["priority_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_milestones_previous_status_id", "milestones", "master_lookups", ["previous_status_id"], ["id"], ondelete="SET NULL")

    # ── issues ─────────────────────────────────────────────────────────────
    # priority_id was missing in previous Turn's checks
    op.add_column("issues", sa.Column("priority_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_issues_priority_id", "issues", "master_lookups", ["priority_id"], ["id"], ondelete="SET NULL")

def downgrade() -> None:
    # issues
    op.drop_constraint("fk_issues_priority_id", "issues", type_="foreignkey")
    op.drop_column("issues", "priority_id")

    # milestones
    op.drop_constraint("fk_milestones_previous_status_id", "milestones", type_="foreignkey")
    op.drop_constraint("fk_milestones_priority_id", "milestones", type_="foreignkey")
    op.drop_constraint("fk_milestones_status_id", "milestones", type_="foreignkey")
    op.drop_column("milestones", "previous_status_id")
    op.drop_column("milestones", "priority_id")
    op.drop_column("milestones", "status_id")

    # projects
    op.drop_constraint("fk_projects_previous_status_id", "projects", type_="foreignkey")
    op.drop_constraint("fk_projects_priority_id", "projects", type_="foreignkey")
    op.drop_constraint("fk_projects_status_id", "projects", type_="foreignkey")
    op.drop_column("projects", "previous_status_id")
    op.drop_column("projects", "priority_id")
    op.drop_column("projects", "status_id")
