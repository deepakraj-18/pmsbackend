
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'bb2987b8b2d1'
down_revision: Union[str, Sequence[str], None] = 'e161d777bea1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column('project_templates', sa.Column('is_public', sa.Boolean(), nullable=False, server_default='1'))
    op.drop_column('project_templates', 'status')


    op.add_column('template_tasks', sa.Column('duration',     sa.Integer(),     nullable=True))
    op.add_column('template_tasks', sa.Column('billing_type', sa.String(50),    nullable=True))
    op.add_column('template_tasks', sa.Column('tags',         sa.String(500),   nullable=True))
    op.alter_column('template_tasks', 'estimated_hours',
                    existing_type=mysql.DECIMAL(precision=5, scale=2),
                    type_=sa.Numeric(precision=10, scale=2),
                    existing_nullable=True)


    try:
        op.drop_constraint('template_tasks_ibfk_2', 'template_tasks', type_='foreignkey')
    except Exception:
        pass

    op.drop_column('template_tasks', 'priority_id')


def downgrade() -> None:
    op.add_column('template_tasks', sa.Column('priority_id', mysql.INTEGER(), nullable=True))
    op.alter_column('template_tasks', 'estimated_hours',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    type_=mysql.DECIMAL(precision=5, scale=2),
                    existing_nullable=True)
    op.drop_column('template_tasks', 'tags')
    op.drop_column('template_tasks', 'billing_type')
    op.drop_column('template_tasks', 'duration')
    op.add_column('project_templates', sa.Column('status', mysql.VARCHAR(length=50), nullable=True))
    op.drop_column('project_templates', 'is_public')
