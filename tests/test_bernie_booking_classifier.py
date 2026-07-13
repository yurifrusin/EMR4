"""
Exhaustive tests for the Bernie booking classifier module.

Covers:
- All four classification values (exact_duplicate, overlapping_same_patient,
  same_day_distinct, none)
- Exact-duplicate rules: both-bounds window, earliest-only, latest-only refused,
  no-temporal-evidence refused, type/location/duration matching
- Terminal-status exclusion (Completed, Cancelled, NoShow, DNA)
- Source-appointment self-exclusion
- Tenant (practice) isolation
- Interval overlap detection
- Route-level golden regression matching the live 15:00-16:30 report semantics
- No appointment/audit write on exact duplicate
- No candidates or confirm affordance on exact duplicate
- Candidates for non-duplicate stay inside normalized date/time bounds
- Existing D6/D8 source-exclusion behavior remains intact
"""

from datetime import date, datetime, time, timezone
import uuid

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.tenancy import Practitioner
from app.services.bernie_booking_classifier import (
    BookingClassification,
    BookingClassificationEvidence,
    classify_existing_booking,
)


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _make_appt(
    db,
    practice_id,
    patient_id,
    practitioner_id,
    appt_date,
    h,
    m,
    status=AppointmentStatus.Booked,
    duration=15,
    appointment_type_id=None,
    location_id=None,
):
    appt = Appointment(
        practice_id=practice_id,
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        appointment_type_id=appointment_type_id,
        location_id=location_id,
        start_time=datetime(
            appt_date.year, appt_date.month, appt_date.day, h, m, tzinfo=timezone.utc,
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


# Dates
CLASS_DATE = date(2026, 7, 15)  # Wednesday (future, has schedule)
CLASS_OTHER_DATE = date(2026, 7, 16)  # Thursday


# ─── Pure unit tests: classification enum values ──────────────────────────────

def test_classification_enum_values():
    """All four expected classification values are present."""
    assert BookingClassification.exact_duplicate.value == "exact_duplicate"
    assert BookingClassification.overlapping_same_patient.value == "overlapping_same_patient"
    assert BookingClassification.same_day_distinct.value == "same_day_distinct"
    assert BookingClassification.none.value == "none"


def test_classification_evidence_frozen():
    """BookingClassificationEvidence is frozen (immutable)."""
    ev = BookingClassificationEvidence(classification=BookingClassification.none)
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ev.classification = BookingClassification.exact_duplicate


# ─── No-matches ────────────────────────────────────────────────────────────────

def test_no_existing_appointments_returns_none(db, practice, patient, practitioner):
    """No appointments at all returns classification='none'."""
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
    )
    assert ev.classification == BookingClassification.none
    assert ev.appointment_date is None


def test_no_appointments_on_requested_date_returns_none(db, practice, patient, practitioner):
    """Appointments exist but not on the requested date returns 'none'."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_OTHER_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
    )
    assert ev.classification == BookingClassification.none


def test_different_patient_no_collision(db, practice, patient, patient_b, practitioner):
    """Different patient's appointments are not considered for this patient."""
    _make_appt(db, practice.id, patient_b.id, practitioner.id, CLASS_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
    )
    assert ev.classification == BookingClassification.none


# ─── Terminal-status exclusion ────────────────────────────────────────────────

@pytest.mark.parametrize("terminal_status", [
    AppointmentStatus.Completed,
    AppointmentStatus.Cancelled,
    AppointmentStatus.NoShow,
    AppointmentStatus.DNA,
])
def test_terminal_status_excluded(db, practice, patient, practitioner, terminal_status):
    """Terminal-status appointments are excluded from classification."""
    _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 9, 0, status=terminal_status,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
    )
    assert ev.classification == BookingClassification.none, (
        f"Terminal status {terminal_status.value} should be excluded"
    )


