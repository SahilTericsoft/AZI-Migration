"""Tests for the Facility service — the REAL ported logic: name uniqueness,
draft defaults, rich list filters + createdBy population, view sub-details +
location count, toggle cascade to locations, physician/admin management.
"""

import services.location.models as lm
import services.user_service.models as um

FAC = "/facility"


def _add(client, name="North Clinic", type_="clinic", login=1, **extra):
    return client.post(
        f"{FAC}/facilities",
        json={
            "name": name,
            "type": type_,
            "loginUserId": login,
            "addressDetails": {
                "addressLine1": "1 st",
                "zipcode": "75001",
                "state": "TX",
                "city": "Dallas",
            },
            **extra,
        },
    )


def test_add_facility_defaults_and_uniqueness(client):
    r = _add(client, name="North Clinic")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["name"] == "north clinic"  # stored lowercase
    assert data["code"] == "North Clinic"  # original as code
    assert data["status"] == "draft" and data["isActive"] is False
    assert data["createdBy"] == 1
    # duplicate name (case-insensitive) rejected
    dup = _add(client, name="north CLINIC")
    assert dup.status_code == 400
    assert "already exists" in dup.json()["detail"]


def test_facility_list_filters_and_population(client, db):
    db.add(um.User(id=4, firstName="cara", lastName="creator"))
    db.commit()
    _add(client, name="Alpha", login=4)
    _add(client, name="Beta", login=4)

    res = client.post(f"{FAC}/facilities/list", json={"search": "alpha"})
    body = res.json()["data"]
    assert body["total"] == 1
    rec = body["docs"][0]
    assert rec["statusObj"] == {"title": "draft", "code": "draft"}
    assert rec["createdByDetails"]["firstName"] == "cara"

    by_city = client.post(f"{FAC}/facilities/list", json={"cities": ["Dallas"]})
    assert by_city.json()["data"]["total"] == 2
    none_city = client.post(f"{FAC}/facilities/list", json={"cities": ["Austin"]})
    assert none_city.json()["data"]["total"] == 0


def test_facility_view_sub_details_and_location_count(client, db):
    fid = _add(client, name="Gamma").json()["data"]["id"]
    db.add(um.User(id=9, firstName="adam", lastName="admin"))
    db.add_all(
        [
            __import__("services.facility.models", fromlist=["FacilityUser"]).FacilityUser(
                facilityId=fid, userId=9
            ),
            lm.Location(facilityId=fid, name="L1"),
            lm.Location(facilityId=fid, name="L2"),
        ]
    )
    db.commit()

    res = client.post(
        f"{FAC}/facilities/view",
        json={"facilityId": fid, "isSubDetailsRequired": True, "isNumberOfLocationsRequired": True},
    )
    data = res.json()["data"]
    assert data["userIds"] == [9]
    assert data["userDetails"][0]["firstName"] == "adam"
    assert data["numberOfLocations"] == 2


def test_facility_toggle_cascades_to_completed_locations(client, db):
    fid = _add(client, name="Delta").json()["data"]["id"]
    completed = lm.Location(facilityId=fid, name="C", status="completed", isActive=True)
    draft = lm.Location(facilityId=fid, name="D", status="draft", isActive=True)
    db.add_all([completed, draft])
    db.commit()
    completed_id, draft_id = completed.id, draft.id

    res = client.put(f"{FAC}/facilities/{fid}/toggle")
    assert res.json()["data"]["isActive"] is True  # facility was draft/inactive -> active
    assert res.json()["message"] == "Facility Activated"

    # toggle again -> inactive, cascades to completed location only
    res2 = client.put(f"{FAC}/facilities/{fid}/toggle")
    assert res2.json()["data"]["isActive"] is False
    db.expire_all()
    assert db.get(lm.Location, completed_id).isActive is False  # cascaded
    assert db.get(lm.Location, draft_id).isActive is True  # untouched (draft)


def test_facility_physician_management(client):
    fid = _add(client, name="Epsilon").json()["data"]["id"]
    add = client.post(f"{FAC}/facilities/{fid}/physicians", json={"physicians": [10, 11]})
    assert add.json()["data"]["physicians"] == [10, 11]
    # idempotent append
    again = client.post(f"{FAC}/facilities/{fid}/physicians", json={"physicians": [11, 12]})
    assert again.json()["data"]["physicians"] == [10, 11, 12]
    # unlink
    rm = client.delete(f"{FAC}/facilities/{fid}/physicians/11")
    assert rm.status_code == 200
    view = client.post(f"{FAC}/facilities/view", json={"facilityId": fid})
    assert view.json()["data"]["physicians"] == [10, 12]


def test_facility_set_admin_creates_link(client, db):
    fid = _add(client, name="Zeta").json()["data"]["id"]
    res = client.put(f"{FAC}/facilities/{fid}/admin", json={"adminId": 55})
    assert res.json()["data"]["adminId"] == 55
    from services.facility.models import FacilityUser

    link = (
        db.query(FacilityUser)
        .filter(FacilityUser.facilityId == fid, FacilityUser.userId == 55)
        .first()
    )
    assert link is not None


def test_facility_edit_name_uniqueness(client):
    _add(client, name="Same", type_="clinic")
    other = _add(client, name="Other", type_="clinic").json()["data"]["id"]
    res = client.put(f"{FAC}/facilities/{other}", json={"name": "Same", "type": "clinic"})
    assert res.status_code == 409
