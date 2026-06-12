"""Controllers for the Lab Operations service (ported from GkLabOsService).

Real logic: department name uniqueness + active default; instruments/SOPs/
validations/sessions scoped to a lab.
"""

from fastapi import HTTPException
from sqlalchemy import func

from core.api import ok
from core.controller import BaseController
from services.lab_os.models import Department, Instrument, LabSession, Sop, Validation


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

    def list_by_lab(self, lab_id: int) -> dict:
        rows = self.db.query(Instrument).filter(Instrument.labId == lab_id).all()
        return ok([self.serialize(r) for r in rows], "Instrument list")


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
