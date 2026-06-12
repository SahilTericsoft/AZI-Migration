"""Tests for the Location service — REAL ported logic: facility validation,
draft status + internal id, rich list, view sub-details, toggle, physician
linking (LocationPhysician rows + array).
"""

import services.facility.models as fm
import services.location.models as lm
import services.user_service.models as um

LOC = "/location"


def _facility(db, active=True):
    f = fm.Facility(name="fac", code="fac", type="clinic", isActive=active, status="completed")
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def _add(client, facility_id, name="Front Desk", lab_id=1, login=1, **extra):
    return client.post(
        f"{LOC}/locations",
        json={
            "name": name,
            "type": "draw",
            "facilityId": facility_id,
            "labId": lab_id,
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


def test_add_location_requires_valid_active_facility(client, db):
    # no facility
    assert _add(client, 999).status_code == 400
    # inactive facility blocks (non-external flow)
    inactive = _facility(db, active=False)
    blocked = _add(client, inactive.id)
    assert blocked.status_code == 400
    assert blocked.json()["detail"] == "Facility is inactive"
    # external-lab flow allowed against inactive facility
    ok_ext = _add(client, inactive.id, isExternalLabFlow=True)
    assert ok_ext.status_code == 200


def test_add_location_defaults_and_internal_id(client, db):
    fac = _facility(db)
    r = _add(client, fac.id, name="Front Desk")
    data = r.json()["data"]
    assert data["status"] == "draft"
    assert data["code"] == "Front Desk"
    assert data["internalLocationId"] is not None
    assert data["createdBy"] == 1


def test_location_list_filters_and_population(client, db):
    fac = _facility(db)
    db.add(um.User(id=3, firstName="liam", lastName="lister"))
    db.commit()
    _add(client, fac.id, name="Alpha", login=3)
    _add(client, fac.id, name="Beta", login=3)
    res = client.post(f"{LOC}/locations/list", json={"search": "alpha", "facilityId": fac.id})
    body = res.json()["data"]
    assert body["total"] == 1
    assert body["docs"][0]["createdByDetails"]["firstName"] == "liam"
    assert body["docs"][0]["statusObj"]["code"] == "draft"


def test_location_view_sub_details(client, db):
    fac = _facility(db)
    lid = _add(client, fac.id, name="Gamma").json()["data"]["id"]
    db.add(lm.LocationUser(locationId=lid, userId=8))
    db.add(um.User(id=8, firstName="uma", lastName="user"))
    db.commit()
    res = client.post(
        f"{LOC}/locations/view", json={"locationId": lid, "isSubDetailsRequired": True}
    )
    data = res.json()["data"]
    assert data["facilityDetails"]["name"] == "fac"
    assert data["userIds"] == [8]
    assert data["userDetails"][0]["firstName"] == "uma"


def test_location_toggle(client, db):
    fac = _facility(db)
    lid = _add(client, fac.id).json()["data"]["id"]
    # new locations default active -> toggle deactivates
    res = client.put(f"{LOC}/locations/{lid}/toggle")
    assert res.json()["data"]["isActive"] is False
    assert res.json()["message"] == "Location De-Activated"


def test_location_physician_linking(client, db):
    fac = _facility(db)
    lid = _add(client, fac.id).json()["data"]["id"]
    res = client.post(f"{LOC}/locations/{lid}/physicians", json={"physicianId": 7})
    assert res.json()["data"]["physicians"] == [7]
    # a LocationPhysician row was created
    link = (
        db.query(lm.LocationPhysician)
        .filter(lm.LocationPhysician.locationId == lid, lm.LocationPhysician.physicianId == 7)
        .first()
    )
    assert link is not None and link.isActive is True
    # bulk add dedupes
    bulk = client.post(f"{LOC}/locations/{lid}/physicians/bulk", json={"physicianIds": [7, 8, 9]})
    assert bulk.json()["data"]["physicians"] == [7, 8, 9]


def test_location_edit_rederives_code_and_populates(client, db):
    fac = _facility(db)
    lid = _add(client, fac.id, name="Old").json()["data"]["id"]
    res = client.put(f"{LOC}/locations/{lid}", json={"name": "New Name"})
    data = res.json()["data"]
    assert data["code"] == "New Name"  # code re-derived from name
    assert data["facilityDetails"]["name"] == "fac"  # populated on edit


def test_location_physician_linking_dedupes(client, db):
    fac = _facility(db)
    lid = _add(client, fac.id).json()["data"]["id"]
    client.post(f"{LOC}/locations/{lid}/physicians", json={"physicianId": 5})
    # re-linking the same physician does not create a duplicate row
    again = client.post(f"{LOC}/locations/{lid}/physicians", json={"physicianId": 5})
    assert again.json()["data"]["physicians"] == [5]
    assert (
        db.query(lm.LocationPhysician).filter(lm.LocationPhysician.locationId == lid).count() == 1
    )
