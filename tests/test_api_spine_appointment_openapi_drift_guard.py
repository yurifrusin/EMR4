import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"
INVENTORY = ROOT / "orchestration" / "api_spine_appointment_command_alignment_inventory.md"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"
PREFIX = "/api/v1/appointments"


EXPECTED_ROUTE_INVENTORY = (
    ("GET", "/types", "list_appointment_types", "read-only route"),
    ("GET", "", "list_appointments", "read-only route"),
    ("POST", "", "create_appointment", "compatibility write"),
    ("POST", "/proposals/create", "propose_create_appointment", "proposal command"),
    ("POST", "/proposals/create/confirm", "confirm_create_proposal_route", "confirm command"),
    ("POST", "/proposals/update/confirm", "confirm_update_proposal_route", "confirm command"),
    ("POST", "/proposals/update/{appointment_id}", "propose_update_appointment", "proposal command"),
    ("POST", "/proposals/bernie/tool-intent", "propose_bernie_tool_intent", "command-style read"),
    ("POST", "/proposals/status/{appointment_id:uuid}", "propose_status_update", "proposal command"),
    ("POST", "/proposals/waiting-area/{appointment_id}", "propose_waiting_area_update", "proposal command"),
    ("POST", "/proposals/status/confirm", "confirm_status_proposal_route", "confirm command"),
    ("POST", "/proposals/status-confirm", "confirm_status_proposal_route", "compatibility alias"),
    (
        "POST",
        "/proposals/check-in/{appointment_id:uuid}",
        "propose_check_in_appointment",
        "proposal command",
    ),
    (
        "POST",
        "/proposals/check-in/confirm",
        "confirm_check_in_proposal_route",
        "confirm command",
    ),
    ("GET", "/waiting-room", "get_waiting_room", "read-only route"),
    ("GET", "/bernie/pilot-eligibility", "get_bernie_pilot_eligibility", "read-only route"),
    ("GET", "/bernie/sessions/active", "get_active_bernie_session", "read-only route"),
    ("POST", "/bernie/sessions/new", "create_new_bernie_session", "Bernie session command"),
    (
        "POST",
        "/bernie/sessions/{session_id}/events",
        "append_bernie_session_event",
        "Bernie session command",
    ),
    (
        "POST",
        "/proposals/bernie/interpret-booking-instruction",
        "interpret_bernie_booking_instruction",
        "command-style read",
    ),
    ("GET", "/{appointment_id}", "get_appointment", "read-only route"),
    ("PUT", "/{appointment_id}", "update_appointment", "compatibility write"),
    ("GET", "/{appointment_id}/checkin-defaults", "get_checkin_defaults", "read-only route"),
    ("GET", "/{appointment_id}/audit", "get_appointment_audit", "read-only route"),
    ("PATCH", "/{appointment_id}/status", "update_appointment_status", "compatibility write"),
    ("DELETE", "/{appointment_id}", "cancel_appointment", "compatibility write"),
    ("POST", "/proposals/delete-confirm", "confirm_delete_proposal_route", "confirm command"),
    ("POST", "/proposals/delete/{appointment_id}", "propose_delete_appointment", "proposal command"),
    ("GET", "/slots/{practitioner_id}", "get_available_slots", "read-only route"),
    ("POST", "/proposals/slot-search", "propose_slot_search", "command-style read"),
    (
        "POST",
        "/proposals/slot-search/normalize",
        "normalize_slot_search_proposal_command",
        "command-style read",
    ),
    ("POST", "/proposals/slot-search/normalized", "propose_normalized_slot_search", "command-style read"),
    ("POST", "/proposals/slot-search/selection", "propose_slot_selection_for_create", "command-style read"),
    (
        "POST",
        "/proposals/reception-one/compose",
        "compose_reception_one_product_context_proposal",
        "command-style read",
    ),
    ("POST", "/proposals/bernie/supervised-booking", "propose_bernie_supervised_booking", "command-style read"),
    ("POST", "/proposals/create/confirm-bernie", "confirm_bernie_create_proposal", "confirm command"),
    (
        "POST",
        "/proposals/bernie/no-slot-suggestion-selection",
        "select_no_slot_suggestion",
        "command-style read",
    ),
)

