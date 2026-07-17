"""Unchanged-product robustness evaluation for admitted synthetic Silver v2."""

from __future__ import annotations

from collections import Counter, defaultdict
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
from app.services.bernie.scenario_spec import ReceptionScenarioSpec
from app.services.bernie.synthetic_noise_robustness import (
    DIAGNOSTIC_PRIORITY,
    _dimension_records,
    _observation_fingerprint,
)
from app.services.bernie.synthetic_noise_v2_candidates import (
    DEFAULT_ADMISSION_PATH_V2,
    DEFAULT_CANDIDATE_PATH_V2,
    build_v2_candidate_artifacts,
    candidate_records_hash,
    load_jsonl,
)


REPORT_SCHEMA_VERSION_V2 = "emr4.bernie.synthetic_noise_robustness.v2"
DEFAULT_REPORT_PATH_V2 = Path(
    "docs/bernie-synthetic-silver-v2-robustness-baseline.json"
)
REPEATS_V2 = 2


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def _candidate_scenario(
    candidate: dict[str, Any], anchor: dict[str, Any]
) -> ReceptionScenarioSpec:
    contract = anchor["semantic_contract"]
    form = anchor["dialogue_form_contract"]["dialogue_form"]
    payload = {
        "spec_version": "lc1.v1",
        "scenario_id": candidate["candidate_id"],
        "provenance": "silver",
        "adjudication": "pending",
        "family": "synthetic_silver_v2_robustness",
        "description": f"Admitted coherent synthetic Silver v2 candidate {candidate['candidate_id']}",
        "dialogue_turns": candidate["dialogue_turns"],
        "reference_date": contract["reference_date"],
        "clinic_clock": contract["clinic_clock"],
        "intended_action": contract["intended_action"],
        "action_semantics": contract["action_semantics"],
        "temporal_relation": contract["temporal_relation"],
        "earliest_time": contract["earliest_time"],
        "latest_time": contract["latest_time"],
        "normalized_values": contract["normalized_values"],
        "source_spans": candidate["evidence_spans"],
        "duration_minutes": contract["duration_minutes"],
        "practitioner_semantics": contract["practitioner_semantics"],
        "patient_semantics": contract["patient_semantics"],
        "location_semantics": contract["location_semantics"],
        "appointment_type_semantics": contract["appointment_type_semantics"],
        "duration_semantics": contract["duration_semantics"],
        "diary_state": contract["diary_state"],
        "entity_state": contract["entity_state"],
        "dialogue_form": "repeated" if form == "repeated_request" else form,
        "language_form": "speech_like" if candidate["noise_level"] == "high" else "abbreviation",
        "initial_diary_state": contract["initial_diary_state"],
        "expected_outcome_kind": contract["expected_outcome_kind"],
        "expected_tool_sequence": contract["expected_tool_sequence"],
        "expected_appointment_deltas": contract["expected_appointment_deltas"],
        "expected_audit_deltas": contract["expected_audit_deltas"],
        "forbidden_outcomes": contract["forbidden_outcomes"],
        "forbidden_tool_calls": contract["forbidden_tool_calls"],
        "expected_clarification": contract["expected_clarification"],
        "clarification_choices": contract["clarification_choices"],
    }
    return ReceptionScenarioSpec.model_validate(payload)


def build_v2_evaluation_scenarios() -> list[
    tuple[dict[str, Any], dict[str, Any], ReceptionScenarioSpec]
]:
    manifest, expected, expected_admission = build_v2_candidate_artifacts()
    records = load_jsonl(DEFAULT_CANDIDATE_PATH_V2)
    admission = json.loads(DEFAULT_ADMISSION_PATH_V2.read_text(encoding="utf-8"))
    if records != expected or admission != expected_admission:
        raise ValueError("committed v2 candidate/admission binding drift")
    if admission["canonical_candidate_hash"] != candidate_records_hash(records):
        raise ValueError("v2 admission candidate hash mismatch")
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    selected = set(admission["accepted_candidate_ids"])
    evaluation = [
        (candidate, anchors[candidate["source_seed_id"]], _candidate_scenario(candidate, anchors[candidate["source_seed_id"]]))
        for candidate in records
        if candidate["candidate_id"] in selected
    ]
    if len(evaluation) != admission["accepted_count"]:
        raise ValueError("v2 evaluation population does not match admission")
    return evaluation


