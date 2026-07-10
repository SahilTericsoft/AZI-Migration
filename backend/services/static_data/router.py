"""Static Data — small, stable option catalogs the UI needs.

The legacy app served these from `/static-data/*` list-lite endpoints (Redux
`staticData`). They are tiny, stable enums, so we serve them as constants here
rather than store them in tables. Used by the Test Configuration report-config /
POC-config builders (expressions, age bands, gender, yes/no).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.api import ok
from core.database import get_db
from services.legacy_parity.models import BiomarkerStaticSampleTypes as SampleTypeRow
from services.static_data import schemas as s

router = APIRouter(prefix="/static-data")
TAG = ["static-data"]


def _serialize_sample_type(row: SampleTypeRow) -> dict:
    return {
        "id": row.id,
        "sampleType": row.sampleType,
        "sampleCollectionDeviceName": row.sampleCollectionDeviceName or [],
    }


# Comparison expressions used in biomarker report-configuration rules.
# `-` means "between" (range) — the UI enables the low-bound `value1` only for it.
EXPRESSIONS = [
    {"title": "Greater than", "code": ">"},
    {"title": "Greater than or equal to", "code": ">="},
    {"title": "Less than", "code": "<"},
    {"title": "Less than or equal to", "code": "<="},
    {"title": "Equal to", "code": "="},
    {"title": "Between", "code": "-"},
]

# Age bands for reference ranges (title == code).
AGE_LIST = [
    {"title": "All", "code": "all"},
    {"title": "0-1 years", "code": "0-1"},
    {"title": "1-5 years", "code": "1-5"},
    {"title": "5-12 years", "code": "5-12"},
    {"title": "12-18 years", "code": "12-18"},
    {"title": "18-40 years", "code": "18-40"},
    {"title": "40-60 years", "code": "40-60"},
    {"title": "60+ years", "code": "60+"},
]

GENDER = [
    {"title": "Male", "code": "male"},
    {"title": "Female", "code": "female"},
    {"title": "Other", "code": "other"},
]

YES_NO = [
    {"title": "Yes", "code": True},
    {"title": "No", "code": False},
]

# Sample types with the collection devices allowed for each (legacy
# `/staticData/biomarker/sampleTypes`). The admin-managed source of truth is the
# `BiomarkerStaticSampleTypes` table; this is the fallback used when that table
# is empty, so the Test/Panel wizard always has options + the type→device link.
SAMPLE_TYPES_WITH_DEVICES = [
    {"sampleType": "Blood", "sampleCollectionDeviceName": [
        {"title": "Vacutainer (EDTA)", "code": "vacutainer edta"},
        {"title": "Vacutainer (SST)", "code": "vacutainer sst"},
    ]},
    {"sampleType": "Serum", "sampleCollectionDeviceName": [
        {"title": "Vacutainer (SST)", "code": "vacutainer sst"},
    ]},
    {"sampleType": "Plasma", "sampleCollectionDeviceName": [
        {"title": "Vacutainer (EDTA)", "code": "vacutainer edta"},
    ]},
    {"sampleType": "Urine", "sampleCollectionDeviceName": [
        {"title": "Urine Cup", "code": "urine cup"},
    ]},
    {"sampleType": "Saliva", "sampleCollectionDeviceName": [
        {"title": "Saliva Collection Kit", "code": "saliva kit"},
    ]},
    {"sampleType": "Nasal Swab", "sampleCollectionDeviceName": [
        {"title": "Swab", "code": "swab"},
        {"title": "Viral Transport Medium", "code": "vtm"},
    ]},
    {"sampleType": "Nasopharyngeal Swab", "sampleCollectionDeviceName": [
        {"title": "Swab", "code": "swab"},
        {"title": "Viral Transport Medium", "code": "vtm"},
    ]},
    {"sampleType": "Oropharyngeal Swab", "sampleCollectionDeviceName": [
        {"title": "Swab", "code": "swab"},
        {"title": "Viral Transport Medium", "code": "vtm"},
    ]},
    {"sampleType": "Wound Swab", "sampleCollectionDeviceName": [
        {"title": "Swab", "code": "swab"},
    ]},
    {"sampleType": "Stool", "sampleCollectionDeviceName": [
        {"title": "Stool Container", "code": "stool container"},
    ]},
    {"sampleType": "Tissue", "sampleCollectionDeviceName": [
        {"title": "Swab", "code": "swab"},
    ]},
    {"sampleType": "Sputum", "sampleCollectionDeviceName": [
        {"title": "Viral Transport Medium", "code": "vtm"},
    ]},
]


@router.get("/expressions", tags=TAG, summary="Comparison expressions")
def get_expressions():
    return ok(EXPRESSIONS, "expressions")


@router.get("/age-list", tags=TAG, summary="Age bands")
def get_age_list():
    return ok(AGE_LIST, "age list")


@router.get("/gender", tags=TAG, summary="Gender options")
def get_gender():
    return ok(GENDER, "gender options")


@router.get("/yes-no", tags=TAG, summary="Yes/No options")
def get_yes_no():
    return ok(YES_NO, "yes/no options")


@router.get("/sample-types", tags=TAG, summary="List sample types with their collection devices")
def list_sample_types(db: Session = Depends(get_db)):
    """Admin-managed sample types + the collection devices allowed for each
    (legacy `/staticData/biomarker/sampleTypes`).

    Reads the `BiomarkerStaticSampleTypes` table. If it has never been populated,
    the built-in default `SAMPLE_TYPES_WITH_DEVICES` is returned (without ids) so
    the wizard always has options — run `scripts.seed_sample_types` to make them
    editable.
    """
    rows = db.query(SampleTypeRow).order_by(SampleTypeRow.sampleType).all()
    if not rows:
        return ok(SAMPLE_TYPES_WITH_DEVICES, "sample types (default)")
    return ok([_serialize_sample_type(r) for r in rows], "sample types")


@router.post("/sample-types", tags=TAG, summary="Create a sample type")
def create_sample_type(body: s.SampleTypeCreate, db: Session = Depends(get_db)):
    name = body.sampleType.strip()
    if not name:
        raise HTTPException(400, "sampleType is required")
    exists = (
        db.query(SampleTypeRow)
        .filter(func.lower(SampleTypeRow.sampleType) == name.lower())
        .first()
    )
    if exists:
        raise HTTPException(409, "Sample type already exists")
    now = datetime.now(timezone.utc)
    row = SampleTypeRow(
        sampleType=name,
        sampleCollectionDeviceName=[d.model_dump() for d in body.sampleCollectionDeviceName],
        createdAt=now,
        updatedAt=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(_serialize_sample_type(row), "Sample type added")


@router.put("/sample-types/{type_id}", tags=TAG, summary="Update a sample type")
def update_sample_type(type_id: int, body: s.SampleTypeUpdate, db: Session = Depends(get_db)):
    row = db.get(SampleTypeRow, type_id)
    if not row:
        raise HTTPException(404, "Sample type not found")
    if body.sampleType is not None:
        name = body.sampleType.strip()
        if not name:
            raise HTTPException(400, "sampleType cannot be blank")
        clash = (
            db.query(SampleTypeRow)
            .filter(
                func.lower(SampleTypeRow.sampleType) == name.lower(),
                SampleTypeRow.id != type_id,
            )
            .first()
        )
        if clash:
            raise HTTPException(409, "Sample type already exists")
        row.sampleType = name
    if body.sampleCollectionDeviceName is not None:
        row.sampleCollectionDeviceName = [d.model_dump() for d in body.sampleCollectionDeviceName]
    row.updatedAt = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return ok(_serialize_sample_type(row), "Sample type updated")


@router.delete("/sample-types/{type_id}", tags=TAG, summary="Delete a sample type")
def delete_sample_type(type_id: int, db: Session = Depends(get_db)):
    row = db.get(SampleTypeRow, type_id)
    if not row:
        raise HTTPException(404, "Sample type not found")
    db.delete(row)
    db.commit()
    return ok({"id": type_id}, "Sample type deleted")


@router.get("", tags=TAG, summary="All static-data catalogs")
def get_all():
    return ok(
        {
            "expressions": EXPRESSIONS,
            "ageList": AGE_LIST,
            "gender": GENDER,
            "yesNo": YES_NO,
        },
        "static data",
    )
