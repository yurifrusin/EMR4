from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = (
    ROOT / "orchestration" / "api_spine_appointment_idempotency_proposal_only_preflight.md"
)
POLICY_PACKET = ROOT / "orchestration" / "api_spine_appointment_idempotency_policy_packet.md"
INVENTORY = ROOT / "orchestration" / "api_spine_appointment_command_alignment_inventory.md"
ROUTER = ROOT / "app" / "routers" / "appointments.py"


PROPOSAL_ROUTES = {
    "create": {
        "route": "POST /api/v1/appointments/proposals/create",
        "handler": "propose_create_appointment",
        "operation": "proposeAppointmentCreate",
        "end": "def _build_create_appointment_proposal(",
    },
    "update": {
        "route": "POST /api/v1/appointments/proposals/update/{appointment_id}",
        "handler": "propose_update_appointment",
        "operation": "proposeAppointmentUpdate",
        "end": "def _block_bernie_update_confirmation(",
    },
    "status": {
        "route": "POST /api/v1/appointments/proposals/status/{appointment_id}",
        "handler": "propose_status_update",
        "operation": "proposeAppointmentStatus",
        "end": '@router.post("/proposals/waiting-area/{appointment_id}"',
    },
    "waiting_area": {
        "route": "POST /api/v1/appointments/proposals/waiting-area/{appointment_id}",
        "handler": "propose_waiting_area_update",
        "operation": "proposeAppointmentStatus",
        "end": "def _status_update_body_from_command(",
    },
    "delete": {
        "route": "POST /api/v1/appointments/proposals/delete/{appointment_id}",
        "handler": "propose_delete_appointment",
        "operation": "proposeAppointmentDelete",
        "end": '@router.get("/slots/{practitioner_id}"',
    },
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _route_body(router_text: str, handler: str, end_marker: str) -> str:
    start = router_text.index(f"def {handler}(")
    end = router_text.index(end_marker, start)
    return router_text[start:end]


def test_preflight_selects_proposal_only_before_raw_compatibility():
    text = _read(PREFLIGHT)
    compact = _compact(text)

    assert "| Sprint | 147 |" in text
    assert "No route behavior changed" in text
    assert "proposal-only appointment routes, not raw compatibility writes" in text
    assert "proposal routes are canonical OpenAPI command-plane routes" in compact
    assert "proposal routes are non-mutating" in compact
    assert "must not create write authority" in compact
    assert "raw compatibility writes still need a separate" in compact
    assert "Proposal-only idempotency must have a different contract" in text
    assert "must not take on confirmation-grade write replay authority" in compact


def test_preflight_lists_current_proposal_only_scope():
    text = _read(PREFLIGHT)

    for details in PROPOSAL_ROUTES.values():
        assert details["route"] in text
        assert details["handler"] in text
        assert details["operation"] in text
    assert "Slot-search" in text
    assert "remain out of scope" in text


def test_policy_packet_supports_proposal_only_as_client_discipline_not_write_authority():
    policy = _compact(_read(POLICY_PACKET))

    assert "Proposal routes in OpenAPI" in policy
    assert "Require syntactic `Idempotency-Key` after client readiness" in policy
    assert "do not treat proposals as write replay authority" in policy
    assert "proposal-only entries, if implemented, may use a shorter retention window" in policy
    assert "Raw compatibility writes | Explicit migration decision required" in policy


def test_inventory_classifies_proposal_routes_as_non_mutating_proposal_commands():
    inventory = _read(INVENTORY)

    for details in PROPOSAL_ROUTES.values():
        assert details["route"] in inventory
        assert details["handler"] in inventory
    for phrase in (
        "`proposal command`: prepares a backend proposal",
        "no appointment write",
        "The current FastAPI surface already has proposal-confirm families",
    ):
        assert phrase in inventory


def test_current_fastapi_proposal_routes_reflect_create_only_wiring():
    router_text = _read(ROUTER)

    create_route = _route_body(
        router_text,
        PROPOSAL_ROUTES["create"]["handler"],
        PROPOSAL_ROUTES["create"]["end"],
    )
    assert "Idempotency-Key" in create_route
    assert "claim_appointment_command(" not in create_route
    assert "complete_appointment_command(" not in create_route

    for name, details in PROPOSAL_ROUTES.items():
        if name == "create":
            continue
        route = _route_body(router_text, details["handler"], details["end"])
        assert "Idempotency-Key" not in route
        assert "claim_appointment_command(" not in route
        assert "complete_appointment_command(" not in route


def test_preflight_keeps_confirmation_routes_and_raw_routes_separate():
    text = _read(PREFLIGHT)
    compact = _compact(text)

    for phrase in (
        "no `Idempotency-Key` header binding on proposal-only routes",
        "no `claim_appointment_command()` or `complete_appointment_command()` calls",
        "no appointment/audit mutation behavior changes",
        "no raw compatibility route behavior changes",
        "raw compatibility `POST`, `PUT`, `PATCH`, or `DELETE` idempotency",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
    ):
        assert phrase in compact


def test_preflight_recommends_create_proposal_route_test_contract_next():
    text = _read(PREFLIGHT)
    compact = _compact(text)

    assert "Recommended Sprint 148" in text
    assert "guarded proposal-only route-test contract" in compact
    assert "POST /api/v1/appointments/proposals/create" in compact
    assert "Do not wire proposal-route enforcement in Sprint 148" in compact
    assert "proposal-specific replay/conflict/client-readiness semantics" in compact


def test_preflight_records_deepseek_design_questions_before_wiring():
    text = _read(PREFLIGHT)

    for phrase in (
        "Client readiness",
        "Replay response",
        "Same-key/different-body conflict",
        "Retention",
        "Operation identity",
        "Storage reuse",
        "Do not assume confirmation-style stored response replay",
        "short and bounded by proposal freshness/session expectations",
        "status/{appointment_id}` and `waiting-area/{appointment_id}` share",
    ):
        assert phrase in text
