from __future__ import annotations

import ast
import json
from pathlib import Path

import jsonschema

from scripts import ariadne_vertex_sydney_admission as admission


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_policy_schema_and_semantics_fail_closed() -> None:
    policy = load(admission.POLICY_PATH)
    schema = load(admission.POLICY_SCHEMA_PATH)
    sources = load(admission.SOURCE_OBSERVATION_PATH)

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(policy, schema)
    assert admission.validate_admission(policy, schema, sources) == []
    assert policy["status"] == "blocked"
    assert policy["decision"] == {
        "admitted": False,
        "result": "ariadne_vertex_sydney_provider_admission_blocked",
        "blocking_reasons": [
            "gemini_3_5_flash_not_published_for_australia_southeast1"
        ],
        "next_action": (
            "stop_for_yuri_without_adc_inspection_provider_call_model_substitution_"
            "or_external_cloud_change"
        ),
    }


def test_model_card_and_residency_matrix_both_block_sydney() -> None:
    sources = load(admission.SOURCE_OBSERVATION_PATH)
    by_id = {item["id"]: item for item in sources["sources"]}

    card = by_id["gemini_3_5_flash_model_card"]["observations"]
    matrix = by_id["model_data_residency_matrix"]["observations"]
    endpoint = by_id["service_endpoints"]["observations"]

    assert card["model_id"] == "gemini-3.5-flash"
    assert card["australia_southeast1_listed"] is False
    assert "australia-southeast1" not in card["model_availability_locations"]
    assert matrix["australia_southeast1_supported"] is False
    assert matrix["gemini_3_5_flash_australia_cell"] == "unsupported"
    assert endpoint["regional_service_endpoint_exists"] is True
    assert endpoint["endpoint_existence_does_not_prove_model_support"] is True


def test_policy_distinguishes_data_geography_and_evidence_classes() -> None:
    policy = load(admission.POLICY_PATH)

    assert policy["data_classes"]["authored_synthetic"]["admitted"] is True
    assert policy["data_classes"]["product_derived"]["admitted"] is False
    assert (
        policy["data_classes"]["patient_or_health_information"]["admitted"] is False
    )
    assert policy["geography"]["container_effect"] == (
        "constrains_local_capabilities_but_does_not_determine_remote_provider_"
        "processing_geography"
    )
    assert policy["geography"]["regional_storage"] != (
        policy["geography"]["australian_regional_processing"]
    )
    assert policy["claim_boundary"]["independently_observed_evidence"]
    assert policy["claim_boundary"]["provider_contractual_residency_evidence"]
    assert "in_memory_cache_disabled" in policy["required_admission_checks"]
    assert (
        policy["provider_controls"]["in_memory_cache"]["provider_contract"]
        .startswith("Google states")
    )
    assert (
        "stop for Yuri"
        in policy["provider_controls"]["in_memory_cache"]["local_requirement"]
    )


def test_default_in_memory_cache_is_separate_and_fails_closed() -> None:
    observation = load(admission.SOURCE_OBSERVATION_PATH)
    retention = next(
        source
        for source in observation["sources"]
        if source["id"] == "zero_data_retention"
    )["observations"]
    assert retention["published_gemini_in_memory_cache_default"] == "enabled"
    assert retention["published_gemini_in_memory_cache_scope"] == (
        "project_isolated_not_at_rest"
    )
    assert retention["published_gemini_in_memory_cache_ttl_hours"] == 24
    assert retention[
        "published_gemini_in_memory_cache_can_be_disabled_at_project_level"
    ] is True
    assert retention["project_cache_setting_inspected"] is False


def test_every_prohibited_route_is_explicit() -> None:
    rejected = set(load(admission.POLICY_PATH)["rejected_routes"])
    assert {
        "generativelanguage.googleapis.com",
        "gemini_developer_api",
        "aiplatform.googleapis.com_global",
        "automatic_cross_region_fallback",
        "api_key_authentication",
        "service_account_json_key",
        "openai",
        "terra",
        "deepseek",
        "another_provider",
        "another_model_family",
        "another_project",
        "another_service_account",
        "another_region",
        "model_without_published_sydney_support",
    } <= rejected


def test_evidence_records_zero_external_actions_and_consumes_no_calls() -> None:
    evidence = admission.build_evidence(
        load(admission.POLICY_PATH),
        load(admission.POLICY_SCHEMA_PATH),
        load(admission.SOURCE_OBSERVATION_PATH),
    )
    assert evidence["result"] == "ariadne_vertex_sydney_provider_admission_blocked"
    assert evidence["next_tranche_opened"] is False
    assert set(evidence["external_actions"].values()) == {False}
    assert evidence["call_accounting"] == {
        "occupied_calls_authorized": 2,
        "occupied_calls_consumed": 0,
        "occupied_calls_remaining_under_this_closed_sequence": 0,
        "retry_performed": False,
        "fallback_performed": False,
    }


def test_validator_has_no_cloud_network_subprocess_or_environment_surface() -> None:
    source = Path(admission.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports |= {
        (node.module or "").split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not imports & {
        "google",
        "http",
        "os",
        "requests",
        "socket",
        "subprocess",
        "urllib",
    }
    referenced_names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    referenced_attributes = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    assert not {"environ", "urlopen"} & (referenced_names | referenced_attributes)


def test_committed_evidence_is_exact() -> None:
    assert admission.check_committed_evidence()["policy_valid"] is True
