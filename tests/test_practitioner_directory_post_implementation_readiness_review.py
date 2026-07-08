import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_JSON = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-post-implementation-readiness-review.json"
)
REVIEW_MD = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-post-implementation-readiness-review.md"
)
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)


def _review() -> dict:
    return json.loads(REVIEW_JSON.read_text(encoding="utf-8"))


def _compact(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_review_records_implemented_rest_slice_without_readiness_approval():
    review = _review()

    assert review["decision"] == "implemented_rest_slice_reviewed_readiness_blocked"
    assert review["reviewer"] == "ariadne"
    assert review["implementation_commit"] == "5b3b9102"
    assert review["approved_contract_commit"] == "ce23212d538fbba24e5061def2142b817d5528ad"
    assert review["implemented_surface"] == {
        "route": "GET /api/v1/practice/practitioners",
        "router": "app/routers/practice.py",
        "schema": "app/schemas/practice.py",
        "read_service": "app/services/practice/practitioner_directory_read.py",
        "runtime_tests": "tests/test_practitioner_directory_route.py",
    }
    assert review["readiness"]["rest_route_implemented"] is True
    assert review["readiness"]["rest_route_runtime_tests_passed"] is True
    for key in [
        "rest_route_ready",
        "graphql_resolver_ready",
        "external_read_model_runtime_ready",
        "runtime_or_memory_ready",
        "provider_or_directory_runtime_ready",
        "write_authority_ready",
        "deployment_ready",
        "production_ready",
    ]:
        assert review["readiness"][key] is False


def test_review_runtime_evidence_is_complete_and_read_only():
    evidence = _review()["runtime_evidence"]

    required_true = {
        "authn_checked",
        "inactive_user_denied",
        "practice_scoping_checked",
        "inactive_scope_admin_owner_only",
        "sensitive_fields_excluded",
        "default_location_scoped",
        "deterministic_ordering_checked",
        "pagination_bounds_checked",
        "no_practitioner_detail_route",
        "no_database_writes_checked",
        "no_appointment_audit_write_checked",
        "no_idempotency_key_required_for_read",
        "no_provider_or_access_ai_imports",
        "no_memory_or_rag_or_graphrag_imports",
        "no_h15_h_series_or_historical_diary_imports",
    }
    assert set(evidence) == required_true
    assert all(evidence.values())


def test_review_keeps_blocked_readiness_snapshot_unchanged():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert snapshot["approval_gate_decision"] == "approved_for_rest_route_first_slice"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False
    assert snapshot["runtime_or_memory_ready"] is False
    assert snapshot["write_authority_ready"] is False


def test_review_boundary_names_all_forbidden_scope_expansions():
    review = _review()
    blocked = "\n".join(review["blocked_until_separate_review"])
    compact = _compact(REVIEW_MD)

    for phrase in [
        "changing tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json rest_route_ready to true",
        "adding SDL or GraphQL resolver coverage for Query.practice.practitioners",
        "adding provider, Access AI, memory, RAG, or GraphRAG wiring",
        "adding H15, H-series, historical diary, or local_data runtime imports",
        "adding write authority, audit writes, or appointment mutation behavior",
        "claiming deployment, production, external patient-client, rate-limit, RLS, or field-encryption readiness",
    ]:
        assert phrase in blocked

    for phrase in [
        "post-implementation review, not a deployment or production readiness approval",
        "Programme 2G / EMR4 API Spine",
        "It is not.",
        "not an automatic scope expansion",
    ]:
        assert phrase in compact


def test_review_only_names_readiness_claims_as_blocked_or_not_approved():
    text = (json.dumps(_review(), sort_keys=True) + "\n" + _compact(REVIEW_MD)).lower()

    for phrase in [
        "does not mark the route deployed",
        "not a deployment or production readiness approval",
        "changing `rest_route_ready` to `true`",
        "not an automatic scope expansion",
    ]:
        assert phrase in text
    assert '"deployment_ready": false' in text
    assert '"production_ready": false' in text
    assert '"graphql_resolver_ready": false' in text
    assert '"write_authority_ready": false' in text
