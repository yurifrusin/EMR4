#!/usr/bin/env python3
"""LC4R5 deterministic explanation clarification/action semantics report.

Usage:
    python scripts/bernie_lc4r5_report.py            # print report JSON
    python scripts/bernie_lc4r5_report.py --check     # verify frozen assertions only
    python scripts/bernie_lc4r5_report.py --check --json  # verify + print JSON
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
REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4r5-report.json"

# ---------------------------------------------------------------------------
# Constants — frozen from the LC4R5 contract
# ---------------------------------------------------------------------------

# Frozen selection hashes from Sol contract
EXPECTED_REPAIR_HASH = "b69abbcbc6febe29"
EXPECTED_PRESERVE_HASH = "34c95db64c716f56"

# Pre-LC4R5 baseline per-scenario counts (from contract)
BASELINE_INTENDED_ACTION = 880
BASELINE_ACTION_SEMANTICS = 730
BASELINE_TEMPORAL_RELATION = 628
BASELINE_NORMALIZED_VALUES = 101
BASELINE_ENTITY_SEMANTICS = 300
BASELINE_CLARIFICATION = 698
BASELINE_SAFETY = 1152
TOTAL_SCENARIOS = 1152
TOTAL_SAMPLES = 2304
REPEATS = 2

# Frozen target counts
EXPECTED_REPAIR_TARGET = 84
EXPECTED_PRESERVE_TARGET = 12

# Expected post-LC4R5 counts
EXPECTED_ACTION_SEMANTICS = 814
EXPECTED_CLARIFICATION = 782

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


def _analyze_explanation_selection(corpus, aligned_ids: set[str] | None = None) -> dict[str, Any]:
    """Recompute LC4R5 frozen selection using runtime extractor predicates.

    Repair target: explain_schedule scenarios where practitioner is
    ``exact`` or ``corrected`` (runtime surface-derived, not scenario labels).

    Preservation target: explain_schedule scenarios where practitioner
    is ``ambiguous`` (runtime surface-derived).

    When *aligned_ids* is provided, only scenarios inside the aligned boundary
    are considered.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.semantic_extraction import _detect_intended_action, _extract_entity_semantics

    repair_ids: list[str] = []
    preserve_ids: list[str] = []

    for v in corpus.all_variants():
        tid = v.scenario_id
        if aligned_ids is not None and tid not in aligned_ids:
            continue

        turns = [t.get("utterance", "") for t in v.dialogue_turns]
        primary = turns[0]

        intended = _detect_intended_action(primary)
        if intended != "explain_schedule":
            continue

        entities = _extract_entity_semantics(turns)
        prac_sem = entities.get("practitioner", "omitted")

        if prac_sem in ("exact", "corrected"):
            repair_ids.append(tid)
        elif prac_sem == "ambiguous":
            preserve_ids.append(tid)

    return {
        "repair_count": len(repair_ids),
        "repair_selection_hash": _selection_hash(repair_ids),
        "repair_expected_hash": EXPECTED_REPAIR_HASH,
        "repair_hash_match": _selection_hash(repair_ids) == EXPECTED_REPAIR_HASH,
        "preserve_count": len(preserve_ids),
        "preserve_selection_hash": _selection_hash(preserve_ids),
        "preserve_expected_hash": EXPECTED_PRESERVE_HASH,
        "preserve_hash_match": _selection_hash(preserve_ids) == EXPECTED_PRESERVE_HASH,
    }


