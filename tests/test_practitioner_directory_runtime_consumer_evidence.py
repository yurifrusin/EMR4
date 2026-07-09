import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "api-spine" / "practitioner-directory-runtime-consumer-evidence.json"
EVIDENCE_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-runtime-consumer-evidence.md"
SMOKE = ROOT / "review" / "test_diary_smoke.py"
ROUTE_TESTS = ROOT / "tests" / "test_practitioner_directory_route.py"


def _payload() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_runtime_consumer_evidence_shape_is_specific():
    payload = _payload()

    assert payload["schema_version"] == "api_spine.practitioner_directory_runtime_consumer_evidence.v1"
    assert payload["sprint"] == 265
    assert payload["target_route"] == "GET /api/v1/practice/practitioners"
    assert payload["approved_consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert payload["evidence_type"] == "route_intercepted_browser_and_backend_runtime_tests"


def test_browser_evidence_names_executable_route_intercept_checks():
    payload = _payload()
    smoke = SMOKE.read_text(encoding="utf-8")
    browser = payload["browser_evidence"]

    assert browser["test_file"] == "review/test_diary_smoke.py"
    for test_name in browser["tests"]:
        assert f"def {test_name}" in smoke
    assert browser["observed_request"] == {
        "method": "GET",
        "path": "/api/v1/practice/practitioners",
        "query": {"activeOnly": "true", "limit": "200"},
        "authorization_header_present": True,
    }
    assert browser["observed_selector_behavior"]["route_uuid_option_used_when_selection_preserved"] is True
    assert browser["observed_selector_behavior"]["legacy_ahpra_fallback_kept_when_route_uuid_unmapped"] is True
    assert browser["observed_selector_behavior"]["write_methods_observed"] == []


def test_backend_evidence_names_existing_route_contract_tests():
    payload = _payload()
    assert payload["backend_evidence"]["test_file"] == "tests/test_practitioner_directory_route.py"
    assert ROUTE_TESTS.exists()
    coverage = " ".join(payload["backend_evidence"]["coverage"])
    for required in ("auth", "practice scoping", "sensitive keys", "limit upper bound"):
        assert required in coverage


def test_evidence_keeps_adjacent_gates_false_but_recommends_graphql_next():
    payload = _payload()

    assert all(value is False for value in payload["must_remain_false"].values())
    decision = payload["graphql_follow_on_decision"]
    assert decision["rest_consumer_evidence_passed"] is True
    assert decision["graphql_work_recommended_next"] is True
    assert decision["allowed_next_scope"] == "practitioner_directory_graphql_sdl_resolver_alignment"
    assert payload["must_remain_false"]["graphql_resolver_ready"] is False


def test_markdown_records_no_deployment_or_graphql_readiness_claim():
    text = " ".join(EVIDENCE_MD.read_text(encoding="utf-8").split())

    assert "does not claim deployment" in text
    assert "GraphQL resolver readiness" in text
    assert "limit=200" in text
    assert "GraphQL SDL/resolver alignment" in text
