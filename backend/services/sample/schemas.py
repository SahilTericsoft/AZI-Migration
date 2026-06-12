"""Request schemas for the Sample service (ported from GkTestOrderService)."""

from typing import Any

from pydantic import BaseModel

from core.api import MutationBody


class SampleCreate(MutationBody):
    orderId: int
    barcode: str
    physicianId: int | None = None
    panelId: int | None = None
    testDetails: dict[str, Any] | None = None
    panelDetails: dict[str, Any] | None = None
    biomarkerDetails: dict[str, Any] | None = None
    loginUserId: int | None = None


class SampleEdit(MutationBody):
    pass


class SampleListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    orderId: int | None = None
    barcode: str | None = None
    barcodes: list[str] | None = None
    statuses: list[str] | None = None
    isAccessioned: bool | None = None


class AccessionIn(BaseModel):
    accessionedBy: int
    status: str | None = None
    accessionedLabId: int | None = None
