from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    ROOT / "orchestration" / "api_spine_appointment_idempotency_create_proposal_replay_model.md"
)
ROUTE_CONTRACT = (
    ROOT / "orchestration" / "api_spine_appointment_idempotency_create_proposal_route_tests.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
IDEMPOTENCY_HELPER = ROOT / "app" / "services" / "appointment_idempotency.py"
PROPOSAL_TESTS = ROOT / "tests" / "test_appointment_proposals.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _route_body(router_text: str, start_marker: str, end_marker: str) -> str:
    start = router_text.index(start_marker)
    end = router_text.index(end_marker, start)
    return router_text[start:end]


def test_decision_selects_deterministic_re_evaluation_without_proposal_ledger():
    text = _read(DECISION)
    compact = _compact(text)

    assert "| Sprint | 149 |" in text
    assert "Sprint 150 wires syntactic header enforcement only" in text
    assert "Deterministic re-evaluation with a required `Idempotency-Key`" in text
    assert "no proposal ledger" in compact
    assert "no stored proposal-envelope replay" in compact
    assert "mint fresh proposal evidence" in compact


def test_decision_defines_same_key_semantics_without_conflict_or_stored_replay():
    compact = _compact(_read(DECISION))

    for phrase in (
        "Same key + same body | Re-evaluate current state and return a fresh proposal envelope",
        "do not replay stale evidence",
        "Same key + different body | Re-evaluate current state for the new body",
        "do not return `409`",
        "Confirmation payload | Still requires staff confirmation",
    ):
        assert phrase in compact


def test_decision_rejects_marker_and_stored_envelope_for_first_create_proposal_pass():
    text = _read(DECISION)
    compact = _compact(text)

    assert "Short-Retention Proposal Marker" in text
    assert "Stored Proposal-Envelope Replay" in text
    assert "Rejected for the first create-proposal wiring pass" in compact
    assert "Rejected because proposal envelopes contain freshness and signed confirmation evidence" in compact


def test_decision_forbids_confirmation_ledger_helper_reuse_on_create_proposal():
    text = _read(DECISION)
    helper = _read(IDEMPOTENCY_HELPER)

    assert "avoid `claim_appointment_command()`" in text
    assert "avoid creating `AppointmentCommandIdempotency` rows" in text
    assert "confirmation route responsible for durable replay" in text
    assert "syntactic only" in text
    assert "not actor/operation scoped in storage" in text
    assert "proposeAppointmentCreate" in text
    assert "logging/review metadata only" in text
    assert 'Header(None, alias="Idempotency-Key")' in text
    assert "not inside" in text
    assert "_build_create_appointment_proposal" in text
    assert "response_body_json" in helper
    assert "target_appointment_id" in helper


def test_current_create_proposal_route_wires_syntactic_header_without_ledger_after_decision():
    router_text = _read(ROUTER)
    route = _route_body(
        router_text,
        "def propose_create_appointment(",
        "def _build_create_appointment_proposal(",
    )
    helper = _route_body(
        router_text,
        "def _build_create_appointment_proposal(",
        "def _block_create_confirmation(",
    )

    assert "Idempotency-Key" in route
    assert "Header(" in route
    assert "_normalize_create_proposal_idempotency_key(idempotency_key)" in route
    assert "claim_appointment_command(" not in f"{route}\n{helper}"
    assert "complete_appointment_command(" not in f"{route}\n{helper}"


def test_dynamic_proposal_tests_guard_no_idempotency_ledger_side_effect():
    proposal_tests = _read(PROPOSAL_TESTS)

    assert "AppointmentCommandIdempotency" in proposal_tests
    assert "before_idempotency_rows = db.query(AppointmentCommandIdempotency).count()" in proposal_tests
    assert "db.query(AppointmentCommandIdempotency).count() == before_idempotency_rows" in proposal_tests


def test_sprint148_contract_points_to_sprint149_decision_and_sprint150_wiring():
    decision = _read(DECISION)
    contract = _read(ROUTE_CONTRACT)

    assert "Replay-Model Decision" in contract
    assert "do not create a proposal ledger" in contract
    assert "Recommended Sprint 150" in decision
    assert "deterministic re-evaluation semantics only" in decision


def test_decision_keeps_blocked_gates_closed():
    compact = _compact(_read(DECISION))

    for phrase in (
        "create-proposal route enforcement wiring",
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
        assert phrase in compact


def test_decision_records_client_readiness_additive_migration_and_bernie_consistency():
    text = _read(DECISION)
    compact = _compact(text)

    assert "define client readiness as" in text
    assert "fresh proposal evaluations, not conflicts or cached envelopes" in compact
    assert "leaves no stored proposal data to migrate" in compact
    assert "must be additive and must go through a new explicit review" in compact
    assert "Bernie create-proposal surfaces" in text
    assert "no separate Bernie proposal idempotency path" in compact
