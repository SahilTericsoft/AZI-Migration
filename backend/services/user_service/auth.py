"""Auth + system config routes.

Migrated from GkUserService/AuthController.ts. Consolidations:
  - forgot-password merges forgotPassword + forgotManualPassword (sendEmail flag)
  - system-config merges systemConfig (list) + systemConfigView (?id=)
External login enrichment (facility/lab) and email dispatch are TODOs until
those services are migrated.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import (
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from services.user_service.models import (
    AclModule,
    SystemConfig,
    Token,
    User,
    UserAcl,
)
from services.user_service.schemas import (
    EmailIn,
    ForgotPasswordIn,
    LoginIn,
    UserIdIn,
    VerifyPasswordIn,
)
from services.user_service.utils import ok, to_dict

router = APIRouter(prefix="/auth", tags=["user-service: auth"])


def build_access_modules(db: Session, user_id: int, role_code: str | None) -> dict:
    """Map of accessible modules. superAdmin sees everything; others see their
    explicit UserAcl grants. (Mirror of legacy getUserRoleAclModules.)"""
    result: dict[str, list] = {}
    if role_code == "superAdmin":
        for m in db.query(AclModule).all():
            result.setdefault(m.module, []).append(
                {"module": m.module, "feature": m.code, "isAccessible": True}
            )
    else:
        for a in db.query(UserAcl).filter(UserAcl.userId == user_id).all():
            result.setdefault(a.moduleAccess, []).append(
                {"module": a.moduleAccess, "feature": a.featureAccess, "isAccessible": True}
            )
    return result


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.emailId == body.emailId.lower()).first()
    if not user:
        raise HTTPException(404, "User Does Not Exists")
    if not user.isActive:
        raise HTTPException(403, "User Inactive. Please contact admin")
    if not verify_password(body.password, user.password):
        raise HTTPException(403, "Invalid login credentials")

    # Single active session per user.
    db.query(Token).filter(Token.userId == user.id).delete()

    payload = to_dict(user, exclude={"password", "signature"})
    role_code = (user.roleObj or {}).get("code")

    config = db.get(SystemConfig, 1)
    if config:
        payload["systemConfig"] = config.labConfiguration

    token, expiry = create_token({**payload, "sub": str(user.id)})
    db.add(Token(userId=user.id, token=token, isActive=True, expiryTime=expiry.isoformat()))
    db.commit()

    payload["token"] = token
    payload["expiryTime"] = expiry.isoformat()
    payload["userAccessModules"] = build_access_modules(db, user.id, role_code)
    return ok(payload, "Login Successful")


@router.get("/check-login")
def check_login(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not authorization or len(authorization.split(" ")) <= 1:
        raise HTTPException(403, "User not logged in")
    token = authorization.split(" ")[1]
    claims = decode_token(token)
    if not claims:
        raise HTTPException(403, "Invalid Token")

    row = (
        db.query(Token)
        .filter(Token.token == token, Token.isActive.is_(True), Token.userId == claims.get("id"))
        .first()
    )
    if not row:
        raise HTTPException(403, "User not logged in")

    role_code = (claims.get("roleObj") or {}).get("code")
    claims["userAccessModules"] = build_access_modules(db, claims.get("id"), role_code)
    return ok(claims, "Check Login Successful")


@router.post("/logout")
def logout(body: UserIdIn, db: Session = Depends(get_db)):
    db.query(Token).filter(Token.userId == body.userId).delete()
    db.commit()
    return ok(message="Logout Successfully")


@router.post("/verify-password")
def verify_user_password(body: VerifyPasswordIn, db: Session = Depends(get_db)):
    user = db.get(User, body.userId)
    if not user:
        raise HTTPException(404, "User Does Not Exists")
    if not user.isActive:
        raise HTTPException(403, "User Inactive. Please contact admin")
    if not verify_password(body.password, user.password):
        raise HTTPException(403, "Invalid login credentials")
    return ok({}, "Login Successful")


@router.put("/forgot-password")
def forgot_password(body: ForgotPasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.emailId == body.emailId.lower()).first()
    if not user:
        raise HTTPException(404, "can not get user details")
    user.password = hash_password(body.newPassword)
    db.commit()
    if body.sendEmail:
        pass  # TODO(email service): send "password-manual-reset-link" job
    return ok({}, "User new password updated successfully")


@router.post("/forgot-password/send-mail")
def send_forgot_password_mail(body: EmailIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.emailId == body.emailId.lower()).first()
    if not user:
        raise HTTPException(403, "User Not Found")
    if not user.isActive:
        raise HTTPException(403, "User Account is Inactive. Please contact admin")
    # TODO(email service): send "password-reset-link" OTP job
    return ok({}, "Email Sent To Mail")


@router.post("/end-session")
def end_user_session(body: UserIdIn, db: Session = Depends(get_db)):
    db.query(Token).filter(Token.userId == body.userId).update({"isActive": False})
    db.commit()
    return ok({}, "Token Expired")


@router.get("/system-config")
def system_config(id: int | None = Query(default=None), db: Session = Depends(get_db)):
    if id is not None:
        return ok(to_dict(db.get(SystemConfig, id)), "System Config Details")
    rows = [to_dict(r) for r in db.query(SystemConfig).all()]
    return ok(rows, "System Config")
