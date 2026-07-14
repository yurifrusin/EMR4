"""LC4 development corpus — reproducible manifest and coverage report.

Usage:
    python scripts/bernie_lc4_development_report.py          # write report
    python scripts/bernie_lc4_development_report.py --check  # verify in memory only

Output:
    docs/bernie-lc4-development-report.json (deterministic, write mode only)
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

_HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

from app.services.bernie.scale_corpus import (
    DEVELOPMENT_GROUP_COUNT,
    TOTAL_SURFACE_VARIANTS,
    TOTAL_TRAJECTORIES,
    TOTAL_INDIVIDUAL_RECORDS,
    ALL_ACTIONS,
    ALL_TEMPORAL_RELATIONS,
    ALL_DIARY_STATES,
    ALL_ENTITY_SEMANTICS,
    ALL_DIALOGUE_FORMS,
    ALL_LANGUAGE_FORMS,
    DevelopmentOnlyLoader,
    validate_corpus,
    GAP_PRIORITY_MINIMUM,
)

REPORT_PATH = _HERE / "docs" / "bernie-lc4-development-report.json"


def _compute_report() -> dict:
    """Compute the report in memory and return the dict."""
    fixture_dir = _HERE / "tests" / "fixtures" / "bernie_lc4_development"
    loader = DevelopmentOnlyLoader(fixture_dir)
    corpus = loader.load_all()

    # Validate
    errors = validate_corpus(corpus)
    if errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    # Coverage counts
    action_counts: dict[str, int] = {}
    temporal_counts: dict[str, int] = {}
    diary_state_counts: dict[str, int] = {}
    entity_sem_counts: dict[str, int] = {}
    dialogue_form_counts: dict[str, int] = {}
    language_form_counts: dict[str, int] = {}
    gap_target_counts: dict[str, int] = {}

    for g in corpus.groups:
        a = g.spec.intended_action
        action_counts[a] = action_counts.get(a, 0) + 1

        t = g.spec.temporal_relation
        temporal_counts[t] = temporal_counts.get(t, 0) + 1

        ds = g.spec.diary_state
        diary_state_counts[ds] = diary_state_counts.get(ds, 0) + 1

        es = g.spec.entity_state
        entity_sem_counts[es] = entity_sem_counts.get(es, 0) + 1

        df = g.spec.dialogue_form
        dialogue_form_counts[df] = dialogue_form_counts.get(df, 0) + 1

        lf = g.spec.language_form
        language_form_counts[lf] = language_form_counts.get(lf, 0) + 1

        for target in g.spec.gap_targets:
            gap_target_counts[target] = gap_target_counts.get(target, 0) + 1

    # Check all dimensions covered
    dimensions_covered = {
        "actions": {a: action_counts.get(a, 0) >= 1 for a in ALL_ACTIONS},
        "temporal_relations": {t: temporal_counts.get(t, 0) >= 1 for t in ALL_TEMPORAL_RELATIONS},
        "diary_states": {s: diary_state_counts.get(s, 0) >= 1 for s in ALL_DIARY_STATES},
        "entity_semantics": {e: entity_sem_counts.get(e, 0) >= 1 for e in ALL_ENTITY_SEMANTICS},
        "dialogue_forms": {d: dialogue_form_counts.get(d, 0) >= 1 for d in ALL_DIALOGUE_FORMS},
        "language_forms": {l: language_form_counts.get(l, 0) >= 1 for l in ALL_LANGUAGE_FORMS},
    }

    report: dict = {
        "schema_version": "lc4.development_report.v2",
        "generated_at": None,
        "corpus_manifest": {
            "development_group_count": len(corpus.groups),
            "surface_variant_count": TOTAL_SURFACE_VARIANTS,
            "multi_turn_trajectory_count": TOTAL_TRAJECTORIES,
            "total_individual_records": TOTAL_INDIVIDUAL_RECORDS,
            "corpus_hash": corpus.corpus_hash,
            "provenance": "silver",
            "adjudication": "pending",
            "generator_identity": {
                "provider_id": "deepseek",
                "model_id": "deepseek-v4-flash",
                "instance_id": "lc4-dw1",
            },
        },
        "coverage": {
            "action": action_counts,
            "temporal_relation": temporal_counts,
            "diary_state": diary_state_counts,
            "entity_semantics": entity_sem_counts,
            "dialogue_form": dialogue_form_counts,
            "language_form": language_form_counts,
            "gap_targets": gap_target_counts,
        },
        "dimensions_covered": dimensions_covered,
        "gap_priority": {
            "minimum_required": GAP_PRIORITY_MINIMUM,
            "actual_gap_priority_groups": corpus.gap_priority_group_count,
            "met": corpus.gap_priority_group_count >= GAP_PRIORITY_MINIMUM,
        },
        "action_min_12": {
            "required_per_action": 12,
            "met": all(c >= 12 for c in action_counts.values()),
            "actual": action_counts,
        },
        "temporal_min_12": {
            "required_per_temporal": 12,
            "met": all(c >= 12 for c in temporal_counts.values()),
            "actual": temporal_counts,
        },
        "validation_errors": errors,
    }
    return report


def main() -> None:
    check_mode = "--check" in sys.argv

    report = _compute_report()
    report_json = json.dumps(report, indent=2, default=str) + "\n"

    if check_mode:
        # --check: compute in memory, compare exact bytes, fail on drift, no write
        if REPORT_PATH.exists():
            existing = REPORT_PATH.read_text(encoding="utf-8")
            if existing != report_json:
                print("REPORT DRIFT DETECTED", file=sys.stderr)
                print("  Existing report differs from in-memory computation.", file=sys.stderr)
                print("  Regenerate with: python scripts/bernie_lc4_development_report.py", file=sys.stderr)
                sys.exit(1)
            print("Report check passed — in-memory computation matches stored report.")
        else:
            print(f"Report file not found at {REPORT_PATH} — nothing to check.", file=sys.stderr)
            sys.exit(1)
    else:
        # Write mode (default)
        REPORT_PATH.write_text(report_json, encoding="utf-8")
        print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
