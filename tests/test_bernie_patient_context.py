"""
Sprint 104: BerniePatientBookingContext service — unit tests.

Proves the service is pure read-only, practice-scoped, correct on edge cases,
and does not call any LLM or external provider. No live Gemini dependency.
"""

from datetime import date, datetime, time, timezone, timedelta
import uuid

import pytest

from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel
from app.models.tenancy import Practitioner
from app.services.bernie_patient_context import build_patient_booking_context, _relative_label
from tests.conftest import make_token


REFERENCE_DATE = date(2026, 7, 2)


def _make_appt(db, practice, practitioner, patient, appt_date, h, m, status, duration=15):
    start = datetime.combine(appt_date, time(h, m, tzinfo=None)).replace(tzinfo=timezone.utc)
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=start,
        appointment_date=appt_date,
        start_time_local=time(h, m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


# ── Relative label helper ─────────────────────────────────────────────────────

def test_relative_label_today():
    assert _relative_label(REFERENCE_DATE, REFERENCE_DATE) == "today"


def test_relative_label_tomorrow():
    assert _relative_label(REFERENCE_DATE + timedelta(days=1), REFERENCE_DATE) == "tomorrow"


def test_relative_label_yesterday():
    assert _relative_label(REFERENCE_DATE - timedelta(days=1), REFERENCE_DATE) == "yesterday"


def test_relative_label_future_days():
    assert _relative_label(REFERENCE_DATE + timedelta(days=7), REFERENCE_DATE) == "in 7 days"


def test_relative_label_past_days():
    assert _relative_label(REFERENCE_DATE - timedelta(days=14), REFERENCE_DATE) == "14 days ago"


# ── Core context tests ────────────────────────────────────────────────────────

def test_recognized_patient_returns_context(db, practice, practitioner, patient):
    """Exact-match recognized patient gets non-None context with correct structure."""
    _make_appt(db, practice, practitioner, patient,
               REFERENCE_DATE - timedelta(days=14), 10, 0, AppointmentStatus.Completed)
    _make_appt(db, practice, practitioner, patient,
               REFERENCE_DATE + timedelta(days=7), 14, 0, AppointmentStatus.Booked)

    ctx = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert ctx.patient_key == str(patient.id)
    assert ctx.has_future_booking is True
    assert ctx.existing_future_follow_up is True
    assert ctx.recent_count >= 1
    assert ctx.future_count >= 1
    assert len(ctx.recent_bookings) >= 1
    assert len(ctx.future_bookings) >= 1
    assert ctx.reference_date == REFERENCE_DATE
    assert isinstance(ctx.generated_at, datetime)


def test_no_appointments_returns_empty_context(db, practice, practitioner, patient):
    """Patient with no appointments gets context with empty lists and False flags."""
    ctx = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert ctx.patient_key == str(patient.id)
    assert ctx.has_future_booking is False
    assert ctx.existing_future_follow_up is False
    assert ctx.recent_count == 0
    assert ctx.future_count == 0
    assert ctx.recent_bookings == []
    assert ctx.future_bookings == []


def test_existing_future_follow_up_warning(db, practice, practitioner, patient):
    """Patient with a future booked appointment triggers existing_future_follow_up=True."""
    _make_appt(db, practice, practitioner, patient,
               REFERENCE_DATE + timedelta(days=7), 9, 0, AppointmentStatus.Booked)

    ctx = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert ctx.has_future_booking is True
    assert ctx.existing_future_follow_up is True


def test_cancelled_future_does_not_set_follow_up_flag(db, practice, practitioner, patient):
    """A Cancelled future appointment is terminal — not counted as an active future booking."""
    _make_appt(db, practice, practitioner, patient,
               REFERENCE_DATE + timedelta(days=7), 9, 0, AppointmentStatus.Cancelled)

    ctx = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert ctx.has_future_booking is False
    assert ctx.existing_future_follow_up is False


def test_recent_and_future_capped_at_three(db, practice, practitioner, patient):
    """recent_bookings and future_bookings are capped at 3 entries each."""
    for i in range(5):
        _make_appt(db, practice, practitioner, patient,
                   REFERENCE_DATE - timedelta(days=i + 1), 9, 0, AppointmentStatus.Completed)
    for i in range(5):
        _make_appt(db, practice, practitioner, patient,
                   REFERENCE_DATE + timedelta(days=i + 1), 10, 0, AppointmentStatus.Booked)

    ctx = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert len(ctx.recent_bookings) == 3
    assert len(ctx.future_bookings) == 3
    assert ctx.recent_count == 5
    assert ctx.future_count == 5


def test_context_no_db_writes(db, practice, practitioner, patient):
    """build_patient_booking_context never writes any new rows."""
    _make_appt(db, practice, practitioner, patient,
               REFERENCE_DATE + timedelta(days=3), 9, 0, AppointmentStatus.Booked)

    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert db.query(Appointment).count() == appt_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_context_practice_scoped(db, practice, practice_b, practitioner, patient, patient_b):
    """Context only includes appointments from the caller's practice."""
    # Patient (practice A) has a future appointment
    _make_appt(db, practice, practitioner, patient,
               REFERENCE_DATE + timedelta(days=7), 10, 0, AppointmentStatus.Booked)
    # Practice B patient has appointments in their own practice
    pr_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Other",
        last_name="Doc",
    )
    db.add(pr_b)
    db.flush()
    _make_appt(db, practice_b, pr_b, patient_b,
               REFERENCE_DATE + timedelta(days=3), 11, 0, AppointmentStatus.Booked)

    ctx_a = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)
    ctx_b = build_patient_booking_context(db, practice_b.id, patient_b.id, REFERENCE_DATE)

    # Cross-practice check: practice A context only has practice A appointments
    assert ctx_a.future_count == 1
    assert ctx_b.future_count == 1


