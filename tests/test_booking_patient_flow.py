"""
Booking and patient-flow contract tests.

Covers the gaps not addressed by test_booking_create_edit.py or test_waiting_room.py:

Schema validation:
- AppointmentUpdate: partial local pair (date-only or time-only) → 422
- AppointmentUpdate: both date and time → 200 (contract positive case)

Cancellation semantics:
- Cancelled is recoverable: PATCH Cancelled → Booked → appears in waiting room
- Cancelled does not block new booking at same slot
- Cancelled appointment appears in GET /appointments list
- Cancelled does NOT appear in waiting room

DNA / NoShow semantics:
- DNA and NoShow do not block new bookings at same slot (isolated per-status)
- DNA and NoShow appear in GET /appointments list
- DNA and NoShow do NOT appear in waiting room

Appointment type update via PUT:
- appointment_type_id can be changed on an existing appointment

Queue / patient-flow ordering in the waiting room:
- Mixed-status waiting room (Booked/Arrived/InConsult) ordered by queue_position then start_time_local
- queue_position update via PUT is reflected in waiting-room ordering

List endpoint visibility:
- GET /appointments returns all statuses by default
- GET /appointments?status= filter works for terminal statuses
"""
import uuid
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from tests.conftest import make_token

TODAY = date.today()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked,
               start_h=9, start_m=0, duration=15,
               queue_position=None):
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(TODAY, time(start_h, start_m), tzinfo=timezone.utc),
        appointment_date=TODAY,
        start_time_local=time(start_h, start_m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
        queue_position=queue_position,
    )
    db.add(a)
    db.flush()
    return a


def _auth(client, gp_user):
    return {"Authorization": f"Bearer {make_token(gp_user)}"}


# ─── AppointmentUpdate partial-pair validation ─────────────────────────────────

def test_update_partial_date_without_time_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={"appointment_date": TODAY.isoformat()},
        headers=_auth(client, gp_user),
    )
    assert resp.status_code == 422


def test_update_partial_time_without_date_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={"start_time_local": "10:00:00"},
        headers=_auth(client, gp_user),
    )
    assert resp.status_code == 422


def test_update_full_local_pair_is_accepted(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={"appointment_date": TODAY.isoformat(), "start_time_local": "10:00:00"},
        headers=_auth(client, gp_user),
    )
    assert resp.status_code == 200
    assert resp.json()["start_time_local"] == "10:00:00"


# ─── Cancellation semantics ────────────────────────────────────────────────────

def test_cancelled_appointment_can_be_reopened_to_booked(
        client, db, gp_user, practice, practitioner, patient):
    """Cancelled is a recoverable status — PATCH back to Booked must succeed."""
    appt = _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Cancelled)
    token = make_token(gp_user)
    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Booked"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "Booked"


def test_reopened_cancelled_appears_in_waiting_room(
        client, db, gp_user, practice, practitioner, patient):
    """After reopening a cancelled appointment it must appear in the waiting room."""
    appt = _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Cancelled)
    token = make_token(gp_user)
    client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Arrived"},
        headers={"Authorization": f"Bearer {token}"},
    )
    wr = client.get("/api/v1/appointments/waiting-room", headers={"Authorization": f"Bearer {token}"})
    assert str(appt.id) in [e["id"] for e in wr.json()]


def test_cancelled_does_not_block_new_booking_at_same_slot(
        client, db, gp_user, practice, practitioner, patient):
    _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Cancelled, start_h=9, duration=15)
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "appointment_date": TODAY.isoformat(),
            "start_time_local": "09:00:00",
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201


def test_cancelled_appears_in_appointments_list(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Cancelled)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    ids = [e["id"] for e in resp.json()]
    assert str(appt.id) in ids


def test_cancelled_excluded_from_waiting_room(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Cancelled)
    token = make_token(gp_user)
    wr = client.get("/api/v1/appointments/waiting-room", headers={"Authorization": f"Bearer {token}"})
    assert str(appt.id) not in [e["id"] for e in wr.json()]


# ─── DNA / NoShow semantics ───────────────────────────────────────────────────

