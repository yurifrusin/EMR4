import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-first-runtime-implementation-proposal.md"
)
CANDIDATE = (
    ROOT / "docs" / "api-spine" / "practitioner-directory-route-schema-ownership-candidate.md"
)
CONSOLIDATION = (
    ROOT / "docs" / "api-spine" / "external-read-model-ownership-consolidation-preflight.md"
)
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
APP_DIR = ROOT / "app"
ROUTERS_DIR = APP_DIR / "routers"
SCHEMAS_DIR = APP_DIR / "schemas"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _python_text_under(path: Path) -> str:
    return "\n".join(
        child.read_text(encoding="utf-8", errors="replace")
        for child in sorted(path.glob("*.py"))
    )


def _gate_rows() -> dict[str, str]:
    section = _read(PROPOSAL).split("## Gate Verdict", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = cells[1].strip("`")
    return rows


def test_proposal_references_inputs_and_keeps_readiness_snapshot_blocked():
    text = _read(PROPOSAL)
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    for artifact in [
        "practitioner-directory-read-shape-design.md",
        "practitioner-directory-route-schema-ownership-candidate.md",
        "external-read-model-ownership-consolidation-preflight.md",
        "external-read-model-implementation-planning-review.md",
        "external-read-model-combined-readiness-review.md",
        "external-read-model-readiness-dag.json",
        "blocked_readiness_status.json",
        "Claude Sprint 227 worker review",
        "Antigravity Sprint 227 worker review",
        "DeepSeek Sprint 227 worker review",
    ]:
        assert artifact in text

    assert CANDIDATE.exists()
    assert CONSOLIDATION.exists()
    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False


def test_gate_verdict_requires_yuri_go_no_go_before_runtime_code():
    rows = _gate_rows()

    assert rows == {
        "first_candidate": "practice_practitioners",
        "implementation_proposal_ready_for_yuri_review": "true",
        "runtime_code_authorized": "false",
        "rest_route_ready": "false",
        "graphql_resolver_ready": "false",
        "external_read_model_runtime_ready": "false",
        "readiness_snapshot_decision": "blocked",
        "pause_required_before_route_code": "true",
        "explicit_yuri_go_no_go_required": "true",
    }
    assert (
        "Approval of this document itself is not approval to write runtime code"
        in _compact(_read(PROPOSAL))
    )


def test_route_contract_is_explicit_but_current_code_remains_absent():
    text = _read(PROPOSAL)
    router_text = _python_text_under(ROUTERS_DIR)
    schema_text = _python_text_under(SCHEMAS_DIR)

    for phrase in [
        "new `app/routers/practice.py`",
        "`/api/v1/practice`",
        "`GET /practitioners`",
        "`GET /api/v1/practice/practitioners`",
        "existing `get_current_user` pattern",
        "`Practitioner.practice_id == current_user.practice_id`",
        "bare `list[PractitionerOut]`",
        "`200` plus `[]`",
    ]:
        assert phrase in text

    for fragment in [
        '@router.get("/practice/practitioners"',
        '@router.get("/practitioners"',
        "def list_practitioners",
        "def get_practitioners",
    ]:
        assert fragment not in router_text
    for fragment in [
        "class PractitionerOut",
        "class PractitionerDirectory",
        "class PractitionerDefaultLocationOut",
    ]:
        assert fragment not in schema_text


def test_schema_contract_uses_minimal_directory_fields_and_safe_location_shape():
    text = _read(PROPOSAL)

    for phrase in [
        "`app/schemas/practice.py::PractitionerOut`",
        "`id`",
        "`displayName`",
        "`roleLabel`",
        "`active`",
        "`defaultLocation`",
        "`PractitionerDefaultLocationOut or null`",
        "only `id` and `name`",
        "must not reuse `app/schemas/appointments.py::PractitionerBrief`",
        "full diary/location schema",
    ]:
        assert phrase in text


def test_sensitive_field_exclusions_are_complete_and_test_required():
    text = _read(PROPOSAL)

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
        assert field in text
    assert "must assert forbidden response keys" in text


def test_query_policy_commits_pagination_ordering_inactive_gate_and_location_join():
    compact = _compact(_read(PROPOSAL))

    for phrase in [
        "`activeOnly` | `bool`, default `true`, alias preserved as camelCase",
        "`limit` | `int`, default `50`, `ge=1`, `le=200`",
        "`offset` | `int`, default `0`, `ge=0`",
        "`Practitioner.last_name` ascending",
        "`Practitioner.first_name` ascending",
        "`Practitioner.id` ascending",
        "`activeOnly=false` is admin-only",
        "`Admin` or `PracticeOwner` authority",
        "`PracticeLocation.id == Practitioner.default_location_id`",
        "`PracticeLocation.practice_id == current_user.practice_id`",
        "`PracticeLocation.is_active == true`",
        "`defaultLocation: null`",
    ]:
        assert phrase in compact


def test_required_runtime_test_blueprint_covers_boundary_and_side_effects():
    text = _read(PROPOSAL)

    for test_name in [
        "test_auth_denial_returns_401",
        "test_invalid_token_returns_401",
        "test_practice_scoping_never_returns_other_practice_practitioners",
        "test_active_only_default_excludes_inactive_practitioners",
        "test_active_only_false_requires_admin_or_practice_owner",
        "test_display_name_derivation_joins_non_empty_name_parts",
        "test_response_excludes_sensitive_practitioner_fields",
        "test_default_location_same_practice_active_only",
        "test_inactive_or_other_practice_default_location_returns_null",
        "test_deterministic_ordering_by_last_first_id",
        "test_limit_default_and_maximum",
        "test_invalid_limit_and_offset_return_422",
        "test_empty_practice_returns_200_empty_list",
        "test_get_route_does_not_write_database_state",
        "test_route_does_not_call_provider_access_ai_rag_or_graphrag",
    ]:
        assert test_name in text


def test_graphql_and_closed_gates_remain_blocked():
    text = _read(PROPOSAL)
    compact = _compact(text)

    for phrase in [
        "This proposal does not authorize GraphQL resolver implementation",
        "`Query.practice.practitioners` remains a future read-model resolver candidate",
        "GraphQL mutations remain prohibited",
        "adding a REST practitioner directory route",
        "adding GraphQL resolvers or GraphQL mutations",
        "adding Pydantic runtime schemas",
        "adding database queries, joins, indexes, migrations, or query services",
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


def test_boundary_says_this_is_not_runtime_or_production_readiness():
    compact = _compact(_read(PROPOSAL))

    for phrase in [
        "static implementation-proposal gate packet",
        "does not prove runtime REST authorization",
        "database query correctness",
        "GraphQL resolver implementation",
        "field-level authorization",
        "pagination performance",
        "deployment readiness",
        "provider readiness",
        "external directory readiness",
        "patient-facing client readiness",
        "production readiness",
    ]:
        assert phrase in compact
