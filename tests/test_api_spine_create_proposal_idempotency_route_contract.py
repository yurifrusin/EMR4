from pathlib import Path
from datetime import datetime, time, timezone

import pytest

import app.routers.appointments as appointments_router
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
    AppointmentStatus,
    BookingChannel,
)
from tests.conftest import make_token
from tests.test_appointment_proposals import THURSDAY, _base_body, _post_proposal


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT / "orchestration" / "api_spine_appointment_idempotency_create_proposal_route_tests.md"
)
PREFLIGHT_DOC = (
    ROOT / "orchestration" / "api_spine_appointment_idempotency_proposal_only_preflight.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
PROPOSAL_TESTS = ROOT / "tests" / "test_appointment_proposals.py"
ROUTE_CONTRACT_TESTS = ROOT / "tests" / "test_diary_action_route_contract.py"
ROUTE_CONTRACT = ROOT / "app" / "services" / "diary" / "action_route_contract.py"
PROPOSAL_URL = "/api/v1/appointments/proposals/create"
HANDLER = "propose_create_appointment"
HELPER = "_build_create_appointment_proposal"
OPERATION_ID = "proposeAppointmentCreate"

PASSING_CONTRACT_TESTS = {
    "test_create_proposal_route_test_contract_records_scope",
    "test_create_proposal_contract_records_proposal_specific_idempotency_boundary",
    "test_create_proposal_contract_lists_future_behavior_cases",
    "test_current_router_wires_create_proposal_syntactic_header_only",
    "test_current_router_preserves_create_proposal_confirmation_evidence_path",
    "test_existing_dynamic_create_proposal_test_guards_idempotency_ledger_side_effect",
    "test_diary_action_route_contract_remains_consistent_with_create_proposal_no_wiring",
    "test_contract_keeps_other_proposals_raw_and_runtime_gates_closed",
    "test_route_contract_test_inventory_matches_wired_surface",
    "test_missing_idempotency_key_blocks_before_create_proposal_evidence",
    "test_blank_idempotency_key_is_treated_as_missing_for_create_proposal",
    "test_keyed_create_proposal_has_no_appointment_audit_ledger_or_slot_reservation_side_effect",
    "test_short_nonblank_key_is_accepted_until_minlength_client_readiness_decision",
    "test_same_key_same_body_create_proposal_retry_does_not_gain_write_authority",
    "test_same_key_different_body_create_proposal_semantics_are_proposal_scoped",
    "test_create_proposal_idempotency_does_not_weaken_confirmation_evidence_or_freshness",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


@pytest.fixture(autouse=True)
def _freeze_create_proposal_contract_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


def _compact(text: str) -> str:
    return " ".join(text.split())


def _route_body(router_text: str, start_marker: str, end_marker: str) -> str:
    start = router_text.index(start_marker)
    end = router_text.index(end_marker, start)
    return router_text[start:end]


def _create_proposal_route(router_text: str) -> str:
    return _route_body(
        router_text,
        f"def {HANDLER}(",
        f"def {HELPER}(",
    )


def _create_proposal_helper(router_text: str) -> str:
    return _route_body(
        router_text,
        f"def {HELPER}(",
        "def _block_create_confirmation(",
    )


def test_create_proposal_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)
    preflight = _read(PREFLIGHT_DOC)

    assert "| Sprint | 148 |" in text
    assert "Guarded route-test contract only" in text
    assert PROPOSAL_URL in text
    assert HANDLER in text
    assert OPERATION_ID in text
    assert "proposal command" in text
    assert "Recommended Sprint 148" in preflight


def test_create_proposal_contract_records_proposal_specific_idempotency_boundary():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "future client-discipline behavior",
        "not confirmation-write replay authority",
        "authorize or imply appointment creation",
        "reserve diary slots",
        "skip staff confirmation",
        "replace signed confirmation evidence",
        "weaken `create_proposal_freshness_id`",
        "replay a confirmed appointment response",
    ):
        assert phrase in text


def test_create_proposal_contract_lists_future_behavior_cases():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "missing `Idempotency-Key` fails closed",
        "blank or whitespace-only `Idempotency-Key`",
        "valid keyed create-proposal request returns a proposal envelope",
        "no appointment, audit, confirmation-ledger, or slot-reservation side effect",
        "same-key/same-body retry does not create write authority",
        "same-key/different-body behavior is explicitly scoped",
        "confirmation payloads still require staff confirmation",
    ):
        assert phrase in text
    assert "DB-backed `POST /api/v1/appointments/proposals/create` integration tests" in text
    assert "Replay-Model Decision" in text
    assert "Deterministic re-evaluation" in text
    assert "Short-retention proposal marker" in text
    assert "Stored proposal-envelope replay" in text
    assert "Chosen" in text


def _make_conflicting_appt(db, practice, practitioner, patient):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        appointment_date=THURSDAY,
        start_time_local=time(9, 0),
        start_time=datetime.combine(
            THURSDAY,
            time(9, 0),
            tzinfo=timezone.utc,
        ),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def test_current_router_wires_create_proposal_syntactic_header_only():
    router_text = _read(ROUTER)
    route = _create_proposal_route(router_text)
    helper = _create_proposal_helper(router_text)
    combined = f"{route}\n{helper}"

    assert "Idempotency-Key" in route
    assert "Header(" in route
    assert "_normalize_create_proposal_idempotency_key(idempotency_key)" in route
    assert "claim_appointment_command(" not in combined
    assert "complete_appointment_command(" not in combined


