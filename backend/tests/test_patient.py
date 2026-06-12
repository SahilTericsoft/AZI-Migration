"""Tests for the Patient service (PHI) — REAL ported logic: deterministic dup
code, name/SSN normalization, internal id, allergy merge, soft-delete/recover,
rich search; plus HIPAA controls (auth, SSN masking, audit)."""

import core.audit as audit_mod
import services.patient.models as pm

PAT = "/patient"


def _add(client, headers, first="John", last="Doe", dob="1990-01-01", **extra):
    return client.post(
        f"{PAT}/patients",
        json={"firstName": first, "lastName": last, "dateOfBirth": dob, "loginUserId": 1, **extra},
        headers=headers,
    )


def test_add_patient_normalizes_and_generates_ids(client, auth_headers):
    r = _add(client, auth_headers, first="John", last="Doe")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["firstName"] == "john" and data["lastName"] == "doe"  # lowercased
    assert data["code"] == "johndoe19900101"  # deterministic unique code
    assert data["internalPatientId"] is not None
    assert data["isActive"] is True and data["isDeleted"] is False
    assert data["createdBy"] == 1


def test_add_duplicate_returns_existing(client, auth_headers):
    first = _add(client, auth_headers).json()["data"]["id"]
    dup = _add(client, auth_headers)  # same name + dob
    assert dup.json()["message"] == "Patient Already Exists"
    assert dup.json()["data"]["id"] == first  # no new row


def test_patient_requires_auth(client):
    assert client.get(f"{PAT}/patients/1").status_code == 401
    assert client.post(f"{PAT}/patients", json={"firstName": "x"}).status_code == 401


def test_patient_add_requires_dob(client, auth_headers):
    r = client.post(
        f"{PAT}/patients", json={"firstName": "A", "lastName": "B"}, headers=auth_headers
    )
    assert r.status_code == 422  # dateOfBirth required by schema


def test_patient_ssn_masked(client, auth_headers):
    r = _add(client, auth_headers, ssn="111-22-3333", password="secret", drivingLicenseNumber="DL9")
    data = r.json()["data"]
    assert not ({"ssn", "password", "drivingLicenseNumber"} & set(data))


def test_patient_audited(client, auth_headers, db):
    rid = _add(client, auth_headers, first="Aud", last="It").json()["data"]["id"]
    client.get(f"{PAT}/patients/{rid}", headers=auth_headers)
    logs = (
        db.query(audit_mod.AuditLog)
        .filter(audit_mod.AuditLog.entity == "Patient", audit_mod.AuditLog.recordId == rid)
        .all()
    )
    assert {"create", "view"} <= {x.action for x in logs}
    assert all(x.userId == 1 for x in logs)


def test_patient_edit_merges_allergies(client, auth_headers, db):
    rid = _add(client, auth_headers).json()["data"]["id"]
    db.query(pm.Patient).filter(pm.Patient.id == rid).update({"allergieIds": [1, 2]})
    db.commit()
    res = client.put(f"{PAT}/patients/{rid}", json={"allergieIds": [2, 3]}, headers=auth_headers)
    assert sorted(res.json()["data"]["allergieIds"]) == [1, 2, 3]  # union


def test_patient_soft_delete_and_recover(client, auth_headers, db):
    rid = _add(client, auth_headers, first="Soft", last="Del").json()["data"]["id"]
    client.delete(f"{PAT}/patients/{rid}", headers=auth_headers)
    assert client.get(f"{PAT}/patients/{rid}", headers=auth_headers).status_code == 404
    assert db.get(pm.Patient, rid).isDeleted is True  # retained
    # recover
    client.put(f"{PAT}/patients/{rid}/recover", headers=auth_headers)
    assert client.get(f"{PAT}/patients/{rid}", headers=auth_headers).status_code == 200


def test_patient_list_search_and_excludes_deleted(client, auth_headers):
    _add(client, auth_headers, first="Alice", last="Anderson")
    bob = _add(client, auth_headers, first="Bob", last="Brown").json()["data"]["id"]
    client.delete(f"{PAT}/patients/{bob}", headers=auth_headers)

    res = client.post(f"{PAT}/patients/list", json={}, headers=auth_headers)
    assert res.json()["data"]["total"] == 1  # deleted excluded
    search = client.post(f"{PAT}/patients/list", json={"search": "alice"}, headers=auth_headers)
    assert search.json()["data"]["total"] == 1
    deleted = client.post(
        f"{PAT}/patients/list", json={"statuses": ["deleted"]}, headers=auth_headers
    )
    assert deleted.json()["data"]["total"] == 1  # only the deleted one


def test_patient_validate(client, auth_headers):
    _add(client, auth_headers, first="Val", last="Idate")
    taken = client.post(
        f"{PAT}/patients/validate",
        json={"firstName": "Val", "lastName": "Idate", "dateOfBirth": "1990-01-01"},
        headers=auth_headers,
    )
    assert taken.json()["message"] == "Patient Already Exists"
    free = client.post(
        f"{PAT}/patients/validate",
        json={"firstName": "New", "lastName": "Person", "dateOfBirth": "2000-01-01"},
        headers=auth_headers,
    )
    assert free.json()["message"] == "Patient available"


def test_patient_insurance_by_patient(client, auth_headers):
    rid = _add(client, auth_headers).json()["data"]["id"]
    client.post(
        f"{PAT}/patient-insurances",
        json={"patientId": rid, "insuranceCompany": "Aetna"},
        headers=auth_headers,
    )
    res = client.get(f"{PAT}/patient-insurances/by-patient/{rid}", headers=auth_headers)
    assert len(res.json()["data"]) == 1


def test_allergies_open(client):
    r = client.post(f"{PAT}/allergies", json={"name": "Penicillin"})
    assert r.status_code == 200
    aid = r.json()["data"]["id"]
    assert client.get(f"{PAT}/allergies/{aid}").json()["data"]["name"] == "Penicillin"
