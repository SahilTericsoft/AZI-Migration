# Messaging service

Consolidates **GkEmailService** + **GkSMSService**. Mounted at `/messaging`.

## Files
`models.py` (EmailLog, EmailTemplate, EmailSecurity, SmsLog, SmsTemplate,
SmsSecurity) · `schemas.py` · `controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on:
- `/messaging/email-logs` — **protected + audited** (may contain PHI)
- `/messaging/email-templates`
- `/messaging/email-securities` — OTP `code` masked
- `/messaging/sms-logs` — **protected + audited**
- `/messaging/sms-templates`
- `/messaging/sms-securities` — OTP `code` masked

## HIPAA
Message logs require a bearer token and are audited (content may be PHI). OTP
codes are never returned. Legacy `from`/`to` columns are modelled as
`fromAddress`/`toAddress`/`toNumber`.

## Tests
`tests/test_remaining_services.py` — email/sms templates, email-log PHI + auth.
