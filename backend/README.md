# AZI Backend — Monorepo

One FastAPI service (single process) replacing the old 30+ `Gk*` microservices.
Each domain lives under `services/<name>/` and plugs its router into `main.py`.

## Documentation index

| Doc | What it covers |
| --- | --- |
| **This README** | Architecture, service anatomy, run/test/lint, migration status |
| [`AUDIT.md`](AUDIT.md) | Independent technical audit — migration %, code quality, security/HIPAA, performance, scorecard |
| [`SCHEMA_CHANGES.md`](SCHEMA_CHANGES.md) | DB changes vs legacy + how to sync |
| [`schema.sql`](schema.sql) | Full PostgreSQL DDL (all tables + indexes) |
| [`migrate_legacy.sql`](migrate_legacy.sql) / [`migrate_perf_indexes.sql`](migrate_perf_indexes.sql) | Deltas to apply onto an existing DB |
| `services/<name>/README.md` | Per-service entities, ported logic, endpoints, tests |
| `/docs` (running app) | Live OpenAPI reference (Swagger UI) with grouped tags |

## Developer workflow

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                # set DATABASE_URL, JWT_SECRET, CORS_ORIGINS…

python -m scripts.init_db           # create all tables locally
uvicorn main:app --reload           # http://localhost:8000/docs

