# MySQL → SQL Server Migration

Branch: `feat/mysql-to-mssql-migration`

This backend was converted from MySQL (`mysql+pymysql`) to Microsoft SQL Server
(`mssql+pyodbc`). The application layer is SQLAlchemy ORM and was already
portable; the changes below cover the MySQL-specific coupling.

## What changed in code

| Area | File | Change |
|------|------|--------|
| Drivers | `requirements.txt` | `PyMySQL`/`aiomysql` → `pyodbc`/`aioodbc` |
| Connection URL | `app/core/config.py` | `mssql+pyodbc` / `mssql+aioodbc`; added `DB_DRIVER`, `DB_ENCRYPT`, `DB_TRUST_SERVER_CERTIFICATE`, `DB_TRUSTED_CONNECTION` (Windows auth); `DB_PORT` may be left empty for a named/shared-memory instance; default user `sa` |
| FK delete rules | `app/models/*.py` | Removed 54 `ON DELETE CASCADE`/`SET NULL` clauses — SQL Server rejects cascade cycles / multiple cascade paths (see below). Deletion is now app-managed/soft-delete; FKs default to `NO ACTION` |
| UTC server default | `app/core/database.py` | New dialect-aware `utcnow()` (`SYSUTCDATETIME()` on MSSQL, `UTC_TIMESTAMP()` on MySQL) replaces `func.utc_timestamp()` |
| DB bootstrap | `app/core/database.py` | `ensure_database_exists()` rewritten to T-SQL: connects to `master`, `AUTOCOMMIT`, checks `sys.databases`, `CREATE DATABASE [name]` |
| Model defaults | `app/models/user.py` | `func.utc_timestamp()` → `utcnow()`; `func.current_date()` → Python date default |
| Migrations | `alembic/versions/` | 27 MySQL-dialect migrations archived to `versions/legacy_mysql/`; single `0001_mssql_baseline.py` builds the schema from the models |

Generic constructs were left untouched because SQLAlchemy maps them to SQL
Server automatically: `Boolean` → `BIT`, `JSON` (roles.permissions) →
`NVARCHAR(MAX)`, `Numeric`, `BigInteger`/`Integer` autoincrement → `IDENTITY`,
`ilike` → `LOWER() LIKE` (and MSSQL's default collation is case-insensitive).

## Prerequisites (host)

1. Install the Microsoft ODBC driver: **msodbcsql18** (provides
   "ODBC Driver 18 for SQL Server"). Match the `DB_DRIVER` env value to the
   exact installed name.
2. `pip install -r requirements.txt`
3. A reachable SQL Server (local instance, container, or Azure SQL).
   - Docker: `docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=<pwd>" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest`

## Authentication options

The config supports both auth modes:

- **SQL login (Azure SQL / production):** set `DB_USER` + `DB_PASSWORD`, leave
  `DB_TRUSTED_CONNECTION=false`. Requires the server to have mixed-mode auth and
  the login enabled, and TCP reachable on `DB_PORT`.
- **Windows / integrated auth (local dev):** set `DB_TRUSTED_CONNECTION=true`
  (DB_USER/DB_PASSWORD are ignored). Leave `DB_PORT` empty to use shared memory
  for a local default instance, or set `HOST\INSTANCE` in `DB_SERVER`.

> On this machine TCP/1433 is disabled and the `sa` login is not enabled, so the
> local `.env` uses Windows auth + shared memory. To use the `sa`/TCP path
> instead: enable TCP/IP in SQL Server Configuration Manager and restart the
> service, then enable mixed-mode auth and the `sa` login
> (`ALTER LOGIN sa WITH PASSWORD=...; ALTER LOGIN sa ENABLE;`).

## Run the migration (verified against SQL Server 2022)

```bash
# 1. Configure .env (see authentication options above)
# 2. Create the database + schema
alembic upgrade head        # 0001_mssql_baseline creates every table
# 3. Start the app (AUTO_SEED will populate master lookups)
uvicorn app.main:app
```

## Data transfer (only if existing MySQL data must be preserved)

The baseline creates an empty schema. To move existing rows:
- Use a tool such as the SQL Server Migration Assistant (SSMA) for MySQL, or
  export per-table CSV from MySQL and `BULK INSERT` into SQL Server.
- Watch for: `utf8mb4` text → `NVARCHAR`, MySQL `TINYINT(1)` booleans → `BIT`,
  datetime precision, and reseeding `IDENTITY` columns after load
  (`DBCC CHECKIDENT`).

## Cascade paths (why 54 FK actions were dropped)

MySQL/InnoDB allows many cascading FKs to converge on one table and permits
self-referential cascades. SQL Server **rejects** any cascade cycle or multiple
cascade paths at `CREATE`/`ALTER` time, e.g.:

```
Introducing FOREIGN KEY constraint 'FK__users__manager_e__...' on table 'users'
may cause cycles or multiple cascade paths.
```

This schema is full of them (self-ref `users.manager_email → users.email`;
`tasks`/`issues`/`projects`/`timelogs` each cascade into `users` via several
columns while also cascading to `projects`). Rather than hand-pick a single
legal cascade path per table, all DB-level `ON DELETE` actions were removed
(→ `NO ACTION`). This is safe here because the app already deletes softly via
the `is_active`/`is_deleted` flags on `AuditMixin`. If a specific cascade is
needed later, reintroduce it on a single, cycle-free path (or handle it in the
service layer).

## Verification done in this branch

- Offline: all models import and `Base.metadata` compiles to valid SQL Server
  DDL via SQLAlchemy's `mssql` dialect (31 tables).
- Live: ran against a local **SQL Server 2022** instance (Windows auth):
  `alembic upgrade head` created all 32 tables and stamped
  `0001_mssql_baseline`; `downgrade base` → `upgrade head` round-trips cleanly.

## Recommended follow-up (non-blocking)

- SQLAlchemy's generic `Text` compiles to SQL Server's legacy `TEXT` type
  (used by `AuditLogs.Comments`, `AuditLogDetails.Old/NewValue`, issue/project
  descriptions, etc.). `TEXT` works on all current SQL Server versions but is
  deprecated. Prefer mapping these columns to `NVARCHAR(MAX)` (e.g.
  `Text().with_variant(sqlalchemy.dialects.mssql.NVARCHAR(None), "mssql")`)
  before this becomes a hard constraint, and to store Unicode correctly.

## Post-migration test checklist

- [ ] Paginated list endpoints: SQL Server `OFFSET/FETCH` requires an
      `ORDER BY`. Confirm every `.offset()/.limit()` query has an explicit
      order (exercise issues/milestones/search list endpoints).
- [ ] Case-insensitive search (`ilike`) returns expected matches.
- [ ] Audit log writes (UUID `PerformedBy`/`TransactionId` → `UNIQUEIDENTIFIER`).
- [ ] `roles.permissions` JSON round-trips.
