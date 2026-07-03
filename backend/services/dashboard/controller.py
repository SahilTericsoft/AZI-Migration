"""Dashboard aggregations (ported from the legacy GkTestOrderService dashboard
endpoints). Read-only counts/group-bys over already-migrated tables — no new
models. Numbers reflect whatever is in the connected DB.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.api import ok
from services.facility.models import Facility
from services.location.models import Location
from services.patient.models import Patient
from services.sample.models import OrderSample
from services.sendout.models import SendoutBatch
from services.test_order.models import Order

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


class DashboardController:
    def __init__(self, db: Session):
        self.db = db

    # ---- helpers -------------------------------------------------------
    def _scalar(self, model, *filters) -> int:
        q = self.db.query(func.count(model.id))
        for f in filters:
            q = q.filter(f)
        return q.scalar() or 0

    def _onboard(self, model) -> dict:
        return {
            "count": self._scalar(model),
            "thisMonth": self._scalar(model, model.createdAt >= _month_start()),
        }

    # ---- endpoints -----------------------------------------------------
    def onboarding_count(self) -> dict:
        return ok(
            {
                "facilities": self._onboard(Facility),
                "locations": self._onboard(Location),
                "testOrders": self._onboard(Order),
                "patients": self._onboard(Patient),
            },
            "Onboarding count",
        )

    def order_status_count(self) -> dict:
        rows = (
            self.db.query(Order.status, func.count(Order.id))
            .group_by(Order.status)
            .all()
        )
        segments = [{"label": (s or "unknown"), "value": c} for s, c in rows]
        total = sum(c for _, c in rows)
        return ok({"total": total, "segments": segments}, "Order status count")

    def order_count_by_year(self, year: int) -> dict:
        rows = (
            self.db.query(func.extract("month", Order.createdAt), func.count(Order.id))
            .filter(func.extract("year", Order.createdAt) == year)
            .group_by(func.extract("month", Order.createdAt))
            .all()
        )
        by_month = {int(m): c for m, c in rows}
        months = [{"month": MONTHS[i], "count": by_month.get(i + 1, 0)} for i in range(12)]
        return ok({"year": year, "months": months}, "Order count by year")

    def sample_workflow(self) -> dict:
        S = OrderSample
        c = lambda *fs: self._scalar(S, *fs)  # noqa: E731

        ordered = {
            "total": c(S.isAccessioned.isnot(True), S.isSendOut.isnot(True)),
            "collected": c(S.dateOfCollection.isnot(None), S.isAccessioned.isnot(True)),
            "received": c(S.status == "received"),
        }
        accessioned = {
            "total": c(S.isAccessioned.is_(True)),
            "routine": c(S.isAccessioned.is_(True), S.isPriorityOrder.isnot(True)),
            "stat": c(S.isAccessioned.is_(True), S.isPriorityOrder.is_(True)),
            "priority": c(S.isPriorityOrder.is_(True)),
        }
        discontinued = {
            "total": c(S.status.in_(["rejected", "sampleRejected", "cancelled", "orderCancelled"])),
            "sampleRejected": c(S.status.in_(["rejected", "sampleRejected"])),
            "orderCanceled": c(S.status.in_(["cancelled", "orderCancelled"])),
        }
        in_progress = {
            "total": c(S.status.in_(["inProcess", "partiallyResulted", "completed"])),
            "partiallyResulted": c(S.status == "partiallyResulted"),
            "completed": c(S.isPdfGenerated.is_(True)),
        }
        sendout = {
            "total": c(S.isSendOut.is_(True)),
            "atReferenceLab": c(S.isSendOut.is_(True), S.isPdfGenerated.isnot(True)),
            "resulted": c(S.isSendOut.is_(True), S.isPdfGenerated.is_(True)),
        }
        return ok(
            {
                "ordered": ordered,
                "accessioned": accessioned,
                "discontinued": discontinued,
                "inProgress": in_progress,
                "sendout": sendout,
            },
            "Sample workflow",
        )

    def sendout_analysis(self) -> dict:
        total = self._scalar(OrderSample)
        sendout = self._scalar(OrderSample, OrderSample.isSendOut.is_(True))
        completed = self._scalar(OrderSample, OrderSample.isPdfGenerated.is_(True))
        total_sendouts = self._scalar(SendoutBatch)
        ref_labs = (
            self.db.query(func.count(func.distinct(SendoutBatch.sendoutLabId))).scalar() or 0
        )
        pct = round(sendout / total * 100) if total else 0
        comp = round(completed / total * 100) if total else 0
        return ok(
            {
                "sendoutPercentage": pct,
                "sampleCompletionRate": comp,
                "totalSendouts": total_sendouts,
                "avgTurnaround": None,
                "referenceLabs": ref_labs,
            },
            "Sendout analysis",
        )
