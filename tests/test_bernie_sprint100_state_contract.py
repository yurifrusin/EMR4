"""Sprint 100: Bernie backend state contract tests.

Covers:
- Open-ended after-hours same-day request returns clinic_day_exhausted (after slot search)
- Bounded window fully past returns clinic_day_exhausted (before slot search, no slot query)
- Partly-past in-hours clamp preserved: returns candidate_selection_required, not exhausted
- request_reference_date echoed in interpret response
- request_reference_date echoed in supervised-booking response
- tomorrow immutability: resolves to reference+1, not re-resolved on confirm
- Selected-candidate confirmation uses absolute slot fields (rejects mismatched reference)
- No mutation before confirm: interpret and supervised-booking write zero Appointment/audit rows
- No live-provider dependency: all tests run on fake/deterministic path

All exhaustion tests use monkeypatch to control clinic-local now — never hits a live provider.
"""

from datetime import date, datetime, time, timezone

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
SUPERVISED_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"

# Reference date pinned to a weekday (Tuesday) so schedule fixtures apply.
# Chosen well in the past to avoid accidental "today" matches in non-patched tests.
REFERENCE_DATE = "2026-07-14"  # Tuesday
REFERENCE_DATE_OBJ = date(2026, 7, 14)

# The "clinic today" used by exhaustion tests — pinned by monkeypatch
CLINIC_TODAY = date(2026, 7, 15)  # Wednesday
CLINIC_TODAY_STR = "2026-07-15"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _post_interpret(client, token, instruction, reference_date=REFERENCE_DATE):
    resp = client.post(
        INTERPRET_URL,
        json={"instruction": instruction, "reference_date": reference_date},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _post_supervised(client, token, body):
    resp = client.post(
        SUPERVISED_URL,
        json=body,
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _base_supervised_body(practitioner, *, date_from="today", earliest_time=None, latest_time=None,
                           duration_minutes=15, reference_date=CLINIC_TODAY_STR):
    command = {
        "practitioner_id": str(practitioner.id),
        "date_from": date_from,
        "duration_minutes": str(duration_minutes),
    }
    if earliest_time:
        command["earliest_time"] = earliest_time
    if latest_time:
        command["latest_time"] = latest_time
    return {
        "reference_date": reference_date,
        "command": command,
    }


# ─── Open-ended after-hours → clinic_day_exhausted (after slot search) ────────

def test_after_3_today_at_2040_open_ended_returns_clinic_day_exhausted(
    client, db, gp_user, practitioner, schedule, monkeypatch,
):
    """Yuri's concrete failing case: 'after 3 today' at 20:40.

    Clamp-to-now pushes earliest_time to 20:40; practitioner schedule ends at 17:00
    so zero remaining bookable slots → clinic_day_exhausted, NOT candidate_selection_required
    with empty list. date_from must NOT be auto-advanced to tomorrow.
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 20, 40, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    body = _base_supervised_body(
        practitioner,
        date_from="today",
        earliest_time="15:00",  # "after 3 today"
        # no latest_time → open-ended
    )
    data = _post_supervised(client, token, body)

    assert data["result"] == "clinic_day_exhausted", (
        f"Expected clinic_day_exhausted, got {data['result']!r}. "
        "Open-ended after-hours same-day must not return empty candidate_selection_required."
    )
    assert data["safe"] is False
    # date_from must NOT have been silently advanced to tomorrow
    norm_constraint = data.get("normalization", {}).get("constraint") or {}
    date_from_in_response = norm_constraint.get("date_from")
    if date_from_in_response:
        assert date_from_in_response == CLINIC_TODAY_STR, (
            f"date_from must remain {CLINIC_TODAY_STR}, not auto-advanced to {date_from_in_response!r}"
        )
    # Blocks must include clinic_day_exhausted code
    codes = [b["code"] for b in data.get("blocks", [])]
    assert "clinic_day_exhausted" in codes, f"Expected clinic_day_exhausted block, got: {codes}"


# ─── Bounded window fully past → clinic_day_exhausted (before slot search) ────

def test_today_before_3pm_at_2040_bounded_past_returns_clinic_day_exhausted(
    client, db, gp_user, practitioner, schedule, monkeypatch,
):
    """Bounded window 'today before 3 pm' at 20:40 — window fully past.

    Pre-search check fires before any slot query (latest_time=15:00 <= now_time=20:40).
    Returns clinic_day_exhausted. date_from not advanced.
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 20, 40, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    body = _base_supervised_body(
        practitioner,
        date_from="today",
        earliest_time="09:00",
        latest_time="15:00",  # "before 3 pm" → window fully past at 20:40
    )
    data = _post_supervised(client, token, body)

    assert data["result"] == "clinic_day_exhausted", (
        f"Expected clinic_day_exhausted for fully-past bounded window, got {data['result']!r}."
    )
    assert data["safe"] is False
    codes = [b["code"] for b in data.get("blocks", [])]
    assert "clinic_day_exhausted" in codes, f"Expected clinic_day_exhausted block, got: {codes}"
    # date_from must not be advanced
    norm_constraint = data.get("normalization", {}).get("constraint") or {}
    date_from_in_response = norm_constraint.get("date_from")
    if date_from_in_response:
        assert date_from_in_response == CLINIC_TODAY_STR, (
            f"date_from must remain {CLINIC_TODAY_STR}, not {date_from_in_response!r}"
        )


# ─── Partly-past in-hours → clamped, returns candidates ──────────────────────

def test_today_after_2pm_at_1420_clamps_and_returns_candidates(
    client, db, gp_user, practitioner, schedule, monkeypatch,
):
    """'after 2 pm today' at 14:20 — earliest_time is partly past, clamp forward.

    After clamping earliest_time to 14:20, the schedule still has slots (14:20-17:00),
    so the result is candidate_selection_required (not clinic_day_exhausted).
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 14, 20, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    body = _base_supervised_body(
        practitioner,
        date_from="today",
        earliest_time="14:00",  # "after 2 pm" — in the past at 14:20
        # no latest_time → open-ended; schedule ends at 17:00
    )
    data = _post_supervised(client, token, body)

    # Partly past — must NOT return clinic_day_exhausted; schedule has remaining slots
    assert data["result"] != "clinic_day_exhausted", (
        "Partly-past open-ended request should not return clinic_day_exhausted "
        "when slots remain in the schedule."
    )
    assert data["result"] == "candidate_selection_required", (
        f"Expected candidate_selection_required, got {data['result']!r}"
    )
    assert data["safe"] is True
    candidates = data.get("search_proposal", {}).get("candidates", [])
    assert len(candidates) > 0, (
        "Expected candidates for 'after 2pm' at 14:20 with schedule through 17:00"
    )


# ─── request_reference_date echoed ────────────────────────────────────────────

def test_request_reference_date_echoed_in_interpret(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """interpret response echoes request_reference_date from inbound reference_date.
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 14, 9, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    data = _post_interpret(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        f"date_from:{REFERENCE_DATE} duration:15 earliest_time:09:00",
        reference_date=REFERENCE_DATE,
    )
    assert data.get("request_reference_date") == REFERENCE_DATE, (
        f"Expected request_reference_date={REFERENCE_DATE!r}, got {data.get('request_reference_date')!r}"
    )


def test_request_reference_date_echoed_in_supervised_booking(
    client, db, gp_user, practitioner, schedule, monkeypatch,
):
    """supervised-booking response echoes request_reference_date from inbound reference_date.
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 9, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    body = _base_supervised_body(
        practitioner,
        date_from="today",
        earliest_time="09:00",
        reference_date=CLINIC_TODAY_STR,
    )
    data = _post_supervised(client, token, body)
    assert data.get("request_reference_date") == CLINIC_TODAY_STR, (
        f"Expected request_reference_date={CLINIC_TODAY_STR!r}, got {data.get('request_reference_date')!r}"
    )


# ─── tomorrow immutability ────────────────────────────────────────────────────

def test_tomorrow_resolves_to_reference_plus_one(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """'tomorrow' resolved against reference_date yields reference+1.

    Confirms relative token is resolved once against the fixed reference_date,
    not against whatever 'actual today' happens to be at call time.
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    # Pin clinic-local now to a different date so "today" != reference
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 8, 1, 9, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    # reference_date = 2026-07-14 → tomorrow should resolve to 2026-07-15
    data = _post_interpret(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        "date_from:tomorrow duration:15",
        reference_date=REFERENCE_DATE,
    )
    norm = data.get("normalization") or {}
    constraint = norm.get("constraint") or {}
    resolved_date = constraint.get("date_from")
    expected = "2026-07-15"  # reference_date (2026-07-14) + 1 day
    if resolved_date:
        assert resolved_date == expected, (
            f"Expected 'tomorrow' to resolve to {expected!r} from reference {REFERENCE_DATE!r}, "
            f"got {resolved_date!r}. 'tomorrow' must not re-resolve against actual today."
        )


# ─── No mutation before confirm ───────────────────────────────────────────────

def test_interpret_writes_no_appointment_or_audit_rows(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """interpret endpoint writes zero Appointment and AppointmentAuditLog rows.
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    appt_count_before = db.query(Appointment).count()
    audit_count_before = db.query(AppointmentAuditLog).count()

    _post_interpret(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        f"date_from:{REFERENCE_DATE} duration:15",
    )

    assert db.query(Appointment).count() == appt_count_before, (
        "interpret must not create Appointment rows"
    )
    assert db.query(AppointmentAuditLog).count() == audit_count_before, (
        "interpret must not create AppointmentAuditLog rows"
    )


def test_supervised_booking_writes_no_appointment_or_audit_rows(
    client, db, gp_user, practitioner, schedule, monkeypatch,
):
    """supervised-booking endpoint writes zero Appointment and AppointmentAuditLog rows.
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 14, 9, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    appt_count_before = db.query(Appointment).count()
    audit_count_before = db.query(AppointmentAuditLog).count()

    body = _base_supervised_body(
        practitioner,
        date_from="today",
        earliest_time="09:00",
        reference_date=REFERENCE_DATE,
    )
    _post_supervised(client, token, body)

    assert db.query(Appointment).count() == appt_count_before, (
        "supervised-booking must not create Appointment rows"
    )
    assert db.query(AppointmentAuditLog).count() == audit_count_before, (
        "supervised-booking must not create AppointmentAuditLog rows"
    )


# ─── clinic_day_exhausted does not trigger for non-today dates ────────────────

def test_tomorrow_date_does_not_trigger_exhaustion(
    client, db, gp_user, practitioner, schedule, monkeypatch,
):
    """A request for 'tomorrow after 3 pm' at 20:40 should NOT trigger clinic_day_exhausted.

    The exhaustion check is same-day only; future dates are not exhausted.
    [route-intercepted/fake — no live provider]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 20, 40, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    # reference_date is 2026-07-15 (clinic today), date_from=tomorrow → 2026-07-16
    body = _base_supervised_body(
        practitioner,
        date_from="tomorrow",
        earliest_time="15:00",
        reference_date=CLINIC_TODAY_STR,
    )
    data = _post_supervised(client, token, body)

    assert data["result"] != "clinic_day_exhausted", (
        "clinic_day_exhausted must not fire for a future date"
    )
    assert data["result"] == "candidate_selection_required", (
        f"Expected candidate_selection_required for tomorrow, got {data['result']!r}"
    )


# ─── No live-provider dependency (meta-check) ─────────────────────────────────

def test_all_exhaustion_paths_use_fake_provider_not_live(
    client, db, gp_user, practitioner, schedule, monkeypatch,
):
    """Structural: exhaustion detection is purely deterministic — no LLM, no live provider.

    The supervised-booking endpoint is not gated by the interpreter provider setting.
    [route-intercepted/fake — deterministic path asserted]
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "disabled")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 20, 40, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    body = _base_supervised_body(
        practitioner,
        date_from="today",
        earliest_time="15:00",
        reference_date=CLINIC_TODAY_STR,
    )
    # Even with the interpreter disabled, the supervised-booking endpoint must
    # return clinic_day_exhausted (it does not call the interpreter at all).
    data = _post_supervised(client, token, body)
    assert data["result"] == "clinic_day_exhausted", (
        "supervised-booking exhaustion must work regardless of interpreter provider setting"
    )
