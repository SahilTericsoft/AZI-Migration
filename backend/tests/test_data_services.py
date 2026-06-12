"""Tests for the data/support services' REAL ported logic:
notification, activity_log, messaging (OTP), inventory, billing, lab_os, d2c
(auth + pricing), state_reporting, sendout, result, integration.
"""

import services.messaging.models as mm


# ----------------------------------------------------------- notification
def test_notification_defaults_user_scope_and_read(client):
    r = client.post(
        "/notification/notifications", json={"message": "hi", "title": "T", "toUserId": 5}
    )
    assert r.json()["data"]["isActive"] is True
    nid = r.json()["data"]["id"]
    client.post("/notification/notifications", json={"message": "x", "toUserId": 9})
    mine = client.post("/notification/notifications/list", json={"toUserId": 5})
    assert mine.json()["data"]["total"] == 1
    client.put(f"/notification/notifications/{nid}/read")
    assert client.get(f"/notification/notifications/{nid}").json()["data"]["isActive"] is False


def test_notification_requires_recipient(client):
    assert client.post("/notification/notifications", json={"message": "x"}).status_code == 422


# ----------------------------------------------------------- activity_log
def test_activity_log_bulk_and_filter(client):
    client.post(
        "/activity-log/logs/bulk",
        json={
            "logs": [
                {"module": "Patient", "action": "create", "identityId": 1},
                {"module": "Order", "action": "edit", "identityId": 2},
            ]
        },
    )
    res = client.post("/activity-log/logs/list", json={"identityId": 1})
    assert res.json()["data"]["total"] == 1


# --------------------------------------------------------------- messaging
def test_email_otp_generate_and_verify(client, db):
    gen = client.post("/messaging/email/otp/generate", json={"emailId": "a@x.com"})
    assert "code" not in gen.json()["data"]  # masked
    code = db.query(mm.EmailSecurity).filter(mm.EmailSecurity.emailId == "a@x.com").first().code
    ok = client.post("/messaging/email/otp/verify", json={"emailId": "a@x.com", "code": code})
    assert ok.json()["data"]["verified"] is True
    # consumed -> second verify fails
    again = client.post("/messaging/email/otp/verify", json={"emailId": "a@x.com", "code": code})
    assert again.status_code == 400


def test_email_otp_wrong_code(client):
    client.post("/messaging/email/otp/generate", json={"emailId": "b@x.com"})
    bad = client.post("/messaging/email/otp/verify", json={"emailId": "b@x.com", "code": "000000"})
    assert bad.status_code == 400


def test_sms_template_by_purpose(client):
    client.post("/messaging/sms/templates", json={"purpose": "otp", "message": "code {x}"})
    res = client.get("/messaging/sms/templates/by-purpose/otp")
    assert res.json()["data"]["message"] == "code {x}"


# --------------------------------------------------------------- inventory
def test_inventory_item_uniqueness_and_low_stock(client):
    r = client.post("/inventory/items", json={"name": "Reagent", "quantity": 3, "alertQuantity": 5})
    assert r.json()["data"]["isLowStock"] is True  # 3 <= 5
    assert client.post("/inventory/items", json={"name": "reagent"}).status_code == 409
    healthy = client.post(
        "/inventory/items", json={"name": "Tubes", "quantity": 50, "alertQuantity": 5}
    )
    assert healthy.json()["data"]["isLowStock"] is False


def test_inventory_toggle_subitems_and_lots(client):
    iid = client.post("/inventory/items", json={"name": "Kit"}).json()["data"]["id"]
    assert client.put(f"/inventory/items/{iid}/toggle").json()["data"]["isActive"] is False
    client.post("/inventory/sub-items", json={"inventoryItemId": iid, "name": "Vial"})
    assert (
        client.post(
            "/inventory/sub-items", json={"inventoryItemId": iid, "name": "vial"}
        ).status_code
        == 409
    )
    client.post("/inventory/quantities", json={"itemId": iid, "lotNumber": "L1"})
    client.post("/inventory/quantities", json={"itemId": iid, "lotNumber": "L2"})
    lots = client.get(f"/inventory/items/{iid}/lot-numbers")
    assert lots.json()["data"] == ["L1", "L2"]


def test_product_uniqueness(client):
    client.post("/inventory/products", json={"name": "Panel A"})
    assert client.post("/inventory/products", json={"name": "panel a"}).status_code == 409


# ----------------------------------------------------------------- billing
def test_insurer_uniqueness(client):
    client.post("/billing/insurers", json={"title": "Aetna", "code": "AET"})
    assert client.post("/billing/insurers", json={"title": "aetna"}).status_code == 409


# ------------------------------------------------------------------ lab_os
def test_department_uniqueness_and_by_lab(client):
    client.post("/lab-os/departments", json={"name": "Molecular", "code": "MOL"})
    assert client.post("/lab-os/departments", json={"name": "molecular"}).status_code == 409
    client.post("/lab-os/instruments", json={"instrument": "PCR", "labId": 3})
    by_lab = client.get("/lab-os/instruments/by-lab/3")
    assert len(by_lab.json()["data"]) == 1


