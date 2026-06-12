"""Shared API helpers used by every service."""

from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict

from core.database import Base


class MutationBody(BaseModel):
    """Base for create/update request bodies.

    Declares the important typed fields per entity; `extra="allow"` lets the full
    record payload through (the controller whitelists to real columns).
    """

    model_config = ConfigDict(extra="allow")


def to_dict(obj: Base | None, *, exclude: Iterable[str] = ()) -> dict[str, Any] | None:
    """Serialise an ORM row to a JSON-safe dict (datetimes -> ISO, Decimal -> float)."""
    if obj is None:
        return None
    excluded = set(exclude)
    out: dict[str, Any] = {}
    for col in obj.__table__.columns:
        if col.name in excluded:
            continue
        val = getattr(obj, col.name)
        if isinstance(val, (datetime, date)):
            val = val.isoformat()
        elif isinstance(val, Decimal):
            val = float(val)
        out[col.name] = val
    return out


def ok(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"message": message, "data": data}


def paginate(rows: list, total: int, page: int, limit: int) -> dict[str, Any]:
    return {"page": page, "limit": limit, "docs": rows, "total": total}


class ListIn(BaseModel):
    """Generic list/search request body shared by every CRUD list endpoint."""

    page: int | None = None
    limit: int | None = None
    search: str | None = None
    filters: dict[str, Any] | None = None  # {column: value} equality filters
