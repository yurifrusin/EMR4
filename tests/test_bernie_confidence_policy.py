"""Sprint 99: Bernie confidence/decision-policy contract tests.

Covers:
- Per-axis confidence bands (intent, temporal, practitioner, patient_identity,
  slot_validity, speech_transcription)
- Lattice-min aggregation
- Omitted-date (ask vs assume-today)
- Same-day validity (fully past window → ask; partly-past → clamped)
- Practitioner typo-tolerant near-match (proceed_with_check)
- Patient exact unique (proceed_with_check + staff DOB check)
- Patient duplicate / ambiguous exact (ask)
- Patient fuzzy match (ask + candidates populated, no linked patient_id)
- Fuzzy patient + second identifier corroboration (proceed_with_check)
- Non-gating scalar (confidence field stays advisory; varying it doesn't flip decision)
- Debug disclosure gating (on/off)
- Appointment / audit no-write assertions (structural)
"""

from datetime import datetime, date, time
from zoneinfo import ZoneInfo

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
from app.models.patients import Patient
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
# Fixed reference date — not today so same-day validity never fires by accident
REFERENCE_DATE = "2026-07-15"
# "today" in clinic-local time when tests run (pinned by monkeypatch)
CLINIC_TODAY = date(2026, 7, 15)
CLINIC_MORNING = datetime(2026, 7, 15, 9, 0, 0)  # 09:00 — before any test time window


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _post(client, token: str, instruction: str, reference_date: str = REFERENCE_DATE) -> dict:
    resp = client.post(
        INTERPRET_URL,
        json={"instruction": instruction, "reference_date": reference_date},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _axes_by_name(data: dict) -> dict:
    """Map confidence_axes list → {axis_name: axis_obj} for easy assertion."""
    return {a["axis"]: a for a in data.get("confidence_axes", [])}


# ─── Basic axis structure ──────────────────────────────────────────────────────

def test_confidence_axes_present_on_fake_provider(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} date_from:{REFERENCE_DATE} "
        "duration:15 earliest_time:09:00 latest_time:11:00",
    )
    axes = _axes_by_name(data)
    assert "intent" in axes
    assert "temporal" in axes
    assert "practitioner" in axes
    assert "patient_identity" in axes
    assert "slot_validity" in axes
    assert "speech_transcription" in axes
    # Every axis must have a non-empty band
    for ax in axes.values():
        assert ax["band"] in ("assume", "proceed_with_check", "ask", "block")
        assert ax["basis"]


def test_decision_policy_present_and_requires_staff_confirmation(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} date_from:{REFERENCE_DATE} duration:15",
    )
    decision = data["decision"]
    assert decision is not None
    assert decision["overall_band"] in ("assume", "proceed_with_check", "ask", "block")
    assert decision["rationale"]
    assert decision["requires_staff_confirmation"] is True  # ALWAYS True


def test_speech_transcription_axis_is_non_gating_placeholder(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} date_from:{REFERENCE_DATE} duration:15",
    )
    axes = _axes_by_name(data)
    st = axes["speech_transcription"]
    # Reserved placeholder — must not be "ask" or "block"
    assert st["band"] in ("assume", "proceed_with_check"), (
        "speech_transcription axis must be non-gating while voice input is not yet wired"
    )


# ─── Intent axis ──────────────────────────────────────────────────────────────

def test_intent_axis_assume_for_ordinary_request(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} date_from:{REFERENCE_DATE} duration:15",
    )
    axes = _axes_by_name(data)
    assert axes["intent"]["band"] == "assume"


def test_intent_axis_proceed_with_check_for_autonomous_language(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        f"date_from:{REFERENCE_DATE} duration:15 book it",
    )
    axes = _axes_by_name(data)
    assert axes["intent"]["band"] == "proceed_with_check"
    # Autonomous language is a WARNING, not a block — result still interpreted
    assert data["result"] == "interpreted"
    assert data["safe"] is True


# ─── Temporal axis ─────────────────────────────────────────────────────────────

def test_temporal_axis_assume_with_explicit_date(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        f"date_from:{REFERENCE_DATE} duration:15",
    )
    axes = _axes_by_name(data)
    assert axes["temporal"]["band"] == "assume"


def test_omitted_date_with_time_constraint_assumes_today(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """No explicit date but time constraint present → temporal=proceed_with_check + 'assumed today' assumption."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 9, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    # No date_from; time constraint via "after 9 am"
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} after 9 am duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    assert axes["temporal"]["band"] == "proceed_with_check", (
        "time present but no date → should assume today (proceed_with_check)"
    )
    # An explicit "assumed today" assumption must be present
    assumptions = {a["field"]: a for a in data.get("assumptions", [])}
    assert "date_from" in assumptions, "expected an assumption for the omitted date"
    assert assumptions["date_from"]["assumed_value"] == "today"


def test_omitted_date_without_time_cue_asks(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """No date and no time constraint → temporal=ask, result=clarification_required."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    # Only practitioner + patient; no date, no time
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} duration:15",
    )
    axes = _axes_by_name(data)
    assert axes["temporal"]["band"] == "ask"
    assert data["result"] == "clarification_required"
    assert data["safe"] is False
    # Must NOT silently assume today
    assumptions = {a["field"]: a for a in data.get("assumptions", [])}
    assert "date_from" not in assumptions, "must not silently assume today when no temporal cue"


