"""Request schemas for the Lab service (ported from GkLabService)."""

from __future__ import annotations

from pydantic import BaseModel

from core.api import MutationBody


class LabCreate(MutationBody):
    name: str
    cliaId: str
    emailId: str
    mobileNumber: str
    addressLine1: str
    zipcode: str
    state: str
    city: str
    labRole: str  # sendLab | receiveLab | sendReceiveLab
    labType: str | None = None
    loginUserId: int | None = None


class LabEdit(MutationBody):
    pass


class LabListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    labTypes: list[str] | None = None
    cities: list[str] | None = None
    statuses: list[str] | None = None
    createdByIds: list[int] | None = None
    startDate: str | None = None
    endDate: str | None = None
    sort: dict[str, str] | None = None


class LabViewIn(BaseModel):
    labId: int | None = None
    code: str | None = None
    labType: str | None = None
    adminId: int | None = None
    isActive: bool | None = None
    appliedAttributes: list[str] | None = None


class LabListLiteQuery(BaseModel):
    search: str | None = None
    isActive: bool | None = None
    labType: str | None = None
    labIds: list[int] | None = None
    appliedAttributes: list[str] | None = None


class LabUserCreate(MutationBody):
    labId: int
    userId: int


class LabUserEdit(MutationBody):
    pass


class AssignLabsIn(BaseModel):
    """Set the exact set of labs assigned to a test/panel/biomarker."""

    labIds: list[int] = []
