"""BaseController — the shared, explicit CRUD implementation.

Every service has its own `controller.py` with controller classes that extend
this base. The real logic (querying, pagination, search, soft-delete, sensitive-
field masking, HIPAA audit) lives here once and is readable; service controllers
configure it and override the `before_create` / `before_update` hooks to add
domain logic (e.g. generating an internal id or an order code).

A controller is constructed per request with the DB session and the acting user:

    PatientController(db, actor_id=current_user["id"]).create(payload)
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Query, Session

from core.api import ListIn, ok, paginate, to_dict
from core.audit import record_audit
from core.database import Base
from core.populate import attach_created_by


class BaseController:
    # ---- configuration (set by each service's controller) ----
    model: type[Base]
    name: str = "Record"
    sensitive: Sequence[str] = ()  # columns never returned by the API
    search_fields: Sequence[str] = ()  # columns matched by `search`
    audit_entity: str | None = None  # set for PHI -> writes an audit row

    def __init__(self, db: Session, actor_id: int | None = None):
        self.db = db
        self.actor_id = actor_id
        self.columns = {c.name for c in self.model.__table__.columns}
        self.has_soft_delete = "isDeleted" in self.columns

    # ---- helpers ----
    def serialize(self, obj: Base) -> dict[str, Any]:
        return to_dict(obj, exclude=self.sensitive)

    def writable(self, data: dict) -> dict:
        """Keep only real, client-writable columns."""
        blocked = {"id", "createdAt", "updatedAt"}
        return {k: v for k, v in data.items() if k in self.columns and k not in blocked}

    def audit(self, action: str, record_id: int | None) -> None:
        if self.audit_entity:
            record_audit(self.db, self.actor_id, action, self.audit_entity, record_id)

    def fetch(self, id_: int) -> Base:
        obj = self.db.get(self.model, id_)
        if not obj or (self.has_soft_delete and getattr(obj, "isDeleted", False)):
            raise HTTPException(404, f"{self.name} not found")
        return obj

    # ---- domain hooks (override in service controllers) ----
    def before_create(self, data: dict) -> dict:
        return data

    def before_update(self, obj: Base, data: dict) -> dict:
        return data

    # ---- operations ----
    def create(self, data: dict) -> dict:
        obj = self.model(**self.before_create(self.writable(data)))
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        self.audit("create", obj.id)
        return ok(self.serialize(obj), f"{self.name} created")

    def get(self, id_: int) -> dict:
        obj = self.fetch(id_)
        self.audit("view", id_)
        return ok(self.serialize(obj), f"{self.name} details")

    # ---- shared list building (reused by every service's list endpoint) ----
    def apply_filters(
        self,
        query: Query,
        *,
        search: str | None = None,
        search_fields: Sequence[str] | None = None,
        statuses: Sequence[str] | None = None,
        created_by_ids: Sequence[int] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        sort: dict | None = None,
    ) -> Query:
        """Apply the filters common to the catalog/list endpoints: createdBy,
        free-text search, active/status, created-at range, and sort."""
        model = self.model
        fields = self.search_fields if search_fields is None else search_fields

        if created_by_ids and "createdBy" in self.columns:
            query = query.filter(model.createdBy.in_(created_by_ids))
        if search and search.strip() and fields:
            term = f"%{search.strip().lower()}%"
            query = query.filter(or_(*[func.lower(getattr(model, f)).like(term) for f in fields]))
        if statuses:
            if "isActive" in self.columns and "active" in statuses:
                query = query.filter(model.isActive.is_(True))
            if "isActive" in self.columns and "inactive" in statuses:
                query = query.filter(model.isActive.is_(False))
            if "status" in self.columns:
                real = [s for s in statuses if s not in ("active", "inactive", "deleted")]
                if real:
                    query = query.filter(model.status.in_(real))
        if start_date and end_date and "createdAt" in self.columns:
            end = datetime.fromisoformat(end_date) + timedelta(days=1)
            query = query.filter(model.createdAt.between(datetime.fromisoformat(start_date), end))
        if sort:
            for field, direction in sort.items():
                if hasattr(model, field):
                    col = getattr(model, field)
                    query = query.order_by(
                        desc(col) if str(direction).upper() == "DESC" else asc(col)
                    )
        elif "createdAt" in self.columns:
            query = query.order_by(model.createdAt.desc())
        return query

    def paginated(
        self,
        query: Query,
        page,
        limit,
        *,
        status_obj: bool = False,
        populate_created_by: bool = False,
        message: str = "success",
    ) -> dict:
        """Count + page a query, serialize rows, and optionally attach a
        `statusObj` and batched `createdByDetails` (single query, no N+1)."""
        page, limit = page or 1, limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        docs = [self.serialize(r) for r in rows]
        if status_obj:
            for d in docs:
                d["statusObj"] = {"title": d.get("status"), "code": d.get("status")}
        if populate_created_by:
            attach_created_by(self.db, docs)
        return ok(paginate(docs, total, page, limit), message)

    def list(self, body: ListIn) -> dict:
        self.audit("list", None)  # HIPAA: record PHI list/search access
        query = self.db.query(self.model)
        if self.has_soft_delete:
            query = query.filter(self.model.isDeleted.isnot(True))
        if body.filters:
            for col, val in body.filters.items():
                if col in self.columns:
                    column = getattr(self.model, col)
                    query = query.filter(
                        column.in_(val) if isinstance(val, list) else column == val
                    )
        query = self.apply_filters(query, search=body.search)
        if body.page or body.limit:
            return self.paginated(query, body.page, body.limit, message=f"{self.name} list")
        return ok([self.serialize(r) for r in query.all()], f"{self.name} list")

    def update(self, id_: int, data: dict) -> dict:
        obj = self.fetch(id_)
        for key, value in self.before_update(obj, self.writable(data)).items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        self.audit("update", id_)
        return ok(self.serialize(obj), f"{self.name} updated")

    def delete(self, id_: int) -> dict:
        obj = self.fetch(id_)
        if self.has_soft_delete:
            obj.isDeleted = True
            if "isActive" in self.columns:
                obj.isActive = False
        else:
            self.db.delete(obj)
        self.db.commit()
        self.audit("delete", id_)
        return ok({}, f"{self.name} deleted")