def test_current_router_preserves_create_proposal_confirmation_evidence_path():
    helper = _create_proposal_helper(_read(ROUTER))

    for phrase in (
        "response.confirm_endpoint = _STAFF_CREATE_CONFIRM_ACTION.endpoint",
        "response.create_proposal_freshness_id = create_proposal_freshness_id",
        "response.signed_confirmation_evidence = signed_confirmation_evidence",
        "response.signed_confirmation_evidence_required = True",
        '"confirmed": False',
        '"create_proposal_freshness_id": create_proposal_freshness_id',
        '"signed_confirmation_evidence": signed_confirmation_evidence',
    ):
        assert phrase in helper


def test_existing_dynamic_create_proposal_test_guards_idempotency_ledger_side_effect():
    proposal_tests = _read(PROPOSAL_TESTS)

    assert "AppointmentCommandIdempotency" in proposal_tests
    assert "before_idempotency_rows = db.query(AppointmentCommandIdempotency).count()" in proposal_tests
    assert "db.query(AppointmentCommandIdempotency).count() == before_idempotency_rows" in proposal_tests


def test_diary_action_route_contract_remains_consistent_with_create_proposal_no_wiring():
    route_contract = _read(ROUTE_CONTRACT)
    route_tests = _read(ROUTE_CONTRACT_TESTS)

    assert 'proposal_routes=("/api/v1/appointments/proposals/create",)' in route_contract
    assert "RouteAuthority.signed_confirm" in route_contract
    assert "confirm_routes=(" in route_contract
    assert "test_signed_confirm_contracts_keep_proposal_and_confirm_paths_separate" in route_tests


def test_contract_keeps_other_proposals_raw_and_runtime_gates_closed():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "update/status/waiting-area/delete proposal idempotency enforcement",
        "raw compatibility `POST`, `PUT`, `PATCH`, or `DELETE` idempotency",
        "slot-search reservation or replay semantics",
        "Bernie interpreter/session command idempotency expansion",
        "provider calls",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
    ):
        assert phrase in text


def test_route_contract_test_inventory_matches_wired_surface():
    test_functions = {
        name
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    }
    assert test_functions == PASSING_CONTRACT_TESTS


def test_missing_idempotency_key_blocks_before_create_proposal_evidence(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    before = (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )

    resp = _post_proposal(client, token, _base_body(patient, practitioner), idempotency_key=None)

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    ) == before


def test_blank_idempotency_key_is_treated_as_missing_for_create_proposal(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)

    resp = _post_proposal(client, token, _base_body(patient, practitioner), idempotency_key="   ")

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_keyed_create_proposal_has_no_appointment_audit_ledger_or_slot_reservation_side_effect(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    before = (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )

    resp = _post_proposal(client, token, _base_body(patient, practitioner), idempotency_key="proposal-keyed")

    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is True, resp.json()
    assert (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    ) == before


def test_short_nonblank_key_is_accepted_until_minlength_client_readiness_decision(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)

    resp = _post_proposal(client, token, _base_body(patient, practitioner), idempotency_key="a")

    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is True, resp.json()
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_same_key_same_body_create_proposal_retry_does_not_gain_write_authority(
    client, db, gp_user, practice, patient, practitioner
):
    token = make_token(gp_user)
    body = _base_body(patient, practitioner)
    first = _post_proposal(client, token, body, idempotency_key="same-body-fresh")
    assert first.status_code == 200, first.text
    assert first.json()["safe"] is True, first.json()
    _make_conflicting_appt(db, practice, practitioner, patient)

    second = _post_proposal(client, token, body, idempotency_key="same-body-fresh")

    assert second.status_code == 200, second.text
    assert second.json()["safe"] is False
    assert second.json()["blocks"][0]["code"] == "appointment_conflict"
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_same_key_different_body_create_proposal_semantics_are_proposal_scoped(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    first = _post_proposal(client, token, _base_body(patient, practitioner), idempotency_key="different-body")
    assert first.status_code == 200, first.text
    changed = _base_body(patient, practitioner)
    changed["start_time_local"] = "09:30:00"

    second = _post_proposal(client, token, changed, idempotency_key="different-body")

    assert second.status_code == 200, second.text
    assert second.json()["command"]["start_time_local"] == "09:30:00"
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_create_proposal_idempotency_does_not_weaken_confirmation_evidence_or_freshness(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)

    resp = _post_proposal(client, token, _base_body(patient, practitioner), idempotency_key="evidence-key")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["confirm_payload"]["confirmed"] is False
    assert data["create_proposal_freshness_id"]
    assert data["signed_confirmation_evidence_required"] is True
    assert data["signed_confirmation_evidence"]["purpose"] == "staff_confirm_create_proposal"
    assert data["confirm_payload"]["signed_confirmation_evidence"] == data["signed_confirmation_evidence"]
