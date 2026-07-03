"""Request schemas for the Patient service (ported from GkPatientService)."""

from __future__ import annotations

from pydantic import BaseModel

from core.api import MutationBody


class PatientCreate(MutationBody):
    firstName: str
    lastName: str
    dateOfBirth: str
    loginUserId: int | None = None


class PatientEdit(MutationBody):
    pass


class PatientListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    genders: list[str] | None = None
    cities: list[str] | None = None
    createdByIds: list[int] | None = None
    specialPatientTypes: list[str] | None = None
    statuses: list[str] | None = None  # active / inactive / deleted
    isAlertPatientFlag: bool | None = None
    facilityIds: list[int] | None = None
    locationIds: list[int] | None = None
    panelIds: list[int] | None = None
    testIds: list[int] | None = None
    startDate: str | None = None
    endDate: str | None = None
    sort: dict[str, str] | None = None


class ValidatePatientIn(BaseModel):
    firstName: str
    lastName: str
    dateOfBirth: str


class PatientInsuranceCreate(MutationBody):
    patientId: int


class PatientInsuranceEdit(MutationBody):
    pass


class AllergyCreate(MutationBody):
    name: str


class AllergyEdit(MutationBody):
    pass
