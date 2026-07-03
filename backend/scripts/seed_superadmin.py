"""Seed a local superAdmin user so the frontend can log in (dev convenience).

Idempotent — re-running just refreshes the password/role. Run from backend root:

    .venv/bin/python -m scripts.seed_superadmin
"""

from __future__ import annotations

from core.database import SessionLocal
from core.security import hash_password
from services.user_service.models import Role, SystemConfig, User

EMAIL = "superadmin@gmail.com"
PASSWORD = "Welcome@1234"
INSTANCE_NAME = "Alturos Labs, LLC"


def main() -> None:
    db = SessionLocal()
    try:
        # superAdmin role (login reads roleObj.code == "superAdmin" for full access)
        role = db.query(Role).filter(Role.code == "superAdmin").first()
        if not role:
            role = Role(
                title="Super Admin",
                code="superAdmin",
                isSdiRole=True,
                isSignatureRequired=False,
            )
            db.add(role)
            db.commit()
            db.refresh(role)

        # SystemConfig id=1 → login attaches labConfiguration (instanceName) to the token
        config = db.get(SystemConfig, 1)
        if not config:
            config = SystemConfig(
                id=1,
                title=INSTANCE_NAME,
                labConfiguration={"instanceName": INSTANCE_NAME},
            )
            db.add(config)
            db.commit()

        # upsert the user
        user = db.query(User).filter(User.emailId == EMAIL).first()
        if not user:
            user = User(emailId=EMAIL, firstName="Super", lastName="Admin")
            db.add(user)
        user.password = hash_password(PASSWORD)
        user.isActive = True
        user.isDeleted = False
        user.roleId = role.id
        user.roleObj = {"id": role.id, "title": role.title, "code": role.code}
        db.commit()
        db.refresh(user)
        print(f"Seeded superAdmin: {EMAIL} (id={user.id}) password={PASSWORD!r}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
