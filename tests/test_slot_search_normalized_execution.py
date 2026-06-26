"""
POST /api/v1/appointments/proposals/slot-search/normalized.

Proves the Bernie command execution contract stays deterministic and
non-mutating: normalize SlotSearchCommandIn with an explicit reference_date,
short-circuit unsafe commands before slot search, and reuse the existing
non-mutating slot-search proposal path for safe commands.
"""

from datetime import date
import inspect

from app.models.appointments import Appointment, AppointmentAuditLog
from app.schemas.appointments import SlotSearchProposalOut
import app.routers.appointments as appointments_router
from tests.conftest import make_token

NORMALIZED_SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
REFERENCE_DATE = "2026-06-22"


def _normalized_search(
    client,
    token,
    body: dict,
    reference_date: str = REFERENCE_DATE,
):
    return client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": reference_date},
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def _base_body(practitioner) -> dict:
    return {
        "practitioner_id": str(practitioner.id),
        "date_from": "today",
        "duration_minutes": "15",
    }


def test_normalized_slot_search_requires_auth(client, practitioner):
    resp = client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": REFERENCE_DATE},
        json=_base_body(practitioner),
    )

    assert resp.status_code == 401


def test_normalized_slot_search_requires_explicit_reference_date(
    client,
    gp_user,
    practitioner,
):
    resp = client.post(
        NORMALIZED_SEARCH_URL,
        json=_base_body(practitioner),
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )

    assert resp.status_code == 422


def test_safe_command_returns_normalization_context_and_candidate_slots(
    client,
    gp_user,
    practitioner,
    schedule,
):
    token = make_token(gp_user)
    resp = _normalized_search(client, token, _base_body(practitioner))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "search_slots_from_command"
    assert data["safe"] is True
    assert data["blocks"] == []
    assert data["normalization"]["safe"] is True
    assert data["normalization"]["constraint"]["date_from"] == REFERENCE_DATE
    assert data["normalization"]["constraint"]["date_to"] == REFERENCE_DATE

    proposal = data["proposal"]
    assert proposal["intent"] == "search_slots"
    assert proposal["safe"] is True
    assert proposal["autonomy_tier"] == "execute_with_report"
    assert proposal["resolved_duration_minutes"] == 15
    assert proposal["candidates"], "safe normalized search should return candidates"
    assert proposal["candidates"][0]["appointment_date"] == REFERENCE_DATE
    assert proposal["candidates"][0]["start_time_local"] == "09:00:00"


def test_safe_command_reuses_existing_slot_search_helper(
    client,
    gp_user,
    practitioner,
    monkeypatch,
):
    token = make_token(gp_user)
    captured = {}

    def fake_proposal(body, db, practice_id):
        captured["body"] = body
        captured["practice_id"] = practice_id
        return SlotSearchProposalOut(
            safe=True,
            autonomy_tier="execute_with_report",
            summary="stubbed proposal",
            resolved_duration_minutes=body.duration_minutes,
            candidates=[],
        )

    monkeypatch.setattr(appointments_router, "_build_slot_search_proposal", fake_proposal)

    resp = _normalized_search(client, token, _base_body(practitioner))

    assert resp.status_code == 200, resp.text
    assert captured["body"].practitioner_id == practitioner.id
    assert captured["body"].date_from == date(2026, 6, 22)
    assert captured["body"].duration_minutes == 15
    assert captured["practice_id"] == gp_user.practice_id
    assert resp.json()["proposal"]["summary"] == "stubbed proposal"


def test_unsafe_command_returns_blocks_without_executing_slot_search(
    client,
    gp_user,
    monkeypatch,
):
    token = make_token(gp_user)

    def forbidden(*args, **kwargs):
        raise AssertionError("unsafe normalization must not execute slot search")

    monkeypatch.setattr(appointments_router, "_build_slot_search_proposal", forbidden)
    resp = _normalized_search(client, token, {
        "practitioner_id": "not-a-uuid",
        "date_from": "not-a-date",
        "duration_minutes": "15",
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["proposal"] is None
    assert data["normalization"]["safe"] is False
    codes = {block["code"] for block in data["blocks"]}
    assert "invalid_practitioner_id" in codes
    assert "invalid_date_from" in codes


def test_normalized_slot_search_writes_no_appointments_or_audit_rows(
    client,
    db,
    gp_user,
    practitioner,
    schedule,
):
    token = make_token(gp_user)
    appt_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _normalized_search(client, token, _base_body(practitioner))

    assert resp.status_code == 200, resp.text
    assert db.query(Appointment).count() == appt_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_normalized_slot_search_has_no_llm_or_mutation_calls():
    source = inspect.getsource(appointments_router.propose_normalized_slot_search)

    assert "normalize_slot_search_command" in source
    assert "_build_slot_search_proposal" in source
    assert "generate_content" not in source
    assert "Gemini" not in source
    assert "db.add" not in source
    assert "db.commit" not in source
    assert "_write_audit" not in source
