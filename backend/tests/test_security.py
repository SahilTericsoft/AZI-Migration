"""Security & HIPAA hardening tests: response security headers, and that PHI
list/search access is written to the audit trail."""

import core.audit as audit_mod


def test_security_headers_present(client):
    r = client.get("/health")
    h = r.headers
    assert h["x-content-type-options"] == "nosniff"
    assert h["x-frame-options"] == "DENY"
    assert h["referrer-policy"] == "no-referrer"
    assert h["cache-control"] == "no-store"  # responses may carry PHI
    assert "permissions-policy" in h


def test_phi_list_is_audited(client, auth_headers, db):
    client.post(
        "/patient/patients",
        json={
            "firstName": "Aud",
            "lastName": "List",
            "dateOfBirth": "1990-01-01",
            "loginUserId": 1,
        },
        headers=auth_headers,
    )
    client.post("/patient/patients/list", json={}, headers=auth_headers)
    list_logs = (
        db.query(audit_mod.AuditLog)
        .filter(audit_mod.AuditLog.entity == "Patient", audit_mod.AuditLog.action == "list")
        .count()
    )
    assert list_logs >= 1
