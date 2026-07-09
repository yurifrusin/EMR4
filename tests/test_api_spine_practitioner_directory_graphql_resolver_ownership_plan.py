import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-graphql-resolver-ownership-plan.md"
)
REST_PROPOSAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-first-runtime-implementation-proposal.md"
)
SDL = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
DAG = ROOT / "docs" / "api-spine" / "external-read-model-readiness-dag.json"
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
APP = ROOT / "app"


RUNTIME_GRAPHQL_IMPORTS = (
    "import strawberry",
    "from strawberry",
    "import graphene",
    "from graphene",
    "import ariadne",
    "from ariadne",
    "from graphql",
    "import graphql",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _gate_rows() -> dict[str, str]:
    section = _read(PLAN).split("## Gate Verdict", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = cells[1].strip("`")
    return rows


def _type_body(name: str) -> str:
    text = _read(SDL)
    match = re.search(rf"type {name}\s*\{{(?P<body>.*?)\n\}}", text, re.S)
    assert match, f"Missing SDL type {name}"
    return match.group("body")


def _field_names(type_name: str) -> set[str]:
    fields = set()
    for line in _type_body(type_name).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('"') or stripped.startswith("#"):
            continue
        name = stripped.split(":", 1)[0].split("(", 1)[0].strip()
        if name:
            fields.add(name)
    return fields


def _app_python_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(APP.rglob("*.py"))
    )


def test_graphql_sdl_declares_practice_practitioners_without_mutation():
    sdl = _read(SDL)
    practice = _type_body("Practice")

    assert "schema {\n  query: Query\n}" in sdl
    assert "type Mutation" not in sdl
    assert (
        "practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0): "
        "[Practitioner!]!"
    ) in practice


def test_graphql_practitioner_field_set_matches_rest_projection():
    assert _field_names("Practitioner") == {
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation",
    }

    plan = _read(PLAN)
    proposal = _read(REST_PROPOSAL)
    for field in ["id", "displayName", "roleLabel", "active", "defaultLocation"]:
        assert f"`{field}`" in plan
        assert f"`{field}`" in proposal


def test_graphql_resolver_gate_verdict_keeps_runtime_false():
    assert _gate_rows() == {
        "graphql_resolver_owner_defined": "true",
        "graphql_authorization_plan_defined": "true",
        "graphql_runtime_code_authorized": "false",
        "graphql_server_dependency_authorized": "false",
        "graphql_resolver_ready": "false",
        "rest_route_ready": "false",
        "external_read_model_runtime_ready": "false",
        "readiness_snapshot_decision": "blocked",
        "rest_read_route_is_prerequisite": "true",
        "rest_read_service_is_sole_data_path": "true",
        "pause_required_before_resolver_code": "true",
        "explicit_yuri_go_no_go_required": "true",
    }


def test_no_graphql_runtime_dependency_or_import_exists():
    app_text = _app_python_text().lower()
    for fragment in RUNTIME_GRAPHQL_IMPORTS:
        assert fragment not in app_text

    dependency_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace").lower()
        for pattern in ["pyproject.toml", "requirements*.txt"]
        for path in ROOT.glob(pattern)
    )
    for package in ["strawberry-graphql", "graphene", "ariadne"]:
        assert package not in dependency_text


