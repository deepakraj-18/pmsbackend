"""finalize automation schema: add missing string columns across all tables

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-04-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c3d4e5f6g7h8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6g7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ── tasks ──────────────────────────────────────────────────────────────
    op.add_column("tasks", sa.Column("status", sa.String(length=50), nullable=True))
    op.add_column("tasks", sa.Column("priority", sa.String(length=20), nullable=True))
    op.add_column("tasks", sa.Column("previous_status", sa.String(length=100), nullable=True))

    # ── issues ─────────────────────────────────────────────────────────────
    op.add_column("issues", sa.Column("status", sa.String(length=50), nullable=True))
    op.add_column("issues", sa.Column("priority", sa.String(length=20), nullable=True))
    op.add_column("issues", sa.Column("previous_status", sa.String(length=100), nullable=True))
    op.add_column("issues", sa.Column("severity", sa.String(length=50), nullable=True))
    op.add_column("issues", sa.Column("classification", sa.String(length=100), nullable=True))

    # ── milestones ──────────────────────────────────────────────────────────
    op.add_column("milestones", sa.Column("priority", sa.String(length=100), nullable=True))

def downgrade() -> None:
    # milestones
    op.drop_column("milestones", "priority")

    # issues
    op.drop_column("issues", "classification")
    op.drop_column("issues", "severity")
    op.drop_column("issues", "previous_status")
    op.drop_column("issues", "priority")
    op.drop_column("issues", "status")

    # tasks
    op.drop_column("tasks", "previous_status")
    op.drop_column("tasks", "priority")
    op.drop_column("tasks", "status")
