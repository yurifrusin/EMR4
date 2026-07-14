"""LC4R2 development gap report — candidate-quality firewall (final evidence revision).

Reports the 1,152-record LC4 development partition with explicit LC4R1
baseline comparison, candidate-quality audit over the same 1,152 scale variants
(not unrelated LC2 candidates), per-rule uncapped aggregate counts,
per-dimension failure attribution, measured repeat variance, per-field semantic
baseline/current comparison, corpus/report hashes, and provenance counts.

Usage:
    python scripts/bernie_lc4r_development_gap_report.py          # write report
    python scripts/bernie_lc4r_development_gap_report.py --check  # verify in memory only

Output:
    docs/bernie-lc4r-development-gap-report.json (deterministic, write mode only)
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
    load_lc2_candidates,
)
from app.services.bernie.composed_evaluator import (
    InterpretationObservation,
    score_interpretation_replay_pair,
)
from app.services.bernie.development_gap_audit import (
    ATTRIBUTION_DIMENSIONS,
    CandidateInput,
    audit_candidates,
)
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

REPORT_PATH = _HERE / "docs" / "bernie-lc4r-development-gap-report.json"

# ---------------------------------------------------------------------------
# LC4R1 baseline (committed contract, one repeat, 1152 samples)
# ---------------------------------------------------------------------------
LC4R1_BASELINE: dict[str, int] = {
    "downstream_outcome": 50,
    "interpretation_tools": 592,
    "replay_tools": 592,
    "clarification": 610,
    "authority": 642,
    "appointment_deltas": 212,
    "audit_deltas": 192,
    "safety": 1152,
}

LC4_TOTAL = 1152

# Per-field LC4R1 baseline pass counts (from contract Finding D).
LC4R1_SEMANTIC_BASELINE: dict[str, int] = {
    "intended_action": 720,
    "action_semantics": 674,
    "temporal_relation": 628,
    "normalized_values": 101,
    "entity_semantics": 255,
    "clarification": 642,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stable_hash(content: str) -> str:
    """Deterministic SHA-256 hex digest (16‑char prefix)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _canonical_json(obj: object) -> str:
    """Stable JSON without whitespace, sorted keys."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _compute_corpus_hash(variants: list[ReceptionScenarioSpec]) -> str:
    """Stable hash over development variant IDs."""
    ids = sorted(v.scenario_id for v in variants)
    return _stable_hash(_canonical_json(ids))


def _compute_report_hash(report: dict) -> str:
    """Stable hash over the canonical report JSON."""
    return _stable_hash(_canonical_json(report))


# ---------------------------------------------------------------------------
# Evaluation over the LC4 development partition
# ---------------------------------------------------------------------------


def _evaluate_development(
    variants: list[ReceptionScenarioSpec],
    num_repeats: int = 1,
) -> dict[str, object]:
    """Run deterministic interpretation + replay over development variants.

    Returns per-dimension pass counts and per-field semantic passes.
    """
    counts: dict[str, int] = {
        "downstream_outcome": 0,
        "interpretation_tools": 0,
        "replay_tools": 0,
        "clarification": 0,
        "authority": 0,
        "appointment_deltas": 0,
        "audit_deltas": 0,
        "safety": 0,
    }

    # Per-field semantic passes.
    semantic_passes: dict[str, int] = {
        "intended_action": 0,
        "action_semantics": 0,
        "temporal_relation": 0,
        "normalized_values": 0,
        "entity_semantics": 0,
        "clarification": 0,
    }

    for v in variants:
        for sample_idx in range(num_repeats):
            interp = deterministic_interpret(v)
            interp = InterpretationObservation(
                scenario_id=interp.scenario_id,
                sample_index=sample_idx,
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
            replay = deterministic_replay(v, interp)
            result = score_interpretation_replay_pair(v, interp, replay)

            if result.downstream_outcome.passed:
                counts["downstream_outcome"] += 1
            if result.interpretation_tools.passed:
                counts["interpretation_tools"] += 1
            if result.tool_sequence.passed:
                counts["replay_tools"] += 1
            if result.clarification.passed:
                counts["clarification"] += 1
            if result.authority.passed:
                counts["authority"] += 1
            if result.appointment_deltas.passed:
                counts["appointment_deltas"] += 1
            if result.audit_deltas.passed:
                counts["audit_deltas"] += 1
            if result.safety.passed:
                counts["safety"] += 1
            # Per-field semantic passes.
            for field in semantic_passes:
                sf_result = getattr(result.semantic_fields, field, None)
                if sf_result is not None and sf_result.passed:
                    semantic_passes[field] += 1

    return {
        "counts": counts,
        "semantic_passes": semantic_passes,
    }


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------


def _compute_report() -> dict:
    """Compute the full development gap report."""
    # ---------- 1. Load development partition ----------
    loader = DevelopmentOnlyLoader()
    corpus = loader.load_all()
    variants: list[ReceptionScenarioSpec] = []
    for g in corpus.groups:
        variants.extend(g.all_variants)
    assert len(variants) == LC4_TOTAL, f"Expected {LC4_TOTAL} variants, got {len(variants)}"

    corpus_hash = _compute_corpus_hash(variants)

    # ---------- 2. Evaluate one repeat (baseline comparison) ----------
    one_repeat = _evaluate_development(variants, num_repeats=1)
    one_repeat_counts = one_repeat["counts"]
    semantic_passes: dict[str, int] = one_repeat["semantic_passes"]

    # ---------- 3. Evaluate two repeats (current) ----------
    two_repeat = _evaluate_development(variants, num_repeats=2)
    two_repeat_counts = two_repeat["counts"]
    two_repeat_total = LC4_TOTAL * 2

    # ---------- 4. Candidate-quality audit over the 1,152 scale variants ----------
    # Pass bare ReceptionScenarioSpec variants directly (Finding A).
    audit = audit_candidates(variants, num_repeats=2)

    # ---------- 5. LC2 audit (separate, for reference) ----------
    lc2_candidates = load_lc2_candidates()
    lc2_audit = audit_candidates(lc2_candidates, num_repeats=2)

    # Per-rule counts from uncapped tally (Finding B).
    rule_counts: dict[str, int] = dict(audit.per_rule_counts)

    # Bounded conflict examples (max 10)
    MAX_EXAMPLES = 10
    conflict_examples: list[dict[str, str]] = []
    for r in audit.conflict_records[:MAX_EXAMPLES]:
        example: dict[str, str] = {
            "rule_id": r.rule_id,
            "candidate_id": r.candidate_id,
            "category": r.category,
            "observed_value": r.observed_value or "",
            "expected_value": r.expected_value or "",
        }
        if r.evidence_excerpt:
            example["evidence_excerpt"] = r.evidence_excerpt
        conflict_examples.append(example)

    # ---------- 6. Dimension attribution (Finding C) ----------
    dim_attr: dict[str, dict[str, int]] = {}
    # Map internal field names to report dimension labels.
    _dim_label = {
        "downstream_outcome": "downstream_outcome",
        "tool_sequence": "replay_tools",
        "appointment_deltas": "appointment_deltas",
        "audit_deltas": "audit_deltas",
    }
    for dim in ATTRIBUTION_DIMENSIONS:
        da = audit.dimension_attribution.get(dim)
        label = _dim_label.get(dim, dim)
        if da is not None:
            dim_attr[label] = {
                "total": da.total,
                "passed": da.passed,
                "failed": da.failed,
                "surface_contract_conflict": da.surface_contract_conflict,
                "unsupported_or_ambiguous_surface": da.unsupported_or_ambiguous_surface,
                "aligned_failure": da.aligned_failure,
            }

    # ---------- 7. Build report ----------
    report: dict[str, object] = {
        "schema_version": "lc4r2.development_gap_report.v3",
        "development_only": True,
        "no_holdout_accessed": True,
        "silver_conflicts_do_not_reduce_gold_gaps": True,

        "corpus_manifest": {
            "total_development_records": LC4_TOTAL,
            "total_development_samples_one_repeat": LC4_TOTAL,
            "total_development_samples_two_repeats": two_repeat_total,
            "provenance": "silver",
            "adjudication": "pending",
            "corpus_hash": corpus_hash,
        },

        "baseline_lc4r1_one_repeat": {
            "downstream_outcome": f"{LC4R1_BASELINE['downstream_outcome']}/{LC4_TOTAL}",
            "interpretation_tools": f"{LC4R1_BASELINE['interpretation_tools']}/{LC4_TOTAL}",
            "replay_tools": f"{LC4R1_BASELINE['replay_tools']}/{LC4_TOTAL}",
            "clarification": f"{LC4R1_BASELINE['clarification']}/{LC4_TOTAL}",
            "authority": f"{LC4R1_BASELINE['authority']}/{LC4_TOTAL}",
            "appointment_deltas": f"{LC4R1_BASELINE['appointment_deltas']}/{LC4_TOTAL}",
            "audit_deltas": f"{LC4R1_BASELINE['audit_deltas']}/{LC4_TOTAL}",
            "safety": f"{LC4R1_BASELINE['safety']}/{LC4_TOTAL}",
        },

        "current_one_repeat": {
            dim: f"{one_repeat_counts[dim]}/{LC4_TOTAL}"
            for dim in [
                "downstream_outcome", "interpretation_tools", "replay_tools",
                "clarification", "authority", "appointment_deltas",
                "audit_deltas", "safety",
            ]
        },

        "current_two_repeats": {
            dim: f"{two_repeat_counts[dim]}/{two_repeat_total}"
            for dim in [
                "downstream_outcome", "interpretation_tools", "replay_tools",
                "clarification", "authority", "appointment_deltas",
                "audit_deltas", "safety",
            ]
        },

        "delta_vs_baseline_one_repeat": {
            dim: (
                f"+{one_repeat_counts[dim] - LC4R1_BASELINE[dim]}"
                if one_repeat_counts[dim] >= LC4R1_BASELINE[dim]
                else f"{one_repeat_counts[dim] - LC4R1_BASELINE[dim]}"
            )
            for dim in [
                "downstream_outcome", "interpretation_tools", "replay_tools",
                "clarification", "authority", "appointment_deltas",
                "audit_deltas", "safety",
            ]
        },

        "baseline_lc4r1_semantic_fields": {
            field: f"{LC4R1_SEMANTIC_BASELINE[field]}/{LC4_TOTAL}"
            for field in [
                "intended_action", "action_semantics", "temporal_relation",
                "normalized_values", "entity_semantics", "clarification",
            ]
        },

        "current_one_repeat_semantic_fields": {
            field: f"{semantic_passes[field]}/{LC4_TOTAL}"
            for field in [
                "intended_action", "action_semantics", "temporal_relation",
                "normalized_values", "entity_semantics", "clarification",
            ]
        },

        "delta_vs_baseline_semantic_fields": {
            field: (
                f"+{semantic_passes[field] - LC4R1_SEMANTIC_BASELINE[field]}"
                if semantic_passes[field] >= LC4R1_SEMANTIC_BASELINE[field]
                else f"{semantic_passes[field] - LC4R1_SEMANTIC_BASELINE[field]}"
            )
            for field in [
                "intended_action", "action_semantics", "temporal_relation",
                "normalized_values", "entity_semantics", "clarification",
            ]
        },

        "semantic_fields": {
            "passed": semantic_passes.get("intended_action", 0),
            "total": LC4_TOTAL,
            "field_passes": semantic_passes,
            "baseline_field_passes": LC4R1_SEMANTIC_BASELINE,
        },

        "candidate_quality": audit.category_counts(),
        "aligned_subset_scores": audit.aligned_subset_scores(),
        "per_rule_counts": rule_counts,
        "total_candidates": audit.total_candidates,
        "total_candidate_samples": audit.total_samples,

        "dimension_attribution": dim_attr,

        "conflict_examples": conflict_examples,
        "conflict_example_count": len(conflict_examples),

        "provenance_adjudication_counts": {
            "silver_pending": audit.total_candidates,
            "gold_adjudicated": 0,
            "lc2_silver_pending": lc2_audit.total_candidates,
        },

        "repeat_variance": {
            "one_repeat": 0,
            "two_repeats": audit.variance_count,
        },
    }

    # Compute deterministic report hash
    report_hash = _compute_report_hash(report)
    report["report_hash"] = report_hash

    return report


def main() -> None:
    check_mode = "--check" in sys.argv

    report = _compute_report()
    report_json = json.dumps(report, indent=2, default=str, sort_keys=True) + "\n"

    if check_mode:
        if REPORT_PATH.exists():
            existing = REPORT_PATH.read_text(encoding="utf-8")
            if existing != report_json:
                print("REPORT DRIFT DETECTED", file=sys.stderr)
                print("  Existing report differs from in-memory computation.", file=sys.stderr)
                print("  Regenerate with: python scripts/bernie_lc4r_development_gap_report.py", file=sys.stderr)
                sys.exit(1)
            print("Report check passed -- in-memory computation matches stored report.")
        else:
            print(f"Report file not found at {REPORT_PATH} -- nothing to check.", file=sys.stderr)
            sys.exit(1)
    else:
        REPORT_PATH.write_text(report_json, encoding="utf-8")
        print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
