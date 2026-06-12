"""Controller for the Sample service (PHI).

Ported from GkTestOrderService/TestOrderSampleController. Real business logic:
  * add validates the parent order, fans the `barcode` out to
    patient/lab barcodes, sets the false-flag defaults, derives `sampleType`
    from test/panel/biomarker details, assigns `sampleCode` = `sm{id}`, and
    increments the order's `numberOfSamplesOrdered` (+ stamps physician on it)
  * accession flow sets isAccessioned/accessionedBy/date/status
  * edit keeps the three barcode fields in sync
All access is audited.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import or_

from core.api import ok, paginate
from core.controller import BaseController
from services.sample.models import OrderSample
from services.test_order.models import Order


def _derive_sample_type(data: dict):
    for key in ("testDetails", "panelDetails", "biomarkerDetails"):
        details = data.get(key)
        if isinstance(details, dict) and details.get("sampleType"):
            return details["sampleType"]
    return data.get("sampleType")


class SampleController(BaseController):
    model = OrderSample
    name = "Sample"
    search_fields = ("sampleCode", "barcode")
    audit_entity = "Sample"

    def add(self, data: dict) -> dict:
        if data.get("orderId") is None:
            raise HTTPException(400, "orderId is required")
        if not data.get("barcode"):
            raise HTTPException(400, "barcode is required")
        order = self.db.get(Order, data["orderId"])
        if not order:
            raise HTTPException(400, "Invalid Order Id")

        barcode = data["barcode"]
        payload = self.writable(data)
        payload.update(
            barcode=barcode,
            patientBarcode=barcode,
            labBarcode=barcode,
            isBarcodeReplaced=False,
            isIntakeFormCompleted=False,
            isAccessioned=False,
            isSendOut=False,
            isPdfGenerated=False,
            sampleType=_derive_sample_type(data),
            createdBy=data.get("loginUserId"),
        )
        sample = OrderSample(**payload)
        self.db.add(sample)
        self.db.commit()
        self.db.refresh(sample)

        sample.sampleCode = f"sm{sample.id}"  # legacy code scheme
        order.numberOfSamplesOrdered = (order.numberOfSamplesOrdered or 0) + 1
        if data.get("physicianId"):
            order.physicianId = data["physicianId"]
        if data.get("physicianDetails"):
            order.physicianDetails = data["physicianDetails"]
        self.db.commit()
        self.audit("create", sample.id)
        return ok(self.serialize(sample), "TestOrderSample added successfully")

    def view(self, sample_id: int) -> dict:
        sample = self.db.get(OrderSample, sample_id)
        if not sample:
            raise HTTPException(404, "Sample not found")
        self.audit("view", sample_id)
        return ok(self.serialize(sample), "Sample Details")

    def edit(self, sample_id: int, data: dict) -> dict:
        sample = self.db.get(OrderSample, sample_id)
        if not sample:
            raise HTTPException(404, "Invalid sample id")
        fields = self.writable(data)
        if fields.get("barcode"):  # keep barcodes in sync
            fields["labBarcode"] = fields["barcode"]
            fields["patientBarcode"] = fields["barcode"]
        for key, value in fields.items():
            setattr(sample, key, value)
        self.db.commit()
        self.db.refresh(sample)
        self.audit("update", sample_id)
        return ok(self.serialize(sample), "Sample updated successfully")

    def accession(self, sample_id: int, accessioned_by: int, status=None, lab_id=None) -> dict:
        sample = self.db.get(OrderSample, sample_id)
        if not sample:
            raise HTTPException(404, "Invalid sample id")
        sample.isAccessioned = True
        sample.accessionedBy = accessioned_by
        sample.accessionedDate = datetime.now(UTC).isoformat()
        if status:
            sample.status = status
        if lab_id:
            sample.accessionedLabId = lab_id
        self.db.commit()
        self.audit("update", sample_id)
        return ok(self.serialize(sample), "Sample accessioned")

    def list(self, q) -> dict:
        self.audit("list", None)  # HIPAA: record PHI list/search access
        query = self.db.query(OrderSample)
        if q.orderId:
            query = query.filter(OrderSample.orderId == q.orderId)
        if q.barcode:
            query = query.filter(OrderSample.barcode == q.barcode)
        if q.barcodes:
            query = query.filter(OrderSample.barcode.in_(q.barcodes))
        if q.statuses:
            query = query.filter(OrderSample.status.in_(q.statuses))
        if q.isAccessioned is not None:
            query = query.filter(OrderSample.isAccessioned.is_(q.isAccessioned))
        if q.search and q.search.strip():
            term = f"%{q.search.strip().lower()}%"
            query = query.filter(
                or_(OrderSample.sampleCode.ilike(term), OrderSample.barcode.ilike(term))
            )
        query = query.order_by(OrderSample.createdAt.desc())

        page, limit = q.page or 1, q.limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        return ok(paginate([self.serialize(r) for r in rows], total, page, limit), "success")

    def list_by_order(self, order_id: int) -> dict:
        rows = self.db.query(OrderSample).filter(OrderSample.orderId == order_id).all()
        return ok([self.serialize(r) for r in rows], "Sample list")
