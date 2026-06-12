"""Index — the single FastAPI app for the whole monorepo.

Each migrated service lives in `services/<name>/` and exposes an APIRouter.
Include those routers here as services are migrated. One process serves all of
them (monorepo), instead of the old per-service deployments.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse

from core.api_docs import (
    API_CONTACT,
    API_DESCRIPTION,
    API_LICENSE,
    API_TITLE,
    API_VERSION,
    OPENAPI_TAGS,
)
from core.security_middleware import harden_app
from services.activity_log.router import router as activity_log_router
from services.billing.router import router as billing_router
from services.d2c.router import router as d2c_router
from services.dynamic_form.router import router as dynamic_form_router
from services.facility.router import router as facility_router
from services.integration.router import router as integration_router
from services.inventory.router import router as inventory_router
from services.lab.router import router as lab_router
from services.lab_os.router import router as lab_os_router
from services.location.router import router as location_router
from services.messaging.router import router as messaging_router
from services.notification.router import router as notification_router
from services.patient.router import router as patient_router
from services.result.router import router as result_router
from services.sample.router import router as sample_router
from services.sendout.router import router as sendout_router
from services.state_reporting.router import router as state_reporting_router
from services.test_config.router import router as test_config_router
from services.test_order.router import router as test_order_router
from services.user_service.router import router as user_service_router

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    contact=API_CONTACT,
    license_info=API_LICENSE,
    openapi_tags=OPENAPI_TAGS,
    redoc_url=None,  # default points at the broken redoc@next CDN; served below
)
harden_app(app)  # CORS, host allow-list, security headers, safe error handler

# Pin the ReDoc bundle to a working version (FastAPI's default `redoc@next`
# 404s on jsdelivr, leaving the page blank).
REDOC_JS_URL = "https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js"


@app.get("/redoc", include_in_schema=False)
def redoc_html() -> HTMLResponse:
    return get_redoc_html(
        openapi_url=app.openapi_url, title=f"{API_TITLE} — ReDoc", redoc_js_url=REDOC_JS_URL
    )


@app.get("/health", tags=["health"], summary="Liveness probe")
def health() -> dict[str, str]:
    """Return service liveness — used by load balancers / orchestration."""
    return {"status": "ok"}


# --- Service routers (added one per migrated service) ---------------------
app.include_router(user_service_router)  # ACL + System settings + Users
app.include_router(test_config_router)  # Test Configuration
app.include_router(lab_router)  # Lab
app.include_router(facility_router)  # Facility
app.include_router(location_router)  # Location
app.include_router(patient_router)  # Patient (PHI)
app.include_router(test_order_router)  # Test Order (PHI)
app.include_router(sample_router)  # Sample (PHI)
app.include_router(notification_router)  # Notification
app.include_router(activity_log_router)  # Activity Log
app.include_router(messaging_router)  # Email + SMS
app.include_router(inventory_router)  # Inventory (+ lab inventory)
app.include_router(lab_os_router)  # Lab Operations
app.include_router(dynamic_form_router)  # Dynamic Form
app.include_router(billing_router)  # Billing references
app.include_router(d2c_router)  # Direct-to-Consumer (PHI)
app.include_router(state_reporting_router)  # State Reporting (PHI)
app.include_router(sendout_router)  # Sendout (PHI)
app.include_router(result_router)  # Result (PHI)
app.include_router(integration_router)  # AdvancedMD + OCR config
