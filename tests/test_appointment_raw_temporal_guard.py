"""
Sprint R7: Raw temporal guard for appointment create/update and proposal paths.

Tests exercise the past-date and same-day-window-elapsed guards in:
  - POST /appointments (raw create)
  - PUT /appointments/{id} (raw update)
  - POST /appointments/proposals/create (create proposal builder)
  - POST /appointments/proposals/update/{id} (update proposal builder)

Clock is monkeypatched locally per-test (no global/autouse fixture).
All assertions are fully deterministic against a pinned clinic-local now.
"""
from __future__ import annotations

import datetime as _dt
from datetime import date, datetime, time, timezone

import pytest

import app.routers.appointments as appointments_router
from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel
from tests.conftest import make_token

# Fixed dates used across tests
_PAST_DATE = date(2026, 1, 15)
_FUTURE_DATE = date(2026, 12, 1)
_TODAY = date(2026, 7, 5)

CREATE_URL = "/api/v1/appointments"
UPDATE_URL = "/api/v1/appointments/{appt_id}"
PROPOSAL_CREATE_URL = "/api/v1/appointments/proposals/create"
PROPOSAL_UPDATE_URL = "/api/v1/appointments/proposals/update/{appt_id}"


# ─── Clock helpers ────────────────────────────────────────────────────────────

def _fixed_now(target_date: date, hour: int, minute: int = 0):
    """Return a monkeypatch target that yields a tz-aware datetime at date/hour/minute.

    Uses Australia/Sydney (+10) as a representative non-UTC clinic timezone so
    that tz-aware arithmetic is exercised in the guard.
    """
    from zoneinfo import ZoneInfo
    _tz = ZoneInfo("Australia/Sydney")
    dt = datetime(target_date.year, target_date.month, target_date.day, hour, minute, 0, tzinfo=_tz)
    return lambda tz: dt  # noqa: ARG005


# ─── DB helpers ───────────────────────────────────────────────────────────────

