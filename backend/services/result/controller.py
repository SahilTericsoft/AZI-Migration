"""Controllers for the Result service (PHI) — audited.

Real logic: session-scoped and order-scoped result lookups.
"""

from core.api import ok
from core.controller import BaseController
from services.result.models import ResultControl, ResultSample


class ResultSampleController(BaseController):
    model = ResultSample
    name = "Result sample"
    search_fields = ("accessionId", "testCode")
    audit_entity = "ResultSample"

    def list_by_session(self, session_id: int) -> dict:
        rows = (
            self.db.query(ResultSample)
            .filter(ResultSample.uploadResultSessionId == session_id)
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Result sample list")

    def list_by_order(self, order_id: int) -> dict:
        rows = self.db.query(ResultSample).filter(ResultSample.orderId == order_id).all()
        return ok([self.serialize(r) for r in rows], "Result sample list")


class ResultControlController(BaseController):
    model = ResultControl
    name = "Result control"
    audit_entity = "ResultControl"

    def list_by_session(self, session_id: int) -> dict:
        rows = (
            self.db.query(ResultControl)
            .filter(ResultControl.uploadResultSessionId == session_id)
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Result control list")
