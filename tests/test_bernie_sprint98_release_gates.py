"""Sprint 98 Bernie release gates for screenshot regressions.

These tests intentionally exercise public API routes and the non-mutating
interpreter path. They should block regressions where a resolved practitioner
still leaks ``missing_practitioner_id`` to staff, or where confirm failures
fall through to a generic ``Not Found`` response instead of the typed Bernie
confirmation contract.
"""

from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
WRAPPER_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
NORMALIZED_SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
SELECTION_URL = "/api/v1/appointments/proposals/slot-search/selection"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
REFERENCE_DATE = "2026-07-01"


ORDINARY_PROMPT = (
    "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm "
    "but before 3:45"
)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _row_counts(db) -> tuple[int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
    )


def _search_and_select(client, token: str, practitioner, patient):
    search_resp = client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": REFERENCE_DATE},
        json={
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
            "patient_id": str(patient.id),
            "earliest_time": "14:00",
            "latest_time": "15:45",
        },
        headers=_auth(token),
    )
    assert search_resp.status_code == 200, search_resp.text
    search = search_resp.json()
    assert search["safe"] is True
    assert search["proposal"]["candidates"], "release gate needs at least one candidate"

    selection_resp = client.post(
        SELECTION_URL,
        json={
            "search_execution": search,
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": "Sprint 98 release gate",
        },
        headers=_auth(token),
    )
    assert selection_resp.status_code == 200, selection_resp.text
    selection = selection_resp.json()
    assert selection["safe"] is True
    assert selection["create_proposal"]["safe"] is True
    return selection


def test_ordinary_prompt_resolves_practitioner_before_supervised_booking_gate(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
    monkeypatch,
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    before = _row_counts(db)

    interpret_resp = client.post(
        INTERPRET_URL,
        json={"instruction": ORDINARY_PROMPT, "reference_date": REFERENCE_DATE},
        headers=_auth(token),
    )

    assert interpret_resp.status_code == 200, interpret_resp.text
    interpreted = interpret_resp.json()
    assert interpreted["safe"] is True
    assert interpreted["result"] == "interpreted"
    assert interpreted["command_candidate"]["practitioner_id"] == str(practitioner.id)
    assert interpreted["command_candidate"]["patient_id"] == str(patient.id)
    assert interpreted["normalization"]["constraint"]["earliest_time"] == "14:00:00"
    assert interpreted["normalization"]["constraint"]["latest_time"] == "15:45:00"

    wrapper_resp = client.post(
        WRAPPER_URL,
        json={
            "reference_date": REFERENCE_DATE,
            "command": interpreted["command_candidate"],
        },
        headers=_auth(token),
    )

    assert wrapper_resp.status_code == 200, wrapper_resp.text
    wrapper = wrapper_resp.json()
    assert wrapper["result"] == "candidate_selection_required"
    assert wrapper["safe"] is True
    assert wrapper["staff_review"]["status"] == "candidate_selection_required"
    assert wrapper["staff_review"]["candidate_slots"], "resolved Dr Shera should search slots"

    rendered_payload = str(wrapper["staff_review"])
    assert "missing_practitioner_id" not in rendered_payload
    assert "Practitioner ID is required" not in rendered_payload
    assert _row_counts(db) == before


def test_confirmation_ready_uses_practitioner_evidence_not_raw_missing_id(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
):
    token = make_token(gp_user)
    before = _row_counts(db)

    resp = client.post(
        WRAPPER_URL,
        json={
            "reference_date": REFERENCE_DATE,
            "command": {
                "practitioner_id": str(practitioner.id),
                "patient_id": str(patient.id),
                "date_from": "today",
                "duration_minutes": "15",
                "earliest_time": "14:00",
                "latest_time": "15:45",
            },
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": "Sprint 98 release gate",
        },
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "confirmation_ready"
    review = data["staff_review"]
    assert review["confirmation_ready"] is True
    assert review["practitioner_evidence"]["practitioner_id"] == str(practitioner.id)
    assert review["practitioner_evidence"]["display_name"] == "Alex Shera"
    assert review["confirm_endpoint"] == CONFIRM_URL
    assert review["confirm_payload"]["selection_proposal"] == data["selection_proposal"]

    rendered_payload = str(review)
    assert "missing_practitioner_id" not in rendered_payload
    assert "Practitioner ID is required" not in rendered_payload
    assert _row_counts(db) == before


def test_confirm_bernie_invalid_practitioner_returns_typed_failure_not_not_found(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
):
    token = make_token(gp_user)
    selection = _search_and_select(client, token, practitioner, patient)
    selection["create_proposal"]["command"]["practitioner_id"] = (
        "00000000-0000-0000-0000-000000000001"
    )
    before = _row_counts(db)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "selection_proposal": selection},
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["appointment"] is None
    assert data["autonomy_tier"] == "blocked"
    assert "Not Found" not in resp.text
    assert "not found" in resp.text.lower()
    block_codes = {block["code"] for block in data["blocks"]}
    assert "practitioner_not_found" in block_codes
    assert "create_proposal_revalidation_blocked" not in block_codes
    assert _row_counts(db) == before
