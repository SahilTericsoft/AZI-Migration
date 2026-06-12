"""Tests for the Test Order service (PHI) — REAL ported logic: gk-code, draft +
counter defaults, list filters incl. patient search + patientDetails trimming,
results/guarantors/visits by order, SSN masking, auth, audit.
"""

import core.audit as audit_mod

TO = "/test-order"


def _order(client, headers, patient="John", last="Doe", **extra):
    return client.post(
        f"{TO}/orders",
        json={
            "facilityId": 1,
            "locationId": 2,
            "patientId": 3,
            "patientDetails": {
                "id": 3,
                "firstName": patient,
                "lastName": last,
                "gender": "M",
                "dateOfBirth": "1990-01-01",
                "ssn": "secret",
            },
            "loginUserId": 1,
            **extra,
        },
        headers=headers,
    )


def test_add_order_code_and_defaults(client, auth_headers):
    r = _order(client, auth_headers)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["code"] == f"gk{data['id']}"  # legacy gk-code scheme
    assert data["status"] == "draft"
    assert data["numberOfSamplesOrdered"] == 0 and data["numberOfSamplesResulted"] == 0
    assert data["source"] == "web"
    assert data["createdBy"] == 1


def test_order_requires_auth_and_fields(client, auth_headers):
    assert client.get(f"{TO}/orders/1").status_code == 401
    bad = client.post(f"{TO}/orders", json={"facilityId": 1}, headers=auth_headers)
    assert bad.status_code == 422  # missing required fields


def test_order_list_search_and_patient_trim(client, auth_headers):
    _order(client, auth_headers, patient="Alice", last="Anderson")
    _order(client, auth_headers, patient="Bob", last="Brown")
    res = client.post(f"{TO}/orders/list", json={"search": "alice"}, headers=auth_headers)
    body = res.json()["data"]
    assert body["total"] == 1
    pd = body["docs"][0]["patientDetails"]
    assert pd["firstName"] == "Alice"
    assert "ssn" not in pd  # patientDetails trimmed to safe fields


def test_order_list_filter_by_patient(client, auth_headers):
    _order(client, auth_headers)
    res = client.post(f"{TO}/orders/list", json={"patientId": 3}, headers=auth_headers)
    assert res.json()["data"]["total"] == 1
    none = client.post(f"{TO}/orders/list", json={"patientId": 999}, headers=auth_headers)
    assert none.json()["data"]["total"] == 0


def test_order_audited(client, auth_headers, db):
    oid = _order(client, auth_headers).json()["data"]["id"]
    client.get(f"{TO}/orders/{oid}", headers=auth_headers)
    actions = {
        x.action
        for x in db.query(audit_mod.AuditLog)
        .filter(audit_mod.AuditLog.entity == "Order", audit_mod.AuditLog.recordId == oid)
        .all()
    }
    assert {"create", "view"} <= actions


def test_results_by_order(client, auth_headers):
    oid = _order(client, auth_headers).json()["data"]["id"]
    client.post(
        f"{TO}/order-results", json={"orderId": oid, "resultedMode": "manual"}, headers=auth_headers
    )
    res = client.get(f"{TO}/order-results/by-order/{oid}", headers=auth_headers)
    assert len(res.json()["data"]) == 1


def test_guarantor_ssn_masked_and_by_order(client, auth_headers):
    r = client.post(
        f"{TO}/guarantors",
        json={"orderId": "ORD9", "familyName": "Doe", "ssnNumber": "999"},
        headers=auth_headers,
    )
    assert "ssnNumber" not in r.json()["data"]
    by_order = client.get(f"{TO}/guarantors/by-order/ORD9", headers=auth_headers)
    assert by_order.json()["data"]["familyName"] == "Doe"


def test_patient_visit_by_order(client, auth_headers):
    oid = _order(client, auth_headers).json()["data"]["id"]
    client.post(
        f"{TO}/patient-visits",
        json={"orderId": oid, "patientType": "outpatient"},
        headers=auth_headers,
    )
    res = client.get(f"{TO}/patient-visits/by-order/{oid}", headers=auth_headers)
    assert res.json()["data"]["patientType"] == "outpatient"
