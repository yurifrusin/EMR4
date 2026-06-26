"""
POST /api/v1/appointments/proposals/slot-search — non-mutating slot-search contract.

Proves:
- 401 when unauthenticated
- 404 for cross-practice practitioner
- candidates are earliest-first with correct duration and tz-aware times
- blocking appointment removes overlapping candidates; Cancelled/NoShow/DNA do not
- break overlap surfaces a per-candidate warning but still offers the candidate
- missing duration + no appointment type -> autonomy_tier=blocked, empty candidates
- invalid/oversized date range -> 422 (Pydantic validation)
- location filtering: conflict at location A does not block candidates at location B
- a day with no schedule yields no candidates for that day
- NON-MUTATING proof: appointment row count and audit-log row count identical before/after
"""
from datetime import date, datetime, time, timezone, timedelta

import pytest

from app.models.appointments import (
    Appointment, AppointmentAuditLog, AppointmentStatus, AppointmentType,
    BookingChannel,
)
from app.models.diary import DiaryBreak, DiaryColumn, DiaryTemplate
from app.models.tenancy import PracticeLocation
from tests.conftest import make_token

SEARCH_URL = "/api/v1/appointments/proposals/slot-search"

# Deterministic test date: a Monday with no ambiguity around DST
MONDAY = date(2026, 6, 22)
TUESDAY = date(2026, 6, 23)


# ─── helpers ─────────────────────────────────────────────────────────────────

