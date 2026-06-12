# Lab service

Migrated from **GkLabService/LabController**. Mounted at `/lab`.

## Files
`models.py` (Lab, LabUser) · `schemas.py` · `controller.py` (**real ported
logic**) · `router.py`

## Ported business logic
- **Add** — `labRole` must be `sendLab`/`receiveLab`/`sendReceiveLab`; `code` =
  lowercased trimmed name; new labs start `status="draft"`, `isActive=false`;
  `isSdiLab` = `labType != "externalLab"`.
- **Edit** — re-derives `code` from name; populates `adminDetails`.
- **View** — by `labId`/`code`/`labType`/`adminId`/`isActive`; `adminDetails`.
- **List** — filters by `labTypes`, `statuses`, `createdByIds`, date range,
  `search` (name/code/externalId/npi ILIKE), `sort`; paginates; `statusObj` +
  `createdByDetails`.
- **Toggle**; **get_by_admin**; **lab-user** linking (deduped) + `list_by_lab`.

## Endpoints
`POST /labs` · `/labs/list` · `/labs/list-lite` · `/labs/view` ·
`GET /labs/by-admin/{adminId}` · `PUT /labs/{id}` · `/labs/{id}/toggle` ·
`GET/DELETE /labs/{id}` · lab-users (`/by-lab/{id}` + CRUD).

## Tests
`tests/test_lab.py` — defaults, externalLab→isSdiLab, role validation, list
filters + population, edit code, toggle, view/by-admin, lab-user dedupe (8).
