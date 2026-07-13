from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_confirmation_family_checkpoint.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"

CONFIRMATION_FAMILIES = {
    "staff_create": {
        "route": "POST /api/v1/appointments/proposals/create/confirm",
        "handler": "confirm_create_proposal_route",
        "operation": "_STAFF_CREATE_CONFIRM_OPERATION_ID",
        "operation_value": "confirmAppointmentCreateProposal",
        "family": "_STAFF_CREATE_CONFIRM_ROUTE_FAMILY",
        "family_value": "create-confirm",
        "end": "def confirm_update_proposal_route(",
    },
    "update": {
        "route": "POST /api/v1/appointments/proposals/update/confirm",
        "handler": "confirm_update_proposal_route",
        "operation": "_UPDATE_CONFIRM_OPERATION_ID",
        "operation_value": "confirmAppointmentUpdateProposal",
        "family": "_UPDATE_CONFIRM_ROUTE_FAMILY",
        "family_value": "update-confirm",
        "end": "def propose_update_appointment(",
    },
    "status": {
        "route": "POST /api/v1/appointments/proposals/status-confirm",
        "handler": "confirm_status_proposal_route",
        "operation": "_STATUS_CONFIRM_OPERATION_ID",
        "operation_value": "confirmAppointmentStatusProposal",
        "family": "_STATUS_CONFIRM_ROUTE_FAMILY",
        "family_value": "status-confirm",
        "end": "def get_waiting_room(",
    },
    "delete": {
        "route": "POST /api/v1/appointments/proposals/delete-confirm",
        "handler": "confirm_delete_proposal_route",
        "operation": "_DELETE_CONFIRM_OPERATION_ID",
        "operation_value": "confirmAppointmentDeleteProposal",
        "family": "_DELETE_CONFIRM_ROUTE_FAMILY",
        "family_value": "delete-confirm",
        "end": "def propose_delete_appointment(",
    },
    "bernie_create": {
        "route": "POST /api/v1/appointments/proposals/create/confirm-bernie",
        "handler": "confirm_bernie_create_proposal",
        "operation": "_STAFF_CREATE_CONFIRM_OPERATION_ID",
        "operation_value": "confirmAppointmentCreateProposal",
        "family": "_BERNIE_CREATE_CONFIRM_ROUTE_FAMILY",
        "family_value": "create-confirm-bernie",
        "end": "def select_no_slot_suggestion(",
    },
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _route_body(router_text: str, handler: str, end: str) -> str:
    start = router_text.index(f"def {handler}(")
    finish = router_text.index(end, start)
    return router_text[start:finish]


def _compact(text: str) -> str:
    return " ".join(text.split())


def test_checkpoint_lists_all_wired_confirmation_families():
    text = _read(CHECKPOINT)

    assert "| Sprint | 145 |" in text
    assert "Checkpoint/audit only; no route behavior changed" in text
    for details in CONFIRMATION_FAMILIES.values():
        assert details["route"] in text
        assert details["handler"] in text
        assert details["operation_value"] in text
        assert details["family_value"] in text


def test_router_wires_each_confirmation_family_to_idempotency_ledger():
    router_text = _read(ROUTER)

    for details in CONFIRMATION_FAMILIES.values():
        route = _route_body(router_text, details["handler"], details["end"])
        assert "Header(" in route
        assert "Idempotency-Key" in route
        assert "claim_appointment_command(" in route
        assert "complete_appointment_command(" in route
        assert f"operation_id={details['operation']}" in route
        assert f"route_family={details['family']}" in route
        assert "request_body=body.model_dump(mode=\"json\")" in route


def test_router_constants_match_checkpoint_family_values():
    router_text = _read(ROUTER)

    for details in CONFIRMATION_FAMILIES.values():
        assert f'{details["operation"]} = "{details["operation_value"]}"' in router_text
        assert f'{details["family"]} = "{details["family_value"]}"' in router_text


def test_checkpoint_preserves_raw_proposal_and_runtime_gates():
    text = _compact(_read(CHECKPOINT))

    for phrase in (
        "proposal-only route idempotency enforcement",
        "raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement",
        "slot-search reservation or replay semantics",
        "provider calls or live provider gates",
        "runtime FGA clients",
        "external patient clients",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
        "model-to-database writes outside REST command handlers",
    ):
        assert phrase in text


def test_checkpoint_records_shared_fail_closed_decision_map():
    text = _read(CHECKPOINT)

    for phrase in (
        "| `replay` | Stored status | Stored response body |",
        "| `conflict` | `409` | `idempotency_key_conflict` |",
        "| `in_progress` | `409` | `idempotency_key_in_progress` |",
        "| `stale_in_progress` | `409` | `idempotency_key_stale_in_progress` |",
        "| `failed_transient` | `503` | `idempotency_key_failed_transient` |",
    ):
        assert phrase in text


def test_router_keeps_non_confirm_surfaces_outside_appointment_idempotency():
    router_text = _read(ROUTER)
    spans = [
        ("def cancel_appointment(", "@router.post(\n    \"/proposals/delete-confirm\""),
        ("def propose_delete_appointment(", "@router.get(\"/slots/{practitioner_id}\""),
        ("def propose_update_appointment(", "def _block_bernie_update_confirmation("),
        ("def update_appointment(", "def get_checkin_defaults("),
        ("def list_appointments(", "@router.post(\"/proposals/create\""),
    ]

    for start_marker, end_marker in spans:
        span = router_text[
            router_text.index(start_marker):router_text.index(end_marker, router_text.index(start_marker))
        ]
        # Proposal handlers now have Idempotency-Key syntactic validation
        # Non-proposal surfaces must still not have it
        assert "claim_appointment_command(" not in span
        assert "complete_appointment_command(" not in span


def test_checkpoint_recommends_policy_decision_before_broader_expansion():
    text = _read(CHECKPOINT)
    compact = _compact(text)

    assert "Recommended Sprint 146" in text
    assert "route-level integration tests" in compact
    assert "all five wired confirmation families" in compact
    assert "five wired confirmation families against a real DB session" in compact
    assert "Do not open proposal-only or raw compatibility enforcement" in compact
