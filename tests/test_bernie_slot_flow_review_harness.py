"""
Deterministic Bernie normalize -> search -> supervised selection review harness.

This intentionally exercises only backend proposal endpoints. It proves the
pre-booking Bernie chain can prepare review evidence without final booking
writes, appointment audit rows, or LLM/provider calls.
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
REFERENCE_DATE = "2026-06-22"


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _base_command(practitioner, patient=None) -> dict:
    payload = {
        "practitioner_id": str(practitioner.id),
        "date_from": "today",
        "duration_minutes": "15",
    }
    if patient is not None:
        payload["patient_id"] = str(patient.id)
    return payload


def _normalize(client, token: str, body: dict):
    return client.post(
        NORMALIZE_URL,
        params={"reference_date": REFERENCE_DATE},
        json=body,
        headers=_auth(token),
    )


def _normalized_search(client, token: str, body: dict):
    return client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": REFERENCE_DATE},
        json=body,
        headers=_auth(token),
    )


def _select_slot(client, token: str, body: dict):
    return client.post(SELECTION_URL, json=body, headers=_auth(token))


def _row_counts(db) -> tuple[int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    )


def _assert_row_counts_unchanged(db, expected: tuple[int, int]) -> None:
    assert _row_counts(db) == expected


def _install_forbidden_ai_provider_guard(monkeypatch) -> None:
    def forbidden_provider(*args, **kwargs):
        raise AssertionError("Bernie slot flow must not instantiate or call AI providers")

    monkeypatch.setattr(ai_service, "_get_default_provider", forbidden_provider)


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


def test_bernie_normalize_search_select_chain_prepares_create_proposal_without_writes(
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
    command = _base_command(practitioner, patient)
    expected_counts = _row_counts(db)

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

    selection_resp = _select_slot(client, token, {
        "search_execution": search,
        "selected_candidate_index": 0,
        "patient_id": str(patient.id),
        "reason": "Bernie review harness follow-up",
    })
    assert selection_resp.status_code == 200, selection_resp.text
    selection = selection_resp.json()
    assert selection["intent"] == "select_slot_for_create_proposal"
    assert selection["safe"] is True
    assert selection["requires_confirmation"] is True
    assert selection["autonomy_tier"] == "proposal"
    assert selection["create_proposal"]["intent"] == "create_appointment"
    assert selection["create_proposal"]["command"]["patient_id"] == str(patient.id)
    assert selection["create_proposal"]["command"]["practitioner_id"] == str(practitioner.id)
    assert selection["create_proposal"]["command"]["appointment_date"] == REFERENCE_DATE
    assert selection["create_proposal"]["command"]["start_time_local"] == "09:00:00"
    assert selection["create_proposal"]["command"]["reason"] == "Bernie review harness follow-up"
    _assert_row_counts_unchanged(db, expected_counts)


def test_bernie_no_match_search_blocks_selection_without_writes(
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
    command = {
        **_base_command(practitioner),
        "earliest_time": "08:00",
        "latest_time": "09:00",
    }
    expected_counts = _row_counts(db)

    search_resp = _normalized_search(client, token, command)
    assert search_resp.status_code == 200, search_resp.text
    search = search_resp.json()
    assert search["safe"] is True
    assert search["proposal"]["safe"] is True
    assert search["proposal"]["candidates"] == []
    assert "No free slots found" in search["proposal"]["summary"]
    _assert_row_counts_unchanged(db, expected_counts)

    selection_resp = _select_slot(client, token, {
        "search_execution": search,
        "selected_candidate_index": 0,
        "patient_id": str(patient.id),
    })
    assert selection_resp.status_code == 200, selection_resp.text
    selection = selection_resp.json()
    assert selection["safe"] is False
    assert selection["autonomy_tier"] == "blocked"
    assert selection["create_proposal"] is None
    assert selection["blocks"][0]["code"] == "no_slot_candidates"
    _assert_row_counts_unchanged(db, expected_counts)


def test_bernie_conflict_selection_is_blocked_without_new_writes(
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
    _make_conflicting_appointment(db, practice, practitioner, patient)
    token = make_token(gp_user)
    expected_counts = _row_counts(db)

    normalize_resp = _normalize(client, token, _base_command(practitioner, patient))
    assert normalize_resp.status_code == 200, normalize_resp.text
    assert normalize_resp.json()["safe"] is True
    _assert_row_counts_unchanged(db, expected_counts)

    selection_resp = _select_slot(client, token, {
        "selected_candidate": {
            "appointment_date": REFERENCE_DATE,
            "start_time": "2026-06-21T23:00:00+00:00",
            "end_time": "2026-06-21T23:15:00+00:00",
            "start_time_local": "09:00:00",
            "duration_minutes": 15,
            "warnings": [],
        },
        "practitioner_id": str(practitioner.id),
        "patient_id": str(patient.id),
    })
    assert selection_resp.status_code == 200, selection_resp.text
    selection = selection_resp.json()
    assert selection["safe"] is False
    assert selection["autonomy_tier"] == "blocked"
    assert selection["blocks"][0]["code"] == "appointment_conflict"
    assert selection["create_proposal"]["blocks"][0]["code"] == "appointment_conflict"
    _assert_row_counts_unchanged(db, expected_counts)


def test_bernie_slot_flow_routes_have_no_final_write_or_provider_calls():
    route_sources = "\n".join(
        inspect.getsource(route)
        for route in (
            appointments_router.normalize_slot_search_proposal_command,
            appointments_router.propose_normalized_slot_search,
            appointments_router.propose_slot_selection_for_create,
        )
    )

    assert "generate_content" not in route_sources
    assert "Gemini" not in route_sources
    assert "AiService" not in route_sources
    assert "db.add" not in route_sources
    assert "db.commit" not in route_sources
    assert "_write_audit" not in route_sources