def _search(client, token, body: dict):
    return client.post(
        SEARCH_URL,
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def _base_body(practitioner) -> dict:
    return {
        "practitioner_id": str(practitioner.id),
        "date_from": MONDAY.isoformat(),
        "duration_minutes": 15,
    }


def _make_appt(db, practice, practitioner, patient, appt_date, hour, minute, duration, status=AppointmentStatus.Booked):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(appt_date, time(hour, minute), tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(hour, minute),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


# ─── auth / access ────────────────────────────────────────────────────────────

def test_unauthenticated_is_401(client, practitioner):
    resp = client.post(SEARCH_URL, json={
        "practitioner_id": str(practitioner.id),
        "date_from": MONDAY.isoformat(),
        "duration_minutes": 15,
    })
    assert resp.status_code == 401


def test_cross_practice_practitioner_is_404(client, db, practice_b, gp_user_b, practitioner, schedule):
    token = make_token(gp_user_b)
    resp = _search(client, token, {
        "practitioner_id": str(practitioner.id),  # belongs to practice A
        "date_from": MONDAY.isoformat(),
        "duration_minutes": 15,
    })
    assert resp.status_code == 404


# ─── basic candidate generation ──────────────────────────────────────────────

def test_candidates_earliest_first(client, gp_user, practitioner, schedule):
    token = make_token(gp_user)
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "execute_with_report"
    assert data["requires_confirmation"] is False
    assert data["intent"] == "search_slots"
    assert data["resolved_duration_minutes"] == 15

    starts = [c["start_time_local"] for c in data["candidates"]]
    assert starts == sorted(starts), "candidates must be earliest-first"
    assert data["candidates"][0]["duration_minutes"] == 15


def test_candidate_start_times_are_tz_aware(client, gp_user, practitioner, schedule):
    token = make_token(gp_user)
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200
    for c in resp.json()["candidates"]:
        # tz-aware ISO string includes offset or Z
        assert "+" in c["start_time"] or c["start_time"].endswith("Z"), (
            f"start_time not tz-aware: {c['start_time']}"
        )


def test_limit_caps_candidate_count(client, gp_user, practitioner, schedule):
    token = make_token(gp_user)
    body = {**_base_body(practitioner), "limit": 3}
    resp = _search(client, token, body)
    assert resp.status_code == 200
    assert len(resp.json()["candidates"]) <= 3


# ─── conflict filtering ───────────────────────────────────────────────────────

def test_booked_appointment_removes_overlapping_candidates(
    client, db, gp_user, practice, practitioner, patient, schedule
):
    _make_appt(db, practice, practitioner, patient, MONDAY, 9, 0, 15)
    db.commit()

    token = make_token(gp_user)
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200
    starts_local = {c["start_time_local"] for c in resp.json()["candidates"]}
    assert "09:00:00" not in starts_local, "09:00 is booked — must not appear as a candidate"


def test_30min_booking_removes_two_slots_from_candidates(
    client, db, gp_user, practice, practitioner, patient, schedule
):
    _make_appt(db, practice, practitioner, patient, MONDAY, 9, 0, 30)
    db.commit()

    token = make_token(gp_user)
    resp = _search(client, token, {**_base_body(practitioner), "duration_minutes": 15})
    assert resp.status_code == 200
    starts_local = {c["start_time_local"] for c in resp.json()["candidates"]}
    assert "09:00:00" not in starts_local
    assert "09:15:00" not in starts_local
    assert "09:30:00" in starts_local


def test_cancelled_appointment_does_not_remove_candidate(
    client, db, gp_user, practice, practitioner, patient, schedule
):
    _make_appt(db, practice, practitioner, patient, MONDAY, 9, 0, 15, status=AppointmentStatus.Cancelled)
    db.commit()

    token = make_token(gp_user)
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200
    starts_local = {c["start_time_local"] for c in resp.json()["candidates"]}
    assert "09:00:00" in starts_local, "Cancelled booking must not block the slot"


def test_noshow_does_not_remove_candidate(
    client, db, gp_user, practice, practitioner, patient, schedule
):
    _make_appt(db, practice, practitioner, patient, MONDAY, 9, 0, 15, status=AppointmentStatus.NoShow)
    db.commit()

    token = make_token(gp_user)
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200
    starts_local = {c["start_time_local"] for c in resp.json()["candidates"]}
    assert "09:00:00" in starts_local


def test_dna_does_not_remove_candidate(
    client, db, gp_user, practice, practitioner, patient, schedule
):
    _make_appt(db, practice, practitioner, patient, MONDAY, 9, 0, 15, status=AppointmentStatus.DNA)
    db.commit()

    token = make_token(gp_user)
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200
    starts_local = {c["start_time_local"] for c in resp.json()["candidates"]}
    assert "09:00:00" in starts_local


# ─── break overlap warning ────────────────────────────────────────────────────

@pytest.fixture()
def diary_with_morning_break(db, practice, practitioner):
    tmpl = DiaryTemplate(
        practice_id=practice.id,
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
    )
    db.add(tmpl)
    db.flush()
    col = DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        practitioner_id=practitioner.id,
        room_label="Dr Shera",
        display_order=1,
    )
    db.add(col)
    db.flush()
    brk = DiaryBreak(
        column_id=col.id,
        label="Morning Tea",
        from_time=time(10, 30),
        to_time=time(10, 45),
        display_order=1,
    )
    db.add(brk)
    db.flush()
    return tmpl


def test_break_overlap_surfaces_warning_but_candidate_still_offered(
    client, gp_user, practitioner, schedule, diary_with_morning_break
):
    token = make_token(gp_user)
    resp = _search(client, token, {**_base_body(practitioner), "duration_minutes": 15})
    assert resp.status_code == 200
    data = resp.json()
    candidates = {c["start_time_local"]: c for c in data["candidates"]}
    assert "10:30:00" in candidates, "Break-overlap slot must still appear as a candidate"
    warnings = candidates["10:30:00"]["warnings"]
    assert any(w["code"] == "break_overlap" for w in warnings)


# ─── missing / invalid constraints ──────────────────────────────────────────

def test_missing_duration_and_no_type_returns_blocked(client, gp_user, practitioner, schedule):
    token = make_token(gp_user)
    resp = _search(client, token, {
        "practitioner_id": str(practitioner.id),
        "date_from": MONDAY.isoformat(),
        # no duration_minutes, no appointment_type_id
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["candidates"] == []
    assert any(b["code"] == "missing_duration" for b in data["blocks"])


def test_appointment_type_default_duration_used_when_no_explicit_duration(
    client, db, gp_user, practice, practitioner, schedule
):
    appt_type = AppointmentType(
        practice_id=practice.id,
        name="Long Consult",
        default_duration=30,
    )
    db.add(appt_type)
    db.flush()

    token = make_token(gp_user)
    resp = _search(client, token, {
        "practitioner_id": str(practitioner.id),
        "date_from": MONDAY.isoformat(),
        "appointment_type_id": str(appt_type.id),
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["resolved_duration_minutes"] == 30
    assert all(c["duration_minutes"] == 30 for c in data["candidates"])


def test_date_to_before_date_from_is_422(client, gp_user, practitioner, schedule):
    token = make_token(gp_user)
    resp = _search(client, token, {
        "practitioner_id": str(practitioner.id),
        "date_from": TUESDAY.isoformat(),
        "date_to": MONDAY.isoformat(),
        "duration_minutes": 15,
    })
    assert resp.status_code == 422


def test_date_range_exceeding_14_days_is_422(client, gp_user, practitioner, schedule):
    token = make_token(gp_user)
    resp = _search(client, token, {
        "practitioner_id": str(practitioner.id),
        "date_from": MONDAY.isoformat(),
        "date_to": (MONDAY + timedelta(days=14)).isoformat(),  # 15-day range
        "duration_minutes": 15,
    })
    assert resp.status_code == 422


# ─── time-of-day window ───────────────────────────────────────────────────────

def test_earliest_time_filters_candidates(client, gp_user, practitioner, schedule):
    token = make_token(gp_user)
    resp = _search(client, token, {**_base_body(practitioner), "earliest_time": "10:00:00"})
    assert resp.status_code == 200
    for c in resp.json()["candidates"]:
        assert c["start_time_local"] >= "10:00:00"


def test_latest_time_filters_candidates(client, gp_user, practitioner, schedule):
    token = make_token(gp_user)
    resp = _search(client, token, {**_base_body(practitioner), "latest_time": "11:00:00"})
    assert resp.status_code == 200
    for c in resp.json()["candidates"]:
        assert c["start_time_local"] < "11:00:00"


# ─── multi-day range ──────────────────────────────────────────────────────────

def test_no_schedule_day_yields_no_candidates_for_that_day(
    client, db, gp_user, practitioner
):
    """Schedule only for TUESDAY — MONDAY must yield zero candidates."""
    from app.models.appointments import PractitionerSchedule
    db.add(PractitionerSchedule(
        practitioner_id=practitioner.id,
        day_of_week=TUESDAY.weekday(),
        start_time=time(9, 0),
        end_time=time(17, 0),
        slot_duration_minutes=15,
    ))
    db.flush()

    token = make_token(gp_user)
    resp = _search(client, token, {
        "practitioner_id": str(practitioner.id),
        "date_from": MONDAY.isoformat(),
        "date_to": TUESDAY.isoformat(),
        "duration_minutes": 15,
    })
    assert resp.status_code == 200
    candidates = resp.json()["candidates"]
    monday_candidates = [c for c in candidates if c["appointment_date"] == MONDAY.isoformat()]
    tuesday_candidates = [c for c in candidates if c["appointment_date"] == TUESDAY.isoformat()]
    assert monday_candidates == [], "No schedule on Monday — must yield no candidates"
    assert tuesday_candidates, "Tuesday has a schedule — must yield candidates"


# ─── location filtering ───────────────────────────────────────────────────────

def test_conflict_at_other_location_does_not_block_candidates(
    client, db, gp_user, practice, practitioner, patient, schedule
):
    loc_a = PracticeLocation(practice_id=practice.id, name="Site A", is_active=True)
    loc_b = PracticeLocation(practice_id=practice.id, name="Site B", is_active=True)
    db.add_all([loc_a, loc_b])
    db.flush()

    # Book at loc_a
    _make_appt(db, practice, practitioner, patient, MONDAY, 9, 0, 15)
    db.query(Appointment).filter(
        Appointment.practitioner_id == practitioner.id
    ).update({"location_id": loc_a.id})
    db.flush()
    db.commit()

    token = make_token(gp_user)
    # Search at loc_b — conflict at loc_a must not block loc_b candidates
    resp = _search(client, token, {**_base_body(practitioner), "location_id": str(loc_b.id)})
    assert resp.status_code == 200
    starts_local = {c["start_time_local"] for c in resp.json()["candidates"]}
    assert "09:00:00" in starts_local, "Conflict at site A must not block site B"


# ─── non-mutating proof ───────────────────────────────────────────────────────

def test_slot_search_writes_no_appointments_and_no_audit_rows(
    client, db, gp_user, practitioner, patient, practice, schedule
):
    # Pre-count
    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    token = make_token(gp_user)
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200

    db.expire_all()  # force fresh read
    appt_after = db.query(Appointment).count()
    audit_after = db.query(AppointmentAuditLog).count()

    assert appt_after == appt_before, "slot search must not create appointment rows"
    assert audit_after == audit_before, "slot search must not create audit rows"
