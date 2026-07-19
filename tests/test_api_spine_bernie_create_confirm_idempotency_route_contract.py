from pathlib import Path
from datetime import datetime, timedelta, timezone
from copy import deepcopy
from uuid import UUID

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.schemas.appointments import BernieCreateProposalConfirmationIn
from app.services.appointment_idempotency import claim_appointment_command
from app.services.bernie import (
    BernieSessionEventType,
    BernieSessionState,
    DatabaseBernieSessionStore,
)
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_bernie_create_confirm_route_tests.md"
)
PREFLIGHT_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_bernie_create_confirm_preflight.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
BERNIE_CONFIRM_TESTS = ROOT / "tests" / "test_bernie_confirm_create_proposal.py"
BERNIE_ROUTE_OUTCOME_TESTS = ROOT / "tests" / "test_bernie_route_outcome_events.py"
CONTRACT_TEST = Path(__file__).name

OPERATION_ID = "confirmAppointmentCreateProposal"
ROUTE_FAMILY = "create-confirm-bernie"
PASSING_CONTRACT_TESTS = {
    "test_bernie_create_confirm_route_test_contract_records_scope",
    "test_bernie_create_confirm_contract_lists_future_behavior_cases",
    "test_bernie_create_confirm_contract_records_deepseek_session_event_review",
    "test_current_router_wires_confirm_bernie_idempotency_surface",
    "test_existing_bernie_confirm_tests_send_idempotency_keys",
    "test_route_contract_test_inventory_matches_wired_surface",
    "test_missing_idempotency_key_blocks_before_writes_or_session_events",
    "test_invalid_payload_does_not_create_ledger_by_default",
    "test_first_bound_confirmed_bernie_create_writes_appointment_audit_ledger_and_session_events",
    "test_same_key_same_body_replays_without_second_write_or_session_event",
    "test_same_key_same_body_replays_non_session_bound_without_second_write",
    "test_same_key_different_body_conflicts_without_second_write_or_session_event",
    "test_active_in_progress_key_fails_closed_without_write_or_session_event",
    "test_stale_in_progress_key_fails_closed_without_write_or_session_event",
    "test_failed_transient_key_fails_closed_without_write_or_session_event",
    "test_stale_session_binding_not_bypassed_by_idempotency",
    "test_business_rule_failure_after_claim_removes_or_rolls_back_claim",
    "test_replay_telemetry_distinct_from_new_confirm_mutation",
}
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
WRAPPER_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
REFERENCE_DATE = "2026-06-22"


@pytest.fixture(autouse=True)
def _freeze_bernie_contract_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _auth(token: str, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _row_counts(db) -> tuple[int, int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )


def _canonical_request_body(payload: dict) -> dict:
    return BernieCreateProposalConfirmationIn(**payload).model_dump(mode="json")


def _preclaim(db, user, payload: dict, *, key: str):
    return claim_appointment_command(
        db,
        practice_id=user.practice_id,
        actor_user_id=str(user.id),
        actor_role=user.role.value,
        operation_id=OPERATION_ID,
        route_family=ROUTE_FAMILY,
        raw_idempotency_key=key,
        request_body=_canonical_request_body(payload),
        secret=settings.secret_key.encode("utf-8"),
        stale_after=timedelta(minutes=10),
    )


def _create_recognition_session(client, token: str, surface_id: str) -> dict:
    active = client.get(
        "/api/v1/appointments/bernie/sessions/active",
        params={"surface_id": surface_id, "reference_date": REFERENCE_DATE},
        headers=_auth(token),
    )
    assert active.status_code == 200, active.text
    session = active.json()["session"]
    event = client.post(
        f"/api/v1/appointments/bernie/sessions/{session['session_id']}/events",
        json={
            "surface_id": surface_id,
            "event_type": "staff_instruction",
            "expected_revision": 0,
            "event_id": f"{surface_id}-staff",
            "payload": {"intent_ref": f"{surface_id}-intent"},
        },
        headers=_auth(token),
    )
    assert event.status_code == 200, event.text
    return event.json()["session"]


def _store(db, practice_id) -> DatabaseBernieSessionStore:
    return DatabaseBernieSessionStore(
        db,
        practice_id=practice_id,
        secret=settings.secret_key.encode("utf-8"),
    )


def _bound_confirm_payload(client, db, token: str, practitioner, patient, *, surface_id: str) -> dict:
    session = _create_recognition_session(client, token, surface_id)
    interpreted = _store(db, practitioner.practice_id).append_server_outcome_event(
        session_id=session["session_id"],
        event_type=BernieSessionEventType.interpretation_outcome,
        target_state=BernieSessionState.context_enrichment,
        expected_revision=session["revision"],
        payload={"result": "interpreted", "safe": True},
    )
    assert interpreted.accepted is True
    db.commit()
    proposal = client.post(
        WRAPPER_URL,
        json={
            "reference_date": REFERENCE_DATE,
            "command": {
                "practitioner_id": str(practitioner.id),
                "patient_id": str(patient.id),
                "date_from": "today",
                "duration_minutes": "15",
            },
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": f"Sprint 135 {surface_id}",
            "server_session_id": session["session_id"],
            "server_session_surface_id": surface_id,
            "server_session_expected_revision": interpreted.session.revision,
        },
        headers=_auth(token),
    )
    assert proposal.status_code == 200, proposal.text
    payload = proposal.json()["staff_review"]["confirm_payload"]
    assert payload["session_binding"] is not None
    payload["confirmed"] = True
    return payload


def _non_session_confirm_payload(client, token: str, practitioner, patient) -> dict:
    from tests.test_bernie_confirm_create_proposal import _search_and_select

    selection = _search_and_select(client, token, practitioner, patient, reason="Sprint 135")
    return {"confirmed": True, "selection_proposal": selection}


def _session_event_count(db, payload: dict) -> int:
    binding = payload.get("session_binding") or payload["selection_proposal"].get("session_binding")
    if not binding:
        return 0
    session = _store(db, UUID(binding["practice_id"])).get_session(binding["session_id"])
    assert session is not None
    return len(session.events)


def test_bernie_create_confirm_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)
    preflight = _read(PREFLIGHT_DOC)

    assert "| Sprint | 134 |" in text
    assert "Guarded route-test contract only" in text
    assert "POST /api/v1/appointments/proposals/create/confirm-bernie" in text
    assert "confirm_bernie_create_proposal" in text
    assert "BernieCreateProposalConfirmationIn" in text
    assert OPERATION_ID in text
    assert ROUTE_FAMILY in text
    assert "Sprint 135" in text
    assert "Recommended Sprint 134" in preflight


