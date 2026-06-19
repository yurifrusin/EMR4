"""
PATCH /api/v1/appointments/{appointment_id}/status

Covers:
- Auth gate (401 without token)
- Non-existent appointment → 404
- Cross-practice mutation → 404
- All valid statuses accepted (200 + updated status in response)
- Invalid status value → 422
- Waiting-room inclusion/exclusion after mutation
- Response embeds patient, practitioner, appointment_type
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
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
