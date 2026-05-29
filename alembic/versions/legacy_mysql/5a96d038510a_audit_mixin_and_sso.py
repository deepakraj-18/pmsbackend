
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '5a96d038510a'
down_revision: Union[str, Sequence[str], None] = '20f93f74c3ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.add_column('projects', sa.Column('created_by', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('projects', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('projects', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('projects', sa.Column('is_deleted', sa.Boolean(), nullable=False))
    op.create_foreign_key(None, 'projects', 'users', ['created_by'], ['id'], ondelete='SET NULL')
    op.add_column('tasks', sa.Column('created_by', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('tasks', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('tasks', sa.Column('is_deleted', sa.Boolean(), nullable=False))
    op.create_foreign_key(None, 'tasks', 'users', ['created_by'], ['id'], ondelete='SET NULL')
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=False))

def downgrade() -> None:

    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'password_hash')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'is_deleted')
    op.drop_column('tasks', 'is_active')
    op.drop_column('tasks', 'updated_at')
    op.drop_column('tasks', 'created_at')
    op.drop_column('tasks', 'created_by')
    op.drop_constraint(None, 'projects', type_='foreignkey')
    op.drop_column('projects', 'is_deleted')
    op.drop_column('projects', 'is_active')
    op.drop_column('projects', 'updated_at')
    op.drop_column('projects', 'created_at')
    op.drop_column('projects', 'created_by')
