# Location service

Migrated from **GkFacilityService/LocationController**. Mounted at `/location`.

## Files
`models.py` (Location, LocationUser, LocationPhysician) · `schemas.py` ·
`controller.py` (**real ported logic**) · `router.py`

## Ported business logic
- **Add** — validates the parent facility exists and (unless
  `isExternalLabFlow`) is active; new locations start `status="draft"`; assigns
  `internalLocationId` (`{INSTANCE}_{YYYYMMDD}_{NNNN}`); `code` = trimmed name.
- **List** — filters by `types`, `createdByIds`, `cities`/`states`
  (`addressDetails ->> …`), `facilityId(s)`, `labId`, `statuses`, date range,
  `search`, `sort`; paginates; `statusObj` + `createdByDetails`.
- **View** — by `locationId`/`adminId`; collects `userIds`; optional sub-details
  (`facilityDetails`, `labDetails`, `adminDetails`, `userDetails`).
- **Edit** — re-derives `code` from name; populates facility/lab on response.
- **Toggle** — flips `isActive`.
- **Physician linking** — `add_physician` / `add_bulk_physicians` create or
  reactivate `LocationPhysician` rows (deduped) and return the active physician
  ids. (Physicians are tracked via the link table, not a Location column.)

## Endpoints
`POST /locations` · `/locations/list` · `/locations/list-lite` · `/locations/view`
· `PUT /locations/{id}` · `/locations/{id}/toggle` · `POST /locations/{id}/physicians`
(+ `/bulk`) · `GET/DELETE /locations/{id}` · location-users & location-physicians CRUD.

## Tests
`tests/test_location.py` — facility validation, defaults + internal id, list
filters + population, view sub-details, toggle, physician linking/dedupe (8 tests).
