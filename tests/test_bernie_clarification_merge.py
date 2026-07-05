"""Sprint R2 clarification merge semantics — focused regression tests.

Proves that a clarification reply sent back with a prior requested_appointment
context frame carries forward already-resolved patient, practitioner, date, time,
and duration fields (gap-fill only; new-reply-wins).

All tests use the fake interpreter provider; no live Gemini/provider calls.
No appointment or audit rows are written by the interpret route.
"""

from __future__ import annotations

import uuid

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"

# A Wednesday — no same-day clamping, no same-day window issues.
REFERENCE_DATE = "2026-07-08"
REQUEST_DATE = "2026-07-14"  # following Tuesday


def _post(client, token: str, instruction: str, context_frames=None) -> dict:
    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": instruction,
            "reference_date": REFERENCE_DATE,
            "context_frames": context_frames or [],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _requested_appointment_frame(data: dict) -> dict | None:
    """Extract the first requested_appointment frame from reception_context."""
    ctx = data.get("reception_context") or {}
    for frame in ctx.get("frames") or []:
        if frame.get("frame_type") == "requested_appointment":
            return frame
    return None


# ─── Turn 1: clarification_required stores resolved fields in frame payload ─────

def test_turn1_missing_practitioner_stores_patient_and_date_in_frame(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """Turn 1 missing practitioner_id returns clarification_required and stores
    resolved patient_id, date_from, earliest_time, duration_minutes in the
    requested_appointment frame payload so the client can thread it back."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    data = _post(
        client, token,
        f"patient_id:{patient.id} date_from:{REQUEST_DATE} earliest_time:15:30 duration:30",
    )

    assert data["result"] == "clarification_required"
    assert "practitioner_id" in data["missing_fields"]

    frame = _requested_appointment_frame(data)
    assert frame is not None, "reception_context must contain a requested_appointment frame"
    payload = frame.get("payload") or {}
    assert str(patient.id) == payload.get("patient_id"), "patient_id must be in frame payload"
    assert REQUEST_DATE == payload.get("date_from"), "date_from must be in frame payload"
    assert "15:30" == payload.get("earliest_time"), "earliest_time must be in frame payload"
    assert "30" == payload.get("duration_minutes"), "duration_minutes must be in frame payload"


def test_interpreted_turn_stores_all_resolved_fields_in_frame(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """An interpreted (non-clarification) turn also stores resolved fields in the
    requested_appointment frame payload so they can be threaded into a follow-up turn."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    data = _post(
        client, token,
        (
            f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
            f"date_from:{REQUEST_DATE} earliest_time:09:00 duration:20"
        ),
    )

    assert data["result"] == "interpreted"

    frame = _requested_appointment_frame(data)
    assert frame is not None
    payload = frame.get("payload") or {}
    assert str(practitioner.id) == payload.get("practitioner_id"), "practitioner_id in payload"
    assert str(patient.id) == payload.get("patient_id"), "patient_id in payload"
    assert REQUEST_DATE == payload.get("date_from"), "date_from in payload"
    assert "09:00" == payload.get("earliest_time"), "earliest_time in payload"
    assert "20" == payload.get("duration_minutes"), "duration_minutes in payload"


# ─── Turn 2: clarification reply merges prior frame fields ───────────────────