@pytest.mark.parametrize("attendance_status", [
    AppointmentStatus.DNA, AppointmentStatus.NoShow,
])
def test_attendance_outcome_does_not_block_new_booking(
        attendance_status, client, db, gp_user, practice, practitioner, patient):
    """DNA and NoShow are attendance outcomes — they must not block the same slot."""
    _make_appt(db, practice, practitioner, patient,
               status=attendance_status, start_h=9, duration=15)
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "appointment_date": TODAY.isoformat(),
            "start_time_local": "09:00:00",
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201


@pytest.mark.parametrize("attendance_status", [
    AppointmentStatus.DNA, AppointmentStatus.NoShow,
])
def test_attendance_outcome_appears_in_appointments_list(
        attendance_status, client, db, gp_user, practice, practitioner, patient):
    """DNA and NoShow are outcomes that must remain visible in the full list."""
    appt = _make_appt(db, practice, practitioner, patient, status=attendance_status)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert str(appt.id) in [e["id"] for e in resp.json()]


@pytest.mark.parametrize("attendance_status", [
    AppointmentStatus.DNA, AppointmentStatus.NoShow,
])
def test_attendance_outcome_excluded_from_waiting_room(
        attendance_status, client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, status=attendance_status)
    token = make_token(gp_user)
    wr = client.get("/api/v1/appointments/waiting-room", headers={"Authorization": f"Bearer {token}"})
    assert str(appt.id) not in [e["id"] for e in wr.json()]


# ─── GET /appointments list filters ──────────────────────────────────────────

def test_list_appointments_status_filter_returns_only_matching(
        client, db, gp_user, practice, practitioner, patient):
    _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Booked, start_h=9)
    _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Cancelled, start_h=10)
    token = make_token(gp_user)
    resp = client.get(
        "/api/v1/appointments?status=Cancelled",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "Cancelled"


def test_list_appointments_returns_all_statuses_by_default(
        client, db, gp_user, practice, practitioner, patient):
    _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Booked, start_h=9)
    _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Cancelled, start_h=10)
    _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.DNA, start_h=11)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 3


# ─── Appointment type update via PUT ──────────────────────────────────────────

def test_update_appointment_type_via_put(
        client, db, gp_user, practice, practitioner, patient, appt_type):
    appt = _make_appt(db, practice, practitioner, patient)
    assert appt.appointment_type_id is None
    token = make_token(gp_user)
    resp = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={"appointment_type_id": str(appt_type.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["appointment_type"]["name"] == "Standard"


def test_update_appointment_type_cross_practice_returns_404(
        client, db, gp_user, practice, practitioner, patient, practice_b):
    from app.models.appointments import AppointmentType
    other_type = AppointmentType(
        practice_id=practice_b.id,
        name="OtherType",
        default_duration=15,
    )
    db.add(other_type)
    db.flush()
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={"appointment_type_id": str(other_type.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# ─── Queue position update and waiting-room ordering ─────────────────────────

def test_queue_position_update_via_put(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    assert appt.queue_position is None
    token = make_token(gp_user)
    resp = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={"queue_position": 3},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["queue_position"] == 3


def test_waiting_room_mixed_status_ordered_by_queue_then_time(
        client, db, gp_user, practice, practitioner, patient):
    """Arrived at 09:00 q=2, InConsult at 10:00 q=1, Booked at 11:00 q=None → [InConsult, Arrived, Booked]."""
    _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Arrived,
               start_h=9, queue_position=2)
    _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.InConsult,
               start_h=10, queue_position=1)
    _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Booked,
               start_h=11, queue_position=None)
    token = make_token(gp_user)
    wr = client.get("/api/v1/appointments/waiting-room",
                    headers={"Authorization": f"Bearer {token}"})
    assert wr.status_code == 200
    data = wr.json()
    assert len(data) == 3
    assert data[0]["status"] == "InConsult"    # queue_position=1
    assert data[1]["status"] == "Arrived"      # queue_position=2
    assert data[2]["queue_position"] is None   # null last
