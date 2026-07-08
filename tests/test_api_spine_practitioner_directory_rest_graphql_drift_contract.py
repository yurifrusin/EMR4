import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-rest-graphql-drift-contract.md"
)
REST_PROPOSAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-first-runtime-implementation-proposal.md"
)
GRAPHQL_PLAN = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-graphql-resolver-ownership-plan.md"
)
SDL = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
APP = ROOT / "app"


CANONICAL_FIELDS = {"id", "displayName", "roleLabel", "active", "defaultLocation"}
FORBIDDEN_FIELDS = {
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
    "location address",
    "location phone",
    "location email",
    "location billing details",
    "availability internals",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _gate_rows() -> dict[str, str]:
    section = _read(CONTRACT).split("## Gate Verdict", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = cells[1].strip("`")
    return rows


def _type_body(name: str) -> str:
    match = re.search(rf"type {name}\s*\{{(?P<body>.*?)\n\}}", _read(SDL), re.S)
    assert match, f"Missing SDL type {name}"
    return match.group("body")


def _field_names(type_name: str) -> set[str]:
    fields = set()
    for line in _type_body(type_name).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('"') or stripped.startswith("#"):
            continue
        fields.add(stripped.split(":", 1)[0].split("(", 1)[0].strip())
    return fields


def _app_python_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(APP.rglob("*.py"))
    )


def test_drift_contract_gate_verdict_keeps_runtime_blocked():
    assert _gate_rows() == {
        "rest_graphql_drift_contract_defined": "true",
        "canonical_projection_field_set_defined": "true",
        "sensitive_exclusion_parity_defined": "true",
        "shared_read_service_invariants_defined": "true",
        "default_location_shape_status": "known_and_blocked_drift",
        "graphql_pagination_shape_status": "known_and_blocked_drift",
        "shared_read_service_exists": "false",
        "runtime_code_authorized": "false",
        "rest_route_ready": "false",
        "graphql_resolver_ready": "false",
        "external_read_model_runtime_ready": "false",
        "readiness_snapshot_decision": "blocked",
        "pause_required_before_route_or_resolver_code": "true",
        "explicit_yuri_go_no_go_required": "true",
    }


def test_canonical_projection_is_exactly_five_fields():
    text = _read(CONTRACT)

    for field in CANONICAL_FIELDS:
        assert f"`{field}`" in text
    assert "The canonical field set is:" in text
    assert "Adding, removing, or renaming a field on only one surface is a drift defect" in text
    assert "must never leak as `is_active`" in text


def test_sdl_practitioner_field_set_matches_projection():
    assert _field_names("Practitioner") == CANONICAL_FIELDS
    assert "practitioners(activeOnly: Boolean = true): [Practitioner!]!" in _type_body(
        "Practice"
    )
    assert "type Mutation" not in _read(SDL)


def test_default_location_shape_is_known_blocked_drift():
    text = _read(CONTRACT)
    compact = _compact(text)
    sdl_location_fields = _field_names("PracticeLocation")

    assert sdl_location_fields == {"id", "name", "displayOrder", "active"}
    for phrase in [
        "`defaultLocation` in the Sprint 227 REST contract is `{id, name}` only",
        "current SDL points `Practitioner.defaultLocation` at full `PracticeLocation`",
        "`PracticeLocationBrief`",
        "`known_and_blocked_drift` findings",
    ]:
        assert phrase in compact


def test_graphql_pagination_shape_is_known_blocked_drift():
    text = _read(CONTRACT)
    compact = _compact(text)
    practice = _type_body("Practice")

    assert "practitioners(activeOnly: Boolean = true): [Practitioner!]!" in practice
    assert "limit" not in practice.split("practitioners(", 1)[1].split(")", 1)[0]
    assert "offset" not in practice.split("practitioners(", 1)[1].split(")", 1)[0]
    for phrase in [
        "without pagination arguments",
        "add reviewed pagination arguments",
        "server-side capped list",
        "cannot truncate clients silently",
    ]:
        assert phrase in compact


def test_shared_read_service_invariants_are_defined_but_not_implemented():
    text = _read(CONTRACT)

    for phrase in [
        "future `app/services/practice/practitioner_directory_read.py`",
        "`Practitioner.practice_id == viewer.practice_id`",
        "`displayName` derivation",
        "`activeOnly=true` default filtering",
        "`activeOnly=false` admin/owner gate",
        "deterministic ordering by `Practitioner.last_name`, then",
        "`limit=50`, maximum `200`, `offset=0`",
        "same-practice active default-location join",
        "display-safe `{id, name}` default-location projection",
        "provider/Access AI/RAG/GraphRAG/trove prohibition",
        "no write authority",
    ]:
        assert phrase in text
    assert not (APP / "services" / "practice").exists()


def test_sensitive_exclusion_parity_is_canonical():
    contract = _read(CONTRACT)
    rest = _read(REST_PROPOSAL)
    graphql = _read(GRAPHQL_PLAN)

    for field in FORBIDDEN_FIELDS:
        assert field in contract
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
    ]:
        assert field in rest
        assert field in graphql
    assert "PractitionerBrief" in contract
    assert "Bernie practitioner evidence" in contract


def test_active_only_pagination_ordering_and_error_parity_defined():
    compact = _compact(_read(CONTRACT))

    for phrase in [
        "`activeOnly` | default `true`; camelCase preserved on both surfaces",
        "inactive inclusion | `activeOnly=false` requires `Admin` or `PracticeOwner`",
        "REST role failure | `403`",
        "GraphQL role failure | `FORBIDDEN`",
        "unauthenticated | REST `401`; GraphQL `UNAUTHENTICATED`",
        "invalid arguments | REST `422`; GraphQL `BAD_USER_INPUT`",
        "ordering | `last_name`, then `first_name`, then `id`",
        "empty result | REST `200 []`; GraphQL empty list",
        "cross-practice data | silently absent through tenancy filtering",
    ]:
        assert phrase in compact


def test_current_code_has_no_route_schema_service_or_resolver():
    app_text = _app_python_text()

    assert not (APP / "routers" / "practice.py").exists()
    assert not (APP / "schemas" / "practice.py").exists()
    assert not (APP / "services" / "practice").exists()
    for fragment in [
        "class PractitionerOut",
        "class PractitionerDefaultLocationOut",
        "def list_practitioners",
        "def get_practitioners",
        "Query.practice.practitioners",
        "@strawberry.field",
        "ObjectType(\"Practice\")",
        "import strawberry",
        "from strawberry",
        "import graphene",
        "from graphene",
        "import ariadne",
        "from ariadne",
    ]:
        assert fragment not in app_text


def test_readiness_snapshot_remains_blocked():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False
    assert snapshot["runtime_or_memory_ready"] is False
    assert snapshot["write_authority_ready"] is False


def test_closed_gates_preserved():
    compact = _compact(_read(CONTRACT))

    for phrase in [
        "adding a REST practitioner directory route",
        "adding GraphQL resolvers or GraphQL mutations",
        "adding a GraphQL runtime dependency or server",
        "changing the SDL",
        "adding Pydantic runtime schemas",
        "adding `app/services/practice/` or a practitioner directory read service",
        "adding database queries, joins, indexes, migrations, read services, or query services",
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


def test_boundary_says_contract_is_not_runtime_or_production_readiness():
    compact = _compact(_read(CONTRACT))

    for phrase in [
        "static REST/GraphQL drift contract",
        "does not prove runtime REST authorization",
        "GraphQL authorization",
        "resolver correctness",
        "route correctness",
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
