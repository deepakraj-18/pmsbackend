"""Convert billing_model and project_type to String

Revision ID: 60b8b5752aba
Revises: 87633ef8672b
Create Date: 2026-05-06 12:17:22.960162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '60b8b5752aba'
down_revision: Union[str, Sequence[str], None] = '87633ef8672b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('projects', 'billing_model',
               existing_type=mysql.ENUM('TM', 'FIXED', 'MILESTONE'),
               type_=sa.String(length=100),
               existing_nullable=False)
    op.alter_column('projects', 'project_type',
               existing_type=mysql.ENUM('INTERNAL', 'EXTERNAL'),
               type_=sa.String(length=100),
               existing_nullable=False)

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('projects', 'project_type',
               existing_type=sa.String(length=100),
               type_=mysql.ENUM('INTERNAL', 'EXTERNAL'),
               existing_nullable=False)
    op.alter_column('projects', 'billing_model',
               existing_type=sa.String(length=100),
               type_=mysql.ENUM('TM', 'FIXED', 'MILESTONE'),
               existing_nullable=False)

