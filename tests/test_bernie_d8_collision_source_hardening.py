"""Sprint D8 patient collision source hardening --- verification lane.

Probes edge cases the D6 closeout flagged:
1.  Cap overflow: has_existing_booking_on_requested_day only checks
    context.future_bookings (capped at 3 entries).  Patients with
    4+ future bookings where the collision is entry #4+ are invisible to the
    check, producing a false negative.
2.  Source-appointment self-exclusion: reschedule/extend flows do not exclude
    the appointment being edited, producing a false-positive collision warning.
3.  Genuine same-day collision: the warning is still correctly emitted when a
    different appointment exists on the requested day.

No production code changes.  No modifications to existing test files.
Uses _fake_context (pure unit) for direct function-level assertions and
route-level tests via TestClient with the fake interpreter.

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

# July 2026 calendar (weekdays Mon-Fri, schedule fixture covers 09:00-17:00):
#   Jul 13 = Mon, Jul 14 = Tue, Jul 15 = Wed,
#   Jul 16 = Thu, Jul 17 = Fri
D8_REF_DATE_OBJ = date(2026, 7, 13)  # Monday
D8_REF_DATE_STR = "2026-07-13"
D8_CLINIC_NOW = datetime(2026, 7, 13, 9, 0, tzinfo=timezone.utc)

D8_COLLISION_DATE_OBJ = date(2026, 7, 17)  # Friday - entry #4 for cap test
D8_COLLISION_DATE_STR = "2026-07-17"

D8_FILLER_1_OBJ = date(2026, 7, 14)  # Tue
D8_FILLER_2_OBJ = date(2026, 7, 15)  # Wed
D8_FILLER_3_OBJ = date(2026, 7, 16)  # Thu

D8_SAME_DAY_OBJ = date(2026, 7, 14)  # Tue
D8_SAME_DAY_STR = "2026-07-14"


def _make_appt(db, practice, practitioner, patient, appt_date, h, m, status, duration=15):
    appt = appointments_router.Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime(
            appt_date.year, appt_date.month, appt_date.day, h, m,
            tzinfo=timezone.utc,
        ),
        appointment_date=appt_date,
        start_time_local=time(h, m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def _fake_context(future_dates):
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
        reference_date=D8_REF_DATE_OBJ,
        generated_at=datetime.now(tz=timezone.utc),
    )


# ==== 1. Cap overflow - pure unit ===========================================

def test_cap_overflow_skips_collision_beyond_three_entries():
    """has_existing_booking_on_requested_day returns False when the target
    date is not in the capped 3-entry future_bookings list."""
    ctx = _fake_context([D8_FILLER_1_OBJ, D8_FILLER_2_OBJ, D8_FILLER_3_OBJ])
    assert has_existing_booking_on_requested_day(ctx, D8_COLLISION_DATE_OBJ) is False
    assert ctx.future_count == 3


# ==== 2. Cap overflow - route-level =========================================

def test_cap_overflow_interpret_route_misses_fourth_booking(
    client, db, gp_user, practice, patient, practitioner, monkeypatch,
):
    """4 DB appointments, entry #4 on the requested day -> warning IS now emitted
    because the direct DB lookup bypasses the compact-context cap."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D8_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    _make_appt(db, practice, practitioner, patient, D8_FILLER_1_OBJ, 9, 0, AppointmentStatus.Booked)
    _make_appt(db, practice, practitioner, patient, D8_FILLER_2_OBJ, 10, 0, AppointmentStatus.Booked)
    _make_appt(db, practice, practitioner, patient, D8_FILLER_3_OBJ, 11, 0, AppointmentStatus.Booked)
    _make_appt(db, practice, practitioner, patient, D8_COLLISION_DATE_OBJ, 14, 0, AppointmentStatus.Booked)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                f"date_from:{D8_COLLISION_DATE_STR} duration:15"
            ),
            "reference_date": D8_REF_DATE_STR,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    ctx = data.get("patient_booking_context")
    assert ctx is not None
    assert len(ctx["future_bookings"]) == 3
    assert ctx["future_count"] == 4
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True

    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        "FIX VERIFIED: collision on entry #4 now detected by direct DB lookup."
    )


# ==== 3. Self-collision - pure unit =========================================

def test_self_collision_returns_true_for_source_appointment_date():
    """Date match returns True -- function cannot distinguish self-collision."""
    ctx = _fake_context([D8_SAME_DAY_OBJ])
    assert has_existing_booking_on_requested_day(ctx, D8_SAME_DAY_OBJ) is True


# ==== 4. Self-collision - route-level =======================================

def test_self_collision_interpret_route_emits_false_positive_warning(
    client, db, gp_user, practice, patient, practitioner, monkeypatch,
):
    """Same-day interpret request on the source appointment date triggers the
    existing_future_follow_up warning -- a false positive for reschedule/extend."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D8_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    _make_appt(db, practice, practitioner, patient, D8_SAME_DAY_OBJ, 11, 0, AppointmentStatus.Booked)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
                f"date_from:{D8_SAME_DAY_STR} duration:15"
            ),
            "reference_date": D8_REF_DATE_STR,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    ctx = data.get("patient_booking_context")
    assert ctx is not None
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True

    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        "False-positive self-collision warning emitted -- function has no "
        "source-appointment exclusion."
    )


# ==== 5. Genuine same-day collision =========================================

def test_genuine_collision_supervised_booking_emits_warning(
    client, db, gp_user, practice, patient, practitioner, schedule, monkeypatch,
):
    """Genuine same-day collision via supervised-booking route."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: D8_CLINIC_NOW.astimezone(tz),
    )
    token = make_token(gp_user)

    _make_appt(db, practice, practitioner, patient, D8_SAME_DAY_OBJ, 11, 0, AppointmentStatus.Booked)

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": D8_REF_DATE_STR,
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": D8_SAME_DAY_STR,
                "duration_minutes": "15",
            },
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    ctx = data.get("patient_booking_context")
    assert ctx is not None
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True

    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" in warning_codes, (
        "Genuine collision warning must be emitted via supervised-booking route."
    )
