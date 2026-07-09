import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-route-implementation-breakdown-readiness-decision.md"
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _gate_rows() -> dict[str, str]:
    section = _read(PACKET).split("## Gate Verdict", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = cells[1].strip("`")
    return rows


def _app_python_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(APP.rglob("*.py"))
    )


def test_route_breakdown_gate_verdict_keeps_runtime_blocked():
    assert _gate_rows() == {
        "route_breakdown_defined": "true",
        "future_rest_route_slice_defined": "true",
        "future_read_service_slice_defined": "true",
        "future_schema_slice_defined": "true",
        "future_runtime_test_matrix_defined": "true",
        "rest_route_ready": "false",
        "graphql_resolver_ready": "false",
        "external_read_model_runtime_ready": "false",
        "runtime_code_authorized": "false",
        "sdl_changes_authorized": "false",
        "readiness_snapshot_decision": "blocked",
        "pause_required_before_route_code": "true",
        "separate_pause_required_before_sdl_code": "true",
        "separate_pause_required_before_graphql_code": "true",
        "explicit_yuri_go_no_go_required": "true",
    }


def test_inputs_reviewed_cover_sprints_214_223_227_to_231():
    text = _read(PACKET)

    for phrase in [
        "practitioner-directory-read-shape-design.md",
        "practitioner-directory-route-schema-ownership-candidate.md",
        "practitioner-directory-first-runtime-implementation-proposal.md",
        "practitioner-directory-graphql-resolver-ownership-plan.md",
        "practitioner-directory-rest-graphql-drift-contract.md",
        "practitioner-directory-security-audit-test-harness-preflight.md",
        "practitioner-directory-sdl-pagination-default-location-resolution-proposal.md",
        "blocked_readiness_status.json",
        "Claude Sprint 232 review",
        "Antigravity Sprint 232 review",
        "DeepSeek Sprint 232 review",
    ]:
        assert phrase in text


def test_pre_code_readiness_checklist_now_preserves_bounded_rest_slice():
    text = _read(PACKET)
    compact = _compact(text)
    app_text = _app_python_text()

    for phrase in [
        "Yuri has explicitly approved",
        "`dag_decision: blocked`",
        "`rest_route_ready: false`",
        "`graphql_resolver_ready: false`",
        "`external_read_model_runtime_ready: false`",
        "no `approved` or `implemented` ownership rows",
        '@router.get("/practice/practitioners"',
        '@router.get("/practitioners"',
        "`class PractitionerOut`",
        "`class PractitionerDefaultLocationOut`",
        "`app/services/practice/practitioner_directory_read.py`",
        "`Query.practice.practitioners`",
        "known and blocked",
        "worker invocation modes",
        "DeepSeek lane count",
    ]:
        assert phrase in compact

    for fragment in [
        '@router.get("/practitioners"',
        "def get_practitioners",
        "class PractitionerOut",
        "class PractitionerDefaultLocationOut",
        "practitioner_directory_read",
    ]:
        assert fragment in app_text
    for fragment in [
        '@router.get("/practice/practitioners"',
        "def list_practitioners",
        "class PractitionerDirectory",
        "Query.practice.practitioners",
    ]:
        assert fragment not in app_text
    assert (APP / "services" / "practice" / "practitioner_directory_read.py").exists()


def test_future_schema_slice_is_minimal_and_sensitive_fields_excluded():
    text = _read(PACKET)

    for phrase in [
        "Implemented file: `app/schemas/practice.py`",
        "class PractitionerDefaultLocationOut",
        "class PractitionerOut",
        "displayName",
        "roleLabel",
        "defaultLocation",
        "do not reuse `app/schemas/appointments.py::PractitionerBrief`",
        "explicit fields only",
        "only as `{id, name}`",
    ]:
        assert phrase in text

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
        "location contact details",
        "raw model dumps",
    ]:
        assert field in text


def test_future_read_service_slice_captures_tenancy_pagination_location_and_no_side_effects():
    compact = _compact(_read(PACKET))

    for phrase in [
        "Implemented file: `app/services/practice/practitioner_directory_read.py`",
        "`Practitioner.practice_id == current_user.practice_id`",
        "`activeOnly=true` as the default filter",
        "`activeOnly=false` restricted to `Admin` or `PracticeOwner`",
        "`limit=50`, `ge=1`, `le=200`",
        "`offset=0`, `ge=0`",
        "`Practitioner.last_name`",
        "`Practitioner.first_name`",
        "`Practitioner.id`",
        "`PracticeLocation.id == Practitioner.default_location_id`",
        "`PracticeLocation.practice_id == current_user.practice_id`",
        "`PracticeLocation.is_active == true`",
        "`defaultLocation: null`",
        "no `db.add`",
        "no `db.commit`",
        "no `db.flush`",
        "no `db.delete`",
        "no provider call",
        "no Access AI invocation",
        "no RAG",
        "no GraphRAG",
        "no memory wiring",
        "no H15/H-series import",
        "no historical diary trove import",
    ]:
        assert phrase in compact