def build_v2_robustness_report() -> dict[str, Any]:
    evaluation = build_v2_evaluation_scenarios()
    dimension_counts: dict[str, Counter[str]] = defaultdict(Counter)
    primary_counts: Counter[str] = Counter()
    fingerprints: dict[str, set[str]] = defaultdict(set)
    by_action: dict[str, Counter[str]] = defaultdict(Counter)
    by_form: dict[str, Counter[str]] = defaultdict(Counter)
    by_noise: dict[str, Counter[str]] = defaultdict(Counter)
    cases: list[dict[str, Any]] = []

    for candidate, anchor, scenario in evaluation:
        repeat_complete: list[bool] = []
        first_failures: list[dict[str, Any]] = []
        first_primary: str | None = None
        for sample_index in range(REPEATS_V2):
            interpretation = replace(
                deterministic_interpret(scenario), sample_index=sample_index
            )
            replay = deterministic_replay(scenario, interpretation)
            result = score_interpretation_replay_pair(scenario, interpretation, replay)
            fingerprints[candidate["candidate_id"]].add(_observation_fingerprint(result))
            dimensions = _dimension_records(scenario, result)
            failed_categories = {item["category"] for item in dimensions if not item["passed"]}
            for item in dimensions:
                dimension_counts[item["name"]]["passed" if item["passed"] else "failed"] += 1
            primary = next(
                (category for category in DIAGNOSTIC_PRIORITY if category in failed_categories),
                None,
            )
            if primary:
                primary_counts[primary] += 1
            if sample_index == 0:
                first_primary = primary
                first_failures = [item for item in dimensions if not item["passed"]]
            repeat_complete.append(result.all_passed)
        complete = all(repeat_complete)
        contract = anchor["semantic_contract"]
        form = anchor["dialogue_form_contract"]["dialogue_form"]
        outcome = "complete" if complete else "failed"
        by_action[contract["intended_action"]][outcome] += 1
        by_form[form][outcome] += 1
        by_noise[candidate["noise_level"]][outcome] += 1
        cases.append(
            {
                "candidate_id": candidate["candidate_id"],
                "source_seed_id": anchor["seed_id"],
                "intended_action": contract["intended_action"],
                "dialogue_form": form,
                "noise_level": candidate["noise_level"],
                "complete": complete,
                "primary_diagnostic_category": first_primary,
                "failed_dimensions": first_failures,
            }
        )

    variance_ids = sorted(
        candidate_id for candidate_id, values in fingerprints.items() if len(values) != 1
    )
    complete_count = sum(case["complete"] for case in cases)
    safety = dimension_counts["safety"]
    _, _, admission = build_v2_candidate_artifacts()
    without_hash = {
        "schema_version": REPORT_SCHEMA_VERSION_V2,
        "decision": (
            "baseline_complete"
            if len(cases) == admission["accepted_count"] and not variance_ids and safety["failed"] == 0
            else "revision_required"
        ),
        "input_bindings": {
            "anchor_manifest_hash": admission["anchor_manifest_hash"],
            "candidate_hash": admission["canonical_candidate_hash"],
            "admission_hash": admission["admission_hash"],
            "accepted_selection_hash": admission["accepted_selection_hash"],
        },
        "population": {
            "candidates": len(cases),
            "repeats_per_candidate": REPEATS_V2,
            "observations": len(cases) * REPEATS_V2,
            "complete_candidates": complete_count,
            "failed_candidates": len(cases) - complete_count,
        },
        "variance": {
            "variant_candidate_count": len(variance_ids),
            "variant_candidate_ids": variance_ids,
        },
        "safety": {
            "passed": safety["passed"],
            "failed": safety["failed"],
            "total": safety["passed"] + safety["failed"],
        },
        "dimension_counts": {
            name: {
                "passed": counts["passed"],
                "failed": counts["failed"],
                "total": counts["passed"] + counts["failed"],
            }
            for name, counts in sorted(dimension_counts.items())
        },
        "primary_diagnostic_category_observations": dict(sorted(primary_counts.items())),
        "breakdown": {
            "by_action": {key: dict(sorted(value.items())) for key, value in sorted(by_action.items())},
            "by_dialogue_form": {key: dict(sorted(value.items())) for key, value in sorted(by_form.items())},
            "by_noise_level": {key: dict(sorted(value.items())) for key, value in sorted(by_noise.items())},
        },
        "candidate_cases": cases,
        "boundaries": {
            "protected_holdout_access": False,
            "historical_diary_access": False,
            "external_corpus_access": False,
            "provider_access": False,
            "product_write": False,
            "bounded_parser_refinements_present": True,
            "policy_changes": False,
            "replay_changes": False,
            "scorer_changes": False,
        },
    }
    return {**without_hash, "report_hash": _sha256(without_hash)}


def write_v2_robustness_report(path: Path = DEFAULT_REPORT_PATH_V2) -> dict[str, Any]:
    report = build_v2_robustness_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def check_v2_robustness_report(path: Path = DEFAULT_REPORT_PATH_V2) -> list[str]:
    if not path.is_file():
        return ["missing v2 robustness report"]
    actual = json.loads(path.read_text(encoding="utf-8"))
    expected = build_v2_robustness_report()
    return [] if actual == expected else ["v2 robustness report does not regenerate exactly"]


__all__ = [
    "DEFAULT_REPORT_PATH_V2",
    "build_v2_evaluation_scenarios",
    "build_v2_robustness_report",
    "check_v2_robustness_report",
    "write_v2_robustness_report",
]
