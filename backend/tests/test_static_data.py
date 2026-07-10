"""Static-data endpoints — sample types with their collection devices."""


def test_sample_types_returns_linked_devices(client):
    r = client.get("/static-data/sample-types")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert isinstance(data, list) and len(data) > 0
    # each entry carries a sampleType + its allowed devices
    blood = next((d for d in data if d["sampleType"].lower() == "blood"), None)
    assert blood is not None
    assert isinstance(blood["sampleCollectionDeviceName"], list)
    assert all("title" in dev and "code" in dev for dev in blood["sampleCollectionDeviceName"])


def test_sample_type_crud(client):
    base = "/static-data/sample-types"
    # create
    r = client.post(base, json={
        "sampleType": "Whole Blood",
        "sampleCollectionDeviceName": [{"title": "Vacutainer (EDTA)", "code": "vacutainer edta"}],
    })
    assert r.status_code == 200, r.text
    row = r.json()["data"]
    assert row["id"] is not None
    tid = row["id"]
    # duplicate name -> 409
    assert client.post(base, json={"sampleType": "whole blood"}).status_code == 409
    # update devices
    up = client.put(f"{base}/{tid}", json={
        "sampleCollectionDeviceName": [{"title": "Swab", "code": "swab"}],
    })
    assert up.status_code == 200
    assert up.json()["data"]["sampleCollectionDeviceName"] == [{"title": "Swab", "code": "swab"}]
    # list now DB-backed with ids
    lst = client.get(base).json()["data"]
    assert any(d.get("id") == tid for d in lst)
    # delete
    assert client.delete(f"{base}/{tid}").status_code == 200
    assert client.delete(f"{base}/{tid}").status_code == 404
