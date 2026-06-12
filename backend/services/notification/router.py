"""Notification router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.notification import controller as c
from services.notification import schemas as s

router = APIRouter(prefix="/notification")
TAG = ["notification"]


@router.post("/notifications", tags=TAG)
def add_notification(body: s.NotificationCreate, db: Session = Depends(get_db)):
    return c.NotificationController(db).add(body.model_dump(exclude_unset=True))


@router.post("/notifications/list", tags=TAG)
def list_notifications(body: s.NotificationListQuery, db: Session = Depends(get_db)):
    return c.NotificationController(db).list(body)


@router.put("/notifications/{notification_id}/read", tags=TAG)
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    return c.NotificationController(db).mark_read(notification_id)


@router.get("/notifications/{notification_id}", tags=TAG)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    return c.NotificationController(db).get(notification_id)


@router.put("/notifications/{notification_id}", tags=TAG)
def edit_notification(
    notification_id: int, body: s.NotificationEdit, db: Session = Depends(get_db)
):
    return c.NotificationController(db).update(notification_id, body.model_dump(exclude_unset=True))


@router.delete("/notifications/{notification_id}", tags=TAG)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    return c.NotificationController(db).delete(notification_id)
