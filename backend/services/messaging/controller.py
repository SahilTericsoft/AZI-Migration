"""Controllers for the Messaging service (email + sms).

Ported from GkEmailService + GkSMSService. Real business logic:
  * OTP generate (6-digit code, 15-minute expiry) and verify (match + not
    expired + not already consumed) — the security-relevant part
  * templates fetched by `purpose`
  * message logs are audited (may contain PHI); OTP codes are masked on read
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from core.api import ok
from core.controller import BaseController
from services.messaging.models import (
    SECURITY_SENSITIVE,
    EmailLog,
    EmailSecurity,
    EmailTemplate,
    SmsLog,
    SmsSecurity,
    SmsTemplate,
)

_OTP_TTL_MIN = 15


def _new_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _expiry() -> str:
    return (datetime.now(UTC) + timedelta(minutes=_OTP_TTL_MIN)).isoformat()


def _is_expired(expiry_time: str | None) -> bool:
    if not expiry_time:
        return True
    try:
        return datetime.now(UTC) > datetime.fromisoformat(expiry_time)
    except ValueError:
        return True


class _SecurityBase(BaseController):
    sensitive = SECURITY_SENSITIVE
    id_field: str  # "emailId" or "mobileNumber"

    def generate(self, identifier: str, purpose: str | None) -> dict:
        # invalidate any outstanding codes for this identifier
        self.db.query(self.model).filter(
            getattr(self.model, self.id_field) == identifier,
            self.model.isActive.is_(True),
        ).update({"isActive": False})
        row = self.model(
            **{
                self.id_field: identifier,
                "purpose": purpose,
                "code": _new_code(),
                "expiryTime": _expiry(),
                "isActive": True,
            }
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "OTP generated")  # code masked

    def verify(self, identifier: str, code: str) -> dict:
        row = (
            self.db.query(self.model)
            .filter(
                getattr(self.model, self.id_field) == identifier,
                self.model.isActive.is_(True),
            )
            .order_by(self.model.createdAt.desc())
            .first()
        )
        if not row or row.code != code:
            raise HTTPException(400, "Invalid OTP")
        if _is_expired(row.expiryTime):
            raise HTTPException(400, "OTP expired")
        row.isActive = False  # consume
        self.db.commit()
        return ok({"verified": True}, "OTP verified")


class EmailSecurityController(_SecurityBase):
    model = EmailSecurity
    name = "Email security"
    id_field = "emailId"


class SmsSecurityController(_SecurityBase):
    model = SmsSecurity
    name = "SMS security"
    id_field = "mobileNumber"


class EmailTemplateController(BaseController):
    model = EmailTemplate
    name = "Email template"
    search_fields = ("purpose",)

    def by_purpose(self, purpose: str) -> dict:
        row = (
            self.db.query(EmailTemplate)
            .filter(EmailTemplate.purpose == purpose, EmailTemplate.isActive.isnot(False))
            .first()
        )
        return ok(self.serialize(row) if row else None, "Email template")


class SmsTemplateController(BaseController):
    model = SmsTemplate
    name = "SMS template"
    search_fields = ("purpose",)

    def by_purpose(self, purpose: str) -> dict:
        row = (
            self.db.query(SmsTemplate)
            .filter(SmsTemplate.purpose == purpose, SmsTemplate.isActive.isnot(False))
            .first()
        )
        return ok(self.serialize(row) if row else None, "SMS template")


class EmailLogController(BaseController):
    model = EmailLog
    name = "Email log"
    search_fields = ("toAddress", "purpose")
    audit_entity = "EmailLog"


class SmsLogController(BaseController):
    model = SmsLog
    name = "SMS log"
    search_fields = ("toNumber", "purpose")
    audit_entity = "SmsLog"