def test_bernie_create_confirm_contract_lists_future_behavior_cases():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "missing `Idempotency-Key` returns a fail-closed error",
        "invalid manually validated payload preserves current structured blocked",
        "one completed ledger row, one",
        "same-key/same-body replay returns the stored response",
        "without a second appointment, audit row",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "`409 idempotency_key_in_progress`",
        "`409 idempotency_key_stale_in_progress`",
        "`503 idempotency_key_failed_transient`",
        "stale or mismatched `session_binding` remains fail-closed",
        "post-claim business-rule blocks roll back or remove the claim",
        "replay telemetry is distinguishable from a new confirmed mutation",
        "non-session-bound confirmation",
    ):
        assert phrase in text


def test_bernie_create_confirm_contract_records_deepseek_session_event_review():
    text = _compact(_read(ROUTE_TEST_DOC))

    assert "DeepSeek review for Sprint 134" in text
    assert "`confirmation_outcome`" in text
    assert "most concrete double-event risk" in text
    assert "must not rely on the session store to deduplicate replay" in text
    assert "before the `_append_confirmation_outcome` closure can run" in text


def test_current_router_wires_confirm_bernie_idempotency_surface():
    router_text = _read(ROUTER)
    route_start = router_text.index("def confirm_bernie_create_proposal(")
    route_end = router_text.index("def select_no_slot_suggestion(")
    route_body = router_text[route_start:route_end]

    assert "Header(" in route_body
    assert "Idempotency-Key" in route_body
    assert "claim_appointment_command(" in route_body
    assert "complete_appointment_command(" in route_body
    assert "_BERNIE_CREATE_CONFIRM_ROUTE_FAMILY" in route_body
    assert "confirm_submitted" in route_body
    assert "confirmation_outcome" in route_body


def test_existing_bernie_confirm_tests_send_idempotency_keys():
    confirm_tests = _read(BERNIE_CONFIRM_TESTS)
    outcome_tests = _read(BERNIE_ROUTE_OUTCOME_TESTS)

    assert "Idempotency-Key" in confirm_tests
    assert "Idempotency-Key" in outcome_tests
    assert "client.post(CONFIRM_URL" in confirm_tests
    assert "client.post(CONFIRM_URL" in outcome_tests


