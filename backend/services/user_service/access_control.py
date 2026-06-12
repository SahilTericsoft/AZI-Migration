"""Roles + ACL routes (consolidated).

Combines GkUserService RoleController + AclModuleController into one router.
Consolidations:
  - POST /modules                 = addAclModuleMappingData + addAclModuleMappingRawData (seed)
  - GET  /roles                   = role list + listLite (?search) + view (?roleId)
  - PUT  /roles/{id}/permissions  = addRoleAclModule + addBulkRoleAclModule (replace all)
Email side-effects (credentials mail) are TODOs until the email service migrates.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import generate_password, hash_password
from services.user_service.acl_seed import DEFAULT_ACL_MODULES
from services.user_service.models import AclModule, Role, RoleAcl, User, UserAcl
from services.user_service.schemas import (
    AclModuleIn,
    AssignUserRoleIn,
    RoleCreateIn,
    RolePermissionsIn,
)
from services.user_service.utils import ok, to_dict

router = APIRouter(prefix="/access-control", tags=["user-service: access-control"])


def _expand_rules(db: Session, rules, role_id: int, user_id: int | None = None) -> list[dict]:
    """Turn aclRules into RoleAcl/UserAcl rows, pulling apiAccess from the module."""
    records = []
    for rule in rules:
        module = db.query(AclModule).filter(AclModule.code == rule.code).first()
        record = {
            "roleId": role_id,
            "moduleAccess": rule.module,
            "featureAccess": rule.code,
            "apiAccess": list(module.apis) if module and module.apis else [],
        }
        if user_id is not None:
            record["userId"] = user_id
        records.append(record)
    return records


# ------------------------------------------------------------- ACL modules
@router.post("/modules")
def add_modules(body: AclModuleIn, db: Session = Depends(get_db)):
    if body.seed:
        rows = DEFAULT_ACL_MODULES
    elif body.modules:
        rows = body.modules
    elif body.module and body.code:
        rows = [
            {
                "module": body.module,
                "feature": body.feature,
                "code": body.code,
                "description": body.description,
                "apis": body.apis or [],
            }
        ]
    else:
        raise HTTPException(400, "Provide `seed`, `modules`, or a single module")
    db.add_all([AclModule(**r) for r in rows])
    db.commit()
    return ok(rows, "acl data")


@router.get("/modules")
def list_modules(db: Session = Depends(get_db)):
    data = [
        {
            "module": m.module,
            "feature": m.feature,
            "code": m.code,
            "description": m.description,
            "isPrimary": m.isPrimary,
        }
        for m in db.query(AclModule).all()
    ]
    return ok(data, "acl data")


# ------------------------------------------------------------------- roles
@router.post("/roles")
def create_role(body: RoleCreateIn, db: Session = Depends(get_db)):
    role = Role(title=body.role, code=body.role, isSdiRole=False)
    db.add(role)
    db.flush()  # need role.id
    db.query(RoleAcl).filter(RoleAcl.roleId == role.id).delete()
    records = _expand_rules(db, body.aclRules, role.id)
    db.add_all([RoleAcl(**r) for r in records])
    db.commit()
    return ok(records, "acl data")


@router.get("/roles")
def list_roles(
    roleId: int | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int | None = Query(default=None),
    limit: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if roleId is not None:  # view one
        return ok(to_dict(db.get(Role, roleId)), "Role Details")

    q = db.query(Role)
    if search and search.strip():
        like = f"%{search.strip()}%"
        q = q.filter(Role.title.ilike(like) | Role.code.ilike(like))
    q = q.order_by(Role.createdAt.desc())

    if page or limit:
        page, limit = page or 1, limit or 10
        total = q.count()
        rows = [to_dict(r) for r in q.offset((page - 1) * limit).limit(limit).all()]
        return ok({"page": page, "limit": limit, "docs": rows, "total": total}, "Role List")
    return ok([to_dict(r) for r in q.all()], "Role List")


@router.put("/roles/{role_id}/permissions")
def set_role_permissions(role_id: int, body: RolePermissionsIn, db: Session = Depends(get_db)):
    db.query(RoleAcl).filter(RoleAcl.roleId == role_id).delete()
    records = _expand_rules(db, body.aclRules, role_id)
    db.add_all([RoleAcl(**r) for r in records])
    db.commit()
    return ok(records, "acl data")


@router.get("/roles/{role_id}/permissions")
def get_role_permissions(role_id: int, db: Session = Depends(get_db)):
    rows = [to_dict(r) for r in db.query(RoleAcl).filter(RoleAcl.roleId == role_id).all()]
    return ok(rows, "acl data")


# ------------------------------------------------------- user role / perms
@router.put("/users/{user_id}/role")
def assign_user_role(user_id: int, body: AssignUserRoleIn, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    role = db.get(Role, body.roleId)
    if not role:
        raise HTTPException(404, "Role not found")

    db.query(UserAcl).filter(UserAcl.userId == user_id).delete()
    records = _expand_rules(db, body.aclRules, body.roleId, user_id=user_id)
    db.add_all([UserAcl(**r) for r in records])

    if not user.password:  # first-time role assignment -> set a password
        user.password = hash_password(generate_password(12))
        # TODO(email service): email the generated credentials to the user.

    user.roleId = body.roleId
    user.roleObj = {
        "id": role.id,
        "title": role.title,
        "code": role.code,
        "isSdiRole": role.isSdiRole,
    }
    if body.isHybrid is not None:
        user.isHybrid = body.isHybrid
    if body.isActive is not None:
        user.isActive = body.isActive
    db.commit()
    return ok(records, "acl data")


@router.get("/users/{user_id}/permissions")
def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    rows = [to_dict(r) for r in db.query(UserAcl).filter(UserAcl.userId == user_id).all()]
    return ok(rows, "acl data")
