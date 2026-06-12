"""Password hashing + JWT helpers (shared by every service).

bcrypt is used directly (like the old bcryptjs), so existing password hashes
keep verifying. JWT uses HS256 with the secret from settings.
"""

from __future__ import annotations

import secrets
import string
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from core.config import settings

_BCRYPT_MAX_BYTES = 72  # bcrypt only looks at the first 72 bytes


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode()[:_BCRYPT_MAX_BYTES], bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode()[:_BCRYPT_MAX_BYTES], hashed.encode())
    except (ValueError, TypeError):
        return False


def generate_password(length: int = 12) -> str:
    """A reasonably strong random password (upper/lower/digit/symbol)."""
    alphabet = string.ascii_letters + string.digits + "!@#$%*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_token(claims: dict[str, Any]) -> tuple[str, datetime]:
    """Sign a JWT carrying `claims`; returns (token, expiry)."""
    expiry = datetime.now(UTC) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {**claims, "exp": expiry}
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token, expiry


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError:
        return None
