"""Tests for the Sample service (PHI) — REAL ported logic: order validation,
barcode fan-out, sm-code, order sample-counter increment, sampleType derivation,
accession flow, by-order listing; plus auth + audit.
"""

import core.audit as audit_mod
import services.test_order.models as om

SAMP = "/sample"
TO = "/test-order"


def _order(client, headers):
    return client.post(
        f"{TO}/orders",
        json={
            "facilityId": 1,
            "locationId": 2,
            "patientId": 3,
            "patientDetails": {"firstName": "P", "lastName": "Q"},
            "loginUserId": 1,
        },
        headers=headers,
    ).json()["data"]["id"]


def _add_sample(client, headers, order_id, barcode="BC1", **extra):
    return client.post(
        f"{SAMP}/samples",
        json={
            "orderId": order_id,
            "barcode": barcode,
            "physicianId": 7,
            "physicianDetails": {"name": "Dr"},
            "loginUserId": 1,
            "panelDetails": {"sampleType": "blood"},
            **extra,
        },
        headers=headers,
    )


def test_add_sample_defaults_and_code(client, auth_headers, db):
    oid = _order(client, auth_headers)
    r = _add_sample(client, auth_headers, oid, barcode="BC9")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["sampleCode"] == f"sm{data['id']}"
    assert data["barcode"] == "BC9" == data["patientBarcode"] == data["labBarcode"]
    assert data["isAccessioned"] is False
    assert data["sampleType"] == "blood"  # derived from panelDetails
    # parent order's sample counter incremented
    db.expire_all()
    assert db.get(om.Order, oid).numberOfSamplesOrdered == 1


def test_add_sample_rejects_bad_order(client, auth_headers):
    assert _add_sample(client, auth_headers, 999).status_code == 400


def test_sample_requires_auth(client):
    assert client.get(f"{SAMP}/samples/1").status_code == 401


def test_sample_accession_flow(client, auth_headers):
    oid = _order(client, auth_headers)
    sid = _add_sample(client, auth_headers, oid).json()["data"]["id"]
    res = client.put(
        f"{SAMP}/samples/{sid}/accession",
        json={"accessionedBy": 5, "status": "accessioned"},
        headers=auth_headers,
    )
    data = res.json()["data"]
    assert data["isAccessioned"] is True
    assert data["accessionedBy"] == 5
    assert data["accessionedDate"] is not None and data["status"] == "accessioned"


def test_sample_edit_syncs_barcodes(client, auth_headers):
    oid = _order(client, auth_headers)
    sid = _add_sample(client, auth_headers, oid).json()["data"]["id"]
    res = client.put(f"{SAMP}/samples/{sid}", json={"barcode": "NEW"}, headers=auth_headers)
    data = res.json()["data"]
    assert data["barcode"] == data["patientBarcode"] == data["labBarcode"] == "NEW"


def test_sample_list_and_by_order(client, auth_headers):
    oid = _order(client, auth_headers)
    _add_sample(client, auth_headers, oid, barcode="A1")
    _add_sample(client, auth_headers, oid, barcode="A2")
    by_order = client.get(f"{SAMP}/samples/by-order/{oid}", headers=auth_headers)
    assert len(by_order.json()["data"]) == 2
    by_barcode = client.post(f"{SAMP}/samples/list", json={"barcode": "A1"}, headers=auth_headers)
    assert by_barcode.json()["data"]["total"] == 1


def test_sample_audited(client, auth_headers, db):
    oid = _order(client, auth_headers)
    sid = _add_sample(client, auth_headers, oid).json()["data"]["id"]
    assert (
        db.query(audit_mod.AuditLog)
        .filter(audit_mod.AuditLog.entity == "Sample", audit_mod.AuditLog.recordId == sid)
        .count()
        >= 1
    )
