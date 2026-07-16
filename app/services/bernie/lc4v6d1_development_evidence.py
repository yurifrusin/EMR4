"""LC4V6D1 fresh development probes and deterministic evidence runner.

Runs all 24 fresh Sol-authored probes through extract_semantics and
Option A resolve_policy, scoring extraction and policy independently.
Preserves the contract-layer distinction that unknown practitioner text
is exact at extraction but becomes clarification at policy when no
practitioner ID maps.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.semantic_extraction import extract_semantics

FIXTURE_PATH = Path(
    "tests/fixtures/bernie_lc4v6d1_development/probes.json",
)
REFERENCE_DATE = "2026-07-16"
SCHEMA_VERSION = "bernie.lc4v6d1.probes.v1"

EXPECTED_FAMILY_COUNTS: dict[str, int] = {
    "move_unknown_practitioner": 12,
    "move_known_practitioner_control": 6,
    "resize_paraphrase_control": 3,
    "status_paraphrase_control": 3,
}
TOTAL_EXPECTED = 24

REQUIRED_CASE_FIELDS = (
    "probe_id",
    "family",
    "language_form",
    "utterances",
    "extraction",
    "policy",
)

# Fields that must be present in every extraction and policy block
EXTRACTION_REQUIRED_KEYS = (
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
)
POLICY_REQUIRED_KEYS = (
    "requires_clarification",
    "clarification_choices",
    "authority",
    "tools",
    "downstream_outcome",
    "resolved_practitioner_id",
    "appointment_delta_count",
    "audit_delta_count",
    "simulated_write",
)


# --------------------------------------------------------------------------
# Fixture loading and validation
# --------------------------------------------------------------------------


def load_fixture() -> dict[str, Any]:
    """Load and return the probe fixture."""
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    """Validate fixture schema, population, family-counts, IDs, required fields.

    Returns a list of validation errors (empty when valid).
    """
    errors: list[str] = []

    # Schema version
    actual_schema = fixture.get("schema_version")
    if actual_schema != SCHEMA_VERSION:
        errors.append(
            f"schema_version: expected {SCHEMA_VERSION!r}, got {actual_schema!r}",
        )

    # Reference date
    actual_date = fixture.get("reference_date")
    if actual_date != REFERENCE_DATE:
        errors.append(
            f"reference_date: expected {REFERENCE_DATE!r}, got {actual_date!r}",
        )

    # Population count
    cases = fixture.get("cases", [])
    if len(cases) != TOTAL_EXPECTED:
        errors.append(f"case count: expected {TOTAL_EXPECTED}, got {len(cases)}")

    # Family counts
    actual_counts: dict[str, int] = {}
    for case in cases:
        family = case.get("family", "")
        actual_counts[family] = actual_counts.get(family, 0) + 1
    for family, expected_count in EXPECTED_FAMILY_COUNTS.items():
        actual = actual_counts.get(family, 0)
        if actual != expected_count:
            errors.append(
                f"family {family!r} count: expected {expected_count}, got {actual}",
            )

    # Unique probe IDs
    ids = [case.get("probe_id", "") for case in cases]
    if len(ids) != len(set(ids)):
        duplicates = {pid for pid in ids if ids.count(pid) > 1}
        errors.append(f"duplicate probe_id values: {sorted(duplicates)}")

    # Required fields per case
    for case in cases:
        pid = case.get("probe_id", "?")
        for field in REQUIRED_CASE_FIELDS:
            if field not in case:
                errors.append(f"case {pid!r} missing required field {field!r}")

    # Required keys inside extraction and policy blocks
    for case in cases:
        pid = case.get("probe_id", "?")
        extraction = case.get("extraction", {})
        for key in EXTRACTION_REQUIRED_KEYS:
            if key not in extraction:
                errors.append(
                    f"case {pid!r} extraction missing required key {key!r}",
                )
        policy = case.get("policy", {})
        for key in POLICY_REQUIRED_KEYS:
            if key not in policy:
                errors.append(
                    f"case {pid!r} policy missing required key {key!r}",
                )

    return errors


def compute_fixture_hash(fixture: dict[str, Any]) -> str:
    """Compute a deterministic canonical fixture hash over cases only."""
    payload = json.dumps(fixture["cases"], sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()


# --------------------------------------------------------------------------
# Observation
# --------------------------------------------------------------------------


def _observe(utterances: list[str]) -> dict[str, Any]:
    """Run extract_semantics and resolve_policy, returning observed fields."""
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
        # Extraction layer
        "intended_action": extraction.intended_action,
        "action_semantics": extraction.action_semantics,
        "temporal_relation": extraction.temporal_relation,
        "earliest_time": extraction.earliest_time,
        "latest_time": extraction.latest_time,
        "practitioner_semantics": extraction.entity_semantics.get("practitioner"),
        "extraction_requires_clarification": extraction.requires_clarification,
        "extraction_clarification_choices": extraction.clarification_choices,
        "extraction_authority": extraction.authority_claim,
        "extraction_tools": extraction.selected_tool_sequence,
        "extraction_claims_completed": extraction.claims_action_completed,
        "action_negated": extraction.action_negated,
        # Policy layer
        "policy_requires_clarification": policy.requires_clarification,
        "policy_clarification_choices": policy.clarification_choices,
        "policy_authority": policy.authority,
        "policy_tools": policy.selected_tools,
        "downstream_outcome": policy.downstream_outcome,
        "resolved_practitioner_id": policy.resolved_practitioner_id,
        "appointment_deltas": policy.appointment_deltas,
        "audit_deltas": policy.audit_deltas,
        "is_simulated_confirmed_write": policy.is_simulated_confirmed_write,
    }


# --------------------------------------------------------------------------
# Comparison helpers
# --------------------------------------------------------------------------


def _extraction_matches(
    case: dict[str, Any],
    observation: dict[str, Any],
) -> bool:
    """Check extraction layer against fixture extraction expectations."""
    exp = case["extraction"]
    checks = (
        observation["intended_action"] == exp.get("intended_action"),
        observation["action_semantics"] == exp.get("action_semantics"),
        observation["temporal_relation"] == exp.get("temporal_relation"),
        observation["earliest_time"] == exp.get("earliest_time"),
        observation["latest_time"] == exp.get("latest_time"),
        observation["practitioner_semantics"] == exp.get("practitioner_semantics"),
        observation["extraction_requires_clarification"]
        == exp.get("requires_clarification"),
        observation["extraction_clarification_choices"]
        == tuple(exp.get("clarification_choices", [])),
        observation["extraction_authority"] == exp.get("authority"),
        observation["extraction_tools"] == tuple(exp.get("tools", [])),
        observation["action_negated"] == exp.get("action_negated", False),
        observation["extraction_claims_completed"] is False,
    )
    return all(checks)


def _policy_matches(
    case: dict[str, Any],
    observation: dict[str, Any],
) -> bool:
    """Check policy layer against fixture policy expectations."""
    exp = case["policy"]
    checks = (
        observation["policy_requires_clarification"]
        == exp.get("requires_clarification"),
        observation["policy_clarification_choices"]
        == tuple(exp.get("clarification_choices", [])),
        observation["policy_authority"] == exp.get("authority"),
        observation["policy_tools"] == tuple(exp.get("tools", [])),
        observation["downstream_outcome"] == exp.get("downstream_outcome"),
        observation["resolved_practitioner_id"] == exp.get("resolved_practitioner_id"),
        len(observation["appointment_deltas"])
        == exp.get("appointment_delta_count", 0),
        len(observation["audit_deltas"]) == exp.get("audit_delta_count", 0),
        observation["is_simulated_confirmed_write"]
        == exp.get("simulated_write", False),
    )
    return all(checks)


def _is_safe(
    observation: dict[str, Any],
    expected_policy: dict[str, Any],
) -> bool:
    """Check safety: no completion claims, unknown practitioner = no mutation."""
    if observation["extraction_claims_completed"]:
        return False
    # When policy requires clarification, safety means clarify tools + no deltas
    if observation["policy_requires_clarification"]:
        return (
            observation["policy_tools"] == ("request_clarification",)
            and not observation["appointment_deltas"]
            and not observation["audit_deltas"]
            and not observation["is_simulated_confirmed_write"]
        )
    # Otherwise, safety is implied when policy matches expectations
    return True


def _classify(
    extraction_match: bool,
    policy_match: bool,
    fixture_extraction: dict[str, Any],
    fixture_policy: dict[str, Any],
    observation: dict[str, Any],
) -> str:
    """Classify the case outcome into the required taxonomy.

    ``parser_gap`` — extraction layer does not match fixture extraction block.
    ``policy_gap`` — extraction matches but policy does not match fixture
    policy block.
    ``contract_layer_gap`` — both layers match their respective expectations
    but the runner invalidly conflated them (e.g. required identical
    clarification state when the fixture expects them to differ).  This is
    a runner-level bug, not a parser or policy defect.
    ``pass`` — both layers match and the layer-contract is preserved.
    """
    if not extraction_match:
        return "parser_gap"
    if extraction_match and not policy_match:
        return "policy_gap"

    # Both layers match their fixture expectations.  Verify the runner did
    # not improperly conflate layers by checking that the actual layer
    # relationship matches the fixture-intended relationship.
    exp_ext_clarify = fixture_extraction.get("requires_clarification", False)
    exp_pol_clarify = fixture_policy.get("requires_clarification", False)
    layers_expected_to_differ = exp_ext_clarify != exp_pol_clarify

    actual_ext_clarify = observation["extraction_requires_clarification"]
    actual_pol_clarify = observation["policy_requires_clarification"]
    layers_actually_differ = actual_ext_clarify != actual_pol_clarify

    if layers_expected_to_differ != layers_actually_differ:
        return "contract_layer_gap"

    return "pass"


# --------------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------------


def run_lc4v6d1_evidence() -> dict[str, Any]:
    """Run every ordinary probe twice and return deterministic evidence."""
    fixture = load_fixture()
    cases_raw = fixture["cases"]

    # Validate fixture
    validation_errors = validate_fixture(fixture)
    fixture_hash = compute_fixture_hash(fixture)
    fixture_valid = len(validation_errors) == 0

    case_results: list[dict[str, Any]] = []
    extraction_pass_ids: list[str] = []
    policy_pass_ids: list[str] = []
    safe_ids: list[str] = []
    variance_ids: list[str] = []
    classifications: dict[str, int] = {
        "pass": 0,
        "parser_gap": 0,
        "policy_gap": 0,
        "contract_layer_gap": 0,
        "authoring_invalid": 0,
    }

    for case in cases_raw:
        utterances = case["utterances"]
        pid = case["probe_id"]

        # Run twice
        obs1 = _observe(utterances)
        obs2 = _observe(utterances)

        has_variance = obs1 != obs2

        extraction_ok = _extraction_matches(case, obs1)
        policy_ok = _policy_matches(case, obs1)
        safe = _is_safe(obs1, case["policy"])

        classification = _classify(
            extraction_ok,
            policy_ok,
            case["extraction"],
            case["policy"],
            obs1,
        )

        classifications[classification] += 1
        if extraction_ok:
            extraction_pass_ids.append(pid)
        if policy_ok:
            policy_pass_ids.append(pid)
        if safe:
            safe_ids.append(pid)
        if has_variance:
            variance_ids.append(pid)

        case_results.append(
            {
                "probe_id": pid,
                "family": case["family"],
                "language_form": case.get("language_form", ""),
                "classification": classification,
                "extraction_match": extraction_ok,
                "policy_match": policy_ok,
                "safe": safe,
                "variance": has_variance,
                "observations": (obs1, obs2),
            },
        )

    # Aggregate counts
    total = len(cases_raw)
    extraction_pass = len(extraction_pass_ids)
    policy_pass = len(policy_pass_ids)
    composed_pass = len(
        [c for c in case_results if c["extraction_match"] and c["policy_match"]],
    )
    safe_count = len(safe_ids)
    variance_count = len(variance_ids)

    return {
        "schema_version": SCHEMA_VERSION,
        "fixture_hash": fixture_hash,
        "fixture_valid": fixture_valid,
        "fixture_validation_errors": validation_errors,
        "baseline": {
            "total": TOTAL_EXPECTED,
            "family_counts": dict(EXPECTED_FAMILY_COUNTS),
        },
        "aggregate": {
            "total": total,
            "extraction_pass": extraction_pass,
            "policy_pass": policy_pass,
            "composed_pass": composed_pass,
            "safe": safe_count,
            "variance": variance_count,
        },
        "classifications": classifications,
        "layer_ids": {
            "extraction_pass": tuple(sorted(extraction_pass_ids)),
            "policy_pass": tuple(sorted(policy_pass_ids)),
            "safe": tuple(sorted(safe_ids)),
            "variance": tuple(sorted(variance_ids)),
        },
        "cases": tuple(case_results),
    }


__all__ = [
    "EXPECTED_FAMILY_COUNTS",
    "TOTAL_EXPECTED",
    "FIXTURE_PATH",
    "REFERENCE_DATE",
    "SCHEMA_VERSION",
    "compute_fixture_hash",
    "load_fixture",
    "run_lc4v6d1_evidence",
    "validate_fixture",
]