# -------------------------------------------------------------------- d2c
def test_d2c_signup_login_and_password(client):
    r = client.post(
        "/d2c/customers/sign-up",
        json={"emailId": "C@x.com", "password": "secret123", "firstName": "Cara"},
    )
    assert "password" not in r.json()["data"]
    assert (
        client.post(
            "/d2c/customers/sign-up", json={"emailId": "c@x.com", "password": "x"}
        ).status_code
        == 409
    )  # dup
    ok = client.post("/d2c/customers/login", json={"emailId": "c@x.com", "password": "secret123"})
    assert ok.json()["message"] == "Login Successful"
    bad = client.post("/d2c/customers/login", json={"emailId": "c@x.com", "password": "wrong"})
    assert bad.status_code == 403


def test_d2c_forgot_password(client):
    client.post("/d2c/customers/sign-up", json={"emailId": "d@x.com", "password": "oldsecret1"})
    client.put(
        "/d2c/customers/forgot-password", json={"emailId": "d@x.com", "newPassword": "newsecret1"}
    )
    assert (
        client.post(
            "/d2c/customers/login", json={"emailId": "d@x.com", "password": "newsecret1"}
        ).status_code
        == 200
    )


def test_d2c_address_default_and_order_pricing(client, auth_headers):
    client.post("/d2c/addresses", json={"customerId": 1, "isDefault": True}, headers=auth_headers)
    a2 = client.post(
        "/d2c/addresses", json={"customerId": 1, "isDefault": True}, headers=auth_headers
    ).json()["data"]["id"]
    # making a2 default unsets a1
    addrs = client.get("/d2c/addresses/by-customer/1", headers=auth_headers).json()["data"]
    defaults = [a["id"] for a in addrs if a["isDefault"]]
    assert defaults == [a2]

    order = client.post(
        "/d2c/orders",
        json={
            "customerId": 1,
            "products": [
                {"productId": 1, "quantity": 2, "productDetails": {"price": 50}},
                {"productId": 2, "quantity": 1, "productDetails": {"price": 30}},
            ],
        },
        headers=auth_headers,
    )
    data = order.json()["data"]
    assert data["summary"]["total"] == 130.0  # 2*50 + 1*30
    assert data["orderCode"] == f"D2C{data['id']}"


def test_d2c_requires_auth(client):
    assert client.get("/d2c/customers/1").status_code == 401


# ------------------------------------------------- state_reporting / sendout
def test_state_reporting_defaults_and_auth(client, auth_headers):
    assert client.post("/state-reporting/reports", json={}).status_code == 401
    r = client.post("/state-reporting/reports", json={"sampleIds": [1, 2]}, headers=auth_headers)
    assert r.json()["data"]["status"] == "pending"
    rid = r.json()["data"]["id"]
    client.post(
        "/state-reporting/sessions",
        json={"stateReportingId": rid, "attempt": 1},
        headers=auth_headers,
    )
    sessions = client.get(f"/state-reporting/reports/{rid}/sessions", headers=auth_headers)
    assert len(sessions.json()["data"]) == 1


def test_sendout_sample_count_derived(client, auth_headers):
    r = client.post(
        "/sendout/batches",
        json={"sendoutLabId": 3, "sampleIds": [1, 2, 3, 4]},
        headers=auth_headers,
    )
    assert r.json()["data"]["sampleCount"] == 4  # derived from sampleIds


# --------------------------------------------------------------- result
def test_result_by_session(client, auth_headers):
    client.post(
        "/result/samples",
        json={"uploadResultSessionId": 7, "sampleId": 1, "orderId": 1},
        headers=auth_headers,
    )
    res = client.get("/result/samples/by-session/7", headers=auth_headers)
    assert len(res.json()["data"]) == 1


# --------------------------------------------------------- dynamic_form
def test_dynamic_form_chat_crud(client):
    r = client.post("/dynamic-form/chats", json={"icon": "form", "chatData": [{"q": "name?"}]})
    assert r.status_code == 200
    cid = r.json()["data"]["id"]
    assert client.get(f"/dynamic-form/chats/{cid}").json()["data"]["icon"] == "form"
    client.put(f"/dynamic-form/chats/{cid}", json={"icon": "intake"})
    assert client.get(f"/dynamic-form/chats/{cid}").json()["data"]["icon"] == "intake"


# ----------------------------------------------------------- integration
def test_advancedmd_upsert_and_mask(client, auth_headers):
    first = client.post(
        "/integration/advancedmd-tokens",
        json={"userName": "amd", "officeKey": "K1", "token": "t1"},
        headers=auth_headers,
    )
    assert "token" not in first.json()["data"]
    tid = first.json()["data"]["id"]
    # same userName+officeKey upserts (no new row)
    second = client.post(
        "/integration/advancedmd-tokens",
        json={"userName": "amd", "officeKey": "K1", "token": "t2"},
        headers=auth_headers,
    )
    assert second.json()["data"]["id"] == tid
    assert second.json()["message"] == "AdvancedMD token updated"
