
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '1df14cd0c9cd'
down_revision: Union[str, Sequence[str], None] = 'ee0d195e78dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    
    def column_exists(table, column):
        columns = [c['name'] for c in insp.get_columns(table)]
        return column in columns

    def table_exists(table):
        return table in insp.get_table_names()

    if not table_exists('project_groups'):
        op.create_table('project_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_project_groups_id'), 'project_groups', ['id'], unique=False)
        op.create_index(op.f('ix_project_groups_name'), 'project_groups', ['name'], unique=True)
    
    if not column_exists('projects', 'is_template'):
        op.add_column('projects', sa.Column('is_template', sa.Boolean(), nullable=True))
    if not column_exists('projects', 'is_archived'):
        op.add_column('projects', sa.Column('is_archived', sa.Boolean(), nullable=True))
    if not column_exists('projects', 'group_id'):
        op.add_column('projects', sa.Column('group_id', sa.Integer(), nullable=True))
        op.create_foreign_key(None, 'projects', 'project_groups', ['group_id'], ['id'], ondelete='SET NULL')
        
    if not column_exists('users', 'o365_id'):
        op.add_column('users', sa.Column('o365_id', sa.String(length=255), nullable=True))
        op.create_index(op.f('ix_users_o365_id'), 'users', ['o365_id'], unique=True)
    if not column_exists('users', 'is_synced'):
        op.add_column('users', sa.Column('is_synced', sa.Boolean(), nullable=True))
    if not column_exists('users', 'is_external'):
        op.add_column('users', sa.Column('is_external', sa.Boolean(), nullable=True))


def downgrade() -> None:

    op.drop_index(op.f('ix_users_o365_id'), table_name='users')
    op.drop_column('users', 'is_external')
    op.drop_column('users', 'is_synced')
    op.drop_column('users', 'o365_id')
    op.drop_constraint(None, 'projects', type_='foreignkey')
    op.drop_column('projects', 'group_id')
    op.drop_column('projects', 'is_archived')
    op.drop_column('projects', 'is_template')
    op.drop_index(op.f('ix_project_groups_name'), table_name='project_groups')
    op.drop_index(op.f('ix_project_groups_id'), table_name='project_groups')
    op.drop_table('project_groups')
