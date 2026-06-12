"""Location router — explicit routes wired to the controllers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.location import controller as c
from services.location import schemas as s

router = APIRouter(prefix="/location")
LOC = ["location: locations"]
LU = ["location: location-users"]
LP = ["location: location-physicians"]


# ----------------------------------------------------------------- locations
@router.post("/locations", tags=LOC)
def add_location(body: s.LocationCreate, db: Session = Depends(get_db)):
    return c.LocationController(db).add(body.model_dump(exclude_unset=True))


@router.post("/locations/list", tags=LOC)
def list_locations(body: s.LocationListQuery, db: Session = Depends(get_db)):
    return c.LocationController(db).list(body)


@router.post("/locations/list-lite", tags=LOC)
def list_locations_lite(body: s.LocationListLiteQuery, db: Session = Depends(get_db)):
    return c.LocationController(db).list_lite(body)


@router.post("/locations/view", tags=LOC)
def view_location(body: s.LocationViewIn, db: Session = Depends(get_db)):
    return c.LocationController(db).view(body)


@router.put("/locations/{location_id}", tags=LOC)
def edit_location(location_id: int, body: s.LocationEdit, db: Session = Depends(get_db)):
    return c.LocationController(db).edit(location_id, body.model_dump(exclude_unset=True))


@router.put("/locations/{location_id}/toggle", tags=LOC)
def toggle_location(location_id: int, db: Session = Depends(get_db)):
    return c.LocationController(db).toggle(location_id)


@router.post("/locations/{location_id}/physicians", tags=LOC)
def add_location_physician(location_id: int, body: s.AddPhysicianIn, db: Session = Depends(get_db)):
    return c.LocationController(db).add_physician(location_id, body.physicianId)


@router.post("/locations/{location_id}/physicians/bulk", tags=LOC)
def add_location_physicians_bulk(
    location_id: int, body: s.AddBulkPhysiciansIn, db: Session = Depends(get_db)
):
    return c.LocationController(db).add_bulk_physicians(location_id, body.physicianIds)


@router.get("/locations/{location_id}", tags=LOC)
def get_location(location_id: int, db: Session = Depends(get_db)):
    return c.LocationController(db).get(location_id)


@router.delete("/locations/{location_id}", tags=LOC)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    return c.LocationController(db).delete(location_id)


# ------------------------------------------------------ location users / phys
@router.post("/location-users", tags=LU)
def add_location_user(body: s.LocationUserCreate, db: Session = Depends(get_db)):
    return c.LocationUserController(db).create(body.model_dump(exclude_unset=True))


@router.get("/location-users/{lu_id}", tags=LU)
def get_location_user(lu_id: int, db: Session = Depends(get_db)):
    return c.LocationUserController(db).get(lu_id)


@router.put("/location-users/{lu_id}", tags=LU)
def edit_location_user(lu_id: int, body: s.LocationUserEdit, db: Session = Depends(get_db)):
    return c.LocationUserController(db).update(lu_id, body.model_dump(exclude_unset=True))


@router.delete("/location-users/{lu_id}", tags=LU)
def delete_location_user(lu_id: int, db: Session = Depends(get_db)):
    return c.LocationUserController(db).delete(lu_id)


@router.post("/location-physicians", tags=LP)
def add_location_physician_row(body: s.LocationPhysicianCreate, db: Session = Depends(get_db)):
    return c.LocationPhysicianController(db).create(body.model_dump(exclude_unset=True))


@router.get("/location-physicians/{lp_id}", tags=LP)
def get_location_physician(lp_id: int, db: Session = Depends(get_db)):
    return c.LocationPhysicianController(db).get(lp_id)


@router.put("/location-physicians/{lp_id}", tags=LP)
def edit_location_physician(
    lp_id: int, body: s.LocationPhysicianEdit, db: Session = Depends(get_db)
):
    return c.LocationPhysicianController(db).update(lp_id, body.model_dump(exclude_unset=True))


@router.delete("/location-physicians/{lp_id}", tags=LP)
def delete_location_physician(lp_id: int, db: Session = Depends(get_db)):
    return c.LocationPhysicianController(db).delete(lp_id)
