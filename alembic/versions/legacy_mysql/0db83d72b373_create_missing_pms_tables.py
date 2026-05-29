
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0db83d72b373'
down_revision: Union[str, Sequence[str], None] = 'ea2828384a3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.create_table('automation_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.String(length=50), nullable=True),
    sa.Column('trigger_event', sa.String(length=100), nullable=False),
    sa.Column('conditions_json', sa.JSON(), nullable=True),
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['template_id'], ['email_templates.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_automation_rules_id'), 'automation_rules', ['id'], unique=False)
    op.create_index(op.f('ix_automation_rules_template_id'), 'automation_rules', ['template_id'], unique=False)
    op.create_index(op.f('ix_automation_rules_tenant_id'), 'automation_rules', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_automation_rules_trigger_event'), 'automation_rules', ['trigger_event'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=False),
    sa.Column('employee_id', sa.String(length=50), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('job_title', sa.String(length=100), nullable=True),
    sa.Column('join_date', sa.Date(), nullable=True),
    sa.Column('password_hash', sa.String(length=255), nullable=True),
    sa.Column('display_name', sa.String(length=100), nullable=True),
    sa.Column('gender', sa.String(length=20), nullable=True),
    sa.Column('country', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('language', sa.String(length=50), nullable=True),
    sa.Column('timezone', sa.String(length=100), nullable=True),
    sa.Column('o365_id', sa.String(length=255), nullable=True),
    sa.Column('is_synced', sa.Boolean(), nullable=True),
    sa.Column('is_external', sa.Boolean(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('dept_id', sa.Integer(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.Column('manager_email', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['dept_id'], ['departments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['manager_email'], ['users.email'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['status_id'], ['user_statuses.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email', name='uq_user_email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_employee_id'), 'users', ['employee_id'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_o365_id'), 'users', ['o365_id'], unique=True)
    op.create_index(op.f('ix_users_public_id'), 'users', ['public_id'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('automation_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rule_id', sa.Integer(), nullable=False),
    sa.Column('execution_status', sa.String(length=50), nullable=False),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('idempotency_key', sa.String(length=255), nullable=False),
    sa.Column('triggered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['automation_rules.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_automation_logs_id'), 'automation_logs', ['id'], unique=False)
    op.create_index(op.f('ix_automation_logs_idempotency_key'), 'automation_logs', ['idempotency_key'], unique=True)
    op.create_index(op.f('ix_automation_logs_rule_id'), 'automation_logs', ['rule_id'], unique=False)
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('client', sa.String(length=255), nullable=True),
    sa.Column('manager_email', sa.String(length=255), nullable=True),
    sa.Column('created_by_email', sa.String(length=255), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.Column('priority_id', sa.Integer(), nullable=True),
    sa.Column('previous_status', sa.String(length=100), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('budget', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_email'], ['users.email'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['manager_email'], ['users.email'], ),
    sa.ForeignKeyConstraint(['priority_id'], ['priorities.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['statuses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_public_id'), 'projects', ['public_id'], unique=True)
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('team_email', sa.String(length=255), nullable=False),
    sa.Column('budget_allocation', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('team_type', sa.String(length=50), nullable=True),
    sa.Column('max_team_size', sa.Integer(), nullable=True),
    sa.Column('primary_communication_channel', sa.String(length=100), nullable=True),
    sa.Column('channel_id', sa.String(length=100), nullable=True),
    sa.Column('lead_email', sa.String(length=255), nullable=True),
    sa.Column('dept_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dept_id'], ['departments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['lead_email'], ['users.email'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=False)
    op.create_index(op.f('ix_teams_public_id'), 'teams', ['public_id'], unique=True)
    op.create_index(op.f('ix_teams_team_email'), 'teams', ['team_email'], unique=True)
    op.create_table('user_skill_link',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'skill_id')
    )
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('file_url', sa.String(length=1024), nullable=False),
    sa.Column('file_type', sa.String(length=100), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('uploaded_by_email', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['uploaded_by_email'], ['users.email'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_public_id'), 'documents', ['public_id'], unique=True)
    op.create_table('issues',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('reporter_email', sa.String(length=255), nullable=True),
    sa.Column('assignee_email', sa.String(length=255), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.Column('priority_id', sa.Integer(), nullable=True),
    sa.Column('previous_status', sa.String(length=100), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('estimated_hours', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['assignee_email'], ['users.email'], ),
    sa.ForeignKeyConstraint(['priority_id'], ['priorities.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['reporter_email'], ['users.email'], ),
    sa.ForeignKeyConstraint(['status_id'], ['statuses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_issues_id'), 'issues', ['id'], unique=False)
    op.create_index(op.f('ix_issues_public_id'), 'issues', ['public_id'], unique=True)
    op.create_index(op.f('ix_issues_title'), 'issues', ['title'], unique=False)
    op.create_table('milestones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.Column('owner_email', sa.String(length=255), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['owner_email'], ['users.email'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['statuses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_milestones_id'), 'milestones', ['id'], unique=False)
    op.create_index(op.f('ix_milestones_public_id'), 'milestones', ['public_id'], unique=True)
    op.create_index(op.f('ix_milestones_title'), 'milestones', ['title'], unique=False)
    op.create_table('project_users',
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('project_id', 'user_id')
    )
    op.create_table('task_lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_lists_id'), 'task_lists', ['id'], unique=False)
    op.create_index(op.f('ix_task_lists_name'), 'task_lists', ['name'], unique=False)
    op.create_table('timesheets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(length=255), nullable=False),
    sa.Column('billing_type', sa.String(length=50), nullable=True),
    sa.Column('total_hours', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('approval_status', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['user_email'], ['users.email'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timesheets_id'), 'timesheets', ['id'], unique=False)
    op.create_table('user_team_link',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'team_id')
    )
    op.create_table('issue_document_link',
    sa.Column('issue_id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('issue_id', 'document_id')
    )
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('task_list_id', sa.Integer(), nullable=True),
    sa.Column('assignee_email', sa.String(length=255), nullable=True),
    sa.Column('created_by_email', sa.String(length=255), nullable=True),
    sa.Column('status_id', sa.Integer(), nullable=True),
    sa.Column('priority_id', sa.Integer(), nullable=True),
    sa.Column('previous_status', sa.String(length=100), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('progress', sa.Integer(), nullable=True),
    sa.Column('estimated_hours', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['assignee_email'], ['users.email'], ),
    sa.ForeignKeyConstraint(['created_by_email'], ['users.email'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['priority_id'], ['priorities.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['statuses.id'], ),
    sa.ForeignKeyConstraint(['task_list_id'], ['task_lists.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_public_id'), 'tasks', ['public_id'], unique=True)
    op.create_index(op.f('ix_tasks_title'), 'tasks', ['title'], unique=False)
    op.create_table('timelogs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(length=255), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('issue_id', sa.Integer(), nullable=True),
    sa.Column('timesheet_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('hours', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('log_title', sa.String(length=255), nullable=True),
    sa.Column('billing_type', sa.String(length=50), nullable=True),
    sa.Column('approval_status', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
    sa.ForeignKeyConstraint(['timesheet_id'], ['timesheets.id'], name='fk_timelog_timesheet'),
    sa.ForeignKeyConstraint(['user_email'], ['users.email'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timelogs_id'), 'timelogs', ['id'], unique=False)

def downgrade() -> None:

    op.drop_index(op.f('ix_timelogs_id'), table_name='timelogs')
    op.drop_table('timelogs')
    op.drop_index(op.f('ix_tasks_title'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_public_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_table('issue_document_link')
    op.drop_table('user_team_link')
    op.drop_index(op.f('ix_timesheets_id'), table_name='timesheets')
    op.drop_table('timesheets')
    op.drop_index(op.f('ix_task_lists_name'), table_name='task_lists')
    op.drop_index(op.f('ix_task_lists_id'), table_name='task_lists')
    op.drop_table('task_lists')
    op.drop_table('project_users')
    op.drop_index(op.f('ix_milestones_title'), table_name='milestones')
    op.drop_index(op.f('ix_milestones_public_id'), table_name='milestones')
    op.drop_index(op.f('ix_milestones_id'), table_name='milestones')
    op.drop_table('milestones')
    op.drop_index(op.f('ix_issues_title'), table_name='issues')
    op.drop_index(op.f('ix_issues_public_id'), table_name='issues')
    op.drop_index(op.f('ix_issues_id'), table_name='issues')
    op.drop_table('issues')
    op.drop_index(op.f('ix_documents_public_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_table('user_skill_link')
    op.drop_index(op.f('ix_teams_team_email'), table_name='teams')
    op.drop_index(op.f('ix_teams_public_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_name'), table_name='teams')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')
    op.drop_index(op.f('ix_projects_public_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_automation_logs_rule_id'), table_name='automation_logs')
    op.drop_index(op.f('ix_automation_logs_idempotency_key'), table_name='automation_logs')
    op.drop_index(op.f('ix_automation_logs_id'), table_name='automation_logs')
    op.drop_table('automation_logs')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_public_id'), table_name='users')
    op.drop_index(op.f('ix_users_o365_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_employee_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_automation_rules_trigger_event'), table_name='automation_rules')
    op.drop_index(op.f('ix_automation_rules_tenant_id'), table_name='automation_rules')
    op.drop_index(op.f('ix_automation_rules_template_id'), table_name='automation_rules')
    op.drop_index(op.f('ix_automation_rules_id'), table_name='automation_rules')
    op.drop_table('automation_rules')
