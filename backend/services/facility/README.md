# Facility service

Migrated from **GkFacilityService/FacilityController**. Mounted at `/facility`.

## Files
`models.py` (Facility, FacilityUser) · `schemas.py` · `controller.py` (**real
ported logic**) · `router.py`

## Ported business logic
- **Add** — case-insensitive name uniqueness; new facilities start
  `status="draft"`, `isActive=false`; stores `name` lowercased + `code` =
  original.
- **List** — filters by `types`, `createdByIds`, `cities`/`states`
  (via `addressDetails ->> 'city'/'state'`), `statuses`, `facilityIds`, date
  range, `search` (name ILIKE), `sort`; paginates; adds `statusObj`; populates
  `createdByDetails`.
- **View** — by `facilityId`/`adminId`; collects `userIds` from FacilityUsers;
  optional sub-details (`createdByDetails`/`adminDetails`/`userDetails`/
  `physicianDetails`) and a live `numberOfLocations` count.
- **Edit** — name uniqueness (code+type) excluding self; **appends** physicians
  rather than replacing.
- **Toggle** — flips `isActive` and **cascades** it to the facility's
  `completed` locations.
- **Physician/admin** — `add_physicians` (idempotent append), `delete_physician`
  (unlink), `set_admin` (sets `adminId` + ensures a FacilityUser link).

## Endpoints
`POST /facilities` · `POST /facilities/list` · `POST /facilities/list-lite` ·
`POST /facilities/view` · `PUT /facilities/{id}` · `PUT /facilities/{id}/toggle` ·
`POST /facilities/{id}/physicians` · `DELETE /facilities/{id}/physicians/{pid}` ·
`PUT /facilities/{id}/admin` · `GET/DELETE /facilities/{id}` · facility-users CRUD.

## Tests
`tests/test_facility.py` — uniqueness, defaults, list filters + population, view
sub-details + location count, toggle cascade, physician/admin management (7 tests).
