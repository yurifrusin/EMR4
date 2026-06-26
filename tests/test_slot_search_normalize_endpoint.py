"""
POST /api/v1/appointments/proposals/slot-search/normalize.

Deterministic, non-mutating route contract for future Bernie/reception command
normalization. The endpoint normalizes SlotSearchCommandIn into
SlotSearchCommandResult only; it must not run slot search, call LLMs, or write
appointments/audit rows.
"""

from datetime import date
import inspect
import uuid

from app.models.appointments import Appointment, AppointmentAuditLog
from app.schemas.appointments import (
    SlotSearchCommandResult,
    SlotSearchProposalIn,
)
import app.routers.appointments as appointments_router
from tests.conftest import make_token

NORMALIZE_URL = "/api/v1/appointments/proposals/slot-search/normalize"
REFERENCE_DATE = "2026-06-22"


def _normalize(client, token, body: dict, reference_date: str = REFERENCE_DATE):
    return client.post(
        NORMALIZE_URL,
        params={"reference_date": reference_date},
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def _base_body(practitioner) -> dict:
    return {
        "practitioner_id": str(practitioner.id),
        "date_from": "2026-06-22",
        "duration_minutes": 15,
    }


def test_normalize_endpoint_requires_auth(client, practitioner):
    resp = client.post(
        NORMALIZE_URL,
        params={"reference_date": REFERENCE_DATE},
        json=_base_body(practitioner),
    )

    assert resp.status_code == 401


def test_normalize_endpoint_requires_explicit_reference_date(client, gp_user, practitioner):
    resp = client.post(
        NORMALIZE_URL,
        json=_base_body(practitioner),
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )

    assert resp.status_code == 422


def test_normalize_endpoint_returns_result_shape_and_slot_search_proposal_constraint(
    client,
    gp_user,
    practitioner,
    appt_type,
    patient,
):
    token = make_token(gp_user)
    resp = _normalize(client, token, {
        "practitioner_id": str(practitioner.id),
        "date_from": "today",
        "duration_minutes": "30",
        "appointment_type_id": str(appt_type.id),
        "patient_id": str(patient.id),
        "earliest_time": "09:00",
        "latest_time": "12:00",
        "unknown_llm_key": "ignored",
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert set(data) == {"safe", "constraint", "warnings", "blocks", "summary"}
    assert data["safe"] is True
    assert data["warnings"] == []
    assert data["blocks"] == []
    assert data["summary"].startswith("Slot search normalized:")

    constraint = SlotSearchProposalIn(**data["constraint"])
    assert constraint.practitioner_id == practitioner.id
    assert constraint.date_from == date(2026, 6, 22)
    assert constraint.date_to == date(2026, 6, 22)
    assert constraint.duration_minutes == 30
    assert constraint.appointment_type_id == appt_type.id
    assert constraint.patient_id == patient.id
    assert constraint.earliest_time.isoformat() == "09:00:00"
    assert constraint.latest_time.isoformat() == "12:00:00"


def test_normalize_endpoint_deterministically_uses_supplied_reference_date(
    client,
    gp_user,
    practitioner,
):
    token = make_token(gp_user)
    body = {"practitioner_id": str(practitioner.id), "date_from": "today"}

    first = _normalize(client, token, body, reference_date="2026-06-22")
    second = _normalize(client, token, body, reference_date="2026-07-15")

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["constraint"]["date_from"] == "2026-06-22"
    assert second.json()["constraint"]["date_from"] == "2026-07-15"


def test_normalize_endpoint_invalid_command_returns_blocked_result(
    client,
    gp_user,
):
    token = make_token(gp_user)
    resp = _normalize(client, token, {
        "practitioner_id": "not-a-uuid",
        "date_from": "not-a-date",
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["constraint"] is None
    codes = {block["code"] for block in data["blocks"]}
    assert "invalid_practitioner_id" in codes
    assert "invalid_date_from" in codes


def test_normalize_endpoint_invokes_normalizer_with_explicit_reference_date(
    client,
    gp_user,
    practitioner,
    monkeypatch,
):
    token = make_token(gp_user)
    captured = {}
    constraint = SlotSearchProposalIn(
        practitioner_id=uuid.uuid4(),
        date_from=date(2026, 6, 22),
        date_to=date(2026, 6, 22),
        duration_minutes=15,
    )

    def fake_normalizer(payload, *, reference_date):
        captured["payload"] = payload
        captured["reference_date"] = reference_date
        return SlotSearchCommandResult(
            safe=True,
            constraint=constraint,
            warnings=[],
            blocks=[],
            summary="stubbed normalizer",
        )

    monkeypatch.setattr(
        appointments_router,
        "normalize_slot_search_command",
        fake_normalizer,
    )

    resp = _normalize(client, token, {
        "practitioner_id": str(practitioner.id),
        "date_from": "today",
    })

    assert resp.status_code == 200, resp.text
    assert captured["payload"].practitioner_id == str(practitioner.id)
    assert captured["reference_date"] == date(2026, 6, 22)
    assert resp.json()["summary"] == "stubbed normalizer"


def test_normalize_endpoint_does_not_execute_slot_search_or_llm(
    client,
    gp_user,
    practitioner,
    monkeypatch,
):
    token = make_token(gp_user)

    def forbidden(*args, **kwargs):
        raise AssertionError("normalize endpoint must not execute slot search")

    monkeypatch.setattr(appointments_router, "_resolve_day_schedule", forbidden)
    monkeypatch.setattr(appointments_router, "_find_conflicting_appointment", forbidden)
    monkeypatch.setattr(appointments_router, "_get_break_overlaps", forbidden)

    resp = _normalize(client, token, _base_body(practitioner))

    assert resp.status_code == 200, resp.text
    source = inspect.getsource(appointments_router.normalize_slot_search_proposal_command)
    assert "generate_content" not in source
    assert "slot_search" not in source.lower().replace("normalize_slot_search", "")


def test_normalize_endpoint_writes_no_appointments_or_audit_rows(
    client,
    db,
    gp_user,
    practitioner,
):
    token = make_token(gp_user)
    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _normalize(client, token, _base_body(practitioner))

    assert resp.status_code == 200, resp.text
    assert db.query(Appointment).count() == appt_before
    assert db.query(AppointmentAuditLog).count() == audit_before
