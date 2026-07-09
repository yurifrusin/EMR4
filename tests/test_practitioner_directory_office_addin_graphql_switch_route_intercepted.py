import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-switch-route-intercepted-evidence.json"
EVIDENCE_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-switch-route-intercepted-evidence.md"
REVIEW_TEST = ROOT / "review" / "test_diary_graphql_practitioner_switch.py"
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"


def _payload() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_route_intercepted_evidence_shape_is_specific_to_sprint_279():
    payload = _payload()

    assert payload["schema_version"] == "api_spine.practitioner_directory_office_addin_graphql_switch_route_intercepted_evidence.v1"
    assert payload["sprint"] == 279
    assert payload["target_surface"] == "docs/diary/diary.js"
    assert payload["target_consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert payload["evidence_type"] == "route_intercepted_browser_tests"
    assert payload["browser_evidence"]["test_file"] == "review/test_diary_graphql_practitioner_switch.py"


def test_review_tests_name_default_off_and_enabled_fallback_paths():
    payload = _payload()
    source = REVIEW_TEST.read_text(encoding="utf-8")

    for test_name in payload["browser_evidence"]["tests"]:
        assert f"def {test_name}" in source
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = true;" in source
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = false;" in source
    assert '"FORBIDDEN"' in source
    assert '"BAD_USER_INPUT"' in source
    assert "graphql_status=503" in source
    assert '"practice": None' in source
    assert '"defaultLocation": None' in source
    assert "activeOnly=true" in source
    assert "limit=200" in source


def test_runtime_file_remains_default_off_without_user_override():
    source = DIARY_JS.read_text(encoding="utf-8", errors="replace")
    lowered = source.lower()

    assert "const ENABLE_GRAPHQL_PRACTITIONERS = false;" in source
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = true;" not in source
    assert "emr4_flag_graphql_practitioners" not in lowered
    for line in lowered.splitlines():
        if "enable_graphql_practitioners" in line:
            assert "localstorage" not in line
            assert "urlsearchparams" not in line
            assert "office.context.document.settings" not in line


def test_evidence_records_intercepted_not_live_or_ready():
    payload = _payload()

    assert payload["browser_evidence"]["default_off_observed"]["graphql_requests"] == 0
    assert payload["browser_evidence"]["default_off_observed"]["rest_requests"] == 1
    assert payload["browser_evidence"]["enabled_fallback_observed"]["graphql_forbidden_then_rest_fallback"] is True
    assert payload["browser_evidence"]["enabled_fallback_observed"]["graphql_bad_user_input_then_rest_fallback"] is True
    assert payload["browser_evidence"]["enabled_fallback_observed"]["graphql_transport_then_rest_fallback"] is True
    assert payload["browser_evidence"]["enabled_fallback_observed"]["graphql_practice_null_without_rest_fallback"] is True
    assert payload["browser_evidence"]["enabled_fallback_observed"]["graphql_default_location_null_preserves_row_without_rest_fallback"] is True
    assert payload["browser_evidence"]["enabled_fallback_observed"]["feature_gate_flip_source"] == "test_harness_served_copy_only"
    assert all(value is False for value in payload["must_remain_false"].values())


def test_markdown_names_closed_gates_and_next_decision_point():
    text = " ".join(EVIDENCE_MD.read_text(encoding="utf-8").split())

    assert "route-intercepted" in text
    assert "not live backend evidence" in text
    assert "default-on" in text
    assert "requires a separate approval packet" in text
    assert "GraphQL mutations" in text
    assert "provider" in text
