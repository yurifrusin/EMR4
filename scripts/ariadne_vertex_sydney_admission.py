"""Validate the provider-free Sydney Vertex admission gate.

This module is deliberately repository-only.  It does not import a cloud SDK,
read credentials, inspect the environment, open a socket, spawn a process, or
contact Google.  It validates the frozen provider-admission policy and the
reviewed official-source observation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "orchestration" / "continuity" / "ariadne-vertex-sydney"
POLICY_PATH = ARTIFACT_ROOT / "provider-admission-policy.json"
POLICY_SCHEMA_PATH = ARTIFACT_ROOT / "provider-admission-policy.schema.json"
SOURCE_OBSERVATION_PATH = ARTIFACT_ROOT / "official-source-observation.json"
EVIDENCE_PATH = ARTIFACT_ROOT / "tranche-1-admission-evidence.json"

EXPECTED_PROJECT = "bernie-emr4-dev"
EXPECTED_SERVICE_ACCOUNT = (
    "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
)
EXPECTED_AUTHENTICATION = "keyless_impersonated_service_account_adc"
EXPECTED_MODEL = "gemini-3.5-flash"
EXPECTED_LOCATION = "australia-southeast1"
EXPECTED_HOSTNAME = "australia-southeast1-aiplatform.googleapis.com"
EXPECTED_BLOCKING_REASON = "gemini_3_5_flash_not_published_for_australia_southeast1"


class AdmissionError(ValueError):
    """Raised when a frozen admission artifact is unsafe or inconsistent."""


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AdmissionError(f"{path.name}_must_be_object")
    return payload


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _source(source_packet: Mapping[str, Any], source_id: str) -> Mapping[str, Any]:
    matches = [
        item
        for item in source_packet.get("sources", [])
        if isinstance(item, dict) and item.get("id") == source_id
    ]
    if len(matches) != 1:
        raise AdmissionError(f"official_source_not_exact:{source_id}")
    return matches[0]


def validate_admission(
    policy: Mapping[str, Any],
    schema: Mapping[str, Any],
    source_packet: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(policy, schema)
    except jsonschema.ValidationError as exc:
        errors.append(f"policy_schema_invalid:{exc.json_path}")
    except jsonschema.SchemaError as exc:
        errors.append(f"policy_schema_definition_invalid:{exc.json_path}")

    subject = policy.get("subject", {})
    expected_subject = {
        "provider": "google_vertex_ai",
        "model_id": EXPECTED_MODEL,
        "project": EXPECTED_PROJECT,
        "service_account": EXPECTED_SERVICE_ACCOUNT,
        "authentication": EXPECTED_AUTHENTICATION,
        "location": EXPECTED_LOCATION,
        "endpoint_hostname": EXPECTED_HOSTNAME,
        "automatic_fallback": False,
    }
    if subject != expected_subject:
        errors.append("subject_binding_not_exact")

    data_classes = policy.get("data_classes", {})
    expected_data_decisions = {
        "authored_synthetic": True,
        "product_derived": False,
        "patient_or_health_information": False,
    }
    for name, admitted in expected_data_decisions.items():
        if data_classes.get(name, {}).get("admitted") is not admitted:
            errors.append(f"data_class_decision_invalid:{name}")

    rejected = set(policy.get("rejected_routes", []))
    required_rejections = {
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
    }
    missing_rejections = sorted(required_rejections - rejected)
    errors.extend(f"required_rejection_missing:{item}" for item in missing_rejections)

    model_card = _source(source_packet, "gemini_3_5_flash_model_card")
    residency = _source(source_packet, "model_data_residency_matrix")
    endpoint = _source(source_packet, "service_endpoints")
    retention = _source(source_packet, "zero_data_retention")
    model_observation = model_card.get("observations", {})
    residency_observation = residency.get("observations", {})
    endpoint_observation = endpoint.get("observations", {})
    retention_observation = retention.get("observations", {})

    if model_observation.get("model_id") != EXPECTED_MODEL:
        errors.append("official_model_identifier_mismatch")
    if model_observation.get("australia_southeast1_listed") is not False:
        errors.append("official_model_card_location_observation_not_fail_closed")
    if EXPECTED_LOCATION in model_observation.get("model_availability_locations", []):
        errors.append("official_model_card_location_list_contradicts_block")
    if residency_observation.get("australia_southeast1_supported") is not False:
        errors.append("official_residency_matrix_observation_not_fail_closed")
    if residency_observation.get("gemini_3_5_flash_australia_cell") != "unsupported":
        errors.append("official_residency_matrix_cell_not_unsupported")
    if endpoint_observation.get("regional_service_endpoint") != (
        "https://" + EXPECTED_HOSTNAME
    ):
        errors.append("official_regional_endpoint_mismatch")
    if endpoint_observation.get("endpoint_existence_does_not_prove_model_support") is not True:
        errors.append("endpoint_existence_overclaim_guard_missing")
    if retention_observation.get("published_gemini_in_memory_cache_default") != "enabled":
        errors.append("in_memory_cache_default_not_recorded")
    if retention_observation.get("published_gemini_in_memory_cache_ttl_hours") != 24:
        errors.append("in_memory_cache_ttl_not_recorded")
    if (
        retention_observation.get(
            "published_gemini_in_memory_cache_can_be_disabled_at_project_level"
        )
        is not True
    ):
        errors.append("in_memory_cache_disable_control_not_recorded")
    if retention_observation.get("project_cache_setting_inspected") is not False:
        errors.append("project_cache_setting_external_read_detected")

    required_checks = set(policy.get("required_admission_checks", []))
    if "in_memory_cache_disabled" not in required_checks:
        errors.append("in_memory_cache_disabled_check_missing")
    cache_control = policy.get("provider_controls", {}).get("in_memory_cache", {})
    if "stop for Yuri" not in cache_control.get("local_requirement", ""):
        errors.append("in_memory_cache_fail_closed_rule_missing")

    decision = policy.get("decision", {})
    expected_decision = {
        "admitted": False,
        "result": "ariadne_vertex_sydney_provider_admission_blocked",
        "blocking_reasons": [EXPECTED_BLOCKING_REASON],
        "next_action": (
            "stop_for_yuri_without_adc_inspection_provider_call_model_substitution_"
            "or_external_cloud_change"
        ),
    }
    if decision != expected_decision or policy.get("status") != "blocked":
        errors.append("admission_decision_not_exact")

    claim_boundary = policy.get("claim_boundary", {})
    prohibited_claims = set(claim_boundary.get("prohibited_claims", []))
    if {
        "Australian physical processing occurred",
        "Australian sovereign processing is guaranteed",
        "the regional endpoint can serve gemini-3.5-flash",
        "container isolation proves remote provider geography",
    } - prohibited_claims:
        errors.append("claim_boundary_incomplete")

    exclusions = source_packet.get("explicit_exclusions", {})
    if not exclusions or any(value is not False for value in exclusions.values()):
        errors.append("official_source_observation_external_action_detected")
    if source_packet.get("result", {}).get("provider_call_authorized_by_observation") is not False:
        errors.append("official_source_observation_grants_call")

    return sorted(set(errors))


def build_evidence(
    policy: Mapping[str, Any],
    schema: Mapping[str, Any],
    source_packet: Mapping[str, Any],
) -> dict[str, Any]:
    errors = validate_admission(policy, schema, source_packet)
    return {
        "schema_version": "ariadne.vertex_sydney_tranche_1_admission_evidence.v1",
        "tranche": 1,
        "result": (
            "ariadne_vertex_sydney_provider_admission_blocked"
            if not errors
            else "ariadne_vertex_sydney_provider_admission_revision_required"
        ),
        "policy_valid": not errors,
        "admitted": False,
        "model_id": EXPECTED_MODEL,
        "required_location": EXPECTED_LOCATION,
        "model_published_for_required_location": False,
        "blocking_reasons": (
            [EXPECTED_BLOCKING_REASON]
            if not errors
            else ["repository_admission_contract_invalid", *errors]
        ),
        "next_tranche_opened": False,
        "next_action": "stop_for_yuri",
        "artifact_hashes": {
            "policy": sha256_value(policy),
            "policy_schema": sha256_value(schema),
            "official_source_observation": sha256_value(source_packet),
        },
        "external_actions": {
            "adc_inspection": False,
            "credential_read": False,
            "token_refresh": False,
            "cloud_control_plane_read": False,
            "provider_call": False,
            "prompt_transmission": False,
            "container_start": False,
            "external_cloud_mutation": False,
        },
        "call_accounting": {
            "occupied_calls_authorized": 2,
            "occupied_calls_consumed": 0,
            "occupied_calls_remaining_under_this_closed_sequence": 0,
            "retry_performed": False,
            "fallback_performed": False,
        },
        "claim_limit": (
            "Official Google documentation did not publish gemini-3.5-flash for "
            "australia-southeast1. The regional service hostname exists, but that "
            "does not establish model support, project entitlement, provider "
            "acceptance, inference, or Australian physical or sovereign processing."
        ),
    }


def check_committed_evidence() -> dict[str, Any]:
    policy = load_object(POLICY_PATH)
    schema = load_object(POLICY_SCHEMA_PATH)
    source_packet = load_object(SOURCE_OBSERVATION_PATH)
    expected = build_evidence(policy, schema, source_packet)
    actual = load_object(EVIDENCE_PATH)
    if actual != expected:
        raise AdmissionError("committed_admission_evidence_mismatch")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            result = check_committed_evidence()
        else:
            result = build_evidence(
                load_object(POLICY_PATH),
                load_object(POLICY_SCHEMA_PATH),
                load_object(SOURCE_OBSERVATION_PATH),
            )
    except (AdmissionError, OSError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                {
                    "status": "revision_required",
                    "safe_error_code": str(error),
                },
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["result"] == "ariadne_vertex_sydney_provider_admission_blocked" else 2


if __name__ == "__main__":
    raise SystemExit(main())
