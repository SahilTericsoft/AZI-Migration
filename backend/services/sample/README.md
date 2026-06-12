# Sample service (PHI)

Migrated from **GkTestOrderService/TestOrderSampleController**. Mounted at `/sample`.

## Files
`models.py` (OrderSample) · `schemas.py` · `controller.py` (**real ported
logic**) · `router.py`

## Ported business logic
- **Add** — validates the parent order (`Invalid Order Id`); fans `barcode` out
  to `patientBarcode`/`labBarcode`; sets the false-flag defaults
  (barcodeReplaced/intakeCompleted/accessioned/sendOut/pdfGenerated); derives
  `sampleType` from test/panel/biomarker details; assigns `sampleCode` =
  `sm{id}`; **increments the order's `numberOfSamplesOrdered`** and stamps the
  physician on the order.
- **Accession** — sets `isAccessioned=true`, `accessionedBy`, `accessionedDate`,
  optional status / lab.
- **Edit** — keeps the three barcode fields in sync.
- **List** — filter by order/barcode(s)/status/isAccessioned + search; `by-order`.

## HIPAA
All endpoints require a bearer token (`401` otherwise) and are audited.

## Endpoints
`POST /samples` · `/samples/list` · `GET /samples/by-order/{orderId}` ·
`PUT /samples/{id}/accession` · `GET/PUT/DELETE /samples/{id}`.

## Tests
`tests/test_sample.py` — defaults + sm-code + barcode fan-out + counter
increment + sampleType derivation, bad-order reject, accession flow, barcode
sync, list/by-order, auth, audit (7).
