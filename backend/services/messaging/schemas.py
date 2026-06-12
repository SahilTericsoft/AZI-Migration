"""Request schemas for the Messaging service."""

from __future__ import annotations

from core.api import MutationBody


class EmailLogCreate(MutationBody):
    toAddress: str


class SmsLogCreate(MutationBody):
    toNumber: str


class TemplateCreate(MutationBody):
    purpose: str


class GenerateEmailOtpIn(MutationBody):
    emailId: str
    purpose: str | None = None


class VerifyEmailOtpIn(MutationBody):
    emailId: str
    code: str


class GenerateSmsOtpIn(MutationBody):
    mobileNumber: str
    purpose: str | None = None


class VerifySmsOtpIn(MutationBody):
    mobileNumber: str
    code: str


class Edit(MutationBody):
    pass