def test_rest_route_slice_is_explicit_and_current_code_matches_bounded_surface():
    text = _read(PACKET)
    app_text = _app_python_text()

    for phrase in [
        "Implemented file: `app/routers/practice.py`",
        "router prefix: `/api/v1/practice`",
        "route: `GET /practitioners`",
        "full path: `GET /api/v1/practice/practitioners`",
        "existing `get_current_user`",
        "`activeOnly: bool = true`",
        "`limit: int = 50`",
        "`offset: int = 0`",
        "bare `list[PractitionerOut]`",
        "`200 []`",
        "no `GET /api/v1/practice/practitioners/{id}`",
    ]:
        assert phrase in text

    for fragment in [
        "PractitionerOut",
        "PractitionerDefaultLocationOut",
        "practitioner_directory_read",
        "get_practitioners",
    ]:
        assert fragment in app_text
    for fragment in [
        '@router.get("/practice/practitioners"',
        "list_practitioners",
        "class PractitionerDirectory",
        "Query.practice.practitioners",
    ]:
        assert fragment not in app_text


def test_future_runtime_test_matrix_unifies_sprint_227_and_230_requirements():
    text = _read(PACKET)

    for test_name in [
        "test_auth_denial_returns_401",
        "test_invalid_token_returns_401",
        "test_inactive_user_denied",
        "test_all_authenticated_roles_can_read_active_directory",
        "test_active_only_default_excludes_inactive_practitioners",
        "test_active_only_false_requires_admin_or_practice_owner",
        "test_unknown_or_unmapped_role_fails_closed",
        "test_practice_scoping_never_returns_other_practice_practitioners",
        "test_no_practitioner_detail_route_or_idor_surface",
        "test_no_cross_practice_existence_leak",
        "test_display_name_derivation_joins_non_empty_name_parts",
        "test_response_excludes_sensitive_practitioner_fields",
        "test_default_location_same_practice_active_only",
        "test_inactive_or_other_practice_default_location_returns_null",
        "test_deterministic_ordering_by_last_first_id",
        "test_limit_default_and_maximum",
        "test_invalid_limit_and_offset_return_422",
        "test_empty_practice_returns_200_empty_list",
        "test_read_does_not_create_appointment_audit_log",
        "test_read_does_not_require_idempotency_key",
        "test_get_route_does_not_write_database_state",
        "test_route_does_not_call_provider_access_ai_rag_or_graphrag",
        "test_route_does_not_import_h15_h_series_or_historical_diary_material",
        "test_route_does_not_change_readiness_snapshot",
    ]:
        assert test_name in text


def test_deferred_sdl_and_graphql_gates_remain_separate():
    text = _read(PACKET)
    sdl = _read(SDL)

    for phrase in [
        "Separate SDL Gate",
        "add `PracticeLocationBrief { id, name }`",
        "change `Practitioner.defaultLocation` to `PracticeLocationBrief`",
        "add `activeOnly`, `limit=50`, and `offset=0`",
        "reject `PractitionerListResult` and `PractitionerConnection`",
        "separate pause and explicit approval",
        "Separate GraphQL Runtime Gate",
        "REST route",
        "shared read service",
        "SDL alignment",
        "GraphQL resolver",
        "must not query the database independently",
        "thin facade over the shared read service",
    ]:
        assert phrase in text

    assert "type PracticeLocationBrief" in sdl
    assert "defaultLocation: PracticeLocationBrief" in sdl
    assert "PractitionerListResult" not in sdl
    assert "PractitionerConnection" not in sdl
    assert (
        "practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0): "
        "[Practitioner!]!"
    ) in sdl


def test_stop_go_points_and_consumer_notes_are_documented():
    compact = _compact(_read(PACKET))

    for phrase in [
        "Pre-code | explicit Yuri go/no-go for REST route",
        "Pre-code | readiness snapshot remains blocked/false",
        "Pre-code | no existing route/schema/service/resolver",
        "Pre-code | Sprint 229 drift items still blocked",
        "Implementation | schema exposes only five canonical fields",
        "Implementation | inactive inclusion restricted to `Admin`/`PracticeOwner`",
        "Pre-merge | no SDL, GraphQL runtime, resolver, readiness, provider, or memory changes",
        "`GET /api/v1/practice/practitioners?activeOnly=true&limit=50&offset=0`",
        "render `displayName` directly",
        "neutral fallback when `defaultLocation` is `null`",
        "`403` on `activeOnly=false`",
        "do not use this route as a roster, appointment, billing, clinical, provider",
    ]:
        assert phrase in compact


def test_readiness_snapshot_remains_blocked():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False
    assert snapshot["runtime_or_memory_ready"] is False
    assert snapshot["write_authority_ready"] is False


def test_boundary_says_packet_is_not_runtime_or_production_readiness():
    compact = _compact(_read(PACKET))

    for phrase in [
        "static route implementation breakdown and readiness decision packet",
        "does not prove runtime REST authorization",
        "route correctness",
        "database query correctness",
        "field-level authorization",
        "audit implementation",
        "SDL correctness after edit",
        "GraphQL authorization",
        "resolver correctness",
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
