"""Sprint D8 patient collision source hardening - regression tests.

Proves that:
1.  patient_has_active_booking_on_date bypasses the compact-context cap:
    a patient with 4+ future bookings on the requested day is detected even
    though future_bookings is capped at 3.
2.  source_appointment_id exclusion: passing the appointment being rescheduled
    as the source_appointment_id suppresses the self-collision warning.
3.  The interpret-booking-instruction route emits the warning for a cap-overflow
    collision (4th same-day booking not in compact context).
4.  The interpret route does NOT emit the warning when the only same-day booking
    is the source appointment (reschedule self-exclusion).
5.  The supervised-booking route mirrors (3) and (4) above.

All route tests use the fake interpreter; no live Gemini calls.
"""

from datetime import date, datetime, time, timezone
import uuid

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.schemas.appointments import (
    BernieBookingContextEntry,
    BerniePatientBookingContext,
)
from app.services.bernie_patient_context import (
    patient_has_active_booking_on_date,
)
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
SUPERVISED_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"

# Dates chosen to land on weekdays (Mon–Fri schedule fixture) and avoid
# same-day clamping. July 2026: Jul 14=Tue, Jul 16=Thu, Jul 21=Tue.
D8_REQUEST_DATE_OBJ = date(2026, 7, 14)
D8_REQUEST_DATE_STR = "2026-07-14"
D8_REF_DATE_OBJ = date(2026, 7, 14)
D8_REF_DATE_STR = "2026-07-14"
D8_CLINIC_NOW = datetime(2026, 7, 14, 9, 0, tzinfo=timezone.utc)

D8_SB_DATE_OBJ = date(2026, 7, 16)
D8_SB_DATE_STR = "2026-07-16"


def _make_appt(db, practice, practitioner, patient, appt_date, h, m, status, duration=15):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime(appt_date.year, appt_date.month, appt_date.day, h, m, tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(h, m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


# ── Unit tests for patient_has_active_booking_on_date ─────────────────────────

def test_direct_db_detects_booking_on_date(db, practice, practitioner, patient):
    """Direct DB query returns True for a non-terminal booking on the requested date."""
    _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, 10, 0, AppointmentStatus.Booked)
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, D8_REQUEST_DATE_OBJ
    ) is True


def test_direct_db_returns_false_for_different_date(db, practice, practitioner, patient):
    """Direct DB query returns False when the existing booking is on a different date."""
    _make_appt(db, practice, practitioner, patient, date(2026, 7, 21), 10, 0, AppointmentStatus.Booked)
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, D8_REQUEST_DATE_OBJ
    ) is False


def test_direct_db_ignores_terminal_statuses(db, practice, practitioner, patient):
    """Direct DB query ignores Completed/Cancelled/NoShow/DNA bookings."""
    for status in (
        AppointmentStatus.Completed,
        AppointmentStatus.Cancelled,
        AppointmentStatus.NoShow,
        AppointmentStatus.DNA,
    ):
        _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, 10, 0, status)
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, D8_REQUEST_DATE_OBJ
    ) is False


def test_direct_db_cap_overflow(db, practice, practitioner, patient):
    """Direct DB query detects a collision that lies beyond the 3-entry compact cap.

    Creates 4 non-terminal future bookings on D8_REQUEST_DATE_OBJ (different
    times). The first 3 fill the compact cap; only the direct DB query can
    detect the 4th.
    """
    for hour in (9, 10, 11, 14):
        _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, hour, 0, AppointmentStatus.Booked)
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, D8_REQUEST_DATE_OBJ
    ) is True


def test_direct_db_source_exclusion(db, practice, practitioner, patient):
    """Passing source_appointment_id excludes that booking from the collision check."""
    appt = _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, 10, 0, AppointmentStatus.Booked)
    # Without exclusion: collision detected.
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, D8_REQUEST_DATE_OBJ
    ) is True
    # With source excluded: no other booking on the day → no collision.
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, D8_REQUEST_DATE_OBJ,
        source_appointment_id=appt.id,
    ) is False


def test_direct_db_source_exclusion_with_second_booking(db, practice, practitioner, patient):
    """Source exclusion removes only the source booking; a second same-day booking still triggers."""
    source = _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, 9, 0, AppointmentStatus.Booked)
    _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, 11, 0, AppointmentStatus.Booked)
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, D8_REQUEST_DATE_OBJ,
        source_appointment_id=source.id,
    ) is True


