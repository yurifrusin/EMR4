#!/usr/bin/env python3
"""LC4R6 temporal source-evidence audit report.

Derives the surface temporal relation by applying the oracle-free temporal
extractor independently to every dialogue turn and retaining the last
non-``unspecified`` relation and bounds.  Classifies each selected scenario
into exactly one of:

- ``insufficient_surface_evidence``: contract expects non-unspecified but
  the dialogue has no extractable point/bound/interval relation;
- ``surface_contract_conflict``: dialogue has an explicit surface relation
  that differs from the contract relation;
- ``parser_gap``: explicit surface evidence supports the contract relation
  but the final interpreter observation differs.

Usage:
    python scripts/bernie_lc4r6_temporal_evidence_report.py            # print JSON
    python scripts/bernie_lc4r6_temporal_evidence_report.py --check     # verify frozen
    python scripts/bernie_lc4r6_temporal_evidence_report.py --check --json  # both
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
REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4r6-temporal-evidence-report.json"

# ---------------------------------------------------------------------------
# Frozen constants from the LC4R6 contract
# ---------------------------------------------------------------------------

# Frozen selection
EXPECTED_TEMPORAL_AF_HASH = "f56b4a20aad6161c"
EXPECTED_TEMPORAL_AF_COUNT = 159

# Taxonomy buckets
EXPECTED_BUCKETS: dict[str, dict[str, Any]] = {
    "insufficient_surface_evidence": {
        "count": 84,
        "hash": "c341652065504d17",
    },
    "surface_contract_conflict": {
        "count": 75,
        "hash": "fd04b9c86a54fea4",
    },
    "parser_gap": {
        "count": 0,
        "hash": "e3b0c44298fc1c14",
    },
}

# Insufficient subtypes by expected contract relation
EXPECTED_INSUFFICIENT_SUBTYPES: dict[str, int] = {
    "exact": 18,
    "not_before": 18,
    "not_after": 18,
    "interval": 18,
    "approximate": 12,
}

# Conflict expected/observed pairs
EXPECTED_CONFLICT_PAIRS: dict[tuple[str, str], int] = {
    ("approximate", "exact"): 10,
    ("exact", "approximate"): 2,
    ("interval", "approximate"): 3,
    ("interval", "exact"): 14,
    ("not_after", "approximate"): 2,
    ("not_after", "exact"): 16,
    ("not_before", "approximate"): 3,
    ("not_before", "exact"): 14,
    ("unspecified", "approximate"): 2,
    ("unspecified", "exact"): 9,
}

# LC4R5 semantic baseline (unchanged)
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

# Post-LC4R5 expected values (unchanged)
EXPECTED_POST_ACTION_SEMANTICS = 814
EXPECTED_POST_CLARIFICATION = 782


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _stable_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _selection_hash(scenario_ids: list[str]) -> str:
    """SHA-256 hexdigest truncated to 16 chars over newline-joined sorted IDs."""
    return hashlib.sha256(
        "\n".join(sorted(scenario_ids)).encode("utf-8")
    ).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Corpus loading and evaluation
# ---------------------------------------------------------------------------


def _load_corpus():
    """Load the LC4 development corpus."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.scale_corpus import DevelopmentOnlyLoader

    return DevelopmentOnlyLoader().load_all()


