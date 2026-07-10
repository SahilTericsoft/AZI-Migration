# AZI Backend — Knowledge Transfer

## 1. What this project is (in one line)
A **single FastAPI app** (one Python process, one Postgres DB) that replaces **30+ old `Gk*` Node.js microservices** for a **laboratory / diagnostics platform** (labs, patients, test orders, samples, results, billing, etc.). It handles PHI, so it's built to be **HIPAA-compliant**.

The whole thing lives in `backend/`. There is no frontend here.

## 2. The big idea — one repeated pattern everywhere
Instead of 30 services, there is **one app** with **domains** under `services/`. **Every domain folder looks identical**, so once you understand one, you understand all 20:

```
services/<name>/
├── models.py       # database tables (SQLAlchemy)
├── schemas.py      # request body shapes (Pydantic) — what the client sends
├── controller.py   # business logic (one class per entity)
├── router.py       # HTTP routes → call the controller
└── README.md       # what this domain does + its endpoints
```

**Request flow (memorize this):**
```
HTTP request → router.py → builds a Controller → Controller does the work → returns { "message", "data" }
```

## 3. The core/ folder — shared machinery used by ALL services
This is the reusable engine. Read these 8 files and you understand 80% of the codebase:

| File | What it does |
|---|---|
| `core/config.py` | Settings from `.env` (DB URL, JWT secret, CORS, Azure). Auto-fixes `postgres://` → `postgresql+psycopg2://`. |
| `core/database.py` | DB engine, session, `Base` for models, `TimestampMixin` (createdAt/updatedAt). Sync SQLAlchemy — endpoints are plain `def`, FastAPI threadpools them. |
| `core/controller.py` | **`BaseController`** — the shared CRUD logic (create/list/get/update/delete, search, pagination, soft-delete, field masking, audit). **This is the heart of the app.** |
| `core/api.py` | Helpers: `ok()` (success shape), `paginate()`, `to_dict()` (ORM→JSON), `ListIn` (list request body). |
| `core/deps.py` | `require_user_id` — the auth guard. PHI routes depend on it → no token = **401**. |
| `core/security.py` | Password hashing (bcrypt) + JWT create/decode (HS256). |
| `core/audit.py` | `AuditLog` table + `record_audit()` — logs every PHI access (who/what/when). |
| `core/security_middleware.py` | `harden_app()` — security headers, CORS allow-list, trusted hosts, safe errors (no stack traces leak). |

Two smaller helpers: `core/ids.py` generates legacy-style IDs like `AZI_20260705_0001`, and `core/populate.py` batch-loads related rows (e.g. "created by" user) without N+1 queries.

## 4. How BaseController works (the key file)
Almost every controller just extends `BaseController` and sets a few class attributes:

```python
class AllergyController(BaseController):
    model = Allergy            # which table
    name = "Allergy"           # for messages
    search_fields = ("name",)  # what `search` matches
    sensitive = (...)          # columns NEVER returned (e.g. ssn, password)
    audit_entity = "Patient"   # if set → every access logs a HIPAA audit row
```

You get `create / get / list / update / delete` for free. To add domain logic, you override hooks:
- `before_create(data)` / `before_update(obj, data)` — e.g. mint an ID, normalize fields.
- Or override a whole method (like `PatientController` does — see `services/patient/controller.py`).

**Soft delete:** if a table has an `isDeleted` column, DELETE just sets `isDeleted=True` (row is kept, hidden from reads). This is a HIPAA retention requirement.

## 5. Standard API surface (per entity)
Most entities expose the same 5 endpoints:

| Method | Path | Action |
|---|---|---|
| POST | `/` | create |
| POST | `/list` | list/search (paginates if `page`/`limit` given) |
| GET | `/{id}` | view one |
| PUT | `/{id}` | update |
| DELETE | `/{id}` | delete (soft if possible) |

**Response is always:** success → `{ "message": ..., "data": ... }`, error → `{ "detail": ... }`.

## 6. The 20 domains (services/)
All wired into the app in `main.py`. Ones marked **PHI** require a login token.

