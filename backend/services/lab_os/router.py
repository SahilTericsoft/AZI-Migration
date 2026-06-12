"""Lab Operations router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from services.lab_os import controller as c
from services.lab_os import schemas as s

router = APIRouter(prefix="/lab-os")
TAG = ["lab-os"]


@router.post("/departments", tags=TAG)
def add_department(body: s.DepartmentCreate, db: Session = Depends(get_db)):
    return c.DepartmentController(db).add(body.model_dump(exclude_unset=True))


def _crud(prefix, controller_cls, create_schema, edit_schema):
    @router.post(f"/{prefix}/list", tags=TAG, name=f"list_{prefix}")
    def listing(body: ListIn, db: Session = Depends(get_db)):
        return controller_cls(db).list(body)

    @router.get(f"/{prefix}/{{row_id}}", tags=TAG, name=f"get_{prefix}")
    def get(row_id: int, db: Session = Depends(get_db)):
        return controller_cls(db).get(row_id)

    @router.put(f"/{prefix}/{{row_id}}", tags=TAG, name=f"edit_{prefix}")
    def edit(row_id: int, body: edit_schema, db: Session = Depends(get_db)):
        return controller_cls(db).update(row_id, body.model_dump(exclude_unset=True))

    @router.delete(f"/{prefix}/{{row_id}}", tags=TAG, name=f"delete_{prefix}")
    def delete(row_id: int, db: Session = Depends(get_db)):
        return controller_cls(db).delete(row_id)


_crud("departments", c.DepartmentController, s.DepartmentCreate, s.DepartmentUpdate)


@router.post("/instruments", tags=TAG)
def add_instrument(body: s.InstrumentCreate, db: Session = Depends(get_db)):
    return c.InstrumentController(db).create(body.model_dump(exclude_unset=True))


@router.get("/instruments/by-lab/{lab_id}", tags=TAG)
def instruments_by_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.InstrumentController(db).list_by_lab(lab_id)


_crud("instruments", c.InstrumentController, s.InstrumentCreate, s.InstrumentUpdate)


@router.post("/sops", tags=TAG)
def add_sop(body: s.SopCreate, db: Session = Depends(get_db)):
    return c.SopController(db).create(body.model_dump(exclude_unset=True))


@router.get("/sops/by-lab/{lab_id}", tags=TAG)
def sops_by_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.SopController(db).list_by_lab(lab_id)


_crud("sops", c.SopController, s.SopCreate, s.SopUpdate)


@router.post("/validations", tags=TAG)
def add_validation(body: s.ValidationCreate, db: Session = Depends(get_db)):
    return c.ValidationController(db).create(body.model_dump(exclude_unset=True))


@router.get("/validations/by-lab/{lab_id}", tags=TAG)
def validations_by_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.ValidationController(db).list_by_lab(lab_id)


_crud("validations", c.ValidationController, s.ValidationCreate, s.ValidationUpdate)


@router.post("/sessions", tags=TAG)
def add_session(body: s.LabSessionCreate, db: Session = Depends(get_db)):
    return c.LabSessionController(db).create(body.model_dump(exclude_unset=True))


@router.get("/sessions/by-lab/{lab_id}", tags=TAG)
def sessions_by_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.LabSessionController(db).list_by_lab(lab_id)


_crud("sessions", c.LabSessionController, s.LabSessionCreate, s.LabSessionUpdate)
