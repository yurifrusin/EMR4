"""
PATCH /api/v1/appointments/{appointment_id}/status
DELETE /api/v1/appointments/{appointment_id}
POST /api/v1/appointments/proposals/delete/{appointment_id}

Covers:
- Auth gate (401 without token)
- Non-existent appointment → 404
- Cross-practice mutation → 404
- All valid statuses accepted (200 + updated status in response)
- Invalid status value → 422
- Waiting-room inclusion/exclusion after mutation
- Response embeds patient, practitioner, appointment_type
- DELETE soft-cancels, clears waiting_area_id, row remains in DB
- proposals/delete surfaces waiting_area side-effects before the write
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.diary import WaitingArea
from app.models.tenancy import Practitioner
from tests.conftest import make_token

TODAY = date.today()


def _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked,
               appt_date=None, start_h=9):
    appt_date = appt_date if appt_date is not None else TODAY
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(appt_date, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(a)
    db.flush()
    return a


def _patch_status(client, token, appt_id, new_status: str):
    return client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": new_status},
        headers={"Authorization": f"Bearer {token}"},
    )


# ─── Auth gate ─────────────────────────────────────────────────────────────────

def test_status_mutation_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Confirmed"},
    )
    assert resp.status_code == 401


def test_status_mutation_rejects_unknown_role_token(client, db, practice, practitioner, patient):
    """A token with no mutating appointment role cannot patch appointment status."""
    from app.services.auth_service import create_access_token

    appt = _make_appt(db, practice, practitioner, patient)
    bad_token = create_access_token({
        "sub": str(appt.id),
        "practice_id": str(practice.id),
        "role": "UnknownRole",
    })
    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Confirmed"},
        headers={"Authorization": f"Bearer {bad_token}"},
    )
    assert resp.status_code in (401, 403)


# ─── Not found ─────────────────────────────────────────────────────────────────

def test_status_mutation_nonexistent_appointment_returns_404(client, gp_user):
    import uuid
    token = make_token(gp_user)
    resp = _patch_status(client, token, uuid.uuid4(), "Confirmed")
    assert resp.status_code == 404


# ─── Cross-practice isolation ──────────────────────────────────────────────────

def test_status_mutation_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    """A user from practice A cannot mutate practice B's appointment."""
    from app.models.tenancy import Practitioner
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Bob", last_name="Other",
        ahpra_number="MED0008888888",
    )
    db.add(prac_b)
    db.flush()
    appt_b = _make_appt(db, practice_b, prac_b, patient_b)

    token = make_token(gp_user)  # belongs to practice A
    resp = _patch_status(client, token, appt_b.id, "Confirmed")
    assert resp.status_code == 404


# ─── Valid statuses ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("new_status", [
    "Booked", "Confirmed", "Arrived", "InConsult",
    "Completed", "Cancelled", "NoShow", "DNA",
])
def test_status_mutation_all_valid_statuses_accepted(
        new_status, client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _patch_status(client, token, appt.id, new_status)
    assert resp.status_code == 200
    assert resp.json()["status"] == new_status


# ─── Invalid status ────────────────────────────────────────────────────────────

def test_status_mutation_invalid_status_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _patch_status(client, token, appt.id, "NotAStatus")
    assert resp.status_code == 422


# ─── Response shape ────────────────────────────────────────────────────────────

def test_status_mutation_response_embeds_patient_and_practitioner(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _patch_status(client, token, appt.id, "Confirmed")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "Confirmed"
    assert data["patient"]["first_name"] == "Margaret"
    assert data["practitioner"]["ahpra_number"] == "MED0001234567"
    assert "end_time" in data
    assert "start_time_local" in data


def test_status_mutation_response_embeds_appointment_type(
        client, db, gp_user, practice, practitioner, patient, appt_type):
    appt = _make_appt(db, practice, practitioner, patient)
    appt.appointment_type_id = appt_type.id
    db.flush()
    token = make_token(gp_user)
    resp = _patch_status(client, token, appt.id, "Arrived")
    assert resp.status_code == 200
    assert resp.json()["appointment_type"]["name"] == "Standard"


# ─── Waiting-room interaction ──────────────────────────────────────────────────

@pytest.mark.parametrize("active_status", [
    "Booked", "Confirmed", "Arrived", "InConsult",
])
def test_mutation_to_active_status_appears_in_waiting_room(
        active_status, client, db, gp_user, practice, practitioner, patient):
    """After mutating to an active status, appointment appears in the waiting room."""
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.Completed)
    token = make_token(gp_user)
    _patch_status(client, token, appt.id, active_status)

    wr = client.get("/api/v1/appointments/waiting-room",
                    headers={"Authorization": f"Bearer {token}"})
    ids = [e["id"] for e in wr.json()]
    assert str(appt.id) in ids


@pytest.mark.parametrize("terminal_status", [
    "Completed", "Cancelled", "NoShow", "DNA",
])
def test_mutation_to_terminal_status_disappears_from_waiting_room(
        terminal_status, client, db, gp_user, practice, practitioner, patient):
    """After mutating to a terminal status, appointment is gone from the waiting room."""
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.Arrived)
    token = make_token(gp_user)
    _patch_status(client, token, appt.id, terminal_status)

    wr = client.get("/api/v1/appointments/waiting-room",
                    headers={"Authorization": f"Bearer {token}"})
    ids = [e["id"] for e in wr.json()]
    assert str(appt.id) not in ids


