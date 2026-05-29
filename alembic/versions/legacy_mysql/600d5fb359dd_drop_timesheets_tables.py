
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '600d5fb359dd'
down_revision: Union[str, Sequence[str], None] = '765541d1aad8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    try:
        op.drop_constraint(op.f('fk_timelog_timesheet'), 'timelogs', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_column('timelogs', 'timesheet_id')
    except Exception:
        pass
    try:
        op.drop_index(op.f('ix_timesheets_id'), table_name='timesheets')
    except Exception:
        pass
    try:
        op.drop_table('timesheets')
    except Exception:
        pass

def downgrade() -> None:

    pass
