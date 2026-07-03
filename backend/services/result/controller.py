"""Controllers for the Result service (PHI) — audited.

Covers the Upload-Result + Result-Review workflow: manual-entry templates,
manual submit, instrument run-file upload (qPCR), result sessions, per-sample /
per-control edits, control recalculation, reject / rerun / generate-report.
"""

from __future__ import annotations

from fastapi import HTTPException

from core.api import ok, paginate
from core.controller import BaseController
from core.populate import attach_related
from services.lab_os.models import LabSession
from services.result import runfile
from services.result.models import ResultControl, ResultSample, UploadResultSession
from services.test_config.models import Biomarker, Panel
from services.user_service.models import User


def _worklist_samples(session: LabSession) -> list[dict]:
    cfg = session.sample_config or {}
    if cfg.get("kind") == "processing":
        return []
    return cfg.get("samples") or []


class ResultSampleController(BaseController):
    model = ResultSample
    name = "Result sample"
    search_fields = ("accessionId", "testCode")
    audit_entity = "ResultSample"

    def list_by_session(self, session_id: int) -> dict:
        rows = self.db.query(ResultSample).filter(ResultSample.uploadResultSessionId == session_id).all()
        return ok([self.serialize(r) for r in rows], "Result sample list")

    def list_by_order(self, order_id: int) -> dict:
        rows = self.db.query(ResultSample).filter(ResultSample.orderId == order_id).all()
        return ok([self.serialize(r) for r in rows], "Result sample list")


class ResultControlController(BaseController):
    model = ResultControl
    name = "Result control"
    audit_entity = "ResultControl"

    def list_by_session(self, session_id: int) -> dict:
        rows = self.db.query(ResultControl).filter(ResultControl.uploadResultSessionId == session_id).all()
        return ok([self.serialize(r) for r in rows], "Result control list")


