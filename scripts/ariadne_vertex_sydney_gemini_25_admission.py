"""Validate the repository-only Gemini 2.5 Flash Sydney admission gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-vertex-sydney-gemini-25"
)
POLICY_PATH = ARTIFACT_ROOT / "provider-admission-policy.json"
SCHEMA_PATH = ARTIFACT_ROOT / "provider-admission-policy.schema.json"
SOURCE_PATH = ARTIFACT_ROOT / "official-source-observation.json"
EVIDENCE_PATH = ARTIFACT_ROOT / "tranche-1-admission-evidence.json"

EXPECTED_SUBJECT = {
    "provider": "google_vertex_ai",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "service_account": (
        "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
    ),
    "authentication": "keyless_impersonated_service_account_adc",
    "location": "australia-southeast1",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "automatic_fallback": False,
}


class AdmissionError(ValueError):
    """Raised for an inconsistent frozen admission artifact."""


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AdmissionError(f"{path.name}_must_be_object")
    return value


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _source(packet: Mapping[str, Any], source_id: str) -> Mapping[str, Any]:
    matches = [
        item
        for item in packet.get("sources", [])
        if isinstance(item, dict) and item.get("id") == source_id
    ]
    if len(matches) != 1:
        raise AdmissionError(f"official_source_not_exact:{source_id}")
    return matches[0]


def validate(
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

    if policy.get("subject") != EXPECTED_SUBJECT:
        errors.append("subject_binding_not_exact")
    expected_classes = {
        "authored_synthetic": True,
        "product_derived": False,
        "patient_or_health_information": False,
    }
    for name, expected in expected_classes.items():
        if policy.get("data_classes", {}).get(name, {}).get("admitted") is not expected:
            errors.append(f"data_class_decision_invalid:{name}")

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
        "another_model",
        "another_project",
        "another_service_account",
        "another_region",
        "model_without_published_sydney_support",
    }
    rejected = set(policy.get("rejected_routes", []))
    errors.extend(
        f"required_rejection_missing:{item}"
        for item in sorted(required_rejections - rejected)
    )

    model = _source(source_packet, "gemini_2_5_flash_model_card")[
        "observations"
    ]
    residency = _source(source_packet, "model_data_residency")["observations"]
    retention = _source(source_packet, "zero_data_retention")["observations"]
    endpoint = _source(source_packet, "service_endpoints")["observations"]
    if model.get("model_id") != "gemini-2.5-flash":
        errors.append("model_identifier_mismatch")
    if model.get("launch_stage") != "GA":
        errors.append("model_not_ga")
    if model.get("structured_output_supported") is not True:
        errors.append("structured_output_not_supported")
    if model.get("model_availability_australia_southeast1") is not True:
        errors.append("sydney_model_availability_missing")
    if model.get("ml_processing_australia_southeast1") is not True:
        errors.append("sydney_ml_processing_missing")
    if model.get("retirement_on") != "2026-10-16":
        errors.append("retirement_binding_mismatch")
    if residency.get("gemini_2_5_flash_australia_supported") is not True:
        errors.append("residency_matrix_sydney_support_missing")
    if retention.get("published_gemini_in_memory_cache_default") != "enabled":
        errors.append("in_memory_cache_default_not_recorded")
    if retention.get("published_gemini_in_memory_cache_scope") != (
        "project_isolated_not_at_rest"
    ):
        errors.append("in_memory_cache_scope_not_recorded")
    if retention.get("published_gemini_in_memory_cache_ttl_hours") != 24:
        errors.append("in_memory_cache_ttl_not_recorded")
    if retention.get("project_cache_setting_inspected") is not False:
        errors.append("project_cache_external_read_detected")
    if endpoint.get("regional_service_endpoint") != (
        "https://australia-southeast1-aiplatform.googleapis.com"
    ):
        errors.append("regional_endpoint_mismatch")
    if "in_memory_cache_disabled" not in set(
        policy.get("required_admission_checks", [])
    ):
        errors.append("in_memory_cache_disabled_check_missing")
    if source_packet.get("unverified_provider_controls") != {
        "provider_training_control": "not_verified",
        "provider_abuse_monitoring_retention": "not_verified",
    }:
        errors.append("unverified_provider_controls_not_explicit")
    controls = policy.get("provider_controls", {})
    if "not independently verified" not in str(controls.get("training", "")):
        errors.append("training_control_proof_limit_missing")
    if "not independently verified" not in str(
        controls.get("abuse_monitoring_retention", "")
    ):
        errors.append("abuse_retention_proof_limit_missing")

    exclusions = source_packet.get("explicit_exclusions", {})
    if not exclusions or any(value is not False for value in exclusions.values()):
        errors.append("documentary_external_action_detected")
    expected_decision = {
        "admitted": True,
        "result": "ariadne_vertex_sydney_gemini_25_provider_admission_pass",
        "blocking_reasons": [],
        "next_action": "open_provider_blocked_contract_tranche_only",
    }
    if policy.get("decision") != expected_decision:
        errors.append("admission_decision_not_exact")
    return sorted(set(errors))


def build_evidence(
    policy: Mapping[str, Any],
    schema: Mapping[str, Any],
    source_packet: Mapping[str, Any],
) -> dict[str, Any]:
    errors = validate(policy, schema, source_packet)
    passed = not errors
    return {
        "schema_version": (
            "ariadne.vertex_sydney_gemini_25_tranche_1_admission_evidence.v1"
        ),
        "tranche": 1,
        "result": (
            "ariadne_vertex_sydney_gemini_25_provider_admission_pass"
            if passed
            else "ariadne_vertex_sydney_gemini_25_provider_admission_revision_required"
        ),
        "policy_valid": passed,
        "admitted": passed,
        "model_id": "gemini-2.5-flash",
        "required_location": "australia-southeast1",
        "model_published_for_required_location": True,
        "retirement_on": "2026-10-16",
        "blocking_reasons": errors,
        "next_tranche_opened": passed,
        "next_action": (
            "open_provider_blocked_contract_tranche_only"
            if passed
            else "fail_closed"
        ),
        "artifact_hashes": {
            "policy": canonical_hash(policy),
            "policy_schema": canonical_hash(schema),
            "official_source_observation": canonical_hash(source_packet),
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
            "occupied_calls_remaining": 2,
            "retry_performed": False,
            "fallback_performed": False,
        },
        "claim_limit": (
            "Current official Google documentation publishes gemini-2.5-flash "
            "for australia-southeast1 model availability and ML processing. "
            "This does not prove project entitlement, ADC usability, control "
            "posture, provider training or abuse-retention controls, provider "
            "acceptance, inference, or Australian physical or sovereign "
            "processing."
        ),
    }


def check_committed() -> dict[str, Any]:
    expected = build_evidence(
        load_object(POLICY_PATH),
        load_object(SCHEMA_PATH),
        load_object(SOURCE_PATH),
    )
    if load_object(EVIDENCE_PATH) != expected:
        raise AdmissionError("committed_admission_evidence_mismatch")
    return expected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = (
            check_committed()
            if args.check
            else build_evidence(
                load_object(POLICY_PATH),
                load_object(SCHEMA_PATH),
                load_object(SOURCE_PATH),
            )
        )
    except (AdmissionError, OSError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                {"status": "revision_required", "safe_error_code": str(error)},
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["policy_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
