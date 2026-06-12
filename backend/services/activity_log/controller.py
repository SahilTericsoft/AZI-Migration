"""Controller for the Activity Log service (ported from GkActivityLogService).

Real logic: bulk-friendly create, and filtered/scoped listing by
identity / user / module / action.
"""

from core.api import ok, paginate
from core.controller import BaseController
from services.activity_log.models import ActivityLog


class ActivityLogController(BaseController):
    model = ActivityLog
    name = "Activity log"
    search_fields = ("module", "feature", "action")

    def save_logs(self, logs: list[dict]) -> dict:
        rows = [ActivityLog(**self.writable(log)) for log in logs]
        self.db.add_all(rows)
        self.db.commit()
        return ok({"count": len(rows)}, "Activity logs saved")

    def list(self, q) -> dict:
        query = self.db.query(ActivityLog)
        if q.identityId is not None:
            query = query.filter(ActivityLog.identityId == q.identityId)
        if q.userId is not None:
            query = query.filter(ActivityLog.userId == q.userId)
        if q.module:
            query = query.filter(ActivityLog.module == q.module)
        if q.type:
            query = query.filter(ActivityLog.type == q.type)
        query = query.order_by(ActivityLog.createdAt.desc())
        page, limit = q.page or 1, q.limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        return ok(
            paginate([self.serialize(r) for r in rows], total, page, limit), "Activity log list"
        )
