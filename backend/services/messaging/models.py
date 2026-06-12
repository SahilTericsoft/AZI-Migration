"""Messaging models — consolidates GkEmailService + GkSMSService.

Email `from`/`to` are renamed to `fromAddress`/`toAddress` and SMS `to` to
`toNumber` (DB latitude; `from` is a Python keyword). Message logs can contain
PHI, so they are auth-protected + audited; OTP `code`s are masked.
"""

from sqlalchemy import JSON, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin

SECURITY_SENSITIVE = {"code"}


class EmailLog(TimestampMixin, Base):
    __tablename__ = "EmailLogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fromAddress: Mapped[str | None] = mapped_column(String)
    toAddress: Mapped[str | None] = mapped_column(String, index=True)
    purpose: Mapped[str | None] = mapped_column(String)
    message: Mapped[str | None] = mapped_column(Text)
    isDelivered: Mapped[bool | None] = mapped_column(Boolean)
    error: Mapped[str | None] = mapped_column(String)
    providerResponse: Mapped[dict | None] = mapped_column(JSON)


class EmailTemplate(TimestampMixin, Base):
    __tablename__ = "EmailTemplets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purpose: Mapped[str | None] = mapped_column(String)
    templet: Mapped[str | None] = mapped_column(Text)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)


class EmailSecurity(TimestampMixin, Base):
    __tablename__ = "EmailSecurities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(String)
    emailId: Mapped[str | None] = mapped_column(String, index=True)
    purpose: Mapped[str | None] = mapped_column(String)
    expiryTime: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)


class SmsLog(TimestampMixin, Base):
    __tablename__ = "SmsLogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    toNumber: Mapped[str | None] = mapped_column(String, index=True)
    purpose: Mapped[str | None] = mapped_column(String)
    message: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(String)
    isDelivered: Mapped[bool | None] = mapped_column(Boolean)
    providerResponse: Mapped[dict | None] = mapped_column(JSON)


class SmsTemplate(TimestampMixin, Base):
    __tablename__ = "SmsTemplates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purpose: Mapped[str | None] = mapped_column(String)
    message: Mapped[str | None] = mapped_column(Text)
    variables: Mapped[dict | None] = mapped_column(JSON)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)


class SmsSecurity(TimestampMixin, Base):
    __tablename__ = "SmsSecurities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(String)
    mobileNumber: Mapped[str | None] = mapped_column(String, index=True)
    purpose: Mapped[str | None] = mapped_column(String)
    expiryTime: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