# ── Interpret route: cap overflow ──────────────────────────────────────────────

def test_interpret_cap_overflow_emits_warning(
    client, db, gp_user, practice, patient, practitioner, monkeypatch,
):
    """interpret route emits existing_future_follow_up when the same-day collision is
    the 4th booking — beyond the compact-context cap of 3."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D8_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    # Create 4 same-day bookings. The compact cap keeps only 3; the 4th is
    # invisible to has_existing_booking_on_requested_day.
    for hour in (9, 10, 11, 14):
        _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, hour, 0, AppointmentStatus.Booked)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                f"date_from:{D8_REQUEST_DATE_STR} duration:15"
            ),
            "reference_date": D8_REF_DATE_STR,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        "existing_future_follow_up warning must be emitted even when the collision "
        "lies beyond the compact-context cap"
    )


# ── Interpret route: reschedule self-exclusion ─────────────────────────────────

def test_interpret_source_frame_prevents_self_collision(
    client, db, gp_user, practice, patient, practitioner, monkeypatch,
):
    """interpret route does NOT emit the warning when the only same-day booking
    is the appointment being rescheduled (passed as a selected_diary_appointment
    context frame)."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D8_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    # One existing booking on the requested day — the appointment being rescheduled.
    source = _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, 10, 0, AppointmentStatus.Booked)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                f"date_from:{D8_REQUEST_DATE_STR} duration:15"
            ),
            "reference_date": D8_REF_DATE_STR,
            "context_frames": [
                {
                    "type": "selected_diary_appointment",
                    "appointment_id": str(source.id),
                    "patient_label": "test patient",
                }
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" not in warning_codes, (
        "existing_future_follow_up warning must NOT be emitted when the only "
        "same-day booking is the appointment being rescheduled (source exclusion)"
    )


def test_interpret_source_frame_excluded_but_second_booking_still_warns(
    client, db, gp_user, practice, patient, practitioner, monkeypatch,
):
    """interpret route still emits the warning when there is a second same-day
    booking besides the source appointment."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D8_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    source = _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, 9, 0, AppointmentStatus.Booked)
    _make_appt(db, practice, practitioner, patient, D8_REQUEST_DATE_OBJ, 11, 0, AppointmentStatus.Booked)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                f"date_from:{D8_REQUEST_DATE_STR} duration:15"
            ),
            "reference_date": D8_REF_DATE_STR,
            "context_frames": [
                {
                    "type": "selected_diary_appointment",
                    "appointment_id": str(source.id),
                    "patient_label": "test patient",
                }
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        "existing_future_follow_up warning must still be emitted when a second "
        "same-day booking exists beyond the excluded source appointment"
    )


# ── Supervised booking route: cap overflow ─────────────────────────────────────

def test_supervised_booking_cap_overflow_emits_warning(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """supervised-booking emits existing_future_follow_up when the same-day collision
    is the 4th booking — beyond the compact-context cap."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D8_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    for hour in (9, 10, 11, 14):
        _make_appt(db, practice, practitioner, patient, D8_SB_DATE_OBJ, hour, 0, AppointmentStatus.Booked)

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": D8_REF_DATE_STR,
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": D8_SB_DATE_STR,
                "duration_minutes": "15",
            },
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        "existing_future_follow_up warning must be emitted even when the collision "
        "lies beyond the compact-context cap (supervised-booking route)"
    )


# ── Supervised booking route: reschedule self-exclusion ───────────────────────

def test_supervised_booking_source_frame_prevents_self_collision(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """supervised-booking does NOT emit the warning when the only same-day booking
    is the appointment being rescheduled (source exclusion via context_frames)."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D8_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    source = _make_appt(db, practice, practitioner, patient, D8_SB_DATE_OBJ, 10, 0, AppointmentStatus.Booked)

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": D8_REF_DATE_STR,
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": D8_SB_DATE_STR,
                "duration_minutes": "15",
            },
            "patient_id": str(patient.id),
            "context_frames": [
                {
                    "type": "selected_diary_appointment",
                    "appointment_id": str(source.id),
                }
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" not in warning_codes, (
        "existing_future_follow_up warning must NOT be emitted when the only "
        "same-day booking is the appointment being rescheduled (supervised-booking)"
    )