def test_non_terminal_status_included(db, practice, patient, practitioner):
    """Non-terminal appointments (Booked) are not excluded."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
    )
    assert ev.classification == BookingClassification.exact_duplicate, (
        "Booked appointment should be considered for classification"
    )


# ─── Tenant (practice) isolation ──────────────────────────────────────────────

def test_practice_isolation(db, practice, practice_b, patient, patient_b, practitioner):
    """Appointments in practice_b do not affect practice classification."""
    prac_b_practitioner = Practitioner(
        practice_id=practice_b.id,
        first_name="PracB",
        last_name="Doctor",
    )
    db.add(prac_b_practitioner)
    db.flush()
    _make_appt(
        db, practice_b.id, patient_b.id, prac_b_practitioner.id,
        CLASS_DATE, 9, 0,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
    )
    assert ev.classification == BookingClassification.none


# ─── Source-appointment exclusion ─────────────────────────────────────────────

def test_source_appointment_excluded(db, practice, patient, practitioner):
    """The source appointment (reschedule/extend) does not self-collide."""
    appt = _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 9, 0,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
        source_appointment_id=appt.id,
    )
    assert ev.classification == BookingClassification.none, (
        "Source appointment should self-exclude"
    )


def test_source_exclusion_other_appointment_still_detected(db, practice, patient, practitioner):
    """Source exclusion only excludes the matching appointment; other collisions remain."""
    appt_source = _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 9, 0,
    )
    appt_other = _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 10, 0,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(10, 0),
        requested_latest_time=time(11, 0),
        source_appointment_id=appt_source.id,
    )
    assert ev.classification == BookingClassification.exact_duplicate
    assert ev.start_time_local == time(10, 0)


# ─── Missing temporal evidence cannot claim exact duplicate ──────────────────

def test_no_temporal_evidence_not_exact(db, practice, patient, practitioner):
    """No temporal evidence means classification cannot be exact_duplicate."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
    )
    assert ev.classification != BookingClassification.exact_duplicate


def test_latest_only_not_exact(db, practice, patient, practitioner):
    """Latest-time without earliest-time cannot be exact duplicate."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_latest_time=time(10, 0),
    )
    assert ev.classification != BookingClassification.exact_duplicate


# ─── Exact duplicate with both bounds ────────────────────────────────────────

def test_exact_duplicate_both_bounds(db, practice, patient, practitioner):
    """Existing start inside [earliest, latest) is exact duplicate."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 30)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
    )
    assert ev.classification == BookingClassification.exact_duplicate
    assert ev.appointment_date == CLASS_DATE
    assert ev.start_time_local == time(9, 30)
    assert ev.practitioner_display


def test_exact_duplicate_start_equal_earliest(db, practice, patient, practitioner):
    """Existing start exactly at earliest bound qualifies."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
    )
    assert ev.classification == BookingClassification.exact_duplicate


def test_exact_duplicate_start_equal_latest_not_included(db, practice, patient, practitioner):
    """Existing start exactly at latest bound is NOT in half-open window."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 10, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
    )
    # It's same_day_distinct because start == latest, not inside [earliest, latest)
    assert ev.classification != BookingClassification.exact_duplicate


def test_explicit_exact_equal_bounds_are_point_evidence(
    db, practice, patient, practitioner
):
    """LC1 exact semantics treat equal bounds as a point, not [t, t)."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 15, 0)
    ev = classify_existing_booking(
        db,
        practice.id,
        patient.id,
        CLASS_DATE,
        practitioner.id,
        requested_earliest_time=time(15, 0),
        requested_latest_time=time(15, 0),
        requested_temporal_relation="exact",
    )
    assert ev.classification == BookingClassification.exact_duplicate


@pytest.mark.parametrize(
    "relation",
    ["not_before", "not_after", "interval", "approximate", "unspecified"],
)
def test_explicit_non_exact_relation_cannot_grant_duplicate_authority(
    db, practice, patient, practitioner, relation
):
    """An appointment inside a preference/window is not an exact request."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 15, 0)
    ev = classify_existing_booking(
        db,
        practice.id,
        patient.id,
        CLASS_DATE,
        practitioner.id,
        requested_earliest_time=time(14, 30),
        requested_latest_time=time(15, 30),
        requested_temporal_relation=relation,
    )
    assert ev.classification != BookingClassification.exact_duplicate


# ─── Exact duplicate with earliest-only ──────────────────────────────────────

def test_exact_duplicate_earliest_only(db, practice, patient, practitioner):
    """Earliest-only: existing start must equal earliest exactly."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 30)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 30),
    )
    assert ev.classification == BookingClassification.exact_duplicate


def test_earliest_only_not_matching_not_exact(db, practice, patient, practitioner):
    """Earliest-only: if existing start differs, it is NOT exact duplicate."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 30),
    )
    assert ev.classification != BookingClassification.exact_duplicate


# ─── Exact duplicate with matching type / location / duration ────────────────

def test_exact_duplicate_with_matching_type(db, practice, patient, practitioner, appt_type):
    """Matching appointment type contributes to exact duplicate."""
    _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 9, 0,
        appointment_type_id=appt_type.id,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
        requested_appointment_type_id=appt_type.id,
    )
    assert ev.classification == BookingClassification.exact_duplicate


