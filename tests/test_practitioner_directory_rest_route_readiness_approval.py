import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPROVAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-rest-route-readiness-approval.json"
)
APPROVAL_MD = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-rest-route-readiness-approval.md"
)
CRITERIA = ROOT / "docs" / "api-spine" / "practitioner-directory-readiness-criteria.json"
SPRINT258 = (
    ROOT / "docs" / "api-spine" / "practitioner-directory-sprint258-blocker-closure.json"
)
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)


def _approval() -> dict:
    return json.loads(APPROVAL.read_text(encoding="utf-8"))


def test_rest_route_readiness_approval_payload_matches_required_shape():
    payload = _approval()
    criteria = json.loads(CRITERIA.read_text(encoding="utf-8"))

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_rest_route_readiness_approval.v1"
    )
    assert payload["gate"] == "practitioner_directory_rest_route_readiness"
    assert payload["decision"] == criteria["approval_packet_shape"]["decision"]
    assert payload["reviewer"] == "yuri"
    assert payload["target_readiness_flag"] == "rest_route_ready"
    assert payload["target_route"] == "GET /api/v1/practice/practitioners"
    assert payload["approved_value"] is True
    assert len(payload["approved_contract_commit"]) == 40
    assert all(char in "0123456789abcdef" for char in payload["approved_contract_commit"])
    assert payload["approval_expires_on"] == "2026-08-08"
    assert payload["approval"] == {
        "reviewer": "yuri",
        "go_no_go_acknowledged": True,
        "approval_expires_on": "2026-08-08",
        "approved_contract_commit": payload["approved_contract_commit"],
    }
    assert payload["approval_source"]["kind"] == "explicit_yuri_chat_authorization"


def test_rest_route_readiness_approval_satisfies_all_sprint255_criteria():
    payload = _approval()
    criteria = json.loads(CRITERIA.read_text(encoding="utf-8"))

    required = set(criteria["required_before_true"])
    assert set(payload["criteria_evidence"]) == required
    assert all(value["status"].startswith("satisfied") for value in payload["criteria_evidence"].values())
    assert payload["criteria_evidence"]["separate_yuri_approval_payload_exists"] == {
        "status": "satisfied_by_this_payload",
        "artifact": "docs/api-spine/practitioner-directory-rest-route-readiness-approval.json",
    }


def test_rest_route_readiness_approval_inherits_closed_sprint258_blockers():
    payload = _approval()
    sprint258 = json.loads(SPRINT258.read_text(encoding="utf-8"))

    assert sprint258["decision"] == "readiness_blockers_closed_except_separate_yuri_approval"
    assert sprint258["criteria_status_after_sprint258"][
        "separate_yuri_approval_payload_exists"
    ] == "missing_requires_explicit_yuri_approval"
    assert payload["criteria_evidence"]["rate_limit_or_deferred_rate_limit_decision_recorded"][
        "status"
    ] == "satisfied_deferred_internal_route"
    assert payload["criteria_evidence"]["rls_or_rls_equivalent_gap_recorded"][
        "status"
    ] == "satisfied_gap_recorded_not_equivalent_to_rls"
    assert payload["criteria_evidence"]["external_client_exposure_decision_recorded"][
        "status"
    ] == "satisfied_internal_staff_only"


def test_rest_route_readiness_approval_keeps_adjacent_gates_false():
    payload = _approval()
    criteria = json.loads(CRITERIA.read_text(encoding="utf-8"))

    assert payload["approved_scope"] == {
        "rest_route_ready": True,
        "route": "GET /api/v1/practice/practitioners",
        "rest_route_ready_route_scoped_only": True,
        "client_scope": "authenticated_internal_staff_only",
        "read_only": True,
        "practice_scoped": True,
        "paginated": True,
        "sensitive_practitioner_identifiers_excluded_from_response": True,
    }
    assert payload["non_rest_scope_fields"] == criteria["must_remain_false_when_rest_route_ready_true"]
    assert payload["must_remain_false"] == criteria["must_remain_false_when_rest_route_ready_true"]
    assert all(value is False for value in payload["must_remain_false"].values())
    forbidden_text = " ".join(payload["not_authorized"]).lower()
    for fragment in (
        "graphql",
        "provider",
        "memory",
        "historical diary",
        "write authority",
        "external patient-client",
        "deployment",
        "production",
    ):
        assert fragment in forbidden_text


def test_rest_route_readiness_approval_does_not_silently_flip_global_snapshot():
    payload = _approval()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert payload["readiness_fixture_change"]["performed_in_this_payload"] is False
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False
    assert snapshot["write_authority_ready"] is False


def test_rest_route_readiness_approval_markdown_names_scope_and_limits():
    text = " ".join(APPROVAL_MD.read_text(encoding="utf-8").split())

    assert "approved_for_practitioner_directory_rest_route_ready_true" in text
    assert "GET /api/v1/practice/practitioners" in text
    assert "authenticated internal-staff read route" in text
    assert "does not authorize" in text
    assert "GraphQL SDL or resolver readiness" in text
    assert "not equivalent to database-level RLS" in text
    assert "does not itself update the external read-model readiness snapshot" in text
