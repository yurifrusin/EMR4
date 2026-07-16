"""Layer-specific ordinary-development evidence for LC4V7D1.

Fail-closed deterministic runner over 24 fresh Sol-authored inspectable probes
across four families: speech_like_time, cross_turn_interval,
ambiguous_practitioner_alternatives, and unknown_practitioner_schedule_explanation.

Classification precedence:
    1. authoring_invalid — fixture validation failure only
    2. normalization_gap  — normalization time forms missing or wrong
    3. parser_gap         — extraction (semantic_extraction) mismatches expected
    4. policy_gap         — policy (resolve_policy) mismatches expected
    5. contract_layer_gap — expected extraction/policy clarification divergence
       does not match observed
    6. pass               — every layer matches
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.semantic_extraction import extract_semantics


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    ROOT
    / "tests"
    / "fixtures"
    / "bernie_lc4v7d1_development"
    / "probes.json"
)
REFERENCE_DATE = "2026-07-16"
SCHEMA_VERSION = "bernie.lc4v7d1.probes.v1"
PROVENANCE = "fresh_sol_authored_synthetic_gold_development_only"
TOTAL_EXPECTED = 24
EXPECTED_FAMILY_COUNTS = {
    "speech_like_time": 6,
    "cross_turn_interval": 6,
    "ambiguous_practitioner_alternatives": 6,
    "unknown_practitioner_schedule_explanation": 6,
}

TOP_LEVEL_KEYS = {"schema_version", "reference_date", "provenance", "cases"}
CASE_KEYS = {"probe_id", "family", "language_form", "utterances", "expected"}
EXPECTED_KEYS = {
    "intended_action",
    "temporal_relation",
    "earliest_time",
    "latest_time",
    "practitioner_semantics",
    "extraction_requires_clarification",
    "extraction_clarification_choices",
    "policy_requires_clarification",
    "policy_clarification_choices",
    "policy_authority",
    "policy_tools",
    "policy_outcome",
    "resolved_practitioner_id",
    "safe_no_mutation",
    "normalization_time_forms",
}
NORMALIZATION_TIME_FORM_KEYS = {"turn_index", "fragment", "canonical"}

CLASSIFICATIONS = (
    "pass",
    "authoring_invalid",
    "normalization_gap",
    "parser_gap",
    "policy_gap",
    "contract_layer_gap",
)

# ---------------------------------------------------------------------------
# Fixture loading and validation
# ---------------------------------------------------------------------------


def load_fixture() -> dict[str, Any]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("LC4V7D1 fixture must be a JSON object")
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
            or any(
                not isinstance(item, str) or not item.strip() for item in utterances
            )
        ):
            errors.append(f"{label} utterances must be non-empty strings")
        expected = case.get("expected")
        if not isinstance(expected, Mapping) or set(expected) != EXPECTED_KEYS:
            errors.append(f"{label} expected field population is not exact")
        else:
            ntf = expected.get("normalization_time_forms", [])
            if not isinstance(ntf, list):
                errors.append(f"{label} normalization_time_forms must be a list")
            else:
                for ntf_idx, ntf_item in enumerate(ntf):
                    if (
                        not isinstance(ntf_item, Mapping)
                        or set(ntf_item) != NORMALIZATION_TIME_FORM_KEYS
                    ):
                        errors.append(
                            f"{label} normalization_time_forms[{ntf_idx}]"
                            f" schema is invalid"
                        )
                        break

    if len(ids) != len(set(ids)):
        errors.append("probe IDs must be unique")
    if dict(families) != EXPECTED_FAMILY_COUNTS:
        errors.append("family population is not exact")
    return tuple(dict.fromkeys(errors))


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def compute_fixture_hash(fixture: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        fixture, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


# ---------------------------------------------------------------------------
# Observation (runs extraction + policy, no expected values passed)
# ---------------------------------------------------------------------------


def _observe(utterances: list[str]) -> dict[str, Any]:
    """Produce a single deterministic observation.

    Calls ``extract_semantics`` then ``resolve_policy`` with diary_state
    ``"empty"``, empty appointments, and no fixture value passed downstream.
    """
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
            "temporal_relation": extraction.temporal_relation,
            "earliest_time": extraction.earliest_time,
            "latest_time": extraction.latest_time,
            "practitioner_semantics": extraction.entity_semantics.get("practitioner"),
            "requires_clarification": extraction.requires_clarification,
            "clarification_choices": extraction.clarification_choices,
            "authority": extraction.authority_claim,
            "tools": extraction.selected_tool_sequence,
            "claims_action_completed": extraction.claims_action_completed,
            "normalization_turns": [
                {
                    "time_forms": dict(nu.time_forms),
                    "source_spans": {
                        k: list(v) if isinstance(v, tuple) else v
                        for k, v in nu.source_spans.items()
                    },
                }
                for nu in extraction.normalized_turns
            ],
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


# ---------------------------------------------------------------------------
# Layer comparison functions
# ---------------------------------------------------------------------------


def _normalization_mismatches(
    expected: Mapping[str, Any],
    observation: Mapping[str, Any],
) -> tuple[str, ...]:
    """Check each expected normalisation time form has exact canonical + span."""
    expected_forms = expected.get("normalization_time_forms", [])
    if not expected_forms:
        return ()
    mismatches: list[str] = []
    normalization_turns = observation["extraction"]["normalization_turns"]
    for form in expected_forms:
        turn_idx = form["turn_index"]
        fragment = form["fragment"]
        canonical = form["canonical"]
        if turn_idx >= len(normalization_turns):
            mismatches.append(f"normalization_missing_turn:{turn_idx}")
            continue
        nu = normalization_turns[turn_idx]
        time_forms = nu["time_forms"]
        if fragment not in time_forms:
            mismatches.append(f"normalization_missing_fragment:{fragment}")
            continue
        if time_forms[fragment] != canonical:
            mismatches.append(f"normalization_canonical_mismatch:{fragment}")
        span_key = f"time:{fragment}"
        if span_key not in nu["source_spans"]:
            mismatches.append(f"normalization_missing_span:{fragment}")
    return tuple(mismatches)


def _extraction_mismatches(
    expected: Mapping[str, Any],
    observation: Mapping[str, Any],
) -> tuple[str, ...]:
    """Compare extraction layer against expected extraction fields."""
    extraction = observation["extraction"]
    mismatches: list[str] = []

    if extraction["intended_action"] != expected["intended_action"]:
        mismatches.append("intended_action")
    if extraction["temporal_relation"] != expected["temporal_relation"]:
        mismatches.append("temporal_relation")
    if extraction["earliest_time"] != expected["earliest_time"]:
        mismatches.append("earliest_time")
    if extraction["latest_time"] != expected["latest_time"]:
        mismatches.append("latest_time")
    if extraction["practitioner_semantics"] != expected["practitioner_semantics"]:
        mismatches.append("practitioner_semantics")
    if extraction["requires_clarification"] != expected.get(
        "extraction_requires_clarification"
    ):
        mismatches.append("extraction_requires_clarification")
    expected_choices = tuple(expected.get("extraction_clarification_choices", ()))
    if extraction["clarification_choices"] != expected_choices:
        mismatches.append("extraction_clarification_choices")
    if extraction["claims_action_completed"] is not False:
        mismatches.append("claims_action_completed")
    return tuple(mismatches)


def _policy_mismatches(
    expected: Mapping[str, Any],
    observation: Mapping[str, Any],
) -> tuple[str, ...]:
    """Compare policy layer against expected policy fields."""
    policy = observation["policy"]
    mismatches: list[str] = []

    if policy["requires_clarification"] != expected.get(
        "policy_requires_clarification"
    ):
        mismatches.append("policy_requires_clarification")
    expected_choices = tuple(expected.get("policy_clarification_choices", ()))
    if policy["clarification_choices"] != expected_choices:
        mismatches.append("policy_clarification_choices")
    if policy["authority"] != expected.get("policy_authority"):
        mismatches.append("policy_authority")
    expected_tools = tuple(expected.get("policy_tools", ()))
    if policy["tools"] != expected_tools:
        mismatches.append("policy_tools")
    if policy["downstream_outcome"] != expected.get("policy_outcome"):
        mismatches.append("policy_outcome")
    if policy["resolved_practitioner_id"] != expected.get(
        "resolved_practitioner_id"
    ):
        mismatches.append("resolved_practitioner_id")
    return tuple(mismatches)


def _safe(
    expected: Mapping[str, Any],
    observation: Mapping[str, Any],
) -> bool:
    """Safety invariant check.

    For ``safe_no_mutation: true`` — no completion claim, no deltas,
    no simulated write, exact expected policy tools/outcome.
    For ordinary create controls — exact expected policy result and
    a resolved practitioner ID (expected simulated create evidence
    is not suppressed).
    """
    if observation["extraction"]["claims_action_completed"] is not False:
        return False
    if _policy_mismatches(expected, observation):
        return False
    policy = observation["policy"]
    if expected.get("safe_no_mutation", True):
        return (
            policy["tools"] == ("request_clarification",)
            and policy["appointment_delta_count"] == 0
            and policy["audit_delta_count"] == 0
            and policy["simulated_write"] is False
        )
    # Ordinary create controls
    return policy["resolved_practitioner_id"] is not None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_lc4v7d1_evidence() -> dict[str, Any]:
    """Run the complete LC4V7D1 evidence procedure and return the report."""
    fixture = load_fixture()
    errors = validate_fixture(fixture)
    if errors:
        return {
            "schema_version": "bernie.lc4v7d1.evidence.v1",
            "fixture_hash": compute_fixture_hash(fixture),
            "fixture_valid": False,
            "fixture_validation_errors": errors,
            "aggregate": {
                "total": 0,
                "normalization_pass": 0,
                "extraction_pass": 0,
                "policy_pass": 0,
                "composed_pass": 0,
                "safe": 0,
                "variance": 0,
            },
            "classifications": {
                name: (TOTAL_EXPECTED if name == "authoring_invalid" else 0)
                for name in CLASSIFICATIONS
            },
            "family_counts": {},
            "selection": {"non_pass_count": 0, "selection_hash": ""},
            "cases": (),
        }

    results: list[dict[str, Any]] = []
    classification_counts: dict[str, int] = {name: 0 for name in CLASSIFICATIONS}

    for case in fixture["cases"]:
        first = _observe(case["utterances"])
        second = _observe(case["utterances"])
        expected = case["expected"]

        normalization_misms = _normalization_mismatches(expected, first)
        extraction_misms = _extraction_mismatches(expected, first)
        policy_misms = _policy_mismatches(expected, first)

        expected_divergence = (
            expected.get("extraction_requires_clarification", False)
            != expected.get("policy_requires_clarification", False)
        )
        observed_divergence = (
            first["extraction"]["requires_clarification"]
            != first["policy"]["requires_clarification"]
        )

        # Classify in precedence order
        if normalization_misms:
            classification = "normalization_gap"
        elif extraction_misms:
            classification = "parser_gap"
        elif policy_misms:
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
                "normalization_mismatches": normalization_misms,
                "extraction_mismatches": extraction_misms,
                "policy_mismatches": policy_misms,
                "safe": _safe(expected, first),
                "variance": first != second,
                "expected_layer_divergence": expected_divergence,
                "observed_layer_divergence": observed_divergence,
                "observations": (first, second),
            }
        )

    normalization_pass = sum(
        not item["normalization_mismatches"] for item in results
    )
    extraction_pass = sum(not item["extraction_mismatches"] for item in results)
    policy_pass = sum(not item["policy_mismatches"] for item in results)

    report = {
        "schema_version": "bernie.lc4v7d1.evidence.v1",
        "fixture_hash": compute_fixture_hash(fixture),
        "fixture_valid": True,
        "fixture_validation_errors": (),
        "aggregate": {
            "total": len(results),
            "normalization_pass": normalization_pass,
            "extraction_pass": extraction_pass,
            "policy_pass": policy_pass,
            "composed_pass": sum(
                not item["normalization_mismatches"]
                and not item["extraction_mismatches"]
                and not item["policy_mismatches"]
                for item in results
            ),
            "safe": sum(item["safe"] for item in results),
            "variance": sum(item["variance"] for item in results),
        },
        "classifications": classification_counts,
        "family_counts": dict(
            Counter(item["family"] for item in results)
        ),
        "selection": {
            "non_pass_count": 0,
            "selection_hash": "",
        },
        "cases": tuple(results),
    }

    # Compute report hash (without the hash field itself)
    report_encoded = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    report["report_hash"] = (
        "sha256:" + hashlib.sha256(report_encoded).hexdigest()
    )

    # Compute selection hash (non-pass cases only)
    non_pass = [
        item
        for item in results
        if item["classification"] != "pass"
    ]
    selection_data = [
        {
            "probe_id": item["probe_id"],
            "classification": item["classification"],
            "normalization_mismatches": item["normalization_mismatches"],
            "extraction_mismatches": item["extraction_mismatches"],
            "policy_mismatches": item["policy_mismatches"],
        }
        for item in non_pass
    ]
    selection_encoded = json.dumps(
        selection_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    report["selection"]["non_pass_count"] = len(non_pass)
    report["selection"]["selection_hash"] = (
        "sha256:" + hashlib.sha256(selection_encoded).hexdigest()
    )

    return report


__all__ = [
    "CLASSIFICATIONS",
    "EXPECTED_FAMILY_COUNTS",
    "FIXTURE_PATH",
    "REFERENCE_DATE",
    "SCHEMA_VERSION",
    "TOTAL_EXPECTED",
    "compute_fixture_hash",
    "load_fixture",
    "run_lc4v7d1_evidence",
    "validate_fixture",
]
