from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_bernie_create_confirm_preflight.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_bernie_create_confirm_preflight_names_next_confirmation_family():
    text = _read(PREFLIGHT)

    assert "| Sprint | 133 |" in text
    assert "POST /api/v1/appointments/proposals/create/confirm-bernie" in text
    assert "confirm_bernie_create_proposal" in text
    assert "BernieCreateProposalConfirmationIn" in text
    assert "confirmAppointmentCreateProposal" in text
    assert "create-confirm-bernie" in text
    assert "Preflight/review only; no route behavior changed" in text


def test_bernie_create_confirm_preflight_records_session_event_boundary():
    text = _read(PREFLIGHT)

    for phrase in (
        "Bernie `confirm_submitted` and `confirmation_outcome` session events",
        "appointment ledger and Bernie session store are not one obvious",
        "without re-appending Bernie session events",
        "no-double-session-event replay cases",
        "stale or mismatched `session_binding` remains fail-closed",
    ):
        assert phrase in text


def test_bernie_create_confirm_preflight_keeps_closed_gates_and_scope_limits():
    text = _read(PREFLIGHT)

    for phrase in (
        "Do not enforce HTTP `Idempotency-Key` on `confirm-bernie`",
        "Do not wire update, status,",
        "proposal-only routes",
        "slot-search routes",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "model-to-database writes",
    ):
        assert phrase in text


def test_router_consumed_bernie_create_confirm_preflight_in_sprint_135():
    router_text = _read(ROUTER)
    route_start = router_text.index("def confirm_bernie_create_proposal(")
    route_end = router_text.index("def select_no_slot_suggestion(")
    route_body = router_text[route_start:route_end]

    assert "Header(" in route_body
    assert "Idempotency-Key" in route_body
    assert "claim_appointment_command(" in route_body
    assert "complete_appointment_command(" in route_body
    assert "_BERNIE_CREATE_CONFIRM_ROUTE_FAMILY" in route_body
    assert "_STAFF_CREATE_CONFIRM_ROUTE_FAMILY" not in route_body
    assert "confirm_submitted" in route_body
    assert "confirmation_outcome" in route_body
