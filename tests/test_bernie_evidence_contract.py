"""
Bernie API evidence contract tests.

Proves that supervised-booking returns structured practitioner and patient
evidence in the staff-review payload (additive, non-mutating), that the
confirm-bernie endpoint records the identity-confidence tier as a bounded
audit-evidence code on the AppointmentAuditLog row, and that provisional /
unlinked / ambiguous patient paths emit appropriate evidence without PHI leaks.
"""

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
)
from app.models.patients import Patient
from tests.conftest import make_token

WRAPPER_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
NORMALIZED_SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
SELECTION_URL = "/api/v1/appointments/proposals/slot-search/selection"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
REFERENCE_DATE = "2026-06-22"


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _post_wrapper(client, token, body: dict):
    return client.post(
        WRAPPER_URL,
        json=body,
        headers=_auth(token),
    )


def _base_body(practitioner, **overrides):
    body = {
        "reference_date": REFERENCE_DATE,
        "command": {
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
        },
    }
    body.update(overrides)
    return body


def _row_counts(db):
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    )


def _search_and_select(client, token, practitioner, patient, reason="Bernie evidence test"):
    search_resp = client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": REFERENCE_DATE},
        json={
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
            "patient_id": str(patient.id),
        },
        headers=_auth(token),
    )
    assert search_resp.status_code == 200, search_resp.text
    search = search_resp.json()
    assert search["safe"] is True

    selection_resp = client.post(
        SELECTION_URL,
        json={
            "search_execution": search,
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": reason,
        },
        headers=_auth(token),
    )
    assert selection_resp.status_code == 200, selection_resp.text
    selection = selection_resp.json()
    assert selection["safe"] is True
    assert selection["create_proposal"]["safe"] is True
    return selection


# ── Practitioner evidence ─────────────────────────────────────────────────────

def test_confirmation_ready_includes_practitioner_evidence(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    before = _row_counts(db)

    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        selected_candidate_index=0,
        patient_id=str(patient.id),
        reason="Follow-up",
    ))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "confirmation_ready"
    assert _row_counts(db) == before

    prac_ev = data["staff_review"]["practitioner_evidence"]
    assert prac_ev is not None
    assert prac_ev["practitioner_id"] == str(practitioner.id)
    assert prac_ev["display_name"] == "Alex Shera"


def test_candidate_selection_required_has_no_practitioner_evidence(
    client, db, gp_user, practitioner, schedule
):
    token = make_token(gp_user)
    resp = _post_wrapper(client, token, _base_body(practitioner))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "candidate_selection_required"
    assert data["staff_review"]["practitioner_evidence"] is None


def test_practitioner_evidence_includes_provider_number_when_set(
    client, db, gp_user, practitioner, patient, schedule
):
    practitioner.provider_number = "2345678A"
    db.flush()
    token = make_token(gp_user)

    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        selected_candidate_index=0,
        patient_id=str(patient.id),
    ))

    assert resp.status_code == 200, resp.text
    prac_ev = resp.json()["staff_review"]["practitioner_evidence"]
    assert prac_ev is not None
    assert prac_ev["provider_number"] == "2345678A"


# ── Patient evidence ──────────────────────────────────────────────────────────

def test_linked_patient_evidence_contains_dob_and_masked_phone(
    client, db, gp_user, practitioner, patient, schedule
):
    patient.phone_mobile = "0412 345 678"
    db.flush()
    token = make_token(gp_user)

    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        selected_candidate_index=0,
        patient_id=str(patient.id),
    ))

    assert resp.status_code == 200, resp.text
    pat_ev = resp.json()["staff_review"]["patient_evidence"]
    assert pat_ev is not None
    assert pat_ev["patient_id"] == str(patient.id)
    assert pat_ev["patient_label"] == "Margaret Thompson"
    assert pat_ev["date_of_birth"] == "1955-03-20"
    assert pat_ev["is_provisional"] is False
    assert pat_ev["confidence"] == "medium"
    masked = pat_ev["masked_phone"]
    assert masked is not None
    assert "5678" in masked
    assert "0412 345" not in masked


