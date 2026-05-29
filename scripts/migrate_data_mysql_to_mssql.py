"""One-shot data copy: MySQL (source) -> SQL Server (target).

The schema must already exist on SQL Server (run `alembic upgrade head` first).
This copies row data only, table-by-table in FK-dependency order, preserving
primary keys via IDENTITY_INSERT.

Target connection comes from the app settings (app.core.config.settings), i.e.
your normal .env. Source (MySQL) connection comes from MYSQL_* env vars:

    MYSQL_HOST      (default: localhost)
    MYSQL_PORT      (default: 3306)
    MYSQL_DB        (default: trucsprojects)
    MYSQL_USER      (default: root)
    MYSQL_PASSWORD  (required)

Usage (PowerShell):
    $env:MYSQL_PASSWORD = "..."; .venv\\Scripts\\python.exe scripts\\migrate_data_mysql_to_mssql.py
"""
from __future__ import annotations

import json
import os
import sys
from urllib.parse import quote_plus

from sqlalchemy import create_engine, inspect, text

# Ensure the app package is importable when run from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.models  # noqa: F401  (registers every table on Base.metadata)
from app.core.config import settings
from app.core.database import Base

SKIP_TABLES = {"alembic_version"}


def source_url() -> str:
    pwd = os.environ.get("MYSQL_PASSWORD")
    if pwd is None:
        raise SystemExit("MYSQL_PASSWORD env var is required for the source DB.")
    user = os.environ.get("MYSQL_USER", "root")
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3306")
    db = os.environ.get("MYSQL_DB", "trucsprojects")
    return f"mysql+pymysql://{user}:{quote_plus(pwd)}@{host}:{port}/{db}"


def coerce(value):
    """Make a MySQL-driver value safe for pyodbc/SQL Server."""
    if isinstance(value, (dict, list)):
        return json.dumps(value)  # JSON column -> NVARCHAR(MAX)
    return value


def main() -> None:
    src = create_engine(source_url())
    tgt = create_engine(settings.DATABASE_URL)

    src_insp = inspect(src)
    tgt_insp = inspect(tgt)
    src_tables = set(src_insp.get_table_names())
    tgt_tables = set(tgt_insp.get_table_names())

    # Dependency order from the model metadata (parents before children).
    ordered = [t.name for t in Base.metadata.sorted_tables]
    copy_tables = [
        t for t in ordered
        if t not in SKIP_TABLES and t in src_tables and t in tgt_tables
    ]

    # IMPORTANT: read ALL schema metadata up front. Reflecting a table opens a
    # separate pooled connection; doing it after the write transaction has taken
    # schema-modification locks (via NOCHECK CONSTRAINT) would self-deadlock.
    col_map: dict[str, list[str]] = {}
    for name in copy_tables:
        src_cols = [c["name"] for c in src_insp.get_columns(name)]
        tgt_cols = {c["name"] for c in tgt_insp.get_columns(name)}
        col_map[name] = [c for c in src_cols if c in tgt_cols]  # common, source order

    summary: list[tuple[str, int]] = []

    with src.connect() as sconn, tgt.begin() as tconn:
        # 1. Disable FK checking on every target table for the load.
        for name in tgt_tables:
            tconn.execute(text(f"ALTER TABLE [{name}] NOCHECK CONSTRAINT ALL"))

        # 2. Clear existing target rows (reverse dependency order) for idempotency.
        for name in reversed(ordered):
            if name in tgt_tables and name not in SKIP_TABLES:
                tconn.execute(text(f"DELETE FROM [{name}]"))

        # 3. Copy each table (metadata already gathered; uses only `tconn`).
        for name in copy_tables:
            cols = col_map[name]
            rows = sconn.execute(text(f"SELECT * FROM `{name}`")).mappings().all()
            if not rows:
                summary.append((name, 0))
                continue

            col_list = ", ".join(f"[{c}]" for c in cols)
            params = ", ".join(f":{c}" for c in cols)
            insert_sql = text(f"INSERT INTO [{name}] ({col_list}) VALUES ({params})")

            has_identity = tconn.execute(
                text("SELECT OBJECTPROPERTY(OBJECT_ID(:t), 'TableHasIdentity')"),
                {"t": name},
            ).scalar()

            if has_identity:
                tconn.execute(text(f"SET IDENTITY_INSERT [{name}] ON"))
            tconn.execute(
                insert_sql,
                [{c: coerce(r[c]) for c in cols} for r in rows],
            )
            if has_identity:
                tconn.execute(text(f"SET IDENTITY_INSERT [{name}] OFF"))

            summary.append((name, len(rows)))

        # 4. Re-enable + re-validate FK constraints.
        for name in tgt_tables:
            tconn.execute(text(f"ALTER TABLE [{name}] WITH CHECK CHECK CONSTRAINT ALL"))

    total = sum(n for _, n in summary)
    print("Data migration complete.")
    for name, n in summary:
        if n:
            print(f"  {name}: {n}")
    print(f"TOTAL rows copied: {total}")


if __name__ == "__main__":
    main()
