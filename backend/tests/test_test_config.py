"""Tests for the Test Configuration service — exercises the REAL ported logic:
uniqueness, code normalization, internal-id, draft-aware toggle, rich list
filters + createdBy population, list-lite, code-duplicate check.
"""

import services.user_service.models as um

TC = "/test-config"


# ------------------------------------------------------------------ panels
def test_add_panel_uppercases_code_and_sets_internal_id(client):
    r = client.post(f"{TC}/panels", json={"name": "Lipid", "code": "lip", "loginUserId": 1})
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert r.json()["message"] == "Test Panel added successfully"
    assert data["code"] == "LIP"  # normalized to upper
    assert data["status"] == "completed"  # default status
    assert data["isActive"] is True
    assert data["internalPanelId"] is not None  # generated sequence
    assert data["createdBy"] == 1


def test_add_panel_rejects_duplicate_code(client):
    client.post(f"{TC}/panels", json={"name": "Lipid", "code": "LIP"})
    dup = client.post(f"{TC}/panels", json={"name": "Lipid", "code": "lip"})
    assert dup.status_code == 409
    assert dup.json()["detail"] == "Can Not Add Test Panel With Same code"


def test_edit_panel_blocks_duplicate_code(client):
    p1 = client.post(f"{TC}/panels", json={"name": "A", "code": "AAA"}).json()["data"]["id"]
    client.post(f"{TC}/panels", json={"name": "B", "code": "BBB"})
    res = client.put(f"{TC}/panels/{p1}", json={"code": "bbb"})
    assert res.status_code == 409


def test_panel_toggle_blocks_draft_then_flips(client):
    draft = client.post(
        f"{TC}/panels", json={"name": "D", "code": "DDD", "status": "draft"}
    ).json()["data"]["id"]
    blocked = client.put(f"{TC}/panels/{draft}/toggle")
    assert blocked.status_code == 400
    assert blocked.json()["detail"] == "Can Not Activate Draft Profile"

    done = client.post(f"{TC}/panels", json={"name": "E", "code": "EEE"}).json()["data"]["id"]
    off = client.put(f"{TC}/panels/{done}/toggle")
    assert off.json()["data"]["isActive"] is False
    assert off.json()["message"] == "Profile De-Activated"


def test_panel_list_filters_search_and_populates_created_by(client, db):
    db.add(um.User(id=7, firstName="ada", lastName="admin"))
    db.commit()
    client.post(f"{TC}/panels", json={"name": "Thyroid", "code": "THY", "loginUserId": 7})
    client.post(f"{TC}/panels", json={"name": "Lipid", "code": "LIP", "loginUserId": 7})

    found = client.post(f"{TC}/panels/list", json={"search": "thyroid"})
    body = found.json()["data"]
    assert body["total"] == 1
    rec = body["docs"][0]
    assert rec["statusObj"] == {"title": "completed", "code": "completed"}
    assert rec["createdByDetails"]["firstName"] == "ada"  # populated

    page = client.post(f"{TC}/panels/list", json={"page": 1, "limit": 1})
    assert page.json()["data"]["total"] == 2 and len(page.json()["data"]["docs"]) == 1


def test_panel_status_filter(client):
    client.post(f"{TC}/panels", json={"name": "Act", "code": "ACT"})
    inactive = client.post(f"{TC}/panels", json={"name": "Ina", "code": "INA"}).json()["data"]["id"]
    client.put(f"{TC}/panels/{inactive}/toggle")  # -> inactive
    res = client.post(f"{TC}/panels/list", json={"statuses": ["inactive"]})
    docs = res.json()["data"]["docs"]
    assert all(d["isActive"] is False for d in docs) and len(docs) == 1


def test_panel_check_code_and_list_lite(client):
    client.post(f"{TC}/panels", json={"name": "Lipid", "code": "LIP"})
    exists = client.post(f"{TC}/panels/check-code", json={"code": "lip"})
    assert exists.json()["message"] == "Panel Code already exists"
    missing = client.post(f"{TC}/panels/check-code", json={"code": "ZZZ"})
    assert missing.json()["message"] == "Panel Code not exists"

    lite = client.post(f"{TC}/panels/list-lite", json={"search": "lip"})
    assert len(lite.json()["data"]) == 1


def test_panel_view(client):
    pid = client.post(f"{TC}/panels", json={"name": "Lipid", "code": "LIP"}).json()["data"]["id"]
    res = client.get(f"{TC}/panels/{pid}")
    assert res.json()["data"]["code"] == "LIP"


# ------------------------------------------------------------------- tests
def test_add_test_normalizes_and_dedupes(client):
    r = client.post(f"{TC}/tests", json={"name": "Glucose", "code": "glu", "sampleType": "Blood"})
    data = r.json()["data"]
    assert data["code"] == "GLU" and data["sampleType"] == "blood"
    assert data["status"] == "draft"
    # duplicate code
    assert (
        client.post(
            f"{TC}/tests", json={"name": "Other", "code": "GLU", "sampleType": "serum"}
        ).status_code
        == 409
    )
    # duplicate name + sampleType
    assert (
        client.post(
            f"{TC}/tests", json={"name": "glucose", "code": "G2", "sampleType": "blood"}
        ).status_code
        == 409
    )


def test_test_toggle_and_check_code(client):
    tid = client.post(
        f"{TC}/tests",
        json={"name": "T", "code": "TTT", "sampleType": "blood", "status": "completed"},
    ).json()["data"]["id"]
    assert client.put(f"{TC}/tests/{tid}/toggle").json()["data"]["isActive"] is False
    assert (
        client.post(f"{TC}/tests/check-code", json={"code": "ttt"}).json()["message"]
        == "Test Code already exists"
    )


# -------------------------------------------------------------- biomarkers
def test_add_biomarker_dedupes_code(client):
    r = client.post(f"{TC}/biomarkers", json={"name": "HDL", "code": "hdl", "sampleType": "Blood"})
    assert r.json()["data"]["code"] == "HDL"
    assert r.json()["data"]["sampleType"] == "blood"
    assert client.post(f"{TC}/biomarkers", json={"name": "HDL2", "code": "HDL"}).status_code == 409


# --------------------------------------------------------- cpt / icd codes
def test_cpt_code_crud_and_dedupe(client):
    r = client.post(f"{TC}/cpt-codes", json={"cptCode": "80061", "description": "Lipid"})
    assert r.status_code == 200
    assert client.post(f"{TC}/cpt-codes", json={"cptCode": "80061"}).status_code == 409
    lst = client.post(f"{TC}/cpt-codes/list", json={"search": "8006"})
    assert lst.json()["data"]["total"] == 1


def test_icd_code_crud_and_dedupe(client):
    r = client.post(f"{TC}/icd-codes", json={"icdCode": "E78.5", "description": "Hyperlipidemia"})
    assert r.status_code == 200
    assert client.post(f"{TC}/icd-codes", json={"icdCode": "E78.5"}).status_code == 409
    cid = r.json()["data"]["id"]
    assert client.get(f"{TC}/icd-codes/{cid}").json()["data"]["icdCode"] == "E78.5"
