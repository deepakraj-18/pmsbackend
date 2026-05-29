
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = 'd81878d4a890'
down_revision: Union[str, Sequence[str], None] = '600d5fb359dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column('projects', sa.Column('tags', sa.String(length=500), nullable=True))
    op.add_column('projects', sa.Column('ms_teams_group_id', sa.String(length=255), nullable=True))
    op.add_column('projects', sa.Column('ms_teams_channel_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_projects_ms_teams_group_id'), 'projects', ['ms_teams_group_id'], unique=False)
    

    op.add_column('project_members', sa.Column('role_in_project', sa.String(length=100), nullable=True))
    op.add_column('project_members', sa.Column('invitation_status', sa.String(length=50), server_default='Accepted', nullable=False))
    op.add_column('project_members', sa.Column('is_owner', sa.Boolean(), server_default='0', nullable=False))
    

    op.add_column('issues', sa.Column('flag', sa.String(length=50), nullable=True))
    op.add_column('issues', sa.Column('last_modified_time', sa.DateTime(), nullable=True))
    

    op.add_column('tasks', sa.Column('milestone_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tasks', 'milestones', ['milestone_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:

    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'milestone_id')
    

    op.drop_column('issues', 'last_modified_time')
    op.drop_column('issues', 'flag')
    

    op.drop_column('project_members', 'is_owner')
    op.drop_column('project_members', 'invitation_status')
    op.drop_column('project_members', 'role_in_project')
    

    op.drop_index(op.f('ix_projects_ms_teams_group_id'), table_name='projects')
    op.drop_column('projects', 'ms_teams_channel_id')
    op.drop_column('projects', 'ms_teams_group_id')
    op.drop_column('projects', 'tags')
