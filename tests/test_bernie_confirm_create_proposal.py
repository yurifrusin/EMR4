"""
POST /api/v1/appointments/proposals/create/confirm-bernie.

Proves supervised Bernie slot-selection/create-proposal evidence only mutates
after explicit confirmation, then writes exactly one appointment and bounded
audit evidence. Blocked, stale, mismatched, or unconfirmed paths write nothing.
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

NORMALIZED_SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
SELECTION_URL = "/api/v1/appointments/proposals/slot-search/selection"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
REFERENCE_DATE = "2026-06-22"


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
        raise AssertionError("Bernie confirmation must not instantiate or call AI providers")

    monkeypatch.setattr(ai_service, "_get_default_provider", forbidden_provider)


def _search_and_select(client, token: str, practitioner, patient, reason="Bernie confirmed follow-up"):
    search_resp = client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": REFERENCE_DATE},
        json={
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
            "patient_id": str(patient.id),
        },
        headers=_auth(token),
    )
    assert search_resp.status_code == 200, search_resp.text
    search = search_resp.json()
    assert search["safe"] is True
    assert search["proposal"]["candidates"]

    selection_resp = client.post(
        SELECTION_URL,
        json={
            "search_execution": search,
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": reason,
        },
        headers=_auth(token),
    )
    assert selection_resp.status_code == 200, selection_resp.text
    selection = selection_resp.json()
    assert selection["safe"] is True
    assert selection["create_proposal"]["safe"] is True
    return selection


def _confirm(client, token: str, selection: dict, confirmed=True):
    return client.post(
        CONFIRM_URL,
        json={
            "confirmed": confirmed,
            "selection_proposal": selection,
        },
        headers=_auth(token),
    )


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


def test_bernie_confirm_requires_auth(client, practitioner, patient, schedule):
    resp = client.post(CONFIRM_URL, json={
        "confirmed": False,
        "selection_proposal": {
            "intent": "select_slot_for_create_proposal",
            "safe": False,
            "requires_confirmation": True,
            "autonomy_tier": "blocked",
            "summary": "blocked",
            "blocks": [],
        },
    })

    assert resp.status_code == 401


def test_bernie_confirm_success_writes_exactly_one_appointment_and_bounded_audit(
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
    selection = _search_and_select(client, token, practitioner, patient)
    appointment_before, audit_before = _row_counts(db)

    resp = _confirm(client, token, selection, confirmed=True)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "confirm_create_appointment"
    assert data["safe"] is True
    assert data["requires_confirmation"] is False
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["blocks"] == []
    assert data["appointment"]["patient_id"] == str(patient.id)
    assert data["appointment"]["practitioner_id"] == str(practitioner.id)
    assert data["appointment"]["appointment_date"] == REFERENCE_DATE
    assert data["appointment"]["start_time_local"] == "09:00:00"
    assert "bernie_confirm_create_proposal" in data["audit_evidence"]
    assert "source_slot_selection_proposal" in data["audit_evidence"]
    assert "source_create_proposal" in data["audit_evidence"]
    assert "bernie_identity_confidence_medium" in data["audit_evidence"]
    assert db.query(Appointment).count() == appointment_before + 1
    assert db.query(AppointmentAuditLog).count() == audit_before + 1

    audit = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == data["appointment"]["id"]
    ).one()
    assert audit.action.value == "create"
    assert set(audit.confirmed_warnings) == set(data["audit_evidence"])


def test_bernie_confirm_false_writes_no_appointment_or_audit(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
):
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)
    expected_counts = _row_counts(db)

    resp = _confirm(client, token, selection, confirmed=False)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["appointment"] is None
    assert data["blocks"][0]["code"] == "explicit_confirmation_required"
    _assert_row_counts_unchanged(db, expected_counts)


def test_bernie_confirm_stale_conflict_writes_no_new_rows(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
    schedule,
):
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)
    _make_conflicting_appointment(db, practice, practitioner, patient)
    expected_counts = _row_counts(db)

    resp = _confirm(client, token, selection, confirmed=True)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["appointment"] is None
    assert data["blocks"][0]["code"] == "create_proposal_revalidation_blocked"
    assert data["blocks"][1]["code"] == "appointment_conflict"
    _assert_row_counts_unchanged(db, expected_counts)


def test_bernie_confirm_mismatched_selection_and_create_proposal_writes_no_rows(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
):
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)
    selection["create_proposal"]["command"]["start_time_local"] = "09:15:00"
    expected_counts = _row_counts(db)

    resp = _confirm(client, token, selection, confirmed=True)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["appointment"] is None
    assert data["blocks"][0]["code"] == "selection_create_proposal_mismatch"
    _assert_row_counts_unchanged(db, expected_counts)


def test_bernie_confirm_route_has_no_llm_or_autonomous_natural_language_execution():
    route_source = inspect.getsource(appointments_router.confirm_bernie_create_proposal)

    assert "generate_content" not in route_source
    assert "Gemini" not in route_source
    assert "AiService" not in route_source
    assert "normalize_slot_search_command" not in route_source
    assert "_build_create_appointment_proposal" in route_source
    assert "_create_appointment_from_body" in route_source
