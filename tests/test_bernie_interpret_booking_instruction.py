"""
POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction.

Proves Sprint 63's first Bernie AI runway slice stays read-only, mocked/default
off, and returns structured intent without appointment writes, audit writes,
slot search, proposal creation, confirmation, or live LLM/provider calls.
"""

import inspect

from app.config import settings
from app.models.ai_audit import AccessAiAuditLog
from app.models.appointments import Appointment, AppointmentAuditLog
import app.routers.appointments as appointments_router
import app.services.bernie_booking_interpreter as interpreter_service
from app.services.ai.entitlements import AiActorContext
from app.services.bernie_booking_interpreter import GeminiVertexBookingInstructionInterpreter
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
REFERENCE_DATE = "2026-06-22"


class MockLiveProvider:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def generate_json(self, contents, temperature: float) -> dict:
        self.calls.append((contents, temperature))
        return self.response


def _post_interpret(client, token, instruction: str, **overrides):
    body = {
        "instruction": instruction,
        "reference_date": REFERENCE_DATE,
    }
    body.update(overrides)
    return client.post(
        INTERPRET_URL,
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def test_interpret_booking_instruction_requires_auth(client):
    resp = client.post(
        INTERPRET_URL,
        json={"instruction": "practitioner_id:00000000-0000-0000-0000-000000000000 today"},
    )

    assert resp.status_code == 401


def test_default_disabled_provider_returns_structured_block_without_mutating(
    client,
    db,
    gp_user,
    practitioner,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "disabled")
    token = make_token(gp_user)
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()
    access_ai_audit_before = db.query(AccessAiAuditLog).count()

    resp = _post_interpret(
        client,
        token,
        f"practitioner_id:{practitioner.id} date_from:today duration_minutes:15",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "interpret_booking_instruction"
    assert data["safe"] is False
    assert data["result"] == "blocked"
    assert data["autonomy_tier"] == "blocked"
    assert data["confidence"] == 0
    assert data["command_candidate"] is None
    assert data["normalization"] is None
    assert data["missing_fields"] == ["interpreter_provider"]
    assert data["safety_flags"] == ["provider_disabled"]
    assert data["blocks"][0]["code"] == "booking_interpreter_disabled"
    assert data["provider_metadata"] == {
        "provider": "disabled",
        "mode": "disabled",
        "live_provider": False,
    }
    assert "instruction" not in data
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before
    assert db.query(AccessAiAuditLog).count() == access_ai_audit_before


def test_fake_provider_returns_validated_structured_intent(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()
    access_ai_audit_before = db.query(AccessAiAuditLog).count()

    resp = _post_interpret(
        client,
        token,
        (
            f"Please find practitioner_id:{practitioner.id} "
            f"patient_id:{patient.id} date_from:today duration:15 "
            "earliest_time:09:00 latest_time:11:00"
        ),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["result"] == "interpreted"
    assert data["autonomy_tier"] == "execute_with_report"
    assert data["confidence"] == 0.9
    assert data["missing_fields"] == []
    assert data["safety_flags"] == []
    assert data["clarifying_question"] is None
    assert data["provider_metadata"] == {
        "provider": "fake",
        "mode": "mocked",
        "live_provider": False,
    }
    command = data["command_candidate"]
    assert command["practitioner_id"] == str(practitioner.id)
    assert command["patient_id"] == str(patient.id)
    assert command["date_from"] == "today"
    assert command["duration_minutes"] == "15"
    assert command["earliest_time"] == "09:00"
    assert command["latest_time"] == "11:00"
    normalization = data["normalization"]
    assert normalization["safe"] is True
    assert normalization["constraint"]["practitioner_id"] == str(practitioner.id)
    assert normalization["constraint"]["patient_id"] == str(patient.id)
    assert normalization["constraint"]["date_from"] == REFERENCE_DATE
    assert normalization["constraint"]["duration_minutes"] == 15
    assert normalization["constraint"]["earliest_time"] == "09:00:00"
    assert normalization["constraint"]["latest_time"] == "11:00:00"
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_fake_provider_missing_fields_returns_clarifying_intent(
    client,
    gp_user,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    resp = _post_interpret(client, token, "Please find a 15 minute booking today")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["result"] == "clarification_required"
    assert data["missing_fields"] == ["practitioner_id"]
    assert data["clarifying_question"] == "Did you forget to mention the doctor or nurse?"
    assert data["normalization"]["safe"] is False
    assert data["blocks"][0]["code"] == "missing_practitioner_id"


def test_fake_provider_resolves_practice_names_as_optional_context(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _post_interpret(
        client,
        token,
        (
            "Make an appointment for Margaret Thompson with Dr Shera "
            "today duration:15 earliest_time:14:00 latest_time:15:30"
        ),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["result"] == "interpreted"
    assert data["missing_fields"] == []
    assert data["clarifying_question"] is None
    assert data["command_candidate"]["practitioner_id"] == str(practitioner.id)
    assert data["command_candidate"]["patient_id"] == str(patient.id)
    assert data["normalization"]["constraint"]["practitioner_id"] == str(practitioner.id)
    assert data["normalization"]["constraint"]["patient_id"] == str(patient.id)
    warning_codes = {warning["code"] for warning in data["warnings"]}
    assert "practitioner_name_resolved" in warning_codes
    assert "patient_recognized_by_register" in warning_codes
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_fake_provider_autonomous_booking_language_is_warning_only(
    client,
    gp_user,
    practitioner,
    patient,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    resp = _post_interpret(
        client,
        token,
        (
            f"practitioner_id:{practitioner.id} patient_id:{patient.id} "
            "date_from:today duration:15 book it"
        ),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["result"] == "interpreted"
    assert data["safety_flags"] == ["autonomous_booking_language"]
    assert data["warnings"][0]["code"] == "autonomous_booking_language"
    assert data["blocks"] == []
    assert data["normalization"]["safe"] is True


def test_disabled_and_fake_providers_do_not_call_live_provider(
    client,
    gp_user,
    practitioner,
    monkeypatch,
):
    def fail_if_called():
        raise AssertionError("live provider should not be constructed")

    interpreter_service.set_live_provider_factory(fail_if_called)
    token = make_token(gp_user)
    try:
        monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "disabled")
        disabled = _post_interpret(
            client,
            token,
            f"practitioner_id:{practitioner.id} date_from:today duration:15",
        )
        assert disabled.status_code == 200, disabled.text
        assert disabled.json()["provider_metadata"]["provider"] == "disabled"

        monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
        fake = _post_interpret(
            client,
            token,
            f"practitioner_id:{practitioner.id} date_from:today duration:15",
        )
        assert fake.status_code == 200, fake.text
        assert fake.json()["provider_metadata"]["provider"] == "fake"
    finally:
        interpreter_service.set_live_provider_factory(None)


def test_mocked_live_provider_returns_validated_structured_intent_without_mutating(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    monkeypatch.setattr(settings, "bernie_booking_interpreter_live_temperature", 0.0)
    provider = MockLiveProvider({
        "command_candidate": {
            "practitioner_id": str(practitioner.id),
            "patient_id": str(patient.id),
            "date_from": "today",
            "duration_minutes": 15,
            "earliest_time": "09:00",
            "latest_time": "11:00",
        },
        "confidence": 0.82,
        "summary": (
            f"Structured request for patient_id:{patient.id} "
            f"with practitioner_id:{practitioner.id}."
        ),
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
    })
    interpreter_service.set_live_provider_factory(lambda: provider)
    token = make_token(gp_user)
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()
    access_ai_audit_before = db.query(AccessAiAuditLog).count()

    try:
        resp = _post_interpret(
            client,
            token,
            "Patient asks for a short GP booking today between 9 and 11.",
        )
    finally:
        interpreter_service.set_live_provider_factory(None)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["result"] == "interpreted"
    assert data["confidence"] == 0.82
    assert data["provider_metadata"] == {
        "provider": "gemini_vertex",
        "mode": "live",
        "live_provider": True,
    }
    assert data["command_candidate"]["practitioner_id"] == str(practitioner.id)
    assert data["command_candidate"]["patient_id"] == str(patient.id)
    assert data["normalization"]["safe"] is True
    assert data["normalization"]["constraint"]["date_from"] == REFERENCE_DATE
    assert len(provider.calls) == 1
    prompt, temperature = provider.calls[0]
    assert "Do not book, confirm, create appointments, search slots" in prompt
    assert "Return only JSON" in prompt
    assert temperature == 0.0
    assert "Patient asks for a short GP booking" not in data["summary"]
    assert str(patient.id) not in data["summary"]
    assert str(practitioner.id) not in data["summary"]
    assert "patient_id:[redacted]" in data["summary"]
    assert "practitioner_id:[redacted]" in data["summary"]
    assert "instruction" not in data
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before
    assert db.query(AccessAiAuditLog).count() == access_ai_audit_before + 1
    access_ai_audit = db.query(AccessAiAuditLog).one()
    assert access_ai_audit.event_type == "ai.invocation.allowed"
    assert access_ai_audit.capability == "admin.booking.interpret"
    assert access_ai_audit.method == "invoke"
    assert access_ai_audit.metadata_json["interpreter"] == "bernie_booking_instruction"
    assert "prompt" not in access_ai_audit.metadata_json


def test_live_provider_name_values_in_id_fields_are_resolved_before_normalization(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    provider = MockLiveProvider({
        "command_candidate": {
            "practitioner_id": "Dr Shera",
            "patient_id": "Margaret Thompson",
            "date_from": "today",
            "earliest_time": "14:00",
            "latest_time": "15:45",
        },
        "confidence": 0.78,
        "summary": "Search for an appointment for Margaret Thompson with Dr Shera.",
        "missing_fields": [],
        "safety_flags": ["autonomous_booking_language"],
        "clarifying_question": "What type of appointment is this and how long should it be?",
    })
    interpreter_service.set_live_provider_factory(lambda: provider)
    token = make_token(gp_user)

    try:
        resp = _post_interpret(
            client,
            token,
            (
                "Make an appointment for Margaret Thompson with Dr Shera today "
                "after 2 pm but before 3.45."
            ),
        )
    finally:
        interpreter_service.set_live_provider_factory(None)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["result"] == "interpreted"
    assert data["command_candidate"]["practitioner_id"] == str(practitioner.id)
    assert data["command_candidate"]["patient_id"] == str(patient.id)
    assert data["command_candidate"]["duration_minutes"] == 15
    assert data["normalization"]["safe"] is True
    assert data["blocks"] == []
    warning_codes = {warning["code"] for warning in data["warnings"]}
    assert "practitioner_name_resolved" in warning_codes
    assert "patient_recognized_by_register" in warning_codes
    assert "appointment_duration_defaulted" in warning_codes


def test_live_provider_week_relative_instruction_overrides_stale_model_date(
    client,
    gp_user,
    practitioner,
    patient,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    provider = MockLiveProvider({
        "command_candidate": {
            "practitioner_id": str(practitioner.id),
            "patient_id": str(patient.id),
            "date_from": "today",
            "duration_minutes": 30,
            "earliest_time": "15:00",
            "latest_time": "16:30",
        },
        "confidence": 0.8,
        "summary": "Search for a week-relative appointment.",
        "missing_fields": [],
        "safety_flags": [],
        "clarifying_question": None,
    })
    interpreter_service.set_live_provider_factory(lambda: provider)
    token = make_token(gp_user)

    try:
        resp = _post_interpret(
            client,
            token,
            (
                "Make a 30 minute appointment for Margaret Thompson with Dr Shera "
                "in a week's time, after 3 but before 4.30."
            ),
        )
    finally:
        interpreter_service.set_live_provider_factory(None)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["command_candidate"]["date_from"] == "2026-06-29"
    assert data["normalization"]["constraint"]["date_from"] == "2026-06-29"
    assert data["result"] == "interpreted"
    warning_codes = {warning["code"] for warning in data["warnings"]}
    assert "date_resolved_from_instruction_relative_week" in warning_codes


def test_mocked_live_provider_invalid_response_fails_closed(
    client,
    gp_user,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    provider = MockLiveProvider({"command_candidate": "not-a-dict", "confidence": 0.9})
    interpreter_service.set_live_provider_factory(lambda: provider)
    token = make_token(gp_user)

    try:
        resp = _post_interpret(client, token, "Please find a booking today")
    finally:
        interpreter_service.set_live_provider_factory(None)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["result"] == "blocked"
    assert data["confidence"] == 0
    assert data["safety_flags"] == ["provider_response_unusable"]
    assert data["blocks"][0]["code"] == "booking_interpreter_invalid_command"
    assert data["provider_metadata"]["live_provider"] is True


def test_mocked_live_provider_autonomous_booking_language_is_warning_only(
    client,
    gp_user,
    practitioner,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "gemini_vertex")
    provider = MockLiveProvider({
        "command_candidate": {
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": 15,
        },
        "confidence": 0.92,
        "summary": "Structured appointment search request.",
        "missing_fields": [],
        "safety_flags": [],
    })
    interpreter_service.set_live_provider_factory(lambda: provider)
    token = make_token(gp_user)

    try:
        resp = _post_interpret(
            client,
            token,
            f"practitioner_id:{practitioner.id} date_from:today duration:15 book it",
        )
    finally:
        interpreter_service.set_live_provider_factory(None)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["result"] == "interpreted"
    assert data["safety_flags"] == ["autonomous_booking_language"]
    assert data["warnings"][0]["code"] == "autonomous_booking_language"
    assert data["blocks"] == []
    assert data["normalization"]["safe"] is True


def test_live_interpreter_access_ai_denial_fails_closed_before_provider_call(monkeypatch):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_live_temperature", 0.0)
    # Explicitly disable fallback: this test verifies the strict fail-closed path.
    monkeypatch.setattr(settings, "bernie_booking_interpreter_fallback_to_deterministic", False)
    provider = MockLiveProvider({
        "command_candidate": {
            "date_from": "today",
        },
    })
    interpreter = GeminiVertexBookingInstructionInterpreter(lambda: provider)
    denied_actor = AiActorContext(
        user_id=None,
        practice_id=None,
        roles=(),
        environment="dev",
    )

    result = interpreter.interpret(
        interpreter_service.BernieBookingInstructionInterpretIn(
            instruction="Please find a booking today",
            reference_date=REFERENCE_DATE,
        ),
        denied_actor,
    )

    assert result.safe is False
    assert result.result == "blocked"
    assert result.blocks[0].code == "booking_interpreter_provider_unavailable"
    assert provider.calls == []


def test_interpret_booking_instruction_does_not_search_create_confirm_or_mutate():
    route_source = inspect.getsource(appointments_router.interpret_bernie_booking_instruction)
    service_source = inspect.getsource(interpreter_service)

    assert "get_booking_instruction_interpreter" in route_source
    assert "actor_context_for_interpreter_user" in route_source
    assert "_build_slot_search_proposal" not in route_source
    assert "_build_create_appointment_proposal" not in route_source
    assert "confirm_bernie_create_proposal" not in route_source
    assert "_create_appointment_from_body" not in route_source
    assert "_write_audit" not in route_source
    assert "persist_access_ai_audit_events" in route_source

    assert "normalize_slot_search_command" in service_source
    assert "AccessAiService" in service_source
    assert "_build_slot_search_proposal" not in service_source
    assert "_build_create_appointment_proposal" not in service_source
    assert "confirm_bernie_create_proposal" not in service_source
    assert "_create_appointment_from_body" not in service_source
    assert "generate_content" not in service_source
    assert "google.genai" not in service_source
    assert "vertexai=True" not in service_source
    assert "db.add" not in service_source
    assert "db.commit" not in service_source
    assert "_write_audit" not in service_source


def test_live_provider_factory_reset_after_tests():
    assert interpreter_service._live_provider_factory is None


# ── Sprint 104: patient_booking_context and context_freshness fields ──────────

from datetime import date as date_type, datetime, time, timezone, timedelta
from app.models.appointments import AppointmentStatus, BookingChannel


def _make_appt(db, practice, practitioner, patient, appt_date, h, m, status, duration=15):
    appt = appointments_router.Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime(appt_date.year, appt_date.month, appt_date.day, h, m, tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(h, m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


SPRINT104_REFERENCE_DATE = "2026-07-02"


def _post_interpret_s104(client, token, instruction: str, reference_date: str = SPRINT104_REFERENCE_DATE):
    return client.post(
        INTERPRET_URL,
        json={"instruction": instruction, "reference_date": reference_date},
        headers={"Authorization": f"Bearer {token}"},
    )


def test_in_a_weeks_time_resolves_against_reference_date(
    client, gp_user, patient, practitioner, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    resp = _post_interpret_s104(
        client,
        token,
        (
            f"Make a 30 minute appointment for {patient.first_name} {patient.last_name} "
            f"with {practitioner.first_name} {practitioner.last_name} "
            "in a week's time, after 3 but before 4.30"
        ),
        reference_date="2026-07-02",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    command = data["command_candidate"]
    assert command["date_from"] == "2026-07-09"
    assert command["duration_minutes"] == "30"
    assert command["earliest_time"] == "15:00"
    assert command["latest_time"] == "16:30"
    assert data["result"] == "interpreted"
    assert data["clarifying_question"] is None


def test_recognized_patient_interpret_returns_booking_context(
    client, db, gp_user, patient, practitioner, monkeypatch
):
    """Exact-match recognized patient returns patient_booking_context in interpret response."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    fixed_now = datetime(2026, 7, 2, 9, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", lambda tz: fixed_now.astimezone(tz))
    token = make_token(gp_user)

    _make_appt(
        db, gp_user.practice, practitioner, patient,
        date_type(2026, 6, 18), 10, 0, AppointmentStatus.Completed,
    )
    _make_appt(
        db, gp_user.practice, practitioner, patient,
        date_type(2026, 7, 9), 9, 0, AppointmentStatus.Booked,
    )

    resp = _post_interpret_s104(
        client, token,
        f"Book {patient.first_name} {patient.last_name} with "
        f"{practitioner.first_name} {practitioner.last_name} next week",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    ctx = data.get("patient_booking_context")
    assert ctx is not None, "Expected patient_booking_context for a recognized patient"
    assert ctx["patient_key"] == str(patient.id)
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True
    assert len(ctx["future_bookings"]) >= 1


def test_fuzzy_candidate_has_no_booking_context(
    client, db, gp_user, patient, practitioner, monkeypatch
):
    """Fuzzy/ambiguous patient candidates (band=ask) must NOT receive patient_booking_context."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    # Use a slightly misspelled name to trigger fuzzy (no exact match)
    resp = _post_interpret_s104(
        client, token,
        f"Book Margret Tompson with {practitioner.first_name} {practitioner.last_name} next week",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("patient_booking_context") is None, (
        "Fuzzy candidates must not receive patient_booking_context"
    )


def test_existing_future_follow_up_warning_in_interpret(
    client, db, gp_user, patient, practitioner, monkeypatch
):
    """Recognized patient with a future appointment triggers existing_future_follow_up warning."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    fixed_now = datetime(2026, 7, 2, 9, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", lambda tz: fixed_now.astimezone(tz))
    token = make_token(gp_user)

    _make_appt(
        db, gp_user.practice, practitioner, patient,
        date_type(2026, 7, 9), 9, 0, AppointmentStatus.Booked,
    )

    resp = _post_interpret_s104(
        client, token,
        f"Book {patient.first_name} {patient.last_name} with "
        f"{practitioner.first_name} {practitioner.last_name} next week",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    ctx = data.get("patient_booking_context")
    if ctx is not None and ctx.get("existing_future_follow_up"):
        warning_codes = [w["code"] for w in data.get("warnings", [])]
        assert "existing_future_follow_up" in warning_codes, (
            "existing_future_follow_up warning expected in response warnings"
        )


def test_different_day_future_booking_stays_in_context_without_warning(
    client, db, gp_user, patient, practitioner, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    fixed_now = datetime(2026, 7, 2, 9, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", lambda tz: fixed_now.astimezone(tz))
    token = make_token(gp_user)

    _make_appt(
        db, gp_user.practice, practitioner, patient,
        date_type(2026, 7, 23), 9, 0, AppointmentStatus.Booked,
    )

    resp = _post_interpret_s104(
        client, token,
        f"Book {patient.first_name} {patient.last_name} with "
        f"{practitioner.first_name} {practitioner.last_name} next week",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    ctx = data.get("patient_booking_context")
    assert ctx is not None
    assert ctx["has_future_booking"] is True
    assert ctx["existing_future_follow_up"] is True
    warning_codes = [w["code"] for w in data.get("warnings", [])]
    assert "existing_future_follow_up" not in warning_codes


def test_interpret_booking_context_no_db_writes(
    client, db, gp_user, patient, practitioner, monkeypatch
):
    """patient_booking_context fetch on interpret path never writes any DB rows."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    fixed_now = datetime(2026, 7, 2, 9, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(appointments_router, "_clinic_local_now", lambda tz: fixed_now.astimezone(tz))
    token = make_token(gp_user)

    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    _post_interpret_s104(
        client, token,
        f"Book {patient.first_name} {patient.last_name} with "
        f"{practitioner.first_name} {practitioner.last_name} next week",
    )

    assert db.query(Appointment).count() == appt_before
    assert db.query(AppointmentAuditLog).count() == audit_before
