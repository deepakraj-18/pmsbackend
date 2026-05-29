
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '99ca54d81b48'
down_revision: Union[str, Sequence[str], None] = 'ba6c7bc54f35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.add_column('issue_document_link', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('issue_document_link', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('issue_document_link', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('issue_document_link', sa.Column('is_deleted', sa.Boolean(), nullable=False))
    op.add_column('project_users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('project_users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('project_users', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('project_users', sa.Column('is_deleted', sa.Boolean(), nullable=False))
    op.add_column('user_skill_link', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('user_skill_link', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user_skill_link', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('user_skill_link', sa.Column('is_deleted', sa.Boolean(), nullable=False))
    op.add_column('user_team_link', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('user_team_link', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user_team_link', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.add_column('user_team_link', sa.Column('is_deleted', sa.Boolean(), nullable=False))

def downgrade() -> None:

    op.drop_column('user_team_link', 'is_deleted')
    op.drop_column('user_team_link', 'is_active')
    op.drop_column('user_team_link', 'updated_at')
    op.drop_column('user_team_link', 'created_at')
    op.drop_column('user_skill_link', 'is_deleted')
    op.drop_column('user_skill_link', 'is_active')
    op.drop_column('user_skill_link', 'updated_at')
    op.drop_column('user_skill_link', 'created_at')
    op.drop_column('project_users', 'is_deleted')
    op.drop_column('project_users', 'is_active')
    op.drop_column('project_users', 'updated_at')
    op.drop_column('project_users', 'created_at')
    op.drop_column('issue_document_link', 'is_deleted')
    op.drop_column('issue_document_link', 'is_active')
    op.drop_column('issue_document_link', 'updated_at')
    op.drop_column('issue_document_link', 'created_at')