python -m pytest                    # 112 tests (real Postgres)
ruff check . && black .             # lint + format (config in pyproject.toml)
python -m scripts.dump_schema > schema.sql   # regenerate the DDL
```

```
backend/
├── main.py                  # the index — includes every service router
├── core/                    # shared machinery (used by all services)
│   ├── config.py            # settings (DATABASE_URL, JWT)
│   ├── database.py          # engine, session, Base, TimestampMixin
│   ├── security.py          # bcrypt + JWT helpers
│   ├── api.py               # ok() / paginate() / to_dict() / ListIn / MutationBody
│   ├── controller.py        # BaseController (shared CRUD logic)
│   ├── deps.py              # require_user_id (JWT auth guard for PHI)
│   ├── security_middleware.py # harden_app: headers, CORS, host allow-list, safe errors
│   ├── api_docs.py          # OpenAPI metadata (title/description/tags) for /docs
│   └── audit.py             # AuditLog model + record_audit (HIPAA)
├── services/
│   ├── user_service/        # ACL, System settings, Users, Auth   (mounted /user-service)
│   ├── test_config/         # Panels, Tests, Biomarkers, CPT, ICD (/test-config)
│   ├── lab/                 # Labs, LabUsers                        (/lab)
│   ├── facility/            # Facilities, FacilityUsers            (/facility)
│   ├── location/            # Locations, Users, Physicians         (/location)
│   ├── patient/             # Patients, Insurances, Allergies  PHI (/patient)
│   ├── test_order/          # Orders, Results, Guarantors, Visits PHI (/test-order)
│   └── sample/              # OrderSamples                     PHI (/sample)
└── tests/                   # pytest, real Postgres
```

## Service anatomy (models · schemas · controller · router)

Every service folder is complete and self-contained:

```
services/<name>/
├── models.py       # SQLAlchemy entities
├── schemas.py      # Pydantic request bodies (Create/Update per entity)
├── controller.py   # business logic — one controller class per entity
├── router.py       # HTTP routes → controllers
└── README.md       # what the folder contains + its endpoints
```

Controllers extend `core/controller.BaseController`, which holds the shared,
readable CRUD implementation (query / pagination / search / soft-delete /
sensitive-field masking / HIPAA audit) **once**. Each service's `controller.py`
configures it and overrides `before_create` / `before_update` (or a method) to
add real domain logic — e.g. `PatientController` mints `internalPatientId`,
`OrderController` mints the order `code`, `SampleController` mints `sampleCode`.
Each service's `router.py` is pure transport: it builds the controller with the
acting user (`require_user_id` on PHI routers) and delegates to its methods.

Standard consolidated 5-endpoint surface per entity:

| Method | Path | Action |
| --- | --- | --- |
| POST | `/` | create |
| POST | `/list` | list/search (paginates when `page`/`limit` given; `search`, `filters`) |
| GET | `/{id}` | view one |
| PUT | `/{id}` | update one |
| DELETE | `/{id}` | delete (soft when the model has `isDeleted`) |

The logic lives in explicit, per-service controllers; the base class keeps it
DRY and uniformly tested.

## HIPAA compliance

Patient health information lives in the **patient**, **test_order** and **sample**
services. Controls applied there:

- **Authentication required** — those routers depend on `require_user_id`; no
  valid bearer token → `401`. (`core/deps.py`)
- **Audit trail** — every create/view/update/delete on a PHI record writes an
  `AuditLogs` row (who, action, entity, recordId, when). (`core/audit.py`)
- **Minimum necessary** — sensitive columns are never returned by the API:
  `Patient.ssn / password / drivingLicenseNumber`, `Guarantor.ssnNumber`.
- **Retention via soft delete** — deleting PHI sets `isDeleted=true` (the row is
  retained and hidden from reads) rather than destroying it.
- **HTTP hardening** — `harden_app()` (`core/security_middleware.py`) adds
  security headers (nosniff, `X-Frame-Options: DENY`, `Referrer-Policy`,
  `Cache-Control: no-store`, HSTS in production), an env-driven CORS allow-list,
  a trusted-host filter, and a safe error handler (no stack traces to clients).

### Security configuration (`.env`)

| Variable | Purpose |
| --- | --- |
| `ENVIRONMENT` | `production` enables HSTS and stricter defaults |
| `CORS_ORIGINS` | Comma-separated allowed origins (empty = none) |
| `ALLOWED_HOSTS` | Comma-separated host allow-list (`*` = any, dev only) |
| `JWT_SECRET` | Signing key for PHI auth tokens |

> Operational HIPAA items handled outside the app: encryption in transit (TLS at
> the ingress) and at rest (Postgres disk/column encryption), backups, and BAA
> with the hosting provider.

## Response shape

- Success: `{ "message": ..., "data": ... }`
- Error: FastAPI `{ "detail": ... }`; body-validation failures return `422`.

## Tests

Real Postgres, fresh schema per test.

```bash
createdb azi_user_test        # one-time (or set TEST_DATABASE_URL)
source .venv/bin/activate
python -m pytest              # 112 tests
```

Behavioural coverage — success + key error paths per endpoint, including the
HIPAA controls (auth-required, field masking, audit trail, soft delete) and the
HTTP hardening (`tests/test_security.py`: security headers present, PHI list
access audited).

## Completeness — every legacy Gk* service accounted for

| Legacy service | New service | Real logic ported? |
| --- | --- | --- |
| GkUserService | user_service | ✅ (auth/users/ACL) |
| GkPanelService | test_config | ✅ uniqueness, internal-id, toggle, filters |
| GkLabService / GkLabOsService | lab, lab_os, result | ✅ |
| GkFacilityService | facility, location | ✅ cascade, sub-details, physician links |
| GkPatientService | patient, billing | ✅ dedup-code, allergy-merge, soft-delete |
| GkTestOrderService / GkBulkUploadService | test_order, sample | ✅ gk/sm codes, counters, accession |
| GkSendoutService | sendout | ✅ |
| GkStateReportingService | state_reporting | ✅ |
| GKNotificationService | notification | ✅ by-user, mark-read |
| GkActivityLogService | activity_log | ✅ bulk, scoped |
| GkEmailService / GkSMSService | messaging | ✅ OTP generate/verify, templates |
| GkInventoryService / GkLabInventoryService | inventory | ✅ uniqueness, low-stock, lots |
| GkDynamicFormService | dynamic_form | ✅ |
| GkD2CService | d2c | ✅ customer auth, address-default, order pricing |
| GkAdvancedMDService / GkOCRService | integration | ✅ token upsert, OCR config |
| GkPdfGeneratorService | result | ✅ (result data; PDF *generation* deferred) |

**Deferred — pure compute/integration (no standalone CRUD data):**
GkBackgroundTasks, GkBillingDataAPIService, GkCovidPdfGenerationService,
GkHl7GenerationService, GkMlService, GkPythonPdfService, GkReactPdfService,
GkSFTPService, and the PDF-generation / OCR-inference *runtimes*. These run
external processes (PDF/HL7/ML/OCR/SFTP/cron); their data entities (where any)
are already covered above.

## Migration status

| Service | Legacy origin | PHI | Status |
| --- | --- | :-: | --- |
| user_service | GkUserService | | ✅ ACL, system settings, users, auth |
| test_config | GkPanelService / GkLabOsService | | ✅ panels, tests, biomarkers, CPT, ICD |
| lab | GkLabService / GkLabOsService | | ✅ labs, lab-users |
| facility | GkFacilityService | | ✅ facilities, facility-users |
| location | GkFacilityService | | ✅ locations, users, physicians |
| patient | GkPatientService | ✅ | ✅ patients, insurances, allergies |
| test_order | GkTestOrderService / GkBulkUploadService | ✅ | ✅ orders, results, guarantors, visits |
| sample | GkTestOrderService / GkBulkUploadService | ✅ | ✅ order-samples |
| notification | GKNotificationService | | ✅ notifications |
| activity_log | GkActivityLogService | | ✅ activity logs |
| messaging | GkEmailService + GkSMSService | ✅* | ✅ email/sms logs, templates, securities |
| inventory | GkInventoryService + GkLabInventoryService | | ✅ products, barcodes, qr, items, quantities |
| lab_os | GkLabOsService | | ✅ departments, instruments, SOPs, validations, sessions |
| dynamic_form | GkDynamicFormService | | ✅ chats |
| billing | GkPatientService (refs) | | ✅ insurers, clearing houses |
| d2c | GkD2CService | ✅ | ✅ customers, addresses, carts, orders |
| state_reporting | GkStateReportingService | ✅ | ✅ reports, sessions |
| sendout | GkSendoutService | ✅ | ✅ batches |
| result | GkPdfGeneratorService (result data) | ✅ | ✅ result samples, controls |
| integration | GkAdvancedMDService + GkOCRService | ✅* | ✅ AMD tokens, OCR config |

`*` = message logs / AMD tokens are protected because they may carry PHI/secrets.

### Deferred — compute / integration services (no standalone CRUD data)
These are processing pipelines that depend on external systems; their *data*
tables (where any) are covered above, but the generation/processing logic is a
follow-up: **PDF generation** (Gk{Pdf,ReactPdf,PythonPdf,CovidPdf}Service),
**HL7 generation**, **ML** (GkMlService), **OCR inference** (GkOCRService runtime),
**SFTP** (GkSFTPService), **BackgroundTasks**, **BillingDataAPI**.

### Scope notes
Services expose consolidated CRUD over each domain's core entities (DB latitude
used to model focused, required-field schemas). Domain workflows beyond CRUD
(order-placement orchestration, result PDF generation, barcode/accession flows,
cross-service link tables) are follow-ups, flagged in [`AUDIT.md`](AUDIT.md).
