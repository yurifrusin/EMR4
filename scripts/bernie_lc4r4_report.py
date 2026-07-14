#!/usr/bin/env python3
"""LC4R4 deterministic normalization/entity evidence report.

Usage:
    python scripts/bernie_lc4r4_report.py            # print report JSON
    python scripts/bernie_lc4r4_report.py --check     # verify frozen assertions only
    python scripts/bernie_lc4r4_report.py --check --json  # verify + print JSON
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4r4-report.json"

# ---------------------------------------------------------------------------
# Constants — frozen from the LC4R4 contract
# ---------------------------------------------------------------------------

# Frozen selection hashes from Sol contract
EXPECTED_SOMEONE_HASH = "50260edcf0fa2c0d"
EXPECTED_ADDITIVE_HASH = "485cd258fd5ebd60"

# Pre-LC4R4 baseline per-scenario counts (from contract)
BASELINE_INTENDED_ACTION = 880
BASELINE_ACTION_SEMANTICS = 730
BASELINE_TEMPORAL_RELATION = 628
BASELINE_NORMALIZED_VALUES = 101
BASELINE_ENTITY_SEMANTICS = 255
BASELINE_CLARIFICATION = 698
BASELINE_SAFETY = 1152
TOTAL_SCENARIOS = 1152
TOTAL_SAMPLES = 2304
REPEATS = 2

# Frozen target counts
EXPECTED_SOMEONE_TARGET = 70
EXPECTED_ADDITIVE_TARGET = 13

# Normalization failure signatures (from Sol contract)
EXPECTED_SIGNATURES: dict[str, int] = {
    "unsupported_expected_value_only": 298,
    "surface_disagrees_contract_plus_unsupported_expected": 114,
    "surface_disagrees_contract_only": 31,
    "surface_absent_from_contract_plus_unsupported_expected": 17,
    "all_three_conflict_types": 15,
    "surface_absent_from_contract_plus_surface_disagreement": 12,
    "surface_absent_from_contract_only": 2,
}

# Expected total aligned nv failure records
EXPECTED_ALIGNED_NV_FAILURES = 489

EXPECTED_LC4R4_REPORT_HASH = "sha256:a2ecc5b45d13c0a0caba6aa9f92a20a2cddbfa99015df530a6674df5443e4a5b"

# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _stable_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _selection_hash(scenario_ids: list[str]) -> str:
    """SHA-256 hexdigest truncated to 16 chars over newline-joined sorted IDs."""
    text = "\n".join(sorted(scenario_ids))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Corpus loading and evaluation
# ---------------------------------------------------------------------------


def _load_corpus():
    """Load the LC4 development corpus."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.scale_corpus import DevelopmentOnlyLoader

    loader = DevelopmentOnlyLoader()
    corpus = loader.load_all()
    return corpus


