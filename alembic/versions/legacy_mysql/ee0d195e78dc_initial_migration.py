
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'ee0d195e78dc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    pass

def downgrade() -> None:

    pass
