"""Pure fail-closed readiness contract for a future Australian Vertex evaluation.

The module performs no cloud discovery, authentication, SDK import, provider
call, or product-runtime wiring.  It reduces a reviewed evidence packet to a
deterministic readiness report for a separately approved synthetic evaluation.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json
from typing import Any, Mapping


EVIDENCE_SCHEMA_VERSION = "emr4.bernie.t3r5_vertex_au_feasibility.v1"
REPORT_SCHEMA_VERSION = "emr4.bernie.t3r5_vertex_au_readiness_report.v1"
READY_DECISION = "ready_for_separately_approved_synthetic_evaluation"
BLOCKED_DECISION = "blocked_before_provider_call"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _runway_days(checked_at: str, retirement_on: str) -> int:
    return (date.fromisoformat(retirement_on) - date.fromisoformat(checked_at)).days


def validate_evidence(evidence: Mapping[str, Any]) -> None:
    """Reject evidence that broadens the no-call, Australian-only boundary."""

    if evidence.get("schema_version") != EVIDENCE_SCHEMA_VERSION:
        raise ValueError("unexpected T3R5 evidence schema")
    date.fromisoformat(str(evidence["checked_at"]))

    scope = evidence["scope"]
    required_false = (
        "provider_model_call_performed",
        "cloud_mutation_performed",
        "product_runtime_wiring",
        "graphql_or_rest_change",
        "database_or_audit_write",
        "appointment_or_confirmation_authority",
        "deployment_or_release",
        "patient_or_practice_data_allowed",
        "protected_holdout_material_allowed",
        "historical_diary_material_allowed",
        "external_corpus_material_allowed",
    )
    if scope.get("no_call_feasibility_only") is not True:
        raise ValueError("T3R5 must remain a no-call feasibility exercise")
    if any(scope.get(key) is not False for key in required_false):
        raise ValueError("T3R5 evidence opens a prohibited authority surface")

    policy = evidence["policy"]
    if policy.get("required_location") != "australia-southeast1":
        raise ValueError("T3R5 requires the Sydney regional endpoint")
    if policy.get("minimum_model_runway_days") < 180:
        raise ValueError("model runway floor must be at least 180 days")
    if policy.get("phi_allowed") is not False:
        raise ValueError("PHI must remain prohibited")
    if policy.get("raw_prompt_or_response_persistence") is not False:
        raise ValueError("raw prompt and response persistence must remain prohibited")
    if policy.get("grounding_allowed") is not False or policy.get("tools_allowed") is not False:
        raise ValueError("grounding and provider tools must remain prohibited")

    models = evidence["documentary_evidence"]["models"]
    if not models or len({model["model_id"] for model in models}) != len(models):
        raise ValueError("documentary model evidence must be present and unique")
    for model in models:
        if model["lifecycle_stage"] != "GA":
            continue
        date.fromisoformat(model["retirement_on_or_after"])
        if "global" in model["available_locations"] and model.get("regional_isolation") is True:
            raise ValueError("global availability cannot be treated as regional isolation")


def build_readiness_report(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a deterministic fail-closed report from reviewed evidence."""

    validate_evidence(evidence)
    checked_at = str(evidence["checked_at"])
    policy = evidence["policy"]
    required_location = policy["required_location"]
    minimum_runway = int(policy["minimum_model_runway_days"])

    model_assessments: list[dict[str, Any]] = []
    eligible_models: list[str] = []
    for model in evidence["documentary_evidence"]["models"]:
        runway = _runway_days(checked_at, model["retirement_on_or_after"])
        location_ready = required_location in model["available_locations"]
        assessment = {
            "model_id": model["model_id"],
            "role": model["role"],
            "lifecycle_stage": model["lifecycle_stage"],
            "required_location_available": location_ready,
            "retirement_on_or_after": model["retirement_on_or_after"],
            "documented_runway_days": runway,
            "minimum_runway_satisfied": runway >= minimum_runway,
            "eligible": (
                model["lifecycle_stage"] == "GA"
                and location_ready
                and model.get("regional_isolation") is True
                and runway >= minimum_runway
            ),
        }
        if assessment["eligible"]:
            eligible_models.append(model["model_id"])
        model_assessments.append(assessment)

    observations = evidence["local_observations"]
    verification = evidence["control_verification"]
    local_checks = {
        "expected_project_selected": observations["configured_project"]
        == policy["required_project"],
        "keyless_impersonated_adc": observations["adc_is_impersonated_service_account"] is True,
        "vertex_ai_api_enabled": observations["vertex_ai_api_enabled"] is True,
        "billing_enabled": observations["billing_enabled"] is True,
        "project_environment_pin": observations["project_environment_pin_present"] is True,
        "location_environment_pin": (
            observations["location_environment_pin"] == required_location
        ),
        "vertex_transport_environment_pin": (
            observations["vertex_transport_environment_pin_present"] is True
        ),
    }
    control_checks = {
        "prediction_only_iam_verified": verification["prediction_only_iam_verified"] is True,
        "data_access_audit_logging_verified": (
            verification["data_access_audit_logging_verified"] is True
        ),
        "request_response_logging_disabled_verified": (
            verification["request_response_logging_disabled_verified"] is True
        ),
        "australian_resource_location_policy_verified": (
            verification["australian_resource_location_policy_verified"] is True
        ),
        "global_endpoint_denied_verified": (
            verification["global_endpoint_denied_verified"] is True
        ),
        "retention_and_abuse_monitoring_posture_verified": (
            verification["retention_and_abuse_monitoring_posture_verified"] is True
        ),
        "grounding_and_tools_disabled_verified": (
            verification["grounding_and_tools_disabled_verified"] is True
        ),
        "cost_acceptance_recorded": verification["cost_acceptance_recorded"] is True,
        "billing_budget_alert_verified": verification["billing_budget_alert_verified"] is True,
        "application_hard_limit_and_kill_switch_verified": (
            verification["application_hard_limit_and_kill_switch_verified"] is True
        ),
    }

    reasons: list[str] = []
    if not eligible_models:
        reasons.append("no_ga_model_has_both_sydney_availability_and_minimum_runway")
    reasons.extend(key for key, passed in local_checks.items() if not passed)
    reasons.extend(key for key, passed in control_checks.items() if not passed)
    decision = READY_DECISION if not reasons else BLOCKED_DECISION

    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "checked_at": checked_at,
        "decision": decision,
        "authorizes_provider_call": False,
        "evidence_hash": canonical_hash(evidence),
        "required_location": required_location,
        "minimum_model_runway_days": minimum_runway,
        "model_assessments": model_assessments,
        "eligible_models": eligible_models,
        "local_checks": local_checks,
        "control_checks": control_checks,
        "blocking_reasons": reasons,
        "next_boundary": (
            "obtain_separate_user_approval_for_a_bounded_synthetic_evaluation"
            if decision == READY_DECISION
            else "recheck_when_a_current_gemini_successor_is_ga_in_australia_southeast1"
        ),
        "api_spine_boundary": {
            "classification": "developer_only_access_ai_provider_feasibility",
            "stable_capability_id": policy["stable_capability_id"],
            "method": policy["method"],
            "product_runtime_wiring": False,
            "graphql_or_rest_route_change": False,
            "database_or_audit_write": False,
            "appointment_or_confirmation_authority": False,
            "deployment_or_release": False,
        },
    }
    report["report_hash"] = canonical_hash(report)
    return report