def _run_evaluation():
    """Run the full scaled evaluation and return the report."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.scaled_evaluator import generate_scaled_evaluation_report

    report = generate_scaled_evaluation_report()
    return report


# ---------------------------------------------------------------------------
# Selection analysis — uses runtime extractor/correction predicates
# ---------------------------------------------------------------------------


def _analyze_frozen_selection(corpus, aligned_ids: set[str] | None = None) -> dict[str, Any]:
    """Recompute frozen selection using runtime extractor/correction predicates.

    Standalone `someone`: any dialogue turn contains standalone ``\\bsomeone\\b``
    and no other old ambiguous phrase.

    Additive resolution: first turn has ambiguous patient semantics and a later
    non-correction turn has an explicit patient name, using the same pure
    extractor/correction predicates as runtime.

    When *aligned_ids* is provided, only scenarios inside the aligned boundary
    (i.e., whose IDs are in *aligned_ids*) are considered.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.semantic_extraction import _extract_patient, _is_correction_turn

    old_ambiguous = __import__("re").compile(
        r"\b(another patient|the patient|my patient|which patient|"
        r"multiple patients|two patients|same name|a patient|this patient)\b",
        __import__("re").I,
    )

    someone_ids: list[str] = []
    additive_ids: list[str] = []

    for v in corpus.all_variants():
        tid = v.scenario_id
        # Optionally filter to aligned boundary
        if aligned_ids is not None and tid not in aligned_ids:
            continue

        turns = [t.get("utterance", "") for t in v.dialogue_turns]

        # --- Standalone someone: any turn contains \\bsomeone\\b ---
        has_someone = any(
            bool(__import__("re").search(r"\bsomeone\b", t, __import__("re").I))
            for t in turns
        )
        # Exclude scenarios where old ambiguous phrases (not someone) match
        # so that only the "someone" fix (not other ambiguous phrases) is captured.
        has_other_old = any(old_ambiguous.search(t) for t in turns)
        if has_someone and not has_other_old:
            someone_ids.append(tid)

        # --- Additive resolution: first turn ambiguous, later non-correction exact ---
        if len(turns) >= 2 and v.patient_semantics == "exact":
            # Use runtime _extract_patient to check first turn semantics
            _, first_sem = _extract_patient(turns[0])
            if first_sem == "ambiguous":
                # Check later non-correction turns for explicit name
                for i in range(1, len(turns)):
                    if not _is_correction_turn(turns[i]):
                        _, later_sem = _extract_patient(turns[i])
                        if later_sem == "exact":
                            additive_ids.append(tid)
                            break

    return {
        "someone_count": len(someone_ids),
        "someone_selection_hash": _selection_hash(someone_ids),
        "someone_expected_hash": EXPECTED_SOMEONE_HASH,
        "someone_hash_match": _selection_hash(someone_ids) == EXPECTED_SOMEONE_HASH,
        "additive_count": len(additive_ids),
        "additive_selection_hash": _selection_hash(additive_ids),
        "additive_expected_hash": EXPECTED_ADDITIVE_HASH,
        "additive_hash_match": _selection_hash(additive_ids) == EXPECTED_ADDITIVE_HASH,
    }


# ---------------------------------------------------------------------------
# Normalization failure classification — exact scenario-level signatures
# ---------------------------------------------------------------------------


def _classify_nv_field_failure(
    field_name: str,
    expected_val: Any,
    observed_val: Any,
    source_spans: dict[str, Any],
) -> str:
    """Classify one field-level normalized-values mismatch.

    Returns one of:
        ``unsupported_expected_without_span``
        ``observed_surface_value_absent_from_contract``
        ``surface_value_disagrees_with_contract``
        ``other``
    """
    exp_missing = field_name not in expected_val if isinstance(expected_val, dict) else True
    obs_missing = field_name not in observed_val if isinstance(observed_val, dict) else True
    has_span = field_name in source_spans

    # Observed missing and expected field has no span
    if obs_missing and not exp_missing and not has_span:
        return "unsupported_expected_without_span"

    # Expected missing but an observed value exists
    if exp_missing and not obs_missing:
        return "observed_surface_value_absent_from_contract"

    # Both exist, differ, and the expected field has a span
    if not exp_missing and not obs_missing:
        # Compare expected vs observed values
        norm_expected = expected_val if isinstance(expected_val, dict) else {}
        norm_observed = observed_val if isinstance(observed_val, dict) else {}
        if norm_expected.get(field_name) != norm_observed.get(field_name):
            if has_span:
                return "surface_value_disagrees_with_contract"
            else:
                return "other"

    return "other"


def _per_scenario_nv_categories(
    expected_nv: dict[str, Any],
    observed_nv: dict[str, Any],
    source_spans: dict[str, Any],
) -> set[str]:
    """Classify all field-level normalized-value failures for one scenario.

    Returns the sorted set of category strings that apply.
    """
    categories: set[str] = set()
    all_keys = set(expected_nv.keys()) | set(observed_nv.keys())

    for key in all_keys:
        cat = _classify_nv_field_failure(
            key, expected_nv, observed_nv, source_spans,
        )
        if cat != "other":
            categories.add(cat)

    return categories


