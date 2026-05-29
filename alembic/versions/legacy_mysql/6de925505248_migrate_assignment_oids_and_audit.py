
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '6de925505248'
down_revision: Union[str, Sequence[str], None] = '5e52bba644e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.add_column('audit_details', sa.Column('old_value', sa.Text(), nullable=True))
    op.add_column('audit_details', sa.Column('new_value', sa.Text(), nullable=True))
    op.drop_column('audit_details', 'old_state')
    op.drop_column('audit_details', 'new_state')
    op.add_column('project_users', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    op.add_column('project_users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.alter_column('project_users', 'user_id',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False)
    op.drop_constraint(op.f('project_users_ibfk_2'), 'project_users', type_='foreignkey')
    op.create_foreign_key(None, 'project_users', 'users', ['user_id'], ['o365_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'project_users', 'roles', ['role_id'], ['id'], ondelete='SET NULL')
    op.add_column('user_team_link', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    op.alter_column('user_team_link', 'user_id',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False)
    op.drop_constraint(op.f('user_team_link_ibfk_2'), 'user_team_link', type_='foreignkey')
    op.create_foreign_key(None, 'user_team_link', 'users', ['user_id'], ['o365_id'], ondelete='CASCADE')

def downgrade() -> None:

    op.drop_constraint(None, 'user_team_link', type_='foreignkey')
    op.create_foreign_key(op.f('user_team_link_ibfk_2'), 'user_team_link', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('user_team_link', 'user_id',
               existing_type=sa.String(length=255),
               type_=mysql.INTEGER(),
               existing_nullable=False)
    op.drop_column('user_team_link', 'id')
    op.drop_constraint(None, 'project_users', type_='foreignkey')
    op.drop_constraint(None, 'project_users', type_='foreignkey')
    op.create_foreign_key(op.f('project_users_ibfk_2'), 'project_users', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.alter_column('project_users', 'user_id',
               existing_type=sa.String(length=255),
               type_=mysql.INTEGER(),
               existing_nullable=False)
    op.drop_column('project_users', 'role_id')
    op.drop_column('project_users', 'id')
    op.add_column('audit_details', sa.Column('new_state', mysql.TEXT(), nullable=True))
    op.add_column('audit_details', sa.Column('old_state', mysql.TEXT(), nullable=True))
    op.drop_column('audit_details', 'new_value')
    op.drop_column('audit_details', 'old_value')
