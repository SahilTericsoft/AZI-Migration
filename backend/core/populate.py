"""Related-data population — the Python equivalent of the legacy `Populator`.

Batch-loads referenced rows (e.g. the `createdBy` user) and attaches a trimmed
detail object onto each serialized record, in a single query (no N+1).
"""

from collections.abc import Sequence

from sqlalchemy.orm import Session

from core.api import to_dict
from core.database import Base


def attach_related(
    db: Session,
    records: list[dict],
    *,
    model: type[Base],
    source_field: str,
    target_field: str,
    attributes: Sequence[str] | None = None,
    key: str = "id",
) -> list[dict]:
    """For each record, look up `model` where `key == record[source_field]` and
    attach the (optionally trimmed) row as `record[target_field]`."""
    ids = {r.get(source_field) for r in records if r.get(source_field) is not None}
    if not ids:
        for r in records:
            r.setdefault(target_field, None)
        return records

    rows = db.query(model).filter(getattr(model, key).in_(ids)).all()
    index: dict = {}
    for row in rows:
        full = to_dict(row) or {}
        index[getattr(row, key)] = {a: full.get(a) for a in attributes} if attributes else full
    for r in records:
        r[target_field] = index.get(r.get(source_field))
    return records


def attach_many(
    db: Session,
    records: list[dict],
    *,
    model: type[Base],
    source_field: str,
    target_field: str,
    attributes: Sequence[str] | None = None,
    key: str = "id",
) -> list[dict]:
    """Like `attach_related`, but `source_field` holds a *list* of ids; attaches
    a list of detail objects (e.g. `physicians` -> `physicianDetails`)."""
    all_ids: set = set()
    for r in records:
        vals = r.get(source_field) or []
        if isinstance(vals, list):
            all_ids.update(v for v in vals if v is not None)
    if not all_ids:
        for r in records:
            r.setdefault(target_field, [])
        return records

    rows = db.query(model).filter(getattr(model, key).in_(all_ids)).all()
    index: dict = {}
    for row in rows:
        full = to_dict(row) or {}
        index[getattr(row, key)] = {a: full.get(a) for a in attributes} if attributes else full
    for r in records:
        vals = r.get(source_field) or []
        r[target_field] = [index[v] for v in vals if v in index] if isinstance(vals, list) else []
    return records


def attach_created_by(db: Session, records: list[dict]) -> list[dict]:
    """Convenience: attach `createdByDetails` (id/firstName/middleName/lastName)
    from the Users table — mirrors the legacy `SetCreatedBy`."""
    from services.user_service.models import User

    return attach_related(
        db,
        records,
        model=User,
        source_field="createdBy",
        target_field="createdByDetails",
        attributes=["id", "firstName", "middleName", "lastName"],
    )
