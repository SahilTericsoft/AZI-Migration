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

import csv
import io
import re
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import asc, desc, func, or_

from core.api import ok, paginate
from core.controller import BaseController
from core.ids import daily_sequence_id
from core.populate import attach_related
from services.patient.models import (
    PATIENT_SENSITIVE,
    Allergy,
    Patient,
    PatientInsurance,
)
from services.sample.models import OrderSample
from services.test_config.models import Panel
from services.test_order.models import Order

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
        if q.cities:
            query = query.filter(func.lower(Patient.city).in_([c.lower() for c in q.cities]))
        if q.createdByIds:
            query = query.filter(Patient.createdBy.in_(q.createdByIds))
        if q.specialPatientTypes:
            query = query.filter(Patient.specialPatientType.in_(q.specialPatientTypes))

        # Order/sample-derived filters (facility, location, panel, test) and the
        # alert-limit flag all resolve to a set of patient ids we intersect in.
        id_sets: list[set[int]] = []
        if q.facilityIds or q.locationIds or q.panelIds or q.testIds:
            id_sets.append(
                self._order_patient_ids(
                    facility_ids=q.facilityIds,
                    location_ids=q.locationIds,
                    panel_ids=self._resolve_panel_ids(q.panelIds, q.testIds),
                )
            )
        if q.isAlertPatientFlag:
            id_sets.append(self._flagged_patient_ids())
        if id_sets:
            allowed = set.intersection(*id_sets) if len(id_sets) > 1 else id_sets[0]
            query = query.filter(Patient.id.in_(allowed or {0}))
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
        data = [self.serialize(r) for r in rows]
        # Populate "Added By" for the list (createdByDetails).
        from services.user_service.models import User

        attach_related(
            self.db, data, model=User, source_field="createdBy", target_field="createdByDetails"
        )
        self._attach_linked(data)
        return ok(paginate(data, total, page, limit), "success")

    # ---- order/sample-derived helpers ----
    def _resolve_panel_ids(
        self, panel_ids: list[int] | None, test_ids: list[int] | None
    ) -> list[int] | None:
        """Combine explicit panel ids with the panels that contain the given tests."""
        result: set[int] = set(panel_ids or [])
        if test_ids:
            wanted = set(test_ids)
            for panel in self.db.query(Panel.id, Panel.testIds).all():
                if wanted & set(panel.testIds or []):
                    result.add(panel.id)
            if not result:
                return [0]  # no panel matches → match nothing
        return list(result) if result else None

    def _order_patient_ids(
        self,
        *,
        facility_ids: list[int] | None = None,
        location_ids: list[int] | None = None,
        panel_ids: list[int] | None = None,
    ) -> set[int]:
        query = self.db.query(Order.patientId)
        if panel_ids is not None:
            query = query.join(OrderSample, OrderSample.orderId == Order.id).filter(
                OrderSample.panelId.in_(panel_ids)
            )
        if facility_ids:
            query = query.filter(Order.facilityId.in_(facility_ids))
        if location_ids:
            query = query.filter(Order.locationId.in_(location_ids))
        return {pid for (pid,) in query.distinct() if pid}

    def _flag_patient_sets(self) -> tuple[set[int], set[int]]:
        """Return (alerted, maxed) patient ids based on this month's panel orders.

        Each panel may set a per-patient monthly ordering limit (alertLimit /
        maxLimit). A patient whose order count for a limited panel this month
        reaches maxLimit is "maxed"; reaching alertLimit (but not maxLimit) is
        "alerted". A patient maxed on any panel takes precedence over alerted.
        """
        limits = {
            p.id: (p.alertLimit, p.maxLimit)
            for p in self.db.query(Panel.id, Panel.alertLimit, Panel.maxLimit).filter(
                Panel.hasOrderingLimit.is_(True), Panel.maxLimit.isnot(None)
            )
        }
        if not limits:
            return set(), set()

        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        counts = (
            self.db.query(Order.patientId, OrderSample.panelId, func.count().label("cnt"))
            .join(OrderSample, OrderSample.orderId == Order.id)
            .filter(
                Order.createdAt >= month_start,
                Order.patientId.isnot(None),
                OrderSample.panelId.isnot(None),
            )
            .group_by(Order.patientId, OrderSample.panelId)
            .all()
        )
        alerted: set[int] = set()
        maxed: set[int] = set()
        for patient_id, panel_id, cnt in counts:
            lim = limits.get(panel_id)
            if not lim:
                continue
            alert_lim, max_lim = lim
            if max_lim and cnt >= max_lim:
                maxed.add(patient_id)
            elif alert_lim and cnt >= alert_lim:
                alerted.add(patient_id)
        return alerted, maxed

    def _flagged_patient_ids(self) -> set[int]:
        alerted, maxed = self._flag_patient_sets()
        return alerted | maxed

    def flagged_count(self) -> dict:
        """Counts of patients who crossed the alert and the (stricter) max limit."""
        alerted, maxed = self._flag_patient_sets()
        return ok(
            {"alertLimitCount": len(alerted - maxed), "maxLimitCount": len(maxed)},
            "Flagged patient counts",
        )

    def _attach_linked(self, data: list[dict]) -> None:
        """Attach distinct linked facilities/locations from the patients' orders."""
        ids = [d["id"] for d in data if d.get("id")]
        if not ids:
            return
        rows = (
            self.db.query(
                Order.patientId,
                Order.facilityId,
                Order.facilityDetails,
                Order.locationId,
                Order.locationDetails,
            )
            .filter(Order.patientId.in_(ids))
            .all()
        )
        fac: dict[int, dict[int, dict]] = defaultdict(dict)
        loc: dict[int, dict[int, dict]] = defaultdict(dict)
        for pid, fid, fdet, lid, ldet in rows:
            if fid:
                fdet = fdet or {}
                fac[pid][fid] = {"id": fid, "name": fdet.get("name") or fdet.get("code")}
            if lid:
                ldet = ldet or {}
                loc[pid][lid] = {"id": lid, "name": ldet.get("name") or ldet.get("code")}
        for d in data:
            d["linkedFacilities"] = list(fac.get(d["id"], {}).values())
            d["linkedLocations"] = list(loc.get(d["id"], {}).values())

    def bulk_upload(self, content: bytes, login_user_id: int | None) -> dict:
        """Create patients from a CSV (firstName,lastName,dateOfBirth required)."""
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(400, "File must be UTF-8 encoded CSV")
        reader = csv.DictReader(io.StringIO(text))
        created, skipped, errors = 0, 0, []
        for i, raw in enumerate(reader, start=2):  # row 1 is the header
            row = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
            first, last, dob = row.get("firstName"), row.get("lastName"), row.get("dateOfBirth")
            if not first or not last or not dob:
                errors.append({"row": i, "error": "firstName, lastName and dateOfBirth are required"})
                continue
            code = patient_unique_code(first, last, dob)
            if self.db.query(Patient).filter(Patient.code == code).first():
                skipped += 1
                continue
            allowed = {k: v for k, v in row.items() if v != ""}
            payload = self._normalize(self.writable(allowed))
            payload.update(
                code=code,
                isActive=True,
                isDeleted=False,
                isPasswordSet=False,
                internalPatientId=daily_sequence_id(self.db, Patient),
                createdBy=login_user_id,
            )
            self.db.add(Patient(**payload))
            created += 1
        self.db.commit()
        return ok(
            {"created": created, "skipped": skipped, "errors": errors},
            f"{created} patient(s) imported",
        )


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
