"""Sprint D6 patient advisory collision semantics - regression-test hardening.

Proves that:
1.  has_existing_booking_on_requested_day returns True only for an exact date
    match in future_bookings, False for None, different dates, or empty context.
2.  The interpret-booking-instruction route emits the existing_future_follow_up
    warning when normalized date_from matches a future_booking date, and does
    NOT emit it for an unrelated future booking on a different day, while
    preserving patient_booking_context in both cases.
3.  The supervised-booking route emits the warning when constraint.date_from
    matches a future_booking date, and does NOT emit it otherwise, while
    preserving patient_booking_context in both cases.

BerniePatientBookingContext.existing_future_follow_up intentionally stays broad
(equivalent to has_future_booking) - it is advisory context, not the warning
gate.  Warning emission is gated by has_existing_booking_on_requested_day at
the router/policy level.

All route tests use the fake interpreter; no live Gemini calls.
"""

from datetime import date, datetime, time, timezone
import uuid

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import AppointmentStatus, BookingChannel
from app.schemas.appointments import (
    BernieBookingContextEntry,
    BerniePatientBookingContext,
)
from app.services.bernie_patient_context import (
    build_existing_future_follow_up_warning,
    has_existing_booking_on_requested_day,
)
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
SUPERVISED_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"

# Dates chosen to avoid accidental same-day clamping and to land on weekdays
# (the schedule fixture covers Mon-Fri 09:00-17:00).
# July 2026 calendar: Jul 9=Thu, Jul 10=Fri, Jul 23=Thu.
D6_REF_DATE_OBJ = date(2026, 7, 9)   # Thursday - reference / interpret test date
D6_REF_DATE_STR = "2026-07-09"
D6_CLINIC_NOW = datetime(2026, 7, 9, 9, 0, tzinfo=timezone.utc)

D6_SB_DATE_OBJ = date(2026, 7, 10)   # Friday - supervised booking requested date
D6_SB_DATE_STR = "2026-07-10"

D6_OTHER_DATE = date(2026, 7, 23)     # Thursday - unrelated future date


