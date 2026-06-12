"""Tests for the Lab service — REAL ported logic: labRole validation, code
lowercasing, draft/isSdiLab defaults, rich list + population, view, toggle,
lab-user linking, lookup by admin.
"""

import services.user_service.models as um

LAB = "/lab"


def _add(client, name="Central Lab", role="sendReceiveLab", lab_type="inHouseLab", **extra):
    return client.post(
        f"{LAB}/labs",
        json={
            "name": name,
            "cliaId": "12D3456789",
            "emailId": "lab@x.com",
            "mobileNumber": "5551234",
            "addressLine1": "1 st",
            "zipcode": "75001",
            "state": "TX",
            "city": "Dallas",
            "labRole": role,
            "labType": lab_type,
            "loginUserId": 1,
            **extra,
        },
    )


def test_add_lab_defaults(client):
    r = _add(client, name="Central Lab")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["code"] == "central lab"  # lowercased name
    assert data["status"] == "draft" and data["isActive"] is False
    assert data["isSdiLab"] is True  # not externalLab
    assert data["createdBy"] == 1


def test_external_lab_is_not_sdi(client):
    data = _add(client, name="Ext", lab_type="externalLab").json()["data"]
    assert data["isSdiLab"] is False


def test_add_lab_rejects_bad_role(client):
    r = _add(client, role="bogus")
    assert r.status_code == 400
    assert "labRole" in r.json()["detail"]


def test_lab_list_filters_and_population(client, db):
    db.add(um.User(id=1, firstName="leo", lastName="lab"))  # matches loginUserId=1
    db.commit()
    _add(client, name="Alpha Lab", lab_type="inHouseLab")
    _add(client, name="Beta Lab", lab_type="externalLab")

    res = client.post(f"{LAB}/labs/list", json={"search": "alpha"})
    body = res.json()["data"]
    assert body["total"] == 1
    assert body["docs"][0]["statusObj"]["code"] == "draft"
    assert body["docs"][0]["createdByDetails"]["firstName"] == "leo"

    by_type = client.post(f"{LAB}/labs/list", json={"labTypes": ["externalLab"]})
    assert by_type.json()["data"]["total"] == 1


def test_lab_edit_rederives_code(client):
    lid = _add(client, name="Old Lab").json()["data"]["id"]
    res = client.put(f"{LAB}/labs/{lid}", json={"name": "New Lab"})
    assert res.json()["data"]["code"] == "new lab"


def test_lab_toggle(client):
    lid = _add(client).json()["data"]["id"]  # draft/inactive
    res = client.put(f"{LAB}/labs/{lid}/toggle")
    assert res.json()["data"]["isActive"] is True
    assert res.json()["message"] == "Lab Activated"


def test_lab_view_and_by_admin(client, db):
    lid = _add(client).json()["data"]["id"]
    db.query(__import__("services.lab.models", fromlist=["Lab"]).Lab).filter_by(id=lid).update(
        {"adminId": 42}
    )
    db.commit()
    by_admin = client.get(f"{LAB}/labs/by-admin/42")
    assert by_admin.json()["data"]["id"] == lid
    view = client.post(f"{LAB}/labs/view", json={"labId": lid})
    assert view.json()["data"]["id"] == lid


def test_lab_user_linking_dedupes(client):
    lid = _add(client).json()["data"]["id"]
    first = client.post(f"{LAB}/lab-users", json={"labId": lid, "userId": 5, "locationIds": [1]})
    assert first.status_code == 200
    again = client.post(f"{LAB}/lab-users", json={"labId": lid, "userId": 5})
    assert again.json()["message"] == "Lab user already linked"
    by_lab = client.get(f"{LAB}/lab-users/by-lab/{lid}")
    assert len(by_lab.json()["data"]) == 1
