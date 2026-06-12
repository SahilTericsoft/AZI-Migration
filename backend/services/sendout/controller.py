"""Controller for the Sendout service (PHI) — audited.

Real logic: derive `sampleCount` from `sampleIds` when not supplied; lab-scoped
listing.
"""

from core.api import ok
from core.controller import BaseController
from services.sendout.models import SendoutBatch


class SendoutBatchController(BaseController):
    model = SendoutBatch
    name = "Sendout batch"
    audit_entity = "SendoutBatch"

    def add(self, data: dict) -> dict:
        payload = self.writable(data)
        if payload.get("sampleCount") is None and data.get("sampleIds"):
            payload["sampleCount"] = len(data["sampleIds"])
        row = SendoutBatch(**payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        self.audit("create", row.id)
        return ok(self.serialize(row), "Sendout batch created")

    def list_by_lab(self, lab_id: int) -> dict:
        rows = (
            self.db.query(SendoutBatch)
            .filter(SendoutBatch.sendoutLabId == lab_id)
            .order_by(SendoutBatch.createdAt.desc())
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Sendout batch list")
