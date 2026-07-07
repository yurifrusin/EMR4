import ast
import re
from pathlib import Path

from tests.test_api_spine_appointment_openapi_drift_guard import (
    EXPECTED_ROUTE_INVENTORY,
)

ROOT = Path(__file__).resolve().parents[1]
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"
INDEX_PATH = ROOT / "docs" / "api-spine" / "appointment-read-model-route-inventory.md"

ALLOWED_COVERAGE = {"full", "partial", "external", "unmapped"}
ALLOWED_ROUTE_POSTURES = {"read_only_route", "read_model_only"}

REQUIRED_BLOCKED_GATE_PHRASES = {
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
}

FORBIDDEN_GRAPHQL_REFERENCE_FIELDS = {
    "idempotencyKey",
    "idempotency_key",
    "confirmer",
}


def _router_routes() -> dict[tuple[str, str], str]:
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
            routes[(method, decorator.args[0].value)] = node.name
    return routes


def _graphql_query_fields() -> set[str]:
    text = GRAPHQL_PATH.read_text(encoding="utf-8")
    match = re.search(r"type Query \{(?P<body>.*?)\n\}", text, re.S)
    assert match, "GraphQL type Query not found"
    fields = set()
    for raw_line in match.group("body").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith('"'):
            continue
        field_match = re.match(r"^([a-zA-Z0-9_]+)", line)
        if field_match:
            fields.add(field_match.group(1))
    return fields


def _read_bridge_rows() -> list[dict[str, str]]:
    return _table_rows("## Read Route Bridge")


def _outside_read_graph_rows() -> list[dict[str, str]]:
    rows = []
    for row in _table_rows("## Outside The Read Graph"):
        rows.append(
            {
                "method_route": row["col0"],
                "handler": row["col1"],
                "classification": row["col2"],
                "status": row["col3"],
            }
        )
    return rows


def _table_rows(section_heading: str) -> list[dict[str, str]]:
    text = INDEX_PATH.read_text(encoding="utf-8")
    section = text.split(section_heading, 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append({f"col{idx}": cell.strip("`") for idx, cell in enumerate(cells)})
    return rows


def _relative_route(public_route: str) -> str:
    if public_route == "none":
        return "none"
    prefix = "GET /api/v1/appointments"
    if public_route == prefix:
        return ""
    assert public_route.startswith(prefix)
    return public_route[len(prefix) :]


def _method_route_parts(method_route: str) -> tuple[str, str]:
    method, public_route = method_route.split(" ", 1)
    prefix = "/api/v1/appointments"
    if public_route == prefix:
        return method, ""
    assert public_route.startswith(prefix)
    return method, public_route[len(prefix) :]


def test_read_model_inventory_covers_all_graphql_query_roots():
    graphql_fields = _graphql_query_fields()
    indexed_roots = {
        row["col0"].split(".")[1]
        for row in _read_bridge_rows()
        if row["col0"].startswith("Query.") and "." not in row["col0"][len("Query.") :]
    }

    assert indexed_roots == graphql_fields


def test_read_model_inventory_covers_all_current_get_routes():
    expected_gets = {
        (route, handler)
        for method, route, handler, classification in EXPECTED_ROUTE_INVENTORY
        if method == "GET" and classification == "read-only route"
    }
    indexed_gets = {
        (_relative_route(row["col1"]), row["col2"])
        for row in _read_bridge_rows()
        if row["col1"] != "none"
    }

    assert indexed_gets == expected_gets


def test_read_model_inventory_routes_exist_as_get_handlers():
    routes = _router_routes()
    for row in _read_bridge_rows():
        coverage = row["col3"].strip("`")
        posture = row["col4"].strip("`")
        assert coverage in ALLOWED_COVERAGE
        assert posture in ALLOWED_ROUTE_POSTURES

        if row["col1"] == "none":
            assert row["col2"] == "none"
            assert posture == "read_model_only"
            assert coverage == "external"
            continue

        route = _relative_route(row["col1"])
        assert routes[("GET", route)] == row["col2"]
        assert posture == "read_only_route"
        assert coverage in {"full", "partial", "unmapped"}


def test_compatibility_writes_are_outside_read_graph():
    expected_compatibility_writes = {
        (method, route, handler, classification)
        for method, route, handler, classification in EXPECTED_ROUTE_INVENTORY
        if classification == "compatibility write"
    }
    indexed_compatibility_writes = set()

    for row in _outside_read_graph_rows():
        method, route = _method_route_parts(row["method_route"])
        indexed_compatibility_writes.add(
            (method, route, row["handler"], row["classification"])
        )
        assert row["status"] == "outside_read_graph"

    assert indexed_compatibility_writes == expected_compatibility_writes


def test_non_get_command_surfaces_do_not_enter_read_bridge():
    bridge_routes = {
        _relative_route(row["col1"])
        for row in _read_bridge_rows()
        if row["col1"] != "none"
    }
    non_get_commands = {
        route
        for method, route, _, classification in EXPECTED_ROUTE_INVENTORY
        if method != "GET" and classification != "compatibility write"
    }

    assert bridge_routes.isdisjoint(non_get_commands)


def test_inventory_preserves_command_field_boundary_for_graphql_references():
    text = INDEX_PATH.read_text(encoding="utf-8")

    for field in FORBIDDEN_GRAPHQL_REFERENCE_FIELDS:
        assert field not in text


def test_read_model_inventory_preserves_closed_gate_boundary():
    text = INDEX_PATH.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for phrase in REQUIRED_BLOCKED_GATE_PHRASES:
        assert phrase in text
    assert "does not authorize" in text
    assert "does not prove runtime resolver implementation" in compact
    assert "GraphQL mutations" in text


def test_read_model_inventory_names_static_sources():
    text = INDEX_PATH.read_text(encoding="utf-8")

    assert "docs/api-spine/graphql/appointment-diary-read.graphql" in text
    assert "app/routers/appointments.py" in text
    assert "tests/test_api_spine_appointment_openapi_drift_guard.py" in text
