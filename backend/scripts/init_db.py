"""Create all tables in the configured database (dev convenience).

Importing `main` pulls in every service router, which imports every model, so
they are all registered on Base.metadata. Run once for local dev:

    python -m scripts.init_db
"""

import core.audit  # noqa: F401  (register AuditLogs)
import main  # noqa: F401  (registers every service's models)
from core.database import Base, engine


def init() -> None:
    Base.metadata.create_all(engine)
    print(f"Created {len(Base.metadata.tables)} tables in the configured database.")


if __name__ == "__main__":
    init()
