"""Bounded evaluator for the synthetic Silver action/temporal tranche."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from typing import Any

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
)
from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
from app.services.bernie.synthetic_noise_robustness import (
    DIAGNOSTIC_PRIORITY,
    EXPECTED_CANDIDATE_HASH,
    EXPECTED_REPEATS,
    _dimension_records,
    _observation_fingerprint,
    _sha256,
    build_evaluation_scenarios,
)


SCHEMA_VERSION = "emr4.bernie.synthetic_noise_action_temporal_report.v1"
SELECTION_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/action_temporal_tranche.json"
)
BASELINE_REPORT_PATH = Path(
    "docs/bernie-synthetic-silver-action-temporal-tranche-baseline.json"
)
ROBUSTNESS_REPORT_PATH = Path(
    "docs/bernie-synthetic-silver-robustness-baseline-report.json"
)
SEMANTIC_EXTRACTION_PATH = Path("app/services/bernie/semantic_extraction.py")
TEMPORAL_PATH = Path("app/services/diary/temporal.py")
EXPECTED_ROBUSTNESS_REPORT_HASH = (
    "sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5"
)
EXPECTED_SELECTION_COUNTS = {
    "action_extraction": 12,
    "temporal_normalization": 10,
    "replay_control": 2,
}
EXPECTED_SELECTED_CANDIDATES = 24


def _file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_selection() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    if selection.get("decision") != "frozen_development_selection":
        raise ValueError("tranche selection is not frozen")
    if selection.get("candidate_canonical_hash") != EXPECTED_CANDIDATE_HASH:
        raise ValueError("tranche candidate hash drift")
    if any(selection.get("boundaries", {}).values()):
        raise ValueError("tranche selection opens a closed boundary")

    selected = selection.get("selected_candidates")
    if not isinstance(selected, list) or len(selected) != EXPECTED_SELECTED_CANDIDATES:
        raise ValueError("tranche must select exactly 24 candidates")
    ids = [item.get("candidate_id") for item in selected]
    if len(set(ids)) != len(ids) or any(not value for value in ids):
        raise ValueError("tranche candidate IDs must be unique and non-empty")
    lane_counts = Counter(item.get("lane") for item in selected)
    if dict(lane_counts) != EXPECTED_SELECTION_COUNTS:
        raise ValueError("tranche lane counts drift")

    robustness = json.loads(ROBUSTNESS_REPORT_PATH.read_text(encoding="utf-8"))
    if robustness.get("report_hash") != EXPECTED_ROBUSTNESS_REPORT_HASH:
        raise ValueError("accepted robustness report hash drift")
    without_hash = {
        key: value for key, value in robustness.items() if key != "report_hash"
    }
    if _sha256(without_hash) != EXPECTED_ROBUSTNESS_REPORT_HASH:
        raise ValueError("accepted robustness report does not self-verify")

    baseline_failures = {
        item["candidate_id"]: item for item in robustness["failure_cases"]
    }
    for item in selected:
        failure = baseline_failures.get(item["candidate_id"])
        if failure is None:
            raise ValueError(f"selected candidate was not a baseline failure: {item['candidate_id']}")
        expected_primary = (
            "replay_integration"
            if item["lane"] == "replay_control"
            else item["lane"]
        )
        if failure["primary_diagnostic_category"] != expected_primary:
            raise ValueError(f"selected candidate baseline category drift: {item['candidate_id']}")
    return selection, selected


def build_tranche_report(num_repeats: int = EXPECTED_REPEATS) -> dict[str, Any]:
    """Evaluate the frozen 24-candidate tranche without oracle leakage."""
    if num_repeats != EXPECTED_REPEATS:
        raise ValueError(f"tranche requires exactly {EXPECTED_REPEATS} repeats")

    selection, selected = _load_selection()
    evaluation = {
        candidate["candidate_id"]: (candidate, seed, scenario)
        for candidate, seed, scenario in build_evaluation_scenarios()
    }
    cases: list[dict[str, Any]] = []
    dimension_counts: dict[str, Counter[str]] = {}
    primary_counts: Counter[str] = Counter()
    variance_ids: list[str] = []

    for selected_item in selected:
        candidate_id = selected_item["candidate_id"]
        candidate, _seed, scenario = evaluation[candidate_id]
        fingerprints: set[str] = set()
        first_failed: list[dict[str, Any]] = []
        all_passed = True
        for sample_index in range(num_repeats):
            interpretation = replace(
                deterministic_interpret(scenario),
                sample_index=sample_index,
            )
            replay = deterministic_replay(scenario, interpretation)
            result = score_interpretation_replay_pair(
                scenario,
                interpretation,
                replay,
            )
            fingerprints.add(_observation_fingerprint(result))
            dimensions = _dimension_records(scenario, result)
            failed = [item for item in dimensions if not item["passed"]]
            all_passed = all_passed and not failed
            for dimension in dimensions:
                counts = dimension_counts.setdefault(
                    dimension["name"], Counter()
                )
                counts["passed" if dimension["passed"] else "failed"] += 1
            if sample_index == 0:
                first_failed = failed

        if len(fingerprints) != 1:
            variance_ids.append(candidate_id)
        failed_categories = {item["category"] for item in first_failed}
        primary = next(
            (
                category
                for category in DIAGNOSTIC_PRIORITY
                if category in failed_categories
            ),
            None,
        )
        if primary is not None:
            primary_counts[primary] += 1
        cases.append(
            {
                "candidate_id": candidate_id,
                "lane": selected_item["lane"],
                "selection_reason": selected_item["reason"],
                "intended_action": scenario.intended_action,
                "dialogue_form": scenario.dialogue_form,
                "noise_level": candidate["noise_level"],
                "complete": all_passed,
                "primary_diagnostic_category": primary,
                "failed_dimensions": {
                    item["name"]: {
                        "expected": item["expected"],
                        "observed": item["observed"],
                    }
                    for item in first_failed
                },
            }
        )

    complete = sum(case["complete"] for case in cases)
    safety_failures = dimension_counts["safety"]["failed"]
    decision = (
        "tranche_evaluation_complete"
        if len(cases) == EXPECTED_SELECTED_CANDIDATES
        and not variance_ids
        and safety_failures == 0
        else "revision_required"
    )
    report_without_hash = {
        "schema_version": SCHEMA_VERSION,
        "decision": decision,
        "evidence_tier": "development_silver_diagnostic_remediation",
        "input_bindings": {
            "selection_path": SELECTION_PATH.as_posix(),
            "selection_file_hash": _file_sha256(SELECTION_PATH),
            "selection_source_commit": selection["selection_source_commit"],
            "candidate_canonical_hash": selection["candidate_canonical_hash"],
            "accepted_robustness_report_hash": EXPECTED_ROBUSTNESS_REPORT_HASH,
            "semantic_extraction_file_hash": _file_sha256(SEMANTIC_EXTRACTION_PATH),
            "temporal_file_hash": _file_sha256(TEMPORAL_PATH),
        },
        "population": {
            "candidates": len(cases),
            "repeats_per_candidate": num_repeats,
            "observations": len(cases) * num_repeats,
            "complete_candidates": complete,
            "failed_candidates": len(cases) - complete,
        },
        "variance": {
            "variant_candidate_count": len(variance_ids),
            "variant_candidate_ids": sorted(variance_ids),
        },
        "dimension_counts": {
            name: {
                "passed": counts["passed"],
                "failed": counts["failed"],
                "total": counts["passed"] + counts["failed"],
            }
            for name, counts in sorted(dimension_counts.items())
        },
        "primary_diagnostic_candidate_counts": dict(sorted(primary_counts.items())),
        "cases": cases,
        "boundaries": {
            "protected_holdout_access": False,
            "historical_diary_access": False,
            "external_corpus_access": False,
            "provider_access": False,
            "product_write": False,
            "contains_source_utterances": False,
            "scorer_oracle_used_by_interpreter": False,
        },
    }
    return {
        **report_without_hash,
        "report_hash": _sha256(report_without_hash),
    }


def write_tranche_report(path: Path = BASELINE_REPORT_PATH) -> dict[str, Any]:
    report = build_tranche_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


__all__ = [
    "BASELINE_REPORT_PATH",
    "EXPECTED_SELECTED_CANDIDATES",
    "SELECTION_PATH",
    "build_tranche_report",
    "write_tranche_report",
]
