"""Lab router — explicit routes wired to the controllers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.lab import controller as c
from services.lab import schemas as s

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
