"""Small helpers local to the user service."""

from collections.abc import Iterable
from datetime import UTC, date, datetime
from typing import Any

from core.config import settings
from core.database import Base


def to_dict(obj: Base | None, *, exclude: Iterable[str] = ()) -> dict[str, Any] | None:
    """Serialise an ORM row to a JSON-safe dict (datetimes -> ISO strings)."""
    if obj is None:
        return None
    excluded = set(exclude)
    out: dict[str, Any] = {}
    for col in obj.__table__.columns:
        if col.name in excluded:
            continue
        val = getattr(obj, col.name)
        out[col.name] = val.isoformat() if isinstance(val, (datetime, date)) else val
    return out


def ok(data: Any = None, message: str = "success") -> dict[str, Any]:
    """Standard success envelope (matches the legacy { message, data } shape)."""
    return {"message": message, "data": data}


def paginate(rows: list, total: int, page: int, limit: int) -> dict[str, Any]:
    return {"page": page, "limit": limit, "docs": rows, "total": total}


def next_internal_user_id(last_internal_id: str | None) -> str:
    """Build the next internalUserId: {INSTANCE}_{YYYYMMDD}_{seq:04}."""
    date_code = datetime.now(UTC).strftime("%Y%m%d")
    seq = 1
    if last_internal_id:
        parts = last_internal_id.split("_")
        if len(parts) >= 3 and parts[2].isdigit():
            seq = int(parts[2]) + 1
    return f"{settings.instance_code}_{date_code}_{seq:04d}"
