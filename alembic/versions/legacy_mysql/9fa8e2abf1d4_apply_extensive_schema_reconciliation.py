
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = '9fa8e2abf1d4'
down_revision: Union[str, Sequence[str], None] = 'c00c9b562154'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    

    op.execute("SET FOREIGN_KEY_CHECKS=0")
    op.execute("DROP TABLE IF EXISTS auditlogdetails CASCADE")
    op.execute("DROP TABLE IF EXISTS auditfieldsmapping CASCADE")
    op.execute("DROP TABLE IF EXISTS auditmetadatainfo CASCADE")
    op.execute("DROP TABLE IF EXISTS auditlogs CASCADE")
    op.execute("DROP TABLE IF EXISTS project_users CASCADE")
    op.execute("DROP TABLE IF EXISTS timesheets CASCADE")
    op.execute("SET FOREIGN_KEY_CHECKS=1")
    op.create_table('AuditFieldsMapping',
    sa.Column('ID', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('EntityName', sa.String(length=150), nullable=False),
    sa.Column('FieldName', sa.String(length=150), nullable=False),
    sa.Column('DisplayName', sa.String(length=150), nullable=True),
    sa.Column('IsActive', sa.Boolean(), nullable=False),
    sa.Column('IsVisible', sa.Boolean(), nullable=True),
    sa.Column('OrderNo', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('ID')
    )
    op.create_table('AuditLogs',
    sa.Column('ID', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('TableName', sa.String(length=250), nullable=False),
    sa.Column('Action', sa.Integer(), nullable=False),
    sa.Column('PerformedBy', sa.Uuid(), nullable=False),
    sa.Column('PerformedOn', sa.DateTime(), nullable=False),
    sa.Column('RecordName', sa.String(length=500), nullable=True),
    sa.Column('TransactionId', sa.Uuid(), nullable=False),
    sa.Column('Comments', sa.Text(), nullable=True),
    sa.Column('ModuleName', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('ID')
    )
    op.create_table('AuditMetaDataInfo',
    sa.Column('Id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('File_name', sa.String(length=255), nullable=True),
    sa.Column('StartDate', sa.DateTime(), nullable=False),
    sa.Column('EndDate', sa.DateTime(), nullable=False),
    sa.Column('ModuleOrEntityName', sa.String(length=255), nullable=True),
    sa.Column('CreatedOn', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_table('AuditLogDetails',
    sa.Column('Id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('AuditLogId', sa.BigInteger(), nullable=False),
    sa.Column('FieldName', sa.String(length=250), nullable=False),
    sa.Column('OldValue', sa.Text(), nullable=True),
    sa.Column('NewValue', sa.Text(), nullable=True),
    sa.Column('ValueType', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['AuditLogId'], ['AuditLogs.ID'], ),
    sa.PrimaryKeyConstraint('Id')
    )
    op.drop_index(op.f('ix_departments_id'), table_name='departments')
    op.drop_index(op.f('ix_departments_name'), table_name='departments')
    try:
        op.drop_constraint(op.f('users_ibfk_1'), 'users', type_='foreignkey')
    except:
        pass
    op.drop_table('departments')
    op.drop_table('auditlogdetails')
    op.drop_index(op.f('uq_project_user'), table_name='project_users')
    op.drop_table('project_users')
    op.drop_table('auditfieldsmapping')
    op.drop_table('auditmetadatainfo')
    op.drop_table('auditlogs')
    op.drop_index(op.f('ix_timesheets_id'), table_name='timesheets')
    op.drop_table('timesheets')
    op.alter_column('issues', 'bug_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('issues', 'reproducible_flag',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.alter_column('issues', 'is_processed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.drop_index(op.f('ix_issues_id'), table_name='issues')
    op.drop_index(op.f('ix_issues_title'), table_name='issues')
    op.create_index(op.f('ix_issues_bug_name'), 'issues', ['bug_name'], unique=False)
    op.drop_constraint(op.f('issues_ibfk_3'), 'issues', type_='foreignkey')
    op.drop_constraint(op.f('issues_ibfk_5'), 'issues', type_='foreignkey')
    op.drop_constraint(op.f('issues_ibfk_4'), 'issues', type_='foreignkey')
    op.drop_constraint(op.f('issues_ibfk_1'), 'issues', type_='foreignkey')
    op.drop_constraint(op.f('issues_ibfk_2'), 'issues', type_='foreignkey')
    op.create_foreign_key(None, 'issues', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'issues', 'teams', ['associated_team_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'issues', 'users', ['reporter_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'issues', 'users', ['assignee_id'], ['id'], ondelete='SET NULL')
    op.drop_column('issues', 'end_date')
    op.drop_column('issues', 'title')
    op.drop_column('issues', 'reporter_email')
    op.drop_column('issues', 'assignee_email')
    op.drop_column('issues', 'priority_id')
    op.drop_column('issues', 'previous_status')
    op.drop_column('issues', 'status_id')
    op.alter_column('milestones', 'milestone_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('milestones', 'is_processed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.drop_index(op.f('ix_milestones_id'), table_name='milestones')
    op.drop_index(op.f('ix_milestones_title'), table_name='milestones')
    op.create_index(op.f('ix_milestones_milestone_name'), 'milestones', ['milestone_name'], unique=False)
    op.drop_constraint(op.f('milestones_ibfk_2'), 'milestones', type_='foreignkey')
    op.drop_constraint(op.f('milestones_ibfk_1'), 'milestones', type_='foreignkey')
    op.drop_constraint(op.f('milestones_ibfk_3'), 'milestones', type_='foreignkey')
    op.create_foreign_key(None, 'milestones', 'users', ['owner_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'milestones', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.drop_column('milestones', 'owner_email')
    op.drop_column('milestones', 'title')
    op.drop_column('milestones', 'status_id')
    op.alter_column('projects', 'project_id_sync',
               existing_type=mysql.VARCHAR(length=100),
               nullable=False)
    op.alter_column('projects', 'account_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('projects', 'project_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('projects', 'customer_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('projects', 'billing_model',
               existing_type=mysql.ENUM('TM', 'FIXED', 'MILESTONE'),
               nullable=False)
    op.alter_column('projects', 'project_type',
               existing_type=mysql.ENUM('INTERNAL', 'EXTERNAL'),
               nullable=False)
    op.alter_column('projects', 'status',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.alter_column('projects', 'priority',
               existing_type=mysql.VARCHAR(length=20),
               nullable=False)
    op.alter_column('projects', 'estimated_hours',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=False)
    op.alter_column('projects', 'actual_hours',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=False)
    op.alter_column('projects', 'is_template',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.alter_column('projects', 'is_group',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.alter_column('projects', 'is_processed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('project_id_sync'), table_name='projects')
    op.create_index(op.f('ix_projects_owner_id'), 'projects', ['owner_id'], unique=False)
    op.create_index(op.f('ix_projects_project_id_sync'), 'projects', ['project_id_sync'], unique=True)
    op.create_index(op.f('ix_projects_project_name'), 'projects', ['project_name'], unique=False)
    op.drop_constraint(op.f('projects_ibfk_4'), 'projects', type_='foreignkey')
    op.drop_constraint(op.f('fk_projects_prev_status'), 'projects', type_='foreignkey')
    op.drop_constraint(op.f('projects_ibfk_2'), 'projects', type_='foreignkey')
    op.drop_constraint(op.f('projects_ibfk_3'), 'projects', type_='foreignkey')
    op.drop_constraint(op.f('projects_ibfk_1'), 'projects', type_='foreignkey')
    op.create_foreign_key(None, 'projects', 'users', ['project_manager_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'projects', 'users', ['delivery_head_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'projects', 'project_templates', ['template_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'projects', 'users', ['owner_id'], ['id'], ondelete='SET NULL')
    op.drop_column('projects', 'manager_email')
    op.drop_column('projects', 'start_date')
    op.drop_column('projects', 'end_date')
    op.drop_column('projects', 'name')
    op.drop_column('projects', 'client')
    op.drop_column('projects', 'created_by_email')
    op.drop_column('projects', 'priority_id')
    op.drop_column('projects', 'previous_status')
    op.drop_column('projects', 'status_id')
    op.alter_column('tasks', 'task_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)
    op.alter_column('tasks', 'billing_type',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False,
               existing_server_default=sa.text("'Billable'"))
    op.alter_column('tasks', 'is_processed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_title'), table_name='tasks')
    op.create_index(op.f('ix_tasks_task_name'), 'tasks', ['task_name'], unique=False)
    op.drop_constraint(op.f('tasks_ibfk_2'), 'tasks', type_='foreignkey')
    op.drop_constraint(op.f('tasks_ibfk_5'), 'tasks', type_='foreignkey')
    op.drop_constraint(op.f('tasks_ibfk_1'), 'tasks', type_='foreignkey')
    op.drop_constraint(op.f('tasks_ibfk_3'), 'tasks', type_='foreignkey')
    op.drop_constraint(op.f('tasks_ibfk_4'), 'tasks', type_='foreignkey')
    op.create_foreign_key(None, 'tasks', 'users', ['owner_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'tasks', 'users', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'tasks', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'tasks', 'users', ['assignee_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'tasks', 'teams', ['associated_team_id'], ['id'], ondelete='SET NULL')
    op.drop_column('tasks', 'progress')
    op.drop_column('tasks', 'end_date')
    op.drop_column('tasks', 'title')
    op.drop_column('tasks', 'assignee_email')
    op.drop_column('tasks', 'created_by_email')
    op.drop_column('tasks', 'priority_id')
    op.drop_column('tasks', 'previous_status')
    op.drop_column('tasks', 'actual_hours')
    op.drop_column('tasks', 'status_id')
    op.drop_constraint(op.f('teams_ibfk_1'), 'teams', type_='foreignkey')
    op.drop_column('teams', 'dept_id')
    op.alter_column('timelogs', 'user_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.alter_column('timelogs', 'daily_log_hours',
               existing_type=mysql.DECIMAL(precision=5, scale=2),
               nullable=False)
    op.alter_column('timelogs', 'billing_type',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.alter_column('timelogs', 'approval_status',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.alter_column('timelogs', 'general_log',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    op.drop_index(op.f('ix_timelogs_id'), table_name='timelogs')
    op.drop_constraint(op.f('timelogs_ibfk_2'), 'timelogs', type_='foreignkey')
    op.drop_constraint(op.f('timelogs_ibfk_3'), 'timelogs', type_='foreignkey')
    op.drop_constraint(op.f('timelogs_ibfk_4'), 'timelogs', type_='foreignkey')
    op.drop_constraint(op.f('timelogs_ibfk_1'), 'timelogs', type_='foreignkey')
    op.create_foreign_key(None, 'timelogs', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'timelogs', 'users', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'timelogs', 'tasks', ['task_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'timelogs', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'timelogs', 'issues', ['issue_id'], ['id'], ondelete='CASCADE')
    op.drop_column('timelogs', 'description')
    op.drop_column('timelogs', 'user_email')
    op.drop_column('timelogs', 'hours')

    op.drop_column('users', 'dept_id')



def downgrade() -> None:
    

    op.add_column('users', sa.Column('dept_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('users_ibfk_1'), 'users', 'departments', ['dept_id'], ['id'], ondelete='SET NULL')
    op.add_column('timelogs', sa.Column('hours', mysql.DECIMAL(precision=5, scale=2), nullable=False))
    op.add_column('timelogs', sa.Column('user_email', mysql.VARCHAR(length=255), nullable=False))
    op.add_column('timelogs', sa.Column('description', mysql.TEXT(), nullable=True))
    op.drop_constraint(None, 'timelogs', type_='foreignkey')
    op.drop_constraint(None, 'timelogs', type_='foreignkey')
    op.drop_constraint(None, 'timelogs', type_='foreignkey')
    op.drop_constraint(None, 'timelogs', type_='foreignkey')
    op.drop_constraint(None, 'timelogs', type_='foreignkey')
    op.create_foreign_key(op.f('timelogs_ibfk_1'), 'timelogs', 'issues', ['issue_id'], ['id'])
    op.create_foreign_key(op.f('timelogs_ibfk_4'), 'timelogs', 'users', ['user_email'], ['email'])
    op.create_foreign_key(op.f('timelogs_ibfk_3'), 'timelogs', 'tasks', ['task_id'], ['id'])
    op.create_foreign_key(op.f('timelogs_ibfk_2'), 'timelogs', 'projects', ['project_id'], ['id'])
    op.create_index(op.f('ix_timelogs_id'), 'timelogs', ['id'], unique=False)
    op.alter_column('timelogs', 'general_log',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_server_default=sa.text("'0'"))
    op.alter_column('timelogs', 'approval_status',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    op.alter_column('timelogs', 'billing_type',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    op.alter_column('timelogs', 'daily_log_hours',
               existing_type=mysql.DECIMAL(precision=5, scale=2),
               nullable=True)
    op.alter_column('timelogs', 'user_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.add_column('teams', sa.Column('dept_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('teams_ibfk_1'), 'teams', 'departments', ['dept_id'], ['id'], ondelete='SET NULL')
    op.add_column('tasks', sa.Column('status_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('tasks', sa.Column('actual_hours', mysql.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('tasks', sa.Column('previous_status', mysql.VARCHAR(length=100), nullable=True))
    op.add_column('tasks', sa.Column('priority_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('tasks', sa.Column('created_by_email', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('tasks', sa.Column('assignee_email', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('tasks', sa.Column('title', mysql.VARCHAR(length=255), nullable=False))
    op.add_column('tasks', sa.Column('end_date', sa.DATE(), nullable=True))
    op.add_column('tasks', sa.Column('progress', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.create_foreign_key(op.f('tasks_ibfk_4'), 'tasks', 'projects', ['project_id'], ['id'])
    op.create_foreign_key(op.f('tasks_ibfk_3'), 'tasks', 'priorities', ['priority_id'], ['id'])
    op.create_foreign_key(op.f('tasks_ibfk_1'), 'tasks', 'users', ['assignee_email'], ['email'])
    op.create_foreign_key(op.f('tasks_ibfk_5'), 'tasks', 'statuses', ['status_id'], ['id'])
    op.create_foreign_key(op.f('tasks_ibfk_2'), 'tasks', 'users', ['created_by_email'], ['email'], ondelete='SET NULL')
    op.drop_index(op.f('ix_tasks_task_name'), table_name='tasks')
    op.create_index(op.f('ix_tasks_title'), 'tasks', ['title'], unique=False)
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.alter_column('tasks', 'is_processed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('tasks', 'billing_type',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True,
               existing_server_default=sa.text("'Billable'"))
    op.alter_column('tasks', 'task_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.add_column('projects', sa.Column('status_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('projects', sa.Column('previous_status', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('projects', sa.Column('priority_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('projects', sa.Column('created_by_email', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('projects', sa.Column('client', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('projects', sa.Column('name', mysql.VARCHAR(length=255), nullable=False))
    op.add_column('projects', sa.Column('end_date', sa.DATE(), nullable=True))
    op.add_column('projects', sa.Column('start_date', sa.DATE(), nullable=True))
    op.add_column('projects', sa.Column('manager_email', mysql.VARCHAR(length=255), nullable=True))
    op.drop_constraint(None, 'projects', type_='foreignkey')
    op.drop_constraint(None, 'projects', type_='foreignkey')
    op.drop_constraint(None, 'projects', type_='foreignkey')
    op.drop_constraint(None, 'projects', type_='foreignkey')
    op.create_foreign_key(op.f('projects_ibfk_1'), 'projects', 'users', ['created_by_email'], ['email'], ondelete='SET NULL')
    op.create_foreign_key(op.f('projects_ibfk_3'), 'projects', 'priorities', ['priority_id'], ['id'])
    op.create_foreign_key(op.f('projects_ibfk_2'), 'projects', 'users', ['manager_email'], ['email'])
    op.create_foreign_key(op.f('fk_projects_prev_status'), 'projects', 'statuses', ['previous_status'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('projects_ibfk_4'), 'projects', 'statuses', ['status_id'], ['id'])
    op.drop_index(op.f('ix_projects_project_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_project_id_sync'), table_name='projects')
    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
    op.create_index(op.f('project_id_sync'), 'projects', ['project_id_sync'], unique=True)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.alter_column('projects', 'is_processed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('projects', 'is_group',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_server_default=sa.text("'0'"))
    op.alter_column('projects', 'is_template',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_server_default=sa.text("'0'"))
    op.alter_column('projects', 'actual_hours',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=True)
    op.alter_column('projects', 'estimated_hours',
               existing_type=mysql.DECIMAL(precision=10, scale=2),
               nullable=True)
    op.alter_column('projects', 'priority',
               existing_type=mysql.VARCHAR(length=20),
               nullable=True)
    op.alter_column('projects', 'status',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    op.alter_column('projects', 'project_type',
               existing_type=mysql.ENUM('INTERNAL', 'EXTERNAL'),
               nullable=True)
    op.alter_column('projects', 'billing_model',
               existing_type=mysql.ENUM('TM', 'FIXED', 'MILESTONE'),
               nullable=True)
    op.alter_column('projects', 'customer_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.alter_column('projects', 'project_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.alter_column('projects', 'account_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.alter_column('projects', 'project_id_sync',
               existing_type=mysql.VARCHAR(length=100),
               nullable=True)
    op.add_column('milestones', sa.Column('status_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('milestones', sa.Column('title', mysql.VARCHAR(length=255), nullable=False))
    op.add_column('milestones', sa.Column('owner_email', mysql.VARCHAR(length=255), nullable=True))
    op.drop_constraint(None, 'milestones', type_='foreignkey')
    op.drop_constraint(None, 'milestones', type_='foreignkey')
    op.create_foreign_key(op.f('milestones_ibfk_3'), 'milestones', 'statuses', ['status_id'], ['id'])
    op.create_foreign_key(op.f('milestones_ibfk_1'), 'milestones', 'users', ['owner_email'], ['email'])
    op.create_foreign_key(op.f('milestones_ibfk_2'), 'milestones', 'projects', ['project_id'], ['id'])
    op.drop_index(op.f('ix_milestones_milestone_name'), table_name='milestones')
    op.create_index(op.f('ix_milestones_title'), 'milestones', ['title'], unique=False)
    op.create_index(op.f('ix_milestones_id'), 'milestones', ['id'], unique=False)
    op.alter_column('milestones', 'is_processed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('milestones', 'milestone_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.add_column('issues', sa.Column('status_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('issues', sa.Column('previous_status', mysql.VARCHAR(length=100), nullable=True))
    op.add_column('issues', sa.Column('priority_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('issues', sa.Column('assignee_email', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('issues', sa.Column('reporter_email', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('issues', sa.Column('title', mysql.VARCHAR(length=255), nullable=False))
    op.add_column('issues', sa.Column('end_date', sa.DATE(), nullable=True))
    op.drop_constraint(None, 'issues', type_='foreignkey')
    op.drop_constraint(None, 'issues', type_='foreignkey')
    op.drop_constraint(None, 'issues', type_='foreignkey')
    op.drop_constraint(None, 'issues', type_='foreignkey')
    op.create_foreign_key(op.f('issues_ibfk_2'), 'issues', 'priorities', ['priority_id'], ['id'])
    op.create_foreign_key(op.f('issues_ibfk_1'), 'issues', 'users', ['assignee_email'], ['email'])
    op.create_foreign_key(op.f('issues_ibfk_4'), 'issues', 'users', ['reporter_email'], ['email'])
    op.create_foreign_key(op.f('issues_ibfk_5'), 'issues', 'statuses', ['status_id'], ['id'])
    op.create_foreign_key(op.f('issues_ibfk_3'), 'issues', 'projects', ['project_id'], ['id'])
    op.drop_index(op.f('ix_issues_bug_name'), table_name='issues')
    op.create_index(op.f('ix_issues_title'), 'issues', ['title'], unique=False)
    op.create_index(op.f('ix_issues_id'), 'issues', ['id'], unique=False)
    op.alter_column('issues', 'is_processed',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('issues', 'reproducible_flag',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('issues', 'bug_name',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
    op.create_table('timesheets',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('start_date', sa.DATE(), nullable=False),
    sa.Column('end_date', sa.DATE(), nullable=False),
    sa.Column('project_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_email', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('billing_type', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('total_hours', mysql.DECIMAL(precision=5, scale=2), nullable=True),
    sa.Column('approval_status', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('is_deleted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('timesheets_ibfk_1')),
    sa.ForeignKeyConstraint(['user_email'], ['users.email'], name=op.f('timesheets_ibfk_2')),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_timesheets_id'), 'timesheets', ['id'], unique=False)
    op.create_table('auditlogs',
    sa.Column('ID', mysql.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('TableName', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('Action', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('PerformedBy', mysql.CHAR(length=32), nullable=False),
    sa.Column('PerformedOn', mysql.DATETIME(), nullable=False),
    sa.Column('RecordName', mysql.VARCHAR(length=500), nullable=True),
    sa.Column('TransactionId', mysql.CHAR(length=32), nullable=False),
    sa.Column('Comments', mysql.TEXT(), nullable=True),
    sa.Column('ModuleName', mysql.VARCHAR(length=250), nullable=True),
    sa.PrimaryKeyConstraint('ID'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('auditmetadatainfo',
    sa.Column('Id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('File_name', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('StartDate', mysql.DATETIME(), nullable=False),
    sa.Column('EndDate', mysql.DATETIME(), nullable=False),
    sa.Column('ModuleOrEntityName', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('CreatedOn', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False),
    sa.PrimaryKeyConstraint('Id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('auditfieldsmapping',
    sa.Column('ID', mysql.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('EntityName', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('FieldName', mysql.VARCHAR(length=150), nullable=False),
    sa.Column('DisplayName', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('IsActive', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('IsVisible', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('OrderNo', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('ID'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('project_users',
    sa.Column('project_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_processed', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('is_deleted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('user_email', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('role_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('project_users_ibfk_1'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('project_users_ibfk_3'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('project_users_ibfk_2'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('uq_project_user'), 'project_users', ['project_id', 'user_id'], unique=True)
    op.create_table('auditlogdetails',
    sa.Column('Id', mysql.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('AuditLogId', mysql.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('FieldName', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('OldValue', mysql.TEXT(), nullable=True),
    sa.Column('NewValue', mysql.TEXT(), nullable=True),
    sa.Column('ValueType', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['AuditLogId'], ['auditlogs.ID'], name=op.f('auditlogdetails_ibfk_1')),
    sa.PrimaryKeyConstraint('Id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('departments',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.Column('is_deleted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_departments_name'), 'departments', ['name'], unique=True)
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
    op.drop_table('AuditLogDetails')
    op.drop_table('AuditMetaDataInfo')
    op.drop_table('AuditLogs')
    op.drop_table('AuditFieldsMapping')

