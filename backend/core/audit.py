"""HIPAA audit trail.

Every access to protected health information (create/view/update/delete on PHI
entities) is recorded here: who (userId), what action, which entity + record,
and when. Required for HIPAA's "record and examine activity" safeguard.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, Session, mapped_column

from core.database import Base


class AuditLog(Base):
    __tablename__ = "AuditLogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int | None] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String)  # create / view / update / delete
    entity: Mapped[str] = mapped_column(String, index=True)
    recordId: Mapped[int | None] = mapped_column(Integer, index=True)
    details: Mapped[dict | None] = mapped_column(JSON)
    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def record_audit(
    db: Session,
    user_id: int | None,
    action: str,
    entity: str,
    record_id: int | None,
    details: dict | None = None,
) -> None:
    db.add(
        AuditLog(userId=user_id, action=action, entity=entity, recordId=record_id, details=details)
    )
    db.commit()
