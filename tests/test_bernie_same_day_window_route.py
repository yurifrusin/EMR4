"""
Deterministic temporal-boundary route tests for the interpret-booking-instruction path.

Sprint R6 temporal harness foundation — Claude implementation lane.

Tests exercise the same-day window check in
propose_bernie_interpret_booking_instruction (app/routers/appointments.py).
The wall clock is replaced by monkeypatching appointments_router._clinic_local_now
so every assertion is fully deterministic.

Coverage:
  T1 - window_fully_past with both earliest+latest → ask band (pre-existing guard fires)
  T2 - window_fully_past with latest_time only (A1 gap) → ask band after route fix
  T3 - clamp_earliest: earliest in the past, no latest → clamp, not block
  T4 - clock-sensitivity control: same T2 request before the window expires → interpreted
"""

from __future__ import annotations

import datetime as _dt
from zoneinfo import ZoneInfo

import app.routers.appointments as appointments_router
import app.services.bernie_booking_interpreter as interpreter_service
from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
from tests.conftest import make_token

INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
_SYDNEY = ZoneInfo("Australia/Sydney")
# Fixed anchor — a Tuesday; normalizer never blocks on day-of-week.
_TEST_DATE = "2026-06-23"


class _MockProvider:
    """Minimal live-provider mock that returns a preset JSON command candidate."""

    def __init__(self, response: dict) -> None:
        self._response = response
        self.calls: list = []

    def generate_json(self, contents, temperature: float) -> dict:
        self.calls.append((contents, temperature))
        return self._response


def _fixed_now(hour: int, minute: int = 0):
    """Return a monkeypatch target that always yields the anchor date at HH:MM Sydney."""
    dt = _dt.datetime(2026, 6, 23, hour, minute, 0, tzinfo=_SYDNEY)
    return lambda tz: dt  # noqa: ARG005  (tz arg ignored — test replaces the whole function)


def _post(client, token: str, instruction: str, **overrides):
    body = {"instruction": instruction, "reference_date": _TEST_DATE}
    body.update(overrides)
    return client.post(INTERPRET_URL, json=body, headers={"Authorization": f"Bearer {token}"})


# ---------------------------------------------------------------------------
# T1: window_fully_past with both earliest+latest fires ask band
# ---------------------------------------------------------------------------

def test_window_fully_past_both_earliest_and_latest_fires_ask_band(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Existing guard: both times in past at 10:30 → temporal ask, no DB mutation."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(10, 30))
    token = make_token(gp_user)
    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        "date_from:today duration:15 earliest_time:08:00 latest_time:09:00",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "clarification_required"
    assert data["safe"] is False
    assert data["clarifying_question"] is not None
    assert "already passed today" in data["clarifying_question"]
    assert db.query(Appointment).count() == appt_before
    assert db.query(AppointmentAuditLog).count() == audit_before


# ---------------------------------------------------------------------------
# T2 (A1): window_fully_past with latest_time only fires ask band
# ---------------------------------------------------------------------------

def test_window_fully_past_latest_only_fires_ask_band(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """A1 gap: 'before 09:00' at 10:30 with no earliest_time must raise temporal ask.

    The fake-provider always fills earliest_time from the positional HH:MM fallback,
    so this test uses MockLiveProvider to produce a command candidate that contains
    only latest_time — matching what a real LLM returns for 'Book today before 09:00'.

    Before the route fix (guard required _earliest is not None) the window_fully_past
    branch is never entered and the route returns interpreted/safe.
    After the fix (_latest is not None suffices) the branch fires correctly.
    """
    provider = _MockProvider({
        "command_candidate": {
            "practitioner_id": str(practitioner.id),
            "patient_id": str(patient.id),
            "date_from": "today",
            "duration_minutes": 15,
            "latest_time": "09:00",
            # earliest_time deliberately absent — represents 'before 09:00'
        },
        "confidence": 0.9,
        "summary": "Book today before 09:00.",
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
    })
    interpreter_service.set_live_provider_factory(lambda: provider)
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(10, 30))
    token = make_token(gp_user)
    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    try:
        resp = _post(client, token, "Book me in before 09:00 today")

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["result"] == "clarification_required", (
            "Expected temporal ask for 'before 09:00' at 10:30 — "
            "this fails if the route guard still requires _earliest is not None (A1 gap)"
        )
        assert data["safe"] is False
        assert data["clarifying_question"] is not None
        assert "already passed today" in data["clarifying_question"]
        assert db.query(Appointment).count() == appt_before
        assert db.query(AppointmentAuditLog).count() == audit_before
    finally:
        interpreter_service.set_live_provider_factory(None)


# ---------------------------------------------------------------------------
# T3: clamp_earliest adjusts window without blocking
# ---------------------------------------------------------------------------

def test_clamp_earliest_adjusts_constraint_without_blocking(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """earliest in the past but no latest → clamp to now, result stays interpreted."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(10, 30))
    token = make_token(gp_user)
    appt_before = db.query(Appointment).count()

    resp = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        "date_from:today duration:15 earliest_time:09:00",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "interpreted"
    assert data["safe"] is True
    assert db.query(Appointment).count() == appt_before


# ---------------------------------------------------------------------------
# T4: clock-sensitivity control — same request before the window expires
# ---------------------------------------------------------------------------

def test_clock_sensitivity_control_before_window_returns_interpreted(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Control: same 'before 09:00' request at 08:00 → window still open → interpreted.

    Confirms the A1 fix is genuinely clock-driven, not always-ask.
    """
    provider = _MockProvider({
        "command_candidate": {
            "practitioner_id": str(practitioner.id),
            "patient_id": str(patient.id),
            "date_from": "today",
            "duration_minutes": 15,
            "latest_time": "09:00",
        },
        "confidence": 0.9,
        "summary": "Book today before 09:00.",
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
    })
    interpreter_service.set_live_provider_factory(lambda: provider)
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    # Clock at 08:00 — BEFORE the 09:00 latest_time ceiling
    monkeypatch.setattr(appointments_router, "_clinic_local_now", _fixed_now(8, 0))
    token = make_token(gp_user)

    try:
        resp = _post(client, token, "Book me in before 09:00 today")

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["result"] == "interpreted", (
            "Window is still open at 08:00 — should be interpreted, not clarification"
        )
        assert data["safe"] is True
        assert data["clarifying_question"] is None
    finally:
        interpreter_service.set_live_provider_factory(None)
