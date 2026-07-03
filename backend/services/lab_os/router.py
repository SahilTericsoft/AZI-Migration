"""Lab Operations router."""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from core.api import ListIn
from core import storage
from core.database import get_db
from core.deps import require_user_id
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
    return c.InstrumentController(db).add_instrument(body.model_dump(exclude_unset=True))


@router.post("/instruments/search", tags=TAG)
def search_instruments(body: s.InstrumentSearchQuery, db: Session = Depends(get_db)):
    return c.InstrumentController(db).search(body)


@router.put("/instruments/{instrument_id}/toggle", tags=TAG)
def toggle_instrument(instrument_id: int, db: Session = Depends(get_db)):
    return c.InstrumentController(db).toggle(instrument_id)


@router.post("/instruments/{instrument_id}/maintenance-logs", tags=TAG)
def add_maintenance_log(instrument_id: int, body: s.MaintenanceLogIn, db: Session = Depends(get_db)):
    return c.InstrumentController(db).add_maintenance_log(instrument_id, body.model_dump(exclude_unset=True))


@router.post("/instruments/{instrument_id}/attachments", tags=TAG)
async def add_instrument_attachment(
    instrument_id: int,
    attachmentName: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    data = await file.read()
    url = storage.upload_attachment(
        data, file.filename or "attachment", file.content_type, prefix=f"instrument/{instrument_id}"
    )
    record = {"attachmentName": attachmentName, "secureUrl": url, "mimeType": file.content_type, "size": len(data)}
    return c.InstrumentController(db).add_attachment(instrument_id, record)


@router.get("/instruments/by-lab/{lab_id}", tags=TAG)
def instruments_by_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.InstrumentController(db).list_by_lab(lab_id)


@router.get("/instruments/list-lite", tags=TAG)
def instruments_list_lite(db: Session = Depends(get_db)):
    return c.InstrumentController(db).list_lite()


_crud("instruments", c.InstrumentController, s.InstrumentCreate, s.InstrumentUpdate)


# ----------------------------------------------------------------- reagents
@router.post("/reagents", tags=TAG)
def add_reagent(body: s.ReagentCreate, db: Session = Depends(get_db)):
    return c.ReagentController(db).add(body.model_dump(exclude_unset=True))


@router.get("/reagents/list-lite", tags=TAG)
def reagents_list_lite(db: Session = Depends(get_db)):
    return c.ReagentController(db).list_lite()


_crud("reagents", c.ReagentController, s.ReagentCreate, s.ReagentUpdate)


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


# --------------------------------------------- Auto Triggers / Order Reports
@router.post("/order-reports/list", tags=TAG)
def list_order_reports(body: s.OrderReportListQuery, db: Session = Depends(get_db)):
    return c.OrderReportController(db).paginated_list(body)


@router.post("/order-reports", tags=TAG)
def add_order_report(
    body: s.OrderReportCreate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.OrderReportController(db).add_report(body.model_dump(exclude_unset=True), actor)


@router.get("/order-reports/{row_id}", tags=TAG)
def view_order_report(row_id: int, db: Session = Depends(get_db)):
    return c.OrderReportController(db).view(row_id)


@router.put("/order-reports/{row_id}/toggle", tags=TAG)
def toggle_order_report(row_id: int, db: Session = Depends(get_db)):
    return c.OrderReportController(db).toggle(row_id)
