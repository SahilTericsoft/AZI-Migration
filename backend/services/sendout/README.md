# Sendout service (PHI)

Migrated from **GkSendoutService**. Mounted at `/sendout`.

## Files
`models.py` (SendoutBatch) · `schemas.py` · `controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on `/sendout/batches` — **protected + audited**.

## HIPAA
Bearer token required (`401` otherwise); every access audited.

## Tests
`tests/test_remaining_services.py` — `test_sendout_phi`.
