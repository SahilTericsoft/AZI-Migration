# Result service (PHI)

Migrated from **GkPdfGeneratorService** result entities. Mounted at `/result`.

## Files
`models.py` (ResultSample, ResultControl) · `schemas.py` · `controller.py` ·
`router.py`

## Entities & endpoints
Standard CRUD on `/result/{samples|controls}` — **protected + audited**.

## HIPAA
Bearer token required (`401` otherwise); every access audited (lab results).

## Tests
`tests/test_remaining_services.py` — `test_result_samples_phi`, auth.
