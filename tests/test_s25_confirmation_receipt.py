"""
S25 Typed Confirmation Receipt contract.

Proves that successful appointment-create confirmations on both the canonical
staff route and the Bernie route carry an additive
appointment.confirmation_receipt.v1 response object with the correct shape and
content.  Blocked responses have no receipt.  Idempotent replay returns the
stored receipt without another write.
"""

from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
    AppointmentStatus,
)
import app.routers.appointments as appointments_router
from tests.conftest import make_token
# Route URLs

STAFF_CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm"
BERNIE_CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
PROPOSAL_URL = "/api/v1/appointments/proposals/create"
NORMALIZED_SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
SELECTION_URL = "/api/v1/appointments/proposals/slot-search/selection"

REFERENCE_DATE = "2026-06-22"
THURSDAY = date(2026, 6, 25)


@pytest.fixture(autouse=True)
def _freeze_confirm_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


def _auth(token, idempotency_key=None):
    headers = {"Authorization": f"Bearer {token}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _base_body(patient, practitioner):
    return {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": THURSDAY.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }


def _post_proposal(client, token, body, idempotency_key="proposal-key"):
    return client.post(
        PROPOSAL_URL,
        json=body,
        headers=_auth(token, idempotency_key),
    )


def _confirm_proposal(client, token, proposal, idempotency_key="receipt-staff-key"):
    payload = proposal["confirm_payload"]
    payload["confirmed"] = True
    return client.post(
        STAFF_CONFIRM_URL,
        json=payload,
        headers=_auth(token, idempotency_key),
    )


def _search_and_select(client, token, practitioner, patient, reason="Receipt test"):
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
    assert search["proposal"]["candidates"]

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


def _confirm_bernie(client, token, selection, confirmed=True, idempotency_key="receipt-bernie-key"):
    return client.post(
        BERNIE_CONFIRM_URL,
        json={
            "confirmed": confirmed,
            "selection_proposal": selection,
        },
        headers=_auth(token, idempotency_key),
    )


def _assert_generic_receipt_shape(data, expected_patient_display=None):
    """Assert the confirmation_receipt has the right shape and content."""
    assert "confirmation_receipt" in data, "Missing confirmation_receipt in response"
    r = data["confirmation_receipt"]

    assert r["schema_version"] == "appointment.confirmation_receipt.v1"
    assert r["outcome"] == "appointment_created"
    assert "appointment_id" in r
    assert isinstance(r["appointment_id"], str)
    assert r["patient_display"] and isinstance(r["patient_display"], str)
    if expected_patient_display:
        assert r["patient_display"] == expected_patient_display
    assert r["practitioner_display"] and isinstance(r["practitioner_display"], str)
    assert r["appointment_date"] and isinstance(r["appointment_date"], str)
    assert r["start_time_local"] and isinstance(r["start_time_local"], str)
    assert isinstance(r["duration_minutes"], int) and r["duration_minutes"] > 0
    assert r["status"] and isinstance(r["status"], str)
    assert "appointment_type" in r
    assert r["confirmed_by_display"] and isinstance(r["confirmed_by_display"], str)
    assert "confirmed_by_role" in r

    # Verification block
    assert "verification" in r
    v = r["verification"]
    assert v["actor_authenticated"] is True
    assert v["practice_scope_verified"] is True
    assert v["proposal_revalidated"] is True
    assert v["conflict_check_passed"] is True
    assert v["idempotency_verified"] is True
    assert v["audit_recorded"] is True
    assert v["visual_diary_check_required"] is False
    assert isinstance(v["signed_evidence_verified"], bool)

    # Cross-check against main appointment
    appt = data["appointment"]
    assert r["appointment_id"] == appt["id"]
    assert r["appointment_date"] == appt["appointment_date"]
    assert r["start_time_local"] == appt["start_time_local"]
    assert r["duration_minutes"] == appt["duration_minutes"]
    assert r["status"] == appt["status"]


# Staff confirm receipt tests


def test_staff_confirm_receipt_present_on_success(client, db, gp_user, patient, practitioner):
    """Successful staff confirmation includes a typed confirmation_receipt."""
    token = make_token(gp_user)
    proposal_resp = _post_proposal(client, token, _base_body(patient, practitioner))
    assert proposal_resp.status_code == 200
    proposal = proposal_resp.json()

    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = _confirm_proposal(client, token, proposal)
    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()

    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"

    _assert_generic_receipt_shape(data)

    # Exactly one write
    assert db.query(Appointment).count() == before_appts + 1
    assert db.query(AppointmentAuditLog).count() == before_audits + 1


def test_staff_confirm_receipt_blocked_has_no_receipt(client, db, gp_user, patient, practitioner):
    """Blocked staff confirmation must not carry a confirmation_receipt."""
    token = make_token(gp_user)
    proposal_resp = _post_proposal(client, token, _base_body(patient, practitioner))
    assert proposal_resp.status_code == 200
    proposal = proposal_resp.json()

    payload = proposal["confirm_payload"]
    payload["confirmed"] = False

    before_appts = db.query(Appointment).count()

    confirm_resp = client.post(
        STAFF_CONFIRM_URL,
        json=payload,
        headers=_auth(token, "receipt-blocked-key"),
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()

    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["confirmation_receipt"] is None, "Receipt must be None on blocked"
    assert data["appointment"] is None
    assert db.query(Appointment).count() == before_appts


def test_staff_confirm_receipt_idempotent_replay(client, db, gp_user, patient, practitioner):
    """Idempotent replay of a successful staff confirmation returns the same receipt."""
    token = make_token(gp_user)
    proposal_resp = _post_proposal(client, token, _base_body(patient, practitioner))
    assert proposal_resp.status_code == 200
    proposal = proposal_resp.json()

    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    resp1 = _confirm_proposal(client, token, proposal, idempotency_key="replay-staff-key")
    assert resp1.status_code == 200, resp1.text
    data1 = resp1.json()
    assert data1["safe"] is True
    receipt1 = data1["confirmation_receipt"]

    resp2 = _confirm_proposal(client, token, proposal, idempotency_key="replay-staff-key")
    assert resp2.status_code == 200, resp2.text
    data2 = resp2.json()
    assert data2["safe"] is True
    receipt2 = data2["confirmation_receipt"]

    assert receipt1 == receipt2

    assert db.query(Appointment).count() == before_appts + 1
    assert db.query(AppointmentAuditLog).count() == before_audits + 1


# Bernie confirm receipt tests


def test_bernie_confirm_receipt_present_on_success(client, db, gp_user, patient, practitioner, schedule):
    """Successful Bernie confirmation includes a typed confirmation_receipt."""
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)

    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = _confirm_bernie(client, token, selection)
    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()

    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"

    _assert_generic_receipt_shape(data)

    assert db.query(Appointment).count() == before_appts + 1
    assert db.query(AppointmentAuditLog).count() == before_audits + 1


def test_bernie_confirm_receipt_blocked_has_no_receipt(client, db, gp_user, patient, practitioner, schedule):
    """Blocked Bernie confirmation must not carry a confirmation_receipt."""
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)

    before_appts = db.query(Appointment).count()

    confirm_resp = _confirm_bernie(client, token, selection, confirmed=False,
                                   idempotency_key="bernie-blocked-key")
    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()

    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["confirmation_receipt"] is None, "Blocked Bernie no receipt"
    assert data["appointment"] is None
    assert db.query(Appointment).count() == before_appts


def test_bernie_confirm_receipt_idempotent_replay(client, db, gp_user, patient, practitioner, schedule):
    """Idempotent replay of a successful Bernie confirmation returns same receipt."""
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)

    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    resp1 = _confirm_bernie(client, token, selection, idempotency_key="replay-bernie-key")
    assert resp1.status_code == 200, resp1.text
    data1 = resp1.json()
    assert data1["safe"] is True
    receipt1 = data1["confirmation_receipt"]

    resp2 = _confirm_bernie(client, token, selection, idempotency_key="replay-bernie-key")
    assert resp2.status_code == 200, resp2.text
    data2 = resp2.json()
    assert data2["safe"] is True
    receipt2 = data2["confirmation_receipt"]

    assert receipt1 == receipt2

    assert db.query(Appointment).count() == before_appts + 1
    assert db.query(AppointmentAuditLog).count() == before_audits + 1


def test_bernie_confirm_verification_flag(client, db, gp_user, patient, practitioner, schedule):
    """Signed evidence verification flag reflects whether signed evidence used."""
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)

    confirm_resp = _confirm_bernie(client, token, selection, idempotency_key="bernie-flag-key")
    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()

    assert data["safe"] is True
    v = data["confirmation_receipt"]["verification"]
    # Legacy unsigned compat: signed_evidence_verified is False
    assert v["signed_evidence_verified"] is False
