
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20f93f74c3ae'
down_revision: Union[str, Sequence[str], None] = '1df14cd0c9cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.add_column('users', sa.Column('display_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('state', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('language', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(length=100), nullable=True))

def downgrade() -> None:

    op.drop_column('users', 'timezone')
    op.drop_column('users', 'language')
    op.drop_column('users', 'state')
    op.drop_column('users', 'country')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'display_name')
