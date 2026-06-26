"""
Deterministic Bernie normalize -> search -> select -> confirm review harness.

This exercises the full supervised backend path and proves appointment/audit
writes happen only after explicit confirmation, with no LLM/provider calls or
autonomous natural-language execution.
"""

from datetime import date, datetime, time, timezone
import inspect

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentStatus,
    BookingChannel,
)
import app.routers.appointments as appointments_router
import app.services.ai.service as ai_service
from tests.conftest import make_token

NORMALIZE_URL = "/api/v1/appointments/proposals/slot-search/normalize"
NORMALIZED_SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
SELECTION_URL = "/api/v1/appointments/proposals/slot-search/selection"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
REFERENCE_DATE = "2026-06-22"
EXPECTED_AUDIT_EVIDENCE = [
    "bernie_confirm_create_proposal",
    "source_slot_selection_proposal",
    "source_create_proposal",
]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _base_command(practitioner, patient) -> dict:
    return {
        "practitioner_id": str(practitioner.id),
        "date_from": "today",
        "duration_minutes": "15",
        "patient_id": str(patient.id),
    }


def _row_counts(db) -> tuple[int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    )


def _assert_row_counts_unchanged(db, expected: tuple[int, int]) -> None:
    assert _row_counts(db) == expected


def _install_forbidden_ai_provider_guard(monkeypatch) -> None:
    def forbidden_provider(*args, **kwargs):
        raise AssertionError("Bernie confirmed flow must not call AI providers")

    monkeypatch.setattr(ai_service, "_get_default_provider", forbidden_provider)


def _normalize(client, token: str, command: dict):
    return client.post(
        NORMALIZE_URL,
        params={"reference_date": REFERENCE_DATE},
        json=command,
        headers=_auth(token),
    )


def _normalized_search(client, token: str, command: dict):
    return client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": REFERENCE_DATE},
        json=command,
        headers=_auth(token),
    )


def _select_slot(client, token: str, search: dict, patient, reason: str):
    return client.post(
        SELECTION_URL,
        json={
            "search_execution": search,
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": reason,
        },
        headers=_auth(token),
    )


def _confirm(client, token: str, selection: dict, confirmed: bool = True):
    return client.post(
        CONFIRM_URL,
        json={
            "confirmed": confirmed,
            "selection_proposal": selection,
        },
        headers=_auth(token),
    )


def _prepare_selection(client, db, token: str, practitioner, patient, reason: str) -> dict:
    expected_counts = _row_counts(db)
    command = _base_command(practitioner, patient)

    normalize_resp = _normalize(client, token, command)
    assert normalize_resp.status_code == 200, normalize_resp.text
    normalized = normalize_resp.json()
    assert normalized["safe"] is True
    assert normalized["constraint"]["date_from"] == REFERENCE_DATE
    assert normalized["constraint"]["patient_id"] == str(patient.id)
    _assert_row_counts_unchanged(db, expected_counts)

    search_resp = _normalized_search(client, token, command)
    assert search_resp.status_code == 200, search_resp.text
    search = search_resp.json()
    assert search["intent"] == "search_slots_from_command"
    assert search["safe"] is True
    assert search["normalization"]["constraint"] == normalized["constraint"]
    assert search["proposal"]["candidates"]
    candidate = search["proposal"]["candidates"][0]
    assert candidate["appointment_date"] == REFERENCE_DATE
    assert candidate["start_time_local"] == "09:00:00"
    _assert_row_counts_unchanged(db, expected_counts)

    selection_resp = _select_slot(client, token, search, patient, reason)
    assert selection_resp.status_code == 200, selection_resp.text
    selection = selection_resp.json()
    assert selection["intent"] == "select_slot_for_create_proposal"
    assert selection["safe"] is True
    assert selection["requires_confirmation"] is True
    assert selection["autonomy_tier"] == "proposal"
    assert selection["create_proposal"]["safe"] is True
    assert selection["create_proposal"]["command"]["patient_id"] == str(patient.id)
    assert selection["create_proposal"]["command"]["practitioner_id"] == str(practitioner.id)
    assert selection["create_proposal"]["command"]["appointment_date"] == REFERENCE_DATE
    assert selection["create_proposal"]["command"]["start_time_local"] == "09:00:00"
    assert selection["create_proposal"]["command"]["reason"] == reason
    _assert_row_counts_unchanged(db, expected_counts)

    return selection


