"""Lab router — explicit routes wired to the controllers."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from core.api import ok
from core.database import get_db
from core import storage
from services.lab import controller as c
from services.lab import schemas as s
from services.lab.models import Lab

router = APIRouter(prefix="/lab")
LAB = ["lab: labs"]
LU = ["lab: lab-users"]


# ----------------------------------------------------------------------- labs
@router.post("/labs", tags=LAB)
def add_lab(body: s.LabCreate, db: Session = Depends(get_db)):
    return c.LabController(db).add(body.model_dump(exclude_unset=True))


@router.post("/labs/list", tags=LAB)
def list_labs(body: s.LabListQuery, db: Session = Depends(get_db)):
    return c.LabController(db).list(body)


@router.post("/labs/list-lite", tags=LAB)
def list_labs_lite(body: s.LabListLiteQuery, db: Session = Depends(get_db)):
    return c.LabController(db).list_lite(body)


@router.post("/labs/view", tags=LAB)
def view_lab(body: s.LabViewIn, db: Session = Depends(get_db)):
    return c.LabController(db).view(body)


@router.get("/labs/by-admin/{admin_id}", tags=LAB)
def lab_by_admin(admin_id: int, db: Session = Depends(get_db)):
    return c.LabController(db).get_by_admin(admin_id)


@router.put("/labs/{lab_id}", tags=LAB)
def edit_lab(lab_id: int, body: s.LabEdit, db: Session = Depends(get_db)):
    return c.LabController(db).edit(lab_id, body.model_dump(exclude_unset=True))


@router.put("/labs/{lab_id}/toggle", tags=LAB)
def toggle_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.LabController(db).toggle(lab_id)


@router.get("/labs/{lab_id}", tags=LAB)
def get_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.LabController(db).get(lab_id)


@router.delete("/labs/{lab_id}", tags=LAB)
def delete_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.LabController(db).delete(lab_id)


@router.post("/labs/{lab_id}/attachments", tags=LAB)
async def upload_lab_attachment(
    lab_id: int,
    attachmentName: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload an onboarding document to Azure Blob and record it on the lab.

    Returns 503 until `AZURE_STORAGE_CONNECTION_STRING` is configured.
    """
    lab = db.get(Lab, lab_id)
    if not lab:
        raise HTTPException(404, "Lab not found")

    data = await file.read()
    url = storage.upload_attachment(
        data, file.filename or "attachment", file.content_type, prefix=str(lab_id)
    )
    record = {
        "attachmentName": attachmentName,
        "secureUrl": url,
        "mimeType": file.content_type,
        "size": len(data),
    }
    lab.attachments = [*(lab.attachments or []), record]
    flag_modified(lab, "attachments")
    db.commit()
    return ok(record, "Attachment uploaded")


@router.post("/labs/{lab_id}/logo", tags=LAB)
async def upload_lab_logo(
    lab_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a lab report logo to Azure Blob and record it on the lab.

    Returns 503 until `AZURE_STORAGE_CONNECTION_STRING` is configured.
    """
    lab = db.get(Lab, lab_id)
    if not lab:
        raise HTTPException(404, "Lab not found")

    data = await file.read()
    url = storage.upload_attachment(
        data, file.filename or "logo", file.content_type, prefix=f"{lab_id}/logo"
    )
    lab.logo = {"secureUrl": url, "mimeType": file.content_type}
    flag_modified(lab, "logo")
    db.commit()
    return ok(lab.logo, "Logo uploaded")


# ------------------------------------------------------------------ lab users
@router.post("/lab-users", tags=LU)
def add_lab_user(body: s.LabUserCreate, db: Session = Depends(get_db)):
    return c.LabUserController(db).add_user(body.model_dump(exclude_unset=True))


@router.get("/lab-users/by-lab/{lab_id}", tags=LU)
def lab_users_by_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.LabUserController(db).list_by_lab(lab_id)


@router.get("/lab-users/{lu_id}", tags=LU)
def get_lab_user(lu_id: int, db: Session = Depends(get_db)):
    return c.LabUserController(db).get(lu_id)


@router.put("/lab-users/{lu_id}", tags=LU)
def edit_lab_user(lu_id: int, body: s.LabUserEdit, db: Session = Depends(get_db)):
    return c.LabUserController(db).update(lu_id, body.model_dump(exclude_unset=True))


@router.delete("/lab-users/{lu_id}", tags=LU)
def delete_lab_user(lu_id: int, db: Session = Depends(get_db)):
    return c.LabUserController(db).delete(lu_id)
