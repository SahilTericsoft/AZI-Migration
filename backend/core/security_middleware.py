"""Application hardening: security headers, CORS, host allow-list, and a
non-leaking error handler. Wired in `main.py` via `harden_app(app)`.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from core.config import settings

# "Helmet"-equivalent response headers applied to every response.
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "X-XSS-Protection": "0",
    "Cache-Control": "no-store",  # responses may contain PHI — never cache
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        for key, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(key, value)
        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
            )
        return response


def harden_app(app: FastAPI) -> None:
    """Apply CORS, host allow-list, security headers and a safe error handler."""
    # CORS — only the explicitly configured origins (none by default).
    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Host header allow-list (skip when "*" — i.e. dev).
    if settings.allowed_host_list != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_host_list)

    app.add_middleware(SecurityHeadersMiddleware)

    @app.exception_handler(Exception)
    async def _unhandled_exception(_: Request, __: Exception) -> JSONResponse:
        # Never leak stack traces / internals / PHI in error bodies.
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
