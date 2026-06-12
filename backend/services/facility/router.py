"""Facility router — explicit routes wired to the controllers.

Surfaces the real legacy endpoints: add, rich list, list-lite, view (with
sub-details), edit, toggle (cascades to locations), and physician/admin links.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.facility import controller as c
from services.facility import schemas as s

router = APIRouter(prefix="/facility")
FAC = ["facility: facilities"]
FU = ["facility: facility-users"]


# ---------------------------------------------------------------- facilities
@router.post("/facilities", tags=FAC)
def add_facility(body: s.FacilityCreate, db: Session = Depends(get_db)):
    return c.FacilityController(db).add(body.model_dump(exclude_unset=True))


@router.post("/facilities/list", tags=FAC)
def list_facilities(body: s.FacilityListQuery, db: Session = Depends(get_db)):
    return c.FacilityController(db).list(body)


@router.post("/facilities/list-lite", tags=FAC)
def list_facilities_lite(body: s.FacilityListLiteQuery, db: Session = Depends(get_db)):
    return c.FacilityController(db).list_lite(body)


@router.post("/facilities/view", tags=FAC)
def view_facility(body: s.FacilityViewIn, db: Session = Depends(get_db)):
    return c.FacilityController(db).view(body)


@router.put("/facilities/{facility_id}", tags=FAC)
def edit_facility(facility_id: int, body: s.FacilityEdit, db: Session = Depends(get_db)):
    return c.FacilityController(db).edit(facility_id, body.model_dump(exclude_unset=True))


@router.put("/facilities/{facility_id}/toggle", tags=FAC)
def toggle_facility(facility_id: int, db: Session = Depends(get_db)):
    return c.FacilityController(db).toggle(facility_id)


@router.post("/facilities/{facility_id}/physicians", tags=FAC)
def add_physicians(facility_id: int, body: s.AddPhysiciansIn, db: Session = Depends(get_db)):
    return c.FacilityController(db).add_physicians(facility_id, body.physicians)


@router.delete("/facilities/{facility_id}/physicians/{physician_id}", tags=FAC)
def delete_physician(facility_id: int, physician_id: int, db: Session = Depends(get_db)):
    return c.FacilityController(db).delete_physician(facility_id, physician_id)


@router.put("/facilities/{facility_id}/admin", tags=FAC)
def set_admin(facility_id: int, body: s.SetAdminIn, db: Session = Depends(get_db)):
    return c.FacilityController(db).set_admin(facility_id, body.adminId)


@router.get("/facilities/{facility_id}", tags=FAC)
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    return c.FacilityController(db).get(facility_id)


@router.delete("/facilities/{facility_id}", tags=FAC)
def delete_facility(facility_id: int, db: Session = Depends(get_db)):
    return c.FacilityController(db).delete(facility_id)


# ------------------------------------------------------------- facility users
@router.post("/facility-users", tags=FU)
def add_facility_user(body: s.FacilityUserCreate, db: Session = Depends(get_db)):
    return c.FacilityUserController(db).create(body.model_dump(exclude_unset=True))


@router.get("/facility-users/by-facility/{facility_id}", tags=FU)
def facility_users_by_facility(facility_id: int, db: Session = Depends(get_db)):
    return c.FacilityUserController(db).list_by_facility(facility_id)


@router.get("/facility-users/{fu_id}", tags=FU)
def get_facility_user(fu_id: int, db: Session = Depends(get_db)):
    return c.FacilityUserController(db).get(fu_id)


@router.put("/facility-users/{fu_id}", tags=FU)
def edit_facility_user(fu_id: int, body: s.FacilityUserEdit, db: Session = Depends(get_db)):
    return c.FacilityUserController(db).update(fu_id, body.model_dump(exclude_unset=True))


@router.delete("/facility-users/{fu_id}", tags=FU)
def delete_facility_user(fu_id: int, db: Session = Depends(get_db)):
    return c.FacilityUserController(db).delete(fu_id)
