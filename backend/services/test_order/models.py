"""Test Order models (PHI) — migrated from GkTestOrderService / GkBulkUploadService."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Order(TimestampMixin, Base):
    __tablename__ = "Orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(String, index=True)
    facilityId: Mapped[int | None] = mapped_column(Integer)
    locationId: Mapped[int | None] = mapped_column(Integer)
    facilityDetails: Mapped[dict | None] = mapped_column(JSON)
    locationDetails: Mapped[dict | None] = mapped_column(JSON)
    patientId: Mapped[int | None] = mapped_column(Integer, index=True)
    externalPatientId: Mapped[str | None] = mapped_column(String)
    externalOrderId: Mapped[str | None] = mapped_column(String)
    patientDetails: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str | None] = mapped_column(String)
    numberOfSamplesOrdered: Mapped[int | None] = mapped_column(Integer)
    numberOfSamplesResulted: Mapped[int | None] = mapped_column(Integer)
    physicianId: Mapped[int | None] = mapped_column(Integer)
    physicianDetails: Mapped[dict | None] = mapped_column(JSON)
    labDetails: Mapped[dict | None] = mapped_column(JSON)
    isPriorityOrder: Mapped[bool | None] = mapped_column(Boolean)
    isConsentSigned: Mapped[bool | None] = mapped_column(Boolean)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    createdByDetails: Mapped[dict | None] = mapped_column(JSON)
    source: Mapped[str | None] = mapped_column(String)
    orderPlacedTime: Mapped[str | None] = mapped_column(String)
    # Uploaded order docs: [{attachmentName, secureUrl, mimeType, size}].
    attachments: Mapped[list | None] = mapped_column(JSON)
    # --- Added to match legacy AI-Portal V2 Orders schema (MIGRATION_GAPS.md) ---
    labId: Mapped[int | None] = mapped_column(Integer)
    primaryInsuranceId: Mapped[int | None] = mapped_column(Integer)
    secondaryInsuranceId: Mapped[int | None] = mapped_column(Integer)
    tertiaryInsuranceId: Mapped[int | None] = mapped_column(Integer)
    billingMode: Mapped[str | None] = mapped_column(String)
    icdCodes: Mapped[list | None] = mapped_column(ARRAY(String))
    icdCodeDetails: Mapped[list | None] = mapped_column(ARRAY(JSON))
    allergies: Mapped[list | None] = mapped_column(ARRAY(String))
    allergieIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    medicationDetails: Mapped[list | None] = mapped_column(ARRAY(JSON))
    integrationDetails: Mapped[dict | None] = mapped_column(JSON)
    internalOrderId: Mapped[str | None] = mapped_column(String)
    rejectionDetails: Mapped[dict | None] = mapped_column(JSON)
    rawOrderResultData: Mapped[dict | None] = mapped_column(JSON)
    priorityOrderStatus: Mapped[str | None] = mapped_column(String)
    resultSentToPatient: Mapped[bool | None] = mapped_column(Boolean)
    externalReferenceNumber: Mapped[str | None] = mapped_column(String)
    sampleDraftDetails: Mapped[dict | None] = mapped_column(JSON)
    isDiscarded: Mapped[bool | None] = mapped_column(Boolean)
    testOrderReportTitle: Mapped[str | None] = mapped_column(String)


class OrderResult(TimestampMixin, Base):
    __tablename__ = "OrderResults"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orderId: Mapped[int | None] = mapped_column(Integer, index=True)
    sampleId: Mapped[int | None] = mapped_column(Integer, index=True)
    pdfGeneratedDate: Mapped[str | None] = mapped_column(String)
    pdfDetails: Mapped[dict | None] = mapped_column(JSON)
    results: Mapped[dict | None] = mapped_column(JSON)
    loginUserId: Mapped[int | None] = mapped_column(Integer)
    resultedMode: Mapped[str | None] = mapped_column(String)


class Guarantor(TimestampMixin, Base):
    __tablename__ = "Guarantors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orderId: Mapped[str | None] = mapped_column(String, index=True)
    number: Mapped[str | None] = mapped_column(String)
    familyName: Mapped[str | None] = mapped_column(String)
    givenName: Mapped[str | None] = mapped_column(String)
    secondAndFurtherGivenName: Mapped[str | None] = mapped_column(String)
    addressLine1: Mapped[str | None] = mapped_column(String)
    addressLine2: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    state: Mapped[str | None] = mapped_column(String)
    zipcode: Mapped[str | None] = mapped_column(String)
    homePhone: Mapped[str | None] = mapped_column(String)
    phoneNumberBusiness: Mapped[str | None] = mapped_column(String)
    dateOfBirth: Mapped[str | None] = mapped_column(String)
    sex: Mapped[str | None] = mapped_column(String)
    relationshipIdentifier: Mapped[str | None] = mapped_column(String)
    ssnNumber: Mapped[str | None] = mapped_column(String)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    updatedBy: Mapped[int | None] = mapped_column(Integer)


class PatientVisit(TimestampMixin, Base):
    __tablename__ = "PatientVisits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orderId: Mapped[int | None] = mapped_column(Integer, index=True)
    attendingDoctorId: Mapped[int | None] = mapped_column(Integer)
    attendingDoctorFamilyName: Mapped[str | None] = mapped_column(String)
    attendingDoctorGivenName: Mapped[str | None] = mapped_column(String)
    attendingDoctorSecondAndFurtherGivenName: Mapped[str | None] = mapped_column(String)
    attendingDoctorDegree: Mapped[str | None] = mapped_column(String)
    referringDoctorId: Mapped[int | None] = mapped_column(Integer)
    referringDoctorFamilyName: Mapped[str | None] = mapped_column(String)
    referringDoctorGivenName: Mapped[str | None] = mapped_column(String)
    referringDoctorSecondAndFurtherGivenName: Mapped[str | None] = mapped_column(String)
    referringDoctorDegree: Mapped[str | None] = mapped_column(String)
    hospitalService: Mapped[str | None] = mapped_column(String)
    patientType: Mapped[str | None] = mapped_column(String)
    visitNumberId: Mapped[str | None] = mapped_column(String)
    financialClass: Mapped[str | None] = mapped_column(String)
    admitDateTime: Mapped[str | None] = mapped_column(String)
    dischargeDateTime: Mapped[str | None] = mapped_column(String)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    updatedBy: Mapped[int | None] = mapped_column(Integer)


GUARANTOR_SENSITIVE = {"ssnNumber"}