def test_type_mismatch_not_exact(db, practice, patient, practitioner, appt_type):
    """Mismatched type prevents exact duplicate."""
    other_type_id = uuid.uuid4()
    _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 9, 0,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
        requested_appointment_type_id=other_type_id,
    )
    assert ev.classification != BookingClassification.exact_duplicate


def test_duration_mismatch_not_exact(db, practice, patient, practitioner):
    """Mismatched duration prevents exact duplicate when duration supplied."""
    _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 9, 0, duration=30,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
        requested_duration_minutes=15,
    )
    assert ev.classification != BookingClassification.exact_duplicate


# ─── Different practitioner ─────────────────────────────────────────────────

def test_different_practitioner_not_exact(db, practice, patient, practitioner):
    """Different practitioner means not exact duplicate."""
    other_prac = Practitioner(
        practice_id=practice.id,
        first_name="Other",
        last_name="Doctor",
    )
    db.add(other_prac)
    db.flush()
    _make_appt(
        db, practice.id, patient.id, other_prac.id,
        CLASS_DATE, 9, 0,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
    )
    assert ev.classification != BookingClassification.exact_duplicate


# ─── Interval overlap detection ─────────────────────────────────────────────

def test_overlapping_same_practitioner(db, practice, patient, practitioner):
    """Same-practitioner appointment overlapping the requested window."""
    # Existing at 09:45 for 30 min ends at 10:15, overlapping requested [10:00, 11:00)
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 45, duration=30)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(10, 0),
        requested_latest_time=time(11, 0),
        requested_duration_minutes=30,
    )
    assert ev.classification == BookingClassification.overlapping_same_patient


def test_overlapping_different_practitioner(db, practice, patient, practitioner):
    """Different-practitioner appointment within the requested window."""
    other_prac = Practitioner(
        practice_id=practice.id,
        first_name="Other",
        last_name="Doctor",
    )
    db.add(other_prac)
    db.flush()
    _make_appt(
        db, practice.id, patient.id, other_prac.id,
        CLASS_DATE, 10, 15,
    )
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(10, 0),
        requested_latest_time=time(11, 0),
    )
    assert ev.classification == BookingClassification.overlapping_same_patient


# ─── Same-day-distinct ──────────────────────────────────────────────────────

def test_same_day_distinct_before_window(db, practice, patient, practitioner):
    """Existing appointment before requested window is same_day_distinct."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(10, 0),
        requested_latest_time=time(11, 0),
    )
    assert ev.classification == BookingClassification.same_day_distinct


def test_same_day_distinct_after_window(db, practice, patient, practitioner):
    """Existing appointment after requested window is same_day_distinct."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 14, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
        requested_earliest_time=time(9, 0),
        requested_latest_time=time(10, 0),
    )
    assert ev.classification == BookingClassification.same_day_distinct


def test_same_day_distinct_no_time_bounds(db, practice, patient, practitioner):
    """Without time bounds, an existing same-day appointment is same_day_distinct."""
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    ev = classify_existing_booking(
        db, practice.id, patient.id, CLASS_DATE, practitioner.id,
    )
    assert ev.classification == BookingClassification.same_day_distinct


# ─── Route-level: exact duplicate produces existing_booking_found result ──────

SUPERVISED_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
CLASS_REF_DATE = date(2026, 7, 15)


