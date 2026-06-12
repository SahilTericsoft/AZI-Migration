"""Billing reference router — insurers + clearing houses."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from services.billing import controller as c
from services.billing import schemas as s

router = APIRouter(prefix="/billing")
TAG = ["billing"]


@router.post("/insurers", tags=TAG)
def add_insurer(body: s.InsurerCreate, db: Session = Depends(get_db)):
    return c.InsurerController(db).add(body.model_dump(exclude_unset=True))


@router.post("/insurers/list", tags=TAG)
def list_insurers(body: ListIn, db: Session = Depends(get_db)):
    return c.InsurerController(db).list(body)


@router.get("/insurers/{insurer_id}", tags=TAG)
def get_insurer(insurer_id: int, db: Session = Depends(get_db)):
    return c.InsurerController(db).get(insurer_id)


@router.put("/insurers/{insurer_id}", tags=TAG)
def edit_insurer(insurer_id: int, body: s.InsurerUpdate, db: Session = Depends(get_db)):
    return c.InsurerController(db).update(insurer_id, body.model_dump(exclude_unset=True))


@router.delete("/insurers/{insurer_id}", tags=TAG)
def delete_insurer(insurer_id: int, db: Session = Depends(get_db)):
    return c.InsurerController(db).delete(insurer_id)


@router.post("/clearing-houses", tags=TAG)
def add_clearing_house(body: s.ClearingHouseCreate, db: Session = Depends(get_db)):
    return c.ClearingHouseController(db).add(body.model_dump(exclude_unset=True))


@router.post("/clearing-houses/list", tags=TAG)
def list_clearing_houses(body: ListIn, db: Session = Depends(get_db)):
    return c.ClearingHouseController(db).list(body)


@router.get("/clearing-houses/{ch_id}/insurances", tags=TAG)
def clearing_house_insurances(ch_id: int, db: Session = Depends(get_db)):
    return c.ClearingHouseInsuranceController(db).list_by_clearing_house(ch_id)


@router.get("/clearing-houses/{ch_id}", tags=TAG)
def get_clearing_house(ch_id: int, db: Session = Depends(get_db)):
    return c.ClearingHouseController(db).get(ch_id)


@router.put("/clearing-houses/{ch_id}", tags=TAG)
def edit_clearing_house(ch_id: int, body: s.ClearingHouseUpdate, db: Session = Depends(get_db)):
    return c.ClearingHouseController(db).update(ch_id, body.model_dump(exclude_unset=True))


@router.post("/clearing-house-insurances", tags=TAG)
def add_ch_insurance(body: s.ClearingHouseInsuranceCreate, db: Session = Depends(get_db)):
    return c.ClearingHouseInsuranceController(db).create(body.model_dump(exclude_unset=True))
