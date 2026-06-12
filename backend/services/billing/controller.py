"""Controllers for the Billing reference service.

Real logic: insurer/clearing-house uniqueness, active defaults, and
clearing-house-scoped insurance lookups.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func

from core.api import ok
from core.controller import BaseController
from services.billing.models import ClearingHouse, ClearingHouseInsurance, Insurer


class InsurerController(BaseController):
    model = Insurer
    name = "Insurer"
    search_fields = ("title", "code", "payerId")

    def add(self, data: dict) -> dict:
        title = (data.get("title") or "").strip()
        if not title:
            raise HTTPException(400, "title is required")
        if self.db.query(Insurer).filter(func.lower(Insurer.title) == title.lower()).first():
            raise HTTPException(409, "Insurer already exists")
        row = Insurer(**self.writable({**data, "title": title}))
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "Insurer added successfully")


class ClearingHouseController(BaseController):
    model = ClearingHouse
    name = "Clearing house"
    search_fields = ("clearingHouse", "clearingHouseCode")

    def add(self, data: dict) -> dict:
        payload = self.writable(data)
        payload.setdefault("isActive", True)
        row = ClearingHouse(**payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "Clearing house added successfully")


class ClearingHouseInsuranceController(BaseController):
    model = ClearingHouseInsurance
    name = "Clearing house insurance"
    search_fields = ("payerName", "payerId")

    def list_by_clearing_house(self, clearing_house_id: int) -> dict:
        rows = (
            self.db.query(ClearingHouseInsurance)
            .filter(ClearingHouseInsurance.clearingHouseId == clearing_house_id)
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Clearing house insurance list")