class ResultController(BaseController):
    model = UploadResultSession
    name = "Result session"
    audit_entity = "Result"

    # ------------------------------------------------------------- selection
    def worklist_by_test_panel(self, data: dict) -> dict:
        """Worklists available for result entry (non-processing LabSessions)."""
        out = []
        for w in self.db.query(LabSession).all():
            cfg = w.sample_config or {}
            if cfg.get("kind") == "processing":
                continue
            samples = cfg.get("samples") or []
            out.append({
                "id": w.id,
                "workListId": w.id,
                "worklistId": w.id,
                "batchName": cfg.get("name") or w.rack_number or f"Worklist #{w.id}",
                "accessionCount": len(samples),
            })
        return ok(out, "Worklists")

    def _biomarker_details(self, test_id: int | None, biomarker_id: int | None) -> list[dict]:
        if biomarker_id:
            b = self.db.get(Biomarker, biomarker_id)
            return [{"id": b.id, "name": b.name}] if b else []
        if test_id:
            panel = self.db.get(Panel, test_id)
            ids = (panel.biomarkerIds if panel else None) or []
            bios = self.db.query(Biomarker).filter(Biomarker.id.in_(ids)).all() if ids else []
            return [{"id": b.id, "name": b.name} for b in bios]
        return []

    def manual_template(self, data: dict) -> dict:
        worklist_id = data.get("worklistid") or data.get("worklistId")
        worklist = self.db.get(LabSession, worklist_id) if worklist_id else None
        if not worklist:
            raise HTTPException(400, "Invalid worklistId")
        samples = _worklist_samples(worklist)
        accession_ids = [s.get("sampleCode") or s.get("barcode") or str(s.get("id")) for s in samples]
        biomarker_details = self._biomarker_details(data.get("testId"), data.get("biomarkerId"))
        return ok(
            {"accessionIds": accession_ids, "biomarkerDetails": biomarker_details, "existingResultData": {}},
            "Manual template",
        )

    # --------------------------------------------------------------- create
    def manual_submit(self, data: dict, actor: int | None) -> dict:
        results: dict = data.get("results") or {}
        biomarker_details: list = data.get("biomarkerDetails") or []
        accession_ids = data.get("accessionIds") or list(results.keys())
        bio_name = {str(b.get("id")): b.get("name") for b in biomarker_details}

        session = UploadResultSession(
            worklistId=data.get("worklistId"),
            testId=data.get("testId"),
            biomarkerId=data.get("biomarkerId"),
            biomarkerDetails=biomarker_details,
            accessionIds=accession_ids,
            status="pendingReview",
            isManual=True,
            isDiscarded=False,
            createdBy=actor,
        )
        self.db.add(session)
        self.db.flush()
        for accession, by_bio in results.items():
            for bio_id, value in (by_bio or {}).items():
                self.db.add(ResultSample(
                    uploadResultSessionId=session.id,
                    accessionId=accession,
                    biomarkerCode=str(bio_id),
                    biomarkerName=bio_name.get(str(bio_id)),
                    value=str(value) if value is not None else None,
                    result=str(value) if value is not None else None,
                    isManual=True,
                ))
        self.db.commit()
        self.db.refresh(session)
        self.audit("create", session.id)
        return ok(self.serialize(session), "Manual result submitted")

    def upload_runfile(self, content: bytes, file_name: str, data: dict, actor: int | None) -> dict:
        cutoff = float(data.get("cqCutoff") or runfile.DEFAULT_CQ_CUTOFF)
        parsed = runfile.parse_runfile(content, cutoff)
        accession_ids = list(parsed["samples"].keys())
        targets: list[str] = []
        for recs in parsed["samples"].values():
            for r in recs:
                if r["targetName"] not in targets:
                    targets.append(r["targetName"])

        session = UploadResultSession(
            worklistId=data.get("worklistId"),
            accessionIds=accession_ids,
            biomarkerDetails=[{"id": None, "name": t} for t in targets],
            status="pendingReview",
            isManual=False,
            isDiscarded=False,
            fileName=file_name,
            runMetadata=parsed["metadata"],
            cqCutoff=cutoff,
            createdBy=actor,
        )
        self.db.add(session)
        self.db.flush()
        for accession, recs in parsed["samples"].items():
            for r in recs:
                self.db.add(ResultSample(
                    uploadResultSessionId=session.id,
                    accessionId=accession,
                    targetName=r["targetName"],
                    biomarkerName=r["biomarkerName"],
                    fluorophore=r["fluorophore"],
                    wellPosition=r["wellPosition"],
                    cqValue=r["ctValue"],
                    result=r["result"],
                    isManual=False,
                ))
        for c in parsed["controls"]:
            self.db.add(ResultControl(
                uploadResultSessionId=session.id,
                wellPosition=c["wellPosition"],
                control=c["control"],
                targetName=c["targetName"],
                biomarkerName=c["biomarkerName"],
                fluorophore=c["fluorophore"],
                ctValue=c["ctValue"],
                result=c["result"],
            ))
        self.db.commit()
        self.db.refresh(session)
        self.audit("create", session.id)
        return ok(self.serialize(session), "Run file uploaded")

    # ----------------------------------------------------------------- read
    def list_sessions(self, q) -> dict:
        query = self.db.query(UploadResultSession).filter(UploadResultSession.isDiscarded.isnot(True))
        statuses = getattr(q, "statuses", None)
        if statuses:
            query = query.filter(UploadResultSession.status.in_(statuses))
        search = getattr(q, "search", None)
        if search and search.strip():
            query = query.filter(UploadResultSession.fileName.ilike(f"%{search.strip()}%"))
        query = query.order_by(UploadResultSession.createdAt.desc())
        page, limit = (getattr(q, "page", None) or 1), (getattr(q, "limit", None) or 10)
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        data = [self.serialize(r) for r in rows]
        attach_related(self.db, data, model=User, source_field="createdBy", target_field="createdByDetails")
        return ok(paginate(data, total, page, limit), "Result sessions")

    def session_detail(self, session_id: int) -> dict:
        s = self.db.get(UploadResultSession, session_id)
        if not s:
            raise HTTPException(404, "Session not found")
        data = self.serialize(s)
        attach_related(self.db, [data], model=User, source_field="createdBy", target_field="createdByDetails")
        return ok(data, "Result session")

    def session_samples(self, session_id: int) -> dict:
        rows = self.db.query(ResultSample).filter(ResultSample.uploadResultSessionId == session_id).all()
        return ok([self.serialize(r) for r in rows], "Result samples")

    def session_controls(self, session_id: int) -> dict:
        rows = self.db.query(ResultControl).filter(ResultControl.uploadResultSessionId == session_id).all()
        return ok([self.serialize(r) for r in rows], "Result controls")

    # --------------------------------------------------------------- update
    @staticmethod
    def _apply(obj, data: dict, columns: set[str]) -> None:
        blocked = {"id", "createdAt", "updatedAt", "uploadResultSessionId"}
        for k, v in data.items():
            if k in columns and k not in blocked:
                setattr(obj, k, v)

    def edit_sample(self, sample_id: int, data: dict) -> dict:
        s = self.db.get(ResultSample, sample_id)
        if not s:
            raise HTTPException(404, "Result sample not found")
        self._apply(s, data, {c.name for c in ResultSample.__table__.columns})
        self.db.commit()
        self.db.refresh(s)
        return ok(self.serialize(s), "Result updated")

    def edit_control(self, control_id: int, data: dict) -> dict:
        c = self.db.get(ResultControl, control_id)
        if not c:
            raise HTTPException(404, "Control not found")
        self._apply(c, data, {col.name for col in ResultControl.__table__.columns})
        self.db.commit()
        self.db.refresh(c)
        return ok(self.serialize(c), "Control updated")

    def recalculate_controls(self, session_id: int, data: dict) -> dict:
        s = self.db.get(UploadResultSession, session_id)
        if not s:
            raise HTTPException(404, "Session not found")
        cutoff = float(data.get("cqCutoff") or s.cqCutoff or runfile.DEFAULT_CQ_CUTOFF)
        s.cqCutoff = cutoff
        for c in self.db.query(ResultControl).filter(ResultControl.uploadResultSessionId == session_id):
            c.result = runfile.call_result(c.ctValue, cutoff)
            amplified = c.ctValue is not None and c.ctValue <= cutoff
            kind = (c.control or "").lower()
            if "ntc" in kind:
                c.comments = "PASS" if not amplified else "FAIL: NTC amplified"
            elif "ctrl" in kind or "pos" in kind:
                c.comments = "PASS" if amplified else "FAIL: Pos Ctrl did not amplify"
        for r in self.db.query(ResultSample).filter(ResultSample.uploadResultSessionId == session_id):
            if r.cqValue is not None or not r.isManual:
                r.result = runfile.call_result(r.cqValue, cutoff)
        self.db.commit()
        self.audit("update", session_id)
        return ok({"id": session_id, "cqCutoff": cutoff}, "Controls recalculated")

    def reject_sample(self, session_id: int, data: dict) -> dict:
        accession = data.get("accessionId")
        reason = data.get("reasonForRejection") or data.get("reason")
        q = self.db.query(ResultSample).filter(ResultSample.uploadResultSessionId == session_id)
        if accession:
            q = q.filter(ResultSample.accessionId == accession)
        for r in q:
            r.isRejected = True
            r.reasonForRejection = reason
        self.db.commit()
        self.audit("update", session_id)
        return ok({"id": session_id}, "Sample rejected")

    def mark_rerun(self, session_id: int, data: dict) -> dict:
        accessions = data.get("accessionIds") or []
        q = self.db.query(ResultSample).filter(ResultSample.uploadResultSessionId == session_id)
        if accessions:
            q = q.filter(ResultSample.accessionId.in_(accessions))
        for r in q:
            r.isRerun = True
        self.db.commit()
        return ok({"id": session_id}, "Marked for rerun")

    def generate_report(self, session_id: int, data: dict) -> dict:
        accessions = data.get("accessionIds") or []
        q = self.db.query(ResultSample).filter(
            ResultSample.uploadResultSessionId == session_id,
            ResultSample.isRejected.isnot(True),
        )
        if accessions:
            q = q.filter(ResultSample.accessionId.in_(accessions))
        for r in q:
            r.isGenerated = True
        s = self.db.get(UploadResultSession, session_id)
        if s:
            s.status = "completed"
        self.db.commit()
        self.audit("update", session_id)
        return ok({"id": session_id}, "Reports generated")

    def discard_session(self, session_id: int) -> dict:
        s = self.db.get(UploadResultSession, session_id)
        if not s:
            raise HTTPException(404, "Session not found")
        s.isDiscarded = True
        s.status = "discarded"
        self.db.commit()
        self.audit("update", session_id)
        return ok({"id": session_id}, "Session discarded")
