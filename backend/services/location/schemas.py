"""Request schemas for the Location service (ported from GkFacilityService)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from core.api import MutationBody


class LocationCreate(MutationBody):
    name: str
    type: str
    addressDetails: dict[str, Any]
    facilityId: int
    labId: int
    loginUserId: int
    isExternalLabFlow: bool = False


class LocationEdit(MutationBody):
    pass


class LocationListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    types: list[str] | None = None
    createdByIds: list[int] | None = None
    cities: list[str] | None = None
    states: list[str] | None = None
    statuses: list[str] | None = None
    facilityId: int | None = None
    facilityIds: list[int] | None = None
    labId: int | None = None
    startDate: str | None = None
    endDate: str | None = None
    sort: dict[str, str] | None = None


class LocationViewIn(BaseModel):
    locationId: int | None = None
    adminId: int | None = None
    appliedAttributes: list[str] | None = None
    isSubDetailsRequired: bool = False


class LocationListLiteQuery(BaseModel):
    search: str | None = None
    isActive: bool | None = None
    facilityId: int | None = None
    locationIds: list[int] | None = None
    appliedAttributes: list[str] | None = None


class AddPhysicianIn(BaseModel):
    physicianId: int


class AddBulkPhysiciansIn(BaseModel):
    physicianIds: list[int]


class LocationUserCreate(MutationBody):
    locationId: int
    userId: int


class LocationUserEdit(MutationBody):
    pass


class LocationPhysicianCreate(MutationBody):
    locationId: int
    physicianId: int


class LocationPhysicianEdit(MutationBody):
    pass