def _run_evaluation():
    """Run the full scaled evaluation and return the report."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.scaled_evaluator import generate_scaled_evaluation_report

    return generate_scaled_evaluation_report()


# ---------------------------------------------------------------------------
# Temporal aligned-failure analysis
# ---------------------------------------------------------------------------


def _extract_utterances_from_scenario(v) -> list[str]:
    return [
        turn.get("utterance", "")
        for turn in v.dialogue_turns
        if isinstance(turn.get("utterance"), str)
    ]


def _compute_temporal_category(
    v,
) -> tuple[bool, str]:
    """Compute the audit category for a single scenario at repeat index 0.

    Returns (is_aligned_failure, category_label).
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.composed_corpus_evaluator import (
        deterministic_interpret,
        deterministic_replay,
    )
    from app.services.bernie.composed_evaluator import (
        InterpretationObservation,
        score_interpretation_replay_pair,
    )
    from app.services.bernie.development_gap_audit import (
        ConflictRecord,
        RULE_NEGATION_MISMATCH,
        _check_action_conflict,
        _check_ambiguous_surface,
        _check_authority_conflict,
        _check_clarification_conflict,
        _check_duration_conflict,
        _check_entity_conflict,
        _check_temporal_conflict,
        _detect_surface_negation,
        _safe_excerpt,
    )

    utterances = _extract_utterances_from_scenario(v)
    interp = deterministic_interpret(v)
    interp_obj = InterpretationObservation(
        scenario_id=interp.scenario_id,
        sample_index=0,
        intended_action=interp.intended_action,
        action_semantics=interp.action_semantics,
        temporal_relation=interp.temporal_relation,
        normalized_values=dict(interp.normalized_values),
        entity_semantics=dict(interp.entity_semantics),
        requires_clarification=interp.requires_clarification,
        clarification_choices=interp.clarification_choices,
        selected_tool_sequence=interp.selected_tool_sequence,
        authority_claim=interp.authority_claim,
        claims_action_completed=interp.claims_action_completed,
        action_negated=interp.action_negated,
    )
    replay = deterministic_replay(v, interp_obj)
    result = score_interpretation_replay_pair(v, interp_obj, replay)

    # Replicate audit_candidates conflict detection order
    detected = None
    surface_negated = _detect_surface_negation(utterances)
    if surface_negated and not interp_obj.action_negated:
        detected = ConflictRecord(
            rule_id=RULE_NEGATION_MISMATCH,
            candidate_id=v.scenario_id,
            category="surface_contract_conflict",
            observed_value="surface_detected_negation",
            expected_value="parser_no_negation",
            evidence_excerpt=_safe_excerpt(utterances[0] if utterances else ""),
        )
    if detected is None:
        detected = _check_action_conflict(v, interp_obj, utterances)
    if detected is None:
        detected = _check_temporal_conflict(v, interp_obj, utterances)
    if detected is None:
        detected = _check_duration_conflict(v, interp_obj, utterances)
    if detected is None:
        detected = _check_entity_conflict(v, interp_obj, utterances)
    if detected is None:
        detected = _check_clarification_conflict(v, interp_obj, utterances)
    if detected is None:
        detected = _check_authority_conflict(v, interp_obj)
    if detected is None:
        detected = _check_ambiguous_surface(v, interp_obj, utterances)

    if detected is not None:
        cat = detected.category
    elif result.all_passed:
        cat = "aligned_pass"
    else:
        cat = "aligned_failure"

    is_af = cat == "aligned_failure"
    temporal_fails = not result.semantic_fields.temporal_relation.passed
    return is_af and temporal_fails, cat


