"""Tests for the consolidated User service (real Postgres + TestClient).

Covers every endpoint: success paths and the key error paths migrated from the
old GkUserService controllers.
"""

import services.user_service.models as m

BASE = "/user-service"


# =====================================================================
# AUTH
# =====================================================================
def test_login_success(client, make_user, db):
    make_user(emailId="admin@example.com", password="secret123")
    db.add(m.SystemConfig(id=1, title="cfg", labConfiguration={"theme": "light"}))
    db.commit()

    r = client.post(
        f"{BASE}/auth/login", json={"emailId": "admin@example.com", "password": "secret123"}
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["emailId"] == "admin@example.com"
    assert "password" not in data
    assert data["token"]
    assert data["systemConfig"] == {"theme": "light"}
    assert "userAccessModules" in data


def test_login_wrong_password(client, make_user):
    make_user(password="secret123")
    r = client.post(
        f"{BASE}/auth/login", json={"emailId": "admin@example.com", "password": "wrongpass1"}
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Invalid login credentials"


def test_login_user_not_found(client):
    r = client.post(
        f"{BASE}/auth/login", json={"emailId": "ghost@example.com", "password": "secret123"}
    )
    assert r.status_code == 404


def test_login_inactive(client, make_user):
    make_user(is_active=False)
    r = client.post(
        f"{BASE}/auth/login", json={"emailId": "admin@example.com", "password": "secret123"}
    )
    assert r.status_code == 403
    assert "Inactive" in r.json()["detail"]


def test_login_validation_short_password(client):
    r = client.post(f"{BASE}/auth/login", json={"emailId": "admin@example.com", "password": "x"})
    assert r.status_code == 422  # pydantic validation


def test_check_login_flow(client, make_user):
    make_user()
    token = client.post(
        f"{BASE}/auth/login", json={"emailId": "admin@example.com", "password": "secret123"}
    ).json()["data"]["token"]
    ok = client.get(f"{BASE}/auth/check-login", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200
    assert ok.json()["data"]["emailId"] == "admin@example.com"


def test_check_login_missing_and_invalid(client):
    assert client.get(f"{BASE}/auth/check-login").status_code == 403
    bad = client.get(f"{BASE}/auth/check-login", headers={"Authorization": "Bearer nope"})
    assert bad.status_code == 403


def test_logout_invalidates_session(client, make_user):
    user = make_user()
    token = client.post(
        f"{BASE}/auth/login", json={"emailId": "admin@example.com", "password": "secret123"}
    ).json()["data"]["token"]
    assert client.post(f"{BASE}/auth/logout", json={"userId": user.id}).status_code == 200
    after = client.get(f"{BASE}/auth/check-login", headers={"Authorization": f"Bearer {token}"})
    assert after.status_code == 403


def test_verify_password(client, make_user):
    user = make_user(password="secret123")
    good = client.post(
        f"{BASE}/auth/verify-password", json={"userId": user.id, "password": "secret123"}
    )
    assert good.status_code == 200
    bad = client.post(
        f"{BASE}/auth/verify-password", json={"userId": user.id, "password": "nopenope1"}
    )
    assert bad.status_code == 403


def test_forgot_password(client, make_user):
    make_user(emailId="admin@example.com", password="oldsecret1")
    r = client.put(
        f"{BASE}/auth/forgot-password",
        json={"emailId": "admin@example.com", "newPassword": "newsecret1"},
    )
    assert r.status_code == 200
    assert (
        client.post(
            f"{BASE}/auth/login", json={"emailId": "admin@example.com", "password": "oldsecret1"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"{BASE}/auth/login", json={"emailId": "admin@example.com", "password": "newsecret1"}
        ).status_code
        == 200
    )


def test_send_forgot_password_mail(client, make_user):
    make_user(emailId="admin@example.com")
    assert (
        client.post(
            f"{BASE}/auth/forgot-password/send-mail", json={"emailId": "admin@example.com"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"{BASE}/auth/forgot-password/send-mail", json={"emailId": "ghost@example.com"}
        ).status_code
        == 403
    )


def test_system_config_list_and_view(client, db):
    db.add(m.SystemConfig(title="Default", url="https://x", labConfiguration={"a": 1}))
    db.commit()
    lst = client.get(f"{BASE}/auth/system-config")
    assert lst.status_code == 200 and len(lst.json()["data"]) == 1
    one = client.get(f"{BASE}/auth/system-config", params={"id": 1})
    assert one.json()["data"]["title"] == "Default"


# =====================================================================
# USERS
# =====================================================================
def test_create_user(client, make_role):
    role = make_role(code="labUser")
    r = client.post(
        f"{BASE}/users",
        json={
            "firstName": "John",
            "lastName": "Doe",
            "loginUserId": 1,
            "roleId": role.id,
            "emailId": "john@example.com",
            "password": "secret123",
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["firstName"] == "john" and data["emailId"] == "john@example.com"
    assert "password" not in data
    assert data["internalUserId"] is not None
    assert data["roleObj"]["code"] == "labUser"


def test_create_user_duplicate_email(client, make_user):
    make_user(emailId="dupe@example.com")
    r = client.post(
        f"{BASE}/users",
        json={
            "firstName": "A",
            "lastName": "B",
            "loginUserId": 1,
            "emailId": "dupe@example.com",
        },
    )
    assert r.status_code == 409


def test_create_user_duplicate_npi(client, make_user):
    make_user(emailId="x@example.com", npi="123")
    r = client.post(
        f"{BASE}/users",
        json={
            "firstName": "A",
            "lastName": "B",
            "loginUserId": 1,
            "npiNumber": "123",
        },
    )
    assert r.status_code == 409


def test_list_users_paginated_and_filtered(client, make_user):
    make_user(emailId="a@example.com", first="alice", role_code="superAdmin")
    make_user(emailId="b@example.com", first="bob", role_code="labUser")

    full = client.post(f"{BASE}/users/list", json={})
    assert full.status_code == 200 and len(full.json()["data"]) == 2

    page = client.post(f"{BASE}/users/list", json={"page": 1, "limit": 1})
    body = page.json()["data"]
    assert body["total"] == 2 and len(body["docs"]) == 1

    search = client.post(f"{BASE}/users/list", json={"search": "alice"})
    assert len(search.json()["data"]) == 1

    by_role = client.post(f"{BASE}/users/list", json={"roleCodes": ["labUser"]})
    assert len(by_role.json()["data"]) == 1


def test_view_user(client, make_user):
    user = make_user(emailId="v@example.com")
    by_id = client.post(f"{BASE}/users/view", json={"userId": user.id})
    assert by_id.json()["data"]["emailId"] == "v@example.com"
    by_email = client.post(f"{BASE}/users/view", json={"emailId": "v@example.com"})
    assert by_email.json()["data"]["id"] == user.id


def test_update_user_single_and_toggle_and_signature(client, make_user, db):
    user = make_user()
    # edit a field
    edit = client.put(f"{BASE}/users", json={"userId": user.id, "firstName": "Renamed"})
    assert edit.json()["data"]["firstName"] == "renamed"
    # toggle active
    tog = client.put(f"{BASE}/users", json={"userId": user.id, "toggle": True})
    assert tog.json()["data"]["isActive"] is False
    # signature bumps count
    sig = client.put(f"{BASE}/users", json={"userId": user.id, "signature": "sig"})
    assert sig.json()["data"]["signatureCount"] == 1


def test_bulk_edit_users(client, make_user):
    u1 = make_user(emailId="a@example.com")
    u2 = make_user(emailId="b@example.com")
    r = client.put(f"{BASE}/users", json={"userIds": [u1.id, u2.id], "isActive": False})
    assert r.status_code == 200
    lst = client.post(f"{BASE}/users/list", json={"isActive": False})
    assert len(lst.json()["data"]) == 2


def test_delete_user(client, make_user, db):
    user = make_user()
    db.add(m.UserAcl(userId=user.id, moduleAccess="Lab", featureAccess="labList"))
    db.commit()
    assert client.delete(f"{BASE}/users/{user.id}").status_code == 200
    assert db.query(m.User).count() == 0
    assert db.query(m.UserAcl).filter(m.UserAcl.userId == user.id).count() == 0


def test_validate_user(client, make_user):
    make_user(emailId="taken@example.com")
    conflict = client.post(f"{BASE}/users/validate", json={"emailId": "taken@example.com"})
    assert conflict.status_code == 400
    assert "emailId" in conflict.json()["detail"]
    ok = client.post(f"{BASE}/users/validate", json={"emailId": "free@example.com"})
    assert ok.status_code == 200


# =====================================================================
# ACCESS CONTROL
# =====================================================================
def test_seed_and_list_modules(client):
    seed = client.post(f"{BASE}/access-control/modules", json={"seed": True})
    assert seed.status_code == 200
    lst = client.get(f"{BASE}/access-control/modules")
    assert len(lst.json()["data"]) >= 50


def test_create_role_with_permissions(client):
    client.post(f"{BASE}/access-control/modules", json={"seed": True})
    r = client.post(
        f"{BASE}/access-control/roles",
        json={
            "role": "nurse",
            "aclRules": [{"module": "Lab", "code": "labList"}],
        },
    )
    assert r.status_code == 200
    roles = client.get(f"{BASE}/access-control/roles").json()["data"]
    role_id = next(x["id"] for x in roles if x["code"] == "nurse")
    perms = client.get(f"{BASE}/access-control/roles/{role_id}/permissions").json()["data"]
    assert len(perms) == 1 and perms[0]["featureAccess"] == "labList"


def test_set_role_permissions_replaces(client, make_role):
    role = make_role(code="tech")
    client.put(
        f"{BASE}/access-control/roles/{role.id}/permissions",
        json={
            "aclRules": [
                {"module": "Lab", "code": "labList"},
                {"module": "Lab", "code": "labEdit"},
            ],
        },
    )
    client.put(
        f"{BASE}/access-control/roles/{role.id}/permissions",
        json={
            "aclRules": [{"module": "Lab", "code": "labList"}],
        },
    )
    perms = client.get(f"{BASE}/access-control/roles/{role.id}/permissions").json()["data"]
    assert len(perms) == 1


def test_assign_user_role_sets_password(client, make_role, db):
    role = make_role(code="labUser")
    user = m.User(
        firstName="no", lastName="pass", emailId="np@example.com", isActive=True, isDeleted=False
    )  # no password
    db.add(user)
    db.commit()
    db.refresh(user)

    r = client.put(
        f"{BASE}/access-control/users/{user.id}/role",
        json={
            "roleId": role.id,
            "aclRules": [{"module": "Lab", "code": "labList"}],
        },
    )
    assert r.status_code == 200
    perms = client.get(f"{BASE}/access-control/users/{user.id}/permissions").json()["data"]
    assert len(perms) == 1
    db.expire_all()
    assert db.get(m.User, user.id).password is not None  # password generated


# =====================================================================
# STATIC DATA
# =====================================================================
def test_geo_add_list_lookup_delete(client):
    client.post(
        f"{BASE}/static-data/geo",
        json={
            "address": [
                {
                    "city": "austin",
                    "state": "TX",
                    "zipcode": "73301",
                    "county": "travis",
                    "country": "US",
                    "timezone": "America/Chicago",
                },
                {
                    "city": "dallas",
                    "state": "TX",
                    "zipcode": "75001",
                    "county": "dallas",
                    "country": "US",
                    "timezone": "America/Chicago",
                },
            ]
        },
    )
    zips = client.get(f"{BASE}/static-data/geo", params={"type": "zipcodes"}).json()["data"]
    assert zips["total"] == 2
    states = client.get(f"{BASE}/static-data/geo", params={"type": "states"}).json()["data"]
    assert states["docs"] == [{"state": "TX"}]  # distinct
    cities = client.get(
        f"{BASE}/static-data/geo", params={"type": "cities", "search": "aus"}
    ).json()["data"]
    assert cities["docs"] == [{"city": "austin"}]
    one = client.get(f"{BASE}/static-data/geo/zipcode/73301").json()["data"]
    assert one["city"] == "austin"
    client.request("DELETE", f"{BASE}/static-data/geo", json={"zipcodes": ["73301"]})
    assert (
        client.get(f"{BASE}/static-data/geo", params={"type": "zipcodes"}).json()["data"]["total"]
        == 1
    )


def test_dropdowns_crud(client):
    client.post(
        f"{BASE}/static-data/dropdowns",
        json={"title": "prefix", "value": [{"code": "mr", "label": "Mr"}]},
    )
    got = client.get(f"{BASE}/static-data/dropdowns/prefix").json()["data"]
    assert got == [{"code": "mr", "label": "Mr"}]
    # append
    client.put(
        f"{BASE}/static-data/dropdowns",
        json={"title": "prefix", "value": [{"code": "ms", "label": "Ms"}]},
    )
    assert len(client.get(f"{BASE}/static-data/dropdowns/prefix").json()["data"]) == 2
    # duplicate code rejected
    dup = client.put(
        f"{BASE}/static-data/dropdowns",
        json={"title": "prefix", "value": [{"code": "mr", "label": "Mr"}]},
    )
    assert dup.status_code == 409
    # delete
    client.request(
        "DELETE", f"{BASE}/static-data/dropdowns", json={"title": "prefix", "codes": ["mr"]}
    )
    remaining = client.get(f"{BASE}/static-data/dropdowns/prefix").json()["data"]
    assert remaining == [{"code": "ms", "label": "Ms"}]