def test_provisional_patient_evidence_is_provisional_with_no_dob(
    client, db, gp_user, practitioner, schedule
):
    token = make_token(gp_user)

    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        selected_candidate_index=0,
        patient_name_provisional="Jane Doe",
    ))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    pat_ev = data["staff_review"]["patient_evidence"]
    assert pat_ev is not None
    assert pat_ev["is_provisional"] is True
    assert pat_ev["date_of_birth"] is None
    assert pat_ev["masked_phone"] is None


def test_ambiguous_patient_evidence_confidence_echoes_identity_evidence(
    client, db, gp_user, practice, practitioner, patient, schedule
):
    duplicate = Patient(
        practice_id=practice.id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        date_of_birth=patient.date_of_birth,
    )
    db.add(duplicate)
    db.flush()
    token = make_token(gp_user)

    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        patient_id=str(patient.id),
        selected_candidate_index=0,
    ))

    assert resp.status_code == 200, resp.text
    review = resp.json()["staff_review"]
    assert review["identity_evidence"]["confidence"] == "ambiguous"
    assert review["patient_evidence"]["confidence"] == "ambiguous"


# ── No-mutation assertions ────────────────────────────────────────────────────

def test_evidence_fields_do_not_trigger_writes(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    before = _row_counts(db)

    for _ in range(3):
        _post_wrapper(client, token, _base_body(
            practitioner,
            selected_candidate_index=0,
            patient_id=str(patient.id),
        ))

    assert _row_counts(db) == before


# ── Confirm-bernie identity-confidence audit code ─────────────────────────────

def test_confirmed_write_records_identity_confidence_code_in_audit(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)
    before_appt, before_audit = _row_counts(db)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "selection_proposal": selection},
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"

    assert "bernie_identity_confidence_medium" in data["audit_evidence"]
    assert "bernie_confirm_create_proposal" in data["audit_evidence"]

    assert db.query(Appointment).count() == before_appt + 1
    assert db.query(AppointmentAuditLog).count() == before_audit + 1

    audit = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == data["appointment"]["id"]
    ).one()
    assert "bernie_identity_confidence_medium" in (audit.confirmed_warnings or [])


def test_patient_with_medicare_records_medium_or_better_confidence_code(
    client, db, gp_user, practitioner, patient, schedule
):
    """Patient with medicare on record confirms at medium or higher confidence."""
    patient.medicare_number = "2958303372"
    db.flush()
    token = make_token(gp_user)
    selection = _search_and_select(
        client, token, practitioner, patient,
        reason="Patient with medicare",
    )
    before_appt, before_audit = _row_counts(db)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "selection_proposal": selection},
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert db.query(Appointment).count() == before_appt + 1
    assert db.query(AppointmentAuditLog).count() == before_audit + 1

    confidence_codes = [
        c for c in data["audit_evidence"]
        if c.startswith("bernie_identity_confidence_")
    ]
    assert len(confidence_codes) == 1
    assert confidence_codes[0] in (
        "bernie_identity_confidence_medium",
        "bernie_identity_confidence_high",
    )


def test_blocked_confirm_writes_no_rows(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)
    before = _row_counts(db)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": False, "selection_proposal": selection},
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert _row_counts(db) == before


def test_unlinked_patient_confirm_writes_no_confidence_code(
    client, db, gp_user, practitioner, patient, schedule
):
    """confirm-bernie with a provisional (no patient_id) create command skips confidence code."""
    token = make_token(gp_user)

    search_resp = client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": REFERENCE_DATE},
        json={
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
        },
        headers=_auth(token),
    )
    assert search_resp.status_code == 200
    search = search_resp.json()
    assert search["safe"] is True

    selection_resp = client.post(
        SELECTION_URL,
        json={
            "search_execution": search,
            "selected_candidate_index": 0,
            "patient_name_provisional": "Jane Doe",
            "reason": "Provisional booking",
        },
        headers=_auth(token),
    )
    assert selection_resp.status_code == 200, selection_resp.text
    selection = selection_resp.json()
    assert selection["safe"] is True

    before_appt, before_audit = _row_counts(db)
    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "selection_proposal": selection},
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert "bernie_confirm_create_proposal" in data["audit_evidence"]
    confidence_codes = [c for c in data["audit_evidence"] if c.startswith("bernie_identity_confidence_")]
    assert confidence_codes == []

    assert db.query(Appointment).count() == before_appt + 1
    assert db.query(AppointmentAuditLog).count() == before_audit + 1
