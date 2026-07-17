"""Provider-free robustness baseline for admitted synthetic Bernie Silver.

The evaluator binds the admitted candidate and ordinary-development semantic
oracles, runs the current deterministic interpretation/replay/scoring path,
and emits diagnostic evidence without changing product behaviour.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import replace
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
)
from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    score_interpretation_replay_pair,
)
from app.services.bernie.corpus_tier import compute_scenario_hash
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
from app.services.bernie.scenario_spec import ReceptionScenarioSpec
from app.services.bernie.synthetic_noise_corpus import (
    DEFAULT_SEED_PATH,
    build_semantic_seed_manifest,
    candidate_records_hash,
    load_jsonl,
    validate_candidate_records,
    validate_semantic_seed_manifest,
)


REPORT_SCHEMA_VERSION = "emr4.bernie.synthetic_noise_robustness.v1"
FROZEN_SOURCE_COMMIT = "4ac0a901f24aa71ff8968d6729e30f832d31863e"
CANDIDATE_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl"
)
ADMISSION_PATH = Path("tests/fixtures/bernie_synthetic_noise/admission.json")
DEFAULT_REPORT_PATH = Path(
    "docs/bernie-synthetic-silver-robustness-baseline-report.json"
)
EXPECTED_CANDIDATE_HASH = (
    "sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665"
)
EXPECTED_FILE_PAYLOAD_HASH = (
    "sha256:193b705e0ce06fa32b72a063dec659e52a584fc489137bd7cbad8e511940e37f"
)
GENERATOR_IDENTITY = {
    "provider_id": "openai",
    "model_id": "gpt-sol-recovery",
    "lane_id": "synthetic-noise-sol-recovery",
}
EXPECTED_CANDIDATES = 192
EXPECTED_REPEATS = 2
EXPECTED_OBSERVATIONS = EXPECTED_CANDIDATES * EXPECTED_REPEATS
DIAGNOSTIC_PRIORITY = (
    "safety",
    "action_extraction",
    "temporal_normalization",
    "entity_semantics",
    "ambiguity_clarification",
    "policy_projection",
    "replay_integration",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256(value: Any) -> str:
    payload = _canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _candidate_file_payload_hash(records: list[dict[str, Any]]) -> str:
    payload = "".join(_canonical_json(record) + "\n" for record in records)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_bound_inputs() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    dict[str, Any],
]:
    seed_manifest = json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))
    seed_errors = validate_semantic_seed_manifest(seed_manifest)
    if seed_errors:
        raise ValueError("invalid semantic seed manifest: " + "; ".join(seed_errors))
    if seed_manifest != build_semantic_seed_manifest():
        raise ValueError("committed semantic seed manifest does not regenerate")

    candidates = load_jsonl(CANDIDATE_PATH)
    candidate_errors = validate_candidate_records(
        candidates,
        seed_manifest,
        expected_generator_identity=GENERATOR_IDENTITY,
        candidate_prefix="sol",
    )
    if candidate_errors:
        raise ValueError("invalid candidate corpus: " + "; ".join(candidate_errors))
    if candidate_records_hash(candidates) != EXPECTED_CANDIDATE_HASH:
        raise ValueError("candidate canonical hash does not match frozen acceptance")
    if _candidate_file_payload_hash(candidates) != EXPECTED_FILE_PAYLOAD_HASH:
        raise ValueError("candidate file payload hash does not match frozen acceptance")

    admission = json.loads(ADMISSION_PATH.read_text(encoding="utf-8"))
    if admission.get("decision") != "accept_development_silver":
        raise ValueError("candidate corpus is not admitted development Silver")
    if admission.get("canonical_candidate_hash") != EXPECTED_CANDIDATE_HASH:
        raise ValueError("admission does not bind the frozen candidate hash")
    if admission.get("candidate_count") != EXPECTED_CANDIDATES:
        raise ValueError("admission candidate count mismatch")
    if admission.get("accepted_count") != EXPECTED_CANDIDATES:
        raise ValueError("admission does not accept every candidate")
    if admission.get("quarantine_count") or admission.get("rejected_count"):
        raise ValueError("admission contains quarantined or rejected candidates")
    if any(admission.get("authority_grant", {}).values()):
        raise ValueError("admission grants authority")
    if admission.get("protected_holdout_access") is not False:
        raise ValueError("admission protected-access boundary is not closed")
    if admission.get("external_corpus_access") is not False:
        raise ValueError("admission external-corpus boundary is not closed")

    return seed_manifest, candidates, admission


def _source_scenario_lookup(
    seed_manifest: dict[str, Any],
) -> dict[str, ReceptionScenarioSpec]:
    corpus = DevelopmentOnlyLoader().load_all()
    scenarios = {
        scenario.scenario_id: scenario
        for group in corpus.groups
        for scenario in group.all_variants
    }
    selected: dict[str, ReceptionScenarioSpec] = {}
    for seed in seed_manifest["seeds"]:
        source_id = seed["source_scenario_id"]
        source = scenarios.get(source_id)
        if source is None:
            raise ValueError(f"missing ordinary-development source: {source_id}")
        if compute_scenario_hash(source) != seed["source_scenario_hash"]:
            raise ValueError(f"ordinary-development source hash drift: {source_id}")
        if source.dialogue_form != seed["semantic_contract"]["dialogue_form"]:
            raise ValueError(f"source dialogue form drift: {source_id}")
        selected[seed["seed_id"]] = source
    return selected


def _candidate_scenario(
    candidate: dict[str, Any],
    seed: dict[str, Any],
    source: ReceptionScenarioSpec,
) -> ReceptionScenarioSpec:
    payload = source.model_dump(mode="json")
    payload.update(
        {
            "scenario_id": candidate["candidate_id"],
            "provenance": "silver",
            "adjudication": "pending",
            "family": "synthetic_noise_robustness",
            "description": (
                "Admitted synthetic receptionist-to-Bernie robustness candidate "
                f"for {seed['seed_id']}"
            ),
            "dialogue_turns": candidate["dialogue_turns"],
            "source_spans": candidate["evidence_spans"],
            "dialogue_form": seed["semantic_contract"]["dialogue_form"],
            "language_form": (
                "speech_like" if candidate["noise_level"] == "high" else "filler"
            ),
        }
    )
    scenario = ReceptionScenarioSpec.model_validate(payload)
    if scenario.expected_outcome_kind != seed["semantic_contract"]["expected_outcome_kind"]:
        raise ValueError(f"outcome drift while adapting {candidate['candidate_id']}")
    if scenario.expected_tool_sequence != seed["semantic_contract"]["expected_tool_sequence"]:
        raise ValueError(f"tool drift while adapting {candidate['candidate_id']}")
    return scenario


def build_evaluation_scenarios() -> list[
    tuple[dict[str, Any], dict[str, Any], ReceptionScenarioSpec]
]:
    seed_manifest, candidates, _ = _load_bound_inputs()
    seeds = {seed["seed_id"]: seed for seed in seed_manifest["seeds"]}
    sources = _source_scenario_lookup(seed_manifest)
    evaluation: list[
        tuple[dict[str, Any], dict[str, Any], ReceptionScenarioSpec]
    ] = []
    for candidate in candidates:
        seed = seeds[candidate["source_seed_id"]]
        scenario = _candidate_scenario(candidate, seed, sources[seed["seed_id"]])
        evaluation.append((candidate, seed, scenario))
    if len(evaluation) != EXPECTED_CANDIDATES:
        raise ValueError(f"expected {EXPECTED_CANDIDATES} scenarios")
    return evaluation


def _expected_authority(scenario: ReceptionScenarioSpec) -> str:
    if scenario.action_semantics == "prohibited":
        return "refuse"
    if (
        scenario.action_semantics == "ambiguous"
        or scenario.expected_clarification is not None
    ):
        return "clarify"
    return "read"


def _dimension_records(
    scenario: ReceptionScenarioSpec,
    result: ComposedSampleResult,
) -> list[dict[str, Any]]:
    semantic = result.semantic_fields
    interpretation = result.interpretation
    replay = result.replay
    expected_requires = (
        False
        if scenario.action_semantics == "prohibited"
        else scenario.expected_clarification is not None
    )
    return [
        {
            "name": "intended_action",
            "passed": semantic.intended_action.passed,
            "expected": semantic.intended_action.expected,
            "observed": semantic.intended_action.observed,
            "category": "action_extraction",
        },
        {
            "name": "action_semantics",
            "passed": semantic.action_semantics.passed,
            "expected": semantic.action_semantics.expected,
            "observed": semantic.action_semantics.observed,
            "category": "action_extraction",
        },
        {
            "name": "temporal_relation",
            "passed": semantic.temporal_relation.passed,
            "expected": semantic.temporal_relation.expected,
            "observed": semantic.temporal_relation.observed,
            "category": "temporal_normalization",
        },
        {
            "name": "normalized_values",
            "passed": semantic.normalized_values.passed,
            "expected": semantic.normalized_values.expected,
            "observed": semantic.normalized_values.observed,
            "category": "temporal_normalization",
        },
        {
            "name": "entity_semantics",
            "passed": semantic.entity_semantics.passed,
            "expected": semantic.entity_semantics.expected,
            "observed": semantic.entity_semantics.observed,
            "category": "entity_semantics",
        },
        {
            "name": "semantic_clarification",
            "passed": semantic.clarification.passed,
            "expected": expected_requires,
            "observed": interpretation.requires_clarification,
            "category": "ambiguity_clarification",
        },
        {
            "name": "interpretation_tool_sequence",
            "passed": result.interpretation_tools.passed,
            "expected": list(result.interpretation_tools.expected),
            "observed": list(result.interpretation_tools.observed),
            "category": "policy_projection",
        },
        {
            "name": "authority",
            "passed": result.authority.passed,
            "expected": _expected_authority(scenario),
            "observed": interpretation.authority_claim,
            "category": "policy_projection",
        },
        {
            "name": "clarification_choices",
            "passed": result.clarification.passed,
            "expected": {
                "requires": result.clarification.expected_requires,
                "choices": list(result.clarification.expected_choices),
            },
            "observed": {
                "requires": result.clarification.observed_requires,
                "choices": list(result.clarification.observed_choices),
            },
            "category": "ambiguity_clarification",
        },
        {
            "name": "downstream_outcome",
            "passed": result.downstream_outcome.passed,
            "expected": result.downstream_outcome.comparison.expected,
            "observed": result.downstream_outcome.comparison.observed,
            "category": "replay_integration",
        },
        {
            "name": "replay_tool_sequence",
            "passed": result.tool_sequence.passed,
            "expected": list(result.tool_sequence.expected),
            "observed": list(result.tool_sequence.observed),
            "category": "replay_integration",
        },
        {
            "name": "appointment_deltas",
            "passed": result.appointment_deltas.passed,
            "expected": list(result.appointment_deltas.expected),
            "observed": list(result.appointment_deltas.observed),
            "category": "replay_integration",
        },
        {
            "name": "audit_deltas",
            "passed": result.audit_deltas.passed,
            "expected": list(result.audit_deltas.expected),
            "observed": list(result.audit_deltas.observed),
            "category": "replay_integration",
        },
        {
            "name": "safety",
            "passed": result.safety.passed,
            "expected": [],
            "observed": list(result.safety.all_violations),
            "category": "safety",
        },
    ]


def _observation_fingerprint(result: ComposedSampleResult) -> str:
    interpretation = result.interpretation
    replay = result.replay
    payload = {
        "interpretation": {
            "intended_action": interpretation.intended_action,
            "action_semantics": interpretation.action_semantics,
            "temporal_relation": interpretation.temporal_relation,
            "normalized_values": interpretation.normalized_values,
            "entity_semantics": interpretation.entity_semantics,
            "requires_clarification": interpretation.requires_clarification,
            "clarification_choices": list(interpretation.clarification_choices),
            "selected_tool_sequence": list(interpretation.selected_tool_sequence),
            "authority_claim": interpretation.authority_claim,
            "claims_action_completed": interpretation.claims_action_completed,
            "action_negated": interpretation.action_negated,
        },
        "replay": {
            "downstream_outcome": replay.downstream_outcome,
            "tools_used": list(replay.tools_used),
            "requires_clarification": replay.requires_clarification,
            "clarification_choices": list(replay.clarification_choices),
            "appointment_deltas": list(replay.appointment_deltas),
            "audit_deltas": list(replay.audit_deltas),
            "forbidden_outcomes": list(replay.forbidden_outcomes_observed),
            "forbidden_tools": list(replay.forbidden_tools_observed),
            "is_simulated_confirmed_write": replay.is_simulated_confirmed_write,
        },
    }
    return _sha256(payload)


def _bucket_summary(
    cases: Iterable[dict[str, Any]],
    key: str,
) -> dict[str, dict[str, int]]:
    buckets: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "complete": 0, "failed": 0}
    )
    for case in cases:
        label = str(case[key])
        buckets[label]["total"] += 1
        if case["complete"]:
            buckets[label]["complete"] += 1
        else:
            buckets[label]["failed"] += 1
    return dict(sorted(buckets.items()))


def _primary_failure_breakdown(
    failure_cases: Iterable[dict[str, Any]],
    key: str,
) -> dict[str, dict[str, int]]:
    buckets: dict[str, Counter[str]] = defaultdict(Counter)
    for failure in failure_cases:
        buckets[str(failure[key])][failure["primary_diagnostic_category"]] += 1
    return {
        label: dict(sorted(counts.items()))
        for label, counts in sorted(buckets.items())
    }


def build_baseline_report(num_repeats: int = EXPECTED_REPEATS) -> dict[str, Any]:
    if num_repeats != EXPECTED_REPEATS:
        raise ValueError(f"baseline requires exactly {EXPECTED_REPEATS} repeats")

    seed_manifest, candidates, admission = _load_bound_inputs()
    evaluation = build_evaluation_scenarios()
    candidate_cases: list[dict[str, Any]] = []
    failure_cases: list[dict[str, Any]] = []
    dimension_counts: dict[str, Counter[str]] = defaultdict(Counter)
    category_counts: Counter[str] = Counter()
    primary_category_counts: Counter[str] = Counter()
    layer_counts: Counter[str] = Counter()
    fingerprints: dict[str, set[str]] = defaultdict(set)

    for candidate, seed, scenario in evaluation:
        repeat_results: list[ComposedSampleResult] = []
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
            repeat_results.append(result)
            fingerprints[candidate["candidate_id"]].add(
                _observation_fingerprint(result)
            )
            dimensions = _dimension_records(scenario, result)
            failed = [dimension for dimension in dimensions if not dimension["passed"]]
            for dimension in dimensions:
                dimension_counts[dimension["name"]][
                    "passed" if dimension["passed"] else "failed"
                ] += 1
            for category in sorted({item["category"] for item in failed}):
                category_counts[category] += 1
            failed_categories = {item["category"] for item in failed}
            primary_category = next(
                (
                    category
                    for category in DIAGNOSTIC_PRIORITY
                    if category in failed_categories
                ),
                None,
            )
            if primary_category is not None:
                primary_category_counts[primary_category] += 1
            for layer in result.failure_layers:
                layer_counts[layer] += 1
            if failed and sample_index == 0:
                failure_cases.append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "source_seed_id": candidate["source_seed_id"],
                        "sample_indexes_evaluated": list(range(num_repeats)),
                        "intended_action": scenario.intended_action,
                        "dialogue_form": scenario.dialogue_form,
                        "noise_level": candidate["noise_level"],
                        "noise_operations": candidate["noise_operations"],
                        "failure_layers": list(result.failure_layers),
                        "failure_categories": sorted(
                            {item["category"] for item in failed}
                        ),
                        "primary_diagnostic_category": primary_category,
                        "failed_dimensions": {
                            item["name"]: {
                                "expected": item["expected"],
                                "observed": item["observed"],
                            }
                            for item in failed
                        },
                    }
                )

        complete = all(result.all_passed for result in repeat_results)
        candidate_cases.append(
            {
                "candidate_id": candidate["candidate_id"],
                "source_seed_id": candidate["source_seed_id"],
                "intended_action": scenario.intended_action,
                "dialogue_form": scenario.dialogue_form,
                "noise_level": candidate["noise_level"],
                "variant_index": candidate["variant_index"],
                "complete": complete,
            }
        )

    variance_ids = sorted(
        candidate_id
        for candidate_id, values in fingerprints.items()
        if len(values) != 1
    )
    complete_candidates = sum(case["complete"] for case in candidate_cases)
    safety_failures = dimension_counts["safety"]["failed"]
    decision = (
        "baseline_complete"
        if (
            len(candidate_cases) == EXPECTED_CANDIDATES
            and len(candidate_cases) * num_repeats == EXPECTED_OBSERVATIONS
            and not variance_ids
            and safety_failures == 0
        )
        else "revision_required"
    )

    report_without_hash = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "decision": decision,
        "evidence_tier": "development_silver_diagnostic",
        "source_commit": FROZEN_SOURCE_COMMIT,
        "input_bindings": {
            "candidate_path": CANDIDATE_PATH.as_posix(),
            "candidate_canonical_hash": candidate_records_hash(candidates),
            "candidate_file_payload_hash": _candidate_file_payload_hash(candidates),
            "seed_manifest_path": DEFAULT_SEED_PATH.as_posix(),
            "seed_manifest_hash": seed_manifest["manifest_hash"],
            "source_development_corpus_hash": seed_manifest["source_corpus_hash"],
            "admission_path": ADMISSION_PATH.as_posix(),
            "admission_decision": admission["decision"],
        },
        "population": {
            "candidates": len(candidate_cases),
            "repeats_per_candidate": num_repeats,
            "observations": len(candidate_cases) * num_repeats,
            "complete_candidates": complete_candidates,
            "failed_candidates": len(candidate_cases) - complete_candidates,
        },
        "variance": {
            "variant_candidate_count": len(variance_ids),
            "variant_candidate_ids": variance_ids,
        },
        "dimension_counts": {
            name: {
                "passed": counts["passed"],
                "failed": counts["failed"],
                "total": counts["passed"] + counts["failed"],
            }
            for name, counts in sorted(dimension_counts.items())
        },
        "diagnostic_category_failure_observations": dict(
            sorted(category_counts.items())
        ),
        "primary_diagnostic_category_failure_observations": dict(
            sorted(primary_category_counts.items())
        ),
        "failure_layer_observations": dict(sorted(layer_counts.items())),
        "candidate_breakdown": {
            "by_action": _bucket_summary(candidate_cases, "intended_action"),
            "by_dialogue_form": _bucket_summary(candidate_cases, "dialogue_form"),
            "by_noise_level": _bucket_summary(candidate_cases, "noise_level"),
        },
        "primary_diagnostic_candidate_breakdown": {
            "by_action": _primary_failure_breakdown(
                failure_cases,
                "intended_action",
            ),
            "by_dialogue_form": _primary_failure_breakdown(
                failure_cases,
                "dialogue_form",
            ),
            "by_noise_level": _primary_failure_breakdown(
                failure_cases,
                "noise_level",
            ),
        },
        "failure_cases": failure_cases,
        "boundaries": {
            "protected_holdout_access": False,
            "historical_diary_access": False,
            "external_corpus_access": False,
            "provider_access": False,
            "product_write": False,
            "parser_or_policy_changes": False,
            "contains_source_utterances": False,
        },
    }
    return {
        **report_without_hash,
        "report_hash": _sha256(report_without_hash),
    }


def write_baseline_report(
    path: Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    report = build_baseline_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


__all__ = [
    "ADMISSION_PATH",
    "CANDIDATE_PATH",
    "DEFAULT_REPORT_PATH",
    "EXPECTED_CANDIDATE_HASH",
    "EXPECTED_CANDIDATES",
    "EXPECTED_OBSERVATIONS",
    "EXPECTED_REPEATS",
    "FROZEN_SOURCE_COMMIT",
    "REPORT_SCHEMA_VERSION",
    "build_baseline_report",
    "build_evaluation_scenarios",
    "write_baseline_report",
]
