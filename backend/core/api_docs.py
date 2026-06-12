"""OpenAPI metadata (title, description, version, tag groups) for `/docs`."""

API_TITLE = "AZI Backend"
API_VERSION = "1.0.0"

API_DESCRIPTION = """\
Unified **FastAPI** backend that consolidates the legacy 30-service
`AI-PortalApi-V2` platform into a single, modular monolith.

### Conventions
- **Success**: `{ "message": ..., "data": ... }`
- **Error**: `{ "detail": ... }` (body-validation failures return `422`).
- **Auth**: PHI endpoints require `Authorization: Bearer <JWT>` (`401` otherwise).
- **HIPAA**: PHI access is audited; sensitive fields (SSN, password, OTP codes,
  tokens) are never returned; deletes are soft.

### Standard CRUD surface (per entity)
`POST /` create · `POST /list` list/search · `GET /{id}` view ·
`PUT /{id}` update · `DELETE /{id}` delete.

See `README.md`, `AUDIT.md` and each `services/<name>/README.md` for detail.
"""

API_CONTACT = {"name": "AZI Platform Team"}
API_LICENSE = {"name": "Proprietary"}

# High-level tag descriptions (FastAPI groups operations by tag in /docs).
OPENAPI_TAGS = [
    {"name": "health", "description": "Liveness probe."},
    {"name": "user-service: auth", "description": "Login, session, password, system config."},
    {
        "name": "user-service: users",
        "description": "Staff user CRUD (create/list/view/update/delete/validate).",
    },
    {
        "name": "user-service: access-control",
        "description": "Roles, ACL modules, role & user permissions.",
    },
    {"name": "user-service: static-data", "description": "Geo reference data + dropdown sets."},
    {"name": "test-config: panels", "description": "Test panels (catalog)."},
    {"name": "test-config: tests", "description": "Tests (catalog)."},
    {"name": "test-config: biomarkers", "description": "Biomarkers (catalog)."},
    {"name": "lab: labs", "description": "Laboratories."},
    {
        "name": "facility: facilities",
        "description": "Facilities + sub-details, toggle cascade, physicians/admin.",
    },
    {"name": "location: locations", "description": "Locations + physician linking."},
    {
        "name": "patient: patients",
        "description": "Patients (PHI) — dedup, soft-delete, rich search. Audited.",
    },
    {"name": "test-order: orders", "description": "Test orders (PHI). Audited."},
    {"name": "sample: samples", "description": "Order samples (PHI) — accession flow. Audited."},
    {"name": "result", "description": "Result samples/controls (PHI). Audited."},
    {"name": "messaging: email", "description": "Email logs/templates + OTP generate/verify."},
    {"name": "messaging: sms", "description": "SMS logs/templates + OTP generate/verify."},
    {"name": "inventory", "description": "Products + lab inventory (stock, lots, sub-items)."},
    {"name": "d2c: customers", "description": "Direct-to-consumer customer auth (PHI). Audited."},
    {"name": "billing", "description": "Insurers + clearing houses (reference)."},
    {"name": "integration", "description": "AdvancedMD credentials + OCR config."},
]
