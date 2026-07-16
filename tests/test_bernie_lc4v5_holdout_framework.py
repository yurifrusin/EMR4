"""Content-blind synthetic tests for the LC4V5 one-shot framework."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    InterpretationObservation,
    ReplayObservation,
    score_interpretation_replay_pair,
)
from app.services.bernie.lc4v5_holdout_framework import (
    AggregateCount,
    EvidenceGates,
    EvaluationBatch,
    OneShotPaths,
    REQUIRED_DIMENSIONS,
    V5AggregateReport,
    V5Corpus,
    V5ScenarioGroup,
    V5ScenarioRecord,
    build_aggregate_report,
    build_manifest,
    canonical_hash,
    canonical_json_bytes,
    consume_seal,
    create_unconsumed_seal,
    evaluate_thresholds,
    execute_one_shot,
    file_hash,
    report_contains_case_level_keys,
    validate_manifest,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec


ACTIONS = ("create", "move", "resize", "cancel", "status_change", "explain_schedule")
LANGUAGE_FORMS = (
    "plain",
    "paraphrase",
    "filler",
    "abbreviation",
    "typo",
    "speech_like",
    "punctuation_variant",
    "adversarial",
)


def _scenario(group_index: int, scenario_index: int) -> ReceptionScenarioSpec:
    ordinal = group_index * 12 + scenario_index
    multi_turn = scenario_index in (3, 7, 11)
    turns = [{"speaker": "user", "utterance": "Book Pat at 15:00"}]
    if multi_turn:
        turns.append({"speaker": "user", "utterance": "That is correct"})
    return ReceptionScenarioSpec(
        scenario_id=f"synthetic-{ordinal:03d}",
        provenance="gold",
        adjudication="adjudicated",
        family=f"synthetic-family-{group_index % 6}",
        description="Synthetic framework-only scenario",
        dialogue_turns=turns,
        reference_date=date(2026, 7, 16),
        clinic_clock=datetime(2026, 7, 16, 9, 0, tzinfo=timezone.utc),
        intended_action=ACTIONS[ordinal % len(ACTIONS)],
        action_semantics="intended",
        temporal_relation="exact",
        earliest_time="15:00",
        latest_time="15:00",
        normalized_values={"time": "15:00"},
        source_spans={},
        practitioner_semantics="exact",
        patient_semantics="exact",
        location_semantics="exact",
        appointment_type_semantics="exact",
        duration_semantics="exact",
        diary_state="empty",
        entity_state="exact",
        dialogue_form="clarification" if multi_turn else "one_shot",
        language_form=LANGUAGE_FORMS[ordinal % len(LANGUAGE_FORMS)],
        initial_diary_state={},
        expected_outcome_kind="proposal",
        expected_tool_sequence=[],
        expected_appointment_deltas=[],
        expected_audit_deltas=[],
        forbidden_outcomes=[],
        forbidden_tool_calls=[],
    )


@pytest.fixture(scope="module")
def corpus() -> V5Corpus:
    groups = []
    for group_index in range(24):
        records = tuple(
            V5ScenarioRecord(
                coverage_cell=f"synthetic-cell-{group_index:02d}-{scenario_index:02d}",
                scenario=_scenario(group_index, scenario_index),
            )
            for scenario_index in range(12)
        )
        groups.append(
            V5ScenarioGroup(group_id=f"synthetic-group-{group_index:02d}", scenarios=records)
        )
    return V5Corpus(groups=tuple(groups))


def _passing_results(scenarios: list[ReceptionScenarioSpec]) -> list[ComposedSampleResult]:
    results = []
    for scenario in scenarios:
        entity_semantics = {
            "practitioner": scenario.practitioner_semantics,
            "patient": scenario.patient_semantics,
            "location": scenario.location_semantics,
            "appointment_type": scenario.appointment_type_semantics,
            "duration": scenario.duration_semantics,
        }
        for sample_index in (0, 1):
            interpretation = InterpretationObservation(
                scenario_id=scenario.scenario_id,
                sample_index=sample_index,
                intended_action=scenario.intended_action,
                action_semantics=scenario.action_semantics,
                temporal_relation=scenario.temporal_relation,
                normalized_values=scenario.normalized_values,
                entity_semantics=entity_semantics,
                requires_clarification=False,
                clarification_choices=(),
                selected_tool_sequence=tuple(scenario.expected_tool_sequence),
                authority_claim="read",
            )
            replay = ReplayObservation(
                scenario_id=scenario.scenario_id,
                sample_index=sample_index,
                downstream_outcome=scenario.expected_outcome_kind,
                tools_used=tuple(scenario.expected_tool_sequence),
                requires_clarification=False,
                clarification_choices=(),
                appointment_deltas=(),
                audit_deltas=(),
                forbidden_outcomes_observed=(),
                forbidden_tools_observed=(),
                is_simulated_confirmed_write=False,
            )
            results.append(score_interpretation_replay_pair(scenario, interpretation, replay))
    return results


def _passing_batch(scenarios: list[ReceptionScenarioSpec]) -> EvaluationBatch:
    return EvaluationBatch(results=_passing_results(scenarios))


def _manifest_and_seal(corpus: V5Corpus, framework_hash: str = "1" * 64, evaluator_hash: str = "2" * 64):
    manifest = build_manifest(
        corpus,
        source_commit="a" * 40,
        framework_hash=framework_hash,
        evaluator_hash=evaluator_hash,
        created_at="2026-07-16T00:00:00Z",
    )
    seal = create_unconsumed_seal(
        manifest,
        attempt_id="synthetic-attempt",
        created_at="2026-07-16T00:01:00Z",
    )
    return manifest, seal


def _all_true_evidence() -> EvidenceGates:
    return EvidenceGates(**{name: True for name in EvidenceGates.model_fields})


def test_canonical_hash_is_order_independent_for_mapping_keys() -> None:
    assert canonical_hash({"b": 2, "a": 1}) == canonical_hash({"a": 1, "b": 2})


def test_corpus_rejects_unknown_fields(corpus: V5Corpus) -> None:
    payload = corpus.model_dump(mode="json")
    payload["unexpected"] = True
    with pytest.raises(ValidationError):
        V5Corpus.model_validate(payload)


def test_corpus_rejects_duplicate_coverage_cell(corpus: V5Corpus) -> None:
    payload = corpus.model_dump(mode="json")
    payload["groups"][1]["scenarios"][0]["coverage_cell"] = payload["groups"][0]["scenarios"][0]["coverage_cell"]
    with pytest.raises(ValidationError, match="coverage cells"):
        V5Corpus.model_validate(payload)


def test_manifest_binds_every_scenario_hash(corpus: V5Corpus) -> None:
    manifest, _ = _manifest_and_seal(corpus)
    validate_manifest(corpus, manifest)
    payload = manifest.model_dump(mode="json")
    payload["groups"][0]["scenario_hashes"][0] = "f" * 64
    group = payload["groups"][0]
    group["group_hash"] = canonical_hash(
        {
            "coverage_cells": group["coverage_cells"],
            "group_id": group["group_id"],
            "scenario_hashes": group["scenario_hashes"],
            "scenario_ids": group["scenario_ids"],
        }
    )
    tampered = type(manifest).model_validate(payload)
    with pytest.raises(ValueError, match="exactly bind"):
        validate_manifest(corpus, tampered)


def test_seal_is_hash_bound_and_one_way(corpus: V5Corpus) -> None:
    _, seal = _manifest_and_seal(corpus)
    consumed = consume_seal(seal, report_hash="b" * 64, consumed_at="2026-07-16T00:02:00Z")
    assert consumed.state == "consumed"
    assert consumed.report_hash == "b" * 64
    with pytest.raises(ValueError, match="only an unconsumed"):
        consume_seal(consumed, report_hash="c" * 64, consumed_at="later")


def test_report_requires_exactly_two_complete_repeats(corpus: V5Corpus) -> None:
    manifest, seal = _manifest_and_seal(corpus)
    results = _passing_results(corpus.scenarios)
    with pytest.raises(ValueError, match="576 typed results"):
        build_aggregate_report(corpus, manifest, seal, results[:-1])


def test_report_rejects_missing_dimension(corpus: V5Corpus) -> None:
    manifest, seal = _manifest_and_seal(corpus)
    report = build_aggregate_report(corpus, manifest, seal, _passing_results(corpus.scenarios))
    payload = report.model_dump(mode="json")
    del payload["per_dimension"]["authority"]
    with pytest.raises(ValidationError, match="missing or unknown dimensions"):
        V5AggregateReport.model_validate(payload)


def test_thresholds_require_exact_safety_576(corpus: V5Corpus) -> None:
    manifest, seal = _manifest_and_seal(corpus)
    report = build_aggregate_report(corpus, manifest, seal, _passing_results(corpus.scenarios))
    payload = report.model_dump(mode="json")
    payload["safety"] = AggregateCount(passed=575, failed=1, total=576).model_dump()
    payload["failure_layers"]["safety"] = 1
    unsafe_report = V5AggregateReport.model_validate(payload)
    receipt = evaluate_thresholds(unsafe_report, _all_true_evidence())
    assert receipt.decision == "certification_fail"
    assert receipt.thresholds.safety is False
    assert receipt.thresholds.failure_layers["safety"] is False


def test_evidence_gate_failure_cannot_certify(corpus: V5Corpus) -> None:
    manifest, seal = _manifest_and_seal(corpus)
    report = build_aggregate_report(corpus, manifest, seal, _passing_results(corpus.scenarios))
    evidence = _all_true_evidence().model_copy(update={"valid_source_commit": False})
    receipt = evaluate_thresholds(report, evidence)
    assert receipt.decision == "evidence_invalid"


def test_report_schema_and_scanner_forbid_case_level_evidence(corpus: V5Corpus) -> None:
    manifest, seal = _manifest_and_seal(corpus)
    report = build_aggregate_report(corpus, manifest, seal, _passing_results(corpus.scenarios))
    payload = report.model_dump(mode="json")
    assert report_contains_case_level_keys(payload) is False
    payload["failed_case_ids"] = ["synthetic-001"]
    assert report_contains_case_level_keys(payload) is True
    with pytest.raises(ValidationError):
        V5AggregateReport.model_validate(payload)


def test_exclusive_one_shot_writes_aggregate_report_and_denies_retry(
    tmp_path: Path, corpus: V5Corpus
) -> None:
    framework_path = tmp_path / "framework.py"
    evaluator_path = tmp_path / "evaluator.py"
    framework_path.write_text("framework-v2\n", encoding="utf-8")
    evaluator_path.write_text("evaluator-v1\n", encoding="utf-8")
    manifest = build_manifest(
        corpus,
        source_commit="a" * 40,
        framework_hash=file_hash(framework_path),
        evaluator_hash=file_hash(evaluator_path),
        created_at="2026-07-16T00:00:00Z",
    )
    seal = create_unconsumed_seal(
        manifest,
        attempt_id="synthetic-attempt",
        created_at="2026-07-16T00:01:00Z",
    )
    paths = OneShotPaths(
        corpus=tmp_path / "corpus.json",
        manifest=tmp_path / "manifest.json",
        seal=tmp_path / "seal.json",
        marker=tmp_path / "attempt.marker.json",
        report=tmp_path / "report.json",
        receipt=tmp_path / "receipt.json",
        framework=framework_path,
        evaluator=evaluator_path,
    )
    paths.corpus.write_bytes(canonical_json_bytes(corpus) + b"\n")
    paths.manifest.write_bytes(canonical_json_bytes(manifest) + b"\n")
    paths.seal.write_bytes(canonical_json_bytes(seal) + b"\n")

    receipt = execute_one_shot(
        paths,
        attempt_id="synthetic-attempt",
        source_commit="a" * 40,
        consumed_at="2026-07-16T00:02:00Z",
        evaluator=_passing_batch,
        source_commit_validator=lambda value: value == "a" * 40,
    )
    assert receipt.decision == "certification_pass"
    assert receipt.report_hash == canonical_hash(
        V5AggregateReport.model_validate_json(paths.report.read_text(encoding="utf-8"))
    )
    persisted_seal = json.loads(paths.seal.read_text(encoding="utf-8"))
    assert persisted_seal["state"] == "consumed"
    assert persisted_seal["report_hash"] == receipt.report_hash

    second = execute_one_shot(
        paths,
        attempt_id="synthetic-attempt",
        source_commit="a" * 40,
        consumed_at="2026-07-16T00:03:00Z",
        evaluator=_passing_batch,
        source_commit_validator=lambda value: value == "a" * 40,
    )
    assert second.decision == "evidence_invalid"
    assert second.error_codes == ("one_shot_already_started",)


def test_evaluator_exception_is_invalid_and_still_burns_attempt(
    tmp_path: Path, corpus: V5Corpus
) -> None:
    framework_path = tmp_path / "framework.py"
    evaluator_path = tmp_path / "evaluator.py"
    framework_path.write_text("framework\n", encoding="utf-8")
    evaluator_path.write_text("evaluator\n", encoding="utf-8")
    manifest = build_manifest(
        corpus,
        source_commit="a" * 40,
        framework_hash=file_hash(framework_path),
        evaluator_hash=file_hash(evaluator_path),
        created_at="2026-07-16T00:00:00Z",
    )
    seal = create_unconsumed_seal(manifest, attempt_id="burned", created_at="now")
    paths = OneShotPaths(
        corpus=tmp_path / "corpus.json",
        manifest=tmp_path / "manifest.json",
        seal=tmp_path / "seal.json",
        marker=tmp_path / "marker.json",
        report=tmp_path / "report.json",
        receipt=tmp_path / "receipt.json",
        framework=framework_path,
        evaluator=evaluator_path,
    )
    paths.corpus.write_bytes(canonical_json_bytes(corpus) + b"\n")
    paths.manifest.write_bytes(canonical_json_bytes(manifest) + b"\n")
    paths.seal.write_bytes(canonical_json_bytes(seal) + b"\n")

    def explode(_: list[ReceptionScenarioSpec]) -> EvaluationBatch:
        raise RuntimeError("synthetic failure containing forbidden case detail")

    receipt = execute_one_shot(
        paths,
        attempt_id="burned",
        source_commit="a" * 40,
        consumed_at="later",
        evaluator=explode,
        source_commit_validator=lambda value: value == "a" * 40,
    )
    assert receipt.decision == "evidence_invalid"
    assert receipt.error_codes == ("evaluation_exception",)
    assert not paths.report.exists()
    assert paths.marker.exists()
    assert "forbidden case detail" not in paths.receipt.read_text(encoding="utf-8")
