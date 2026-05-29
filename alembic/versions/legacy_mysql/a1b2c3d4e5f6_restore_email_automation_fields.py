"""restore email automation fields: is_processed, previous_status_id across all tables

Revision ID: a1b2c3d4e5f6
Revises: 9fa8e2abf1d4
Create Date: 2026-04-20

Restores:
  - tasks.previous_status_id         (FK → master_lookups, nullable)
  - issues.previous_status_id        (FK → master_lookups, nullable)
  - milestones.previous_status       (VARCHAR 100, nullable)
  - projects.previous_status         (VARCHAR 50, nullable)
  - project_members.is_processed     (BOOLEAN, default False)
  - project_members.previous_invitation_status (VARCHAR 50, nullable)
  - timelogs.is_processed            (BOOLEAN, default False)
  - timelogs.previous_approval_status (VARCHAR 50, nullable)

All fields are used by the email-automation worker to detect status
transitions (previous_status* → current status) and to track whether a
notification has been dispatched (is_processed=False → pending,
is_processed=True → done).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = ("9fa8e2abf1d4", "bb2987b8b2d1")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tasks ──────────────────────────────────────────────────────────────
    # previous_status_id: tracks status before last update  (FK → master_lookups)
    op.add_column(
        "tasks",
        sa.Column("previous_status_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_tasks_previous_status_id",
        "tasks",
        "master_lookups",
        ["previous_status_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ── issues ─────────────────────────────────────────────────────────────
    op.add_column(
        "issues",
        sa.Column("previous_status_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_issues_previous_status_id",
        "issues",
        "master_lookups",
        ["previous_status_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ── milestones ──────────────────────────────────────────────────────────
    # Milestone status is a plain VARCHAR string (no lookup table)
    op.add_column(
        "milestones",
        sa.Column("previous_status", sa.String(length=100), nullable=True),
    )

    # ── projects ────────────────────────────────────────────────────────────
    # Project status is a plain VARCHAR string
    op.add_column(
        "projects",
        sa.Column("previous_status", sa.String(length=50), nullable=True),
    )

    # ── project_members ─────────────────────────────────────────────────────
    op.add_column(
        "project_members",
        sa.Column(
            "is_processed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "project_members",
        sa.Column("previous_invitation_status", sa.String(length=50), nullable=True),
    )

    # ── timelogs ────────────────────────────────────────────────────────────
    op.add_column(
        "timelogs",
        sa.Column(
            "is_processed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "timelogs",
        sa.Column("previous_approval_status", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    # timelogs
    op.drop_column("timelogs", "previous_approval_status")
    op.drop_column("timelogs", "is_processed")

    # project_members
    op.drop_column("project_members", "previous_invitation_status")
    op.drop_column("project_members", "is_processed")

    # projects
    op.drop_column("projects", "previous_status")

    # milestones
    op.drop_column("milestones", "previous_status")

    # issues
    op.drop_constraint("fk_issues_previous_status_id", "issues", type_="foreignkey")
    op.drop_column("issues", "previous_status_id")

    # tasks
    op.drop_constraint("fk_tasks_previous_status_id", "tasks", type_="foreignkey")
    op.drop_column("tasks", "previous_status_id")