def _make_appt(db, practice, practitioner, patient, appt_date=_FUTURE_DATE, start_h=9):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(appt_date, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    db.commit()
    return appt


def _auth(user):
    return {"Authorization": f"Bearer {make_token(user)}"}


# ─── Raw create guard ─────────────────────────────────────────────────────────

def test_raw_create_past_date_rejected(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /appointments with a past date returns 422 appointment_in_past."""
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": _PAST_DATE.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    resp = client.post(CREATE_URL, json=body, headers=_auth(gp_user))
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert detail["code"] == "appointment_in_past"
    assert db.query(Appointment).count() == 0


def test_raw_create_fully_elapsed_same_day_rejected(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /appointments with a same-day slot that has fully elapsed returns 422 same_day_window_elapsed."""
    # Clock at 10:00; appointment 09:00+15min ended at 09:15 → fully elapsed
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": _TODAY.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    resp = client.post(CREATE_URL, json=body, headers=_auth(gp_user))
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert detail["code"] == "same_day_window_elapsed"
    assert db.query(Appointment).count() == 0


def test_raw_create_same_day_open_window_accepted(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /appointments with a same-day slot that is still open returns 201."""
    # Clock at 08:00; appointment 09:00+15min ends at 09:15 → not yet elapsed
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 8, 0))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": _TODAY.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    resp = client.post(CREATE_URL, json=body, headers=_auth(gp_user))
    assert resp.status_code == 201
    assert db.query(Appointment).count() == 1


def test_raw_create_future_date_accepted(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /appointments with a future date returns 201."""
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": _FUTURE_DATE.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    resp = client.post(CREATE_URL, json=body, headers=_auth(gp_user))
    assert resp.status_code == 201
    assert db.query(Appointment).count() == 1


# ─── Raw update guard ─────────────────────────────────────────────────────────

def test_raw_update_reschedule_into_past_rejected(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """PUT /appointments/{id} rescheduling to a past date returns 422."""
    appt = _make_appt(db, gp_user.practice, practitioner, patient)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": _PAST_DATE.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    url = UPDATE_URL.format(appt_id=appt.id)
    resp = client.put(url, json=body, headers=_auth(gp_user))
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "appointment_in_past"


def test_raw_update_reschedule_into_future_accepted(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """PUT /appointments/{id} rescheduling to a future date returns 200."""
    appt = _make_appt(db, gp_user.practice, practitioner, patient)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    new_date = date(2026, 12, 2)
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": new_date.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    url = UPDATE_URL.format(appt_id=appt.id)
    resp = client.put(url, json=body, headers=_auth(gp_user))
    assert resp.status_code == 200


def test_raw_update_non_temporal_field_unaffected(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """PUT /appointments/{id} with only reason change is not blocked by temporal guard."""
    appt = _make_appt(db, gp_user.practice, practitioner, patient)
    # Clock after the appointment's time — would be 'window_fully_past' if temporal guard fires
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_FUTURE_DATE, 23, 59))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "reason": "Updated reason only",
    }
    url = UPDATE_URL.format(appt_id=appt.id)
    resp = client.put(url, json=body, headers=_auth(gp_user))
    # Temporal guard must not fire on non-temporal fields
    assert resp.status_code == 200


# ─── Create proposal guard ────────────────────────────────────────────────────

def test_create_proposal_past_date_blocked(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /proposals/create for a past date returns safe=False, temporal block, no signed evidence."""
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": _PAST_DATE.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    resp = client.post(PROPOSAL_CREATE_URL, json=body, headers=_auth(gp_user))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    block_codes = [b["code"] for b in data["blocks"]]
    assert "appointment_in_past" in block_codes
    assert data.get("signed_confirmation_evidence") is None


def test_create_proposal_elapsed_same_day_blocked(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /proposals/create for a fully-elapsed same-day slot returns blocked, no signed evidence."""
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": _TODAY.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    resp = client.post(PROPOSAL_CREATE_URL, json=body, headers=_auth(gp_user))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    block_codes = [b["code"] for b in data["blocks"]]
    assert "same_day_window_elapsed" in block_codes
    assert data.get("signed_confirmation_evidence") is None


def test_create_proposal_future_date_safe(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /proposals/create for a future date returns safe=True with signed evidence."""
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    body = {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": _FUTURE_DATE.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    resp = client.post(PROPOSAL_CREATE_URL, json=body, headers=_auth(gp_user))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data.get("signed_confirmation_evidence") is not None


# ─── Update proposal guard ────────────────────────────────────────────────────

def test_update_proposal_reschedule_into_past_blocked(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /proposals/update/{id} rescheduling into past returns blocked, no signed evidence."""
    appt = _make_appt(db, gp_user.practice, practitioner, patient)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    body = {
        "appointment_date": _PAST_DATE.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    url = PROPOSAL_UPDATE_URL.format(appt_id=appt.id)
    resp = client.post(url, json=body, headers=_auth(gp_user))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    block_codes = [b["code"] for b in data["blocks"]]
    assert "appointment_in_past" in block_codes
    assert data.get("signed_confirmation_evidence") is None


def test_update_proposal_reschedule_into_future_safe(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /proposals/update/{id} rescheduling into future returns safe=True with signed evidence."""
    appt = _make_appt(db, gp_user.practice, practitioner, patient)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_TODAY, 10, 0))
    new_date = date(2026, 12, 2)
    body = {
        "appointment_date": new_date.isoformat(),
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
    }
    url = PROPOSAL_UPDATE_URL.format(appt_id=appt.id)
    resp = client.post(url, json=body, headers=_auth(gp_user))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data.get("signed_confirmation_evidence") is not None


def test_update_proposal_non_temporal_field_safe(
    client, db, gp_user, practitioner, patient, appt_type, monkeypatch
):
    """POST /proposals/update/{id} with only reason change: temporal guard does not fire."""
    appt = _make_appt(db, gp_user.practice, practitioner, patient)
    # Clock after the fixture appointment date — would block if temporal guard fires on non-temporal fields
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(_FUTURE_DATE, 23, 59))
    body = {"reason": "Reason-only update, no date change"}
    url = PROPOSAL_UPDATE_URL.format(appt_id=appt.id)
    resp = client.post(url, json=body, headers=_auth(gp_user))
    assert resp.status_code == 200
    data = resp.json()
    # Temporal guard must not fire; proposal should be safe (no temporal blocks)
    temporal_block_codes = {"appointment_in_past", "same_day_window_elapsed"}
    actual_block_codes = {b["code"] for b in data["blocks"]}
    assert not (temporal_block_codes & actual_block_codes), (
        f"Unexpected temporal blocks on non-temporal update: {actual_block_codes}"
    )
