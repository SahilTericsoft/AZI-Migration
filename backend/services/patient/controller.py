"""Controllers for the Patient service (PHI).

Ported from GkPatientService/PatientController. Real business logic:
  * deterministic `code` (firstName+lastName+dob, stripped/lowercased) used for
    duplicate detection — add returns the existing patient instead of creating
  * name / ssn / degree / maritalStatus / aliasName normalized to lowercase
  * `internalPatientId` sequence, `isActive/isDeleted/isPasswordSet` defaults
  * allergy-id union-merge on edit
  * soft delete + recover; rich search (code/name/mobile, ILIKE) excluding
    deleted unless asked
All access is audited; ssn/password/drivingLicenseNumber are never returned.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import asc, desc, or_

from core.api import ok, paginate
from core.controller import BaseController
from core.ids import daily_sequence_id
from services.patient.models import (
    PATIENT_SENSITIVE,
    Allergy,
    Patient,
    PatientInsurance,
)

_LOWER_FIELDS = (
    "firstName",
    "lastName",
    "middleName",
    "suffix",
    "prefix",
    "ssn",
    "degree",
    "maritalStatus",
    "aliasName",
)


def patient_unique_code(first: str, last: str, dob: str) -> str:
    dob_clean = re.sub(r"[/-]", "", dob or "").strip().lower()
    f = (first or "").strip().replace(" ", "").lower()
    last_clean = (last or "").strip().replace(" ", "").lower()
    return f + last_clean + dob_clean


class PatientController(BaseController):
    model = Patient
    name = "Patient"
    sensitive = PATIENT_SENSITIVE
    audit_entity = "Patient"

    @staticmethod
    def _normalize(data: dict) -> dict:
        for field in _LOWER_FIELDS:
            if data.get(field):
                data[field] = str(data[field]).lower()
        return data

    def add(self, data: dict) -> dict:
        first, last, dob = data.get("firstName"), data.get("lastName"), data.get("dateOfBirth")
        if not first or not last or not dob:
            raise HTTPException(400, "firstName, lastName and dateOfBirth are required")
        code = patient_unique_code(first, last, dob)

        existing = self.db.query(Patient).filter(Patient.code == code).first()
        if existing:
            self.audit("view", existing.id)
            return ok(self.serialize(existing), "Patient Already Exists")

        payload = self._normalize(self.writable(data))
        payload.update(
            code=code,
            isActive=True,
            isDeleted=False,
            isPasswordSet=False,
            internalPatientId=daily_sequence_id(self.db, Patient),
        )
        if data.get("loginUserId") is not None:
            payload["createdBy"] = data["loginUserId"]

        patient = Patient(**payload)
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        self.audit("create", patient.id)
        return ok(self.serialize(patient), "Patient added successfully")

    def view(self, patient_id: int) -> dict:
        patient = self.db.get(Patient, patient_id)
        if not patient or patient.isDeleted:
            raise HTTPException(404, "Patient not found")
        self.audit("view", patient_id)
        return ok(self.serialize(patient), "Patient Details")

    def edit(self, patient_id: int, data: dict) -> dict:
        patient = self.db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(404, "Invalid patient id")
        fields = self._normalize(self.writable(data))

        # allergy ids union-merge (legacy behaviour)
        if data.get("allergieIds"):
            merged = list(
                dict.fromkeys(list(patient.allergieIds or []) + list(data["allergieIds"]))
            )
            fields["allergieIds"] = merged

        # recompute the duplicate code if any identity field changed, reject clash
        new_first = fields.get("firstName", patient.firstName)
        new_last = fields.get("lastName", patient.lastName)
        new_dob = fields.get("dateOfBirth", patient.dateOfBirth)
        new_code = patient_unique_code(new_first, new_last, new_dob)
        if new_code != patient.code:
            clash = (
                self.db.query(Patient)
                .filter(Patient.code == new_code, Patient.id != patient_id)
                .first()
            )
            if clash:
                raise HTTPException(409, "Patient already exists")
            fields["code"] = new_code

        for key, value in fields.items():
            setattr(patient, key, value)
        self.db.commit()
        self.db.refresh(patient)
        self.audit("update", patient_id)
        return ok(self.serialize(patient), "Patient details edited successfully")

    def toggle(self, patient_id: int) -> dict:
        patient = self.db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(404, "Invalid patient id")
        patient.isActive = not bool(patient.isActive)
        self.db.commit()
        self.audit("update", patient_id)
        message = "Activated" if patient.isActive else "De-Activated"
        return ok({"id": patient_id, "isActive": patient.isActive}, f"Patient {message}")

    def soft_delete(self, patient_id: int) -> dict:
        patient = self.db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(404, "Invalid patient id")
        patient.isDeleted = True
        patient.isActive = False
        self.db.commit()
        self.audit("delete", patient_id)
        return ok({"id": patient_id}, "Patient deleted")

    def recover(self, patient_id: int) -> dict:
        patient = self.db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(404, "Invalid patient id")
        patient.isDeleted = False
        patient.isActive = True
        self.db.commit()
        self.audit("update", patient_id)
        return ok({"id": patient_id}, "Patient recovered")

    def validate(self, first: str, last: str, dob: str) -> dict:
        code = patient_unique_code(first, last, dob)
        existing = self.db.query(Patient).filter(Patient.code == code).first()
        if existing:
            return ok(self.serialize(existing), "Patient Already Exists")
        return ok(None, "Patient available")

    def list(self, q) -> dict:
        self.audit("list", None)  # HIPAA: record PHI list/search access
        query = self.db.query(Patient)
        want_deleted = bool(q.statuses and "deleted" in q.statuses)
        query = query.filter(
            Patient.isDeleted.is_(True) if want_deleted else Patient.isDeleted.isnot(True)
        )
        if q.statuses:
            if "active" in q.statuses:
                query = query.filter(Patient.isActive.is_(True))
            if "inactive" in q.statuses:
                query = query.filter(Patient.isActive.is_(False))
        if q.genders:
            query = query.filter(Patient.gender.in_(q.genders))
        if q.createdByIds:
            query = query.filter(Patient.createdBy.in_(q.createdByIds))
        if q.specialPatientTypes:
            query = query.filter(Patient.specialPatientType.in_(q.specialPatientTypes))
        if q.search and q.search.strip():
            term = f"%{q.search.strip().lower()}%"
            query = query.filter(
                or_(
                    Patient.code.ilike(term),
                    Patient.firstName.ilike(term),
                    Patient.lastName.ilike(term),
                    Patient.middleName.ilike(term),
                    Patient.mobileNumber.ilike(term),
                )
            )
        if q.startDate and q.endDate:
            start = datetime.fromisoformat(q.startDate)
            end = datetime.fromisoformat(q.endDate) + timedelta(days=1)
            query = query.filter(Patient.createdAt.between(start, end))
        if q.sort:
            for field, direction in q.sort.items():
                if hasattr(Patient, field):
                    col = getattr(Patient, field)
                    query = query.order_by(
                        desc(col) if str(direction).upper() == "DESC" else asc(col)
                    )
        else:
            query = query.order_by(Patient.createdAt.desc())

        page, limit = q.page or 1, q.limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        return ok(paginate([self.serialize(r) for r in rows], total, page, limit), "success")


class PatientInsuranceController(BaseController):
    model = PatientInsurance
    name = "Patient insurance"
    audit_entity = "PatientInsurance"

    def list_by_patient(self, patient_id: int) -> dict:
        rows = (
            self.db.query(PatientInsurance)
            .filter(PatientInsurance.patientId == patient_id)
            .order_by(PatientInsurance.createdAt.desc())
            .all()
        )
        self.audit("view", patient_id)
        return ok([self.serialize(r) for r in rows], "Patient insurance list")


class AllergyController(BaseController):
    model = Allergy
    name = "Allergy"
    search_fields = ("name",)
