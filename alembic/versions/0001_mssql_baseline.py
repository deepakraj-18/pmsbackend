"""MSSQL baseline schema

Fresh baseline for SQL Server. The historical MySQL migration chain (which is
locked to ``sqlalchemy.dialects.mysql`` types and ``mysql_engine`` table args)
has been archived under ``versions/legacy_mysql/`` and is no longer part of the
discovered revision history.

This baseline builds the entire schema from the SQLAlchemy models, so the DDL
is emitted through whatever dialect is connected (SQL Server here). On a fresh
SQL Server database run ``alembic upgrade head`` to create every table; future
schema changes are layered on top with ``alembic revision --autogenerate``.

Revision ID: 0001_mssql_baseline
Revises:
Create Date: 2026-05-30
"""
from alembic import op

# Importing the model package registers every table on Base.metadata.
import app.models  # noqa: F401
from app.core.database import Base

# revision identifiers, used by Alembic.
revision = "0001_mssql_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
