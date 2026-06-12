"""Controllers for the Location service.

Ported from GkFacilityService/LocationController. Real business logic:
  * add validates the parent facility exists and is active (unless external-lab
    flow), starts `status="draft"`, assigns `internalLocationId`
  * rich list filters with `statusObj` + `createdByDetails`
  * view with optional sub-details (facility / lab / admin / users)
  * toggle flips the active flag
  * edit dedupe-appends physicians and re-derives `code` from the name
  * physician linking creates/reactivates LocationPhysician rows + updates the
    location's `physicians` array
"""

from fastapi import HTTPException

from core.api import ok
from core.controller import BaseController
from core.ids import daily_sequence_id
from core.populate import attach_many, attach_related
from services.facility.models import Facility
from services.lab.models import Lab
from services.location.models import Location, LocationPhysician, LocationUser
from services.user_service.models import User


class LocationController(BaseController):
    model = Location
    name = "Location"

    def add(self, data: dict) -> dict:
        facility = self.db.get(Facility, data.get("facilityId"))
        if not facility:
            raise HTTPException(400, "Invalid Facility Id")
        if not data.get("isExternalLabFlow") and facility.isActive is False:
            raise HTTPException(400, "Facility is inactive")

        name = (data.get("name") or "").strip()
        payload = self.writable(data)
        payload.update(
            name=name,
            code=name,
            status="draft",
            createdBy=data.get("loginUserId"),
            internalLocationId=daily_sequence_id(self.db, Location),
        )
        location = Location(**payload)
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        self.audit("create", location.id)
        return ok(self.serialize(location), "Location added successfully")

    def list(self, q) -> dict:
        query = self.db.query(Location)
        if q.types:
            query = query.filter(Location.type.in_(q.types))
        if q.cities:
            query = query.filter(Location.addressDetails.op("->>")("city").in_(q.cities))
        if q.states:
            query = query.filter(Location.addressDetails.op("->>")("state").in_(q.states))
        if q.facilityId:
            query = query.filter(Location.facilityId == q.facilityId)
        if q.facilityIds:
            query = query.filter(Location.facilityId.in_(q.facilityIds))
        if q.labId:
            query = query.filter(Location.labId == q.labId)
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
        query = self.db.query(Location)
        if q.locationId:
            query = query.filter(Location.id == q.locationId)
        if q.adminId:
            query = query.filter(Location.adminId == q.adminId)
        location = query.first()
        if not location:
            return ok(None, "Location Details")

        data = self.serialize(location)
        data["userIds"] = [
            lu.userId
            for lu in self.db.query(LocationUser)
            .filter(LocationUser.locationId == location.id)
            .all()
        ]
        if q.isSubDetailsRequired:
            attach_related(
                self.db,
                [data],
                model=Facility,
                source_field="facilityId",
                target_field="facilityDetails",
                attributes=["id", "name", "type", "isActive"],
            )
            attach_related(
                self.db,
                [data],
                model=Lab,
                source_field="labId",
                target_field="labDetails",
                attributes=["id", "name", "code"],
            )
            attach_related(
                self.db, [data], model=User, source_field="adminId", target_field="adminDetails"
            )
            attach_many(
                self.db, [data], model=User, source_field="userIds", target_field="userDetails"
            )
        self.audit("view", location.id)
        return ok(data, "Location Details")

    def toggle(self, location_id: int) -> dict:
        location = self.db.get(Location, location_id)
        if not location:
            raise HTTPException(404, "can not get List")
        location.isActive = not bool(location.isActive)
        self.db.commit()
        self.audit("update", location_id)
        message = "Activated" if location.isActive else "De-Activated"
        return ok({"id": location_id, "isActive": location.isActive}, f"Location {message}")

    def edit(self, location_id: int, data: dict) -> dict:
        location = self.db.get(Location, location_id)
        if not location:
            raise HTTPException(404, "Invalid location id")
        fields = self.writable(data)
        if fields.get("name"):
            fields["code"] = fields["name"].strip()
        for key, value in fields.items():
            setattr(location, key, value)
        self.db.commit()
        self.db.refresh(location)
        result = self.serialize(location)
        attach_related(
            self.db,
            [result],
            model=Facility,
            source_field="facilityId",
            target_field="facilityDetails",
            attributes=["id", "name", "type"],
        )
        attach_related(
            self.db,
            [result],
            model=Lab,
            source_field="labId",
            target_field="labDetails",
            attributes=["id", "name", "code"],
        )
        self.audit("update", location_id)
        return ok(result, "Location details edited successfully")

    def list_lite(self, q) -> dict:
        query = self.db.query(Location)
        if q.search and q.search.strip():
            query = query.filter(Location.name.ilike(f"%{q.search.strip().lower()}%"))
        if q.isActive is not None:
            query = query.filter(Location.isActive.is_(q.isActive))
        if q.facilityId:
            query = query.filter(Location.facilityId == q.facilityId)
        if q.locationIds:
            query = query.filter(Location.id.in_(q.locationIds))
        return ok([self.serialize(r) for r in query.all()], "Location List")

    def _link_physician(self, location_id: int, physician_id: int) -> None:
        """Create or reactivate a LocationPhysician link (physicians are tracked
        via this link table, not a column on Location)."""
        link = (
            self.db.query(LocationPhysician)
            .filter(
                LocationPhysician.locationId == location_id,
                LocationPhysician.physicianId == physician_id,
            )
            .first()
        )
        if link:
            link.isActive = True
        else:
            self.db.add(
                LocationPhysician(locationId=location_id, physicianId=physician_id, isActive=True)
            )

    def _active_physician_ids(self, location_id: int) -> list[int]:
        return [
            lp.physicianId
            for lp in self.db.query(LocationPhysician)
            .filter(
                LocationPhysician.locationId == location_id,
                LocationPhysician.isActive.is_(True),
            )
            .order_by(LocationPhysician.physicianId.asc())
            .all()
        ]

    def add_physician(self, location_id: int, physician_id: int) -> dict:
        if not self.db.get(Location, location_id):
            raise HTTPException(404, "Invalid location id")
        self._link_physician(location_id, physician_id)
        self.db.commit()
        self.audit("update", location_id)
        return ok(
            {"id": location_id, "physicians": self._active_physician_ids(location_id)},
            "Physician linked successfully",
        )

    def add_bulk_physicians(self, location_id: int, physician_ids: list[int]) -> dict:
        if not self.db.get(Location, location_id):
            raise HTTPException(404, "Invalid location id")
        wanted = set(physician_ids)
        # One query for all existing links (avoid a SELECT per physician).
        existing = (
            self.db.query(LocationPhysician)
            .filter(
                LocationPhysician.locationId == location_id,
                LocationPhysician.physicianId.in_(wanted),
            )
            .all()
            if wanted
            else []
        )
        for link in existing:
            link.isActive = True
        already = {link.physicianId for link in existing}
        self.db.add_all(
            LocationPhysician(locationId=location_id, physicianId=pid, isActive=True)
            for pid in wanted - already
        )
        self.db.commit()
        self.audit("update", location_id)
        return ok(
            {"id": location_id, "physicians": self._active_physician_ids(location_id)},
            "Physicians linked successfully",
        )


class LocationUserController(BaseController):
    model = LocationUser
    name = "Location user"


class LocationPhysicianController(BaseController):
    model = LocationPhysician
    name = "Location physician"
