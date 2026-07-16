"""Content-blind tests for the fresh LC4V6 framework."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from app.services.bernie.lc4v6_content_blind_framework import (
    ACTIONS,
    ATTEMPT_ID,
    DIMENSIONS,
    FAILURE_LAYERS,
    MANIFEST_SCHEMA_VERSION,
    BoundHashes,
    EvaluationContext,
    OneShotPaths,
    OneShotStateMachine,
    ScenarioContract,
    TypedObservation,
    aggregate_observations,
    build_unconsumed_seal,
    canonical_json,
    sha256_payload,
    sha256_text,
    validate_aggregate,
    validate_manifest,
    validate_observations,
)


def _hashes(seed: str = "0") -> BoundHashes:
    return BoundHashes(
        source="sha256:" + seed * 64,
        corpus="sha256:" + "1" * 64,
        manifest="sha256:" + "2" * 64,
        framework="sha256:" + "3" * 64,
        evaluator="sha256:" + "4" * 64,
    )


def _scenarios() -> tuple[ScenarioContract, ...]:
    actions = sorted(ACTIONS)
    result: list[ScenarioContract] = []
    for group_index in range(24):
        for item_index in range(12):
            sequence = ("opaque", "opaque") if item_index < 3 else ("opaque",)
            index = group_index * 12 + item_index
            result.append(
                ScenarioContract(
                    scenario_id=f"opaque-{index:03d}",
                    group=f"group-{group_index:03d}",
                    coverage_cell=f"cell-{index:03d}",
                    action=actions[index % len(actions)],
                    utterances=sequence,
                    reference_date="2026-07-16",
                    expected={},
                    slices={
                        "family": f"group-{group_index:03d}",
                        "dialogue_form": "multi" if len(sequence) > 1 else "one_shot",
                        "action": actions[index % len(actions)],
                        "language_form": "opaque",
                        "temporal_relation": "opaque",
                        "provenance": "gold",
                        "adjudication": "adjudicated",
                    },
                )
            )
    return tuple(result)


def _manifest() -> dict:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "attempt_id": ATTEMPT_ID,
        "group_count": 24,
        "scenario_count": 288,
        "multi_turn_count": 72,
        "one_shot_count": 216,
        "action_count": 6,
        "coverage_cell_count": 288,
        "repeats": 2,
    }


def _observations(
    scenarios: tuple[ScenarioContract, ...] | None = None,
) -> tuple[TypedObservation, ...]:
    source = scenarios or _scenarios()
    return tuple(
        TypedObservation(
            scenario_id=scenario.scenario_id,
            repeat_index=repeat,
            dimension_passes={name: True for name in DIMENSIONS},
            safe=True,
            failure_layers={name: False for name in FAILURE_LAYERS},
            slices=scenario.slices,
        )
        for scenario in source
        for repeat in range(2)
    )


def _report() -> dict:
    return aggregate_observations(_observations(), _hashes())


def test_hashes_are_canonical_and_strict() -> None:
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    assert sha256_text("opaque") == sha256_text("opaque")
    assert sha256_payload({"a": 1}) != sha256_payload({"a": 2})
    assert _hashes().valid() is True
    assert replace(_hashes(), source="sha256:short").valid() is False


def test_manifest_exact_shape_passes() -> None:
    result = validate_manifest(_manifest(), _scenarios())
    assert result.valid, result.errors


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("group_count", 23),
        ("scenario_count", 287),
        ("multi_turn_count", 71),
        ("one_shot_count", 215),
        ("action_count", 5),
        ("coverage_cell_count", 287),
        ("repeats", 3),
        ("attempt_id", "wrong"),
        ("schema_version", "wrong"),
    ],
)
def test_manifest_count_or_identity_drift_fails(field: str, value: object) -> None:
    manifest = _manifest()
    manifest[field] = value
    assert validate_manifest(manifest, _scenarios()).valid is False


def test_manifest_duplicate_id_cell_and_group_drift_fail() -> None:
    scenarios = list(_scenarios())
    scenarios[1] = replace(
        scenarios[1],
        scenario_id=scenarios[0].scenario_id,
        coverage_cell=scenarios[0].coverage_cell,
        group="new-group",
    )
    result = validate_manifest(_manifest(), scenarios)
    assert result.valid is False
    assert any("unique" in error for error in result.errors)


def test_manifest_action_and_multi_turn_drift_fail() -> None:
    scenarios = list(_scenarios())
    scenarios[0] = replace(scenarios[0], action="unknown", utterances=("opaque",))
    result = validate_manifest(_manifest(), scenarios)
    assert result.valid is False
    assert any("action" in error or "multi-turn" in error for error in result.errors)


def test_dependency_injected_evaluation_produces_exact_repeats() -> None:
    def evaluator(scenario: ScenarioContract, repeat: int) -> TypedObservation:
        return TypedObservation(
            scenario_id=scenario.scenario_id,
            repeat_index=repeat,
            dimension_passes={name: True for name in DIMENSIONS},
            safe=True,
            failure_layers={name: False for name in FAILURE_LAYERS},
            slices=scenario.slices,
        )

    observations = EvaluationContext(evaluator).evaluate(_scenarios())
    assert len(observations) == 576
    assert validate_observations(observations, _scenarios()).valid


def test_observation_missing_repeat_or_dimension_fails() -> None:
    scenarios = _scenarios()
    observations = list(_observations(scenarios))
    observations.pop()
    observations[0] = replace(observations[0], dimension_passes={})
    result = validate_observations(observations, scenarios)
    assert result.valid is False
    assert any("population" in error for error in result.errors)


def test_aggregate_exact_shape_and_slice_arithmetic_pass() -> None:
    report = _report()
    assert validate_aggregate(report, _hashes()).valid
    assert report["sample_count"] == 576
    assert report["complete_contract"] == {"passed": 576, "failed": 0, "total": 576}
    assert len(report["slices"]["family"]) == 24
    assert all(row["total"] == 24 for row in report["slices"]["family"])


def test_repeat_variance_is_measured_not_assumed() -> None:
    observations = list(_observations())
    observations[1] = replace(observations[1], safe=False)
    report = aggregate_observations(observations, _hashes())
    assert report["repeat_variance_count"] == 1
    assert validate_aggregate(report, _hashes()).valid is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sample_count", 575),
        ("evaluation_exception_count", 1),
        ("missing_dimension_count", 1),
        ("case_level_artifact_count", 1),
        ("repeat_variance_count", 1),
        ("attempt_id", "wrong"),
        ("schema_version", "wrong"),
    ],
)
def test_aggregate_evidence_drift_fails(field: str, value: object) -> None:
    report = _report()
    report[field] = value
    assert validate_aggregate(report, _hashes()).valid is False


def test_aggregate_hash_drift_and_malformed_arithmetic_fail() -> None:
    report = _report()
    report["hashes"]["source"] = "sha256:" + "f" * 64
    report["complete_contract"]["failed"] = 1
    result = validate_aggregate(report, _hashes())
    assert result.valid is False
    assert any("hash" in error for error in result.errors)
    assert any("arithmetic" in error for error in result.errors)


def test_nested_case_level_key_is_rejected() -> None:
    report = _report()
    report["slices"]["family"][0]["scenario_ids"] = ["opaque"]
    result = validate_aggregate(report, _hashes())
    assert result.valid is False
    assert any("case-level" in error for error in result.errors)


def test_empty_or_incomplete_slices_fail() -> None:
    report = _report()
    report["slices"] = {}
    assert validate_aggregate(report, _hashes()).valid is False
    report = _report()
    report["slices"]["family"][0]["total"] = 23
    assert validate_aggregate(report, _hashes()).valid is False


def _write_seal(paths: OneShotPaths, source: str = "source") -> None:
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.seal.write_text(
        json.dumps(build_unconsumed_seal(source, _hashes())), encoding="utf-8"
    )


def test_one_shot_consumes_and_binds_without_erasing_seal(tmp_path) -> None:
    paths = OneShotPaths(tmp_path)
    _write_seal(paths)
    machine = OneShotStateMachine(paths, "source", _hashes())
    assert machine.validate_prerun().valid
    assert machine.consume(_report()).valid

    report = json.loads(paths.report.read_text(encoding="utf-8"))
    seal = json.loads(paths.seal.read_text(encoding="utf-8"))
    marker = json.loads(paths.marker.read_text(encoding="utf-8"))
    assert report == _report()
    assert seal["consumed"] is True
    assert seal["report_hash"] == sha256_payload(report)
    assert marker["report_hash"] == seal["report_hash"]
    assert marker["consumed_seal_hash"] == sha256_payload(seal)
    assert paths.lock.read_text(encoding="utf-8").strip() == ATTEMPT_ID


@pytest.mark.parametrize("existing", ["marker", "report", "lock"])
def test_one_shot_refuses_every_existing_attempt_artifact(tmp_path, existing: str) -> None:
    paths = OneShotPaths(tmp_path)
    _write_seal(paths)
    getattr(paths, existing).write_text("{}", encoding="utf-8")
    result = OneShotStateMachine(paths, "source", _hashes()).validate_prerun()
    assert result.valid is False


def test_one_shot_refuses_missing_malformed_consumed_or_drifted_seal(tmp_path) -> None:
    paths = OneShotPaths(tmp_path)
    machine = OneShotStateMachine(paths, "source", _hashes())
    assert machine.validate_prerun().valid is False
    paths.seal.write_text("not-json", encoding="utf-8")
    assert machine.validate_prerun().valid is False
    paths.seal.write_text(
        json.dumps({**build_unconsumed_seal("source", _hashes()), "consumed": True}),
        encoding="utf-8",
    )
    assert machine.validate_prerun().valid is False
    _write_seal(paths, source="different")
    assert machine.validate_prerun().valid is False


def test_structurally_unsafe_report_does_not_consume_or_create_lock(tmp_path) -> None:
    paths = OneShotPaths(tmp_path)
    _write_seal(paths)
    report = _report()
    report["scenario_ids"] = ["opaque"]
    result = OneShotStateMachine(paths, "source", _hashes()).consume(report)
    assert result.valid is False
    assert json.loads(paths.seal.read_text(encoding="utf-8"))["consumed"] is False
    assert not paths.lock.exists()


def test_structurally_valid_evidence_invalid_report_is_consumed_once(tmp_path) -> None:
    paths = OneShotPaths(tmp_path)
    _write_seal(paths)
    report = aggregate_observations(
        _observations(), _hashes(), evaluation_exception_count=1
    )
    assert validate_aggregate(report, _hashes()).valid is False
    machine = OneShotStateMachine(paths, "source", _hashes())
    assert machine.consume(report).valid
    assert json.loads(paths.seal.read_text(encoding="utf-8"))["consumed"] is True
    assert machine.consume(report).valid is False


def test_second_consumption_is_permanently_refused(tmp_path) -> None:
    paths = OneShotPaths(tmp_path)
    _write_seal(paths)
    machine = OneShotStateMachine(paths, "source", _hashes())
    assert machine.consume(_report()).valid
    assert machine.consume(_report()).valid is False


def test_framework_contains_no_real_content_or_import_side_effect() -> None:
    from app.services.bernie import lc4v6_content_blind_framework as framework

    source = open(framework.__file__, encoding="utf-8").read()
    assert "Margaret Thompson" not in source
    assert "Dr Shera" not in source
    assert "tests/fixtures" not in source
    assert "semantic_extraction" not in source