def _signature_name(categories: set[str]) -> str:
    """Map a set of per-scenario category strings to a contract signature name."""
    has_unsupported = "unsupported_expected_without_span" in categories
    has_absent = "observed_surface_value_absent_from_contract" in categories
    has_disagreement = "surface_value_disagrees_with_contract" in categories

    if has_unsupported and has_disagreement and has_absent:
        return "all_three_conflict_types"
    if has_unsupported and has_disagreement:
        return "surface_disagrees_contract_plus_unsupported_expected"
    if has_unsupported and has_absent:
        return "surface_absent_from_contract_plus_unsupported_expected"
    if has_disagreement and has_absent:
        return "surface_absent_from_contract_plus_surface_disagreement"
    if has_unsupported:
        return "unsupported_expected_value_only"
    if has_disagreement:
        return "surface_disagrees_contract_only"
    if has_absent:
        return "surface_absent_from_contract_only"
    return "other"


def _compute_normalization_failure_signatures(
    corpus,
    all_scenarios: list,
    aligned_scenario_ids: set[str],
) -> dict[str, Any]:
    """Compute normalization failure signatures for aligned scenarios.

    For each aligned scenario whose normalized-values score fails,
    compare expected and observed mappings field by field with
    ``scenario.source_spans``.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.composed_corpus_evaluator import (
        deterministic_interpret,
        deterministic_replay,
        score_interpretation_replay_pair,
    )

    signatures: dict[str, int] = {
        "unsupported_expected_value_only": 0,
        "surface_disagrees_contract_plus_unsupported_expected": 0,
        "surface_disagrees_contract_only": 0,
        "surface_absent_from_contract_plus_unsupported_expected": 0,
        "all_three_conflict_types": 0,
        "surface_absent_from_contract_plus_surface_disagreement": 0,
        "surface_absent_from_contract_only": 0,
    }
    total_aligned_nv_failures = 0
    other_count = 0

    for scenario in all_scenarios:
        if scenario.scenario_id not in aligned_scenario_ids:
            continue

        # Run interpretation + scoring to get normalized_values comparison
        interp = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interp)
        result = score_interpretation_replay_pair(scenario, interp, replay)

        # Check normalized_values
        nv = result.semantic_fields.normalized_values
        if nv.passed:
            continue

        total_aligned_nv_failures += 1

        # Classify field-level failures
        categories = _per_scenario_nv_categories(
            nv.expected if hasattr(nv, "expected") else scenario.normalized_values,
            nv.observed if hasattr(nv, "observed") else interp.normalized_values,
            scenario.source_spans,
        )

        sig = _signature_name(categories)
        if sig in signatures:
            signatures[sig] += 1
        else:
            other_count += 1

    return {
        "observed_total_nv_failures_per_scenario": total_aligned_nv_failures,
        "expected_aligned_nv_failure_records": EXPECTED_ALIGNED_NV_FAILURES,
        "expected_signatures": EXPECTED_SIGNATURES,
        "observed_signatures": signatures,
        "other_count": other_count,
    }


# ---------------------------------------------------------------------------
# Audit-based aligned boundary
# ---------------------------------------------------------------------------


def _compute_aligned_scenario_ids(corpus) -> set[str]:
    """Determine which scenarios are inside the aligned boundary.

    For each development scenario calls ``audit_candidates([scenario],
    num_repeats=1, max_conflict_examples=0)``.  A scenario is inside the
    aligned boundary iff ``aligned_pass_count + aligned_failure_count == 1``.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.development_gap_audit import audit_candidates

    aligned_ids: set[str] = set()
    all_variants = corpus.all_variants()

    for scenario in all_variants:
        audit = audit_candidates(
            [scenario],
            num_repeats=1,
            max_conflict_examples=0,
        )
        if audit.aligned_pass_count + audit.aligned_failure_count == 1:
            aligned_ids.add(scenario.scenario_id)

    return aligned_ids


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------


