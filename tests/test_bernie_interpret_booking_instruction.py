"""
POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction.

Proves Sprint 63's first Bernie AI runway slice stays read-only, mocked/default
off, and returns structured intent without appointment writes, audit writes,
slot search, proposal creation, confirmation, or live LLM/provider calls.
"""

import inspect

from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
import app.routers.appointments as appointments_router
import app.services.bernie_booking_interpreter as interpreter_service
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
REFERENCE_DATE = "2026-06-22"


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
    assert data["clarifying_question"] == (
        "Please provide practitioner_id before Bernie searches for slots."
    )
    assert data["normalization"]["safe"] is False
    assert data["blocks"][0]["code"] == "missing_practitioner_id"


def test_fake_provider_autonomous_booking_language_is_blocked(
    client,
    gp_user,
    practitioner,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)

    resp = _post_interpret(
        client,
        token,
        f"practitioner_id:{practitioner.id} date_from:today duration:15 book it",
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["result"] == "blocked"
    assert data["safety_flags"] == ["autonomous_booking_language"]
    assert data["warnings"][0]["code"] == "autonomous_booking_language"
    assert data["blocks"][0]["code"] == "staff_confirmation_required"
    assert data["normalization"]["safe"] is True


def test_interpret_booking_instruction_does_not_search_create_confirm_or_mutate():
    route_source = inspect.getsource(appointments_router.interpret_bernie_booking_instruction)
    service_source = inspect.getsource(interpreter_service)

    assert "get_booking_instruction_interpreter" in route_source
    assert "_build_slot_search_proposal" not in route_source
    assert "_build_create_appointment_proposal" not in route_source
    assert "confirm_bernie_create_proposal" not in route_source
    assert "_create_appointment_from_body" not in route_source
    assert "db.add" not in route_source
    assert "db.commit" not in route_source
    assert "_write_audit" not in route_source

    assert "normalize_slot_search_command" in service_source
    assert "_build_slot_search_proposal" not in service_source
    assert "_build_create_appointment_proposal" not in service_source
    assert "confirm_bernie_create_proposal" not in service_source
    assert "_create_appointment_from_body" not in service_source
    assert "generate_content" not in service_source
    assert "Gemini" not in service_source
    assert "vertexai" not in service_source
    assert "db.add" not in service_source
    assert "db.commit" not in service_source
    assert "_write_audit" not in service_source
