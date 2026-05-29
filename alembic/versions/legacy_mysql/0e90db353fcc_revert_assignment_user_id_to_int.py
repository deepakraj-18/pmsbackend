
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '0e90db353fcc'
down_revision: Union[str, Sequence[str], None] = '6de925505248'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.create_foreign_key(None, 'project_users', 'roles', ['role_id'], ['id'], ondelete='SET NULL')
    op.drop_column('projects', 'previous_status')
    op.add_column('user_team_link', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))

def downgrade() -> None:

    op.drop_column('user_team_link', 'id')
    op.add_column('projects', sa.Column('previous_status', mysql.VARCHAR(length=100), nullable=True))
    op.drop_constraint(None, 'project_users', type_='foreignkey')
