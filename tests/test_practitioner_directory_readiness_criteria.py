import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRITERIA = ROOT / "docs" / "api-spine" / "practitioner-directory-readiness-criteria.json"
CRITERIA_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-readiness-criteria.md"
SNAPSHOT = ROOT / "tests" / "fixtures" / "api_spine_external_readiness" / "blocked_readiness_status.json"


def _criteria() -> dict:
    return json.loads(CRITERIA.read_text(encoding="utf-8"))


def test_readiness_criteria_defines_target_without_approval():
    payload = _criteria()

    assert payload["schema_version"] == "api_spine.practitioner_directory_readiness_criteria.v1"
    assert payload["decision"] == "criteria_defined_readiness_not_approved"
    assert payload["target_readiness_flag"] == "rest_route_ready"
    assert payload["target_route"] == "GET /api/v1/practice/practitioners"
    assert payload["current_value"] is False
    assert payload["approved_value_after_this_packet"] is False


def test_readiness_criteria_requires_separate_yuri_approval_payload():
    required = _criteria()["required_before_true"]

    assert set(required) == {
        "runtime_test_matrix_passes_in_isolated_run",
        "api_spine_artifact_tests_pass",
        "openapi_contract_snapshot_matches_runtime_route",
        "authn_authz_tenancy_review_current",
        "anti_enumeration_review_current",
        "sensitive_field_exclusion_review_current",
        "pagination_and_error_contract_review_current",
        "rate_limit_or_deferred_rate_limit_decision_recorded",
        "deployment_surface_explicitly_named",
        "rls_or_rls_equivalent_gap_recorded",
        "field_encryption_gap_recorded",
        "external_client_exposure_decision_recorded",
        "separate_yuri_approval_payload_exists",
    }
    assert all(required.values())


def test_readiness_criteria_keeps_adjacent_gates_false():
    payload = _criteria()

    assert all(value is False for value in payload["must_remain_false_when_rest_route_ready_true"].values())
    assert all(value is False for value in payload["blocked_scope"].values())
    assert payload["approval_packet_shape"] == {
        "decision": "approved_for_practitioner_directory_rest_route_ready_true",
        "reviewer_required": True,
        "approved_contract_commit_required": True,
        "approval_expires_on_required": True,
        "non_rest_scope_fields_must_be_false": True,
    }


def test_readiness_criteria_matches_current_blocked_snapshot():
    payload = _criteria()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert snapshot[payload["target_readiness_flag"]] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["runtime_or_memory_ready"] is False
    assert snapshot["write_authority_ready"] is False


def test_readiness_criteria_markdown_says_not_approved():
    text = " ".join(CRITERIA_MD.read_text(encoding="utf-8").split())

    assert "Decision: `criteria_defined_readiness_not_approved`" in text
    assert "It does not approve that change" in text
    assert "`rest_route_ready=false`" in text
    assert "A separate Yuri approval payload exists" in text
    assert "must not imply GraphQL readiness" in text
