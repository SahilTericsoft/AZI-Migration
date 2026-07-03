"""Controllers for the Lab service.

Ported from GkLabService/LabController. Real business logic:
  * `labRole` is constrained to sendLab/receiveLab/sendReceiveLab
  * `code` = lowercased trimmed name; new labs start `status="draft"`,
    `isActive=false`; `isSdiLab` derived from `labType` (false for externalLab)
  * rich list filters (labType/status/createdBy/search/date/sort) with
    `statusObj` + `createdByDetails`
  * view by id/code/labType/admin with `adminDetails` population
  * toggle; lab-user assignment; lookups by admin / user
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func

from core.api import ok
from core.controller import BaseController
from core.populate import attach_related
from services.lab.models import Lab, LabUser
from services.user_service.models import User

_LAB_ROLES = {"sendLab", "receiveLab", "sendReceiveLab"}


class LabController(BaseController):
    model = Lab
    name = "Lab"

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise HTTPException(400, "name is required")
        if data.get("labRole") not in _LAB_ROLES:
            raise HTTPException(400, "labRole must be sendLab, receiveLab or sendReceiveLab")

        # Duplicate validation: name (case-insensitive) and CLIA ID must be unique.
        if self.db.query(Lab).filter(func.lower(Lab.name) == name.lower()).first():
            raise HTTPException(409, "A lab with this name already exists")
        clia = (data.get("cliaId") or "").strip()
        if clia and self.db.query(Lab).filter(func.upper(Lab.cliaId) == clia.upper()).first():
            raise HTTPException(409, "A lab with this CLIA ID already exists")

        # Labs onboarded through this flow are external partner labs by default.
        lab_type = data.get("labType") or "externalLab"
        payload = self.writable(data)
        payload.update(
            name=name,
            code=name.lower(),
            status="draft",
            isActive=False,
            labType=lab_type,
            isSdiLab=(lab_type != "externalLab"),
            createdBy=data.get("loginUserId"),
        )
        lab = Lab(**payload)
        self.db.add(lab)
        self.db.commit()
        self.db.refresh(lab)
        self.audit("create", lab.id)
        return ok(self.serialize(lab), "Lab added successfully")

    def edit(self, lab_id: int, data: dict) -> dict:
        lab = self.db.get(Lab, lab_id)
        if not lab:
            raise HTTPException(404, "can not get List")
        fields = self.writable(data)
        if fields.get("name"):
            new_name = fields["name"].strip()
            dup = (
                self.db.query(Lab)
                .filter(func.lower(Lab.name) == new_name.lower(), Lab.id != lab_id)
                .first()
            )
            if dup:
                raise HTTPException(409, "A lab with this name already exists")
            fields["code"] = new_name.lower()
        if fields.get("cliaId"):
            dup = (
                self.db.query(Lab)
                .filter(func.upper(Lab.cliaId) == fields["cliaId"].strip().upper(), Lab.id != lab_id)
                .first()
            )
            if dup:
                raise HTTPException(409, "A lab with this CLIA ID already exists")
        for key, value in fields.items():
            setattr(lab, key, value)
        self.db.commit()
        self.db.refresh(lab)
        result = self.serialize(lab)
        attach_related(
            self.db, [result], model=User, source_field="adminId", target_field="adminDetails"
        )
        self.audit("update", lab_id)
        return ok(result, "Lab details updated successfully")

    def view(self, q) -> dict:
        query = self.db.query(Lab)
        if q.labId:
            query = query.filter(Lab.id == q.labId)
        if q.code:
            query = query.filter(Lab.code == q.code)
        if q.labType:
            query = query.filter(Lab.labType == q.labType)
        if q.adminId:
            query = query.filter(Lab.adminId == q.adminId)
        if q.isActive is not None:
            query = query.filter(Lab.isActive.is_(q.isActive))
        lab = query.first()
        if not lab:
            return ok(None, "Lab Details")
        data = self.serialize(lab)
        attach_related(
            self.db, [data], model=User, source_field="adminId", target_field="adminDetails"
        )
        self.audit("view", lab.id)
        return ok(data, "Lab Details")

    def list(self, q) -> dict:
        query = self.db.query(Lab)
        if q.labTypes:
            query = query.filter(Lab.labType.in_(q.labTypes))
        if q.cities:
            query = query.filter(func.lower(Lab.city).in_([c.lower() for c in q.cities]))
        query = self.apply_filters(
            query,
            search=q.search,
            search_fields=("name", "code", "labExternalId", "npiNumber"),
            statuses=q.statuses,
            created_by_ids=q.createdByIds,
            start_date=q.startDate,
            end_date=q.endDate,
            sort=q.sort,
        )
        return self.paginated(query, q.page, q.limit, status_obj=True, populate_created_by=True)

    def toggle(self, lab_id: int) -> dict:
        lab = self.db.get(Lab, lab_id)
        if not lab:
            raise HTTPException(404, "can not get List")
        lab.isActive = not bool(lab.isActive)
        self.db.commit()
        self.audit("update", lab_id)
        message = "Activated" if lab.isActive else "De-activated"
        return ok({"id": lab_id, "isActive": lab.isActive}, f"Lab {message}")

    def list_lite(self, q) -> dict:
        query = self.db.query(Lab)
        if q.search and q.search.strip():
            query = query.filter(Lab.name.ilike(f"%{q.search.strip().lower()}%"))
        if q.isActive is not None:
            query = query.filter(Lab.isActive.is_(q.isActive))
        if q.labType:
            query = query.filter(Lab.labType == q.labType)
        if q.labIds:
            query = query.filter(Lab.id.in_(q.labIds))
        return ok([self.serialize(r) for r in query.all()], "Lab List")

    def get_by_admin(self, admin_id: int) -> dict:
        lab = self.db.query(Lab).filter(Lab.adminId == admin_id).first()
        return ok(self.serialize(lab) if lab else None, "Lab Details")


class LabUserController(BaseController):
    model = LabUser
    name = "Lab user"

    def add_user(self, data: dict) -> dict:
        existing = (
            self.db.query(LabUser)
            .filter(LabUser.labId == data.get("labId"), LabUser.userId == data.get("userId"))
            .first()
        )
        if existing:
            return ok(self.serialize(existing), "Lab user already linked")
        return self.create(data)

    def list_by_lab(self, lab_id: int) -> dict:
        rows = self.db.query(LabUser).filter(LabUser.labId == lab_id).all()
        return ok([self.serialize(r) for r in rows], "Lab user list")
