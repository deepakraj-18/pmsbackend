
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'f87e61035b2d'
down_revision: Union[str, Sequence[str], None] = '0db83d72b373'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.drop_table('automation_logs')
    op.drop_table('automation_rules')
    op.drop_table('email_templates')
    op.add_column('issues', sa.Column('is_processed', sa.Boolean(), nullable=True))
    op.add_column('milestones', sa.Column('is_processed', sa.Boolean(), nullable=True))
    op.add_column('project_users', sa.Column('is_processed', sa.Boolean(), nullable=True))
    op.add_column('projects', sa.Column('is_processed', sa.Boolean(), nullable=True))
    op.add_column('tasks', sa.Column('is_processed', sa.Boolean(), nullable=True))

def downgrade() -> None:

    op.drop_column('tasks', 'is_processed')
    op.drop_column('projects', 'is_processed')
    op.drop_column('project_users', 'is_processed')
    op.drop_column('milestones', 'is_processed')
    op.drop_column('issues', 'is_processed')
    op.create_table('automation_logs',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('rule_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('execution_status', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('error_message', mysql.TEXT(), nullable=True),
    sa.Column('idempotency_key', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('triggered_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=True),
    sa.Column('completed_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['automation_rules.id'], name=op.f('automation_logs_ibfk_1'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_automation_logs_rule_id'), 'automation_logs', ['rule_id'], unique=False)
    op.create_index(op.f('ix_automation_logs_idempotency_key'), 'automation_logs', ['idempotency_key'], unique=True)
    op.create_index(op.f('ix_automation_logs_id'), 'automation_logs', ['id'], unique=False)
    op.create_table('automation_rules',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('tenant_id', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('trigger_event', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('conditions_json', mysql.JSON(), nullable=True),
    sa.Column('template_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['template_id'], ['email_templates.id'], name=op.f('automation_rules_ibfk_1'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_automation_rules_trigger_event'), 'automation_rules', ['trigger_event'], unique=False)
    op.create_index(op.f('ix_automation_rules_tenant_id'), 'automation_rules', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_automation_rules_template_id'), 'automation_rules', ['template_id'], unique=False)
    op.create_index(op.f('ix_automation_rules_id'), 'automation_rules', ['id'], unique=False)
    op.create_table('email_templates',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('tenant_id', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('subject', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('body_html', mysql.TEXT(), nullable=False),
    sa.Column('body_text', mysql.TEXT(), nullable=True),
    sa.Column('variables_schema', mysql.JSON(), nullable=True),
    sa.Column('version', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_email_templates_tenant_id'), 'email_templates', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_email_templates_id'), 'email_templates', ['id'], unique=False)
