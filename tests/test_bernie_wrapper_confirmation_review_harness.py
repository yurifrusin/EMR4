"""
Deterministic Bernie wrapper -> explicit confirm-Bernie review harness.

Proves Sprint 46 confirmation_ready wrapper evidence can be submitted to the
existing confirm-Bernie endpoint for exactly one confirmed appointment/audit
write, while candidate-only, blocked, stale, and unconfirmed paths remain
non-mutating with no LLM/provider calls.
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

WRAPPER_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
REFERENCE_DATE = "2026-06-22"
EXPECTED_AUDIT_EVIDENCE = [
    "bernie_confirm_create_proposal",
    "source_slot_selection_proposal",
    "source_create_proposal",
]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _row_counts(db) -> tuple[int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    )


def _assert_row_counts_unchanged(db, expected: tuple[int, int]) -> None:
    assert _row_counts(db) == expected


def _install_forbidden_ai_provider_guard(monkeypatch) -> None:
    def forbidden_provider(*args, **kwargs):
        raise AssertionError("Bernie wrapper confirmation harness must not call AI providers")

    monkeypatch.setattr(ai_service, "_get_default_provider", forbidden_provider)


def _wrapper_body(practitioner, **overrides) -> dict:
    body = {
        "reference_date": REFERENCE_DATE,
        "command": {
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
        },
    }
    body.update(overrides)
    return body


def _post_wrapper(client, token: str, body: dict):
    return client.post(
        WRAPPER_URL,
        json=body,
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


def _wrapper_confirmation_ready_selection(
    client,
    db,
    token: str,
    practitioner,
    patient,
    reason: str,
) -> dict:
    expected_counts = _row_counts(db)

    wrapper_resp = _post_wrapper(
        client,
        token,
        _wrapper_body(
            practitioner,
            selected_candidate_index=0,
            patient_id=str(patient.id),
            reason=reason,
        ),
    )

    assert wrapper_resp.status_code == 200, wrapper_resp.text
    wrapper = wrapper_resp.json()
    assert wrapper["intent"] == "bernie_supervised_booking"
    assert wrapper["result"] == "confirmation_ready"
    assert wrapper["safe"] is True
    assert wrapper["requires_confirmation"] is True
    assert wrapper["autonomy_tier"] == "proposal"
    assert wrapper["blocks"] == []
    assert wrapper["search_proposal"]["candidates"]

    selection = wrapper["selection_proposal"]
    assert selection["intent"] == "select_slot_for_create_proposal"
    assert selection["safe"] is True
    assert selection["requires_confirmation"] is True
    assert selection["autonomy_tier"] == "proposal"
    assert selection["selected_candidate"]["appointment_date"] == REFERENCE_DATE
    assert selection["selected_candidate"]["start_time_local"] == "09:00:00"
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


def _blocked_selection_evidence() -> dict:
    return {
        "intent": "select_slot_for_create_proposal",
        "safe": False,
        "requires_confirmation": True,
        "autonomy_tier": "blocked",
        "summary": "Blocked wrapper evidence is not confirmation ready.",
        "selected_candidate": None,
        "create_proposal": None,
        "warnings": [],
        "blocks": [
            {
                "code": "wrapper_not_confirmation_ready",
                "severity": "blocked",
                "message": "Wrapper result must be confirmation_ready before confirmation.",
            }
        ],
    }


def test_wrapper_confirmation_ready_evidence_confirms_exactly_one_write(
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
    selection = _wrapper_confirmation_ready_selection(
        client,
        db,
        token,
        practitioner,
        patient,
        "Sprint 47 wrapper confirmation harness",
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


def test_wrapper_staff_review_confirm_payload_confirms_after_explicit_approval(
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
    wrapper_resp = _post_wrapper(
        client,
        token,
        _wrapper_body(
            practitioner,
            selected_candidate_index=0,
            patient_id=str(patient.id),
            reason="Sprint 48 staff review payload harness",
        ),
    )
    assert wrapper_resp.status_code == 200, wrapper_resp.text
    wrapper = wrapper_resp.json()
    review = wrapper["staff_review"]
    assert review["status"] == "confirmation_ready"
    assert review["confirmation_ready"] is True
    assert review["confirm_endpoint"] == CONFIRM_URL
    assert review["confirm_evidence"] == EXPECTED_AUDIT_EVIDENCE
    confirm_payload = review["confirm_payload"]
    assert confirm_payload["confirmed"] is False
    assert confirm_payload["selection_proposal"] == wrapper["selection_proposal"]
    appointment_before, audit_before = _row_counts(db)

    confirm_payload["confirmed"] = True
    confirm_resp = client.post(
        CONFIRM_URL,
        json=confirm_payload,
        headers=_auth(token),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["audit_evidence"] == EXPECTED_AUDIT_EVIDENCE
    assert db.query(Appointment).count() == appointment_before + 1
    assert db.query(AppointmentAuditLog).count() == audit_before + 1


def test_wrapper_confirmation_ready_but_confirmed_false_writes_nothing(
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
    selection = _wrapper_confirmation_ready_selection(
        client,
        db,
        token,
        practitioner,
        patient,
        "Sprint 47 unconfirmed wrapper harness",
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


def test_wrapper_confirmation_stale_conflict_revalidates_and_writes_nothing(
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
    selection = _wrapper_confirmation_ready_selection(
        client,
        db,
        token,
        practitioner,
        patient,
        "Sprint 47 stale wrapper harness",
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


def test_candidate_selection_required_wrapper_output_is_non_mutating(
    client,
    db,
    gp_user,
    practitioner,
    schedule,
    monkeypatch,
):
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)
    expected_counts = _row_counts(db)

    wrapper_resp = _post_wrapper(client, token, _wrapper_body(practitioner))

    assert wrapper_resp.status_code == 200, wrapper_resp.text
    wrapper = wrapper_resp.json()
    assert wrapper["result"] == "candidate_selection_required"
    assert wrapper["safe"] is True
    assert wrapper["requires_confirmation"] is False
    assert wrapper["autonomy_tier"] == "execute_with_report"
    assert wrapper["selection_proposal"] is None
    _assert_row_counts_unchanged(db, expected_counts)


def test_blocked_normalization_wrapper_output_is_non_mutating(
    client,
    db,
    gp_user,
    monkeypatch,
):
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)
    expected_counts = _row_counts(db)

    wrapper_resp = _post_wrapper(
        client,
        token,
        {
            "reference_date": REFERENCE_DATE,
            "command": {
                "date_from": "today",
                "duration_minutes": "15",
            },
        },
    )

    assert wrapper_resp.status_code == 200, wrapper_resp.text
    wrapper = wrapper_resp.json()
    assert wrapper["result"] == "blocked"
    assert wrapper["safe"] is False
    assert wrapper["autonomy_tier"] == "blocked"
    assert wrapper["search_proposal"] is None
    assert wrapper["selection_proposal"] is None
    assert wrapper["blocks"][0]["code"] == "missing_practitioner_id"
    _assert_row_counts_unchanged(db, expected_counts)


def test_non_confirmation_ready_selection_evidence_cannot_write(
    client,
    db,
    gp_user,
    monkeypatch,
):
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)
    expected_counts = _row_counts(db)

    confirm_resp = _confirm(
        client,
        token,
        _blocked_selection_evidence(),
        confirmed=True,
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["appointment"] is None
    assert data["blocks"][0]["code"] == "slot_selection_not_safe"
    assert data["blocks"][1]["code"] == "selected_candidate_required"
    assert data["blocks"][2]["code"] == "create_proposal_required"
    _assert_row_counts_unchanged(db, expected_counts)


def test_wrapper_confirmation_routes_have_no_llm_provider_or_autonomous_execution():
    route_sources = "\n".join(
        inspect.getsource(route)
        for route in (
            appointments_router.propose_bernie_supervised_booking,
            appointments_router.confirm_bernie_create_proposal,
        )
    )

    assert "generate_content" not in route_sources
    assert "Gemini" not in route_sources
    assert "AiService" not in route_sources
    assert "_get_default_provider" not in route_sources
    assert "confirm_bernie_create_proposal(" not in inspect.getsource(
        appointments_router.propose_bernie_supervised_booking
    )
    assert "_create_appointment_from_body" not in inspect.getsource(
        appointments_router.propose_bernie_supervised_booking
    )
    assert "_create_appointment_from_body" in inspect.getsource(
        appointments_router.confirm_bernie_create_proposal
    )