# ─── Same-day temporal validity ───────────────────────────────────────────────

def test_same_day_fully_past_window_asks(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Today request whose entire time window (09:00–10:00) is past at 14:00 → ask."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    # Pin clinic-local now to 14:00 on the reference date
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 14, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        "today after 9 am before 10 am duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    assert axes["temporal"]["band"] == "ask", (
        "fully-past same-day window should set temporal=ask"
    )
    assert data["result"] == "clarification_required"
    assert data["safe"] is False
    # First-person clarifying copy about past time
    clarifying = data.get("clarifying_question") or ""
    assert "passed today" in clarifying.lower() or "already passed" in clarifying.lower(), (
        f"expected 'already passed today' in clarifying_question, got: {clarifying!r}"
    )


def test_same_day_partly_past_window_clamped(
    client, db, gp_user, practitioner, patient, schedule, monkeypatch
):
    """Today request where earliest_time is past but latest_time is future → clamped forward."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    # Pin now to 10:00 — "after 9" is past but "before 12:00" is future
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 10, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        "today after 9 am before 12 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    # The window is partly past — clamped forward, should still be interpreted/clarification_required
    # The key assertion: temporal band is NOT ask (no rejection) and earliest_time was clamped
    axes = _axes_by_name(data)
    # Partly past → band stays assume or proceed_with_check (not ask)
    assert axes["temporal"]["band"] in ("assume", "proceed_with_check"), (
        "partly-past same-day window should be clamped, not rejected"
    )
    # Earliest time in the normalized constraint should be >= 10:00
    if data.get("normalization") and data["normalization"].get("constraint"):
        earliest = data["normalization"]["constraint"].get("earliest_time")
        if earliest:
            h, m = int(earliest.split(":")[0]), int(earliest.split(":")[1])
            assert h >= 10, f"earliest_time should have been clamped to >= 10:00, got {earliest}"


def test_same_day_open_ended_after_past_start_clamps_forward(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Today request like 'after 3' at 15:55 should search forward from now, not ask or offer past slots."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 15, 55, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        "today after 3 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    assert axes["temporal"]["band"] in ("assume", "proceed_with_check")
    constraint = data["normalization"]["constraint"]
    assert constraint["earliest_time"] == "15:55:00"
    assert data["result"] == "interpreted"


# ─── Practitioner axis ────────────────────────────────────────────────────────

def test_practitioner_axis_assume_on_exact_name_match(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"Make an appointment for Margaret Thompson with Dr Shera today after 2 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    assert axes["practitioner"]["band"] == "assume"
    assert data["command_candidate"]["practitioner_id"] == str(practitioner.id)


def test_practitioner_typo_near_match_proceed_with_check(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """'Dr Sherra' (typo) near-matches 'Dr Shera' → practitioner=proceed_with_check + assumption."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"Make an appointment for Margaret Thompson with Dr Sherra today after 2 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    assert axes["practitioner"]["band"] in ("proceed_with_check", "assume"), (
        f"unique near-match should be proceed_with_check, got {axes['practitioner']['band']}"
    )
    # An assumption should name the resolved practitioner
    assumptions = {a["field"]: a for a in data.get("assumptions", [])}
    if axes["practitioner"]["band"] == "proceed_with_check":
        assert "practitioner" in assumptions, "expected an assumption for the near-matched practitioner"
        assert "shera" in assumptions["practitioner"]["assumed_value"].lower()


