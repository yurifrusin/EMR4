"""
GET /api/v1/appointments/waiting-room

Covers:
- Auth gate
- Only today's appointments (appointment_date == practice-local today)
- Included statuses: Booked, Confirmed, Arrived, InConsult
- Excluded statuses: Completed, Cancelled, NoShow, DNA
- Ordering: queue_position (nulls last) then start_time_local
- Optional practitioner_id filter
- Practice isolation
- Required output fields (patient, practitioner, appointment_type embedded)
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from tests.conftest import make_token

TODAY = date.today()
# Use an unambiguous past date for "not today" tests.
NOT_TODAY = date(2020, 1, 1)

# A fixed UTC datetime on TODAY at 09:00 local (close enough for tests that
# don't cross midnight; practice timezone defaults to Australia/Sydney).
def _start(h: int, m: int = 0) -> datetime:
    return datetime.combine(TODAY, time(h, m), tzinfo=timezone.utc)


def _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked,
               appt_date=None,
               start_h=9, start_m=0,
               duration=15,
               queue_position=None,
               appt_type=None):
    appt_date = appt_date if appt_date is not None else TODAY
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        appointment_type_id=appt_type.id if appt_type else None,
        start_time=_start(start_h, start_m),
        appointment_date=appt_date,
        start_time_local=time(start_h, start_m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
        queue_position=queue_position,
    )
    db.add(a)
    db.flush()
    return a


# ─── Auth gate ─────────────────────────────────────────────────────────────────

def test_waiting_room_requires_auth(client):
    resp = client.get("/api/v1/appointments/waiting-room")
    assert resp.status_code == 401


# ─── Empty result ───────────────────────────────────────────────────────────────

def test_waiting_room_empty_when_no_appointments(client, gp_user):
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


# ─── Included statuses ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("status", [
    AppointmentStatus.Booked,
    AppointmentStatus.Confirmed,
    AppointmentStatus.Arrived,
    AppointmentStatus.InConsult,
])
def test_waiting_room_includes_active_status(client, db, gp_user, practice, practitioner, patient, status):
    _make_appt(db, practice, practitioner, patient, status=status)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == status.value


# ─── Excluded statuses ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("status", [
    AppointmentStatus.Completed,
    AppointmentStatus.Cancelled,
    AppointmentStatus.NoShow,
    AppointmentStatus.DNA,
])
def test_waiting_room_excludes_terminal_status(client, db, gp_user, practice, practitioner, patient, status):
    _make_appt(db, practice, practitioner, patient, status=status)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


# ─── Date scoping ──────────────────────────────────────────────────────────────

def test_waiting_room_excludes_past_date(client, db, gp_user, practice, practitioner, patient):
    """Appointments from another date do not appear even with an active status."""
    _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked, appt_date=NOT_TODAY)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_waiting_room_only_today_not_other_dates_mixed(client, db, gp_user, practice, practitioner, patient):
    """Today's appointment appears; another date's does not."""
    _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked, appt_date=NOT_TODAY, start_h=8)
    _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked, appt_date=TODAY, start_h=9)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["appointment_date"] == TODAY.isoformat()


# ─── Ordering ─────────────────────────────────────────────────────────────────

def test_waiting_room_ordered_by_start_time_when_no_queue_position(
        client, db, gp_user, practice, practitioner, patient):
    """Without queue_position, results are ordered by start_time_local ascending."""
    _make_appt(db, practice, practitioner, patient, start_h=10)
    _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    times = [r["start_time_local"] for r in resp.json()]
    assert times == sorted(times)


def test_waiting_room_queue_position_overrides_time_order(
        client, db, gp_user, practice, practitioner, patient):
    """queue_position takes precedence; nulls go last."""
    # 09:00 with queue_position=2, 10:00 with queue_position=1, 11:00 with no position
    _make_appt(db, practice, practitioner, patient, start_h=9, queue_position=2)
    _make_appt(db, practice, practitioner, patient, start_h=10, queue_position=1)
    _make_appt(db, practice, practitioner, patient, start_h=11, queue_position=None)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["start_time_local"] == "10:00:00"   # queue_position=1
    assert data[1]["start_time_local"] == "09:00:00"   # queue_position=2
    assert data[2]["queue_position"] is None             # null last


# ─── Practitioner filter ────────────────────────────────────────────────────────

def test_waiting_room_filters_by_practitioner_id(
        client, db, gp_user, practice, practitioner, patient):
    """?practitioner_id= restricts results to that practitioner."""
    from app.models.tenancy import Practitioner
    other_prac = Practitioner(
        practice_id=practice.id,
        first_name="Jane", last_name="Doe",
        ahpra_number="MED0009999999",
    )
    db.add(other_prac)
    db.flush()

    _make_appt(db, practice, practitioner, patient, start_h=9)
    _make_appt(db, practice, other_prac, patient, start_h=10)

    token = make_token(gp_user)
    resp = client.get(
        f"/api/v1/appointments/waiting-room?practitioner_id={practitioner.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["practitioner"]["id"] == str(practitioner.id)


# ─── Practice isolation ────────────────────────────────────────────────────────

def test_waiting_room_practice_isolation(
        client, db, gp_user, practice, practitioner, patient,
        practice_b, patient_b):
    from app.models.tenancy import Practitioner
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Bob", last_name="Other",
        ahpra_number="MED0008888888",
    )
    db.add(prac_b)
    db.flush()

    # Appointment in practice A
    _make_appt(db, practice, practitioner, patient, start_h=9)
    # Appointment in practice B
    _make_appt(db, practice_b, prac_b, patient_b, start_h=9)

    token = make_token(gp_user)  # belongs to practice A
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["practice_id"] == str(practice.id)


# ─── Output fields ─────────────────────────────────────────────────────────────

def test_waiting_room_embeds_patient_and_practitioner(
        client, db, gp_user, practice, practitioner, patient):
    _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    entry = resp.json()[0]
    assert entry["patient"]["first_name"] == "Margaret"
    assert entry["practitioner"]["last_name"] == "Shera"
    assert entry["practitioner"]["ahpra_number"] == "MED0001234567"
    assert "end_time" in entry
    assert "start_time_local" in entry
    assert "appointment_date" in entry


def test_waiting_room_embeds_appointment_type_when_present(
        client, db, gp_user, practice, practitioner, patient, appt_type):
    _make_appt(db, practice, practitioner, patient, appt_type=appt_type)
    token = make_token(gp_user)
    resp = client.get("/api/v1/appointments/waiting-room",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    appt = resp.json()[0]
    assert appt["appointment_type"] is not None
    assert appt["appointment_type"]["name"] == "Standard"
    assert "color_hex" in appt["appointment_type"]
