"""Internal-id generation — ported from the legacy `internalUserId`/
`internalPanelId` scheme (`{INSTANCE}_{YYYYMMDD}_{NNNN}`), a per-entity daily
incrementing sequence.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from core.config import settings
from core.database import Base


def daily_sequence_id(db: Session, model: type[Base], *, prefix: str | None = None) -> str:
    code = prefix or settings.instance_code
    start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    todays = db.query(model).filter(model.createdAt >= start).count()
    return f"{code}_{datetime.now(UTC).strftime('%Y%m%d')}_{todays + 1:04d}"
