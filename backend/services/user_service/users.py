"""User CRUD routes (consolidated).

Migrated from GkUserService/UserController.ts. One endpoint now covers several
legacy ones:
  - POST /users        = add + addUser
  - POST /users/list   = list + listLite (paginates when page/limit given)
  - POST /users/view   = GET view + POST view
  - PUT  /users        = edit + bulkEdit + toggle + add/edit/updateSignature
  - DELETE /users/{id} = delete (also clears the user's UserAcl rows)
  - POST /users/validate = validateUser
Dead legacy code dropped: Populator.SetCreatedBy (its result was never used) and
the commented-out ActivityLog calls. Email side-effects are TODOs (email service
not migrated yet).
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import generate_password, hash_password
from services.user_service.models import Role, User, UserAcl
from services.user_service.schemas import (
    UserCreateIn,
    UserListIn,
    UserUpdateIn,
    UserValidateIn,
    UserViewIn,
)
from services.user_service.utils import next_internal_user_id, ok, paginate, to_dict

router = APIRouter(prefix="/users", tags=["user-service: users"])

# Columns a client may write; identifiers/audit columns are off-limits.
WRITABLE = {c.name for c in User.__table__.columns} - {"id", "createdAt", "updatedAt"}
_NAME_FIELDS = ("firstName", "lastName", "middleName", "emailId")


def _public(user: User) -> dict:
    return to_dict(user, exclude={"password"})


def _generate_internal_id(db: Session) -> str:
    start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    last = (
        db.query(User.internalUserId)
        .filter(User.createdAt >= start)
        .order_by(User.internalUserId.desc())
        .first()
    )
    return next_internal_user_id(last[0] if last else None)


@router.post("")
def create_user(body: UserCreateIn, db: Session = Depends(get_db)):
    # Resolve role (optional — legacy `add` required it, `addUser` didn't).
    role = None
    if body.roleId or body.roleCode:
        q = db.query(Role)
        role = (
            q.filter(Role.id == body.roleId).first()
            if body.roleId
            else q.filter(Role.code == body.roleCode).first()
        )
        if not role:
            raise HTTPException(400, "Invalid Role Selected")

    # Uniqueness checks.
    if body.emailId and db.query(User).filter(User.emailId == body.emailId.lower()).first():
        raise HTTPException(409, "EmailId is already in use")
    if body.npiNumber and db.query(User).filter(User.npiNumber == body.npiNumber).first():
        raise HTTPException(409, "NPI Number is already in use")

    data = body.model_dump(exclude_none=True)
    for f in _NAME_FIELDS:
        if data.get(f):
            data[f] = data[f].lower().strip()
    for f in ("loginUserId", "roleCode", "shouldSendEmail", "password"):
        data.pop(f, None)

    if role:
        data["roleId"] = role.id
        data["roleObj"] = {
            "id": role.id,
            "title": role.title,
            "code": role.code,
            "isSdiRole": role.isSdiRole,
        }
        data["isSdiUser"] = bool(role.isSdiRole)

    # Password: use given, else generate one when the user has a (login) role.
    raw_password = body.password or (generate_password(12) if role else None)
    if raw_password:
        data["password"] = hash_password(raw_password)

    data["createdBy"] = body.loginUserId
    data["isDeleted"] = False
    data["internalUserId"] = _generate_internal_id(db)

    user = User(**{k: v for k, v in data.items() if k in WRITABLE})
    db.add(user)
    db.commit()
    db.refresh(user)

    if body.shouldSendEmail and body.emailId:
        pass  # TODO(email service): send "credentials" email with raw_password
    return ok(_public(user), "User added successfully")


@router.post("/list")
def list_users(body: UserListIn, db: Session = Depends(get_db)):
    q = db.query(User)

    if body.search and body.search.strip():
        like = f"%{body.search.strip()}%"
        q = q.filter(
            func.lower(func.coalesce(User.firstName, "")).ilike(like.lower())
            | func.lower(func.coalesce(User.middleName, "")).ilike(like.lower())
            | func.lower(func.coalesce(User.lastName, "")).ilike(like.lower())
        )
    role_ids = body.roleIds or ([body.roleId] if body.roleId else None)
    if role_ids:
        q = q.filter(User.roleId.in_(role_ids))
    if body.roleCodes:
        # roleObj is a JSON column; ->> extracts the code as text.
        q = q.filter(User.roleObj.op("->>")("code").in_(body.roleCodes))
    genders = body.genders or ([body.gender] if body.gender else None)
    if genders:
        q = q.filter(User.gender.in_(genders))
    if body.userIds:
        q = q.filter(User.id.in_(body.userIds))
    if body.isPhysician is not None:
        q = q.filter(User.isPhysician.is_(body.isPhysician))
    if body.isActive is not None:
        q = q.filter(User.isActive.is_(body.isActive))
    if body.startDate and body.endDate:
        q = q.filter(User.createdAt.between(body.startDate, body.endDate))

    q = q.order_by(User.createdAt.desc())
    exclude = {"password"}

    if body.page or body.limit:
        page = body.page or 1
        limit = body.limit or 10
        total = q.count()
        rows = q.offset((page - 1) * limit).limit(limit).all()
        docs = [to_dict(u, exclude=exclude) for u in rows]
        return ok(paginate(docs, total, page, limit), "success")

    docs = [to_dict(u, exclude=exclude) for u in q.all()]
    return ok(docs, "User List")


@router.post("/view")
def view_user(body: UserViewIn, db: Session = Depends(get_db)):
    q = db.query(User)
    if body.userId:
        q = q.filter(User.id == body.userId)
    if body.emailId:
        q = q.filter(User.emailId == body.emailId.lower())
    if body.firstName:
        q = q.filter(User.firstName == body.firstName)
    if body.lastName:
        q = q.filter(User.lastName == body.lastName)
    if body.npiNumber:
        q = q.filter(User.npiNumber == body.npiNumber)
    user = q.first()
    return ok(to_dict(user, exclude={"password"}) if user else None, "User Details")


@router.put("")
def update_user(body: UserUpdateIn, db: Session = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    user_id = data.pop("userId", None)
    user_ids = data.pop("userIds", None)
    toggle = data.pop("toggle", False)

    for f in _NAME_FIELDS:
        if data.get(f):
            data[f] = data[f].lower().strip()
    data.pop("npiNumber", None)  # NPI is not editable
    if "password" in data:
        data["password"] = hash_password(data["password"])
    fields = {k: v for k, v in data.items() if k in WRITABLE}

    # Bulk edit.
    if user_ids:
        db.query(User).filter(User.id.in_(user_ids)).update(fields, synchronize_session=False)
        db.commit()
        return ok({}, "User Details Edited Successfully")

    if not user_id:
        raise HTTPException(400, "userId or userIds is required")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "can not get List")

    if "signature" in fields:  # bump count (legacy updateSignature)
        fields["signatureCount"] = (user.signatureCount or 0) + 1
    if toggle:  # legacy toggle: flip active state
        fields["isActive"] = not user.isActive

    for k, v in fields.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return ok(_public(user), "User Details Edited Successfully")


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User can not be Deleted")
    db.delete(user)
    db.query(UserAcl).filter(UserAcl.userId == user_id).delete()
    db.commit()
    return ok({}, "User Deleted")


@router.post("/validate")
def validate_user(body: UserValidateIn, db: Session = Depends(get_db)):
    errors: dict[str, list[str]] = {}
    if db.query(User).filter(User.emailId == body.emailId.lower()).first():
        errors["emailId"] = ["EmailId is already in use"]
    if body.npiNumber and db.query(User).filter(User.npiNumber == body.npiNumber).first():
        errors["npiNumber"] = ["NPI Number is already in use"]
    if errors:
        raise HTTPException(400, detail=errors)
    return ok(message="user validated successfully")
