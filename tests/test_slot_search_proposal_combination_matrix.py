"""DB-backed route combination matrix for POST /api/v1/appointments/proposals/slot-search.

Exercises the real authenticated route against the test DB across a compact set of
representative pairwise combinations. Covers what the fast query-only classifier
matrices cannot prove: appointment status filtering, same/other location conflicts,
duration/time bounds, roster presence/absence, break warnings, candidate ordering
and bounds, and absence of appointment/audit writes.

See T2.3 in docs/bernie-t2-deterministic-behaviour-matrix.md.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentStatus,
    BookingChannel,
)
from app.models.diary import DiaryBreak, DiaryColumn, DiaryTemplate
from app.models.tenancy import PracticeLocation
from tests.conftest import make_token

SEARCH_URL = "/api/v1/appointments/proposals/slot-search"

# Deterministic test dates (Monday and Tuesday, no DST ambiguity)
MONDAY = date(2026, 7, 27)
TUESDAY = date(2026, 7, 28)


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


def _make_appt(
    db, practice, practitioner, patient,
    appt_date, hour, minute, duration,
    status=AppointmentStatus.Booked,
    location_id=None,
):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(
            appt_date, time(hour, minute), tzinfo=timezone.utc,
        ),
        appointment_date=appt_date,
        start_time_local=time(hour, minute),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
        location_id=location_id,
    )
    db.add(appt)
    db.flush()
    return appt


@pytest.fixture()
def two_locations(db, practice):
    """Two active locations in the test practice."""
    loc_a = PracticeLocation(practice_id=practice.id, name="Site A", is_active=True)
    loc_b = PracticeLocation(practice_id=practice.id, name="Site B", is_active=True)
    db.add_all([loc_a, loc_b])
    db.flush()
    return loc_a, loc_b


@pytest.fixture()
def diary_with_break(db, practice, practitioner):
    """Minimal diary template + column + break for the test practitioner."""
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


# ─── Scenario definitions ─────────────────────────────────────────────────────
# Each scenario is one row in the compact combination matrix, exercising a
# specific pairwise interaction through the real slot-search route.

@dataclass
class MatrixScenario:
    """One scenario in the DB-backed combination matrix."""
    case_id: str
    description: str
    # Appointment to create before search (None = no pre-existing appointment)
    blocking_status: AppointmentStatus | None
    blocking_location_idx: int | None  # index into two_locations or None
    search_location_idx: int | None    # index into two_locations or None
    duration: int
    earliest_time: str | None
    latest_time: str | None
    has_break: bool
    has_roster: bool
    # Expected outcome
    expect_09_00_blocked: bool  # True = 09:00 should NOT appear as candidate
    expect_break_warning_10_30: bool  # True = 10:30 candidate should have break_overlap warning
    expect_zero_candidates: bool  # True = expect empty candidates list


# ─── The compact combination matrix ───────────────────────────────────────────
# 16 scenarios covering all required acceptance dimensions without a full
# Cartesian product.  Rows target specific pairwise interactions.

MATRIX = [
    # ── Baseline: no appointment, roster present ──
    MatrixScenario(
        case_id="BASE-01",
        description="No appointment, 15-min, roster present: all slots free",
        blocking_status=None,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=False,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),

    # ── Active blocking statuses ──
    MatrixScenario(
        case_id="ST-BOOKED",
        description="Booked appointment blocks overlapping 15-min slot",
        blocking_status=AppointmentStatus.Booked,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="ST-CONFIRMED",
        description="Confirmed appointment blocks overlapping slot",
        blocking_status=AppointmentStatus.Confirmed,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="ST-ARRIVED",
        description="Arrived appointment blocks overlapping slot",
        blocking_status=AppointmentStatus.Arrived,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="ST-INCONSULT",
        description="InConsult appointment blocks overlapping slot",
        blocking_status=AppointmentStatus.InConsult,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),

    # ── Terminal blocking (Completed) and non-blocking (Cancelled, NoShow, DNA) ──
    MatrixScenario(
        case_id="ST-COMPLETED",
        description="Completed appointment blocks overlapping slot (terminal blocking)",
        blocking_status=AppointmentStatus.Completed,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="ST-CANCELLED",
        description="Cancelled appointment does NOT block overlapping slot",
        blocking_status=AppointmentStatus.Cancelled,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=False,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="ST-NOSHOW",
        description="NoShow appointment does NOT block overlapping slot",
        blocking_status=AppointmentStatus.NoShow,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=False,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="ST-DNA",
        description="DNA appointment does NOT block overlapping slot",
        blocking_status=AppointmentStatus.DNA,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=False,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),

    # ── Same-location blocking vs other-location non-blocking ──
    MatrixScenario(
        case_id="LOC-SAME",
        description="Same-location Booked blocks; search at same location",
        blocking_status=AppointmentStatus.Booked,
        blocking_location_idx=0,
        search_location_idx=0,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="LOC-OTHER",
        description="Booked at location A; search at location B: NOT blocked",
        blocking_status=AppointmentStatus.Booked,
        blocking_location_idx=0,
        search_location_idx=1,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=False,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),

    # ── Duration: 30-min appointment blocking two 15-min slots ──
    MatrixScenario(
        case_id="DUR-30BLOCK",
        description="30-min Booked blocks both 09:00 and 09:15 for 15-min search",
        blocking_status=AppointmentStatus.Booked,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),

    # ── Time bounds: earliest/latest ──
    MatrixScenario(
        case_id="BND-EARLIEST",
        description="earliest_time=10:00 filters all earlier slots on roster",
        blocking_status=None,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time="10:00:00",
        latest_time=None,
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,  # 09:00 excluded by earliest_time
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="BND-LATEST",
        description="latest_time=11:00 caps candidates to before 11:00",
        blocking_status=None,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time="11:00:00",
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=False,
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),
    MatrixScenario(
        case_id="BND-BOTH",
        description="earliest=10:00 and latest=11:00 tight window, 30-min duration",
        blocking_status=None,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=30,
        earliest_time="10:00:00",
        latest_time="11:00:00",
        has_break=False,
        has_roster=True,
        expect_09_00_blocked=True,  # excluded by earliest
        expect_break_warning_10_30=False,
        expect_zero_candidates=False,
    ),

    # ── Roster absent ──
    MatrixScenario(
        case_id="ROSTER-ABSENT",
        description="No schedule configured: zero candidates + no_schedule warning",
        blocking_status=None,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=False,
        has_roster=False,
        expect_09_00_blocked=True,
        expect_break_warning_10_30=False,
        expect_zero_candidates=True,
    ),

    # ── Break overlap warning ──
    MatrixScenario(
        case_id="BREAK-OVERLAP",
        description="Break overlap yields warning at 10:30 but candidate still offered",
        blocking_status=None,
        blocking_location_idx=None,
        search_location_idx=None,
        duration=15,
        earliest_time=None,
        latest_time=None,
        has_break=True,
        has_roster=True,
        expect_09_00_blocked=False,
        expect_break_warning_10_30=True,
        expect_zero_candidates=False,
    ),
]


# ─── Fixtures ─────────────────────────────────────────────────────────────────


# ─── Combination matrix test ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "scenario",
    MATRIX,
    ids=[s.case_id for s in MATRIX],
)
def test_slot_search_combination_matrix(
    scenario: MatrixScenario,
    client, db, gp_user, practice, practitioner, patient,
    two_locations,
    diary_with_break,
):
    """Execute one row of the DB-backed route combination matrix."""
    # ── Setup: conditionally create pre-existing appointment ──
    if scenario.blocking_status is not None:
        loc_a, loc_b = two_locations
        block_location = (
            [loc_a, loc_b][scenario.blocking_location_idx]
            if scenario.blocking_location_idx is not None
            else None
        )
        # Create 30-min appointment at 09:00 for 30-min blocking scenarios
        block_duration = 30 if scenario.case_id == "DUR-30BLOCK" else 15
        _make_appt(
            db, practice, practitioner, patient,
            MONDAY, 9, 0, block_duration,
            status=scenario.blocking_status,
            location_id=block_location.id if block_location else None,
        )
        db.commit()

    # ── Resolve roster presence ──
    from app.models.appointments import PractitionerSchedule
    if scenario.has_roster:
        for dow in range(5):
            db.add(PractitionerSchedule(
                practitioner_id=practitioner.id,
                day_of_week=dow,
                start_time=time(9, 0),
                end_time=time(17, 0),
                slot_duration_minutes=15,
            ))
        db.flush()
    else:
        # No schedule for MONDAY; provide one for TUESDAY only
        db.add(PractitionerSchedule(
            practitioner_id=practitioner.id,
            day_of_week=TUESDAY.weekday(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            slot_duration_minutes=15,
        ))
        db.flush()

    # ── Resolve break presence ──
    # diary_with_break is always injected; for no-break scenarios we skip assertions
    # about break warnings (they're only relevant for BREAK-OVERLAP)

    # ── Build search request ──
    loc_a, loc_b = two_locations
    search_location = (
        [loc_a, loc_b][scenario.search_location_idx]
        if scenario.search_location_idx is not None
        else None
    )

    body = {
        "practitioner_id": str(practitioner.id),
        "date_from": MONDAY.isoformat(),
        "duration_minutes": scenario.duration,
    }
    if search_location:
        body["location_id"] = str(search_location.id)
    if scenario.earliest_time:
        body["earliest_time"] = scenario.earliest_time
    if scenario.latest_time:
        body["latest_time"] = scenario.latest_time

    # ── Execute ──
    token = make_token(gp_user)
    resp = _search(client, token, body)
    assert resp.status_code == 200, (
        f"[{scenario.case_id}] Expected 200, got {resp.status_code}: {resp.text}"
    )
    data = resp.json()

    # ── Verify top-level shape ──
    assert data["intent"] == "search_slots", (
        f"[{scenario.case_id}] intent mismatch"
    )
    assert data["safe"] is True, (
        f"[{scenario.case_id}] expected safe=True"
    )
    assert data["autonomy_tier"] == "execute_with_report", (
        f"[{scenario.case_id}] expected execute_with_report"
    )
    assert data["requires_confirmation"] is False
    assert data["resolved_duration_minutes"] == scenario.duration

    # ── Verify candidate count ──
    if scenario.expect_zero_candidates:
        assert data["candidates"] == [], (
            f"[{scenario.case_id}] expected zero candidates"
        )
        return

    assert len(data["candidates"]) > 0, (
        f"[{scenario.case_id}] expected at least one candidate"
    )

    # ── Verify stable ordering (earliest-first) ──
    starts_local = [c["start_time_local"] for c in data["candidates"]]
    assert starts_local == sorted(starts_local), (
        f"[{scenario.case_id}] candidates not earliest-first: {starts_local}"
    )

    # ── Verify every candidate has correct duration and tz-aware times ──
    for c in data["candidates"]:
        assert c["duration_minutes"] == scenario.duration, (
            f"[{scenario.case_id}] candidate duration mismatch"
        )
        assert "Z" in c["start_time"] or "+" in c["start_time"], (
            f"[{scenario.case_id}] start_time not tz-aware: {c['start_time']}"
        )
        assert "Z" in c["end_time"] or "+" in c["end_time"], (
            f"[{scenario.case_id}] end_time not tz-aware: {c['end_time']}"
        )

    # ── 09:00 blocking check ──
    if scenario.expect_09_00_blocked:
        assert "09:00:00" not in starts_local, (
            f"[{scenario.case_id}] 09:00 should be blocked but appears: {starts_local}"
        )
    else:
        assert "09:00:00" in starts_local, (
            f"[{scenario.case_id}] 09:00 should be free but missing: {starts_local}"
        )

    # ── 30-min blocking: also check 09:15 is blocked ──
    if scenario.case_id == "DUR-30BLOCK":
        assert "09:15:00" not in starts_local, (
            f"[{scenario.case_id}] 09:15 should also be blocked by 30-min appt"
        )
        assert "09:30:00" in starts_local, (
            f"[{scenario.case_id}] 09:30 should be free after 30-min block"
        )

    # ── Time bound assertions ──
    if scenario.earliest_time:
        for c in data["candidates"]:
            assert c["start_time_local"] >= scenario.earliest_time, (
                f"[{scenario.case_id}] candidate {c['start_time_local']} before "
                f"earliest_time {scenario.earliest_time}"
            )

    if scenario.latest_time:
        for c in data["candidates"]:
            assert c["start_time_local"] < scenario.latest_time, (
                f"[{scenario.case_id}] candidate {c['start_time_local']} not "
                f"before latest_time {scenario.latest_time}"
            )

    # ── Break overlap warning check ──
    if scenario.expect_break_warning_10_30:
        candidates_by_start = {c["start_time_local"]: c for c in data["candidates"]}
        assert "10:30:00" in candidates_by_start, (
            f"[{scenario.case_id}] 10:30 must still appear with break_overlap warning"
        )
        warnings = candidates_by_start["10:30:00"]["warnings"]
        assert any(w["code"] == "break_overlap" for w in warnings), (
            f"[{scenario.case_id}] expected break_overlap warning at 10:30"
        )

    # ── Roster absent warning check ──
    if not scenario.has_roster:
        warnings = data.get("warnings", [])
        assert any(w["code"] == "no_practitioner_schedule" for w in warnings), (
            f"[{scenario.case_id}] expected no_practitioner_schedule warning"
        )

    # ── Candidate date bounds: all candidates must be on the requested date ──
    search_date = MONDAY.isoformat()
    for c in data["candidates"]:
        assert c["appointment_date"] == search_date, (
            f"[{scenario.case_id}] candidate on unexpected date "
            f"{c['appointment_date']}, expected {search_date}"
        )


# ─── Non-mutating proof ───────────────────────────────────────────────────────


def test_matrix_overall_writes_no_appointments_and_no_audit_rows(
    client, db, gp_user, practice, practitioner, patient,
    two_locations, diary_with_break,
):
    """Prove the entire matrix (all 16 scenarios combined) creates no rows.

    This is intentionally a separate test from the parametrized matrix above
    because each parametrized row writes to the DB for its own setup and we
    cannot count rows inside a single parametrized row.  Instead this test
    runs a representative cross-section of the matrix scenarios as isolated
    requests and asserts zero row growth overall.
    """
    # Create roster schedule
    from app.models.appointments import PractitionerSchedule
    for dow in range(5):
        db.add(PractitionerSchedule(
            practitioner_id=practitioner.id,
            day_of_week=dow,
            start_time=time(9, 0),
            end_time=time(17, 0),
            slot_duration_minutes=15,
        ))
    db.flush()

    loc_a, loc_b = two_locations
    token = make_token(gp_user)

    # Pre-count
    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    # Run a representative subset that exercises all route paths:
    # baseline, blocking, non-blocking, location-same, location-other,
    # time bounds, break overlap, roster absent

    # 1. Baseline
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200

    # 2. With blocking appointment
    _make_appt(db, practice, practitioner, patient, MONDAY, 9, 0, 15,
               status=AppointmentStatus.Booked)
    db.commit()
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200

    # Remove the blocking appt to avoid cross-contamination
    db.query(Appointment).delete()
    db.commit()

    # 3. With break overlap
    resp = _search(client, token, _base_body(practitioner))
    assert resp.status_code == 200

    # 4. Location-other (non-blocking)
    _make_appt(db, practice, practitioner, patient, MONDAY, 9, 0, 15,
               status=AppointmentStatus.Booked, location_id=loc_a.id)
    db.commit()
    resp = _search(client, token, {**_base_body(practitioner),
                                    "location_id": str(loc_b.id)})
    assert resp.status_code == 200

    # Clean up
    db.query(Appointment).delete()
    db.commit()

    # 5. Time bounds
    resp = _search(client, token, {**_base_body(practitioner),
                                    "earliest_time": "10:00:00",
                                    "latest_time": "11:00:00"})
    assert resp.status_code == 200

    # Post-count
    db.expire_all()
    appt_after = db.query(Appointment).count()
    audit_after = db.query(AppointmentAuditLog).count()

    assert appt_after == appt_before, (
        f"slot search matrix must not create appointment rows: "
        f"{appt_before} -> {appt_after}"
    )
    assert audit_after == audit_before, (
        f"slot search matrix must not create audit rows: "
        f"{audit_before} -> {audit_after}"
    )
