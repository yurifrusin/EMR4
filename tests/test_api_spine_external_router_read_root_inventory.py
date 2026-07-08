import ast
import re
from pathlib import Path

from tests.test_api_spine_appointment_read_model_route_inventory import _graphql_query_fields
from tests.test_api_spine_appointment_openapi_drift_guard import EXPECTED_ROUTE_INVENTORY


ROOT = Path(__file__).resolve().parents[1]
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
INDEX_PATH = ROOT / "docs" / "api-spine" / "external-router-read-root-inventory.md"
ROUTERS = {
    "auth": ROOT / "app" / "routers" / "auth.py",
    "appointments": ROOT / "app" / "routers" / "appointments.py",
    "clinical": ROOT / "app" / "routers" / "clinical.py",
    "diary": ROOT / "app" / "routers" / "diary.py",
    "patients": ROOT / "app" / "routers" / "patients.py",
    "search": ROOT / "app" / "routers" / "search.py",
}
PATIENT_CONTEXT_SERVICE = ROOT / "app" / "services" / "bernie_patient_context.py"

EXTERNAL_ROOTS = {"viewer", "practice", "patient", "directorySearch"}
ALLOWED_COVERAGE = {"full", "partial", "gap"}
ALLOWED_ROUTE_POSTURES = {"read_only_route", "service_read_model", "read_model_gap"}
REQUIRED_BLOCKED_GATE_PHRASES = {
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "runtime FGA clients",
    "external patient clients",
    "GraphQL mutations",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "Access AI invocation wiring",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode change",
}
REQUIRED_STATIC_SOURCES = {
    "docs/api-spine/graphql/appointment-diary-read.graphql",
    "app/services/bernie_patient_context.py",
    "tests/test_api_spine_appointment_read_model_route_inventory.py",
}


def _router_prefix(source: str) -> str:
    match = re.search(r"APIRouter\(prefix=\"([^\"]+)\"", source)
    assert match, "router prefix not found"
    return match.group(1)


def _router_routes(path: Path) -> dict[tuple[str, str], str]:
    source = path.read_text(encoding="utf-8")
    prefix = _router_prefix(source)
    module = ast.parse(source)
    routes = {}
    for node in module.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
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
            routes[(method, f"{prefix}{route}")] = node.name
    return routes


def _all_router_routes() -> dict[tuple[str, str], str]:
    merged = {}
    for path in ROUTERS.values():
        merged.update(_router_routes(path))
    return merged


def _table_rows(section_heading: str = "## External Read Route Bridge") -> list[dict[str, str]]:
    text = INDEX_PATH.read_text(encoding="utf-8")
    section = text.split(section_heading, 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(
            {
                "surface": cells[0].strip("`"),
                "source": cells[1].strip("`"),
                "symbol": cells[2].strip("`"),
                "coverage": cells[3].strip("`"),
                "posture": cells[4].strip("`"),
                "notes": cells[5],
            }
        )
    return rows


def _method_route_parts(source: str) -> tuple[str, str]:
    method, route = source.split(" ", 1)
    return method, route


def test_external_inventory_covers_only_declared_external_query_roots():
    graphql_fields = _graphql_query_fields()
    assert EXTERNAL_ROOTS < graphql_fields

    root_rows = {
        row["surface"].split(".")[1]
        for row in _table_rows()
        if row["surface"].startswith("Query.")
        and "." not in row["surface"][len("Query.") :]
    }

    assert root_rows == EXTERNAL_ROOTS


def test_external_inventory_rows_have_allowed_static_posture():
    for row in _table_rows():
        assert row["coverage"] in ALLOWED_COVERAGE
        assert row["posture"] in ALLOWED_ROUTE_POSTURES
        if row["source"] == "none":
            assert row["symbol"] == "none"
            assert row["coverage"] == "gap"
            assert row["posture"] == "read_model_gap"
        elif row["source"].startswith("GET "):
            assert row["posture"] == "read_only_route"
            assert row["coverage"] in {"full", "partial"}
        else:
            assert row["source"] == "app/services/bernie_patient_context.py"
            assert row["posture"] == "service_read_model"
            assert row["coverage"] == "partial"


def test_external_inventory_get_routes_exist_without_importing_routers():
    routes = _all_router_routes()

    for row in _table_rows():
        if not row["source"].startswith("GET "):
            continue
        method, route = _method_route_parts(row["source"])
        assert method == "GET"
        assert routes[(method, route)] == row["symbol"]


def test_external_inventory_service_source_exists_without_route_claim():
    source = PATIENT_CONTEXT_SERVICE.read_text(encoding="utf-8")
    module = ast.parse(source)
    functions = {
        node.name
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    service_rows = [row for row in _table_rows() if row["posture"] == "service_read_model"]
    assert service_rows == [
        {
            "surface": "Query.patient.bookingContext",
            "source": "app/services/bernie_patient_context.py",
            "symbol": "build_patient_booking_context",
            "coverage": "partial",
            "posture": "service_read_model",
            "notes": "Current patient booking context is a backend service used by Bernie; it is not exposed as a standalone read route.",
        }
    ]
    assert "build_patient_booking_context" in functions


def test_external_inventory_does_not_admit_post_or_write_routes():
    bridge_sources = {row["source"] for row in _table_rows()}

    assert not any(source.startswith(("POST ", "PUT ", "PATCH ", "DELETE ")) for source in bridge_sources)
    assert "GET /api/v1/patients/search" not in bridge_sources
    assert "GET /api/v1/patients/duplicate-candidates" not in bridge_sources
    assert "GET /api/v1/patients/duplicate-groups" not in bridge_sources

    appointment_write_routes = {
        f"{method} /api/v1/appointments{route}"
        for method, route, _, classification in EXPECTED_ROUTE_INVENTORY
        if classification == "compatibility write" or method != "GET"
    }
    assert bridge_sources.isdisjoint(appointment_write_routes)


def test_directory_search_sources_are_limited_to_current_local_directory_reads():
    rows = [row for row in _table_rows() if row["surface"].startswith("Query.directorySearch")]
    mapped_sources = {row["source"] for row in rows if row["source"] != "none"}
    gap_surfaces = {row["surface"] for row in rows if row["source"] == "none"}

    assert mapped_sources == {"GET /api/v1/search-mbs", "GET /api/v1/search-snomed"}
    assert gap_surfaces == {"Query.directorySearch.RACGP_GUIDELINES", "Query.directorySearch.COCHRANE_LIBRARY"}


def test_external_inventory_preserves_closed_gate_boundary():
    text = INDEX_PATH.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for phrase in REQUIRED_BLOCKED_GATE_PHRASES:
        assert phrase in text
    assert "does not authorize" in text
    assert "does not create GraphQL resolvers" in text
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "practice-knowledge facts" in text
    assert "do not become `Query.directorySearch`" in text


def test_external_inventory_names_static_sources():
    text = INDEX_PATH.read_text(encoding="utf-8")

    for source in REQUIRED_STATIC_SOURCES:
        assert source in text
    for router in ROUTERS.values():
        assert str(router.relative_to(ROOT)).replace("\\", "/") in text


def test_external_inventory_keeps_graphql_read_only():
    text = GRAPHQL_PATH.read_text(encoding="utf-8")
    assert "type Mutation" not in text
    assert "schema {\n  query: Query\n}" in text
