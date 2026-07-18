"""Pure T3R6 policy reducer for future US-hosted synthetic development.

This module performs no authentication, cloud discovery, provider call,
network access, subprocess execution, runtime wiring, or database access.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json
from typing import Any, Mapping


EVIDENCE_SCHEMA_VERSION = "emr4.bernie.t3r6_us_synthetic_development.v1"
REPORT_SCHEMA_VERSION = "emr4.bernie.t3r6_us_synthetic_development_report.v1"
SCHEDULED_DECISION = "us_synthetic_development_path_scheduled_not_call_ready"
BLOCKED_DECISION = "us_synthetic_development_path_effective_but_not_call_ready"
READY_DECISION = "ready_for_separate_us_synthetic_provider_call_approval"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _days_between(start: str, end: str) -> int:
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def validate_evidence(evidence: Mapping[str, Any]) -> None:
    if evidence.get("schema_version") != EVIDENCE_SCHEMA_VERSION:
        raise ValueError("unexpected T3R6 evidence schema")
    date.fromisoformat(str(evidence["checked_at"]))

    decision = evidence["user_decision"]
    if decision.get("us_synthetic_development_authorized") is not True:
        raise ValueError("US synthetic-development policy is not authorized")
    date.fromisoformat(decision["effective_from"])
    if decision.get("production_pii_earliest_review_year", 0) < 2027:
        raise ValueError("production/PII review cannot be brought forward before 2027")

    policy = evidence["policy"]
    if policy.get("development_location") != "us":
        raise ValueError("T3R6 development location must be the US multi-region")
    if policy.get("production_pii_location") != "australia-southeast1":
        raise ValueError("production/PII location must remain Sydney")
    if policy.get("minimum_model_runway_days") < 180:
        raise ValueError("model runway floor must be at least 180 days")
    if policy.get("automatic_location_fallback") is not False:
        raise ValueError("automatic regional fallback must remain prohibited")
    required_false = (
        "pii_allowed",
        "patient_or_practice_data_allowed",
        "protected_holdout_material_allowed",
        "historical_diary_material_allowed",
        "external_corpus_material_allowed",
        "raw_prompt_or_response_persistence",
        "grounding_allowed",
        "tools_allowed",
        "product_runtime_wiring",
        "graphql_or_rest_change",
        "database_or_audit_write",
        "appointment_or_confirmation_authority",
        "deployment_or_release",
    )
    if any(policy.get(key) is not False for key in required_false):
        raise ValueError("T3R6 opens a prohibited data or product-authority surface")
    if policy.get("allowed_evidence_class") != "synthetic_development_only":
        raise ValueError("only synthetic development evidence may use the US path")

    models = evidence["documentary_evidence"]["models"]
    if not models or len({model["model_id"] for model in models}) != len(models):
        raise ValueError("documentary model evidence must be present and unique")
    for model in models:
        date.fromisoformat(model["retirement_on_or_after"])
        if "global" in model["location_controlled_locations"]:
            raise ValueError("global availability cannot be treated as a location-controlled path")


def build_readiness_report(
    evidence: Mapping[str, Any], *, as_of: str | None = None
) -> dict[str, Any]:
    """Reduce evidence to a deterministic policy/readiness result."""

    validate_evidence(evidence)
    checked_at = str(evidence["checked_at"])
    effective_as_of = as_of or checked_at
    date.fromisoformat(effective_as_of)
    decision = evidence["user_decision"]
    policy = evidence["policy"]
    development_location = policy["development_location"]
    minimum_runway = int(policy["minimum_model_runway_days"])

    model_assessments: list[dict[str, Any]] = []
    eligible_models: list[str] = []
    for model in evidence["documentary_evidence"]["models"]:
        runway = _days_between(effective_as_of, model["retirement_on_or_after"])
        location_ready = development_location in model["available_locations"]
        eligible = (
            model["lifecycle_stage"] == "GA"
            and location_ready
            and development_location in model["location_controlled_locations"]
            and runway >= minimum_runway
        )
        assessment = {
            "model_id": model["model_id"],
            "role": model["role"],
            "required_development_location_available": location_ready,
            "retirement_on_or_after": model["retirement_on_or_after"],
            "documented_runway_days": runway,
            "minimum_runway_satisfied": runway >= minimum_runway,
            "eligible": eligible,
        }
        model_assessments.append(assessment)
        if eligible:
            eligible_models.append(model["model_id"])

    transition_effective = date.fromisoformat(effective_as_of) >= date.fromisoformat(
        decision["effective_from"]
    )
    controls = evidence["control_verification"]
    control_checks = {
        "vertex_ai_api_enabled": controls["vertex_ai_api_enabled"] is True,
        "billing_and_cost_acceptance_verified": (
            controls["billing_and_cost_acceptance_verified"] is True
        ),
        "keyless_prediction_only_iam_verified": (
            controls["keyless_prediction_only_iam_verified"] is True
        ),
        "us_location_pin_verified": controls["us_location_pin_verified"] is True,
        "global_and_non_us_fallback_denied_verified": (
            controls["global_and_non_us_fallback_denied_verified"] is True
        ),
        "data_access_audit_logging_verified": (
            controls["data_access_audit_logging_verified"] is True
        ),
        "request_response_logging_disabled_verified": (
            controls["request_response_logging_disabled_verified"] is True
        ),
        "retention_and_abuse_monitoring_posture_verified": (
            controls["retention_and_abuse_monitoring_posture_verified"] is True
        ),
        "grounding_tools_and_explicit_cache_disabled_verified": (
            controls["grounding_tools_and_explicit_cache_disabled_verified"] is True
        ),
        "application_hard_limit_and_kill_switch_verified": (
            controls["application_hard_limit_and_kill_switch_verified"] is True
        ),
    }
    blocking_reasons: list[str] = []
    if not transition_effective:
        blocking_reasons.append("us_transition_effective_date_not_reached")
    if not eligible_models:
        blocking_reasons.append("no_ga_us_model_satisfies_minimum_runway")
    blocking_reasons.extend(key for key, passed in control_checks.items() if not passed)

    if not transition_effective:
        readiness_decision = SCHEDULED_DECISION
    elif blocking_reasons:
        readiness_decision = BLOCKED_DECISION
    else:
        readiness_decision = READY_DECISION

    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "checked_at": checked_at,
        "as_of": effective_as_of,
        "policy_decision": "accepted_us_synthetic_development_after_au_2_5_retirement",
        "readiness_decision": readiness_decision,
        "transition_effective": transition_effective,
        "effective_from": decision["effective_from"],
        "development_location": development_location,
        "production_pii_location": policy["production_pii_location"],
        "production_pii_earliest_review_year": decision[
            "production_pii_earliest_review_year"
        ],
        "authorizes_provider_call": False,
        "authorizes_pii": False,
        "authorizes_production": False,
        "automatic_location_fallback": False,
        "evidence_hash": canonical_hash(evidence),
        "model_assessments": model_assessments,
        "eligible_models": eligible_models,
        "control_checks": control_checks,
        "blocking_reasons": blocking_reasons,
        "next_boundary": (
            "obtain_exact_model_retention_budget_and_bounded_prompt_approval"
            if readiness_decision == READY_DECISION
            else "complete_controls_after_effective_date_then_rerun_no_call_readiness"
        ),
        "api_spine_boundary": {
            "classification": "developer_only_synthetic_access_ai_provider_feasibility",
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