def _compute_lc4r4_report_hash(report_no_hash: dict[str, Any]) -> str:
    """Compute the LC4R4 report hash with the hash field excluded."""
    copy = dict(report_no_hash)
    copy.pop("report_hash", None)
    return _stable_hash(_canonical_json(copy))


def build_report() -> dict[str, Any]:
    """Build the full LC4R4 evidence report."""
    corpus = _load_corpus()
    report = _run_evaluation()

    sf = report["per_dimension"]["semantic_fields"]

    # Per-scenario counts (divide by 2 repeats)
    def per_scenario(val: int) -> int:
        return val // REPEATS

    # Compute aligned boundary
    all_variants = corpus.all_variants()
    aligned_ids = _compute_aligned_scenario_ids(corpus)

    # Frozen selection analysis (filtered by aligned boundary)
    selection = _analyze_frozen_selection(corpus, aligned_ids)

    # Normalization failure signatures
    nv_signatures = _compute_normalization_failure_signatures(
        corpus, all_variants, aligned_ids,
    )

    nv_fail_count = nv_signatures["observed_total_nv_failures_per_scenario"]

    # Build report payload (without report_hash)
    report_payload: dict[str, Any] = {
        "schema_version": "lc4r4.patient_entity_evidence.v1",
        "development_only": True,
        "silver_pending_only": True,
        "corpus_hash": report.get("corpus_hash", ""),
        "pre_lc4r4_baseline": {
            "intended_action": BASELINE_INTENDED_ACTION,
            "action_semantics": BASELINE_ACTION_SEMANTICS,
            "temporal_relation": BASELINE_TEMPORAL_RELATION,
            "normalized_values": BASELINE_NORMALIZED_VALUES,
            "entity_semantics": BASELINE_ENTITY_SEMANTICS,
            "clarification": BASELINE_CLARIFICATION,
            "safety": BASELINE_SAFETY,
        },
        "post_lc4r4_semantic_fields_one_repeat": {
            "intended_action": f"{per_scenario(sf['intended_action']['passed'])}/{TOTAL_SCENARIOS}",
            "action_semantics": f"{per_scenario(sf['action_semantics']['passed'])}/{TOTAL_SCENARIOS}",
            "temporal_relation": f"{per_scenario(sf['temporal_relation']['passed'])}/{TOTAL_SCENARIOS}",
            "normalized_values": f"{per_scenario(sf['normalized_values']['passed'])}/{TOTAL_SCENARIOS}",
            "entity_semantics": f"{per_scenario(sf['entity_semantics']['passed'])}/{TOTAL_SCENARIOS}",
            "clarification": f"{per_scenario(sf['requires_clarification']['passed'])}/{TOTAL_SCENARIOS}",
        },
        "safety": {
            "all_safe": report["per_dimension"]["safety"]["passed"] == TOTAL_SAMPLES,
            "passed": report["per_dimension"]["safety"]["passed"],
            "total": TOTAL_SAMPLES,
        },
        "repeat_variance": {
            "all_deltas_zero": report["variance"]["all_samples_deterministic"],
            "variant_scenario_count": report["variance"]["variant_scenario_count"],
            "method": "per-scenario observation and safety fingerprint",
            "sample_count": TOTAL_SAMPLES,
        },
        "frozen_selection": {
            "standalone_someone": {
                "expected_count": EXPECTED_SOMEONE_TARGET,
                "observed_count": selection["someone_count"],
                "observed_hash": selection["someone_selection_hash"],
                "expected_hash": EXPECTED_SOMEONE_HASH,
                "hash_match": selection["someone_hash_match"],
            },
            "additive_resolved": {
                "expected_count": EXPECTED_ADDITIVE_TARGET,
                "observed_count": selection["additive_count"],
                "observed_hash": selection["additive_selection_hash"],
                "expected_hash": EXPECTED_ADDITIVE_HASH,
                "hash_match": selection["additive_hash_match"],
            },
        },
        "full_partition_entity_effects": {
            "pre_lc4r4_entity_passes": BASELINE_ENTITY_SEMANTICS,
            "post_lc4r4_entity_passes": per_scenario(sf["entity_semantics"]["passed"]),
            "net_improvement": per_scenario(sf["entity_semantics"]["passed"]) - BASELINE_ENTITY_SEMANTICS,
            "total_someone_scenarios_fixed": selection["someone_count"],
            "total_additive_scenarios_fixed": selection["additive_count"],
        },
        "normalized_values_preserved": {
            "pre_lc4r4": BASELINE_NORMALIZED_VALUES,
            "post_lc4r4": per_scenario(sf["normalized_values"]["passed"]),
            "preserved": per_scenario(sf["normalized_values"]["passed"]) == BASELINE_NORMALIZED_VALUES,
        },
        "normalization_failure_signatures": {
            "observed_total_nv_failures_per_scenario": nv_fail_count,
            "expected_aligned_nv_failure_records": EXPECTED_ALIGNED_NV_FAILURES,
            "expected_signatures": EXPECTED_SIGNATURES,
            "observed_signatures": nv_signatures["observed_signatures"],
            "note": (
                "Exact scenario-level signature reproduction using the aligned "
                "development audit module with per-field source-span comparison."
            ),
        },
        "assertions": {
            "entity_semantics_at_least_300": per_scenario(sf["entity_semantics"]["passed"]) >= 300,
            "normalized_values_exactly_101": per_scenario(sf["normalized_values"]["passed"]) == 101,
            "intended_action_no_regression": per_scenario(sf["intended_action"]["passed"]) >= BASELINE_INTENDED_ACTION,
            "action_semantics_no_regression": per_scenario(sf["action_semantics"]["passed"]) >= BASELINE_ACTION_SEMANTICS,
            "temporal_relation_no_regression": per_scenario(sf["temporal_relation"]["passed"]) >= BASELINE_TEMPORAL_RELATION,
            "clarification_no_regression": per_scenario(sf["requires_clarification"]["passed"]) >= BASELINE_CLARIFICATION,
            "safety_exact_1152_of_1152": report["per_dimension"]["safety"]["passed"] == TOTAL_SAMPLES,
            "repeat_variance_zero": report["variance"]["all_samples_deterministic"],
        },
    }

    # Compute report hash over payload excluding the hash field itself
    report_payload["report_hash"] = _compute_lc4r4_report_hash(report_payload)

    return report_payload


