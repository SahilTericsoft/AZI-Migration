"""Controllers for the State Reporting service (PHI) — audited.

Real logic: status default, and reporting-scoped session listing.
"""

from __future__ import annotations

from core.api import ok
from core.controller import BaseController
from services.state_reporting.models import StateReporting, StateReportingSession


class StateReportingController(BaseController):
    model = StateReporting
    name = "State reporting"
    search_fields = ("status",)
    audit_entity = "StateReporting"

    def add(self, data: dict) -> dict:
        payload = self.writable(data)
        payload.setdefault("status", "pending")
        row = StateReporting(**payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        self.audit("create", row.id)
        return ok(self.serialize(row), "State reporting added")


class StateReportingSessionController(BaseController):
    model = StateReportingSession
    name = "State reporting session"
    audit_entity = "StateReportingSession"

    def list_by_reporting(self, reporting_id: int) -> dict:
        rows = (
            self.db.query(StateReportingSession)
            .filter(StateReportingSession.stateReportingId == reporting_id)
            .order_by(StateReportingSession.attempt.asc())
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Session list")
