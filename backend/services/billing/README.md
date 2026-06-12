# Billing reference service

Migrated from **GkPatientService** billing references. Mounted at `/billing`.

## Files
`models.py` (Insurer, ClearingHouse, ClearingHouseInsurance) · `schemas.py` ·
`controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on `/billing/{insurers|clearing-houses|clearing-house-insurances}`.

## Domain logic
- **ClearingHouseController** defaults `isActive=true` on create.

## Tests
`tests/test_remaining_services.py` — insurers, clearing houses.
