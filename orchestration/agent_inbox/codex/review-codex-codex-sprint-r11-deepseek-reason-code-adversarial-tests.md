warning: in the working copy of 'tests/test_reason_code_adversarial.py', CRLF will be replaced by LF the next time Git touches it
diff --git a/tests/test_reason_code_adversarial.py b/tests/test_reason_code_adversarial.py
new file mode 100644
index 0000000..71cbc6d
--- /dev/null
+++ b/tests/test_reason_code_adversarial.py
@@ -0,0 +1,716 @@
+﻿"""
+Sprint R11 — Reason-code adversarial tests.
+
+Adversarial tests for the R10 uppercase reason-code taxonomy across all
+mutation surfaces: delete, status, proposal, confirm, and audit.
+
+Dimensions covered:
+- Valid uppercase codes survive round-trips on delete routes
+- Invalid/unknown codes are rejected with 422
+- Null codes accepted for legacy compatibility
+- Audit entries preserve the supplied code
+- Overlong codes are rejected
+- Edge cases: empty string, whitespace-only, injection-like values
+- Status routes accept and persist reason codes (will fail before R11 backend)
+- Cross-practice isolation
+
+These tests define the contract the R11 backend should satisfy.
+No strict xfails; failures on this branch before backend integration are expected.
+"""
+
+from datetime import date, datetime, time, timedelta, timezone
+
+import pytest
+
+from app.models.appointments import (
+    Appointment,
+    AppointmentAuditLog,
+    AppointmentAuditAction,
+    AppointmentStatus,
+    BookingChannel,
+)
+from tests.conftest import make_token
+
+TODAY = date.today() + timedelta(days=14)
+
+APPT_URL = "/api/v1/appointments"
+DELETE_CONFIRM_URL = f"{APPT_URL}/proposals/delete-confirm"
+STATUS_CONFIRM_URL = f"{APPT_URL}/proposals/status-confirm"
+
+# R10 uppercase reason-code taxonomy
+# From docs/receptionist_review_r10_reason_code_inventory.md
+REASON_CODES = [
+    "PATIENT_CANCELLED",
+    "PATIENT_RESCHEDULED",
+    "PATIENT_UNWELL",
+    "PATIENT_TRANSPORT",
+    "PRACTITIONER_UNAVAILABLE",
+    "CLINIC_OPERATIONAL",
+    "CLINIC_RESCHEDULED",
+    "ADMIN_ERROR",
+    "DUPLICATE_BOOKING",
+    "DID_NOT_ATTEND",
+    "LEFT_WITHOUT_SEEN",
+    "OTHER",
+    "LEGACY_UNCLASSIFIED",
+]
+
+VALID_TERMINAL_STATUSES = ["Cancelled", "NoShow", "DNA"]
+
+# Strings that should be rejected as invalid reason codes
+INVALID_CODE_STRINGS = [
+    "patient_cancelled",        # wrong case
+    "CANCELLED_BY_PATIENT",     # non-standard label
+    "NO_SHOW",                  # wrong format (not DID_NOT_ATTEND)
+    "RESCHEDULED",              # missing prefix
+    "MISSED_APPOINTMENT",       # non-standard
+    "COVID_SYMPTOMS",           # clinical detail - prohibited
+    "SICK",                     # too vague / clinical
+    "",                         # empty string (not None)
+]
+
+
+def _make_appt(
+    db,
+    practice,
+    practitioner,
+    patient,
+    status=AppointmentStatus.Booked,
+    start_h=9,
+):
+    a = Appointment(
+        practice_id=practice.id,
+        patient_id=patient.id,
+        practitioner_id=practitioner.id,
+        start_time=datetime.combine(
+            TODAY, time(start_h, 0), tzinfo=timezone.utc
+        ),
+        appointment_date=TODAY,
+        start_time_local=time(start_h, 0),
+        duration_minutes=15,
+        status=status,
+        booked_via=BookingChannel.Receptionist,
+    )
+    db.add(a)
+    db.flush()
+    return a
+
+
+def _auth(token):
+    return {"Authorization": f"Bearer {token}"}
+
+
+# ---------------------------------------------------------------------------
+# Valid code acceptance -- DELETE route (current surface)
+# ---------------------------------------------------------------------------
+
+
+@pytest.mark.parametrize("code", REASON_CODES)
+def test_delete_accepts_valid_reason_code(
+    code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Every valid uppercase reason code is accepted on DELETE."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 204
+
+    # Round-trip verification
+    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
+    assert resp.status_code == 200
+    assert resp.json()["status"] == "Cancelled"
+    assert resp.json()["cancellation_reason"] == code
+
+
+@pytest.mark.parametrize("code", REASON_CODES)
+def test_delete_proposal_accepts_valid_reason_code(
+    code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Every valid reason code is accepted on delete-proposal."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.post(
+        f"{APPT_URL}/proposals/delete/{appt.id}",
+        json={"cancellation_reason": code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+    data = resp.json()
+    assert data["intent"] == "delete_appointment"
+    assert data["autonomy_tier"] in ("proposal",)
+
+
+@pytest.mark.parametrize("code", REASON_CODES)
+def test_delete_confirm_persists_reason_code(
+    code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Every valid reason code survives delete-confirm round-trip."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    # Propose
+    resp = client.post(
+        f"{APPT_URL}/proposals/delete/{appt.id}",
+        json={"cancellation_reason": code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+    payload = resp.json()["confirm_payload"]
+    payload["confirmed"] = True
+
+    # Confirm
+    resp = client.post(DELETE_CONFIRM_URL, json=payload, headers=_auth(token))
+    assert resp.status_code == 200
+
+    # Round-trip
+    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
+    assert resp.status_code == 200
+    assert resp.json()["status"] == "Cancelled"
+    assert resp.json()["cancellation_reason"] == code
+
+
+# ---------------------------------------------------------------------------
+# Null / legacy compatibility
+# ---------------------------------------------------------------------------
+
+
+def test_delete_with_null_reason_code_legacy_compatible(
+    client, db, practice, practitioner, patient, receptionist_user
+):
+    """Null cancellation_reason is accepted (legacy compatibility)."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 204
+
+    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
+    assert resp.status_code == 200
+    assert resp.json()["cancellation_reason"] is None
+
+
+def test_delete_proposal_with_null_reason_code_legacy_compatible(
+    client, db, practice, practitioner, patient, receptionist_user
+):
+    """Null cancellation_reason is accepted on delete-proposal."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.post(
+        f"{APPT_URL}/proposals/delete/{appt.id}",
+        json={},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+
+    payload = resp.json()["confirm_payload"]
+    payload["confirmed"] = True
+
+    resp = client.post(DELETE_CONFIRM_URL, json=payload, headers=_auth(token))
+    assert resp.status_code == 200
+
+    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
+    assert resp.status_code == 200
+    assert resp.json()["cancellation_reason"] is None
+
+
+def test_delete_confirm_with_explicit_null_persists(
+    client, db, practice, practitioner, patient, receptionist_user
+):
+    """Explicit null cancellation_reason persists as null."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.post(
+        f"{APPT_URL}/proposals/delete/{appt.id}",
+        json={"cancellation_reason": None},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+
+    payload = resp.json()["confirm_payload"]
+    payload["confirmed"] = True
+
+    resp = client.post(DELETE_CONFIRM_URL, json=payload, headers=_auth(token))
+    assert resp.status_code == 200
+
+    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
+    assert resp.status_code == 200
+    assert resp.json()["cancellation_reason"] is None
+
+
+# ---------------------------------------------------------------------------
+# Invalid code rejection (will fail before R11 backend adds validation)
+# ---------------------------------------------------------------------------
+
+
+@pytest.mark.parametrize("bad_code", INVALID_CODE_STRINGS)
+def test_delete_rejects_invalid_reason_code(
+    bad_code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """
+    Invalid reason-code strings are rejected with 422.
+    Will fail before R11 backend adds validation; passes after.
+    """
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": bad_code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 422
+
+
+@pytest.mark.parametrize("bad_code", INVALID_CODE_STRINGS)
+def test_delete_proposal_rejects_invalid_reason_code(
+    bad_code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Invalid codes are rejected on delete-proposal."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.post(
+        f"{APPT_URL}/proposals/delete/{appt.id}",
+        json={"cancellation_reason": bad_code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 422
+
+
+@pytest.mark.parametrize("bad_code", INVALID_CODE_STRINGS)
+def test_delete_confirm_rejects_invalid_reason_code(
+    bad_code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Invalid codes are rejected at delete-confirm time."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    # Propose with a valid code to get past the first gate
+    resp = client.post(
+        f"{APPT_URL}/proposals/delete/{appt.id}",
+        json={"cancellation_reason": "PATIENT_CANCELLED"},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+    payload = resp.json()["confirm_payload"]
+
+    # Mutate the reason code in the signed payload before confirm
+    payload["cancellation_reason"] = bad_code
+    payload["confirmed"] = True
+
+    resp = client.post(DELETE_CONFIRM_URL, json=payload, headers=_auth(token))
+    assert resp.status_code == 422
+
+
+# ---------------------------------------------------------------------------
+# Overlong code rejection
+# ---------------------------------------------------------------------------
+
+
+def test_delete_rejects_overlong_reason_code(
+    client, db, practice, practitioner, patient, receptionist_user
+):
+    """Overlong cancellation_reason (>500 chars) is rejected."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": "X" * 501},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 422
+
+
+def test_delete_proposal_rejects_overlong_reason_code(
+    client, db, practice, practitioner, patient, receptionist_user
+):
+    """Overlong code is rejected on delete-proposal."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.post(
+        f"{APPT_URL}/proposals/delete/{appt.id}",
+        json={"cancellation_reason": "X" * 501},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 422
+
+
+# ---------------------------------------------------------------------------
+# Audit persistence
+# ---------------------------------------------------------------------------
+
+
+@pytest.mark.parametrize("code", REASON_CODES)
+def test_delete_persists_reason_code_in_audit(
+    code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Every valid reason code persists in the audit log."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": code},
+        headers=_auth(token),
+    )
+
+    entries = (
+        db.query(AppointmentAuditLog)
+        .filter(AppointmentAuditLog.appointment_id == appt.id)
+        .all()
+    )
+    assert len(entries) == 1
+    assert entries[0].action == AppointmentAuditAction.delete
+    assert entries[0].status_before == AppointmentStatus.Booked
+    assert entries[0].status_after == AppointmentStatus.Cancelled
+    assert entries[0].cancellation_reason == code
+
+
+@pytest.mark.parametrize("code", REASON_CODES)
+def test_delete_confirm_persists_reason_code_in_audit(
+    code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Every valid reason code persists in audit via delete-confirm."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.post(
+        f"{APPT_URL}/proposals/delete/{appt.id}",
+        json={"cancellation_reason": code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+    payload = resp.json()["confirm_payload"]
+    payload["confirmed"] = True
+
+    client.post(DELETE_CONFIRM_URL, json=payload, headers=_auth(token))
+
+    entries = (
+        db.query(AppointmentAuditLog)
+        .filter(AppointmentAuditLog.appointment_id == appt.id)
+        .all()
+    )
+    assert len(entries) == 1
+    assert entries[0].action == AppointmentAuditAction.delete
+    assert entries[0].cancellation_reason == code
+
+
+@pytest.mark.parametrize("code", REASON_CODES)
+def test_reason_code_in_audit_get_response(
+    code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Reason code appears in the GET /{id}/audit response body."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": code},
+        headers=_auth(token),
+    )
+
+    resp = client.get(f"{APPT_URL}/{appt.id}/audit", headers=_auth(token))
+    assert resp.status_code == 200
+    entries = resp.json()
+    assert len(entries) == 1
+    assert entries[0]["action"] == "delete"
+    assert entries[0]["cancellation_reason"] == code
+
+
+@pytest.mark.parametrize("code", REASON_CODES)
+def test_reason_code_in_cancelled_list_response(
+    code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """Reason code appears in the GET /appointments?status=Cancelled list."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": code},
+        headers=_auth(token),
+    )
+
+    resp = client.get(
+        APPT_URL,
+        params={"status": "Cancelled"},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+    rows = {row["id"]: row for row in resp.json()}
+    assert str(appt.id) in rows
+    assert rows[str(appt.id)]["cancellation_reason"] == code
+
+
+# ---------------------------------------------------------------------------
+# Status-route reason capture (will fail before R11 backend)
+# ---------------------------------------------------------------------------
+
+
+@pytest.mark.parametrize("status", VALID_TERMINAL_STATUSES)
+@pytest.mark.parametrize("code", ["PATIENT_CANCELLED", "DID_NOT_ATTEND", "LEFT_WITHOUT_SEEN", "OTHER"])
+def test_patch_status_accepts_reason_code(
+    status, code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """
+    PATCH /{id}/status should accept a status_reason_code.
+    Will fail before R11 backend adds the field; expected.
+    """
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.patch(
+        f"{APPT_URL}/{appt.id}/status",
+        json={"status": status, "status_reason_code": code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+    assert resp.json()["status_reason_code"] == code
+
+
+@pytest.mark.parametrize("status", VALID_TERMINAL_STATUSES)
+def test_patch_status_with_null_reason_code_legacy_compatible(
+    status, client, db, practice, practitioner, patient, receptionist_user
+):
+    """
+    Null status_reason_code is accepted on PATCH (legacy compatibility).
+    Will fail before R11 backend; expected.
+    """
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.patch(
+        f"{APPT_URL}/{appt.id}/status",
+        json={"status": status},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+    assert resp.json()["status_reason_code"] is None
+
+
+@pytest.mark.parametrize("status", VALID_TERMINAL_STATUSES)
+@pytest.mark.parametrize("code", ["PATIENT_CANCELLED", "DID_NOT_ATTEND"])
+def test_status_proposal_accepts_reason_code(
+    status, code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """
+    Status proposal should accept a status_reason_code.
+    Will fail before R11 backend; expected.
+    """
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.post(
+        f"{APPT_URL}/proposals/status/{appt.id}",
+        json={"status": status, "status_reason_code": code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+
+
+@pytest.mark.parametrize("code", ["PATIENT_CANCELLED", "DID_NOT_ATTEND"])
+def test_status_confirm_persists_reason_code(
+    code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """
+    Status-confirm should persist the reason code.
+    Will fail before R11 backend; expected.
+    """
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.post(
+        f"{APPT_URL}/proposals/status/{appt.id}",
+        json={"status": "Cancelled", "status_reason_code": code},
+        headers=_auth(token),
+    )
+    assert resp.status_code == 200
+    payload = resp.json()["confirm_payload"]
+    payload["confirmed"] = True
+
+    resp = client.post(STATUS_CONFIRM_URL, json=payload, headers=_auth(token))
+    assert resp.status_code == 200
+
+    resp = client.get(f"{APPT_URL}/{appt.id}", headers=_auth(token))
+    assert resp.status_code == 200
+    assert resp.json()["status_reason_code"] == code
+
+
+@pytest.mark.parametrize("status", VALID_TERMINAL_STATUSES)
+@pytest.mark.parametrize("code", ["PATIENT_CANCELLED", "DID_NOT_ATTEND"])
+def test_status_route_audit_persists_reason_code(
+    status, code, client, db, practice, practitioner, patient, receptionist_user
+):
+    """
+    Status route's reason code persists in the audit log.
+    Will fail before R11 backend; expected.
+    """
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    client.patch(
+        f"{APPT_URL}/{appt.id}/status",
+        json={"status": status, "status_reason_code": code},
+        headers=_auth(token),
+    )
+
+    entries = (
+        db.query(AppointmentAuditLog)
+        .filter(AppointmentAuditLog.appointment_id == appt.id)
+        .all()
+    )
+    assert len(entries) >= 1
+    audit_entry = entries[-1]
+    assert audit_entry.action == AppointmentAuditAction.status_change
+    assert audit_entry.status_after.value == status
+    assert audit_entry.cancellation_reason == code
+
+
+# ---------------------------------------------------------------------------
+# Injection / special character edge cases (current surface)
+# ---------------------------------------------------------------------------
+
+
+INJECTION_PATTERNS = [
+    "PATIENT_CANCELLED; DROP TABLE appointments;",
+    "<script>alert('xss')</script>",
+    "PATIENT_UNWELL\nPRACTITIONER_UNAVAILABLE",
+    '{"code": "PATIENT_CANCELLED"}',
+    "NULL",
+    "None",
+    "  PATIENT_CANCELLED  ",
+]
+
+
+@pytest.mark.parametrize("payload", INJECTION_PATTERNS)
+def test_delete_handles_edge_case_reason_strings(
+    payload, client, db, practice, practitioner, patient, receptionist_user
+):
+    """
+    Edge-case reason strings should be accepted or rejected safely.
+    Current behaviour accepts any string as free text.
+    After R11 validation, structured/injection patterns should be rejected.
+    """
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": payload},
+        headers=_auth(token),
+    )
+    # Must not crash; either 204 (accepted as string) or 422 (rejected)
+    assert resp.status_code in (204, 422)
+
+
+def test_reason_code_unicode_handling(
+    client, db, practice, practitioner, patient, receptionist_user
+):
+    """Unicode characters in reason code are handled without error."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token = make_token(receptionist_user)
+
+    resp = client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": "PATIENT_CANCELLE\\u00c9D"},
+        headers=_auth(token),
+    )
+    # Unicode is not in the allow-list, so should be rejected when validation
+    # is in place; currently may be accepted as free text
+    assert resp.status_code in (204, 422)
+
+
+# ---------------------------------------------------------------------------
+# Cross-practice isolation (current surface)
+# ---------------------------------------------------------------------------
+
+
+def test_cross_practice_cannot_read_other_practice_reason_code(
+    client, db, practice, practitioner, patient,
+    gp_user, gp_user_b, practice_b, patient_b,
+):
+    """A cancelled appointment from practice B is not visible to practice A."""
+    from app.models.tenancy import Practitioner as PractitionerModel
+
+    prac_b = PractitionerModel(
+        practice_id=practice_b.id,
+        first_name="Other",
+        last_name="Doctor",
+        ahpra_number="MED0007779999",
+    )
+    db.add(prac_b)
+    db.flush()
+
+    appt_b = Appointment(
+        practice_id=practice_b.id,
+        patient_id=patient_b.id,
+        practitioner_id=prac_b.id,
+        start_time=datetime.combine(
+            TODAY, time(9, 0), tzinfo=timezone.utc
+        ),
+        appointment_date=TODAY,
+        start_time_local=time(9, 0),
+        duration_minutes=15,
+        status=AppointmentStatus.Cancelled,
+        cancellation_reason="PATIENT_CANCELLED",
+        booked_via=BookingChannel.Receptionist,
+    )
+    db.add(appt_b)
+    db.flush()
+
+    # Practice A user should not see practice B's cancelled appointment
+    token_a = make_token(gp_user)
+    resp = client.get(
+        APPT_URL,
+        params={"status": "Cancelled"},
+        headers=_auth(token_a),
+    )
+    assert resp.status_code == 200
+    ids = [row["id"] for row in resp.json()]
+    assert str(appt_b.id) not in ids
+
+
+def test_cross_practice_cannot_audit_other_practice_reason_code(
+    client, db, practice, practitioner, patient,
+    gp_user, gp_user_b, practice_b, patient_b,
+    receptionist_user,
+):
+    """Practice B user cannot GET /audit for practice A appointment."""
+    appt = _make_appt(db, practice, practitioner, patient)
+    token_rec = make_token(receptionist_user)
+
+    client.request(
+        "DELETE",
+        f"{APPT_URL}/{appt.id}",
+        json={"cancellation_reason": "PATIENT_CANCELLED"},
+        headers=_auth(token_rec),
+    )
+
+    token_b = make_token(gp_user_b)
+    resp = client.get(
+        f"{APPT_URL}/{appt.id}/audit", headers=_auth(token_b)
+    )
+    assert resp.status_code == 404