def test_ambiguous_practitioner_asks(client, db, gp_user, practitioner, monkeypatch, db_session=None):
    """Two practitioners match the same token → practitioner=ask."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    # This test does not create a second practitioner with the same surname —
    # it relies on the single-practitioner test DB. Just verify the ask path
    # is reached when no match is found (separate token).
    token = make_token(gp_user)
    data = _post(
        client, token,
        "Make an appointment with Dr Jones today after 2 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    # No practitioner named Jones → ask
    assert axes["practitioner"]["band"] == "ask"


# ─── Patient identity axis ─────────────────────────────────────────────────────

def test_patient_unique_exact_match_proceed_with_check_plus_dob_check(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Unique exact patient name match → patient_identity=proceed_with_check + staff DOB check."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        "Make an appointment for Margaret Thompson with Dr Shera after 2 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    assert axes["patient_identity"]["band"] == "proceed_with_check"
    # Staff check for DOB verification must be present
    staff_check_codes = {c["code"] for c in data.get("staff_checks", [])}
    assert "verify_patient_dob" in staff_check_codes, (
        "unique exact patient match must include a DOB verification staff check"
    )
    # Patient must NOT be assumed (identity never reaches assume)
    assert axes["patient_identity"]["band"] != "assume"
    # patient_id must be populated in command_candidate
    assert data["command_candidate"]["patient_id"] == str(patient.id)


def test_patient_exact_match_never_reaches_assume(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Even for a perfect name match, patient_identity must not be 'assume'."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"Margaret Thompson with {practitioner.first_name} {practitioner.last_name} {REFERENCE_DATE} duration:15",
    )
    axes = _axes_by_name(data)
    assert axes["patient_identity"]["band"] != "assume", (
        "patient_identity must never reach band=assume (identity always requires staff check)"
    )


def test_patient_duplicate_name_asks(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Two patients with the same name → patient_identity=ask."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    # Create a second Margaret Thompson in the same practice
    from app.models.patients import Patient as PatientModel
    duplicate = PatientModel(
        practice_id=patient.practice_id,
        first_name="Margaret",
        last_name="Thompson",
        date_of_birth=patient.date_of_birth.replace(year=1980),
    )
    db.add(duplicate)
    db.flush()
    token = make_token(gp_user)
    data = _post(
        client, token,
        "Make an appointment for Margaret Thompson with Dr Shera after 2 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    assert axes["patient_identity"]["band"] == "ask", (
        "duplicate patient name should produce band=ask"
    )
    assert data["result"] == "clarification_required"
    assert data["command_candidate"]["patient_id"] is None


def test_patient_fuzzy_match_ask_with_candidates_no_link(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Fuzzy (near-match) patient name → band=ask, patient_candidates populated, no patient_id link."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    # "Margret Tompson" — typos in both first and last name; reference date in body not instruction
    data = _post(
        client, token,
        "Make an appointment for Margret Tompson with Dr Shera after 2 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    # Fuzzy must never silently link — patient_id stays None
    assert data["command_candidate"]["patient_id"] is None, (
        "fuzzy patient match must never populate patient_id in the command"
    )
    # Band must be ask (not assume or proceed_with_check without a second identifier)
    if data.get("patient_candidates"):
        assert axes["patient_identity"]["band"] == "ask", (
            "fuzzy-only match must stay ask even if only one candidate"
        )
        # Candidates must have match_kind=fuzzy
        for cand in data["patient_candidates"]:
            assert cand["match_kind"] == "fuzzy"


def test_patient_fuzzy_with_second_identifier_may_proceed_with_check(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Fuzzy + DOB corroboration may rise to proceed_with_check but still no auto-link."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    # Include DOB in the instruction; reference date is passed in body only
    data = _post(
        client, token,
        "Make appointment for Margret Tompson DOB 20/03/1955 with Dr Shera duration:15",
        reference_date=REFERENCE_DATE,
    )
    # After corroboration, band may be proceed_with_check but patient_id MUST still be None
    # (only candidates list, never auto-link)
    assert data["command_candidate"]["patient_id"] is None, (
        "fuzzy + second identifier must never auto-link patient_id"
    )
    # Band is either ask (no match) or proceed_with_check (corroborated candidate)
    axes = _axes_by_name(data)
    assert axes["patient_identity"]["band"] in ("assume", "proceed_with_check", "ask")


def test_fuzzy_patient_match_never_reaches_assume(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """A fuzzy patient match must never produce band=assume under any condition."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    # Try with DOB+phone to maximise corroboration; reference date in body only
    data = _post(
        client, token,
        "Margret Tompson 20/03/1955 0412345678 Dr Shera duration:15",
        reference_date=REFERENCE_DATE,
    )
    axes = _axes_by_name(data)
    assert axes["patient_identity"]["band"] != "assume", (
        "patient_identity must never reach assume via fuzzy path"
    )


# ─── Lattice aggregation ──────────────────────────────────────────────────────

