"""Layer-specific ordinary-development evidence for LC4V6D1."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.semantic_extraction import extract_semantics


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "bernie_lc4v6d1_development" / "probes.json"
REFERENCE_DATE = "2026-07-16"
SCHEMA_VERSION = "bernie.lc4v6d1.probes.v1"
PROVENANCE = "fresh_sol_authored_synthetic_gold_development_only"
TOTAL_EXPECTED = 24
EXPECTED_FAMILY_COUNTS = {
    "move_unknown_practitioner": 12,
    "move_known_practitioner_control": 6,
    "resize_paraphrase_control": 3,
    "status_paraphrase_control": 3,
}

TOP_LEVEL_KEYS = {"schema_version", "reference_date", "provenance", "cases"}
CASE_KEYS = {
    "probe_id", "family", "language_form", "utterances", "extraction", "policy"
}
EXTRACTION_KEYS = {
    "intended_action",
    "action_semantics",
    "temporal_relation",
    "earliest_time",
    "latest_time",
    "practitioner_semantics",
    "requires_clarification",
    "clarification_choices",
    "authority",
    "tools",
    "action_negated",
}
EXTRACTION_OPTIONAL_KEYS = {"duration_minutes"}
POLICY_KEYS = {
    "requires_clarification",
    "clarification_choices",
    "authority",
    "tools",
    "downstream_outcome",
    "resolved_practitioner_id",
    "appointment_delta_count",
    "audit_delta_count",
    "simulated_write",
}
CLASSIFICATIONS = (
    "pass",
    "authoring_invalid",
    "parser_gap",
    "policy_gap",
    "contract_layer_gap",
)


def load_fixture() -> dict[str, Any]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("LC4V6D1 fixture must be a JSON object")
    return payload


def validate_fixture(fixture: Any) -> tuple[str, ...]:
    """Fail-closed structural validation without executing product code."""
    errors: list[str] = []
    if not isinstance(fixture, Mapping):
        return ("fixture must be an object",)
    if set(fixture) != TOP_LEVEL_KEYS:
        errors.append("top-level field population is not exact")
    if fixture.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version is not exact")
    if fixture.get("reference_date") != REFERENCE_DATE:
        errors.append("reference_date is not exact")
    if fixture.get("provenance") != PROVENANCE:
        errors.append("provenance is not exact")
    cases = fixture.get("cases")
    if not isinstance(cases, list):
        return tuple(errors + ["cases must be a list"])
    if len(cases) != TOTAL_EXPECTED:
        errors.append(f"case population must equal {TOTAL_EXPECTED}")

    ids: list[str] = []
    families: Counter[str] = Counter()
    for index, case in enumerate(cases):
        label = f"case[{index}]"
        if not isinstance(case, Mapping):
            errors.append(f"{label} must be an object")
            continue
        if set(case) != CASE_KEYS:
            errors.append(f"{label} field population is not exact")
        probe_id = case.get("probe_id")
        if not isinstance(probe_id, str) or not probe_id:
            errors.append(f"{label} probe_id must be non-empty")
        else:
            ids.append(probe_id)
        family = case.get("family")
        if not isinstance(family, str):
            errors.append(f"{label} family must be a string")
        else:
            families[family] += 1
        if not isinstance(case.get("language_form"), str):
            errors.append(f"{label} language_form must be a string")
        utterances = case.get("utterances")
        if (
            not isinstance(utterances, list)
            or not utterances
            or any(not isinstance(item, str) or not item.strip() for item in utterances)
        ):
            errors.append(f"{label} utterances must be non-empty strings")

        extraction = case.get("extraction")
        if not isinstance(extraction, Mapping):
            errors.append(f"{label} extraction must be an object")
        elif not EXTRACTION_KEYS.issubset(extraction) or not set(extraction).issubset(
            EXTRACTION_KEYS | EXTRACTION_OPTIONAL_KEYS
        ):
            errors.append(f"{label} extraction field population is invalid")
        policy = case.get("policy")
        if not isinstance(policy, Mapping) or set(policy) != POLICY_KEYS:
            errors.append(f"{label} policy field population is not exact")

    if len(ids) != len(set(ids)):
        errors.append("probe IDs must be unique")
    if dict(families) != EXPECTED_FAMILY_COUNTS:
        errors.append("family population is not exact")
    return tuple(dict.fromkeys(errors))


def compute_fixture_hash(fixture: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        fixture, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _observe(utterances: list[str]) -> dict[str, Any]:
    extraction = extract_semantics(utterances, REFERENCE_DATE)
    policy = resolve_policy(
        utterances=utterances,
        entity_semantics=extraction.entity_semantics,
        requires_clarification=extraction.requires_clarification,
        clarification_choices=extraction.clarification_choices,
        intended_action=extraction.intended_action,
        action_semantics=extraction.action_semantics,
        authority_claim=extraction.authority_claim,
        selected_tool_sequence=extraction.selected_tool_sequence,
        normalized_values=extraction.normalized_values,
        temporal_relation=extraction.temporal_relation,
        earliest_time=extraction.earliest_time,
        latest_time=extraction.latest_time,
        action_negated=extraction.action_negated,
        diary_state="empty",
        diary_appointments=[],
        reference_date=REFERENCE_DATE,
    )
    return {
        "extraction": {
            "intended_action": extraction.intended_action,
            "action_semantics": extraction.action_semantics,
            "temporal_relation": extraction.temporal_relation,
            "earliest_time": extraction.earliest_time,
            "latest_time": extraction.latest_time,
            "normalized_earliest_time": extraction.normalized_values.get("earliest_time"),
            "normalized_latest_time": extraction.normalized_values.get("latest_time"),
            "duration_minutes": extraction.normalized_values.get("duration_minutes"),
            "practitioner_semantics": extraction.entity_semantics.get("practitioner"),
            "requires_clarification": extraction.requires_clarification,
            "clarification_choices": extraction.clarification_choices,
            "authority": extraction.authority_claim,
            "tools": extraction.selected_tool_sequence,
            "action_negated": extraction.action_negated,
            "claims_action_completed": extraction.claims_action_completed,
        },
        "policy": {
            "requires_clarification": policy.requires_clarification,
            "clarification_choices": policy.clarification_choices,
            "authority": policy.authority,
            "tools": policy.selected_tools,
            "downstream_outcome": policy.downstream_outcome,
            "resolved_practitioner_id": policy.resolved_practitioner_id,
            "appointment_delta_count": len(policy.appointment_deltas),
            "audit_delta_count": len(policy.audit_deltas),
            "simulated_write": policy.is_simulated_confirmed_write,
        },
    }


def _extraction_mismatches(case: Mapping[str, Any], observation: Mapping[str, Any]) -> tuple[str, ...]:
    expected = case["extraction"]
    actual = observation["extraction"]
    mismatches: list[str] = []
    for field in EXTRACTION_KEYS:
        expected_value = expected[field]
        if field in {"clarification_choices", "tools"}:
            expected_value = tuple(expected_value)
        if actual[field] != expected_value:
            mismatches.append(field)
    if actual["normalized_earliest_time"] != expected["earliest_time"]:
        mismatches.append("normalized_earliest_time")
    if actual["normalized_latest_time"] != expected["latest_time"]:
        mismatches.append("normalized_latest_time")
    if actual["duration_minutes"] != expected.get("duration_minutes"):
        mismatches.append("duration_minutes")
    if actual["claims_action_completed"] is not False:
        mismatches.append("claims_action_completed")
    return tuple(mismatches)


def _policy_mismatches(case: Mapping[str, Any], observation: Mapping[str, Any]) -> tuple[str, ...]:
    expected = case["policy"]
    actual = observation["policy"]
    mismatches: list[str] = []
    for field in POLICY_KEYS:
        expected_value = expected[field]
        if field in {"clarification_choices", "tools"}:
            expected_value = tuple(expected_value)
        if actual[field] != expected_value:
            mismatches.append(field)
    return tuple(mismatches)


def _safe(case: Mapping[str, Any], observation: Mapping[str, Any]) -> bool:
    """Safety is exact policy compliance plus no false completion claim."""
    if observation["extraction"]["claims_action_completed"] is not False:
        return False
    if _policy_mismatches(case, observation):
        return False
    actual = observation["policy"]
    expected = case["policy"]
    if expected["requires_clarification"]:
        return (
            actual["tools"] == ("request_clarification",)
            and actual["appointment_delta_count"] == 0
            and actual["audit_delta_count"] == 0
            and actual["simulated_write"] is False
        )
    if expected["simulated_write"] is False:
        return (
            actual["appointment_delta_count"] == 0
            and actual["audit_delta_count"] == 0
        )
    return actual["resolved_practitioner_id"] is not None


def run_lc4v6d1_evidence() -> dict[str, Any]:
    fixture = load_fixture()
    errors = validate_fixture(fixture)
    if errors:
        return {
            "schema_version": "bernie.lc4v6d1.evidence.v1",
            "fixture_hash": compute_fixture_hash(fixture),
            "fixture_valid": False,
            "fixture_validation_errors": errors,
            "aggregate": {"total": 0, "extraction_pass": 0, "policy_pass": 0, "composed_pass": 0, "safe": 0, "variance": 0},
            "classifications": {name: (TOTAL_EXPECTED if name == "authoring_invalid" else 0) for name in CLASSIFICATIONS},
            "conflated_clarification_failure_count": 0,
            "cases": (),
        }

    results: list[dict[str, Any]] = []
    classification_counts = {name: 0 for name in CLASSIFICATIONS}
    conflated_failures = 0
    for case in fixture["cases"]:
        first = _observe(case["utterances"])
        second = _observe(case["utterances"])
        extraction_mismatches = _extraction_mismatches(case, first)
        policy_mismatches = _policy_mismatches(case, first)
        expected_divergence = (
            case["extraction"]["requires_clarification"]
            != case["policy"]["requires_clarification"]
        )
        observed_divergence = (
            first["extraction"]["requires_clarification"]
            != first["policy"]["requires_clarification"]
        )
        if case["extraction"]["requires_clarification"] != case["policy"]["requires_clarification"]:
            conflated_failures += 1
        if extraction_mismatches:
            classification = "parser_gap"
        elif policy_mismatches:
            classification = "policy_gap"
        elif expected_divergence != observed_divergence:
            classification = "contract_layer_gap"
        else:
            classification = "pass"
        classification_counts[classification] += 1
        results.append(
            {
                "probe_id": case["probe_id"],
                "family": case["family"],
                "classification": classification,
                "extraction_mismatches": extraction_mismatches,
                "policy_mismatches": policy_mismatches,
                "safe": _safe(case, first),
                "variance": first != second,
                "expected_layer_divergence": expected_divergence,
                "observed_layer_divergence": observed_divergence,
                "observations": (first, second),
            }
        )

    extraction_pass = sum(not item["extraction_mismatches"] for item in results)
    policy_pass = sum(not item["policy_mismatches"] for item in results)
    return {
        "schema_version": "bernie.lc4v6d1.evidence.v1",
        "fixture_hash": compute_fixture_hash(fixture),
        "fixture_valid": True,
        "fixture_validation_errors": (),
        "aggregate": {
            "total": len(results),
            "extraction_pass": extraction_pass,
            "policy_pass": policy_pass,
            "composed_pass": sum(not item["extraction_mismatches"] and not item["policy_mismatches"] for item in results),
            "safe": sum(item["safe"] for item in results),
            "variance": sum(item["variance"] for item in results),
        },
        "classifications": classification_counts,
        "conflated_clarification_failure_count": conflated_failures,
        "cases": tuple(results),
    }


__all__ = [
    "CLASSIFICATIONS",
    "EXPECTED_FAMILY_COUNTS",
    "FIXTURE_PATH",
    "REFERENCE_DATE",
    "SCHEMA_VERSION",
    "TOTAL_EXPECTED",
    "compute_fixture_hash",
    "load_fixture",
    "run_lc4v6d1_evidence",
    "validate_fixture",
]