def test_tomorrow_at_3pm_interpret_then_duplicate_has_no_second_write(
    client,
    db,
    practice,
    patient,
    practitioner,
    schedule,
    monkeypatch,
):
    """The real LC1 wording traverses interpreter and supervised policy."""
    from app.config import settings
    from app.models.appointments import AppointmentAuditLog
    from app.models.tenancy import User, UserRole
    from app.services.auth_service import hash_password
    from tests.conftest import make_token

    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    user = User(
        practice_id=practice.id,
        email="lc1-exact-time@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.Receptionist,
    )
    db.add(user)
    db.flush()
    token = make_token(user)
    _make_appt(
        db,
        practice.id,
        patient.id,
        practitioner.id,
        CLASS_DATE,
        15,
        0,
        duration=15,
    )
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()
    auth = {"Authorization": f"Bearer {token}"}

    interpreted = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"Make an appointment for patient_id:{patient.id} with "
                f"practitioner_id:{practitioner.id} tomorrow at 3pm duration:15"
            ),
            "reference_date": "2026-07-14",
        },
        headers=auth,
    )
    assert interpreted.status_code == 200, interpreted.text
    command = interpreted.json()["command_candidate"]
    assert command["earliest_time"] == "15:00"
    assert command["latest_time"] == "15:00"
    assert command["temporal_relation"] == "exact"

    supervised = client.post(
        SUPERVISED_URL,
        json={
            "command": command,
            "reference_date": "2026-07-14",
            "patient_id": str(patient.id),
        },
        headers=auth,
    )
    assert supervised.status_code == 200, supervised.text
    assert supervised.json()["result"] == "existing_booking_found"
    assert supervised.json()["requires_confirmation"] is False
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_exact_duplicate_route_response(
    client, db, practice, patient, practitioner, schedule, appt_type,
):
    """Exact duplicate at route level returns existing_booking_found result with no candidates."""
    from tests.conftest import make_token
    from app.models.tenancy import User, UserRole
    from app.services.auth_service import hash_password

    user = User(
        practice_id=practice.id,
        email="reception@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.Receptionist,
    )
    db.add(user)
    db.flush()
    token = make_token(user)

    # Create an existing appointment
    _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 10, 0, status=AppointmentStatus.Booked,
        appointment_type_id=appt_type.id,
    )

    response = client.post(
        SUPERVISED_URL,
        json={
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": CLASS_DATE.isoformat(),
                "date_to": CLASS_DATE.isoformat(),
                "earliest_time": "10:00",
                "latest_time": "11:00",
                "duration_minutes": 15,
                "appointment_type_id": str(appt_type.id),
                "patient_id": str(patient.id),
            },
            "reference_date": CLASS_REF_DATE.isoformat(),
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "existing_booking_found"
    assert data["safe"] is True
    assert data["requires_confirmation"] is False
    assert data["outcome"]["family"] == "advisory"
    assert data["outcome"]["session_state"] == "no_slot"
    assert data["outcome"]["is_terminal"] is False
    # No candidates, no search proposal, no selection proposal
    assert data.get("search_proposal") is None
    assert data.get("selection_proposal") is None
    # No confirm endpoint, no confirm payload
    staff_review = data.get("staff_review", {})
    assert staff_review.get("confirm_endpoint") is None
    assert staff_review.get("confirm_payload") is None
    # Has suggestions
    assert len(data.get("suggestions", [])) == 2
    suggestion_kinds = {s["kind"] for s in data["suggestions"]}
    assert "widen_time_window" in suggestion_kinds
    assert "next_available_day" in suggestion_kinds
    suggestion_by_kind = {s["kind"]: s for s in data["suggestions"]}
    assert suggestion_by_kind["widen_time_window"]["params"] == {
        "earliest_time": None,
        "latest_time": None,
    }
    assert suggestion_by_kind["next_available_day"]["params"] == {
        "date_from": "2026-07-16",
        "date_to": "2026-07-16",
    }
    # Has existing_booking summary
    assert data.get("existing_booking") is not None
    assert data["existing_booking"]["appointment_date"] == CLASS_DATE.isoformat()
    assert data["existing_booking"]["status"] == "Booked"
    assert data["existing_booking"]["start_time_local"] == "10:00:00"
    assert "No new booking was created" in data["summary"]


def test_exact_duplicate_no_write(
    client, db, practice, patient, practitioner, schedule, appt_type,
):
    """Exact duplicate route call does not create a new appointment."""
    from tests.conftest import make_token
    from app.models.tenancy import User, UserRole
    from app.services.auth_service import hash_password
    from app.models.appointments import Appointment as ApptModel, AppointmentAuditLog

    user = User(
        practice_id=practice.id,
        email="reception2@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.Receptionist,
    )
    db.add(user)
    db.flush()
    token = make_token(user)

    _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 10, 0, status=AppointmentStatus.Booked,
        appointment_type_id=appt_type.id,
    )

    pre_count = db.query(ApptModel).count()
    pre_audit = db.query(AppointmentAuditLog).count()

    response = client.post(
        SUPERVISED_URL,
        json={
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": CLASS_DATE.isoformat(),
                "date_to": CLASS_DATE.isoformat(),
                "earliest_time": "10:00",
                "latest_time": "11:00",
                "duration_minutes": 15,
                "appointment_type_id": str(appt_type.id),
                "patient_id": str(patient.id),
            },
            "reference_date": CLASS_REF_DATE.isoformat(),
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "existing_booking_found"

    # No new appointment or audit written
    assert db.query(ApptModel).count() == pre_count
    assert db.query(AppointmentAuditLog).count() == pre_audit


# ─── Non-duplicate requests still produce candidates ──────────────────────────

def test_non_duplicate_returns_candidates(
    client, db, practice, patient, practitioner, schedule, appt_type,
):
    """Non-duplicate requests still produce slot candidates within normalized bounds."""
    from tests.conftest import make_token
    from app.models.tenancy import User, UserRole
    from app.services.auth_service import hash_password

    user = User(
        practice_id=practice.id,
        email="reception3@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.Receptionist,
    )
    db.add(user)
    db.flush()
    token = make_token(user)

    # No existing appointments on this date — should return candidates
    response = client.post(
        SUPERVISED_URL,
        json={
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": CLASS_DATE.isoformat(),
                "date_to": CLASS_DATE.isoformat(),
                "earliest_time": "10:00",
                "latest_time": "11:00",
                "duration_minutes": 15,
                "patient_id": str(patient.id),
            },
            "reference_date": CLASS_REF_DATE.isoformat(),
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    # Should have candidates (not existing_booking_found)
    assert data["result"] in ("candidate_selection_required",)
    assert len(data.get("search_proposal", {}).get("candidates", [])) > 0
    # All candidates inside the requested bounds
    if data.get("search_proposal") and data["search_proposal"].get("candidates"):
        for c in data["search_proposal"]["candidates"]:
            assert c["start_time_local"] >= "10:00:00"
            assert c["start_time_local"] < "11:00:00"
            assert c["appointment_date"] == CLASS_DATE.isoformat()


# ─── Existing D6/D8 source-exclusion behavior remains intact ─────────────────

def test_d6_has_existing_booking_on_requested_day():
    """Re-test D6 pure assertions on has_existing_booking_on_requested_day."""
    from app.schemas.appointments import (
        BernieBookingContextEntry, BerniePatientBookingContext,
    )
    from app.services.bernie_patient_context import has_existing_booking_on_requested_day

    ctx = BerniePatientBookingContext(
        patient_key=str(uuid.uuid4()),
        future_bookings=[
            BernieBookingContextEntry(
                appointment_date=date(2026, 7, 15),
                relative_label="in 2 days",
                status="Booked",
                practitioner_display="Dr Test",
                duration_minutes=15,
            ),
        ],
        recent_bookings=[],
        has_future_booking=True,
        existing_future_follow_up=True,
        recent_count=0,
        future_count=1,
        reference_date=date(2026, 7, 13),
        generated_at=datetime.now(timezone.utc),
    )
    assert has_existing_booking_on_requested_day(ctx, date(2026, 7, 15)) is True
    assert has_existing_booking_on_requested_day(ctx, date(2026, 7, 13)) is False
    assert has_existing_booking_on_requested_day(ctx, None) is False


def test_d8_patient_has_active_booking_on_date(db, practice, patient, practitioner):
    """Re-test D8 authoritative DB query for active booking."""
    from app.services.bernie_patient_context import patient_has_active_booking_on_date

    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    assert patient_has_active_booking_on_date(db, practice.id, patient.id, CLASS_DATE) is True
    assert patient_has_active_booking_on_date(db, practice.id, patient.id, CLASS_OTHER_DATE) is False


def test_d8_source_exclusion_preserved(db, practice, patient, practitioner):
    """Source appointment self-exclusion test matching D8 semantics."""
    from app.services.bernie_patient_context import patient_has_active_booking_on_date

    appt = _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 9, 0)
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, CLASS_DATE, source_appointment_id=appt.id,
    ) is False
    _make_appt(db, practice.id, patient.id, practitioner.id, CLASS_DATE, 10, 0)
    assert patient_has_active_booking_on_date(
        db, practice.id, patient.id, CLASS_DATE, source_appointment_id=appt.id,
    ) is True


