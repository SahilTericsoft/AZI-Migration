"""Activity log router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.activity_log import controller as c
from services.activity_log import schemas as s

router = APIRouter(prefix="/activity-log")
TAG = ["activity-log"]


@router.post("/logs", tags=TAG)
def add_log(body: s.ActivityLogCreate, db: Session = Depends(get_db)):
    return c.ActivityLogController(db).create(body.model_dump(exclude_unset=True))


@router.post("/logs/bulk", tags=TAG)
def add_logs_bulk(body: s.ActivityLogBulkCreate, db: Session = Depends(get_db)):
    return c.ActivityLogController(db).save_logs(body.logs)


@router.post("/logs/list", tags=TAG)
def list_logs(body: s.ActivityLogListQuery, db: Session = Depends(get_db)):
    return c.ActivityLogController(db).list(body)


@router.get("/logs/{log_id}", tags=TAG)
def get_log(log_id: int, db: Session = Depends(get_db)):
    return c.ActivityLogController(db).get(log_id)


@router.delete("/logs/{log_id}", tags=TAG)
def delete_log(log_id: int, db: Session = Depends(get_db)):
    return c.ActivityLogController(db).delete(log_id)
