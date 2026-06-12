# State Reporting service (PHI)

Migrated from **GkStateReportingService**. Mounted at `/state-reporting`.

## Files
`models.py` (StateReporting, StateReportingSession) · `schemas.py` ·
`controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on `/state-reporting/{reports|sessions}` — **protected + audited**.

## HIPAA
Bearer token required (`401` otherwise); every access audited (regulatory
reporting of lab results).

## Tests
`tests/test_remaining_services.py` — `test_state_reporting_phi`.
