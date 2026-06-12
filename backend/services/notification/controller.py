"""Controller for the Notification service (ported from GKNotificationService).

Real logic: recipient required, active by default, list scoped to a recipient,
and a mark-read action (sets isActive=false).
"""

from __future__ import annotations

from fastapi import HTTPException

from core.api import ok, paginate
from core.controller import BaseController
from services.notification.models import Notification


class NotificationController(BaseController):
    model = Notification
    name = "Notification"
    search_fields = ("title", "message")

    def add(self, data: dict) -> dict:
        if data.get("toUserId") is None:
            raise HTTPException(400, "toUserId is required")
        payload = self.writable(data)
        payload.setdefault("isActive", True)
        row = Notification(**payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "Notification added successfully")

    def list(self, q) -> dict:
        query = self.db.query(Notification)
        if q.toUserId is not None:
            query = query.filter(Notification.toUserId == q.toUserId)
        if q.isActive is not None:
            query = query.filter(Notification.isActive.is_(q.isActive))
        if q.search and q.search.strip():
            term = f"%{q.search.strip().lower()}%"
            query = query.filter(Notification.title.ilike(term) | Notification.message.ilike(term))
        query = query.order_by(Notification.createdAt.desc())
        page, limit = q.page or 1, q.limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        return ok(
            paginate([self.serialize(r) for r in rows], total, page, limit), "Notification list"
        )

    def mark_read(self, notification_id: int) -> dict:
        row = self.db.get(Notification, notification_id)
        if not row:
            raise HTTPException(404, "Invalid notification id")
        row.isActive = False
        self.db.commit()
        return ok({"id": notification_id}, "Notification marked read")
