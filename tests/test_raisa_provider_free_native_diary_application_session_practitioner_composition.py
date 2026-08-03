"""Deterministic acceptance for the default-off native-Diary application-session
practitioner composition static contract (Diary lane step 1, architecture-only)."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from app.services.application_auth_runtime import (
    PRACTITIONER_DIRECTORY_ACTION,
    PRACTITIONER_DIRECTORY_POLICY_VERSION,
    PRACTITIONER_DIRECTORY_RESOURCE_TYPE,
    Surface,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-composition"
    / "composition-contract.json"
)
SCHEMA = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-composition"
    / "composition-contract.schema.json"
)
PLAN = ROOT / "docs/raisa-provider-free-native-diary-application-session-practitioner-composition-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-native-diary-application-session-practitioner-composition-design.md"
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-native-diary-application-session-practitioner-composition-threat-model-delta.md"
)
DIARY_JS = ROOT / "docs/diary/diary.js"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_composition_contract_validates_against_draft_2020_12_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator(_json(SCHEMA)).validate(_json(CONTRACT))


def test_composition_contract_binds_exact_native_diary_surface() -> None:
    surface = _json(CONTRACT)["surface"]

    assert surface["bound_surface"] == Surface.NATIVE_DIARY.value
    assert surface["surface_enum"] == "Surface.NATIVE_DIARY"
    assert surface["surface_value"] == Surface.NATIVE_DIARY.value
    assert surface["long_lived_browser_surface"] is True


def test_composition_contract_binds_exact_accepted_policy_identifiers() -> None:
    bridge = _json(CONTRACT)["authorization_bridge"]

    assert bridge["shared_bridge"] == "application_session_product_read_bridge"
    assert bridge["policy_version"] == PRACTITIONER_DIRECTORY_POLICY_VERSION
    assert bridge["action"] == PRACTITIONER_DIRECTORY_ACTION
    assert bridge["resource_type"] == PRACTITIONER_DIRECTORY_RESOURCE_TYPE
    assert bridge["active_only_only"] is True
    assert bridge["inactive_enumeration_closed"] is True


def test_composition_contract_binds_exact_read_and_display_safe_projection() -> None:
    read = _json(CONTRACT)["read_binding"]

    assert read["graphql_query"] == "Query.practice.practitioners"
    assert read["variables"] == {"activeOnly": True, "limit": 200, "offset": 0}
    assert set(read["projection"]) == {"id", "displayName", "roleLabel", "active"}
    assert set(read["default_location_projection"]) == {"id", "name"}
    assert read["fresh_practice_scoped_read"] is True
    assert read["session_artifacts_are_not_ui_data"] is True
    assert read["authority_envelopes_are_not_ui_data"] is True
    assert read["raw_identifiers_are_not_ui_data"] is True


def test_composition_is_unmounted_and_default_off() -> None:
    preservation = _json(CONTRACT)["default_off_preservation"]

    assert preservation["feature_off_default"] is True
    assert preservation["unmounted"] is True
    assert preservation["existing_bearer_graphql_read_unmodified_when_off"] is True
    assert preservation["existing_rest_fallback_unmodified_when_off"] is True
    assert preservation["byte_for_byte_unchanged_when_off"] is True
    assert preservation["behaviorally_unchanged_when_off"] is True


def test_composition_has_no_forbidden_dependency_surfaces() -> None:
    forbidden = set(_json(CONTRACT)["forbidden_dependencies"])

    assert {
        "bernie_probabilistic_work_cell",
        "davida_practice_operations",
        "probabilistic_interpretation",
        "agent_proofreader_gate",
        "office_one_use_terminal_reload_logout_lifecycle",
        "microsoft_federation",
        "real_identity",
    } <= forbidden


def test_composition_failure_behaviour_is_fail_closed() -> None:
    behaviour = _json(CONTRACT)["failure_behaviour"]

    assert behaviour["mismatch"] == "fail_closed_no_data_release"
    assert behaviour["stale_superseded_response"].startswith("reject")
    assert "fresh_read_required" in behaviour["stale_superseded_response"]
    assert "never_ui_data" in behaviour["privacy"]
    assert behaviour["unauthorized_session"] == "generic_denial_no_data_release"
    assert behaviour["audit_unavailable"] == "no_directory_data_release"


def test_composition_api_spine_stays_scoped_read_only() -> None:
    spine = _json(CONTRACT)["api_spine"]

    assert spine["graphql_scoped_read_only"] is True
    assert spine["mutation"] is False
    assert spine["command_tunnel"] is False
    assert spine["new_rest_surface"] is False
    assert spine["event_actuator"] is False


def test_composition_closed_and_blocked_gates_are_preserved() -> None:
    payload = _json(CONTRACT)
    closed = set(payload["closed_gates"])
    blocked = set(payload["blocked_gates"])

    assert {
        "providers",
        "probabilistic_interpretation",
        "proofreader_gates",
        "writes",
        "real_identity",
        "microsoft_federation",
        "deployment",
        "production",
        "release",
    } <= closed
    assert "docs_branding" in closed
    assert {
        "live_provider_runtime",
        "memory_rag_graphrag_runtime",
        "real_identity",
        "patient_clinical_document_data",
        "model_to_database_writes",
        "graphql_mutations",
        "deployment",
        "protected_refs",
    } <= blocked


def test_composition_makes_no_runtime_or_usability_claim() -> None:
    handoff = _json(CONTRACT)["implementation_handoff"]

    assert handoff["diary_asset_edit"] is False
    assert handoff["app_runtime_edit"] is False
    assert handoff["app_main_mounting"] is False
    assert handoff["protected_integration"] is False
    assert handoff["runtime_or_usability_claim"] is False


def test_diary_js_off_path_bearer_read_and_rest_fallback_are_preserved() -> None:
    source = DIARY_JS.read_text(encoding="utf-8")

    assert "PRACTITIONER_DIRECTORY_GRAPHQL_QUERY" in source
    assert "ENABLE_GRAPHQL_PRACTITIONERS" in source
    assert "async function fetchPractitionerDirectoryGraphql()" in source
    assert "async function fetchPractitionerDirectoryRest()" in source
    assert "async function loadPractitionerDirectory()" in source
    assert 'activeOnly: true,\n        limit: 200,\n        offset: 0,' in source
    assert "/practice/practitioners?activeOnly=true&limit=200" in source
    assert 'headers["Authorization"] = `Bearer ${token}`' in source


def test_public_artifacts_state_architecture_only_and_branding_exclusion() -> None:
    assert PLAN.is_file() and DESIGN.is_file() and THREAT.is_file()
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower() for path in (PLAN, DESIGN, THREAT)
    )

    assert "default-off" in combined
    assert "native diary" in combined
    assert "docs/branding/" in combined
    assert "runtime or usability" in combined
    assert "no product or data boundary opens" in combined


def test_composition_contract_source_head_is_exact_hex() -> None:
    source_head = _json(CONTRACT)["source_head"]

    assert re.fullmatch(r"[0-9a-f]{40}", source_head) is not None


def _clone_contract() -> dict:
    return copy.deepcopy(_json(CONTRACT))


def _assert_mutation_invalid(mutator) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    payload = _clone_contract()
    mutator(payload)
    errors = list(
        jsonschema.Draft202012Validator(_json(SCHEMA)).iter_errors(payload)
    )
    assert errors, "mutated contract unexpectedly passed schema validation"


def test_schema_rejects_wrong_surface() -> None:
    def mutate(payload: dict) -> None:
        payload["surface"]["bound_surface"] = "word_online"
        payload["surface"]["surface_enum"] = "Surface.WORD_ONLINE"
        payload["surface"]["surface_value"] = "word_online"

    _assert_mutation_invalid(mutate)


def test_schema_rejects_changed_policy_action_resource() -> None:
    def mutate(payload: dict) -> None:
        bridge = payload["authorization_bridge"]
        bridge["policy_version"] = "practice-practitioner-directory-write.v2"
        bridge["action"] = "practice.practitioner-directory.write"
        bridge["resource_type"] = "patient_clinical_record"

    _assert_mutation_invalid(mutate)


def test_schema_rejects_inactive_enumeration() -> None:
    def mutate(payload: dict) -> None:
        bridge = payload["authorization_bridge"]
        bridge["active_only_only"] = False
        bridge["inactive_enumeration_closed"] = False

    _assert_mutation_invalid(mutate)


def test_schema_rejects_default_on() -> None:
    def mutate(payload: dict) -> None:
        payload["default_off_preservation"]["feature_off_default"] = False

    _assert_mutation_invalid(mutate)


def test_schema_rejects_mounted_composition() -> None:
    def mutate(payload: dict) -> None:
        payload["default_off_preservation"]["unmounted"] = False

    _assert_mutation_invalid(mutate)


def test_schema_rejects_rest_fallback_replacement() -> None:
    def mutate(payload: dict) -> None:
        payload["default_off_preservation"][
            "existing_rest_fallback_unmodified_when_off"
        ] = False

    _assert_mutation_invalid(mutate)


def test_schema_rejects_graphql_mutation() -> None:
    def mutate(payload: dict) -> None:
        payload["api_spine"]["mutation"] = True

    _assert_mutation_invalid(mutate)


def test_schema_rejects_command_tunnel() -> None:
    def mutate(payload: dict) -> None:
        payload["api_spine"]["command_tunnel"] = True

    _assert_mutation_invalid(mutate)


def test_schema_rejects_event_actuator() -> None:
    def mutate(payload: dict) -> None:
        payload["api_spine"]["event_actuator"] = True

    _assert_mutation_invalid(mutate)


def test_schema_rejects_missing_privacy_restriction() -> None:
    def mutate(payload: dict) -> None:
        payload["failure_behaviour"].pop("privacy")

    _assert_mutation_invalid(mutate)


def test_schema_rejects_unknown_nested_field() -> None:
    def mutate(payload: dict) -> None:
        payload["api_spine"]["unrestricted_write"] = True

    _assert_mutation_invalid(mutate)


def test_schema_rejects_missing_nested_field() -> None:
    def mutate(payload: dict) -> None:
        payload["read_binding"].pop("projection")

    _assert_mutation_invalid(mutate)


def test_schema_rejects_missing_contractual_array_item() -> None:
    def mutate(payload: dict) -> None:
        payload["blocked_gates"].pop()

    _assert_mutation_invalid(mutate)


def test_schema_rejects_reordered_contractual_array() -> None:
    def mutate(payload: dict) -> None:
        payload["closed_gates"].reverse()

    _assert_mutation_invalid(mutate)


def test_schema_rejects_unknown_contractual_array_item() -> None:
    def mutate(payload: dict) -> None:
        payload["closed_gates"][0] = "open_provider_gate"

    _assert_mutation_invalid(mutate)


def test_schema_rejects_duplicate_contractual_array_item() -> None:
    def mutate(payload: dict) -> None:
        payload["blocked_gates"][1] = payload["blocked_gates"][0]

    _assert_mutation_invalid(mutate)
