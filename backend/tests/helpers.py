"""Shared test helper: exercise the standard CRUD surface of any service."""


def crud_smoke(client, base, *, create, update, headers=None):
    """create -> get -> list -> update -> delete -> confirm gone.

    Returns the created record's id. Works for every service because they all
    expose the same consolidated CRUD endpoints.
    """
    h = headers or {}

    r = client.post(base, json=create, headers=h)
    assert r.status_code == 200, r.text
    rec = r.json()["data"]
    rid = rec["id"]

    g = client.get(f"{base}/{rid}", headers=h)
    assert g.status_code == 200, g.text

    lst = client.post(f"{base}/list", json={}, headers=h)
    assert lst.status_code == 200
    assert any(d["id"] == rid for d in lst.json()["data"])

    u = client.put(f"{base}/{rid}", json=update, headers=h)
    assert u.status_code == 200, u.text
    for k, v in update.items():
        assert u.json()["data"][k] == v

    d = client.delete(f"{base}/{rid}", headers=h)
    assert d.status_code == 200, d.text

    gone = client.get(f"{base}/{rid}", headers=h)
    assert gone.status_code == 404
    return rid