# ─── DELETE soft-cancel ────────────────────────────────────────────────────────

def _make_area(db, practice):
    area = WaitingArea(practice_id=practice.id, name="Main Waiting Room")
    db.add(area)
    db.flush()
    return area


def _delete(client, token, appt_id):
    return client.delete(
        f"/api/v1/appointments/{appt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )


DELETE_PROPOSAL_URL = "/api/v1/appointments/proposals/delete/{}"


def test_delete_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.delete(f"/api/v1/appointments/{appt.id}")
    assert resp.status_code == 401


def test_delete_soft_cancels_appointment(client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _delete(client, token, appt.id)
    assert resp.status_code == 204
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Cancelled


def test_delete_clears_waiting_area_on_cancel(
        client, db, gp_user, practice, practitioner, patient):
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    appt.waiting_area_id = area.id
    db.flush()

    token = make_token(gp_user)
    resp = _delete(client, token, appt.id)
    assert resp.status_code == 204
    db.refresh(appt)
    assert appt.waiting_area_id is None


def test_delete_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Bob", last_name="Other",
        ahpra_number="MED0009999999",
    )
    db.add(prac_b)
    db.flush()
    appt_b = _make_appt(db, practice_b, prac_b, patient_b)
    token = make_token(gp_user)  # belongs to practice A
    resp = _delete(client, token, appt_b.id)
    assert resp.status_code == 404


def test_delete_proposal_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.post(DELETE_PROPOSAL_URL.format(appt.id))
    assert resp.status_code == 401


def test_delete_proposal_warns_waiting_area_cleared(
        client, db, gp_user, practice, practitioner, patient):
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    appt.waiting_area_id = area.id
    db.flush()

    token = make_token(gp_user)
    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["requires_confirmation"] is True
    assert data["command"]["clears_waiting_area"] is True
    assert any(w["code"] == "waiting_area_cleared" for w in data["warnings"])
    assert data["blocks"] == []
    # Row must not be mutated by the proposal
    db.refresh(appt)
    assert appt.waiting_area_id == area.id


def test_delete_proposal_blocked_already_cancelled(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(
        db, practice, practitioner, patient,
        status=AppointmentStatus.Cancelled,
    )
    token = make_token(gp_user)
    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert len(data["blocks"]) >= 1
    assert data["blocks"][0]["code"] == "already_in_status"


# ─── Cancellation reason ───────────────────────────────────────────────────────

def test_delete_with_reason_persists(client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = _delete(client, token, appt.id)  # no body first; then repeat with reason
    # Use a fresh appointment for the reason test
    appt2 = _make_appt(db, practice, practitioner, patient, start_h=10)
    resp = client.request(
        "DELETE",
        f"/api/v1/appointments/{appt2.id}",
        json={"cancellation_reason": "Patient called to cancel"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
    db.refresh(appt2)
    assert appt2.cancellation_reason == "Patient called to cancel"
    assert appt2.status == AppointmentStatus.Cancelled


def test_delete_without_reason_is_null(client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=11)
    token = make_token(gp_user)
    resp = _delete(client, token, appt.id)
    assert resp.status_code == 204
    db.refresh(appt)
    assert appt.cancellation_reason is None


def test_delete_proposal_echoes_reason_in_command(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=12)
    token = make_token(gp_user)
    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt.id),
        json={"cancellation_reason": "Practitioner unavailable"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["command"]["cancellation_reason"] == "Practitioner unavailable"
    # Row must not be mutated by the proposal
    db.refresh(appt)
    assert appt.cancellation_reason is None
    assert appt.status == AppointmentStatus.Booked


def test_delete_reason_too_long_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=13)
    token = make_token(gp_user)
    resp = client.request(
        "DELETE",
        f"/api/v1/appointments/{appt.id}",
        json={"cancellation_reason": "x" * 501},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
