"""Sprint 97 — Bernie interpreter readiness and deterministic fallback.

Focused tests for:
- Margaret Thompson / Dr Shera ordinary prompt with natural time phrases
- Live provider unavailable → deterministic fallback (fallback=True)
- Live provider unavailable → fail-closed (fallback=False, default)
- No appointment or audit writes during interpretation
- interpreter_is_ready() readiness gate
"""

from app.config import settings
from app.models.ai_audit import AccessAiAuditLog
from app.models.appointments import Appointment, AppointmentAuditLog
import app.services.bernie_booking_interpreter as interpreter_service
from app.services.bernie_booking_interpreter import (
    InterpreterReadinessStatus,
    interpreter_is_ready,
    _parse_time_fragment,
    _extract_natural_time_constraints,
)
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
REFERENCE_DATE = "2026-07-01"


def _post_interpret(client, token, instruction: str, **overrides):
    body = {"instruction": instruction, "reference_date": REFERENCE_DATE}
    body.update(overrides)
    return client.post(
        INTERPRET_URL,
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


# ── Unit: natural time parser ─────────────────────────────────────────────────

def test_parse_time_fragment_bare_hour_assumes_pm():
    assert _parse_time_fragment("3") == "15:00"
    assert _parse_time_fragment("11") == "23:00"


def test_parse_time_fragment_explicit_pm():
    assert _parse_time_fragment("3 pm") == "15:00"
    assert _parse_time_fragment("3:45 pm") == "15:45"
    assert _parse_time_fragment("3PM") == "15:00"


def test_parse_time_fragment_dot_separator():
    assert _parse_time_fragment("3.45") == "15:45"
    assert _parse_time_fragment("3.45 pm") == "15:45"


def test_parse_time_fragment_12_noon_and_midnight():
    assert _parse_time_fragment("12") == "12:00"
    assert _parse_time_fragment("12 pm") == "12:00"
    assert _parse_time_fragment("12 am") == "00:00"


def test_parse_time_fragment_24hr_unchanged():
    assert _parse_time_fragment("14:00") == "14:00"
    assert _parse_time_fragment("15:45") == "15:45"


def test_extract_natural_time_constraints_after():
    earliest, latest = _extract_natural_time_constraints("Make a booking after 3 today")
    assert earliest == "15:00"
    assert latest is None


def test_extract_natural_time_constraints_after_pm():
    earliest, latest = _extract_natural_time_constraints("after 3 pm")
    assert earliest == "15:00"
    assert latest is None


def test_extract_natural_time_constraints_before_colon():
    earliest, latest = _extract_natural_time_constraints("appointment before 3:45")
    assert earliest is None
    assert latest == "15:45"


def test_extract_natural_time_constraints_before_dot():
    earliest, latest = _extract_natural_time_constraints("appointment before 3.45")
    assert earliest is None
    assert latest == "15:45"


def test_extract_natural_time_constraints_between():
    earliest, latest = _extract_natural_time_constraints("between 2 pm and 3:45")
    assert earliest == "14:00"
    assert latest == "15:45"


def test_extract_natural_time_constraints_between_no_meridiem():
    earliest, latest = _extract_natural_time_constraints("between 2 and 4")
    assert earliest == "14:00"
    assert latest == "16:00"


def test_extract_natural_time_no_phrase_returns_none():
    earliest, latest = _extract_natural_time_constraints("practitioner_id:abc today 15 min")
    assert earliest is None
    assert latest is None


# ── Readiness gate ────────────────────────────────────────────────────────────

def test_interpreter_readiness_false_for_disabled():
    for name in ("disabled", "", "DISABLED"):
        status = interpreter_is_ready(name)
        assert isinstance(status, InterpreterReadinessStatus)
        assert not status, f"expected not-ready for {name!r}"
        assert status.mode == "disabled"
        assert not status.live_provider_ok
        assert not status.fallback_active


def test_interpreter_readiness_fake_is_deterministic_only():
    status = interpreter_is_ready("fake")
    assert isinstance(status, InterpreterReadinessStatus)
    assert status  # truthy: requests will be served
    assert status.ready
    assert status.live_provider_ok
    assert status.mode == "deterministic_only"
    assert not status.fallback_active
    assert status.warning is None


def test_interpreter_readiness_gemini_vertex_reports_construction_status():
    """gemini_vertex must not simply return True by name — it checks construction.

    With fallback_to_deterministic=True (new default) the provider is always
    ready from a request-serving perspective, but live_provider_ok and mode
    tell the release gate whether live calls are actually set up.
    """
    status = interpreter_is_ready("gemini_vertex")
    assert isinstance(status, InterpreterReadinessStatus)
    assert status.provider == "gemini_vertex"
    # ready must reflect actual ability to serve requests (live OR fallback)
    assert status.ready == (status.live_provider_ok or status.fallback_active)
    if status.live_provider_ok:
        assert status.mode == "live"
    else:
        # import failed — fallback must be active for ready to be True
        assert status.fallback_active
        assert status.mode == "deterministic_fallback"
        assert status.warning is not None


def test_interpreter_readiness_gemini_vertex_fallback_off_fails_closed_when_import_unavailable(
    monkeypatch,
):
    """With fallback disabled and provider import broken, ready must be False."""
    import app.services.bernie_booking_interpreter as svc

    original = svc._check_live_provider_import

    def _broken():
        return False, "provider_import_failed: simulated import error"

    monkeypatch.setattr(svc, "_check_live_provider_import", _broken)

    status = interpreter_is_ready("gemini_vertex", fallback_override=False)
    assert not status
    assert not status.live_provider_ok
    assert not status.fallback_active
    assert status.mode == "disabled"
    assert status.warning is not None


def test_interpreter_readiness_gemini_vertex_fallback_on_ready_when_import_unavailable(
    monkeypatch,
):
    """With fallback enabled and provider import broken, ready must still be True."""
    import app.services.bernie_booking_interpreter as svc

    def _broken():
        return False, "provider_import_failed: simulated import error"

    monkeypatch.setattr(svc, "_check_live_provider_import", _broken)

    status = interpreter_is_ready("gemini_vertex", fallback_override=True)
    assert status  # truthy: fallback covers the gap
    assert not status.live_provider_ok
    assert status.fallback_active
    assert status.mode == "deterministic_fallback"
    assert status.warning is not None


# ── Ordinary receptionist prompt (fake/deterministic provider) ────────────────

def test_margaret_thompson_dr_shera_ordinary_prompt_deterministic(
    client, db, gp_user, practitioner, patient, monkeypatch
):
    """'Make an appointment for Margaret Thompson after 3 today with Dr Shera'
    should produce an interpreted result using the deterministic provider,
    resolving names via the router and parsing 'after 3' to 15:00."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    before_appt = db.query(Appointment).count()
    before_audit = db.query(AppointmentAuditLog).count()

    resp = _post_interpret(
        client,
        token,
        "Make an appointment for Margaret Thompson after 3 today with Dr Shera",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["result"] == "interpreted"
    assert data["provider_metadata"]["provider"] == "fake"
    # Router resolves names to UUIDs
    assert data["command_candidate"]["practitioner_id"] == str(practitioner.id)
    assert data["command_candidate"]["patient_id"] == str(patient.id)
    # Natural time phrase "after 3" → 15:00
    normalization = data["normalization"]
    assert normalization["safe"] is True
    assert normalization["constraint"]["earliest_time"] == "15:00:00"
    assert normalization["constraint"]["date_from"] == REFERENCE_DATE
    # Name-resolution warnings present
    warning_codes = {w["code"] for w in data["warnings"]}
    assert "practitioner_name_resolved" in warning_codes
    assert "patient_name_resolved_verify_identity" in warning_codes
    # No DB mutations
    assert db.query(Appointment).count() == before_appt
    assert db.query(AppointmentAuditLog).count() == before_audit


# ── Live provider unavailable — fallback behaviour ────────────────────────────

def test_live_provider_unavailable_uses_deterministic_fallback(
    client, gp_user, practitioner, monkeypatch
):
    """When gemini_vertex is configured but raises and fallback=True, the
    deterministic interpreter is used and the response signals mode=deterministic_fallback."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    monkeypatch.setattr(
        settings, "bernie_booking_interpreter_fallback_to_deterministic", True
    )

    def failing_factory():
        raise RuntimeError("Vertex AI unavailable in test")

    interpreter_service.set_live_provider_factory(failing_factory)
    token = make_token(gp_user)

    try:
        resp = _post_interpret(
            client,
            token,
            f"practitioner_id:{practitioner.id} date_from:today duration:15",
        )
    finally:
        interpreter_service.set_live_provider_factory(None)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["result"] == "interpreted"
    assert data["provider_metadata"]["provider"] == "gemini_vertex"
    assert data["provider_metadata"]["mode"] == "deterministic_fallback"
    assert data["provider_metadata"]["live_provider"] is False