# ---------------------------------------------------------------------------
# --check mode — authoritative comparison with frozen report
# ---------------------------------------------------------------------------


def _load_frozen_report() -> dict[str, Any]:
    """Load the frozen LC4R4 report from docs."""
    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            f"Frozen LC4R4 report not found at {REPORT_PATH}"
        )
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_check(report: dict[str, Any]) -> bool:
    """Run authoritative --check comparing recomputed report with frozen report.

    Enforces counts, hashes, signatures, baselines, safety, and variance.
    Exits nonzero on any drift.
    """
    frozen = _load_frozen_report()
    issues: list[str] = []

    # --- 1. Report hash comparison ---
    recomputed_hash_no_hash = _compute_lc4r4_report_hash(report)
    frozen_hash = frozen.get("report_hash", "")
    if recomputed_hash_no_hash != frozen_hash:
        issues.append(
            f"report_hash mismatch: "
            f"recomputed={recomputed_hash_no_hash}, "
            f"frozen={frozen_hash}"
        )

    # --- 2. Corpus hash ---
    frozen_corpus = frozen.get("corpus_hash", "")
    recomputed_corpus = report.get("corpus_hash", "")
    if recomputed_corpus != frozen_corpus:
        issues.append(
            f"corpus_hash mismatch: "
            f"recomputed={recomputed_corpus}, "
            f"frozen={frozen_corpus}"
        )

    # --- 3. Per-dimension semantic field counts (one repeat) ---
    frozen_fields = frozen.get("post_lc4r4_semantic_fields_one_repeat", {})
    recomputed_fields = report.get("post_lc4r4_semantic_fields_one_repeat", {})
    for dim in ("intended_action", "action_semantics", "temporal_relation",
                "normalized_values", "entity_semantics", "clarification"):
        frozen_val = frozen_fields.get(dim, "")
        recomputed_val = recomputed_fields.get(dim, "")
        if frozen_val != recomputed_val:
            issues.append(
                f"{dim} mismatch: "
                f"recomputed={recomputed_val}, "
                f"frozen={frozen_val}"
            )

    # --- 4. Safety ---
    frozen_safety = frozen.get("safety", {})
    recomputed_safety = report.get("safety", {})
    if frozen_safety.get("all_safe") != recomputed_safety.get("all_safe"):
        issues.append(
            f"safety.all_safe mismatch: "
            f"recomputed={recomputed_safety.get('all_safe')}, "
            f"frozen={frozen_safety.get('all_safe')}"
        )
    if frozen_safety.get("passed") != recomputed_safety.get("passed"):
        issues.append(
            f"safety.passed mismatch: "
            f"recomputed={recomputed_safety.get('passed')}, "
            f"frozen={frozen_safety.get('passed')}"
        )

    # --- 5. Variance ---
    frozen_variance = frozen.get("repeat_variance", {})
    recomputed_variance = report.get("repeat_variance", {})
    if frozen_variance.get("all_deltas_zero") != recomputed_variance.get("all_deltas_zero"):
        issues.append(
            f"repeat_variance.all_deltas_zero mismatch: "
            f"recomputed={recomputed_variance.get('all_deltas_zero')}, "
            f"frozen={frozen_variance.get('all_deltas_zero')}"
        )
    if frozen_variance.get("variant_scenario_count") != recomputed_variance.get("variant_scenario_count"):
        issues.append(
            f"variant_scenario_count mismatch: "
            f"recomputed={recomputed_variance.get('variant_scenario_count')}, "
            f"frozen={frozen_variance.get('variant_scenario_count')}"
        )

    # --- 6. Frozen selection hashes ---
    frozen_someone = frozen.get("frozen_selection", {}).get("standalone_someone", {})
    recomputed_someone = report.get("frozen_selection", {}).get("standalone_someone", {})
    if frozen_someone.get("hash_match") != recomputed_someone.get("hash_match"):
        issues.append(
            f"standalone_someone hash_match mismatch: "
            f"recomputed={recomputed_someone.get('hash_match')}, "
            f"frozen={frozen_someone.get('hash_match')}"
        )
    if frozen_someone.get("observed_count") != recomputed_someone.get("observed_count"):
        issues.append(
            f"standalone_someone count mismatch: "
            f"recomputed={recomputed_someone.get('observed_count')}, "
            f"frozen={frozen_someone.get('observed_count')}"
        )
    if frozen_someone.get("observed_hash") != recomputed_someone.get("observed_hash"):
        issues.append(
            f"standalone_someone hash mismatch: "
            f"recomputed={recomputed_someone.get('observed_hash')}, "
            f"frozen={frozen_someone.get('observed_hash')}"
        )

    frozen_additive = frozen.get("frozen_selection", {}).get("additive_resolved", {})
    recomputed_additive = report.get("frozen_selection", {}).get("additive_resolved", {})
    if frozen_additive.get("hash_match") != recomputed_additive.get("hash_match"):
        issues.append(
            f"additive_resolved hash_match mismatch: "
            f"recomputed={recomputed_additive.get('hash_match')}, "
            f"frozen={frozen_additive.get('hash_match')}"
        )
    if frozen_additive.get("observed_count") != recomputed_additive.get("observed_count"):
        issues.append(
            f"additive_resolved count mismatch: "
            f"recomputed={recomputed_additive.get('observed_count')}, "
            f"frozen={frozen_additive.get('observed_count')}"
        )
    if frozen_additive.get("observed_hash") != recomputed_additive.get("observed_hash"):
        issues.append(
            f"additive_resolved hash mismatch: "
            f"recomputed={recomputed_additive.get('observed_hash')}, "
            f"frozen={frozen_additive.get('observed_hash')}"
        )

    # --- 7. Normalization failure signatures ---
    frozen_nv = frozen.get("normalization_failure_signatures", {})
    recomputed_nv = report.get("normalization_failure_signatures", {})
    frozen_sigs = frozen_nv.get("expected_signatures", {})
    recomputed_sigs = recomputed_nv.get("observed_signatures", {})
    for sig_name, expected_count in frozen_sigs.items():
        actual_count = recomputed_sigs.get(sig_name, 0)
        if actual_count != expected_count:
            issues.append(
                f"signature {sig_name} count mismatch: "
                f"recomputed={actual_count}, "
                f"frozen={expected_count}"
            )
    if frozen_nv.get("expected_aligned_nv_failure_records") != recomputed_nv.get("observed_total_nv_failures_per_scenario"):
        issues.append(
            f"total aligned nv failures mismatch: "
            f"recomputed={recomputed_nv.get('observed_total_nv_failures_per_scenario')}, "
            f"frozen={frozen_nv.get('expected_aligned_nv_failure_records')}"
        )

    # --- 8. Baseline counts ---
    frozen_baseline = frozen.get("pre_lc4r4_baseline", {})
    recomputed_baseline = report.get("pre_lc4r4_baseline", {})
    for dim in ("intended_action", "action_semantics", "temporal_relation",
                "normalized_values", "entity_semantics", "clarification", "safety"):
        if frozen_baseline.get(dim) != recomputed_baseline.get(dim):
            issues.append(
                f"baseline {dim} mismatch: "
                f"recomputed={recomputed_baseline.get(dim)}, "
                f"frozen={frozen_baseline.get(dim)}"
            )

    # --- 9. Normalized values preserved ---
    frozen_nv_preserved = frozen.get("normalized_values_preserved", {})
    recomputed_nv_preserved = report.get("normalized_values_preserved", {})
    if frozen_nv_preserved.get("preserved") != recomputed_nv_preserved.get("preserved"):
        issues.append(
            f"normalized_values_preserved mismatch: "
            f"recomputed={recomputed_nv_preserved.get('preserved')}, "
            f"frozen={frozen_nv_preserved.get('preserved')}"
        )

    # --- 10. Assertions ---
    frozen_assertions = frozen.get("assertions", {})
    recomputed_assertions = report.get("assertions", {})
    for assert_name in ("entity_semantics_at_least_300", "normalized_values_exactly_101",
                        "intended_action_no_regression", "action_semantics_no_regression",
                        "temporal_relation_no_regression", "clarification_no_regression",
                        "safety_exact_1152_of_1152", "repeat_variance_zero"):
        if frozen_assertions.get(assert_name) != recomputed_assertions.get(assert_name):
            issues.append(
                f"assertion {assert_name} mismatch: "
                f"recomputed={recomputed_assertions.get(assert_name)}, "
                f"frozen={frozen_assertions.get(assert_name)}"
            )

    if issues:
        print("LC4R4 CHECK FAILED:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("LC4R4 CHECK PASSED")

    return len(issues) == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    check_only = "--check" in sys.argv
    print_json = "--json" in sys.argv or not check_only

    report = build_report()

    if check_only:
        passed = run_check(report)
        if print_json:
            print()
            print(json.dumps(report, indent=2, default=str))
        sys.exit(0 if passed else 1)
    else:
        print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
