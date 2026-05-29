
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '56d7b87c646b'
down_revision: Union[str, Sequence[str], None] = '0e90db353fcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass
def downgrade() -> None:

    op.create_table('audit_logs',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.VARCHAR(length=255), nullable=False, comment='Microsoft OID of the acting user'),
    sa.Column('action_type', mysql.VARCHAR(length=50), nullable=False, comment='CREATE | UPDATE | DELETE | ASSIGN'),
    sa.Column('resource_name', mysql.VARCHAR(length=100), nullable=False, comment='e.g. tasks, projects, milestones'),
    sa.Column('resource_id', mysql.INTEGER(), autoincrement=False, nullable=False, comment='Project-level context ID for filtering'),
    sa.Column('record_id', mysql.INTEGER(), autoincrement=False, nullable=False, comment='The specific item ID that was acted on'),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource'), 'audit_logs', ['resource_name', 'resource_id'], unique=False)
    op.create_table('audit_details',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('audit_log_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('field_name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False),
    sa.Column('old_value', mysql.TEXT(), nullable=True),
    sa.Column('new_value', mysql.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['audit_log_id'], ['audit_logs.id'], name=op.f('audit_details_ibfk_1'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('AuditLogDetails')
    op.drop_table('AuditMetaDataInfo')
    op.drop_table('AuditLogs')
    op.drop_table('AuditFieldsMapping')
