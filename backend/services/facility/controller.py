"""Controllers for the Facility service.

Ported from GkFacilityService/FacilityController. Real business logic:
  * name uniqueness (case-insensitive) on add + edit (excluding self)
  * new facilities start `status="draft"`, `isActive=false`
  * rich list filters (type/createdBy/city/state/status/date/search/ids) with
    `statusObj` and `createdByDetails` population
  * view with optional sub-details (admin/users/physicians) + location count
  * toggle cascades the active flag to the facility's completed locations
  * physician array management (append / unlink)
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func

from core.api import ok
from core.controller import BaseController
from core.populate import attach_many, attach_related
from services.facility.models import Facility, FacilityUser
from services.location.models import Location
from services.user_service.models import User


class FacilityController(BaseController):
    model = Facility
    name = "Facility"

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        type_ = data.get("type")
        if not name or not type_:
            raise HTTPException(400, "name and type are required")
        if self.db.query(Facility).filter(func.lower(Facility.name) == name.lower()).first():
            raise HTTPException(400, "The entered name already exists, please try another name")
        payload = self.writable(data)
        payload.update(
            name=name.lower(),
            code=name,
            type=type_,
            isActive=False,
            status="draft",
            createdBy=data.get("loginUserId"),
        )
        facility = Facility(**payload)
        self.db.add(facility)
        self.db.commit()
        self.db.refresh(facility)
        self.audit("create", facility.id)
        return ok(self.serialize(facility), "Facility added successfully")

    def list(self, q) -> dict:
        query = self.db.query(Facility)
        if q.types:
            query = query.filter(Facility.type.in_(q.types))
        if q.cities:
            query = query.filter(Facility.addressDetails.op("->>")("city").in_(q.cities))
        if q.states:
            query = query.filter(Facility.addressDetails.op("->>")("state").in_(q.states))
        if q.facilityIds:
            query = query.filter(Facility.id.in_(q.facilityIds))
        if q.facilityId:
            query = query.filter(Facility.id == q.facilityId)
        query = self.apply_filters(
            query,
            search=q.search,
            search_fields=("name",),
            statuses=q.statuses,
            created_by_ids=q.createdByIds,
            start_date=q.startDate,
            end_date=q.endDate,
            sort=q.sort,
        )
        return self.paginated(query, q.page, q.limit, status_obj=True, populate_created_by=True)

    def view(self, q) -> dict:
        query = self.db.query(Facility)
        if q.facilityId:
            query = query.filter(Facility.id == q.facilityId)
        if q.adminId:
            query = query.filter(Facility.adminId == q.adminId)
        facility = query.first()
        if not facility:
            return ok(None, "Facility Details")

        data = self.serialize(facility)
        user_ids = [
            fu.userId
            for fu in self.db.query(FacilityUser)
            .filter(FacilityUser.facilityId == facility.id)
            .all()
        ]
        data["userIds"] = user_ids

        if q.isSubDetailsRequired:
            attach_related(
                self.db,
                [data],
                model=User,
                source_field="createdBy",
                target_field="createdByDetails",
            )
            attach_related(
                self.db, [data], model=User, source_field="adminId", target_field="adminDetails"
            )
            attach_many(
                self.db, [data], model=User, source_field="userIds", target_field="userDetails"
            )
            if q.isPhysicianDetailsRequired:
                attach_many(
                    self.db,
                    [data],
                    model=User,
                    source_field="physicians",
                    target_field="physicianDetails",
                )

        if q.isNumberOfLocationsRequired:
            data["numberOfLocations"] = (
                self.db.query(Location).filter(Location.facilityId == facility.id).count()
            )
        self.audit("view", facility.id)
        return ok(data, "Facility Details")

    def edit(self, facility_id: int, data: dict) -> dict:
        facility = self.db.get(Facility, facility_id)
        if not facility:
            raise HTTPException(404, "can not get List")
        fields = self.writable(data)
        # name uniqueness (by code+type) excluding self
        new_name = fields.get("name")
        if new_name:
            code = new_name.strip()
            dup = (
                self.db.query(Facility)
                .filter(
                    func.lower(Facility.code) == code.lower(),
                    Facility.type == fields.get("type", facility.type),
                    Facility.id != facility_id,
                )
                .first()
            )
            if dup:
                raise HTTPException(409, "Facility name already exists")
            fields["code"] = code

        # append physicians rather than replace (legacy behaviour)
        incoming_physicians = data.get("physicians")
        if incoming_physicians:
            fields["physicians"] = list(facility.physicians or []) + list(incoming_physicians)

        for key, value in fields.items():
            setattr(facility, key, value)
        self.db.commit()
        self.db.refresh(facility)
        result = self.serialize(facility)
        if facility.adminId:
            attach_related(
                self.db, [result], model=User, source_field="adminId", target_field="adminDetails"
            )
        self.audit("update", facility_id)
        return ok(result, "Facility details edited successfully")

    def toggle(self, facility_id: int) -> dict:
        facility = self.db.get(Facility, facility_id)
        if not facility:
            raise HTTPException(404, "can not get List")
        is_active = not bool(facility.isActive)
        facility.isActive = is_active
        # cascade: completed locations follow the facility's active flag
        self.db.query(Location).filter(
            Location.facilityId == facility_id, Location.status == "completed"
        ).update({"isActive": is_active}, synchronize_session=False)
        self.db.commit()
        self.audit("update", facility_id)
        message = "Activated" if is_active else "De-activated"
        return ok({"id": facility_id, "isActive": is_active}, f"Facility {message}")

    def list_lite(self, q) -> dict:
        query = self.db.query(Facility)
        if q.search and q.search.strip():
            query = query.filter(Facility.name.ilike(f"%{q.search.strip().lower()}%"))
        if q.isActive is not None:
            query = query.filter(Facility.isActive.is_(q.isActive))
        if q.facilityIds:
            query = query.filter(Facility.id.in_(q.facilityIds))
        return ok([self.serialize(r) for r in query.all()], "Facility List")

    def add_physicians(self, facility_id: int, physicians: list[int]) -> dict:
        facility = self.db.get(Facility, facility_id)
        if not facility:
            raise HTTPException(404, "Invalid FacilityId")
        existing = list(facility.physicians or [])
        facility.physicians = existing + [p for p in physicians if p not in existing]
        self.db.commit()
        self.db.refresh(facility)
        self.audit("update", facility_id)
        return ok(
            {"id": facility_id, "physicians": facility.physicians}, "Physicians linked successfully"
        )

    def delete_physician(self, facility_id: int, physician_id: int) -> dict:
        facility = self.db.get(Facility, facility_id)
        if not facility:
            raise HTTPException(404, "Invalid FacilityId")
        facility.physicians = [p for p in (facility.physicians or []) if p != physician_id]
        self.db.commit()
        self.audit("update", facility_id)
        return ok({}, "Physician un-linked successfully")

    def set_admin(self, facility_id: int, admin_id: int) -> dict:
        facility = self.db.get(Facility, facility_id)
        if not facility:
            raise HTTPException(404, "Invalid FacilityId")
        facility.adminId = admin_id
        # ensure a facility-user link exists for the admin
        link = (
            self.db.query(FacilityUser)
            .filter(FacilityUser.facilityId == facility_id, FacilityUser.userId == admin_id)
            .first()
        )
        if not link:
            self.db.add(FacilityUser(facilityId=facility_id, userId=admin_id))
        self.db.commit()
        self.db.refresh(facility)
        self.audit("update", facility_id)
        return ok(self.serialize(facility), "Admin assigned successfully")


class FacilityUserController(BaseController):
    model = FacilityUser
    name = "Facility user"

    def list_by_facility(self, facility_id: int) -> dict:
        rows = self.db.query(FacilityUser).filter(FacilityUser.facilityId == facility_id).all()
        return ok([self.serialize(r) for r in rows], "Facility user list")
