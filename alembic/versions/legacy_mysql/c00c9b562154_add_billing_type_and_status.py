
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = 'c00c9b562154'
down_revision: Union[str, Sequence[str], None] = 'd81878d4a890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('project_templates', sa.Column('billing_type', sa.String(length=50), nullable=True))
    op.add_column('project_templates', sa.Column('status', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('project_templates', 'status')
    op.drop_column('project_templates', 'billing_type')
