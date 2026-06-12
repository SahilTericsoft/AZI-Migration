"""Controllers for the Test Configuration service.

Ported from GkPanelService (PanelController / TestController / BiomarkerController).
Each controller carries the real business logic from the legacy code:
  * code/name uniqueness (case-insensitive), with edit excluding self
  * normalization (code -> UPPER, sampleType/device -> lower, names trimmed)
  * status defaults + draft-aware activation toggle
  * internal-id sequence for panels
  * rich list filtering (createdBy, search, statuses, date range, sort) with
    `createdByDetails` population and a `statusObj`
BaseController supplies only the plumbing (serialize / audit / writable).
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func, or_

from core.api import ok, paginate
from core.controller import BaseController
from core.ids import daily_sequence_id
from core.populate import attach_created_by
from services.test_config.models import Biomarker, CptCode, IcdCode, Panel, Test


def _filters(controller, query, q):
    """Apply the shared catalog filters from a list-query body."""
    return controller.apply_filters(
        query,
        search=q.search,
        statuses=q.statuses,
        created_by_ids=q.createdByIds,
        start_date=q.startDate,
        end_date=q.endDate,
        sort=q.sort,
    )


class PanelController(BaseController):
    model = Panel
    name = "Panel"
    search_fields = ("name", "code")

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        code = (data.get("code") or "").strip().upper()
        if not name or not code:
            raise HTTPException(400, "name and code are required")
        # legacy: reject a panel with the same name + code
        if self.db.query(Panel).filter(Panel.name == name, func.upper(Panel.code) == code).first():
            raise HTTPException(409, "Can Not Add Test Panel With Same code")

        payload = self.writable(data)
        payload.update(
            name=name,
            code=code,
            status=data.get("status") or "completed",
            isActive=data.get("isActive", True),
            internalPanelId=daily_sequence_id(self.db, Panel),
        )
        if data.get("loginUserId") is not None:
            payload["createdBy"] = data["loginUserId"]

        panel = Panel(**payload)
        self.db.add(panel)
        self.db.commit()
        self.db.refresh(panel)
        self.audit("create", panel.id)
        return ok(self.serialize(panel), "Test Panel added successfully")

    def edit(self, panel_id: int, data: dict) -> dict:
        panel = self.db.get(Panel, panel_id)
        if not panel:
            raise HTTPException(404, "can not get List")
        fields = self.writable(data)
        if fields.get("code"):
            fields["code"] = fields["code"].upper()
            if (
                self.db.query(Panel)
                .filter(func.upper(Panel.code) == fields["code"], Panel.id != panel_id)
                .first()
            ):
                raise HTTPException(409, "Can not update test with same code")
        for key, value in fields.items():
            setattr(panel, key, value)
        self.db.commit()
        self.db.refresh(panel)
        self.audit("update", panel_id)
        return ok(self.serialize(panel), "Test details updated successfully")

    def toggle(self, panel_id: int) -> dict:
        panel = self.db.get(Panel, panel_id)
        if not panel:
            raise HTTPException(404, "can not get Profile")
        if panel.status == "draft":
            raise HTTPException(400, "Can Not Activate Draft Profile")
        panel.isActive = not bool(panel.isActive)
        self.db.commit()
        self.audit("update", panel_id)
        message = "Activated" if panel.isActive else "De-Activated"
        return ok({"id": panel_id, "isActive": panel.isActive}, f"Profile {message}")

    def list(self, q) -> dict:
        query = _filters(self, self.db.query(Panel), q)
        return self.paginated(query, q.page, q.limit, status_obj=True, populate_created_by=True)

    def view(self, panel_id: int, is_active=None, attributes=None) -> dict:
        query = self.db.query(Panel).filter(Panel.id == panel_id)
        if is_active is not None:
            query = query.filter(Panel.isActive.is_(is_active))
        panel = query.first()
        if not panel:
            return ok(None, "Test Panel Details")
        data = self.serialize(panel)
        if attributes:
            data = {
                **{k: data.get(k) for k in attributes},
                "id": panel.id,
                "createdBy": panel.createdBy,
            }
        attach_created_by(self.db, [data])
        self.audit("view", panel_id)
        return ok(data, "Test Panel Details")

    def list_lite(self, q) -> dict:
        query = self.db.query(Panel)
        if q.ids:
            query = query.filter(Panel.id.in_(q.ids))
        if q.search and q.search.strip():
            query = query.filter(Panel.name.ilike(f"%{q.search.strip()}%"))
        if q.isActive is not None:
            query = query.filter(Panel.isActive.is_(q.isActive))
        return ok([self.serialize(r) for r in query.all()], "Test Panel List")

    def check_code(self, code: str) -> dict:
        existing = self.db.query(Panel).filter(func.upper(Panel.code) == code.upper()).first()
        return ok(
            self.serialize(existing) if existing else None,
            "Panel Code already exists" if existing else "Panel Code not exists",
        )


class TestController(BaseController):
    model = Test
    name = "Test"
    search_fields = ("name", "code")

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        code = (data.get("code") or "").strip().upper()
        sample_type = (data.get("sampleType") or "").strip().lower()
        if not name or not code or not sample_type:
            raise HTTPException(400, "name, code and sampleType are required")
        # legacy: reject duplicate code, and duplicate (name + sampleType)
        if self.db.query(Test).filter(func.upper(Test.code) == code).first():
            raise HTTPException(409, "Test code already exists")
        if (
            self.db.query(Test)
            .filter(
                func.lower(Test.name) == name.lower(), func.lower(Test.sampleType) == sample_type
            )
            .first()
        ):
            raise HTTPException(409, "Test with same name and sample type already exists")

        payload = self.writable(data)
        payload.update(
            name=name,
            code=code,
            sampleType=sample_type,
            status=data.get("status") or "draft",
            isActive=data.get("isActive", True),
        )
        if data.get("sampleCollectionDeviceName"):
            payload["sampleCollectionDeviceName"] = (
                data["sampleCollectionDeviceName"].strip().lower()
            )
        if data.get("loginUserId") is not None:
            payload["createdBy"] = data["loginUserId"]
        test = Test(**payload)
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)
        self.audit("create", test.id)
        return ok(self.serialize(test), "Test added successfully")

    def edit(self, test_id: int, data: dict) -> dict:
        test = self.db.get(Test, test_id)
        if not test:
            raise HTTPException(404, "can not get List")
        fields = self.writable(data)
        if fields.get("code"):
            fields["code"] = fields["code"].upper()
            if (
                self.db.query(Test)
                .filter(func.upper(Test.code) == fields["code"], Test.id != test_id)
                .first()
            ):
                raise HTTPException(409, "Can not update test with same code")
        if fields.get("sampleType"):
            fields["sampleType"] = fields["sampleType"].lower()
        for key, value in fields.items():
            setattr(test, key, value)
        self.db.commit()
        self.db.refresh(test)
        self.audit("update", test_id)
        return ok(self.serialize(test), "Test details updated successfully")

    def toggle(self, test_id: int) -> dict:
        test = self.db.get(Test, test_id)
        if not test:
            raise HTTPException(404, "can not get Test")
        if test.status == "draft":
            raise HTTPException(400, "Can Not Activate Draft Test")
        test.isActive = not bool(test.isActive)
        self.db.commit()
        self.audit("update", test_id)
        message = "Activated" if test.isActive else "De-Activated"
        return ok({"id": test_id, "isActive": test.isActive}, f"Test {message}")

    def list(self, q) -> dict:
        query = _filters(self, self.db.query(Test), q)
        return self.paginated(query, q.page, q.limit, populate_created_by=True)

    def view(self, test_id: int, attributes=None) -> dict:
        test = self.db.get(Test, test_id)
        if not test:
            return ok(None, "Test Details")
        data = self.serialize(test)
        if attributes:
            data = {
                **{k: data.get(k) for k in attributes},
                "id": test.id,
                "createdBy": test.createdBy,
            }
        attach_created_by(self.db, [data])
        self.audit("view", test_id)
        return ok(data, "Test Details")

    def list_lite(self, q) -> dict:
        query = self.db.query(Test)
        if q.ids:
            query = query.filter(Test.id.in_(q.ids))
        if q.search and q.search.strip():
            query = query.filter(Test.name.ilike(f"%{q.search.strip()}%"))
        if q.isActive is not None:
            query = query.filter(Test.isActive.is_(q.isActive))
        return ok([self.serialize(r) for r in query.all()], "Test List")

    def check_code(self, code: str) -> dict:
        existing = self.db.query(Test).filter(func.upper(Test.code) == code.upper()).first()
        return ok(
            self.serialize(existing) if existing else None,
            "Test Code already exists" if existing else "Test Code not exists",
        )


class BiomarkerController(BaseController):
    model = Biomarker
    name = "Biomarker"
    search_fields = ("name", "code")

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        code = (data.get("code") or "").strip().upper()
        if not name or not code:
            raise HTTPException(400, "name and code are required")
        if self.db.query(Biomarker).filter(func.upper(Biomarker.code) == code).first():
            raise HTTPException(409, "Biomarker code already exists")

        payload = self.writable(data)
        payload.update(
            name=name,
            code=code,
            status=data.get("status") or "draft",
            isActive=data.get("isActive", True),
        )
        if data.get("sampleType"):
            payload["sampleType"] = data["sampleType"].strip().lower()
        if data.get("loginUserId") is not None:
            payload["createdBy"] = data["loginUserId"]
        biomarker = Biomarker(**payload)
        self.db.add(biomarker)
        self.db.commit()
        self.db.refresh(biomarker)
        self.audit("create", biomarker.id)
        return ok(self.serialize(biomarker), "Biomarker added successfully")

    def edit(self, biomarker_id: int, data: dict) -> dict:
        biomarker = self.db.get(Biomarker, biomarker_id)
        if not biomarker:
            raise HTTPException(404, "can not get List")
        fields = self.writable(data)
        if fields.get("code"):
            fields["code"] = fields["code"].upper()
            if (
                self.db.query(Biomarker)
                .filter(func.upper(Biomarker.code) == fields["code"], Biomarker.id != biomarker_id)
                .first()
            ):
                raise HTTPException(409, "Can not update biomarker with same code")
        for key, value in fields.items():
            setattr(biomarker, key, value)
        self.db.commit()
        self.db.refresh(biomarker)
        self.audit("update", biomarker_id)
        return ok(self.serialize(biomarker), "Biomarker updated successfully")

    def toggle(self, biomarker_id: int) -> dict:
        biomarker = self.db.get(Biomarker, biomarker_id)
        if not biomarker:
            raise HTTPException(404, "can not get Biomarker")
        if biomarker.status == "draft":
            raise HTTPException(400, "Can Not Activate Draft Biomarker")
        biomarker.isActive = not bool(biomarker.isActive)
        self.db.commit()
        self.audit("update", biomarker_id)
        message = "Activated" if biomarker.isActive else "De-Activated"
        return ok({"id": biomarker_id, "isActive": biomarker.isActive}, f"Biomarker {message}")

    def list(self, q) -> dict:
        query = _filters(self, self.db.query(Biomarker), q)
        return self.paginated(query, q.page, q.limit, populate_created_by=True)

    def list_lite(self, q) -> dict:
        query = self.db.query(Biomarker)
        if q.ids:
            query = query.filter(Biomarker.id.in_(q.ids))
        if q.search and q.search.strip():
            query = query.filter(Biomarker.name.ilike(f"%{q.search.strip()}%"))
        if q.isActive is not None:
            query = query.filter(Biomarker.isActive.is_(q.isActive))
        return ok([self.serialize(r) for r in query.all()], "Biomarker List")

    def check_code(self, code: str) -> dict:
        existing = (
            self.db.query(Biomarker).filter(func.upper(Biomarker.code) == code.upper()).first()
        )
        return ok(
            self.serialize(existing) if existing else None,
            "Biomarker Code already exists" if existing else "Biomarker Code not exists",
        )


class CptCodeController(BaseController):
    model = CptCode
    name = "CPT code"

    def add(self, data: dict) -> dict:
        cpt = (data.get("cptCode") or "").strip()
        if not cpt:
            raise HTTPException(400, "cptCode is required")
        if self.db.query(CptCode).filter(CptCode.cptCode == cpt).first():
            raise HTTPException(409, "CPT code already exists")
        row = CptCode(**self.writable({**data, "cptCode": cpt}))
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "CPT code added successfully")

    def list(self, q) -> dict:
        query = self.db.query(CptCode)
        if q.search and q.search.strip():
            term = f"%{q.search.strip()}%"
            query = query.filter(or_(CptCode.cptCode.ilike(term), CptCode.description.ilike(term)))
        query = query.order_by(CptCode.createdAt.desc())
        page, limit = q.page or 1, q.limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        return ok(paginate([self.serialize(r) for r in rows], total, page, limit), "CPT code list")


class IcdCodeController(BaseController):
    model = IcdCode
    name = "ICD code"

    def add(self, data: dict) -> dict:
        icd = (data.get("icdCode") or "").strip()
        if not icd:
            raise HTTPException(400, "icdCode is required")
        if self.db.query(IcdCode).filter(IcdCode.icdCode == icd).first():
            raise HTTPException(409, "ICD code already exists")
        row = IcdCode(**self.writable({**data, "icdCode": icd}))
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "ICD code added successfully")

    def list(self, q) -> dict:
        query = self.db.query(IcdCode)
        if q.search and q.search.strip():
            term = f"%{q.search.strip()}%"
            query = query.filter(or_(IcdCode.icdCode.ilike(term), IcdCode.description.ilike(term)))
        query = query.order_by(IcdCode.createdAt.desc())
        page, limit = q.page or 1, q.limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        return ok(paginate([self.serialize(r) for r in rows], total, page, limit), "ICD code list")
