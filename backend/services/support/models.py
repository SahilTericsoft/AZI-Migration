"""Support models — Help Center sections (Support Center) + system documents
(Resources). Ported from the legacy admin-console helpSection service and the
GET/POST `/systemLabDocuments` endpoints.
"""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class HelpSection(TimestampMixin, Base):
    """A Support Center "Manuals" section with its attachments (JSON list)."""

    __tablename__ = "HelpSections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sequence: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    attachments: Mapped[list | None] = mapped_column(JSON)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    createdBy: Mapped[int | None] = mapped_column(Integer)


class SystemDocument(TimestampMixin, Base):
    """A Resources document — an external link with a title + description."""

    __tablename__ = "SystemDocuments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    createdBy: Mapped[int | None] = mapped_column(Integer)