def _make_appt(db, practice, practitioner, patient, appt_date, h, m, status, duration=15):
    appt = appointments_router.Appointment(
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


# -- Pure unit tests for has_existing_booking_on_requested_day -----------------

def _fake_context(future_dates: list[date]) -> BerniePatientBookingContext:
    """Minimal context with the given future booking dates and no DB dependency."""
    entries = [
        BernieBookingContextEntry(
            appointment_date=d,
            relative_label="in 7 days",
            status="Booked",
            practitioner_display="Dr Test",
            duration_minutes=15,
        )
        for d in future_dates
    ]
    return BerniePatientBookingContext(
        patient_key=str(uuid.uuid4()),
        future_bookings=entries,
        recent_bookings=[],
        has_future_booking=bool(entries),
        existing_future_follow_up=bool(entries),
        recent_count=0,
        future_count=len(entries),
        reference_date=D6_REF_DATE_OBJ,
        generated_at=datetime.now(tz=timezone.utc),
    )


def test_has_existing_returns_true_for_matching_date():
    ctx = _fake_context([D6_REF_DATE_OBJ])
    assert has_existing_booking_on_requested_day(ctx, D6_REF_DATE_OBJ) is True


def test_has_existing_returns_false_for_different_date():
    ctx = _fake_context([D6_OTHER_DATE])
    assert has_existing_booking_on_requested_day(ctx, D6_REF_DATE_OBJ) is False


def test_has_existing_returns_false_for_none_requested_date():
    ctx = _fake_context([D6_REF_DATE_OBJ])
    assert has_existing_booking_on_requested_day(ctx, None) is False


def test_has_existing_returns_false_for_empty_future_bookings():
    ctx = _fake_context([])
    assert has_existing_booking_on_requested_day(ctx, D6_REF_DATE_OBJ) is False


def test_has_existing_checks_future_bookings_not_recent():
    """A past booking on the requested date must not trigger the collision check."""
    recent_entry = BernieBookingContextEntry(
        appointment_date=D6_REF_DATE_OBJ,
        relative_label="5 days ago",
        status="Completed",
        practitioner_display="Dr Test",
        duration_minutes=15,
    )
    ctx = BerniePatientBookingContext(
        patient_key=str(uuid.uuid4()),
        recent_bookings=[recent_entry],
        future_bookings=[],
        has_future_booking=False,
        existing_future_follow_up=False,
        recent_count=1,
        future_count=0,
        reference_date=D6_REF_DATE_OBJ,
        generated_at=datetime.now(tz=timezone.utc),
    )
    assert has_existing_booking_on_requested_day(ctx, D6_REF_DATE_OBJ) is False


def test_has_existing_returns_true_for_one_matching_among_several():
    ctx = _fake_context([D6_OTHER_DATE, D6_REF_DATE_OBJ])
    assert has_existing_booking_on_requested_day(ctx, D6_REF_DATE_OBJ) is True


def test_existing_future_follow_up_warning_has_correct_structure():
    """The same-day booking advisory remains a warning, not a hard block."""
    issue = build_existing_future_follow_up_warning()

    assert issue.code == "existing_future_follow_up"
    assert issue.severity == "warning"
    assert "already has an appointment on the requested day" in issue.message


# -- Interpret route: same requested-day positive warning ----------------------

def test_interpret_same_day_emits_existing_follow_up_warning(
    client, db, gp_user, practice, patient, practitioner, monkeypatch,
):
    """interpret route emits existing_future_follow_up warning when the patient
    already has a booking on the normalized date_from date."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D6_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    _make_appt(db, practice, practitioner, patient, D6_REF_DATE_OBJ, 14, 0, AppointmentStatus.Booked)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                f"date_from:{D6_REF_DATE_STR} duration:15"
            ),
            "reference_date": D6_REF_DATE_STR,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()

    ctx = data.get("patient_booking_context")
    assert ctx is not None, "Expected patient_booking_context for a recognized patient"
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True  # broad advisory flag preserved

    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        "existing_future_follow_up warning must be emitted when the patient "
        "already has a booking on the requested day"
    )


# -- Interpret route: different-day negative -----------------------------------

def test_interpret_different_day_no_warning_but_preserves_context(
    client, db, gp_user, practice, patient, practitioner, monkeypatch,
):
    """interpret route suppresses warning for a booking on a different day while
    preserving patient_booking_context with existing_future_follow_up=True."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D6_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    # Booking is on D6_OTHER_DATE (2026-07-23), request is for D6_REF_DATE_OBJ (2026-07-09).
    _make_appt(db, practice, practitioner, patient, D6_OTHER_DATE, 10, 0, AppointmentStatus.Booked)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                f"date_from:{D6_REF_DATE_STR} duration:15"
            ),
            "reference_date": D6_REF_DATE_STR,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()

    ctx = data.get("patient_booking_context")
    assert ctx is not None, "Expected patient_booking_context for a recognized patient"
    # Broad advisory flag stays True because the patient has a future booking.
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True

    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" not in warning_codes, (
        "existing_future_follow_up warning must NOT be emitted when the patient's "
        "future booking is on a different day from the requested date"
    )


# -- Supervised booking: same requested-day positive warning -------------------

def test_supervised_booking_same_day_emits_existing_follow_up_warning(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """supervised-booking emits existing_future_follow_up warning when the patient
    has a booking on the same day as constraint.date_from."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D6_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    # Booking on D6_SB_DATE_OBJ (2026-07-10, Friday) - same day as the request.
    _make_appt(db, practice, practitioner, patient, D6_SB_DATE_OBJ, 11, 0, AppointmentStatus.Booked)

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": D6_REF_DATE_STR,
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": D6_SB_DATE_STR,
                "duration_minutes": "15",
            },
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()

    ctx = data.get("patient_booking_context")
    assert ctx is not None, "Expected patient_booking_context for a recognized patient"
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True  # broad advisory flag preserved

    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        "existing_future_follow_up warning must be emitted when the patient "
        "already has a booking on the supervised-booking requested day"
    )


# -- Supervised booking: different-day negative --------------------------------

def test_supervised_booking_different_day_no_warning_but_preserves_context(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """supervised-booking suppresses warning for a booking on a different day while
    preserving patient_booking_context with existing_future_follow_up=True."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D6_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    # Booking on D6_OTHER_DATE (2026-07-23, Thursday), request is for D6_SB_DATE (2026-07-10).
    _make_appt(db, practice, practitioner, patient, D6_OTHER_DATE, 10, 0, AppointmentStatus.Booked)

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": D6_REF_DATE_STR,
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": D6_SB_DATE_STR,
                "duration_minutes": "15",
            },
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()

    ctx = data.get("patient_booking_context")
    assert ctx is not None, "Expected patient_booking_context for a recognized patient"
    # Broad advisory flag stays True because the patient has a future booking.
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True

    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" not in warning_codes, (
        "existing_future_follow_up warning must NOT be emitted when the patient's "
        "future booking is on a different day from the supervised-booking requested date"
    )