EXPECTED_OPENAPI_PATHS = {
    "/appointments/proposals/create",
    "/appointments/proposals/create/confirm",
    "/appointments/proposals/update",
    "/appointments/proposals/update/confirm",
    "/appointments/proposals/status",
    "/appointments/proposals/status/confirm",
    "/appointments/proposals/check-in/{appointment_id}",
    "/appointments/proposals/check-in/confirm",
    "/appointments/proposals/delete",
    "/appointments/proposals/delete/confirm",
    "/appointments/proposals/slot-search/normalize",
    "/appointments/proposals/slot-search",
    "/appointments/proposals/slot-search/select",
    "/appointments/proposals/reception-one/compose",
}

DELIBERATE_OPENAPI_DRIFT = (
    (
        "POST",
        "/proposals/delete-confirm",
        "/appointments/proposals/delete/confirm",
    ),
    (
        "POST",
        "/proposals/slot-search/selection",
        "/appointments/proposals/slot-search/select",
    ),
)


def _router_routes():
    source = APPOINTMENTS_ROUTER.read_text(encoding="utf-8")
    module = ast.parse(source)
    routes = {}
    for node in module.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue
            if not isinstance(func.value, ast.Name) or func.value.id != "router":
                continue
            method = func.attr.upper()
            if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                continue
            route = decorator.args[0].value
            routes[(method, route)] = node.name
    return routes


def _public_path(route: str) -> str:
    return PREFIX if route == "" else f"{PREFIX}{route}"


def _inventory_row(text: str, method: str, route: str) -> str:
    public = _public_path(route)
    marker = f"| `{method} {public}` |"
    matches = [line for line in text.splitlines() if line.startswith(marker)]
    assert len(matches) == 1, f"Expected one inventory row for {method} {public}, got {matches}"
    return matches[0]


def _openapi_paths() -> set[str]:
    text = OPENAPI.read_text(encoding="utf-8")
    return set(re.findall(r"^  (/appointments/[^:]+):$", text, flags=re.MULTILINE))


def test_router_route_inventory_is_exhaustive_for_current_appointment_router():
    routes = _router_routes()

    expected_route_keys = {(method, route) for method, route, _, _ in EXPECTED_ROUTE_INVENTORY}
    assert set(routes) == expected_route_keys


def test_inventory_matches_current_router_handlers_and_classifications():
    routes = _router_routes()
    inventory = INVENTORY.read_text(encoding="utf-8")

    for method, route, handler, classification in EXPECTED_ROUTE_INVENTORY:
        assert routes[(method, route)] == handler
        row = _inventory_row(inventory, method, route)
        assert f"| `{handler}` |" in row
        assert f"| `{classification}` |" in row


def test_deliberate_openapi_drift_is_documented_against_canonical_paths():
    inventory = INVENTORY.read_text(encoding="utf-8")
    openapi_paths = _openapi_paths()

    for method, route, openapi_path in DELIBERATE_OPENAPI_DRIFT:
        row = _inventory_row(inventory, method, route)
        assert _public_path(route) in row
        assert openapi_path in inventory
        assert openapi_path in openapi_paths


def test_openapi_path_set_changes_are_intentional():
    assert _openapi_paths() == EXPECTED_OPENAPI_PATHS


def test_openapi_draft_keeps_no_explicit_bernie_variants_yet():
    openapi_paths = _openapi_paths()
    inventory = INVENTORY.read_text(encoding="utf-8")

    for bernie_fragment in (
        "/bernie/tool-intent",
        "/bernie/interpret-booking-instruction",
        "/bernie/supervised-booking",
        "/confirm-bernie",
        "/bernie/no-slot-suggestion-selection",
        "/bernie/sessions",
    ):
        assert bernie_fragment in inventory
        assert not any(bernie_fragment in path for path in openapi_paths)
