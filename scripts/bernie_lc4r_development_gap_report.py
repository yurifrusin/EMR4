"""LC4R2 development gap report — candidate-quality firewall.

Usage:
    python scripts/bernie_lc4r_development_gap_report.py          # write report
    python scripts/bernie_lc4r_development_gap_report.py --check  # verify in memory only

Output:
    docs/bernie-lc4r-development-gap-report.json (deterministic, write mode only)
"""

from __future__ import annotations

import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

from app.services.bernie.composed_corpus_evaluator import (
    evaluate_corpus,
    load_lc2_candidates,
)
from app.services.bernie.development_gap_audit import audit_candidates

REPORT_PATH = _HERE / "docs" / "bernie-lc4r-development-gap-report.json"


def _compute_report() -> dict:
    """Compute the full development gap report."""
    # 1. Run the standard corpus evaluation for baseline metrics
    corpus_report = evaluate_corpus()
    per_dim = corpus_report["per_dimension"]

    # 2. Run candidate-quality audit over Silver/pending candidates
    candidates = load_lc2_candidates()
    audit = audit_candidates(candidates, num_repeats=2)

    # 3. Build gap report
    report: dict[str, object] = {
        "schema_version": "lc4r2.development_gap_report.v1",
        "development_only": True,
        "no_holdout_accessed": True,
        "corpus_manifest": {
            "scenario_count": per_dim["scenario_count"],
            "sample_count": per_dim["sample_count"],
            "repeats_per_scenario": per_dim["repeats_per_scenario"],
            "provenance": "silver",
            "adjudication": "pending",
        },
        "baseline_dimensions": {
            "complete": 0,
            "downstream_outcome": {
                "passed": per_dim["downstream_outcome"]["passed"],
                "failed": per_dim["downstream_outcome"]["failed"],
                "total": per_dim["downstream_outcome"]["total"],
            },
            "interpretation_tools": {
                "passed": per_dim["interpretation_tools"]["passed"],
                "failed": per_dim["interpretation_tools"]["failed"],
                "total": per_dim["interpretation_tools"]["total"],
            },
            "replay_tools": {
                "passed": per_dim["replay_tool_sequence"]["passed"],
                "failed": per_dim["replay_tool_sequence"]["failed"],
                "total": per_dim["replay_tool_sequence"]["total"],
            },
            "clarification": {
                "passed": per_dim["clarification"]["passed"],
                "failed": per_dim["clarification"]["failed"],
                "total": per_dim["clarification"]["total"],
            },
            "authority": {
                "passed": per_dim["authority"]["passed"],
                "failed": per_dim["authority"]["failed"],
                "total": per_dim["authority"]["total"],
            },
            "appointment_deltas": {
                "passed": per_dim["appointment_deltas"]["passed"],
                "failed": per_dim["appointment_deltas"]["failed"],
                "total": per_dim["appointment_deltas"]["total"],
            },
            "audit_deltas": {
                "passed": per_dim["audit_deltas"]["passed"],
                "failed": per_dim["audit_deltas"]["failed"],
                "total": per_dim["audit_deltas"]["total"],
            },
            "safety": {
                "passed": per_dim["safety"]["passed"],
                "failed": per_dim["safety"]["failed"],
                "total": per_dim["safety"]["total"],
            },
        },
        "candidate_quality": audit.category_counts(),
        "aligned_subset_scores": audit.aligned_subset_scores(),
        "total_candidates": audit.total_candidates,
        "total_samples": audit.total_samples,
        "corpus_hash": audit.corpus_hash,
        "conflict_examples": [
            {
                "rule_id": r.rule_id,
                "candidate_id": r.candidate_id,
                "category": r.category,
                "observed_value": r.observed_value,
                "expected_value": r.expected_value,
            }
            for r in audit.conflict_records
        ],
        "conflict_example_count": len(audit.conflict_records),
        "provenance_adjudication_counts": {
            "silver_pending": len(candidates),
            "gold_adjudicated": 0,
        },
    }
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
