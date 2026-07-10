"""Drop and recreate all tables in the configured database.

Importing `main` registers every service's models on Base.metadata, so both
drop_all and create_all cover the full schema.

    python -m scripts.reset_db
"""

from __future__ import annotations

from sqlalchemy import text

import core.audit  # noqa: F401  (register AuditLogs)
import main  # noqa: F401  (registers every service's models)
from core.database import Base, engine


def reset() -> None:
    # Wipe everything in the public schema (handles FK dependencies / stray
    # objects not tracked by Base.metadata), then rebuild from the models.
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    print("Dropped and recreated schema 'public'.")
    Base.metadata.create_all(engine)
    print(f"Created {len(Base.metadata.tables)} tables in the configured database.")


if __name__ == "__main__":
    reset()