def test_turn2_merges_patient_date_time_when_reply_provides_practitioner(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """Turn 2 with prior frame: instruction provides practitioner_id; frame carries
    patient_id, date_from, earliest_time, duration_minutes forward → interpreted."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    # Turn 1: get frame with patient/date/time resolved
    turn1 = _post(
        client, token,
        f"patient_id:{patient.id} date_from:{REQUEST_DATE} earliest_time:15:30 duration:30",
    )
    assert turn1["result"] == "clarification_required"
    prior_frame = _requested_appointment_frame(turn1)
    assert prior_frame is not None

    # Turn 2: provide practitioner, carry back the prior frame
    turn2 = _post(
        client, token,
        f"practitioner_id:{practitioner.id}",
        context_frames=[prior_frame],
    )

    assert turn2["result"] == "interpreted", (
        f"Expected interpreted after clarification merge, got {turn2['result']!r}. "
        f"missing_fields={turn2.get('missing_fields')}"
    )
    cmd = turn2["command_candidate"]
    assert cmd["practitioner_id"] == str(practitioner.id), "practitioner_id should be from turn 2"
    assert cmd["patient_id"] == str(patient.id), "patient_id should be merged from prior frame"
    assert cmd["date_from"] == REQUEST_DATE, "date_from should be merged from prior frame"
    assert cmd["earliest_time"] == "15:30", "earliest_time should be merged from prior frame"
    assert int(cmd["duration_minutes"]) == 30, "duration_minutes should be merged from prior frame"

    # Verify the clarification_merge assumption is present
    assumptions = {a["field"]: a for a in turn2.get("assumptions") or []}
    assert "clarification_merge" in assumptions, (
        "clarification_merge assumption must be emitted when fields are carried forward"
    )


def test_turn2_nl_practitioner_name_plus_prior_frame_merges_patient_and_date(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """Turn 1: patient_id + date, missing practitioner → clarification_required.
    Turn 2: NL practitioner name ('Shera') + prior frame → interpreted with patient
    and date from prior frame and practitioner resolved from name."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    # Turn 1: patient + date, no practitioner
    turn1 = _post(
        client, token,
        f"patient_id:{patient.id} date_from:{REQUEST_DATE} earliest_time:09:00 duration:15",
    )
    assert turn1["result"] == "clarification_required"
    assert "practitioner_id" in turn1["missing_fields"]
    prior_frame = _requested_appointment_frame(turn1)
    assert prior_frame is not None

    # Turn 2: mention practitioner by surname only; prior frame supplies patient + date
    turn2 = _post(
        client, token,
        "With Shera please",
        context_frames=[prior_frame],
    )

    assert turn2["result"] == "interpreted", (
        f"Expected interpreted, got {turn2['result']!r}. missing={turn2.get('missing_fields')}"
    )
    cmd = turn2["command_candidate"]
    assert cmd["practitioner_id"] == str(practitioner.id), "practitioner_id resolved from name in turn 2"
    assert cmd["patient_id"] == str(patient.id), "patient_id merged from prior frame"
    assert cmd["date_from"] == REQUEST_DATE, "date_from merged from prior frame"


# ─── New-reply-wins ───────────────────────────────────────────────────────────

def test_new_reply_wins_over_prior_frame(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """When turn 2 explicitly provides a field, the new value wins over the prior frame."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    # Turn 1: patient + date_from=REQUEST_DATE, no practitioner
    turn1 = _post(
        client, token,
        f"patient_id:{patient.id} date_from:{REQUEST_DATE} earliest_time:15:30 duration:30",
    )
    prior_frame = _requested_appointment_frame(turn1)
    assert prior_frame is not None

    # Turn 2: different date + practitioner — new date should WIN over prior frame date
    different_date = "2026-07-21"
    turn2 = _post(
        client, token,
        f"practitioner_id:{practitioner.id} date_from:{different_date}",
        context_frames=[prior_frame],
    )

    assert turn2["result"] == "interpreted"
    cmd = turn2["command_candidate"]
    assert cmd["date_from"] == different_date, (
        f"New date {different_date!r} must win over prior frame date {REQUEST_DATE!r}"
    )
    assert cmd["patient_id"] == str(patient.id), "patient_id still merged from prior frame"


# ─── No prior frame = no merge ────────────────────────────────────────────────

def test_no_merge_without_prior_frame(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """Without a prior frame, a bare clarification-reply instruction that only
    provides practitioner_id remains clarification_required (no patient/date)."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id}",
        context_frames=[],  # no prior frame
    )

    # patient not resolved + no date → clarification still required
    assert data["result"] == "clarification_required"
    # No clarification_merge assumption
    assumptions = {a["field"]: a for a in data.get("assumptions") or []}
    assert "clarification_merge" not in assumptions


# ─── Duration carry-forward ───────────────────────────────────────────────────

def test_prior_duration_carried_forward_prevents_default(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """When the prior frame has duration_minutes=45, the clarification reply does
    not trigger the 15-minute default; 45 is preserved."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    # Turn 1: patient + date + duration=45, no practitioner
    turn1 = _post(
        client, token,
        f"patient_id:{patient.id} date_from:{REQUEST_DATE} duration:45",
    )
    assert turn1["result"] == "clarification_required"
    prior_frame = _requested_appointment_frame(turn1)
    assert prior_frame is not None
    assert prior_frame["payload"].get("duration_minutes") == "45"

    # Turn 2: provide practitioner; duration should come from prior frame, not default to 15
    turn2 = _post(
        client, token,
        f"practitioner_id:{practitioner.id}",
        context_frames=[prior_frame],
    )

    assert turn2["result"] == "interpreted"
    cmd = turn2["command_candidate"]
    assert int(cmd["duration_minutes"]) == 45, (
        f"Expected duration=45 from prior frame, got {cmd['duration_minutes']!r}"
    )


# ─── No DB mutations ─────────────────────────────────────────────────────────

def test_interpret_route_writes_no_appointment_rows(
    client, db, gp_user, practitioner, patient, monkeypatch,
):
    """The interpret route never writes Appointment or AppointmentAuditLog rows,
    even across a two-turn clarification-merge sequence."""
    from app.models.appointments import Appointment, AppointmentAuditLog

    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    # Turn 1
    turn1 = _post(
        client, token,
        f"patient_id:{patient.id} date_from:{REQUEST_DATE} earliest_time:15:30 duration:30",
    )
    prior_frame = _requested_appointment_frame(turn1)

    # Turn 2
    _post(
        client, token,
        f"practitioner_id:{practitioner.id}",
        context_frames=[prior_frame],
    )

    appt_count = db.query(Appointment).count()
    audit_count = db.query(AppointmentAuditLog).count()
    assert appt_count == 0, f"No appointments should be written; found {appt_count}"
    assert audit_count == 0, f"No audit rows should be written; found {audit_count}"
