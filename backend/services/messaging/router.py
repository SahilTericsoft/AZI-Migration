"""Messaging router — email + sms. Logs protected + audited; OTP generate/verify."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from core.deps import require_user_id
from services.messaging import controller as c
from services.messaging import schemas as s

router = APIRouter(prefix="/messaging")
EMAIL = ["messaging: email"]
SMS = ["messaging: sms"]


# ------------------------------------------------------------- email OTP
@router.post("/email/otp/generate", tags=EMAIL)
def generate_email_otp(body: s.GenerateEmailOtpIn, db: Session = Depends(get_db)):
    return c.EmailSecurityController(db).generate(body.emailId, body.purpose)


@router.post("/email/otp/verify", tags=EMAIL)
def verify_email_otp(body: s.VerifyEmailOtpIn, db: Session = Depends(get_db)):
    return c.EmailSecurityController(db).verify(body.emailId, body.code)


@router.get("/email/templates/by-purpose/{purpose}", tags=EMAIL)
def email_template_by_purpose(purpose: str, db: Session = Depends(get_db)):
    return c.EmailTemplateController(db).by_purpose(purpose)


@router.post("/email/templates", tags=EMAIL)
def add_email_template(body: s.TemplateCreate, db: Session = Depends(get_db)):
    return c.EmailTemplateController(db).create(body.model_dump(exclude_unset=True))


@router.post("/email/templates/list", tags=EMAIL)
def list_email_templates(body: ListIn, db: Session = Depends(get_db)):
    return c.EmailTemplateController(db).list(body)


@router.post("/email/logs", tags=EMAIL)
def add_email_log(
    body: s.EmailLogCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.EmailLogController(db, actor_id=actor).create(body.model_dump(exclude_unset=True))


@router.post("/email/logs/list", tags=EMAIL)
def list_email_logs(
    body: ListIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.EmailLogController(db).list(body)


# --------------------------------------------------------------- sms OTP
@router.post("/sms/otp/generate", tags=SMS)
def generate_sms_otp(body: s.GenerateSmsOtpIn, db: Session = Depends(get_db)):
    return c.SmsSecurityController(db).generate(body.mobileNumber, body.purpose)


@router.post("/sms/otp/verify", tags=SMS)
def verify_sms_otp(body: s.VerifySmsOtpIn, db: Session = Depends(get_db)):
    return c.SmsSecurityController(db).verify(body.mobileNumber, body.code)


@router.get("/sms/templates/by-purpose/{purpose}", tags=SMS)
def sms_template_by_purpose(purpose: str, db: Session = Depends(get_db)):
    return c.SmsTemplateController(db).by_purpose(purpose)


@router.post("/sms/templates", tags=SMS)
def add_sms_template(body: s.TemplateCreate, db: Session = Depends(get_db)):
    return c.SmsTemplateController(db).create(body.model_dump(exclude_unset=True))


@router.post("/sms/logs", tags=SMS)
def add_sms_log(
    body: s.SmsLogCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.SmsLogController(db, actor_id=actor).create(body.model_dump(exclude_unset=True))


@router.post("/sms/logs/list", tags=SMS)
def list_sms_logs(
    body: ListIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.SmsLogController(db).list(body)