def test_route_contract_test_inventory_matches_wired_surface():
    test_functions = [
        (name, value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    ]

    assert {name for name, _ in test_functions} == PASSING_CONTRACT_TESTS


def test_missing_idempotency_key_blocks_before_writes_or_session_events(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-missing")
    before = _row_counts(db)
    before_events = _session_event_count(db, payload)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert _row_counts(db) == before
    assert _session_event_count(db, payload) == before_events


def test_invalid_payload_does_not_create_ledger_by_default(client, db, gp_user):
    token = make_token(gp_user)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "selection_proposal": {"not": "valid"}},
        headers=_auth(token, "invalid-payload-key"),
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_first_bound_confirmed_bernie_create_writes_appointment_audit_ledger_and_session_events(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-first")
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "bound-first-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert _row_counts(db) == (before[0] + 1, before[1] + 1, before[2] + 1)
    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.state == "completed"
    assert ledger.operation_id == OPERATION_ID
    assert ledger.route_family == ROUTE_FAMILY
    assert ledger.response_status_code == 200
    assert ledger.audit_log_id is not None
    assert ledger.bernie_session_id == payload["session_binding"]["session_id"]
    audit = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.id == ledger.audit_log_id,
    ).one()
    assert audit.command_id == ledger.id
    assert audit.appointment_id == ledger.target_appointment_id
    assert audit.bernie_session_id == ledger.bernie_session_id
    receipt = data["confirmation_receipt"]
    assert receipt["correlation_id"] == str(ledger.id)
    assert receipt["audit_event_id"] == str(audit.id)
    assert receipt["session_id"] == ledger.bernie_session_id
    session = _store(db, gp_user.practice_id).get_session(payload["session_binding"]["session_id"])
    assert session is not None
    assert [event.event_type.value for event in session.events[-2:]] == [
        "confirm_submitted",
        "confirmation_outcome",
    ]


def test_same_key_same_body_replays_without_second_write_or_session_event(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-replay")

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "bound-replay-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)
    after_first_events = _session_event_count(db, payload)

    second = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "bound-replay-key"))

    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    assert _row_counts(db) == after_first
    assert _session_event_count(db, payload) == after_first_events


def test_same_key_same_body_replays_non_session_bound_without_second_write(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _non_session_confirm_payload(client, token, practitioner, patient)

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "unbound-replay-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "unbound-replay-key"))

    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    assert _row_counts(db) == after_first


def test_same_key_different_body_conflicts_without_second_write_or_session_event(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-conflict")
    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "bound-conflict-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)
    after_first_events = _session_event_count(db, payload)

    changed = deepcopy(payload)
    changed["confirmed_warnings"] = ["changed-body"]
    second = client.post(CONFIRM_URL, json=changed, headers=_auth(token, "bound-conflict-key"))

    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"
    assert _row_counts(db) == after_first
    assert _session_event_count(db, payload) == after_first_events


def test_active_in_progress_key_fails_closed_without_write_or_session_event(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-progress")
    claim = _preclaim(db, gp_user, payload, key="bound-progress-key")
    assert claim.kind == "started"
    before = _row_counts(db)
    before_events = _session_event_count(db, payload)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "bound-progress-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_in_progress"
    assert _row_counts(db) == before
    assert _session_event_count(db, payload) == before_events


def test_stale_in_progress_key_fails_closed_without_write_or_session_event(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-stale")
    claim = _preclaim(db, gp_user, payload, key="bound-stale-key")
    claim.record.updated_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    db.flush()
    before = _row_counts(db)
    before_events = _session_event_count(db, payload)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "bound-stale-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_stale_in_progress"
    assert _row_counts(db) == before
    assert _session_event_count(db, payload) == before_events


def test_failed_transient_key_fails_closed_without_write_or_session_event(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-failed")
    claim = _preclaim(db, gp_user, payload, key="bound-failed-key")
    claim.record.state = "failed_transient"
    db.flush()
    before = _row_counts(db)
    before_events = _session_event_count(db, payload)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "bound-failed-key"))

    assert resp.status_code == 503, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_failed_transient"
    assert _row_counts(db) == before
    assert _session_event_count(db, payload) == before_events


def test_stale_session_binding_not_bypassed_by_idempotency(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-binding")
    payload["session_binding"]["session_revision"] = 0
    before = _row_counts(db)
    before_events = _session_event_count(db, payload)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "bound-binding-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    block_codes = {block["code"] for block in data["blocks"]}
    assert block_codes & {
        "session_binding_revision_mismatch",
        "session_binding_session_revision_mismatch",
        "session_confirm_transition_failed",
        "stale_session_revision",
    }
    assert _row_counts(db) == before
    assert _session_event_count(db, payload) == before_events


def test_business_rule_failure_after_claim_removes_or_rolls_back_claim(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _non_session_confirm_payload(client, token, practitioner, patient)
    payload["selection_proposal"]["create_proposal"]["command"]["duration_minutes"] = 30
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "business-block-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["appointment"] is None
    assert _row_counts(db) == before


def test_replay_telemetry_distinct_from_new_confirm_mutation(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    payload = _bound_confirm_payload(client, db, token, practitioner, patient, surface_id="s135-telemetry")

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "telemetry-key"))
    assert first.status_code == 200, first.text
    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.audit_log_id is not None
    audit = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.id == ledger.audit_log_id,
    ).one()
    assert audit.command_id == ledger.id
    assert audit.appointment_id == ledger.target_appointment_id
    assert audit.bernie_session_id == ledger.bernie_session_id
    assert ledger.response_body_json == first.json()
    assert ledger.result_kind == "confirmed_write"
    event_count = _session_event_count(db, payload)

    replay = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "telemetry-key"))

    assert replay.status_code == 200, replay.text
    assert replay.json() == ledger.response_body_json
    assert _session_event_count(db, payload) == event_count
