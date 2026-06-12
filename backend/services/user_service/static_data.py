"""Static / reference data routes (consolidated).

Combines GkUserService UserStaticDataController (geo) + RaceAndEthnicityController
(dropdowns) into one router.
  - GET /geo?type=cities|states|county|zipcodes|all  = getCities/getStates/getCounty/
        getZipcode/getCityListLite/listLite in a single, parameterised endpoint
  - GET /dropdowns/{title}                            = view + prefix + suffix + maritalStatus
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from core.database import get_db
from services.user_service.models import Dropdown, StateCityStaticData
from services.user_service.schemas import (
    DropdownDeleteIn,
    DropdownUpsertIn,
    GeoAddIn,
    GeoDeleteIn,
)
from services.user_service.utils import ok, paginate, to_dict

router = APIRouter(prefix="/static-data", tags=["user-service: static-data"])

_GEO_COLS = {c.name for c in StateCityStaticData.__table__.columns}


# ------------------------------------------------------------------- geo
@router.get("/geo")
def geo(
    type: str = Query("zipcodes", pattern="^(cities|states|county|zipcodes|all)$"),
    search: str | None = None,
    state: str | None = None,
    zipcode: str | None = None,
    page: int | None = None,
    limit: int | None = None,
    db: Session = Depends(get_db),
):
    M = StateCityStaticData
    term = f"%{search.lower().strip()}%" if search and search.strip() else None

    if type == "all":  # full list (legacy listLite / getCityListLite)
        return ok([to_dict(r) for r in db.query(M).all()], "Static Data List")

    page, limit = page or 1, limit or 10
    offset = (page - 1) * limit

    if type == "states":
        q = db.query(M.state).distinct()
        if zipcode:
            q = q.filter(M.zipcode == zipcode)
        if term:
            q = q.filter(func.lower(M.state).like(term))
        q = q.order_by(M.state.asc())
        docs = [{"state": r[0]} for r in q.offset(offset).limit(limit).all()]
    elif type == "county":
        q = db.query(M.county).distinct()
        if term:
            q = q.filter(func.lower(M.county).like(term))
        q = q.order_by(M.county.asc())
        docs = [{"county": r[0]} for r in q.offset(offset).limit(limit).all()]
    elif type == "cities":
        q = db.query(M)
        if state:
            q = q.filter(M.state == state)
        if term:
            q = q.filter(func.lower(M.city).like(term))
        q = q.order_by(M.createdAt.desc())
        docs = [{"city": r.city} for r in q.offset(offset).limit(limit).all()]
    else:  # zipcodes
        q = db.query(M)
        if term:
            q = q.filter(
                or_(
                    func.lower(M.zipcode).like(term),
                    func.lower(M.city).like(term),
                    func.lower(M.state).like(term),
                )
            )
        q = q.order_by(M.createdAt.desc())
        docs = [
            {
                "city": r.city,
                "state": r.state,
                "zipcode": r.zipcode,
                "county": r.county,
                "country": r.country,
            }
            for r in q.offset(offset).limit(limit).all()
        ]
    return ok(paginate(docs, q.count(), page, limit), f"{type} Static Data List")


@router.get("/geo/zipcode/{zipcode}")
def geo_by_zipcode(zipcode: str, db: Session = Depends(get_db)):
    row = db.query(StateCityStaticData).filter(StateCityStaticData.zipcode == zipcode).first()
    return ok(to_dict(row), "Zipcode data")


@router.post("/geo")
def add_geo(body: GeoAddIn, db: Session = Depends(get_db)):
    rows = [
        StateCityStaticData(**{k: v for k, v in a.items() if k in _GEO_COLS}) for a in body.address
    ]
    db.add_all(rows)
    db.commit()
    return ok([to_dict(r) for r in rows], "Data")


@router.delete("/geo")
def delete_geo(body: GeoDeleteIn, db: Session = Depends(get_db)):
    db.query(StateCityStaticData).filter(StateCityStaticData.zipcode.in_(body.zipcodes)).delete(
        synchronize_session=False
    )
    db.commit()
    return ok([], "Data Deleted")


# ------------------------------------------------------------- dropdowns
@router.get("/dropdowns/{title}")
def get_dropdown(title: str, db: Session = Depends(get_db)):
    row = db.query(Dropdown).filter(Dropdown.title == title).first()
    return ok(row.value if row and row.value else [], "Data")


@router.post("/dropdowns")
def add_dropdown(body: DropdownUpsertIn, db: Session = Depends(get_db)):
    row = Dropdown(title=body.title, value=body.value)
    db.add(row)
    db.commit()
    return ok(to_dict(row), "StaticData added successfully")


@router.put("/dropdowns")
def edit_dropdown(body: DropdownUpsertIn, db: Session = Depends(get_db)):
    """Append options to a dropdown set, creating it if missing.
    Rejects options whose `code` already exists (legacy behaviour)."""
    row = db.query(Dropdown).filter(Dropdown.title == body.title).first()
    if not row:
        row = Dropdown(title=body.title, value=body.value)
        db.add(row)
        db.commit()
        return ok(body.value, "StaticData added successfully")

    existing = {o.get("code") for o in (row.value or [])}
    for opt in body.value:
        if opt.get("code") in existing:
            raise HTTPException(409, "Given Setting Already Exists")
    row.value = (row.value or []) + body.value
    db.commit()
    return ok(row.value, "StaticData added successfully")


@router.delete("/dropdowns")
def delete_dropdown(body: DropdownDeleteIn, db: Session = Depends(get_db)):
    row = db.query(Dropdown).filter(Dropdown.title == body.title).first()
    if not row:
        raise HTTPException(404, "Not found")
    row.value = [o for o in (row.value or []) if o.get("code") not in body.codes]
    db.commit()
    return ok(row.value, "Data Deleted")
