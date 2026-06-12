"""Notification model — migrated from GKNotificationService.

Legacy `from`/`to` columns are renamed to `fromUserId`/`toUserId` (DB latitude)
since `from` is a Python keyword.
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Notification(TimestampMixin, Base):
    __tablename__ = "Notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fromUserId: Mapped[int | None] = mapped_column(Integer)
    toUserId: Mapped[int | None] = mapped_column(Integer, index=True)
    message: Mapped[str | None] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    createdBy: Mapped[int | None] = mapped_column(Integer)
