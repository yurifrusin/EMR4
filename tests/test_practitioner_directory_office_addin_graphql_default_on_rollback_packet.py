import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-office-addin-graphql-default-on-rollback-packet.json"
)
PACKET_MD = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-office-addin-graphql-default-on-rollback-packet.md"
)
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
LOCAL_SMOKE = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-office-addin-graphql-default-on-local-backend-smoke.json"
)


def _packet() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_rollback_packet_records_no_runtime_rollback_now():
    payload = _packet()
    diary = DIARY_JS.read_text(encoding="utf-8", errors="replace")

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_default_on_rollback_packet.v1"
    )
    assert payload["sprint"] == 284
    assert payload["decision"] == "rollback_path_prepared_no_runtime_rollback_now"
    assert payload["target_consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert payload["current_runtime_state"]["feature_gate_default"] is True
    assert payload["current_runtime_state"]["rollback_applied_now"] is False
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = true;" in diary


def test_rollback_packet_single_line_action_keeps_backend_and_fallback_intact():
    payload = _packet()
    action = payload["rollback_action_if_needed"]

    assert action == {
        "change_scope": "single_line_office_addin_feature_gate_only",
        "from": "const ENABLE_GRAPHQL_PRACTITIONERS = true;",
        "to": "const ENABLE_GRAPHQL_PRACTITIONERS = false;",
        "file": "docs/diary/diary.js",
        "retain_graphql_query_code": True,
        "retain_rest_fallback_code": True,
        "retain_backend_graphql_route_and_resolver": True,
        "requires_yuri_pause_if_not_emergency": True,
    }


def test_rollback_packet_has_actionable_triggers_and_validation_commands():
    payload = _packet()
    triggers = " ".join(payload["rollback_triggers"]).lower()
    commands = payload["post_rollback_validation"]["required_commands"]
    expected = payload["post_rollback_validation"]["expected_after_rollback"]

    for fragment in (
        "selector",
        "401",
        "sensitive-field",
        "fallback",
        "practice-scoping",
        "inactive-practitioner",
        "performance",
    ):
        assert fragment in triggers
    assert commands == [
        ".venv\\Scripts\\python.exe -m pytest tests\\test_practitioner_directory_office_addin_graphql_default_on_rollback_packet.py -q",
        "node --check docs\\diary\\diary.js",
        "git diff --check",
    ]
    assert "pre-rollback baseline tests" in payload["post_rollback_validation"]["operator_check"]
    assert "node --check docs\\diary\\diary.js" in commands
    assert expected == {
        "default_off_rest_first": True,
        "graphql_query_code_present_for_future_reenable": True,
        "backend_graphql_resolver_unchanged": True,
        "rest_fallback_path_available": True,
    }


def test_rollback_packet_forbids_destructive_or_readiness_expanding_rollback():
    payload = _packet()

    assert all(value is False for value in payload["must_not_do_during_rollback"].values())
    assert all(value is False for value in payload["must_remain_false"].values())
    assert payload["current_runtime_state"]["server_config_endpoint"] is False
    assert payload["current_runtime_state"]["runtime_user_override"] is False


def test_rollback_packet_depends_on_passing_local_smoke_and_markdown_boundary():
    payload = _packet()
    smoke = json.loads(LOCAL_SMOKE.read_text(encoding="utf-8"))
    text = " ".join(PACKET_MD.read_text(encoding="utf-8").split())

    assert payload["source_local_backend_smoke"].endswith(
        "practitioner-directory-office-addin-graphql-default-on-local-backend-smoke.json"
    )
    assert smoke["sprint"] == 283
    assert smoke["local_backend_smoke"]["uses_route_interception"] is False
    assert "It does not roll the feature back now" in text
    assert "must not delete the GraphQL query" in text
    assert "default-on baseline suites" in text
    assert "global GraphQL readiness" in text
    assert "field expansion" in text


def test_rollback_single_line_change_would_make_loader_rest_first():
    source = DIARY_JS.read_text(encoding="utf-8", errors="replace")
    rolled_back = source.replace(
        "const ENABLE_GRAPHQL_PRACTITIONERS = true;",
        "const ENABLE_GRAPHQL_PRACTITIONERS = false;",
    )

    assert rolled_back.count("const ENABLE_GRAPHQL_PRACTITIONERS = false;") == 1
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = true;" not in rolled_back
    loader_block = rolled_back.split("async function loadPractitionerDirectory()", 1)[1].split(
        "function normalizeApiPath", 1
    )[0]
    assert "if (!ENABLE_GRAPHQL_PRACTITIONERS) {" in loader_block
    assert "return fetchPractitionerDirectoryRest();" in loader_block
    assert "const graphqlResult = await fetchPractitionerDirectoryGraphql();" in loader_block