# ─── Golden route regression matching live 15:00-16:30 report ────────────────

def test_golden_regression_duplicate_detected(
    client, db, practice, patient, practitioner, schedule, appt_type,
):
    """Golden route: request matching 15:00-16:30 existing booking is exact duplicate."""
    from tests.conftest import make_token
    from app.models.tenancy import User, UserRole
    from app.services.auth_service import hash_password

    user = User(
        practice_id=practice.id,
        email="reception_golden@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.Receptionist,
    )
    db.add(user)
    db.flush()
    token = make_token(user)

    # Existing booking at 15:00
    _make_appt(
        db, practice.id, patient.id, practitioner.id,
        CLASS_DATE, 15, 0, duration=30,
    )

    response = client.post(
        SUPERVISED_URL,
        json={
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": CLASS_DATE.isoformat(),
                "date_to": CLASS_DATE.isoformat(),
                "earliest_time": "15:00",
                "latest_time": "16:30",
                "duration_minutes": 30,
                "patient_id": str(patient.id),
            },
            "reference_date": CLASS_REF_DATE.isoformat(),
            "patient_id": str(patient.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "existing_booking_found", (
        f"Expected existing_booking_found, got {data['result']}"
    )
    assert data.get("search_proposal") is None
    assert len(data.get("suggestions", [])) == 2
