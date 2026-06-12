"""Database engine, session, and the FastAPI session dependency.

Single connection point for the whole monorepo. Sync SQLAlchemy + psycopg2:
endpoints are plain `def`, so FastAPI runs them in a threadpool — no async/
event-loop complexity.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Shared declarative base for every ORM model in the monorepo."""

    pass


class TimestampMixin:
    """createdAt / updatedAt columns, matching the legacy schema."""

    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
