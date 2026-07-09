import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-fetch-wrapper-test-plan.json"
PLAN_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-fetch-wrapper-test-plan.md"
TASKPANE_JS = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "taskpane.js"


def _payload() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8"))


def test_fetch_wrapper_test_plan_is_blocked_by_default():
    payload = _payload()

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_fetch_wrapper_test_plan.v1"
    )
    assert payload["sprint"] == 275
    assert payload["decision"] == "blocked_by_default_test_plan_only"
    assert payload["approval_expires_on"] == "2026-08-06"
    assert payload["scope"] == {
        "docs_and_tests_only": True,
        "mocked_fetch_wrapper_plan": True,
        "runtime_taskpane_wrapper_implementation": False,
        "taskpane_code_change": False,
        "hidden_feature_flag": False,
        "runtime_shadow_fetch": False,
        "client_telemetry_endpoint": False,
        "backend_route_or_schema_change": False,
        "readiness_flag_change": False,
    }


def test_fetch_wrapper_test_plan_names_required_mock_cases():
    cases = _payload()["required_mock_cases"]

    assert cases == [
        "graphql_success_exact_projection",
        "graphql_empty_practitioners_list",
        "http_401_transport_calls_logout",
        "graphql_forbidden_extensions_code_no_logout",
        "graphql_bad_user_input_extensions_code_no_logout",
        "practice_null_returns_empty_without_leak",
        "default_location_null_keeps_row",
        "projection_drift_extra_field_rejected",
        "expired_or_disabled_gate_skips_graphql_fetch",
        "future_rest_fallback_on_graphql_failure",
    ]


def test_fetch_wrapper_test_plan_keeps_projection_and_copy_safe():
    payload = _payload()

    assert payload["approved_projection"] == [
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation.id",
        "defaultLocation.name",
    ]
    assert payload["safe_user_copy"] == {
        "http_401": "Please sign in again.",
        "graphql_forbidden": "You do not have permission to access the practitioner directory.",
        "graphql_bad_user_input": "Invalid request. Please check the practitioner directory filters.",
        "network_or_system": "Unable to load practitioner directory. Please try again later.",
    }
    for forbidden in payload["copy_must_not_include"]:
        assert forbidden not in " ".join(payload["safe_user_copy"].values())


def test_fetch_wrapper_test_plan_forbids_runtime_write_set():
    payload = _payload()

    assert "EMR4 Sidebar/src/taskpane/taskpane.js" in payload["forbidden_write_set"]
    assert "app/" in payload["forbidden_write_set"]
    assert "local_data/" in payload["forbidden_write_set"]
    assert "tests/fixtures/h15_semantic_candidates/" in payload["forbidden_write_set"]
    assert all(value is False for value in payload["must_remain_false"].values())


def test_fetch_wrapper_test_plan_records_distinct_worker_lanes():
    reviews = _payload()["worker_reviews"]

    assert reviews["antigravity_consumer_ux_tests"]["verdict"] == "PASS"
    assert reviews["deepseek_static_gate_tests"]["verdict"] == "PASS"
    assert reviews["claude"] == {
        "used": False,
        "reason": "No API contract, resolver, or runtime auth/error model changed; Claude remains stood down.",
    }


def test_fetch_wrapper_test_plan_markdown_says_no_runtime_switch():
    text = " ".join(PLAN_MD.read_text(encoding="utf-8").split())

    assert "blocked-by-default tests" in text
    assert "does not edit `taskpane.js`" in text
    assert "2026-08-06" in text
    assert "HTTP `401` transport failure" in text
    assert "GraphQL `FORBIDDEN`" in text
    assert "`data.practice = null`" in text
    assert "separate consumer switch approval" in text


def test_sprint_275_does_not_change_taskpane_graphql_runtime():
    source = TASKPANE_JS.read_text(encoding="utf-8", errors="replace").lower()

    assert "/api/v1/graphql" not in source
    assert "query getpractitioners" not in source
    assert "practitioners(activeonly" not in source
    assert "emr4_flag_graphql_practitioners" not in source
    assert "shadow fetch" not in source
