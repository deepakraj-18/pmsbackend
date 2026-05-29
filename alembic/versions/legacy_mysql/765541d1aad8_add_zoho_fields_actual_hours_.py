
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '765541d1aad8'
down_revision: Union[str, Sequence[str], None] = '56d7b87c646b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.add_column('issues', sa.Column('classification', sa.String(length=50), nullable=True))

    op.add_column('projects', sa.Column('actual_start_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('actual_end_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('actual_hours', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('projects', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('0')))

    op.add_column('tasks', sa.Column('actual_hours', sa.Numeric(precision=5, scale=2), nullable=True))

def downgrade() -> None:

    op.drop_column('tasks', 'actual_hours')
    op.drop_column('projects', 'is_archived')
    op.drop_column('projects', 'actual_hours')
    op.drop_column('projects', 'actual_end_date')
    op.drop_column('projects', 'actual_start_date')
    op.drop_column('issues', 'classification')
