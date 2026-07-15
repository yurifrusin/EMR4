"""Build and verify the LC4R10 development-only reconciliation report."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import tempfile
from collections import defaultdict
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
    score_interpretation_replay_pair,
)
from app.services.bernie.scale_corpus import (
    DevelopmentOnlyLoader,
    LC4R10_RECONCILIATION_HASH,
    LC4R10_RECONCILIATION_IDS,
    LC4R10_REPLAY_HASH,
    LC4R10_REPLAY_IDS,
    LC4R10_RESOLVED_CLARIFICATION_HASH,
    LC4R10_RESOLVED_CLARIFICATION_IDS,
    generate_development_fixture,
)
from app.services.bernie.scaled_evaluator import (
    generate_scaled_evaluation_report,
)


DEV_FIXTURES = ROOT / "tests" / "fixtures" / "bernie_lc4_development"
CLARIFICATION_AUDIT = (
    ROOT / "docs" / "bernie-lc4r8-clarification-decision-surface.json"
)
REPLAY_AUDIT = ROOT / "docs" / "bernie-lc4r8-replay-contract-audit.json"
REPORT_PATH = ROOT / "docs" / "bernie-lc4r10-report.json"

EXPECTED_SEMANTIC_COUNTS = {
    "intended_action": 880,
    "action_semantics": 814,
    "temporal_relation": 672,
    "normalized_values": 154,
    "entity_semantics": 330,
    "requires_clarification": 835,
}
EXPECTED_ACTION_HASHES = {
    "create": "1839c8c567e44922",
    "move": "ec7e009f37f0834a",
    "resize": "e49785ce6f8922e5",
    "cancel": "830386f883de7fd0",
}
EXPECTED_REPLAY_SUBSETS = {
    "resolved_reversal_no_outcome": (1, "020fade8ca644684"),
    "resolved_correction_candidate_selection": (1, "d67780b27dbfbdca"),
    "valid_create_policy_alignment": (14, "e79a4ecc777b9f9c"),
    "fail_closed_no_outcome_contract": (24, "2913bfd9110af319"),
}
EXPECTED_CLARIFICATION_OUTCOMES = {
    "action_outcome": (22, "e9b8e74b01d3ffc6"),
    "fail_closed_no_outcome": (31, "73229d3e6f4a355c"),
}


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _selection_hash(scenario_ids: set[str] | frozenset[str]) -> str:
    return hashlib.sha256(
        "\n".join(sorted(scenario_ids)).encode("utf-8")
    ).hexdigest()[:16]


def _audit_selections() -> tuple[set[str], set[str]]:
    clarification_ids = {
        record["scenario_id"]
        for record in _load_json(CLARIFICATION_AUDIT)["records"]
    }
    replay_ids = {
        record["scenario_id"]
        for record in _load_json(REPLAY_AUDIT)["records"]
        if record["blocker_class"] != "audit_change_type_vocabulary_only"
    }
    return clarification_ids, replay_ids


def _dimension_counts(results: list[Any]) -> dict[str, int]:
    counts = {
        "all_passed": sum(result.all_passed for result in results),
    }
    for name in (
        "intended_action",
        "action_semantics",
        "temporal_relation",
        "normalized_values",
        "entity_semantics",
        "clarification",
    ):
        counts[f"semantic_{name}"] = sum(
            getattr(result.semantic_fields, name).passed for result in results
        )
    for name in (
        "downstream_outcome",
        "tool_sequence",
        "interpretation_tools",
        "authority",
        "clarification",
        "appointment_deltas",
        "audit_deltas",
        "safety",
    ):
        counts[name] = sum(getattr(result, name).passed for result in results)
    return counts


def build_report() -> dict[str, Any]:
    clarification_audit_ids, replay_audit_ids = _audit_selections()
    corpus = DevelopmentOnlyLoader(DEV_FIXTURES).load_all()
    scenarios = {
        scenario.scenario_id: scenario
        for group in corpus.groups
        for scenario in group.all_variants
    }

    selected_results = []
    for scenario_id in sorted(LC4R10_RECONCILIATION_IDS):
        scenario = scenarios[scenario_id]
        interpretation = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interpretation)
        selected_results.append(
            score_interpretation_replay_pair(
                scenario, interpretation, replay
            )
        )

    replay_subsets: dict[str, set[str]] = defaultdict(set)
    for scenario_id in LC4R10_REPLAY_IDS:
        scenario = scenarios[scenario_id]
        if scenario_id.endswith("_001_03"):
            key = "resolved_reversal_no_outcome"
        elif scenario_id.endswith("_003_02"):
            key = "resolved_correction_candidate_selection"
        elif scenario.diary_state in {"same_day_distinct", "terminal"}:
            key = "valid_create_policy_alignment"
        else:
            key = "fail_closed_no_outcome_contract"
        replay_subsets[key].add(scenario_id)

    action_subsets: dict[str, set[str]] = defaultdict(set)
    outcome_subsets: dict[str, set[str]] = defaultdict(set)
    for scenario_id in LC4R10_RESOLVED_CLARIFICATION_IDS:
        scenario = scenarios[scenario_id]
        action_subsets[scenario.intended_action].add(scenario_id)
        outcome_key = (
            "action_outcome"
            if scenario.expected_outcome_kind is not None
            else "fail_closed_no_outcome"
        )
        outcome_subsets[outcome_key].add(scenario_id)

    scaled = generate_scaled_evaluation_report(DEV_FIXTURES)
    per_dimension = scaled["per_dimension"]
    semantic_counts = {
        key: value["passed"] // 2
        for key, value in per_dimension["semantic_fields"].items()
    }
    selected_null_outcomes = [
        scenarios[scenario_id]
        for scenario_id in LC4R10_RECONCILIATION_IDS
        if scenarios[scenario_id].expected_outcome_kind is None
    ]

    assertions = {
        "clarification_audit_matches_source_selection": (
            clarification_audit_ids
            == set(LC4R10_RESOLVED_CLARIFICATION_IDS)
        ),
        "replay_audit_matches_source_selection": (
            replay_audit_ids == set(LC4R10_REPLAY_IDS)
        ),
        "combined_selection_is_disjoint_93": (
            not clarification_audit_ids.intersection(replay_audit_ids)
            and len(LC4R10_RECONCILIATION_IDS) == 93
        ),
        "all_93_contracts_pass": all(
            result.all_passed for result in selected_results
        ),
        "explicit_null_outcomes_have_zero_expected_deltas": all(
            not scenario.expected_appointment_deltas
            and not scenario.expected_audit_deltas
            for scenario in selected_null_outcomes
        ),
        "semantic_counts_match": semantic_counts == EXPECTED_SEMANTIC_COUNTS,
        "safety_1152_of_1152": (
            per_dimension["safety"]["passed"] == 2304
            and per_dimension["safety"]["failed"] == 0
        ),
        "variance_zero_over_2304": (
            scaled["variance"]["variant_sample_count"] == 0
            and scaled["variance"]["all_samples_deterministic"] is True
            and per_dimension["sample_count"] == 2304
        ),
    }

    report = {
        "schema_version": "bernie.lc4r10.contract_reconciliation.v1",
        "development_only": True,
        "silver_pending_only": True,
        "corpus_hash": corpus.corpus_hash,
        "selections": {
            "clarification": {
                "count": len(clarification_audit_ids),
                "hash": _selection_hash(clarification_audit_ids),
                "expected_hash": LC4R10_RESOLVED_CLARIFICATION_HASH,
            },
            "replay": {
                "count": len(replay_audit_ids),
                "hash": _selection_hash(replay_audit_ids),
                "expected_hash": LC4R10_REPLAY_HASH,
            },
            "combined": {
                "count": len(LC4R10_RECONCILIATION_IDS),
                "hash": _selection_hash(LC4R10_RECONCILIATION_IDS),
                "expected_hash": LC4R10_RECONCILIATION_HASH,
            },
        },
        "replay_subsets": {
            key: {
                "count": len(ids),
                "hash": _selection_hash(ids),
                "expected_count": EXPECTED_REPLAY_SUBSETS[key][0],
                "expected_hash": EXPECTED_REPLAY_SUBSETS[key][1],
            }
            for key, ids in sorted(replay_subsets.items())
        },
        "resolved_clarification_actions": {
            key: {
                "count": len(ids),
                "hash": _selection_hash(ids),
                "expected_hash": EXPECTED_ACTION_HASHES[key],
            }
            for key, ids in sorted(action_subsets.items())
        },
        "resolved_clarification_outcomes": {
            key: {
                "count": len(ids),
                "hash": _selection_hash(ids),
                "expected_count": EXPECTED_CLARIFICATION_OUTCOMES[key][0],
                "expected_hash": EXPECTED_CLARIFICATION_OUTCOMES[key][1],
            }
            for key, ids in sorted(outcome_subsets.items())
        },
        "corrected_contract_results": {
            "scenario_count": len(selected_results),
            "dimension_pass_counts": _dimension_counts(selected_results),
            "explicit_null_outcome_count": len(selected_null_outcomes),
        },
        "development_baseline": {
            "scenario_count": per_dimension["scenario_count"],
            "semantic_pass_counts_single_repeat": semantic_counts,
            "safety": {"passed": 1152, "failed": 0, "total": 1152},
            "variance": {
                "variant_samples": scaled["variance"]["variant_sample_count"],
                "total_samples": per_dimension["sample_count"],
            },
        },
        "protected_boundary": {
            "holdout_v1_accessed": False,
            "holdout_v1_reused": False,
            "historical_diary_material_accessed": False,
            "provider_calls": False,
            "runtime_or_database_writes": False,
            "t3_1_to_t3_4": "preserved_blocked_by_default",
            "t3_5": "deferred",
        },
        "assertions": assertions,
        "all_assertions_passed": all(assertions.values()),
    }
    return report


def generator_is_reproducible() -> bool:
    with tempfile.TemporaryDirectory(prefix="bernie-lc4r10-") as tmp:
        generated = pathlib.Path(tmp)
        generate_development_fixture(generated)
        expected_names = sorted(path.name for path in DEV_FIXTURES.glob("*.json"))
        observed_names = sorted(path.name for path in generated.glob("*.json"))
        if expected_names != observed_names:
            return False
        return all(
            (DEV_FIXTURES / name).read_bytes() == (generated / name).read_bytes()
            for name in expected_names
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        REPORT_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    if args.check:
        if not report["all_assertions_passed"]:
            raise SystemExit("LC4R10 report assertions failed")
        if not generator_is_reproducible():
            raise SystemExit("LC4R10 generator reproducibility failed")
        if not REPORT_PATH.is_file() or REPORT_PATH.read_text(
            encoding="utf-8"
        ) != rendered:
            raise SystemExit("LC4R10 committed report drift")
        print("LC4R10 contract reconciliation: PASS")
    elif not args.write:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
