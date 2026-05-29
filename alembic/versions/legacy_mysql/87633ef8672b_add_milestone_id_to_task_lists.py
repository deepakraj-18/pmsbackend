"""add_milestone_id_to_task_lists

Revision ID: 87633ef8672b
Revises: d4e5f6g7h8i9
Create Date: 2026-05-04 16:30:07.770944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '87633ef8672b'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add milestone_id column to task_lists table."""
    op.add_column('task_lists', sa.Column('milestone_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_task_lists_milestone_id',
        'task_lists', 'milestones',
        ['milestone_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Remove milestone_id column from task_lists table."""
    op.drop_constraint('fk_task_lists_milestone_id', 'task_lists', type_='foreignkey')
    op.drop_column('task_lists', 'milestone_id')
