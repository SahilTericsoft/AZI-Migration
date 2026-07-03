"""Request schemas for the Lab Operations service."""

from __future__ import annotations

from pydantic import BaseModel

from core.api import MutationBody


class DepartmentCreate(MutationBody):
    name: str


class DepartmentUpdate(MutationBody):
    pass


class InstrumentCreate(MutationBody):
    instrument: str
    loginUserId: int | None = None


class InstrumentUpdate(MutationBody):
    pass


class InstrumentSearchQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    labId: int | None = None
    categories: list[str] | None = None
    statuses: list[str] | None = None
    createdByIds: list[int] | None = None
    startDate: str | None = None
    endDate: str | None = None


class MaintenanceLogIn(MutationBody):
    date: str | None = None
    performedBy: str | None = None
    activity: str | None = None
    notes: str | None = None


class ReagentCreate(MutationBody):
    name: str


class ReagentUpdate(MutationBody):
    pass


class SopCreate(MutationBody):
    sop_name: str


class SopUpdate(MutationBody):
    pass


class ValidationCreate(MutationBody):
    name_of_document: str


class ValidationUpdate(MutationBody):
    pass


class LabSessionCreate(MutationBody):
    pass


class LabSessionUpdate(MutationBody):
    pass


class OrderReportCreate(MutationBody):
    name: str
    testIds: list[int]


class OrderReportListQuery(MutationBody):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    createdByIds: list[int] | None = None
    startDate: str | None = None
    endDate: str | None = None
