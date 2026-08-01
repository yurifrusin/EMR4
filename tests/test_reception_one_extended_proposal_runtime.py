"""Proposal-only extended Reception One runtime coverage."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
import json

import pytest

from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.models.diary_events import DiaryCommittedEvent
from tests.conftest import make_token


URL = "/api/v1/appointments/proposals/reception-one/compose"
REFERENCE_DATE = date(2026, 8, 3)


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


def _appointment(
    db,
    *,
    practice,
    patient,
    practitioner,
    appt_type,
) -> Appointment:
    item = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        appointment_type_id=appt_type.id,
        appointment_date=REFERENCE_DATE,
        start_time_local=time(10, 0),
        start_time=datetime(2026, 8, 3, 0, 0, tzinfo=timezone.utc),
        duration_minutes=15,
    )
    db.add(item)
    db.flush()
    return item


def _post(client, user, instruction: str, appointment_id=None):
    body = {
        "contract_version": "reception.one.product-context-request.v1",
        "instruction": instruction,
        "reference_date": REFERENCE_DATE.isoformat(),
        "surface_id": "diary-main",
        "correlation_id": "synthetic-extended-runtime-001",
        "data_class": "authored_synthetic",
    }
    if appointment_id is not None:
        body["selected_appointment_id"] = str(appointment_id)
    return client.post(
        URL,
        json=body,
        headers={"Authorization": f"Bearer {make_token(user)}"},
    )


def _truth_counts(db) -> tuple[int, int, int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
        db.query(DiaryCommittedEvent).count(),
    )


@pytest.mark.parametrize(
    ("instruction", "goal", "operation_id", "adapter_kind", "duration"),
    [
        (
            "Move Margaret Thompson's appointment with Dr Shera to "
            "tomorrow after 2 pm but before 3 pm",
            "move",
            "proposeAppointmentUpdate",
            "update_proposal",
            15,
        ),
        (
            "Extend Margaret Thompson's appointment with Dr Shera to 30 minutes",
            "resize",
            "proposeAppointmentUpdate",
            "update_proposal",
            30,
        ),
        (
            "Cancel Margaret Thompson's appointment with Dr Shera",
            "cancel",
            "proposeAppointmentDelete",
            "delete_proposal",
            None,
        ),
    ],
)
def test_selected_appointment_families_reuse_proposal_only_api_spine(
    client,
    db,
    monkeypatch,
    practice,
    receptionist_user,
    practitioner,
    patient,
    appt_type,
    schedule,
    instruction,
    goal,
    operation_id,
    adapter_kind,
    duration,
):
    _enable(monkeypatch, practice)
    selected = _appointment(
        db,
        practice=practice,
        patient=patient,
        practitioner=practitioner,
        appt_type=appt_type,
    )
    before = _truth_counts(db)

    response = _post(
        client,
        receptionist_user,
        instruction,
        selected.id,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == "proposal_ready", json.dumps(data, indent=2)
    assert data["goal"] == goal
    assert data["operation_id"] == operation_id
    assert data["selected_appointment"]["appointment_date"] == "2026-08-03"
    assert data["selected_appointment"]["start_time_local"] == "10:00:00"
    assert data["selected_appointment"]["duration_minutes"] == 15
    assert data["adapter_review"]["adapter_kind"] == adapter_kind
    assert data["adapter_review"]["safe"] is True
    assert data["adapter_review"]["freshness_verified"] is True
    assert data["adapter_review"]["confirmation_evidence_released"] is False
    assert data["adapter_review"]["write_performed"] is False
    assert data["proposed_duration_minutes"] == duration
    assert data["requires_confirmation"] is True
    assert data["proposal_only"] is True
    assert data["write_performed"] is False
    assert data["provider_calls"] == 0
    assert _truth_counts(db) == before

    serialized = json.dumps(data, sort_keys=True)
    assert str(selected.id) not in serialized
    assert str(patient.id) not in serialized
    assert str(practitioner.id) not in serialized
    assert "signed_confirmation_evidence" not in serialized


def test_squeeze_in_is_manual_assessment_without_overbook_or_move_authority(
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
    before = _truth_counts(db)

    response = _post(
        client,
        receptionist_user,
        (
            "Can we squeeze Margaret Thompson in with Dr Shera today "
            "for 15 minutes without moving anyone?"
        ),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == "proposal_ready", json.dumps(data, indent=2)
    assert data["goal"] == "squeeze_in_assessment"
    assert data["operation_id"] is None
    assert data["adapter_review"]["adapter_kind"] == "squeeze_in_assessment"
    assert data["adapter_review"]["safe"] is True
    assert "manual_squeeze_in_review" in data["warning_codes"]
    assert data["candidate_slots"]
    assert all(
        "manual_squeeze_in_review" in item["warning_codes"]
        for item in data["candidate_slots"]
    )
    assert data["review"]["operator_ids"] == [
        "resolve_patient_reference",
        "resolve_practitioner_reference",
        "resolve_date_expression",
        "read_practitioner_schedule",
        "assess_squeeze_in_options",
    ]
    assert data["write_performed"] is False
    assert data["provider_calls"] == 0
    assert _truth_counts(db) == before


def test_cross_practice_selected_appointment_fails_before_release(
    client,
    db,
    monkeypatch,
    practice,
    practice_b,
    receptionist_user,
    practitioner,
    patient,
    patient_b,
    appt_type,
    schedule,
):
    _enable(monkeypatch, practice)
    from app.models.tenancy import Practitioner

    other_practitioner = Practitioner(
        practice_id=practice_b.id,
        first_name="Billy",
        last_name="Other",
        ahpra_number="MED0007654321",
    )
    db.add(other_practitioner)
    db.flush()
    other = Appointment(
        practice_id=practice_b.id,
        patient_id=patient_b.id,
        practitioner_id=other_practitioner.id,
        appointment_date=REFERENCE_DATE,
        start_time_local=time(11, 0),
        start_time=datetime(2026, 8, 3, 1, 0, tzinfo=timezone.utc),
        duration_minutes=15,
    )
    db.add(other)
    db.flush()
    before = _truth_counts(db)

    response = _post(
        client,
        receptionist_user,
        "Cancel Margaret Thompson's appointment with Dr Shera",
        other.id,
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "selected_appointment_not_found"
    assert _truth_counts(db) == before
