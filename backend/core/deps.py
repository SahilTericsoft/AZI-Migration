"""Auth dependency shared across services (HIPAA access control)."""

from fastapi import Header, HTTPException

from core.security import decode_token


def _claims_from_header(authorization: str | None) -> dict | None:
    if not authorization or len(authorization.split(" ")) <= 1:
        return None
    return decode_token(authorization.split(" ")[1])


def require_user_id(authorization: str | None = Header(default=None)) -> int:
    """Require a valid bearer token and return the acting user's id (the actor
    for audit). Used by every PHI endpoint — one decode per request, and a 401
    when the token is missing/invalid."""
    claims = _claims_from_header(authorization)
    if not claims:
        raise HTTPException(401, "Authentication required")
    return claims.get("id")
