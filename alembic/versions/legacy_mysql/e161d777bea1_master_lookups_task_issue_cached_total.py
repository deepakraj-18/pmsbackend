
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = 'e161d777bea1'
down_revision: Union[str, Sequence[str], None] = '9fa8e2abf1d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    



    op.execute()


    op.add_column('issues', sa.Column('status_id',         sa.Integer(), nullable=True))
    op.add_column('issues', sa.Column('severity_id',       sa.Integer(), nullable=True))
    op.add_column('issues', sa.Column('classification_id', sa.Integer(), nullable=True))

    op.alter_column('issues', 'estimated_hours',
                    existing_type=mysql.DECIMAL(precision=5, scale=2),
                    type_=sa.Numeric(precision=10, scale=2),
                    existing_nullable=True)

    op.create_foreign_key('fk_issues_status',         'issues', 'master_lookups', ['status_id'],         ['id'])
    op.create_foreign_key('fk_issues_severity',       'issues', 'master_lookups', ['severity_id'],       ['id'])
    op.create_foreign_key('fk_issues_classification', 'issues', 'master_lookups', ['classification_id'], ['id'])

    op.drop_column('issues', 'status')
    op.drop_column('issues', 'severity')
    op.drop_column('issues', 'classification')


    op.add_column('tasks', sa.Column('status_id',            sa.Integer(),                    nullable=True))
    op.add_column('tasks', sa.Column('priority_id',          sa.Integer(),                    nullable=True))
    op.add_column('tasks', sa.Column('cached_timelog_total', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'))

    op.alter_column('tasks', 'estimated_hours',
                    existing_type=mysql.DECIMAL(precision=5, scale=2),
                    type_=sa.Numeric(precision=10, scale=2),
                    existing_nullable=True)
    op.alter_column('tasks', 'work_hours',
                    existing_type=mysql.DECIMAL(precision=5, scale=2),
                    type_=sa.Numeric(precision=10, scale=2),
                    existing_nullable=True)

    op.create_foreign_key('fk_tasks_status',   'tasks', 'master_lookups', ['status_id'],   ['id'])
    op.create_foreign_key('fk_tasks_priority', 'tasks', 'master_lookups', ['priority_id'], ['id'])

    op.drop_column('tasks', 'status')
    op.drop_column('tasks', 'priority')


    op.alter_column('timelogs', 'daily_log_hours',
                    existing_type=mysql.DECIMAL(precision=5, scale=2),
                    type_=sa.Numeric(precision=10, scale=2),
                    existing_nullable=False)


def downgrade() -> None:
    
    op.alter_column('timelogs', 'daily_log_hours',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    type_=mysql.DECIMAL(precision=5, scale=2),
                    existing_nullable=False)

    op.add_column('tasks', sa.Column('priority', mysql.VARCHAR(length=50),  nullable=True))
    op.add_column('tasks', sa.Column('status',   mysql.VARCHAR(length=100), nullable=True))
    op.drop_constraint('fk_tasks_priority', 'tasks',  type_='foreignkey')
    op.drop_constraint('fk_tasks_status',   'tasks',  type_='foreignkey')
    op.alter_column('tasks', 'work_hours',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    type_=mysql.DECIMAL(precision=5, scale=2),
                    existing_nullable=True)
    op.alter_column('tasks', 'estimated_hours',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    type_=mysql.DECIMAL(precision=5, scale=2),
                    existing_nullable=True)
    op.drop_column('tasks', 'cached_timelog_total')
    op.drop_column('tasks', 'priority_id')
    op.drop_column('tasks', 'status_id')

    op.add_column('issues', sa.Column('classification', mysql.VARCHAR(length=50),  nullable=True))
    op.add_column('issues', sa.Column('severity',       mysql.VARCHAR(length=20),  nullable=True))
    op.add_column('issues', sa.Column('status',         mysql.VARCHAR(length=100), nullable=True))
    op.drop_constraint('fk_issues_classification', 'issues', type_='foreignkey')
    op.drop_constraint('fk_issues_severity',       'issues', type_='foreignkey')
    op.drop_constraint('fk_issues_status',         'issues', type_='foreignkey')
    op.alter_column('issues', 'estimated_hours',
                    existing_type=sa.Numeric(precision=10, scale=2),
                    type_=mysql.DECIMAL(precision=5, scale=2),
                    existing_nullable=True)
    op.drop_column('issues', 'classification_id')
    op.drop_column('issues', 'severity_id')
    op.drop_column('issues', 'status_id')

    op.drop_table('master_lookups')
