
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '5e52bba644e7'
down_revision: Union[str, Sequence[str], None] = '99ca54d81b48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.add_column('project_users', sa.Column('user_email', sa.String(length=255), nullable=True))

def downgrade() -> None:

    op.drop_column('project_users', 'user_email')
