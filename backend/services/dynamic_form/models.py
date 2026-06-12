"""Dynamic form model — migrated from GkDynamicFormService (Chats)."""

from __future__ import annotations

from sqlalchemy import JSON, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Chat(TimestampMixin, Base):
    __tablename__ = "Chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    icon: Mapped[str | None] = mapped_column(String)
    chatData: Mapped[list | None] = mapped_column(ARRAY(JSON))
    stepData: Mapped[list | None] = mapped_column(ARRAY(JSON))
