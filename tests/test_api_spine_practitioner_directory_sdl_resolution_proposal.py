import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-sdl-pagination-default-location-resolution-proposal.md"
)
SDL = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
REST_PROPOSAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-first-runtime-implementation-proposal.md"
)
DRIFT_CONTRACT = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-rest-graphql-drift-contract.md"
)
SECURITY_PREFLIGHT = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-security-audit-test-harness-preflight.md"
)
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
APP = ROOT / "app"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _gate_rows() -> dict[str, str]:
    section = _read(PROPOSAL).split("## Gate Verdict", 1)[1].split("\n## ", 1)[0]
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


def _field_line(type_name: str, field_name: str) -> str:
    for line in _type_body(type_name).splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{field_name}") and ":" in stripped:
            return stripped
    raise AssertionError(f"Missing {type_name}.{field_name}")


def _app_python_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(APP.rglob("*.py"))
    )


def test_sdl_resolution_gate_verdict_keeps_runtime_blocked():
    assert _gate_rows() == {
        "sdl_resolution_proposal_defined": "true",
        "practice_location_brief_recommended": "true",
        "offset_pagination_args_recommended": "true",
        "bare_list_return_preserved_for_first_slice": "true",
        "connection_or_wrapper_rejected_for_first_slice": "true",
        "current_default_location_drift_still_present": "true",
        "current_pagination_drift_still_present": "true",
        "sdl_changes_authorized": "false",
        "runtime_code_authorized": "false",
        "rest_route_ready": "false",
        "graphql_resolver_ready": "false",
        "external_read_model_runtime_ready": "false",
        "readiness_snapshot_decision": "blocked",
        "pause_required_before_sdl_or_runtime_code": "true",
        "explicit_yuri_go_no_go_required": "true",
    }


def test_current_sdl_default_location_drift_is_still_present():
    sdl = _read(SDL)

    assert _field_line("Practitioner", "defaultLocation") == "defaultLocation: PracticeLocation"
    assert "type PracticeLocationBrief" not in sdl
    assert set(
        line.strip().split(":", 1)[0]
        for line in _type_body("PracticeLocation").splitlines()
        if ":" in line
    ) == {"id", "name", "displayOrder", "active"}


def test_current_sdl_pagination_drift_is_still_present():
    practitioners = _field_line("Practice", "practitioners")

    assert practitioners == "practitioners(activeOnly: Boolean = true): [Practitioner!]!"
    args = practitioners.split("(", 1)[1].split(")", 1)[0]
    for arg in ["limit", "offset", "first", "after", "last", "before"]:
        assert arg not in args
    assert "PractitionerListResult" not in _read(SDL)
    assert "PractitionerConnection" not in _read(SDL)


def test_proposal_recommends_practice_location_brief():
    text = _read(PROPOSAL)

    for phrase in [
        "type PracticeLocationBrief",
        "id: ID!",
        "name: String!",
        "defaultLocation: PracticeLocationBrief",
        "type-level guarantee",
        "mirrors REST `PractitionerDefaultLocationOut`",
        "leaves full `PracticeLocation` untouched for diary, room, roster",
        "Rejected alternatives",
    ]:
        assert phrase in text


def test_proposal_recommends_offset_pagination_args_matching_rest():
    text = _read(PROPOSAL)
    rest = _read(REST_PROPOSAL)

    for phrase in [
        "activeOnly: Boolean = true",
        "limit: Int = 50",
        "offset: Int = 0",
        "): [Practitioner!]!",
        "`1..200`",
        "`>=0`",
        "same cap as REST",
        "same offset as REST",
        "mirrors REST `activeOnly`, `limit`, and `offset` exactly",
    ]:
        assert phrase in text
    for phrase in [
        "`activeOnly` | `bool`, default `true`, alias preserved as camelCase",
        "`limit` | `int`, default `50`, `ge=1`, `le=200`",
        "`offset` | `int`, default `0`, `ge=0`",
    ]:
        assert phrase in rest


def test_proposal_rejects_wrapper_and_connection_for_first_slice():
    compact = _compact(_read(PROPOSAL))

    for phrase in [
        "bare `list[PractitionerOut]` REST response",
        "`PractitionerListResult { items, totalCount, hasMore }`",
        "Relay-style `PractitionerConnection`",
        "GraphQL-only translation layer",
        "server-capped list with no args",
        "silently truncate clients",
    ]:
        assert phrase in compact


