"""Request schemas for the Test Order service (ported from GkTestOrderService)."""

from typing import Any

from pydantic import BaseModel

from core.api import MutationBody


class OrderCreate(MutationBody):
    facilityId: int
    locationId: int
    patientId: int
    patientDetails: dict[str, Any]
    loginUserId: int | None = None


class OrderEdit(MutationBody):
    pass


class OrderListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    facilityId: int | None = None
    locationId: int | None = None
    patientId: int | None = None
    statuses: list[str] | None = None
    startDate: str | None = None
    endDate: str | None = None


class OrderResultCreate(MutationBody):
    orderId: int


class OrderResultEdit(MutationBody):
    pass


class GuarantorCreate(MutationBody):
    orderId: str


class GuarantorEdit(MutationBody):
    pass


class PatientVisitCreate(MutationBody):
    orderId: int


class PatientVisitEdit(MutationBody):
    pass
