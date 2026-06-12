"""Generate a single PostgreSQL DDL file for the whole backend schema.

Imports every model (via `main` + the audit module), then compiles a
`CREATE TABLE IF NOT EXISTS` statement and the `CREATE INDEX` statements per
table for the PostgreSQL dialect.

    python -m scripts.dump_schema > schema.sql
"""

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

import core.audit  # noqa: F401  (registers AuditLogs)
import main  # noqa: F401  (imports every service -> every model onto Base.metadata)
from core.database import Base

HEADER = """\
-- =====================================================================
-- AZI Backend — full database schema (PostgreSQL)
-- Generated from the SQLAlchemy models. {n} tables.
-- Safe to run on an empty DB or to add missing tables/indexes (IF NOT EXISTS).
--
-- NOTE: foreign keys are modeled as plain integer columns (no FK
-- constraints) to mirror the legacy Sequelize schema 1:1. See
-- SCHEMA_CHANGES.md for changes vs the legacy schema.
-- =====================================================================

"""


def main_dump() -> str:
    dialect = postgresql.dialect()
    tables = sorted(Base.metadata.tables.values(), key=lambda t: t.name)
    parts = [HEADER.format(n=len(tables))]
    for table in tables:
        ddl = str(CreateTable(table).compile(dialect=dialect)).strip()
        ddl = ddl.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
        parts.append(ddl.rstrip() + ";\n")
        for index in sorted(table.indexes, key=lambda i: i.name):
            idx = str(CreateIndex(index).compile(dialect=dialect)).strip()
            idx = idx.replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ", 1)
            idx = idx.replace("CREATE UNIQUE INDEX ", "CREATE UNIQUE INDEX IF NOT EXISTS ", 1)
            parts.append(idx.rstrip() + ";\n")
    return "\n".join(parts)


if __name__ == "__main__":
    print(main_dump())
