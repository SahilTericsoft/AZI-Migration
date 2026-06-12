"""State reporting router (PHI) — protected + audited."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from core.deps import require_user_id
from services.state_reporting import controller as c
from services.state_reporting import schemas as s

router = APIRouter(prefix="/state-reporting", dependencies=[Depends(require_user_id)])
TAG = ["state-reporting"]


@router.post("/reports", tags=TAG)
def add_report(
    body: s.StateReportingCreate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.StateReportingController(db, actor_id=actor).add(body.model_dump(exclude_unset=True))


@router.post("/reports/list", tags=TAG)
def list_reports(body: ListIn, db: Session = Depends(get_db)):
    return c.StateReportingController(db).list(body)


@router.get("/reports/{report_id}", tags=TAG)
def get_report(
    report_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.StateReportingController(db, actor_id=actor).get(report_id)


@router.put("/reports/{report_id}", tags=TAG)
def edit_report(
    report_id: int,
    body: s.StateReportingUpdate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.StateReportingController(db, actor_id=actor).update(
        report_id, body.model_dump(exclude_unset=True)
    )


@router.get("/reports/{report_id}/sessions", tags=TAG)
def report_sessions(report_id: int, db: Session = Depends(get_db)):
    return c.StateReportingSessionController(db).list_by_reporting(report_id)


@router.post("/sessions", tags=TAG)
def add_session(
    body: s.StateReportingSessionCreate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.StateReportingSessionController(db, actor_id=actor).create(
        body.model_dump(exclude_unset=True)
    )
