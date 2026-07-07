"""Static Data — small, stable option catalogs the UI needs.

The legacy app served these from `/static-data/*` list-lite endpoints (Redux
`staticData`). They are tiny, stable enums, so we serve them as constants here
rather than store them in tables. Used by the Test Configuration report-config /
POC-config builders (expressions, age bands, gender, yes/no).
"""

from __future__ import annotations

from fastapi import APIRouter

from core.api import ok

router = APIRouter(prefix="/static-data")
TAG = ["static-data"]


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
