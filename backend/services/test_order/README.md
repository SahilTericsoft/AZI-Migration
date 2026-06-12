# Test Order service (PHI)

Migrated from **GkTestOrderService**. Mounted at `/test-order`.

## Files
`models.py` (Order, OrderResult, Guarantor, PatientVisit) · `schemas.py` ·
`controller.py` (**real ported logic**) · `router.py`

## Ported business logic
- **Add order** — requires facility/location/patient + patientDetails; assigns
  the legacy `code` = `gk{id}` after insert; initialises
  `numberOfSamplesOrdered/Resulted=0`, `status="draft"`, `source="web"`.
- **List** — filters by facility/location/patient/status, date range, and
  `search` across `code` + `patientDetails ->> firstName/lastName/code`; on
  output the patient block is **trimmed** to id/name/gender/dob (minimum
  necessary).
- **Results / guarantors / visits** — scoped-by-order lookups
  (`/by-order/{id}`) + CRUD; guarantor `ssnNumber` masked.

## HIPAA
All endpoints require a bearer token (`401` otherwise) and are audited.

## Endpoints
`POST /orders` · `/orders/list` · `GET/PUT/DELETE /orders/{id}` ·
order-results (`/by-order/{id}` + CRUD) · guarantors (`/by-order/{id}` + CRUD) ·
patient-visits (`/by-order/{id}` + CRUD).

## Tests
`tests/test_test_order.py` — gk-code + defaults, auth/required fields, list
search + patient trim, filter by patient, audit, results/guarantor/visit by
order, SSN masking (8).