def _extract_surface_temporal(utterances: list[str]) -> str:
    """Derive the surface temporal relation from dialogue turns.

    Applies the oracle-free temporal extractor to each turn and retains
    the last non-``unspecified`` relation.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.semantic_extraction import _extract_temporal

    surface_rel = "unspecified"
    for u in utterances:
        rel, _earliest, _latest = _extract_temporal(u)
        if rel != "unspecified":
            surface_rel = rel
    return surface_rel


def _classify_temporal_aligned_failures(
    variants,
) -> dict[str, Any]:
    """Classify the 159 temporal aligned-failure scenarios into three buckets."""
    from app.services.bernie.semantic_extraction import _extract_temporal

    scenarios_by_id = {v.scenario_id: v for v in variants}

    # First, identify aligned-failure + temporal failing scenarios
    af_temporal_ids: list[str] = []
    for v in variants:
        is_af_temporal, _cat = _compute_temporal_category(v)
        if is_af_temporal:
            af_temporal_ids.append(v.scenario_id)

    # Hash and count verification
    selection_hash = _selection_hash(af_temporal_ids)

    # Classify each into a bucket
    insufficient_ids: list[str] = []
    conflict_ids: list[str] = []
    parser_gap_ids: list[str] = []

    insufficient_subtypes: dict[str, int] = {}
    conflict_pair_counts: dict[str, int] = {}

    for sid in af_temporal_ids:
        v = scenarios_by_id[sid]
        contract_rel = v.temporal_relation
        utterances = _extract_utterances_from_scenario(v)
        surface_rel = _extract_surface_temporal(utterances)

        if surface_rel == "unspecified":
            insufficient_ids.append(sid)
            key = (
                contract_rel
                if contract_rel
                in ("exact", "not_before", "not_after", "interval", "approximate")
                else "other"
            )
            insufficient_subtypes[key] = insufficient_subtypes.get(key, 0) + 1
        elif surface_rel != contract_rel:
            conflict_ids.append(sid)
            pair_key = f"{contract_rel}/{surface_rel}"
            conflict_pair_counts[pair_key] = (
                conflict_pair_counts.get(pair_key, 0) + 1
            )
        else:
            parser_gap_ids.append(sid)

    return {
        "selection": {
            "count": len(af_temporal_ids),
            "hash": selection_hash,
            "expected_hash": EXPECTED_TEMPORAL_AF_HASH,
            "hash_match": selection_hash == EXPECTED_TEMPORAL_AF_HASH,
        },
        "buckets": {
            "insufficient_surface_evidence": {
                "count": len(insufficient_ids),
                "hash": _selection_hash(insufficient_ids),
                "expected_count": EXPECTED_BUCKETS["insufficient_surface_evidence"][
                    "count"
                ],
                "expected_hash": EXPECTED_BUCKETS["insufficient_surface_evidence"][
                    "hash"
                ],
            },
            "surface_contract_conflict": {
                "count": len(conflict_ids),
                "hash": _selection_hash(conflict_ids),
                "expected_count": EXPECTED_BUCKETS["surface_contract_conflict"][
                    "count"
                ],
                "expected_hash": EXPECTED_BUCKETS["surface_contract_conflict"]["hash"],
            },
            "parser_gap": {
                "count": len(parser_gap_ids),
                "hash": _selection_hash(parser_gap_ids),
                "expected_count": EXPECTED_BUCKETS["parser_gap"]["count"],
                "expected_hash": EXPECTED_BUCKETS["parser_gap"]["hash"],
            },
        },
        "insufficient_subtypes": {
            "by_expected_relation": {
                rel: insufficient_subtypes.get(rel, 0)
                for rel in ("exact", "not_before", "not_after", "interval", "approximate")
            }
        },
        "conflict_pair_counts": {
            pair_key: conflict_pair_counts.get(pair_key, 0)
            for pair_key in [
                "approximate/exact",
                "exact/approximate",
                "interval/approximate",
                "interval/exact",
                "not_after/approximate",
                "not_after/exact",
                "not_before/approximate",
                "not_before/exact",
                "unspecified/approximate",
                "unspecified/exact",
            ]
        },
    }


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------


def _compute_report_hash(report_no_hash: dict[str, Any]) -> str:
    """Compute report hash with the hash field excluded."""
    copy = dict(report_no_hash)
    copy.pop("report_hash", None)
    return _stable_hash(_canonical_json(copy))


def build_report() -> dict[str, Any]:
    """Build the full LC4R6 temporal evidence report."""
    corpus = _load_corpus()
    variants = list(corpus.all_variants())
    evaluation_report = _run_evaluation()

    sf = evaluation_report["per_dimension"]["semantic_fields"]

    def per_scenario(val: int) -> int:
        return val // REPEATS

    # Temporal aligned-failure analysis
    taxonomy = _classify_temporal_aligned_failures(variants)

    # Build payload
    report_payload: dict[str, Any] = {
        "schema_version": "lc4r6.temporal_source_evidence_audit.v1",
        "development_only": True,
        "silver_pending_only": True,
        "corpus_hash": evaluation_report.get("corpus_hash", ""),
        "lc4r5_baseline": {
            "intended_action": BASELINE_INTENDED_ACTION,
            "action_semantics": BASELINE_ACTION_SEMANTICS,
            "temporal_relation": BASELINE_TEMPORAL_RELATION,
            "normalized_values": BASELINE_NORMALIZED_VALUES,
            "entity_semantics": BASELINE_ENTITY_SEMANTICS,
            "clarification": BASELINE_CLARIFICATION,
            "safety": BASELINE_SAFETY,
        },
        "lc4r5_post_semantic_fields_one_repeat": {
            "intended_action": f"{per_scenario(sf['intended_action']['passed'])}/{TOTAL_SCENARIOS}",
            "action_semantics": f"{per_scenario(sf['action_semantics']['passed'])}/{TOTAL_SCENARIOS}",
            "temporal_relation": f"{per_scenario(sf['temporal_relation']['passed'])}/{TOTAL_SCENARIOS}",
            "normalized_values": f"{per_scenario(sf['normalized_values']['passed'])}/{TOTAL_SCENARIOS}",
            "entity_semantics": f"{per_scenario(sf['entity_semantics']['passed'])}/{TOTAL_SCENARIOS}",
            "clarification": f"{per_scenario(sf['requires_clarification']['passed'])}/{TOTAL_SCENARIOS}",
        },
        "safety": {
            "all_safe": evaluation_report["per_dimension"]["safety"]["passed"]
            == TOTAL_SAMPLES,
            "passed": evaluation_report["per_dimension"]["safety"]["passed"]
            // REPEATS,
            "total": TOTAL_SCENARIOS,
        },
        "repeat_variance": {
            "all_deltas_zero": evaluation_report["variance"][
                "all_samples_deterministic"
            ],
            "variant_scenario_count": evaluation_report["variance"][
                "variant_scenario_count"
            ],
            "method": "per-scenario observation and safety fingerprint",
            "sample_count": TOTAL_SAMPLES,
        },
        "temporal_selection": taxonomy["selection"],
        "temporal_taxonomy": taxonomy["buckets"],
        "insufficient_subtypes": taxonomy["insufficient_subtypes"],
        "conflict_pair_counts": taxonomy["conflict_pair_counts"],
        "assertions": {
            "selection_159": taxonomy["selection"]["count"]
            == EXPECTED_TEMPORAL_AF_COUNT,
            "selection_hash_match": taxonomy["selection"]["hash_match"],
            "insufficient_84": taxonomy["buckets"]["insufficient_surface_evidence"][
                "count"
            ]
            == EXPECTED_BUCKETS["insufficient_surface_evidence"]["count"],
            "insufficient_hash_match": taxonomy["buckets"][
                "insufficient_surface_evidence"
            ]["hash"]
            == EXPECTED_BUCKETS["insufficient_surface_evidence"]["hash"],
            "conflict_75": taxonomy["buckets"]["surface_contract_conflict"]["count"]
            == EXPECTED_BUCKETS["surface_contract_conflict"]["count"],
            "conflict_hash_match": taxonomy["buckets"]["surface_contract_conflict"][
                "hash"
            ]
            == EXPECTED_BUCKETS["surface_contract_conflict"]["hash"],
            "parser_gap_0": taxonomy["buckets"]["parser_gap"]["count"]
            == EXPECTED_BUCKETS["parser_gap"]["count"],
            "parser_gap_hash_match": taxonomy["buckets"]["parser_gap"]["hash"]
            == EXPECTED_BUCKETS["parser_gap"]["hash"],
            "insufficient_subtypes_exact_18": taxonomy["insufficient_subtypes"][
                "by_expected_relation"
            ].get("exact", 0)
            == EXPECTED_INSUFFICIENT_SUBTYPES["exact"],
            "insufficient_subtypes_not_before_18": taxonomy["insufficient_subtypes"][
                "by_expected_relation"
            ].get("not_before", 0)
            == EXPECTED_INSUFFICIENT_SUBTYPES["not_before"],
            "insufficient_subtypes_not_after_18": taxonomy["insufficient_subtypes"][
                "by_expected_relation"
            ].get("not_after", 0)
            == EXPECTED_INSUFFICIENT_SUBTYPES["not_after"],
            "insufficient_subtypes_interval_18": taxonomy["insufficient_subtypes"][
                "by_expected_relation"
            ].get("interval", 0)
            == EXPECTED_INSUFFICIENT_SUBTYPES["interval"],
            "insufficient_subtypes_approximate_12": taxonomy["insufficient_subtypes"][
                "by_expected_relation"
            ].get("approximate", 0)
            == EXPECTED_INSUFFICIENT_SUBTYPES["approximate"],
            "intended_action_no_regression": per_scenario(
                sf["intended_action"]["passed"]
            )
            >= BASELINE_INTENDED_ACTION,
            "action_semantics_exactly_814": per_scenario(
                sf["action_semantics"]["passed"]
            )
            == EXPECTED_POST_ACTION_SEMANTICS,
            "clarification_exactly_782": per_scenario(
                sf["requires_clarification"]["passed"]
            )
            == EXPECTED_POST_CLARIFICATION,
            "temporal_relation_no_regression": per_scenario(
                sf["temporal_relation"]["passed"]
            )
            >= BASELINE_TEMPORAL_RELATION,
            "normalized_values_no_regression": per_scenario(
                sf["normalized_values"]["passed"]
            )
            >= BASELINE_NORMALIZED_VALUES,
            "entity_semantics_no_regression": per_scenario(
                sf["entity_semantics"]["passed"]
            )
            >= BASELINE_ENTITY_SEMANTICS,
            "safety_exact_1152_of_1152": evaluation_report["per_dimension"][
                "safety"
            ]["passed"]
            == TOTAL_SAMPLES,
            "repeat_variance_zero": evaluation_report["variance"][
                "all_samples_deterministic"
            ],
        },
    }

    report_payload["report_hash"] = _compute_report_hash(report_payload)
    return report_payload


# ---------------------------------------------------------------------------
# --check mode
# ---------------------------------------------------------------------------


def _load_frozen_report() -> dict[str, Any]:
    """Load the frozen LC4R6 report from docs."""
    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            f"Frozen LC4R6 report not found at {REPORT_PATH}"
        )
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_check(report: dict[str, Any]) -> bool:
    """Verify recomputed report against frozen report and contract assertions."""
    frozen = _load_frozen_report()
    issues: list[str] = []

    # --- 1. Report hash ---
    recomputed_hash_no_hash = _compute_report_hash(report)
    frozen_hash = frozen.get("report_hash", "")
    if recomputed_hash_no_hash != frozen_hash:
        issues.append(
            f"report_hash mismatch: recomputed={recomputed_hash_no_hash}, "
            f"frozen={frozen_hash}"
        )

    # --- 2. Corpus hash ---
    if report.get("corpus_hash", "") != frozen.get("corpus_hash", ""):
        issues.append("corpus_hash mismatch")

    # --- 3. Selection ---
    for key in ("count", "hash", "hash_match", "expected_hash"):
        rv = report.get("temporal_selection", {}).get(key)
        fv = frozen.get("temporal_selection", {}).get(key)
        if rv != fv:
            issues.append(f"temporal_selection.{key} mismatch: {rv} != {fv}")

    # --- 4. Taxonomy buckets ---
    for bucket in (
        "insufficient_surface_evidence",
        "surface_contract_conflict",
        "parser_gap",
    ):
        for attr in ("count", "hash", "expected_count", "expected_hash"):
            rv = report.get("temporal_taxonomy", {}).get(bucket, {}).get(attr)
            fv = frozen.get("temporal_taxonomy", {}).get(bucket, {}).get(attr)
            if rv != fv:
                issues.append(
                    f"temporal_taxonomy.{bucket}.{attr} mismatch: {rv} != {fv}"
                )

    # --- 5. Insufficient subtypes ---
    r_sub = (
        report.get("insufficient_subtypes", {})
        .get("by_expected_relation", {})
    )
    f_sub = (
        frozen.get("insufficient_subtypes", {})
        .get("by_expected_relation", {})
    )
    for rel in ("exact", "not_before", "not_after", "interval", "approximate"):
        if r_sub.get(rel) != f_sub.get(rel):
            issues.append(
                f"insufficient_subtypes.{rel} mismatch: "
                f"{r_sub.get(rel)} != {f_sub.get(rel)}"
            )

    # --- 6. Conflict pair counts ---
    r_pairs = report.get("conflict_pair_counts", {})
    f_pairs = frozen.get("conflict_pair_counts", {})
    for pair_key in EXPECTED_CONFLICT_PAIRS:
        pair_str = f"{pair_key[0]}/{pair_key[1]}"
        if r_pairs.get(pair_str) != f_pairs.get(pair_str):
            issues.append(
                f"conflict_pair_counts.{pair_str} mismatch: "
                f"{r_pairs.get(pair_str)} != {f_pairs.get(pair_str)}"
            )

    # --- 7. Semantic fields (one repeat) ---
    r_fields = report.get("lc4r5_post_semantic_fields_one_repeat", {})
    f_fields = frozen.get("lc4r5_post_semantic_fields_one_repeat", {})
    for dim in (
        "intended_action",
        "action_semantics",
        "temporal_relation",
        "normalized_values",
        "entity_semantics",
        "clarification",
    ):
        if r_fields.get(dim) != f_fields.get(dim):
            issues.append(
                f"lc4r5_post_semantic_fields_one_repeat.{dim} mismatch: "
                f"{r_fields.get(dim)} != {f_fields.get(dim)}"
            )

    # --- 8. Safety ---
    r_safety = report.get("safety", {})
    f_safety = frozen.get("safety", {})
    if r_safety.get("all_safe") != f_safety.get("all_safe"):
        issues.append("safety.all_safe mismatch")
    if r_safety.get("passed") != f_safety.get("passed"):
        issues.append("safety.passed mismatch")

    # --- 9. Variance ---
    r_var = report.get("repeat_variance", {})
    f_var = frozen.get("repeat_variance", {})
    if r_var.get("all_deltas_zero") != f_var.get("all_deltas_zero"):
        issues.append("repeat_variance.all_deltas_zero mismatch")
    if r_var.get("variant_scenario_count") != f_var.get("variant_scenario_count"):
        issues.append("variant_scenario_count mismatch")

    # --- 10. Baseline ---
    r_base = report.get("lc4r5_baseline", {})
    f_base = frozen.get("lc4r5_baseline", {})
    for dim in (
        "intended_action",
        "action_semantics",
        "temporal_relation",
        "normalized_values",
        "entity_semantics",
        "clarification",
        "safety",
    ):
        if r_base.get(dim) != f_base.get(dim):
            issues.append(f"lc4r5_baseline.{dim} mismatch: {r_base.get(dim)} != {f_base.get(dim)}")

    # --- 11. Assertions ---
    r_assert = report.get("assertions", {})
    f_assert = frozen.get("assertions", {})
    all_assertion_names = set(r_assert.keys()) | set(f_assert.keys())
    for aname in sorted(all_assertion_names):
        if r_assert.get(aname) != f_assert.get(aname):
            issues.append(
                f"assertion {aname} mismatch: "
                f"{r_assert.get(aname)} != {f_assert.get(aname)}"
            )

    if issues:
        print("LC4R6 CHECK FAILED:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("LC4R6 CHECK PASSED")

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