def test_live_provider_unavailable_fallback_off_fails_closed(
    client, gp_user, practitioner, monkeypatch
):
    """When fallback=False (explicitly disabled) and live provider fails, return blocked."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    monkeypatch.setattr(
        settings, "bernie_booking_interpreter_fallback_to_deterministic", False
    )

    def failing_factory():
        raise RuntimeError("Vertex AI unavailable in test")

    interpreter_service.set_live_provider_factory(failing_factory)
    token = make_token(gp_user)

    try:
        resp = _post_interpret(
            client,
            token,
            f"practitioner_id:{practitioner.id} date_from:today duration:15",
        )
    finally:
        interpreter_service.set_live_provider_factory(None)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["result"] == "blocked"
    assert data["blocks"][0]["code"] == "booking_interpreter_provider_unavailable"
    assert data["provider_metadata"]["live_provider"] is True


# ── No appointment or audit writes ────────────────────────────────────────────

def test_no_appointment_or_audit_writes_on_interpretation(
    client, db, gp_user, practitioner, monkeypatch
):
    """The interpret endpoint must never write appointments, appointment audit,
    or Access AI audit rows (fake provider makes no live AI calls)."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    before_appt = db.query(Appointment).count()
    before_audit = db.query(AppointmentAuditLog).count()
    before_ai_audit = db.query(AccessAiAuditLog).count()

    resp = _post_interpret(
        client,
        token,
        f"practitioner_id:{practitioner.id} date_from:today duration:15",
    )

    assert resp.status_code == 200, resp.text
    assert db.query(Appointment).count() == before_appt
    assert db.query(AppointmentAuditLog).count() == before_audit
    assert db.query(AccessAiAuditLog).count() == before_ai_audit
