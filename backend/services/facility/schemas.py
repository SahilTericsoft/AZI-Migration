"""Request schemas for the Facility service (ported from GkFacilityService)."""

from typing import Any

from pydantic import BaseModel

from core.api import MutationBody


class FacilityCreate(MutationBody):
    name: str
    type: str
    addressDetails: dict[str, Any]
    loginUserId: int


class FacilityEdit(MutationBody):
    pass


class FacilityListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    types: list[str] | None = None
    createdByIds: list[int] | None = None
    cities: list[str] | None = None
    states: list[str] | None = None
    statuses: list[str] | None = None
    facilityIds: list[int] | None = None
    facilityId: int | None = None
    startDate: str | None = None
    endDate: str | None = None
    sort: dict[str, str] | None = None


class FacilityViewIn(BaseModel):
    facilityId: int | None = None
    adminId: int | None = None
    appliedAttributes: list[str] | None = None
    isSubDetailsRequired: bool = False
    isPhysicianDetailsRequired: bool = False
    isNumberOfLocationsRequired: bool = False


class FacilityListLiteQuery(BaseModel):
    search: str | None = None
    isActive: bool | None = None
    facilityIds: list[int] | None = None
    appliedAttributes: list[str] | None = None


class AddPhysiciansIn(BaseModel):
    physicians: list[int]


class SetAdminIn(BaseModel):
    adminId: int


class FacilityUserCreate(MutationBody):
    facilityId: int
    userId: int


class FacilityUserEdit(MutationBody):
    pass