def test_no_query_practice_practitioners_resolver_exists():
    app_text = _app_python_text()

    forbidden_fragments = [
        "app/graphql/resolvers/practice.py",
        "def resolve_practitioners",
        "async def resolve_practitioners",
        "Query.practice.practitioners",
        "@strawberry.field",
        "ObjectType(\"Practice\")",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in app_text


def test_readiness_dag_and_snapshot_graphql_resolver_wiring_remain_blocked():
    dag = json.loads(DAG.read_text(encoding="utf-8"))
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert dag["decision"] == "blocked"
    assert dag["readiness"]["graphql_resolver_ready"] is False
    node = next(node for node in dag["nodes"] if node["id"] == "graphql_resolver_wiring")
    assert node["status"] == "blocked"
    assert node["runtime_authority"] is False

    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["rest_route_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False


def test_authorization_and_tenancy_plan_defined():
    compact = _compact(_read(PLAN))

    for phrase in [
        "GraphQL context must authenticate the viewer using the same principal model as REST",
        "`Query.practice(id: ID)` defaults to the viewer's practice",
        "differs from the viewer's practice returns `null` or a generic not-found response",
        "every read filters `Practitioner.practice_id == viewer.practice_id`",
        "`activeOnly=false` requires `Admin` or `PracticeOwner` authority",
        "`UNAUTHENTICATED`",
        "`FORBIDDEN`",
        "`BAD_USER_INPUT`",
        "must not accept a client-supplied `practiceId` on the `practitioners` field",
    ]:
        assert phrase in compact


def test_rest_route_and_read_service_are_prerequisites():
    compact = _compact(_read(PLAN))

    for phrase in [
        "GraphQL must not become the first path to the practitioner table",
        "REST consumer runtime evidence passed",
        "`GET /api/v1/practice/practitioners` is implemented, tested, merged",
        "A shared practitioner directory read service exists",
        "`app/services/practice/practitioner_directory_read.py`",
        "GraphQL does not get an independent database path",
    ]:
        assert phrase in compact


def test_field_sensitivity_and_default_location_join_match_rest_contract():
    text = _read(PLAN)

    for field in [
        "provider_number",
        "prescriber_number",
        "ahpra_number",
        "hpi_i",
        "practice_id",
        "created_at",
        "email",
        "phone",
        "address",
        "password_hash",
        "credentials",
        "schedule_overrides",
        "schedules",
        "appointments",
        "clinical logs",
        "roster internals",
        "raw SQLAlchemy model dumps",
        "location address, phone, email, billing details, or availability internals",
    ]:
        assert field in text

    for phrase in [
        "`PracticeLocation.id == Practitioner.default_location_id`",
        "`PracticeLocation.practice_id == viewer.practice_id`",
        "`PracticeLocation.is_active == true`",
        "`defaultLocation: null`",
        "`defaultLocation` as `{id, name}` only",
    ]:
        assert phrase in text


def test_pagination_cost_depth_and_n_plus_one_plan_defined():
    compact = _compact(_read(PLAN))

    for phrase in [
        "default page size | `50`",
        "maximum page size | `200`",
        "offset | default `0`, minimum `0`",
        "SDL now reserves `activeOnly`, `limit`, and `offset`",
        "ordering | `last_name`, then `first_name`, then `id`",
        "N+1 prevention | pre-join default locations in the read service or batch-load by location id",
        "max depth | production runtime must enforce a global depth limit before public use",
        "complexity/cost | production runtime must enforce a global complexity/cost budget before public use",
        "alias repetition | cost rules must count aliased repetitions",
        "must not ship with an unbounded `[Practitioner!]!` list",
    ]:
        assert phrase in compact


def test_required_static_tests_and_closed_gates_are_preserved():
    compact = _compact(_read(PLAN))

    for test_name in [
        "test_graphql_sdl_declares_practice_practitioners_without_mutation",
        "test_graphql_practitioner_field_set_matches_rest_projection",
        "test_graphql_resolver_gate_verdict_keeps_runtime_false",
        "test_no_graphql_runtime_dependency_or_import_exists",
        "test_no_query_practice_practitioners_resolver_exists",
        "test_readiness_dag_graphql_resolver_wiring_remains_blocked",
        "test_authorization_and_tenancy_plan_defined",
        "test_rest_route_and_read_service_are_prerequisites",
        "test_field_sensitivity_and_default_location_join_match_rest_contract",
        "test_pagination_cost_depth_and_n_plus_one_plan_defined",
        "test_closed_gates_preserved",
        "test_boundary_says_plan_is_not_runtime_or_production_readiness",
    ]:
        assert test_name in compact

    for phrase in [
        "adding GraphQL resolvers or GraphQL mutations",
        "adding a GraphQL runtime dependency or server",
        "adding GraphQL runtime database queries, joins, indexes, migrations, read services, or query services outside the existing shared REST read service",
        "changing the blocked readiness snapshot",
        "changing readiness flags to `true`",
        "provider calls or live provider gates",
        "provider dry-run wiring",
        "runtime FGA clients",
        "external patient clients",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
        "Access AI invocation wiring",
        "RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping",
        "practitioner create/update/onboarding commands",
        "appointment, roster, schedule, diary, billing, result, reminder, message",
        "model-to-database writes outside REST command handlers",
        "raw compatibility deprecation mode changes",
    ]:
        assert phrase in compact


def test_boundary_says_plan_is_not_runtime_or_production_readiness():
    compact = _compact(_read(PLAN))

    for phrase in [
        "static GraphQL ownership and authorization plan",
        "does not prove runtime GraphQL authorization",
        "resolver correctness",
        "REST route correctness",
        "database query correctness",
        "field-level authorization",
        "pagination performance",
        "deployment readiness",
        "provider readiness",
        "external directory readiness",
        "patient-facing client readiness",
        "production readiness",
    ]:
        assert phrase in compact