| Domain | Covers | PHI |
|---|---|:-:|
| user_service | Auth, users, roles, ACL/permissions, system config | |
| test_config | Panels, tests, biomarkers, CPT/ICD codes | |
| lab / lab_os | Labs, lab users; departments, instruments, SOPs | |
| facility / location | Facilities, locations, physicians | |
| patient | Patients, insurances, allergies | ✅ |
| test_order | Orders, results, guarantors, visits | ✅ |
| sample | Order samples (accessioning) | ✅ |
| result | Result samples & controls | ✅ |
| sendout | Sendout batches (to reference labs) | ✅ |
| state_reporting | State health reports | ✅ |
| d2c | Direct-to-consumer: customers, carts, orders | ✅ |
| billing | Insurers, clearing houses | |
| inventory | Products, barcodes, QR, lots/quantities | |
| messaging | Email/SMS logs, templates, OTP | |
| notification / activity_log | In-app notifications, activity logs | |
| dynamic_form | Chats / forms | |
| integration | AdvancedMD tokens, OCR config | |
| dashboard | Aggregated counts/charts (read-only, no new tables) | |
| support | Support center + resources | |

**user_service** is the exception to the pattern — it's split into `auth.py` (login/logout/JWT), `access_control.py` (roles + ACL), `users.py`, and `static_data.py`. Login enforces **one active session per user**, and `superAdmin` sees all modules.

## 7. HIPAA controls (important — this is a medical app)
1. **Auth required** on PHI routes (`require_user_id`) → 401 without a valid token.
2. **Audit trail** — every create/view/list/update/delete on PHI writes an `AuditLogs` row.
3. **Minimum necessary** — sensitive columns (`ssn`, `password`, `drivingLicenseNumber`, etc.) are **never** returned.
4. **Soft delete** for retention.
5. **HTTP hardening** via `harden_app()`.

## 8. Database
- **69 tables**, full DDL in `schema.sql` (matches legacy column names, camelCase, quoted).
- **No migration tool yet** (no Alembic). Instead:
  - `scripts/init_db.py` → `create_all()` — **only creates missing tables, never alters** existing ones.
  - ⚠️ **`migrations/pending_migrations.sql` is the manual workaround.** When someone adds a *column* to an already-deployed table, they must add an idempotent `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` there and run it by hand before deploy. `init_db.py` won't do it for you. This is the thing most likely to bite you.

## 9. Running it locally
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # set DATABASE_URL, JWT_SECRET
python -m scripts.init_db     # create tables
python -m scripts.seed_superadmin   # login: superadmin@gmail.com / Welcome@1234
uvicorn main:app --reload     # http://localhost:8000/docs
python -m pytest              # ~112 tests, needs a real Postgres test DB
ruff check . && black .       # lint + format
```
Interactive API docs at `/docs` (Swagger) and `/redoc`. Health check at `/health`.

## 10. Deployment
- **Docker** (`Dockerfile`, Python 3.12 slim) → **Fly.io** (`fly.toml`, region `iad`, 1 warm machine).
- `DATABASE_URL` and `JWT_SECRET` are Fly **secrets**, not in the file.

## 11. What's NOT done yet (gaps — see `AUDIT.md`)
The audit rates it **A- / production-ready for migrated scope**. Known follow-ups:
- **Deferred compute services** (~28%): PDF generation, HL7, ML, OCR inference, SFTP, background jobs, billing-data API. Their *data tables* exist, but the processing logic isn't ported (needs external workers/queues).
- **No Alembic migrations** (hence the manual `pending_migrations.sql`).
- **No CI** yet (tests + lint aren't gated on PRs).
- **Email/SMS side-effects** are `TODO` stubs in auth (e.g. forgot-password doesn't actually send mail yet).
- **Infra-level HIPAA** (TLS, encryption at rest, signed BAA) is an ops task, not code.

---

### The one thing to remember
It's **20 near-identical CRUD domains** sitting on **one shared `BaseController`**. Learn `core/controller.py` + one service like `patient/`, and the rest is the same shape repeated.