def _analyze_all_explain_semantics(corpus) -> dict[str, Any]:
    """Analyze all explain_schedule scenarios across the full partition."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.semantic_extraction import (
        _detect_intended_action,
        _extract_entity_semantics,
        extract_semantics,
    )

    results: dict[str, Any] = {
        "total_explain_schedule": 0,
        "practitioner_exact": 0,
        "practitioner_corrected": 0,
        "practitioner_ambiguous": 0,
        "practitioner_omitted": 0,
        "patient_exact": 0,
        "patient_ambiguous": 0,
        "patient_omitted": 0,
        "still_clarifying": 0,
    }

    for v in corpus.all_variants():
        turns = [t.get("utterance", "") for t in v.dialogue_turns]
        primary = turns[0]

        intended = _detect_intended_action(primary)
        if intended != "explain_schedule":
            continue

        results["total_explain_schedule"] += 1
        entities = _extract_entity_semantics(turns)
        prac_sem = entities.get("practitioner", "omitted")
        pat_sem = entities.get("patient", "omitted")

        results[f"practitioner_{prac_sem}"] += 1
        results[f"patient_{pat_sem}"] += 1

        obs = extract_semantics(turns, "2026-07-14")
        if obs.requires_clarification:
            results["still_clarifying"] += 1

    return results


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------


def _compute_lc4r5_report_hash(report_no_hash: dict[str, Any]) -> str:
    """Compute the LC4R5 report hash with the hash field excluded."""
    copy = dict(report_no_hash)
    copy.pop("report_hash", None)
    return _stable_hash(_canonical_json(copy))


def build_report() -> dict[str, Any]:
    """Build the full LC4R5 evidence report."""
    corpus = _load_corpus()
    report = _run_evaluation()

    sf = report["per_dimension"]["semantic_fields"]

    # Per-scenario counts (divide by 2 repeats)
    def per_scenario(val: int) -> int:
        return val // REPEATS

    # Frozen selection analysis
    selection = _analyze_explanation_selection(corpus)
    all_explain = _analyze_all_explain_semantics(corpus)

    # Build report payload (without report_hash)
    report_payload: dict[str, Any] = {
        "schema_version": "lc4r5.explanation_clarification.v1",
        "development_only": True,
        "silver_pending_only": True,
        "corpus_hash": report.get("corpus_hash", ""),
        "pre_lc4r5_baseline": {
            "intended_action": BASELINE_INTENDED_ACTION,
            "action_semantics": BASELINE_ACTION_SEMANTICS,
            "temporal_relation": BASELINE_TEMPORAL_RELATION,
            "normalized_values": BASELINE_NORMALIZED_VALUES,
            "entity_semantics": BASELINE_ENTITY_SEMANTICS,
            "clarification": BASELINE_CLARIFICATION,
            "safety": BASELINE_SAFETY,
        },
        "post_lc4r5_semantic_fields_one_repeat": {
            "intended_action": f"{per_scenario(sf['intended_action']['passed'])}/{TOTAL_SCENARIOS}",
            "action_semantics": f"{per_scenario(sf['action_semantics']['passed'])}/{TOTAL_SCENARIOS}",
            "temporal_relation": f"{per_scenario(sf['temporal_relation']['passed'])}/{TOTAL_SCENARIOS}",
            "normalized_values": f"{per_scenario(sf['normalized_values']['passed'])}/{TOTAL_SCENARIOS}",
            "entity_semantics": f"{per_scenario(sf['entity_semantics']['passed'])}/{TOTAL_SCENARIOS}",
            "clarification": f"{per_scenario(sf['requires_clarification']['passed'])}/{TOTAL_SCENARIOS}",
        },
        "safety": {
            "all_safe": report["per_dimension"]["safety"]["passed"] == TOTAL_SAMPLES,
            "passed": report["per_dimension"]["safety"]["passed"] // REPEATS,
            "total": TOTAL_SCENARIOS,
        },
        "repeat_variance": {
            "all_deltas_zero": report["variance"]["all_samples_deterministic"],
            "variant_scenario_count": report["variance"]["variant_scenario_count"],
            "method": "per-scenario observation and safety fingerprint",
            "sample_count": TOTAL_SAMPLES,
        },
        "frozen_selection": {
            "repair_target": {
                "expected_count": EXPECTED_REPAIR_TARGET,
                "observed_count": selection["repair_count"],
                "observed_hash": selection["repair_selection_hash"],
                "expected_hash": EXPECTED_REPAIR_HASH,
                "hash_match": selection["repair_hash_match"],
            },
            "preserve_clarification": {
                "expected_count": EXPECTED_PRESERVE_TARGET,
                "observed_count": selection["preserve_count"],
                "observed_hash": selection["preserve_selection_hash"],
                "expected_hash": EXPECTED_PRESERVE_HASH,
                "hash_match": selection["preserve_hash_match"],
            },
        },
        "explain_semantics_summary": dict(all_explain),
        "assertions": {
            "action_semantics_exactly_814": per_scenario(sf["action_semantics"]["passed"]) == EXPECTED_ACTION_SEMANTICS,
            "clarification_exactly_782": per_scenario(sf["requires_clarification"]["passed"]) == EXPECTED_CLARIFICATION,
            "intended_action_no_regression": per_scenario(sf["intended_action"]["passed"]) >= BASELINE_INTENDED_ACTION,
            "temporal_relation_no_regression": per_scenario(sf["temporal_relation"]["passed"]) >= BASELINE_TEMPORAL_RELATION,
            "normalized_values_no_regression": per_scenario(sf["normalized_values"]["passed"]) >= BASELINE_NORMALIZED_VALUES,
            "entity_semantics_no_regression": per_scenario(sf["entity_semantics"]["passed"]) >= BASELINE_ENTITY_SEMANTICS,
            "safety_exact_1152_of_1152": report["per_dimension"]["safety"]["passed"] == TOTAL_SAMPLES,
            "repeat_variance_zero": report["variance"]["all_samples_deterministic"],
            "repair_selection_correct": selection["repair_count"] == EXPECTED_REPAIR_TARGET,
            "preserve_selection_correct": selection["preserve_count"] == EXPECTED_PRESERVE_TARGET,
        },
    }

    # Compute report hash over payload excluding the hash field itself
    report_payload["report_hash"] = _compute_lc4r5_report_hash(report_payload)

    return report_payload


# ---------------------------------------------------------------------------
# --check mode — authoritative comparison with frozen report
# ---------------------------------------------------------------------------


def _load_frozen_report() -> dict[str, Any]:
    """Load the frozen LC4R5 report from docs."""
    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            f"Frozen LC4R5 report not found at {REPORT_PATH}"
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
    recomputed_hash_no_hash = _compute_lc4r5_report_hash(report)
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
    frozen_fields = frozen.get("post_lc4r5_semantic_fields_one_repeat", {})
    recomputed_fields = report.get("post_lc4r5_semantic_fields_one_repeat", {})
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
    for key in ("repair_target", "preserve_clarification"):
        frozen_sel = frozen.get("frozen_selection", {}).get(key, {})
        recomputed_sel = report.get("frozen_selection", {}).get(key, {})
        if frozen_sel.get("hash_match") != recomputed_sel.get("hash_match"):
            issues.append(f"{key} hash_match mismatch")
        if frozen_sel.get("observed_count") != recomputed_sel.get("observed_count"):
            issues.append(
                f"{key} count mismatch: "
                f"recomputed={recomputed_sel.get('observed_count')}, "
                f"frozen={frozen_sel.get('observed_count')}"
            )
        if frozen_sel.get("observed_hash") != recomputed_sel.get("observed_hash"):
            issues.append(
                f"{key} hash mismatch: "
                f"recomputed={recomputed_sel.get('observed_hash')}, "
                f"frozen={frozen_sel.get('observed_hash')}"
            )

    # --- 7. Baseline counts ---
    frozen_baseline = frozen.get("pre_lc4r5_baseline", {})
    recomputed_baseline = report.get("pre_lc4r5_baseline", {})
    for dim in ("intended_action", "action_semantics", "temporal_relation",
                "normalized_values", "entity_semantics", "clarification", "safety"):
        if frozen_baseline.get(dim) != recomputed_baseline.get(dim):
            issues.append(
                f"baseline {dim} mismatch: "
                f"recomputed={recomputed_baseline.get(dim)}, "
                f"frozen={frozen_baseline.get(dim)}"
            )

    # --- 8. Assertions ---
    frozen_assertions = frozen.get("assertions", {})
    recomputed_assertions = report.get("assertions", {})
    for assert_name in ("action_semantics_exactly_814", "clarification_exactly_782",
                        "intended_action_no_regression", "temporal_relation_no_regression",
                        "normalized_values_no_regression", "entity_semantics_no_regression",
                        "safety_exact_1152_of_1152", "repeat_variance_zero",
                        "repair_selection_correct", "preserve_selection_correct"):
        if frozen_assertions.get(assert_name) != recomputed_assertions.get(assert_name):
            issues.append(
                f"assertion {assert_name} mismatch: "
                f"recomputed={recomputed_assertions.get(assert_name)}, "
                f"frozen={frozen_assertions.get(assert_name)}"
            )

    if issues:
        print("LC4R5 CHECK FAILED:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("LC4R5 CHECK PASSED")

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
