
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'cfd418b1e5c4'
down_revision: Union[str, Sequence[str], None] = 'f87e61035b2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.add_column('projects', sa.Column('estimated_hours', sa.Numeric(precision=10, scale=2), nullable=True))
    op.drop_column('projects', 'budget')

def downgrade() -> None:

    op.add_column('projects', sa.Column('budget', mysql.DECIMAL(precision=10, scale=2), nullable=True))
    op.drop_column('projects', 'estimated_hours')
