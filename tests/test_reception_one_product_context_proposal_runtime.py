"""Default-off Reception One product-context proposal runtime.

The route is deliberately narrower than the legacy Bernie interpreter gate:
authored-synthetic development data, exact practice allowlisting, bounded
practice-scoped reads, opaque planner handles, typed proofreader admission and
proposal-only release.
"""

from __future__ import annotations

import json

from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
from tests.conftest import make_token


URL = "/api/v1/appointments/proposals/reception-one/compose"


def _body(instruction: str) -> dict[str, str]:
    return {
        "contract_version": "reception.one.product-context-request.v1",
        "instruction": instruction,
        "reference_date": "2026-06-21",
        "surface_id": "diary-main",
        "correlation_id": "synthetic-runtime-test-001",
        "data_class": "authored_synthetic",
    }


def _post(client, user, instruction: str):
    return client.post(
        URL,
        json=_body(instruction),
        headers={"Authorization": f"Bearer {make_token(user)}"},
    )


def _enable(monkeypatch, practice) -> None:
    monkeypatch.setattr(
        settings,
        "reception_one_product_context_runtime_enabled",
        True,
    )
    monkeypatch.setattr(
        settings,
        "reception_one_product_context_synthetic_practice_ids",
        str(practice.id),
    )
    monkeypatch.setattr(settings, "environment", "dev")


def test_route_is_default_off(
    client,
    receptionist_user,
    practitioner,
    patient,
):
    response = _post(
        client,
        receptionist_user,
        (
            "Make an appointment for Margaret Thompson with Dr Shera "
            "tomorrow morning."
        ),
    )
    assert response.status_code == 404


def test_authentication_is_required(client):
    response = client.post(
        URL,
        json=_body("Make an appointment tomorrow."),
    )
    assert response.status_code == 401


def test_non_dev_environment_fails_closed(
    client,
    monkeypatch,
    practice,
    receptionist_user,
):
    _enable(monkeypatch, practice)
    monkeypatch.setattr(settings, "environment", "production")
    response = _post(
        client,
        receptionist_user,
        "Make an appointment tomorrow.",
    )
    assert response.status_code == 403


def test_unlisted_practice_fails_before_context_read(
    client,
    monkeypatch,
    practice,
    gp_user_b,
):
    _enable(monkeypatch, practice)
    response = _post(
        client,
        gp_user_b,
        "Make an appointment tomorrow.",
    )
    assert response.status_code == 403


def test_ordinary_create_request_returns_typed_non_mutating_proposal(
    client,
    db,
    monkeypatch,
    practice,
    receptionist_user,
    practitioner,
    patient,
    schedule,
):
    _enable(monkeypatch, practice)
    legacy_provider_before = settings.bernie_booking_interpreter_provider
    appointment_count_before = db.query(Appointment).count()
    audit_count_before = db.query(AppointmentAuditLog).count()

    response = _post(
        client,
        receptionist_user,
        (
            "Make an appointment for Margaret Thompson with Dr Shera "
            "tomorrow morning."
        ),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == "proposal_ready", json.dumps(data, indent=2)
    assert data["safe"] is True
    assert data["data_class"] == "authored_synthetic"
    assert data["patient_display"] == "Margaret Thompson"
    assert data["practitioner_display"] == "Dr Shera"
    assert data["goal"] == "create"
    assert data["operation_id"] == "proposeAppointmentCreate"
    assert data["candidate_slots"]
    assert all(
        slot["duration_minutes"] == 15 for slot in data["candidate_slots"]
    )
    assert data["review"]["disposition"] == "admit"
    assert data["review"]["operator_ids"] == [
        "resolve_patient_reference",
        "resolve_practitioner_reference",
        "resolve_date_expression",
        "search_available_slots",
        "prepare_create_proposal",
    ]
    assert data["review"]["safe_repairs"] == []
    assert data["requires_confirmation"] is True
    assert data["proposal_only"] is True
    assert data["write_performed"] is False
    assert data["confirmation_performed"] is False
    assert data["provider_calls"] == 0
    assert data["model_database_access"] is False
    assert data["database_reads_performed"] is True
    assert data["legacy_interpreter_gate_changed"] is False

    serialized = json.dumps(data, sort_keys=True)
    assert str(patient.id) not in serialized
    assert str(practitioner.id) not in serialized
    assert db.query(Appointment).count() == appointment_count_before
    assert db.query(AppointmentAuditLog).count() == audit_count_before
    assert settings.bernie_booking_interpreter_provider == legacy_provider_before


def test_unknown_patient_releases_only_typed_clarification(
    client,
    db,
    monkeypatch,
    practice,
    receptionist_user,
    practitioner,
    schedule,
):
    _enable(monkeypatch, practice)
    appointment_count_before = db.query(Appointment).count()
    audit_count_before = db.query(AppointmentAuditLog).count()

    response = _post(
        client,
        receptionist_user,
        (
            "Make an appointment for Unknown Person with Dr Shera "
            "tomorrow morning."
        ),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == "clarification_required", json.dumps(data, indent=2)
    assert data["safe"] is True
    assert data["patient_handle"] is None
    assert data["candidate_slots"] == []
    assert data["review"]["disposition"] == "admit"
    assert data["review"]["operator_ids"] == ["request_clarification"]
    assert data["write_performed"] is False
    assert data["provider_calls"] == 0
    assert db.query(Appointment).count() == appointment_count_before
    assert db.query(AppointmentAuditLog).count() == audit_count_before


def test_request_handles_are_request_scoped_and_extra_input_is_rejected(
    client,
    monkeypatch,
    practice,
    receptionist_user,
    practitioner,
    patient,
    schedule,
):
    _enable(monkeypatch, practice)
    instruction = (
        "Make an appointment for Margaret Thompson with Dr Shera "
        "tomorrow morning."
    )
    first = _post(client, receptionist_user, instruction)
    second = _post(client, receptionist_user, instruction)
    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["patient_handle"] != second.json()["patient_handle"]
    assert first.json()["request_id"] != second.json()["request_id"]

    invalid_body = _body(instruction)
    invalid_body["unexpected_authority"] = True
    rejected = client.post(
        URL,
        json=invalid_body,
        headers={
            "Authorization": f"Bearer {make_token(receptionist_user)}"
        },
    )
    assert rejected.status_code == 422
