"""Activity log model — migrated from GkActivityLogService."""

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class ActivityLog(TimestampMixin, Base):
    __tablename__ = "ActivityLogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module: Mapped[str | None] = mapped_column(String)
    feature: Mapped[str | None] = mapped_column(String)
    field: Mapped[str | None] = mapped_column(String)
    value: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(String)
    action: Mapped[str | None] = mapped_column(String)
    userId: Mapped[int | None] = mapped_column(Integer, index=True)
    identityId: Mapped[int | None] = mapped_column(Integer, index=True)
    logDateTime: Mapped[str | None] = mapped_column(String)
    data: Mapped[dict | None] = mapped_column(JSON)
    reasonForEdit: Mapped[str | None] = mapped_column(String)
