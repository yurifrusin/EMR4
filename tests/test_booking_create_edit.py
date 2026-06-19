"""
POST /api/v1/appointments
PUT  /api/v1/appointments/{appointment_id}

Covers:
- Auth gate (401 without token) for create and update
- Role gate (403 for unknown role)
- Create with start_time (UTC datetime)
- Create with appointment_date + start_time_local (canonical local pair)
- Missing time fields → 422
- Partial local pair (only date or only time) → 422
- Duration out of range → 422
- Unknown patient_id → 404
- Unknown practitioner_id → 404
- Cross-practice patient → 404
- Cross-practice practitioner → 404
- Conflict on create → 409
- Non-blocking statuses (Cancelled/NoShow/DNA) do not block a new booking at the same slot
- 201 response shape: embedded patient, practitioner, appointment_type, end_time,
  appointment_date, start_time_local
- Update (reschedule) to a new time → 200
- Update conflict → 409
- Update excludes self (partial update without self-conflict) → 200
- Update change practitioner → 200
- Update conflict with new practitioner → 409
- Partial update (reason only) → 200, time unchanged
- Duration update → 200, end_time recalculated
- Update cross-practice → 404
- Update unknown appointment → 404
"""
import uuid
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from tests.conftest import make_token

TODAY = date.today()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _post(client, token, body: dict):
    return client.post(
        "/api/v1/appointments",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def _put(client, token, appt_id, body: dict):
    return client.put(
        f"/api/v1/appointments/{appt_id}",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def _base_body(patient, practitioner) -> dict:
    """Minimal valid create payload using the local-pair form."""
    return {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": TODAY.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }


def _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked,
               start_h=9, duration=15):
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(TODAY, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=TODAY,
        start_time_local=time(start_h, 0),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(a)
    db.flush()
    return a


# ─── Auth / role gates ─────────────────────────────────────────────────────────

def test_create_requires_auth(client, db, practice, practitioner, patient):
    resp = client.post(
        "/api/v1/appointments",
        json=_base_body(patient, practitioner),
    )
    assert resp.status_code == 401


def test_update_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={"reason": "changed"},
    )
    assert resp.status_code == 401


def test_create_rejects_unknown_role(client, db, practice, practitioner, patient):
    from app.services.auth_service import create_access_token
    bad_token = create_access_token({
        "sub": str(uuid.uuid4()),
        "practice_id": str(practice.id),
        "role": "Ghost",
    })
    resp = client.post(
        "/api/v1/appointments",
        json=_base_body(patient, practitioner),
        headers={"Authorization": f"Bearer {bad_token}"},
    )
    assert resp.status_code in (401, 403)


# ─── Create — valid inputs ─────────────────────────────────────────────────────

def test_create_with_local_pair_returns_201(client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    resp = _post(client, token, _base_body(patient, practitioner))
    assert resp.status_code == 201
    data = resp.json()
    assert data["appointment_date"] == TODAY.isoformat()
    assert data["start_time_local"] == "09:00:00"
    assert data["duration_minutes"] == 15
    assert "end_time" in data
    assert data["status"] == "Booked"


def test_create_with_utc_start_time_returns_201(client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "start_time": "2026-07-01T01:00:00+00:00",
        "duration_minutes": 15,
    }
    resp = _post(client, token, body)
    assert resp.status_code == 201
    data = resp.json()
    assert "appointment_date" in data
    assert "start_time_local" in data


def test_create_embeds_patient_practitioner_type(
        client, db, gp_user, practice, practitioner, patient, appt_type):
    token = make_token(gp_user)
    body = {**_base_body(patient, practitioner), "appointment_type_id": str(appt_type.id)}
    resp = _post(client, token, body)
    assert resp.status_code == 201
    data = resp.json()
    assert data["patient"]["first_name"] == "Margaret"
    assert data["practitioner"]["ahpra_number"] == "MED0001234567"
    assert data["appointment_type"]["name"] == "Standard"


def test_create_end_time_is_start_plus_duration(
        client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    resp = _post(client, token, {**_base_body(patient, practitioner), "duration_minutes": 30})
    assert resp.status_code == 201
    data = resp.json()
    start = datetime.fromisoformat(data["start_time"])
    end = datetime.fromisoformat(data["end_time"])
    assert (end - start).total_seconds() == 30 * 60


# ─── Create — validation errors ───────────────────────────────────────────────

def test_create_missing_time_fields_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "duration_minutes": 15,
    }
    resp = _post(client, token, body)
    assert resp.status_code == 422


def test_create_partial_local_pair_date_only_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": TODAY.isoformat(),
        "duration_minutes": 15,
    }
    resp = _post(client, token, body)
    assert resp.status_code == 422


def test_create_partial_local_pair_time_only_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    resp = _post(client, token, body)
    assert resp.status_code == 422


def test_create_duration_zero_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    body = {**_base_body(patient, practitioner), "duration_minutes": 0}
    resp = _post(client, token, body)
    assert resp.status_code == 422


def test_create_duration_over_max_returns_422(
        client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    body = {**_base_body(patient, practitioner), "duration_minutes": 481}
    resp = _post(client, token, body)
    assert resp.status_code == 422


# ─── Create — foreign-key gates ───────────────────────────────────────────────

def test_create_unknown_patient_returns_404(
        client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    body = {**_base_body(patient, practitioner), "patient_id": str(uuid.uuid4())}
    resp = _post(client, token, body)
    assert resp.status_code == 404


def test_create_unknown_practitioner_returns_404(
        client, db, gp_user, practice, practitioner, patient):
    token = make_token(gp_user)
    body = {**_base_body(patient, practitioner), "practitioner_id": str(uuid.uuid4())}
    resp = _post(client, token, body)
    assert resp.status_code == 404


def test_create_cross_practice_patient_returns_404(
        client, db, gp_user, practice, practitioner, patient, practice_b, patient_b):
    token = make_token(gp_user)
    body = {**_base_body(patient, practitioner), "patient_id": str(patient_b.id)}
    resp = _post(client, token, body)
    assert resp.status_code == 404


def test_create_cross_practice_practitioner_returns_404(
        client, db, gp_user, practice, practitioner, patient, practice_b):
    from app.models.tenancy import Practitioner
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Bob", last_name="Other",
        ahpra_number="MED0007777777",
    )
    db.add(prac_b)
    db.flush()
    token = make_token(gp_user)
    body = {**_base_body(patient, practitioner), "practitioner_id": str(prac_b.id)}
    resp = _post(client, token, body)
    assert resp.status_code == 404


# ─── Create — conflict detection ──────────────────────────────────────────────

def test_create_conflicts_with_existing_booking_returns_409(
        client, db, gp_user, practice, practitioner, patient):
    _make_appt(db, practice, practitioner, patient, start_h=9, duration=30)
    token = make_token(gp_user)
    # Attempt to book at 09:15 — within the existing 09:00–09:30 block
    body = {**_base_body(patient, practitioner), "start_time_local": "09:15:00", "duration_minutes": 15}
    resp = _post(client, token, body)
    assert resp.status_code == 409
    assert "conflicting_appointment_id" in resp.json()["detail"]


@pytest.mark.parametrize("non_blocking_status", [
    AppointmentStatus.Cancelled,
    AppointmentStatus.NoShow,
    AppointmentStatus.DNA,
])
def test_create_at_slot_with_non_blocking_status_succeeds(
        non_blocking_status, client, db, gp_user, practice, practitioner, patient):
    """Cancelled / NoShow / DNA appointments do not block a new booking."""
    _make_appt(db, practice, practitioner, patient,
               status=non_blocking_status, start_h=9, duration=15)
    token = make_token(gp_user)
    resp = _post(client, token, _base_body(patient, practitioner))
    assert resp.status_code == 201


def test_create_adjacent_appointments_do_not_conflict(
        client, db, gp_user, practice, practitioner, patient):
    """09:00–09:15 and 09:15–09:30 must NOT conflict."""
    _make_appt(db, practice, practitioner, patient, start_h=9, duration=15)
    token = make_token(gp_user)
    body = {**_base_body(patient, practitioner), "start_time_local": "09:15:00", "duration_minutes": 15}
    resp = _post(client, token, body)
    assert resp.status_code == 201


# ─── Update — auth / not found ────────────────────────────────────────────────

def test_update_nonexistent_returns_404(client, gp_user):
    token = make_token(gp_user)
    resp = _put(client, token, uuid.uuid4(), {"reason": "x"})
    assert resp.status_code == 404


def test_update_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    from app.models.tenancy import Practitioner
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Bob", last_name="Other",
        ahpra_number="MED0008888888",
    )
    db.add(prac_b)
    db.flush()
    appt_b = _make_appt(db, practice_b, prac_b, patient_b)
    token = make_token(gp_user)
    resp = _put(client, token, appt_b.id, {"reason": "x"})
    assert resp.status_code == 404


# ─── Update — reschedule ──────────────────────────────────────────────────────

def test_update_reschedules_to_new_time(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    resp = _put(client, token, appt.id, {
        "appointment_date": TODAY.isoformat(),
        "start_time_local": "10:00:00",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["start_time_local"] == "10:00:00"
    assert data["appointment_date"] == TODAY.isoformat()


def test_update_reschedule_conflict_returns_409(
        client, db, gp_user, practice, practitioner, patient):
    appt_a = _make_appt(db, practice, practitioner, patient, start_h=9, duration=15)
    appt_b = _make_appt(db, practice, practitioner, patient, start_h=10, duration=15)
    token = make_token(gp_user)
    # Move appt_b to overlap with appt_a
    resp = _put(client, token, appt_b.id, {
        "appointment_date": TODAY.isoformat(),
        "start_time_local": "09:05:00",
    })
    assert resp.status_code == 409


def test_update_partial_no_self_conflict(
        client, db, gp_user, practice, practitioner, patient):
    """Updating only reason (no time change) should never self-conflict."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    resp = _put(client, token, appt.id, {"reason": "updated reason"})
    assert resp.status_code == 200
    assert resp.json()["reason"] == "updated reason"


def test_update_duration_recalculates_end_time(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=9, duration=15)
    token = make_token(gp_user)
    resp = _put(client, token, appt.id, {"duration_minutes": 45})
    assert resp.status_code == 200
    data = resp.json()
    assert data["duration_minutes"] == 45
    start = datetime.fromisoformat(data["start_time"])
    end = datetime.fromisoformat(data["end_time"])
    assert (end - start).total_seconds() == 45 * 60


def test_update_duration_self_conflict_excluded(
        client, db, gp_user, practice, practitioner, patient):
    """Extending the duration of an appointment must not conflict with itself."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9, duration=15)
    token = make_token(gp_user)
    resp = _put(client, token, appt.id, {"duration_minutes": 60})
    assert resp.status_code == 200


def test_update_change_practitioner(
        client, db, gp_user, practice, practitioner, patient):
    from app.models.tenancy import Practitioner
    prac2 = Practitioner(
        practice_id=practice.id,
        first_name="Jane", last_name="Doe",
        ahpra_number="MED0002222222",
    )
    db.add(prac2)
    db.flush()
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    resp = _put(client, token, appt.id, {"practitioner_id": str(prac2.id)})
    assert resp.status_code == 200
    assert resp.json()["practitioner"]["id"] == str(prac2.id)


def test_update_change_to_cross_practice_practitioner_returns_404(
        client, db, gp_user, practice, practitioner, patient, practice_b):
    from app.models.tenancy import Practitioner
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Bob", last_name="Remote",
        ahpra_number="MED0009999999",
    )
    db.add(prac_b)
    db.flush()
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    resp = _put(client, token, appt.id, {"practitioner_id": str(prac_b.id)})
    assert resp.status_code == 404


def test_update_new_practitioner_conflict_returns_409(
        client, db, gp_user, practice, practitioner, patient):
    """Moving an appointment to a practitioner who already has a booking at that time → 409."""
    from app.models.tenancy import Practitioner
    prac2 = Practitioner(
        practice_id=practice.id,
        first_name="Jane", last_name="Doe",
        ahpra_number="MED0002222222",
    )
    db.add(prac2)
    db.flush()
    # Book prac2 at 09:00
    _make_appt(db, practice, prac2, patient, start_h=9, duration=15)
    # appt is on practitioner at 09:00
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    # Move appt to prac2 at 09:00 — should conflict
    resp = _put(client, token, appt.id, {"practitioner_id": str(prac2.id)})
    assert resp.status_code == 409
