"""Controllers for the Test Order service (PHI).

Ported from GkTestOrderService. Real business logic:
  * order `code` = `gk{id}` assigned after insert; sample counters initialised;
    `status="draft"`, `source` defaulted to "web"
  * rich list filters incl. patient search via `patientDetails ->> …`, with the
    patient block trimmed to id/name/gender/dob on output
  * results / guarantors / visits scoped by order; guarantor SSN masked
All access is audited.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import or_

from core.api import ok, paginate
from core.controller import BaseController
from services.test_order.models import (
    GUARANTOR_SENSITIVE,
    Guarantor,
    Order,
    OrderResult,
    PatientVisit,
)

_PATIENT_VIEW_FIELDS = ("id", "firstName", "lastName", "gender", "dateOfBirth")


class OrderController(BaseController):
    model = Order
    name = "Order"
    audit_entity = "Order"

    def add(self, data: dict) -> dict:
        for field in ("facilityId", "locationId", "patientId"):
            if data.get(field) is None:
                raise HTTPException(400, f"{field} is required")
        if not data.get("patientDetails"):
            raise HTTPException(400, "patientDetails is required")

        payload = self.writable(data)
        payload.update(
            numberOfSamplesOrdered=0,
            numberOfSamplesResulted=0,
            status=data.get("status") or "draft",
            source=data.get("source") or "web",
            isPriorityOrder=bool(data.get("isPriorityOrder")),
            createdBy=data.get("loginUserId"),
        )
        order = Order(**payload)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        order.code = f"gk{order.id}"  # legacy code scheme
        self.db.commit()
        self.audit("create", order.id)
        return ok(self.serialize(order), "Order added successfully")

    def view(self, order_id: int) -> dict:
        order = self.db.get(Order, order_id)
        if not order:
            raise HTTPException(404, "Order not found")
        self.audit("view", order_id)
        return ok(self.serialize(order), "Order Details")

    def edit(self, order_id: int, data: dict) -> dict:
        order = self.db.get(Order, order_id)
        if not order:
            raise HTTPException(404, "Invalid order id")
        for key, value in self.writable(data).items():
            setattr(order, key, value)
        self.db.commit()
        self.db.refresh(order)
        self.audit("update", order_id)
        return ok(self.serialize(order), "Order details edited successfully")

    def list(self, q) -> dict:
        self.audit("list", None)  # HIPAA: record PHI list/search access
        query = self.db.query(Order)
        if q.facilityId:
            query = query.filter(Order.facilityId == q.facilityId)
        if q.locationId:
            query = query.filter(Order.locationId == q.locationId)
        if q.patientId:
            query = query.filter(Order.patientId == q.patientId)
        if q.statuses:
            query = query.filter(Order.status.in_(q.statuses))
        if q.search and q.search.strip():
            term = f"%{q.search.strip().lower()}%"
            query = query.filter(
                or_(
                    Order.code.ilike(term),
                    Order.patientDetails.op("->>")("firstName").ilike(term),
                    Order.patientDetails.op("->>")("lastName").ilike(term),
                    Order.patientDetails.op("->>")("code").ilike(term),
                )
            )
        if q.startDate and q.endDate:
            start = datetime.fromisoformat(q.startDate)
            end = datetime.fromisoformat(q.endDate) + timedelta(days=1)
            query = query.filter(Order.createdAt.between(start, end))
        query = query.order_by(Order.createdAt.desc())

        page, limit = q.page or 1, q.limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        docs = []
        for order in rows:
            data = self.serialize(order)
            pd = data.get("patientDetails")
            if isinstance(pd, dict):
                data["patientDetails"] = {k: pd.get(k) for k in _PATIENT_VIEW_FIELDS}
            docs.append(data)
        return ok(paginate(docs, total, page, limit), "success")


class OrderResultController(BaseController):
    model = OrderResult
    name = "Order result"
    audit_entity = "OrderResult"

    def list_by_order(self, order_id: int) -> dict:
        rows = self.db.query(OrderResult).filter(OrderResult.orderId == order_id).all()
        self.audit("view", order_id)
        return ok([self.serialize(r) for r in rows], "Order result list")


class GuarantorController(BaseController):
    model = Guarantor
    name = "Guarantor"
    sensitive = GUARANTOR_SENSITIVE
    search_fields = ("familyName", "givenName")
    audit_entity = "Guarantor"

    def get_by_order(self, order_id: str) -> dict:
        row = self.db.query(Guarantor).filter(Guarantor.orderId == order_id).first()
        return ok(self.serialize(row) if row else None, "Guarantor details")


class PatientVisitController(BaseController):
    model = PatientVisit
    name = "Patient visit"
    audit_entity = "PatientVisit"

    def get_by_order(self, order_id: int) -> dict:
        row = self.db.query(PatientVisit).filter(PatientVisit.orderId == order_id).first()
        return ok(self.serialize(row) if row else None, "Patient visit details")
