# Lab Operations service

Migrated from **GkLabOsService**. Mounted at `/lab-os`.

## Files
`models.py` (Department, Instrument, Sop, Validation, LabSession) · `schemas.py`
· `controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on `/lab-os/{departments|instruments|sops|validations|sessions}`.

## Domain logic
- **DepartmentController** defaults `isActive=true` on create.

## Tests
`tests/test_remaining_services.py` — departments, instruments.
