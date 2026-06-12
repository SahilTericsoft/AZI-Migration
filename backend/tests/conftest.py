"""Test fixtures: real Postgres test DB + FastAPI TestClient.

Sets the test DATABASE_URL before importing the app, creates a fresh schema per
test, and overrides get_db to use the test session.
"""

import os

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://sahilkindarle@localhost:5432/azi_user_test",
)
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import every service's models + audit so Base.metadata.create_all builds all
# tables for the test schema. Aliased + referenced below so linters see them used.
import core.audit as _audit
import services.activity_log.models as _act
import services.billing.models as _bill
import services.d2c.models as _d2c
import services.dynamic_form.models as _form
import services.facility.models as _fac
import services.integration.models as _intg
import services.inventory.models as _inv
import services.lab.models as _lab
import services.lab_os.models as _labos
import services.location.models as _loc
import services.messaging.models as _msg
import services.notification.models as _notif
import services.patient.models as _pat
import services.result.models as _res
import services.sample.models as _samp
import services.sendout.models as _so
import services.state_reporting.models as _sr
import services.test_config.models as _tc
import services.test_order.models as _to
import services.user_service.models as m
from core.config import settings
from core.database import Base, get_db
from core.security import create_token, hash_password
from main import app

_REGISTERED = (
    _audit,
    _tc,
    _lab,
    _fac,
    _loc,
    _pat,
    _to,
    _samp,
    _notif,
    _act,
    _msg,
    _inv,
    _labos,
    _form,
    _bill,
    _d2c,
    _sr,
    _so,
    _res,
    _intg,
)

engine = create_engine(settings.database_url)
TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db():
    s = TestSession()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def client():
    def _override():
        s = TestSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ----------------------------------------------------------------- helpers
@pytest.fixture
def auth_headers():
    """Bearer header for a valid (superAdmin) session — for PHI endpoints."""
    token, _ = create_token({"id": 1, "roleObj": {"code": "superAdmin"}})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def make_role(db):
    def _make(code="superAdmin", title=None, is_sdi=True):
        role = m.Role(title=title or code, code=code, isSdiRole=is_sdi)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    return _make


@pytest.fixture
def make_user(db, make_role):
    def _make(
        emailId="admin@example.com",
        password="secret123",
        role_code="superAdmin",
        is_active=True,
        first="ada",
        last="admin",
        npi=None,
    ):
        role = make_role(code=role_code)
        user = m.User(
            firstName=first,
            lastName=last,
            emailId=emailId.lower(),
            password=hash_password(password),
            roleId=role.id,
            roleObj={"id": role.id, "code": role_code, "title": role_code},
            isActive=is_active,
            isDeleted=False,
            npiNumber=npi,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _make
