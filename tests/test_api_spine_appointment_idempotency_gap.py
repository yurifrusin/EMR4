from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
GAP_DOC = ROOT / "orchestration" / "api_spine_appointment_idempotency_gap.md"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"

OPENAPI_IDEMPOTENCY_PATHS = {
    "/appointments/proposals/create",
    "/appointments/proposals/create/confirm",
    "/appointments/proposals/update",
    "/appointments/proposals/update/confirm",
    "/appointments/proposals/status",
    "/appointments/proposals/status/confirm",
    "/appointments/proposals/delete",
    "/appointments/proposals/delete/confirm",
}


def test_gap_doc_records_sprint_and_source_pass():
    text = GAP_DOC.read_text(encoding="utf-8")

    assert "# API Spine Appointment Idempotency-Key Gap Inspection" in text
    assert "| Sprint | 124 |" in text
    for source in (
        "docs/api-spine/openapi/appointment-commands.yaml",
        "orchestration/api_spine_appointment_command_alignment_inventory.md",
        "tests/test_api_spine_appointment_openapi_drift_guard.py",
        "app/routers/appointments.py",
        "app/schemas/appointments.py",
        "app/services/bernie/session_store.py",
        "tests/test_bernie_session_store.py",
        "tests/test_bernie_session_routes.py",
    ):
        assert f"`{source}`" in text


def test_openapi_idempotency_paths_are_documented_as_missing_enforcement():
    doc_text = GAP_DOC.read_text(encoding="utf-8")
    openapi_text = OPENAPI.read_text(encoding="utf-8")

    for path in OPENAPI_IDEMPOTENCY_PATHS:
        assert path in openapi_text
        assert path in doc_text
    assert doc_text.count("missing_http_header_enforcement") == len(
        OPENAPI_IDEMPOTENCY_PATHS
    )


def test_current_appointments_router_has_bounded_staff_create_confirm_binding():
    router_text = APPOINTMENTS_ROUTER.read_text(encoding="utf-8")
    route_start = router_text.index("def _idempotency_key_required_error(")
    route_end = router_text.index("def confirm_update_proposal_route(")
    update_start = route_end
    update_end = router_text.index("def propose_update_appointment(")
    bernie_start = router_text.index("def confirm_bernie_create_proposal(")
    bernie_end = router_text.index("def select_no_slot_suggestion(")
    status_start = router_text.index("def confirm_status_proposal_route(")
    status_end = router_text.index("def _a5_check_in_gate_open(")
    status_scope_end = router_text.index("def get_waiting_room(")
    delete_start = router_text.index("def confirm_delete_proposal_route(")
    delete_end = router_text.index("def propose_delete_appointment(")
    create_confirm_route = router_text[route_start:route_end]
    update_route = router_text[update_start:update_end]
    bernie_route = router_text[bernie_start:bernie_end]
    status_route = router_text[status_start:status_end]
    delete_route = router_text[delete_start:delete_end]
    non_create_confirm_later_routes = (
        router_text[update_end:status_start]
        + router_text[status_scope_end:delete_start]
        + router_text[delete_end:bernie_start]
        + router_text[bernie_end:]
    )

    assert "Idempotency-Key" in create_confirm_route
    assert re.search(
        r"idempotency[_-]?key[^\n]{0,120}Header\(",
        create_confirm_route,
        re.IGNORECASE,
    ) or re.search(
        r"Header\([^\n]{0,120}idempotency[_-]?key",
        create_confirm_route,
        re.IGNORECASE,
    )
    assert "Idempotency-Key" in bernie_route
    assert "_BERNIE_CREATE_CONFIRM_ROUTE_FAMILY" in bernie_route
    assert "Idempotency-Key" in status_route
    assert "compose_product_status_confirm(" in status_route
    assert "claim_appointment_command(" not in status_route
    assert "complete_appointment_command(" not in status_route
    assert "Idempotency-Key" in update_route
    assert "_UPDATE_CONFIRM_ROUTE_FAMILY" in update_route
    assert "Idempotency-Key" in delete_route
    assert "compose_product_delete_confirm(" in delete_route
    assert "_DELETE_CONFIRM_ROUTE_FAMILY" in router_text
    # Proposal handlers now have Idempotency-Key syntactic validation but
    # must not contain claim/complete ledger calls
    assert "claim_appointment_command(" not in non_create_confirm_later_routes
    assert "complete_appointment_command(" not in non_create_confirm_later_routes
    assert "_normalize_proposal_idempotency_key(" in non_create_confirm_later_routes


def test_gap_doc_distinguishes_existing_safety_controls_from_idempotency():
    text = GAP_DOC.read_text(encoding="utf-8")

    for existing_control in (
        "proposal freshness ids",
        "signed confirmation evidence",
        "explicit `confirmed=true`",
        "raw compatibility routes",
        "Bernie session event routes",
    ):
        assert existing_control in text
    assert "not equivalent to HTTP idempotency" in text
    assert "does not satisfy appointment command-plane `Idempotency-Key`" in text


def test_gap_doc_preserves_closed_gate_posture_and_next_slice():
    text = GAP_DOC.read_text(encoding="utf-8")

    assert "Recommended Sprint 125" in text
    assert "Appointment command idempotency policy packet" in text
    for closed_gate in (
        "live providers",
        "runtime FGA clients",
        "external patient clients",
        "GraphQL mutations",
        "broad historical diary trove mining",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "model-to-database writes",
    ):
        assert closed_gate in text