def _make_conflicting_appointment(db, practice, practitioner, patient) -> Appointment:
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime(2026, 6, 21, 23, 0, tzinfo=timezone.utc),
        appointment_date=date(2026, 6, 22),
        start_time_local=time(9, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def test_confirmed_bernie_flow_writes_only_at_explicit_successful_confirmation(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
    monkeypatch,
):
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)
    selection = _prepare_selection(
        client,
        db,
        token,
        practitioner,
        patient,
        "Sprint 45 confirmed flow harness",
    )
    appointment_before, audit_before = _row_counts(db)

    confirm_resp = _confirm(client, token, selection, confirmed=True)

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["intent"] == "confirm_create_appointment"
    assert data["safe"] is True
    assert data["requires_confirmation"] is False
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["blocks"] == []
    assert data["appointment"]["patient_id"] == str(patient.id)
    assert data["appointment"]["practitioner_id"] == str(practitioner.id)
    assert data["appointment"]["appointment_date"] == REFERENCE_DATE
    assert data["appointment"]["start_time_local"] == "09:00:00"
    assert data["audit_evidence"] == EXPECTED_AUDIT_EVIDENCE
    assert db.query(Appointment).count() == appointment_before + 1
    assert db.query(AppointmentAuditLog).count() == audit_before + 1

    audit = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == data["appointment"]["id"]
    ).one()
    assert audit.action.value == "create"
    assert audit.confirmed_warnings == EXPECTED_AUDIT_EVIDENCE


def test_unconfirmed_bernie_flow_writes_no_appointment_or_audit(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
    monkeypatch,
):
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)
    selection = _prepare_selection(
        client,
        db,
        token,
        practitioner,
        patient,
        "Sprint 45 unconfirmed flow harness",
    )
    expected_counts = _row_counts(db)

    confirm_resp = _confirm(client, token, selection, confirmed=False)

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["appointment"] is None
    assert data["blocks"][0]["code"] == "explicit_confirmation_required"
    _assert_row_counts_unchanged(db, expected_counts)


def test_blocked_bernie_confirmation_writes_no_appointment_or_audit(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
    schedule,
    monkeypatch,
):
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)
    selection = _prepare_selection(
        client,
        db,
        token,
        practitioner,
        patient,
        "Sprint 45 blocked flow harness",
    )
    _make_conflicting_appointment(db, practice, practitioner, patient)
    expected_counts = _row_counts(db)

    confirm_resp = _confirm(client, token, selection, confirmed=True)

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["appointment"] is None
    assert data["blocks"][0]["code"] == "create_proposal_revalidation_blocked"
    assert data["blocks"][1]["code"] == "appointment_conflict"
    _assert_row_counts_unchanged(db, expected_counts)


def test_confirmed_bernie_flow_routes_have_no_llm_provider_or_autonomous_execution():
    route_sources = "\n".join(
        inspect.getsource(route)
        for route in (
            appointments_router.normalize_slot_search_proposal_command,
            appointments_router.propose_normalized_slot_search,
            appointments_router.propose_slot_selection_for_create,
            appointments_router.confirm_bernie_create_proposal,
        )
    )

    assert "generate_content" not in route_sources
    assert "Gemini" not in route_sources
    assert "AiService" not in route_sources
    assert "_get_default_provider" not in route_sources
    assert "normalize_slot_search_command(" not in inspect.getsource(
        appointments_router.confirm_bernie_create_proposal
    )
    assert "_build_create_appointment_proposal" in route_sources
    assert "_create_appointment_from_body" in route_sources