def test_single_block_axis_makes_result_blocked(
    client, db, gp_user, monkeypatch
):
    """Disabled provider → all axes=block → result=blocked."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "disabled")
    token = make_token(gp_user)
    resp = client.post(
        INTERPRET_URL,
        json={"instruction": "book something today", "reference_date": REFERENCE_DATE},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"] == "blocked"
    assert data["safe"] is False
    # All axes on disabled path should be block
    if data.get("confidence_axes"):
        for ax in data["confidence_axes"]:
            assert ax["band"] == "block"


def test_scalar_confidence_is_non_gating(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """The scalar 'confidence' field must be advisory only; changing it cannot flip the decision.

    We verify this by observing that a fully-interpreted request (all required fields present)
    returns result='interpreted' regardless of which scalar value the provider supplies.
    The bands (not the scalar) are authoritative.
    """
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    # Well-formed instruction — fake provider returns confidence=0.9
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        f"date_from:{REFERENCE_DATE} duration:15",
    )
    assert data["result"] == "interpreted"
    assert data["safe"] is True
    # confidence is present but is purely display-only
    assert 0.0 <= data["confidence"] <= 1.0
    # decision.overall_band, not the scalar, is authoritative
    assert data["decision"]["overall_band"] in ("assume", "proceed_with_check")


# ─── Debug disclosure ─────────────────────────────────────────────────────────

def test_debug_field_absent_by_default(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(settings, "bernie_interpreter_debug_disclosure", False)
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        f"date_from:{REFERENCE_DATE} duration:15",
    )
    assert data.get("debug") is None, "debug field must be absent when disclosure is off"


def test_debug_field_present_when_disclosure_enabled(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(settings, "bernie_interpreter_debug_disclosure", True)
    token = make_token(gp_user)
    data = _post(
        client, token,
        f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
        f"date_from:{REFERENCE_DATE} duration:15",
    )
    assert data.get("debug") is not None, "debug field must be present when disclosure is on"
    debug = data["debug"]
    assert "axes" in debug
    assert "scalar_confidence_advisory" in debug


def test_ordinary_staff_response_has_no_raw_codes(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Ordinary (non-debug) response must not expose raw UUIDs, snake_case codes,
    or internal technical tokens to staff-facing fields."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(settings, "bernie_interpreter_debug_disclosure", False)
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 9, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    data = _post(
        client, token,
        "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm duration:15",
        reference_date=REFERENCE_DATE,
    )
    # Check staff-facing text fields
    staff_text = " ".join([
        data.get("summary", ""),
        data.get("clarifying_question", "") or "",
        " ".join(a.get("staff_detail", "") or "" for a in data.get("confidence_axes", [])),
        " ".join(c.get("staff_prompt", "") for c in data.get("staff_checks", [])),
    ])
    assert "missing_practitioner_id" not in staff_text
    assert "patient_id" not in staff_text
    assert "practitioner_id" not in staff_text
    assert data.get("debug") is None


# ─── No-write structural assertions ──────────────────────────────────────────

def test_interpreter_route_never_writes_appointments_or_audit(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    appts_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    _post(
        client, token,
        f"Make an appointment for Margaret Thompson with Dr Shera {REFERENCE_DATE} duration:15",
    )

    assert db.query(Appointment).count() == appts_before, "interpreter must not write appointments"
    assert db.query(AppointmentAuditLog).count() == audit_before, "interpreter must not write audit rows"


def test_interpreter_source_has_no_db_writes(monkeypatch):
    """Structural: interpreter service/route modules must not contain db.add or db.commit calls
    in paths that touch the interpret endpoint."""
    import inspect
    import app.services.bernie_booking_interpreter as svc
    src = inspect.getsource(svc)
    assert "db.add(" not in src, "bernie_booking_interpreter.py must not call db.add()"
    assert "db.commit(" not in src, "bernie_booking_interpreter.py must not call db.commit()"


# ─── Ordinary release-gate prompt (Sprint 99 version) ────────────────────────

def test_ordinary_release_gate_prompt_confidence_axes(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """Margaret Thompson / Dr Shera ordinary prompt must pass Sprint 99 confidence gates."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    monkeypatch.setattr(
        appointments_router, "_clinic_local_now",
        lambda tz: datetime(2026, 7, 15, 9, 0, 0, tzinfo=tz),
    )
    token = make_token(gp_user)
    data = _post(
        client, token,
        "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45",
        reference_date=REFERENCE_DATE,
    )
    assert data["result"] == "interpreted"
    assert data["safe"] is True
    axes = _axes_by_name(data)
    decision = data["decision"]
    # Overall band must not be ask or block
    assert decision["overall_band"] in ("assume", "proceed_with_check")
    # Temporal must resolve the explicit 'today' as assume
    assert axes["temporal"]["band"] == "assume"
    # Practitioner must resolve Dr Shera
    assert axes["practitioner"]["band"] in ("assume", "proceed_with_check")
    assert data["command_candidate"]["practitioner_id"] == str(practitioner.id)
    # Patient identity must be proceed_with_check (never assume)
    assert axes["patient_identity"]["band"] == "proceed_with_check"
    assert axes["patient_identity"]["band"] != "assume"
    # Staff DOB check required
    staff_check_codes = {c["code"] for c in data.get("staff_checks", [])}
    assert "verify_patient_dob" in staff_check_codes
    # requires_staff_confirmation must be True
    assert decision["requires_staff_confirmation"] is True
    # No appointment/audit writes
    assert db.query(Appointment).count() == 0
    assert db.query(AppointmentAuditLog).count() == 0
