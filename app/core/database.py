from __future__ import annotations

from typing import Generator

from datetime import datetime, timezone
from sqlalchemy import Column, Boolean, DateTime, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import FunctionElement
from sqlalchemy.ext.compiler import compiles
from logging import getLogger

from app.core.config import settings

logger = getLogger("app.database")


class utcnow(FunctionElement):
    """Dialect-aware "current UTC timestamp" server default.

    Renders to the native UTC function per backend so the same models run on
    SQL Server (and still on MySQL during the transition)."""
    type = DateTime()
    inherit_cache = True


@compiles(utcnow)
def _utcnow_default(element, compiler, **kw):
    return "CURRENT_TIMESTAMP"


@compiles(utcnow, "mssql")
def _utcnow_mssql(element, compiler, **kw):
    return "SYSUTCDATETIME()"


@compiles(utcnow, "mysql")
def _utcnow_mysql(element, compiler, **kw):
    return "UTC_TIMESTAMP()"


# pyodbc/Azure SQL connection tuning lives in the connection string (see
# config.DB_ENCRYPT / DB_TRUST_SERVER_CERTIFICATE), so no extra connect_args
# are required for SQL Server.
connect_args: dict = {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    echo=settings.DB_ECHO,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

sync_engine = engine

Base = declarative_base()


class AuditMixin:
    created_at = Column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        server_default=utcnow(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=False),
        default=None,
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=True,
    )
    is_active  = Column(Boolean, default=True,  nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


def ensure_database_exists():
    """Create the target database on SQL Server if it does not yet exist.

    Connects to the server's default `master` database. CREATE DATABASE cannot
    run inside a transaction on SQL Server, so we use an AUTOCOMMIT connection.
    The DB name is validated to a safe identifier and bracket-quoted because it
    cannot be parameterized in DDL.
    """
    try:
        db_name = settings.DB_NAME
        if not db_name.replace("_", "").isalnum():
            raise ValueError(f"Unsafe database name for DDL: {db_name!r}")

        # Connect to `master` by overriding the database in the configured URL.
        master_url = settings.DATABASE_URL.replace(
            f"/{db_name}?", "/master?", 1
        )
        temp_engine = create_engine(master_url, connect_args=connect_args)
        with temp_engine.connect().execution_options(
            isolation_level="AUTOCOMMIT"
        ) as conn:
            exists = conn.execute(
                text("SELECT 1 FROM sys.databases WHERE name = :name"),
                {"name": db_name},
            ).scalar()
            if not exists:
                conn.execute(text(f"CREATE DATABASE [{db_name}]"))
        temp_engine.dispose()
        logger.info(f"Ensured database '{db_name}' exists.")
    except Exception as e:
        logger.error(f"Failed to ensure database exists: {e}")
        pass

def get_sync_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

get_db = get_sync_db