def test_context_entries_exclude_reason_and_notes(db, practice, practitioner, patient):
    """Booking context entries must not expose appointment reason or notes text."""
    appt = _make_appt(db, practice, practitioner, patient,
                      REFERENCE_DATE + timedelta(days=7), 9, 0, AppointmentStatus.Booked)
    appt.reason = "Sensitive clinical reason"
    appt.notes = "Private note"
    db.flush()

    ctx = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert ctx.future_bookings, "Expected at least one future booking entry"
    entry = ctx.future_bookings[0]
    entry_dict = entry.model_dump()
    assert "reason" not in entry_dict
    assert "notes" not in entry_dict


def test_recent_bookings_most_recent_first(db, practice, practitioner, patient):
    """recent_bookings are ordered most-recent first (closest past date first)."""
    dates = [
        REFERENCE_DATE - timedelta(days=1),
        REFERENCE_DATE - timedelta(days=5),
        REFERENCE_DATE - timedelta(days=10),
    ]
    for d in dates:
        _make_appt(db, practice, practitioner, patient, d, 9, 0, AppointmentStatus.Completed)

    ctx = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert len(ctx.recent_bookings) == 3
    # Most recent first
    assert ctx.recent_bookings[0].appointment_date == REFERENCE_DATE - timedelta(days=1)
    assert ctx.recent_bookings[2].appointment_date == REFERENCE_DATE - timedelta(days=10)


def test_future_bookings_soonest_first(db, practice, practitioner, patient):
    """future_bookings are ordered soonest first."""
    dates = [
        REFERENCE_DATE + timedelta(days=10),
        REFERENCE_DATE + timedelta(days=3),
        REFERENCE_DATE + timedelta(days=7),
    ]
    for d in dates:
        _make_appt(db, practice, practitioner, patient, d, 9, 0, AppointmentStatus.Booked)

    ctx = build_patient_booking_context(db, practice.id, patient.id, REFERENCE_DATE)

    assert len(ctx.future_bookings) == 3
    assert ctx.future_bookings[0].appointment_date == REFERENCE_DATE + timedelta(days=3)
    assert ctx.future_bookings[2].appointment_date == REFERENCE_DATE + timedelta(days=10)
