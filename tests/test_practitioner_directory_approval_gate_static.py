import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT_JSON = (
    ROOT / "docs" / "api-spine" / "practitioner-directory-approval-payload-draft.json"
)
DECISION_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-approval-decision.md"
APPROVED_GATE = ROOT / "docs" / "api-spine" / "practitioner-directory-approved-gate.json"
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
APP = ROOT / "app"


ALLOWED_DECISIONS = {
    "blocked",
    "approved_for_rest_route_first_slice",
    "deferred",
    "rejected",
    "expired",
}

SPRINT_CHAIN_DOCS = [
    "practitioner-directory-read-shape-design.md",
    "practitioner-directory-route-schema-ownership-candidate.md",
    "practitioner-directory-first-runtime-implementation-proposal.md",
    "practitioner-directory-graphql-resolver-ownership-plan.md",
    "practitioner-directory-rest-graphql-drift-contract.md",
    "practitioner-directory-security-audit-test-harness-preflight.md",
    "practitioner-directory-sdl-pagination-default-location-resolution-proposal.md",
    "practitioner-directory-route-implementation-breakdown-readiness-decision.md",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _draft() -> dict:
    return json.loads(DRAFT_JSON.read_text(encoding="utf-8"))


def _app_python_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(APP.rglob("*.py"))
    )


def test_payload_draft_exists_and_is_blocked_by_default():
    payload = _draft()

    assert payload["gate"] == "practitioner_directory_rest_route_gate"
    assert payload["version"] == 1
    assert payload["decision"] == "blocked"
    assert payload["sprint_range"] == "227..232"
    assert payload["target_route"] == "GET /api/v1/practice/practitioners"
    assert payload["approval"] == {
        "reviewer": "",
        "go_no_go_acknowledged": False,
        "approval_expires_on": None,
        "approved_contract_commit": None,
    }
    assert payload["draft_review"]["not_approved_until"] == "explicit_yuri_decision"


def test_approved_gate_does_not_exist_before_yuri_decision():
    assert not APPROVED_GATE.exists()
    assert "There is deliberately no approved gate file yet" in _read(DECISION_MD)


def test_decision_field_is_enum_restricted_and_consequences_complete():
    payload = _draft()
    consequences = payload["decision_consequences"]

    assert set(consequences) == ALLOWED_DECISIONS
    assert payload["decision"] in ALLOWED_DECISIONS
    for decision in ALLOWED_DECISIONS:
        assert f"`{decision}`" in _read(DECISION_MD)


def test_blocked_decision_rejects_all_non_rest_scope_fields_as_false():
    payload = _draft()
    scope = payload["permitted_scope_if_approved"]

    assert payload["decision"] == "blocked"
    assert scope["rest_route_first_slice_only"] is True
    assert scope["schema_slice_allowed"] is True
    assert scope["shared_read_service_slice_allowed"] is True
    assert scope["rest_route_and_mount_slice_allowed"] is True
    assert scope["runtime_test_matrix_allowed"] is True
    for forbidden_scope in [
        "sdl_changes_allowed",
        "graphql_resolver_allowed",
        "graphql_runtime_dependency_allowed",
        "provider_or_memory_trove_allowed",
        "write_authority_allowed",
        "readiness_flag_changes_allowed",
        "deployment_or_production_readiness_allowed",
    ]:
        assert scope[forbidden_scope] is False


def test_evidence_checklist_maps_to_sprint_214_223_227_to_232_docs():
    payload = _draft()
    checklist = payload["evidence_checklist"]
    decision_text = _read(DECISION_MD)

    for filename in SPRINT_CHAIN_DOCS:
        assert (ROOT / "docs" / "api-spine" / filename).exists()
        assert filename in decision_text
    for required_key in [
        "read_shape_design_exists",
        "ownership_candidate_recorded",
        "implementation_proposal_defined",
        "graphql_sequencing_plan_defined",
        "rest_graphql_drift_contract_defined",
        "security_audit_preflight_defined",
        "sdl_resolution_proposal_defined",
        "route_breakdown_readiness_defined",
        "blocked_readiness_snapshot_intact",
        "no_route_schema_service_resolver_code_exists",
        "all_gates_still_blocked",
    ]:
        assert checklist[required_key] is True
    assert checklist["pre_code_checklist_passed"] is False
    assert checklist["yuri_explicit_go_no_go_recorded"] is False


def test_approval_expiry_and_contract_commit_are_blank_until_approval_but_draft_shape_is_valid():
    payload = _draft()
    approval = payload["approval"]

    assert approval["approval_expires_on"] is None
    assert approval["approved_contract_commit"] is None
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload["draft_review"]["proposed_approval_expires_on"])


def test_closed_gates_preserved_match_route_breakdown_boundary():
    payload = _draft()
    forbidden = "\n".join(payload["forbidden_changes"])
    decision = _compact(_read(DECISION_MD))

    for phrase in [
        "adding a REST practitioner directory route without approved_for_rest_route_first_slice",
        "adding app/routers/practice.py without approved_for_rest_route_first_slice",
        "adding app/schemas/practice.py without approved_for_rest_route_first_slice",
        "adding app/services/practice/ without approved_for_rest_route_first_slice",
        "adding GraphQL resolvers or GraphQL mutations",
        "adding a GraphQL runtime dependency or server",
        "changing the SDL",
        "adding PracticeLocationBrief to the SDL",
        "changing Practitioner.defaultLocation",
        "adding limit or offset arguments to Practice.practitioners",
        "changing the blocked readiness snapshot",
        "changing readiness flags to true",
        "provider calls or live provider gates",
        "runtime FGA clients",
        "external patient clients",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
        "Access AI invocation wiring",
        "practitioner create/update/delete/onboarding commands",
        "model-to-database writes outside REST command handlers",
        "raw compatibility deprecation mode changes",
    ]:
        assert phrase in forbidden
    for phrase in [
        "SDL changes",
        "GraphQL runtime dependencies",
        "readiness flag changes",
        "deployment or production-readiness claims",
        "provider calls or live-provider gates",
        "memory/RAG/GraphRAG runtime wiring",
        "raw compatibility deprecation mode changes",
    ]:
        assert phrase in decision


def test_readiness_snapshot_remains_blocked():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False
    assert snapshot["runtime_or_memory_ready"] is False
    assert snapshot["write_authority_ready"] is False


def test_current_source_has_no_route_schema_service_resolver_or_sdl_gate_change():
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
        "PracticeLocationBrief",
        "provider_or_memory_trove_allowed = True",
    ]:
        assert fragment not in app_text


def test_packet_does_not_authorize_runtime_code_by_itself():
    compact = _compact(_read(DECISION_MD))

    for phrase in [
        "It is not approval",
        "That file may exist only after Yuri explicitly instructs Ariadne",
        "No agent should make that approval patch without Yuri explicitly instructing it",
        "does not prove runtime REST authorization",
        "route correctness",
        "database query correctness",
        "GraphQL authorization",
        "resolver correctness",
        "deployment readiness",
        "production readiness",
        "Yuri approval",
    ]:
        assert phrase in compact
