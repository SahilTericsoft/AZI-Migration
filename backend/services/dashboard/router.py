"""Dashboard router — aggregated counts/charts for the home dashboard.

POST (not GET) to mirror the legacy contract and leave room for filters. The
client gates these behind a "Load Dashboard Data" action to limit calls.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.dashboard import controller as c

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class YearIn(BaseModel):
    year: int | None = None


@router.post("/onboarding-count")
def onboarding_count(db: Session = Depends(get_db)):
    return c.DashboardController(db).onboarding_count()


@router.post("/order-status-count")
def order_status_count(db: Session = Depends(get_db)):
    return c.DashboardController(db).order_status_count()


@router.post("/order-count-by-year")
def order_count_by_year(body: YearIn, db: Session = Depends(get_db)):
    year = body.year or datetime.now(timezone.utc).year
    return c.DashboardController(db).order_count_by_year(year)


@router.post("/sample-workflow")
def sample_workflow(db: Session = Depends(get_db)):
    return c.DashboardController(db).sample_workflow()


@router.post("/sendout-analysis")
def sendout_analysis(db: Session = Depends(get_db)):
    return c.DashboardController(db).sendout_analysis()
