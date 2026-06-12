"""Patient models (PHI) — migrated from GkPatientService.

`ssn`, `password` and `drivingLicenseNumber` are sensitive and excluded from API
responses (see SENSITIVE). Access is audited and requires authentication.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin

# Fields never returned by the API (HIPAA minimum-necessary).
PATIENT_SENSITIVE = {"ssn", "password", "drivingLicenseNumber"}


class Patient(TimestampMixin, Base):
    __tablename__ = "Patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstName: Mapped[str | None] = mapped_column(String)
    middleName: Mapped[str | None] = mapped_column(String)
    lastName: Mapped[str | None] = mapped_column(String)
    dateOfBirth: Mapped[str | None] = mapped_column(String)
    mobileNumber: Mapped[str | None] = mapped_column(String)
    mobileNumberCode: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String, index=True)  # dedup lookup
    isMobileNumberVerified: Mapped[bool | None] = mapped_column(Boolean)
    gender: Mapped[str | None] = mapped_column(String)
    ethnicity: Mapped[str | None] = mapped_column(String)
    race: Mapped[str | None] = mapped_column(String)
    secondaryMobileNumber: Mapped[str | None] = mapped_column(String)
    secondaryMobileNumberCode: Mapped[str | None] = mapped_column(String)
    businessEmailId: Mapped[str | None] = mapped_column(String)
    businessMobileNumber: Mapped[str | None] = mapped_column(String)
    emailId: Mapped[str | None] = mapped_column(String, index=True)
    addressLine1: Mapped[str | None] = mapped_column(String)
    addressLine2: Mapped[str | None] = mapped_column(String)
    zipcode: Mapped[str | None] = mapped_column(String)
    state: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    county: Mapped[str | None] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)
    prefix: Mapped[str | None] = mapped_column(String)
    suffix: Mapped[str | None] = mapped_column(String)
    aliasName: Mapped[str | None] = mapped_column(String)
    patientAccountNumber: Mapped[str | None] = mapped_column(String)
    ssn: Mapped[str | None] = mapped_column(String)
    nationality: Mapped[str | None] = mapped_column(String)
    maritalStatus: Mapped[str | None] = mapped_column(String)
    degree: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(String)
    isDrivingLicenseAvailable: Mapped[bool | None] = mapped_column(Boolean, default=False)
    drivingLicenseNumber: Mapped[str | None] = mapped_column(String)
    isPatientDead: Mapped[bool | None] = mapped_column(Boolean, default=False)
    timeOfDeath: Mapped[str | None] = mapped_column(String)
    dateOfDeath: Mapped[str | None] = mapped_column(String)
    password: Mapped[str | None] = mapped_column(String)
    heightInInches: Mapped[float | None] = mapped_column(Float)
    heightInFeet: Mapped[float | None] = mapped_column(Float)
    heightInCms: Mapped[float | None] = mapped_column(Float)
    weight: Mapped[float | None] = mapped_column(Float)
    externalPatientId: Mapped[str | None] = mapped_column(String)
    externalOrderId: Mapped[str | None] = mapped_column(String)
    parentAccountId: Mapped[int | None] = mapped_column(Integer)
    specialPatientType: Mapped[str | None] = mapped_column(String)
    isPasswordSet: Mapped[bool | None] = mapped_column(Boolean, default=False)
    isSelfRegistered: Mapped[bool | None] = mapped_column(Boolean, default=False)
    isSpecialPatient: Mapped[bool | None] = mapped_column(Boolean, default=False)
    source: Mapped[str | None] = mapped_column(String, default="adminPortal")
    isInsuranceAvailable: Mapped[bool | None] = mapped_column(Boolean, default=False)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    isDeleted: Mapped[bool | None] = mapped_column(Boolean, default=False)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    AMDPatientId: Mapped[str | None] = mapped_column(String)
    internalPatientId: Mapped[str | None] = mapped_column(String)
    allergieIds: Mapped[list | None] = mapped_column(ARRAY(Integer))


class PatientInsurance(TimestampMixin, Base):
    __tablename__ = "PatientInsurances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patientId: Mapped[int | None] = mapped_column(Integer, index=True)
    firstName: Mapped[str | None] = mapped_column(String)
    middleName: Mapped[str | None] = mapped_column(String)
    lastName: Mapped[str | None] = mapped_column(String)
    dateOfBirth: Mapped[str | None] = mapped_column(String)
    payerId: Mapped[str | None] = mapped_column(String)
    type: Mapped[str | None] = mapped_column(String)
    insuranceCompany: Mapped[str | None] = mapped_column(String)
    insurancePlan: Mapped[str | None] = mapped_column(String)
    policyNumber: Mapped[str | None] = mapped_column(String)
    relationship: Mapped[str | None] = mapped_column(String)
    networkPlanName: Mapped[str | None] = mapped_column(String)
    groupName: Mapped[str | None] = mapped_column(String)
    groupNetwork: Mapped[str | None] = mapped_column(String)
    effectiveDate: Mapped[str | None] = mapped_column(String)
    ipaMedicalGroupName: Mapped[str | None] = mapped_column(String)
    groupId: Mapped[str | None] = mapped_column(String)
    isSameName: Mapped[bool | None] = mapped_column(Boolean)


class Allergy(TimestampMixin, Base):
    __tablename__ = "Allergies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
