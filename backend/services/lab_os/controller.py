"""Controllers for the Lab Operations service (ported from GkLabOsService).

Real logic: department name uniqueness + active default; instruments/SOPs/
validations/sessions scoped to a lab.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified

from core.api import ok, paginate
from core.controller import BaseController
from core.populate import attach_related
from services.lab_os.models import (
    Department,
    Instrument,
    LabSession,
    OrderReportHeader,
    Reagent,
    Sop,
    Validation,
)


class DepartmentController(BaseController):
    model = Department
    name = "Department"
    search_fields = ("name", "code")

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise HTTPException(400, "name is required")
        if self.db.query(Department).filter(func.lower(Department.name) == name.lower()).first():
            raise HTTPException(409, "Department already exists")
        payload = self.writable({**data, "name": name})
        payload.setdefault("isActive", True)
        row = Department(**payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "Department added successfully")


class InstrumentController(BaseController):
    model = Instrument
    name = "Instrument"
    search_fields = ("instrument", "serial_number")

    def add_instrument(self, data: dict) -> dict:
        payload = self.writable(data)
        payload.setdefault("status", "draft")
        payload["created_by"] = data.get("loginUserId") or data.get("created_by")
        obj = Instrument(**payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        self.audit("create", obj.id)
        return ok(self.serialize(obj), "Instrument added successfully")

    def search(self, q) -> dict:
        from services.user_service.models import User

        query = self.db.query(Instrument)
        if getattr(q, "labId", None):
            query = query.filter(Instrument.labId == q.labId)
        if getattr(q, "categories", None):
            query = query.filter(Instrument.category.in_(q.categories))
        if getattr(q, "statuses", None):
            query = query.filter(Instrument.status.in_(q.statuses))
        if getattr(q, "createdByIds", None):
            query = query.filter(Instrument.created_by.in_(q.createdByIds))
        if getattr(q, "startDate", None) and getattr(q, "endDate", None):
            from datetime import datetime, timedelta

            start = datetime.fromisoformat(q.startDate)
            end = datetime.fromisoformat(q.endDate) + timedelta(days=1)
            query = query.filter(Instrument.createdAt.between(start, end))
        search = getattr(q, "search", None)
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                Instrument.instrument.ilike(term) | Instrument.serial_number.ilike(term)
            )
        query = query.order_by(Instrument.id.desc())
        page, limit = (getattr(q, "page", None) or 1), (getattr(q, "limit", None) or 10)
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        data = [self.serialize(r) for r in rows]
        attach_related(self.db, data, model=User, source_field="created_by", target_field="createdByDetails")
        return ok(paginate(data, total, page, limit), "Instrument list")

    def toggle(self, instrument_id: int) -> dict:
        obj = self.db.get(Instrument, instrument_id)
        if not obj:
            raise HTTPException(404, "Instrument not found")
        obj.status = "inactive" if (obj.status or "active") == "active" else "active"
        self.db.commit()
        self.audit("update", instrument_id)
        return ok({"id": instrument_id, "status": obj.status}, "Instrument status updated")

    def add_attachment(self, instrument_id: int, record: dict) -> dict:
        obj = self.db.get(Instrument, instrument_id)
        if not obj:
            raise HTTPException(404, "Instrument not found")
        obj.attachments = [*(obj.attachments or []), record]
        flag_modified(obj, "attachments")
        self.db.commit()
        return ok(record, "Attachment added")

    def add_maintenance_log(self, instrument_id: int, log: dict) -> dict:
        obj = self.db.get(Instrument, instrument_id)
        if not obj:
            raise HTTPException(404, "Instrument not found")
        obj.maintenanceLogs = [*(obj.maintenanceLogs or []), log]
        flag_modified(obj, "maintenanceLogs")
        self.db.commit()
        return ok(log, "Maintenance log added")

    def list_by_lab(self, lab_id: int) -> dict:
        rows = self.db.query(Instrument).filter(Instrument.labId == lab_id).all()
        return ok([self.serialize(r) for r in rows], "Instrument list")

    def list_lite(self) -> dict:
        rows = (
            self.db.query(Instrument)
            .filter((Instrument.status.is_(None)) | (Instrument.status != "inactive"))
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Instrument list")


class ReagentController(BaseController):
    model = Reagent
    name = "Reagent"
    search_fields = ("name", "code")

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise HTTPException(400, "name is required")
        payload = self.writable({**data, "name": name})
        payload.setdefault("isActive", True)
        row = Reagent(**payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "Reagent added successfully")

    def list_lite(self) -> dict:
        rows = self.db.query(Reagent).filter(Reagent.isActive.is_(True)).all()
        return ok([self.serialize(r) for r in rows], "Reagent list")


class SopController(BaseController):
    model = Sop
    name = "SOP"
    search_fields = ("sop_name", "sop_number")

    def list_by_lab(self, lab_id: int) -> dict:
        rows = self.db.query(Sop).filter(Sop.labId == lab_id).all()
        return ok([self.serialize(r) for r in rows], "SOP list")


class ValidationController(BaseController):
    model = Validation
    name = "Validation"
    search_fields = ("name_of_document",)

    def list_by_lab(self, lab_id: int) -> dict:
        rows = self.db.query(Validation).filter(Validation.labId == lab_id).all()
        return ok([self.serialize(r) for r in rows], "Validation list")


class LabSessionController(BaseController):
    model = LabSession
    name = "Lab session"

    def list_by_lab(self, lab_id: int) -> dict:
        rows = self.db.query(LabSession).filter(LabSession.lab_id == lab_id).all()
        return ok([self.serialize(r) for r in rows], "Lab session list")


class OrderReportController(BaseController):
    """Auto-trigger 'Order Report Heading' management."""

    model = OrderReportHeader
    name = "Order Report"
    search_fields = ("name",)

    def _decorate(self, rows: list[dict]) -> list[dict]:
        """Attach the creating user + the selected panel details."""
        from services.test_config.models import Panel
        from services.user_service.models import User

        attach_related(
            self.db,
            rows,
            model=User,
            source_field="createdBy",
            target_field="createdByDetails",
            attributes=("id", "firstName", "lastName", "emailId"),
        )
        panel_ids = {pid for r in rows for pid in (r.get("testIds") or [])}
        panels = (
            self.db.query(Panel).filter(Panel.id.in_(panel_ids)).all() if panel_ids else []
        )
        pmap = {p.id: {"id": p.id, "name": p.name, "code": getattr(p, "code", None)} for p in panels}
        for r in rows:
            r["testDetails"] = [pmap[i] for i in (r.get("testIds") or []) if i in pmap]
        return rows

    def paginated_list(self, q) -> dict:
        data = q if isinstance(q, dict) else q.model_dump(exclude_unset=True)
        page = int(data.get("page") or 1)
        limit = int(data.get("limit") or 10)
        query = self.db.query(OrderReportHeader)
        search = (data.get("search") or "").strip().lower()
        if search:
            query = query.filter(func.lower(OrderReportHeader.name).like(f"%{search}%"))
        created_by = data.get("createdByIds") or []
        if created_by:
            query = query.filter(OrderReportHeader.createdBy.in_(created_by))
        start, end = data.get("startDate"), data.get("endDate")
        if start:
            query = query.filter(OrderReportHeader.createdAt >= start)
        if end:
            query = query.filter(OrderReportHeader.createdAt <= end)
        total = query.count()
        rows = (
            query.order_by(OrderReportHeader.createdAt.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        docs = self._decorate([self.serialize(r) for r in rows])
        return ok(paginate(docs, total, page, limit), "Order Report list")

    def add_report(self, data: dict, actor: int) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise HTTPException(400, "name is required")
        if not (data.get("testIds") or []):
            raise HTTPException(400, "Select at least one panel")
        row = OrderReportHeader(
            triggerType=data.get("triggerType") or "Order Report Heading",
            name=name,
            layout=data.get("layout") or "layout6",
            testIds=data.get("testIds") or [],
            createdBy=actor,
            isActive=True,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self._decorate([self.serialize(row)])[0], "Trigger added successfully")

    def view(self, row_id: int) -> dict:
        row = self.db.query(OrderReportHeader).filter(OrderReportHeader.id == row_id).first()
        if not row:
            raise HTTPException(404, "Order Report not found")
        return ok(self._decorate([self.serialize(row)])[0], "Order Report")

    def toggle(self, row_id: int) -> dict:
        row = self.db.query(OrderReportHeader).filter(OrderReportHeader.id == row_id).first()
        if not row:
            raise HTTPException(404, "Order Report not found")
        row.isActive = not bool(row.isActive)
        self.db.commit()
        state = "activated" if row.isActive else "deactivated"
        return ok(self.serialize(row), f"Trigger {state} successfully")