def test_error_and_pagination_semantics_documented():
    compact = _compact(_read(PROPOSAL))

    for phrase in [
        "unauthenticated or inactive viewer | `UNAUTHENTICATED`",
        "`activeOnly=false` without `Admin` or `PracticeOwner` | `FORBIDDEN`",
        "`limit < 1` | `BAD_USER_INPUT`",
        "`limit > 200` | `BAD_USER_INPUT`",
        "`offset < 0` | `BAD_USER_INPUT`",
        "empty authorized practice | `[]`",
        "cross-practice practitioners | silently absent through tenancy filter",
        "inactive or other-practice default location | `defaultLocation: null`",
        "raw SQL errors | never exposed",
        "`Practitioner.last_name` ascending",
        "`Practitioner.first_name` ascending",
        "`Practitioner.id` ascending",
    ]:
        assert phrase in compact


def test_relationship_to_prior_contracts_documented():
    compact = _compact(_read(PROPOSAL))

    for phrase in [
        "Sprint 227 REST proposal",
        "Sprint 228 GraphQL resolver ownership plan",
        "Sprint 229 drift contract",
        "Sprint 230 security/audit preflight",
        "REST route -> shared read service -> SDL/resolver",
        "Authn/authz, tenancy, anti-enumeration, no audit write",
    ]:
        assert phrase in compact
    assert "known_and_blocked_drift" in _read(DRIFT_CONTRACT)
    assert "default-location join filters same-practice active locations only" in _read(
        SECURITY_PREFLIGHT
    )


def test_future_runtime_sdl_tests_are_listed():
    text = _read(PROPOSAL)

    for phrase in [
        "`PracticeLocationBrief` exists and has exactly `id` and `name`",
        "`Practitioner.defaultLocation` points to `PracticeLocationBrief`",
        "full `PracticeLocation` remains available for diary/appointment contexts",
        "`Practice.practitioners` includes `activeOnly`, `limit`, and `offset`",
        "`limit` defaults to `50` and rejects values outside `1..200`",
        "`offset` defaults to `0` and rejects negative values",
        "`activeOnly=false` returns `FORBIDDEN`",
        "empty authorized practices return an empty list",
        "other-practice practitioners remain silently absent",
        "inactive or other-practice default locations return `null`",
        "ordering matches REST `last_name`, `first_name`, `id`",
        "no GraphQL mutations are introduced",
    ]:
        assert phrase in text


def test_current_code_has_no_sdl_runtime_route_schema_service_or_resolver_changes():
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
        "import strawberry",
        "from strawberry",
        "import graphene",
        "from graphene",
        "import ariadne",
        "from ariadne",
    ]:
        assert fragment not in app_text
    assert "type PracticeLocationBrief" not in _read(SDL)
    assert "PractitionerListResult" not in _read(SDL)
    assert "PractitionerConnection" not in _read(SDL)


def test_readiness_snapshot_remains_blocked():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False
    assert snapshot["runtime_or_memory_ready"] is False
    assert snapshot["write_authority_ready"] is False


def test_closed_gates_preserved():
    compact = _compact(_read(PROPOSAL))

    for phrase in [
        "changing the SDL",
        "adding `PracticeLocationBrief` to the SDL",
        "changing `Practitioner.defaultLocation`",
        "adding `limit` or `offset` arguments to `Practice.practitioners`",
        "adding `PractitionerListResult` or `PractitionerConnection`",
        "adding a REST practitioner directory route",
        "adding GraphQL resolvers or GraphQL mutations",
        "adding a GraphQL runtime dependency or server",
        "adding Pydantic runtime schemas",
        "adding `app/services/practice/` or a practitioner directory read service",
        "adding database queries, joins, indexes, migrations, read services, or query services",
        "adding audit writes or audit migrations",
        "adding rate-limiting middleware",
        "adding field-encryption code",
        "adding RLS migrations or policies",
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


def test_boundary_says_proposal_is_not_runtime_or_production_readiness():
    compact = _compact(_read(PROPOSAL))

    for phrase in [
        "static SDL resolution proposal",
        "does not prove runtime REST authorization",
        "GraphQL authorization",
        "resolver correctness",
        "route correctness",
        "database query correctness",
        "field-level authorization",
        "audit implementation",
        "SDL correctness after edit",
        "RLS",
        "field encryption",
        "rate limiting",
        "pagination performance",
        "deployment readiness",
        "provider readiness",
        "external directory readiness",
        "patient-facing client readiness",
        "production readiness",
    ]:
        assert phrase in compact
