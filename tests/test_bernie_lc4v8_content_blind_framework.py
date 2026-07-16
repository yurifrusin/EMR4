from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from typing import Callable

import pytest

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
)
from app.services.bernie.lc4v8_content_blind_framework import (
    DIMENSION_NAMES,
    EXPECTED_GROUP_IDS,
    FIXTURE_SCHEMA_VERSION,
    FROZEN_THRESHOLDS,
    MANIFEST_SCHEMA_VERSION,
    REPORT_SCHEMA_VERSION,
    SEAL_SCHEMA_VERSION,
    AttemptMarker,
    Scenario,
    ScenarioExpected,
    ScenarioInput,
    ScenarioOutput,
    canonical_json_bytes,
    certify,
    convert_fixture_to_scenarios,
    deterministic_hash,
    evaluate_scenario,
    run_one_shot,
    sha256_bytes,
    validate_fixture_schema,
    validate_fixed_shape,
    validate_manifest_schema,
    validate_report_schema,
    validate_seal_schema,
    validate_threshold_schema,
)


def _expected() -> dict[str, object]:
    return {name: {"opaque": name} for name in DIMENSION_NAMES}


def _fixture() -> dict[str, object]:
    actions = (
        "create", "move", "resize", "cancel", "status_change", "explain_schedule"
    )
    forms = (
        "plain", "paraphrase", "speech_like", "word_order", "correction", "interval"
    )
    groups: list[dict[str, object]] = []
    for group_index, group_id in enumerate(EXPECTED_GROUP_IDS):
        scenarios: list[dict[str, object]] = []
        for scenario_index in range(12):
            multi_turn = scenario_index in (0, 4, 8)
            utterances = [f"opaque-{group_index}-{scenario_index}"]
            if multi_turn:
                utterances.append(f"opaque-followup-{group_index}-{scenario_index}")
            scenarios.append({
                "coverage_cell": f"cell-{group_index:02d}-{scenario_index:02d}",
                "language_form": forms[scenario_index // 2],
                "multi_turn": multi_turn,
                "utterances": utterances,
                "diary_state": {"opaque_state": group_index},
                "expected": _expected(),
            })
        groups.append({
            "group_id": group_id,
            "action": actions[group_index // 4],
            "scenarios": scenarios,
        })
    return {
        "schema_version": FIXTURE_SCHEMA_VERSION,
        "total_groups": 24,
        "total_scenarios": 288,
        "groups": groups,
    }


def _passing_output(**overrides: object) -> ScenarioOutput:
    dimensions = _expected()
    dimensions.update(overrides)
    return ScenarioOutput(
        dimensions=dimensions,
        interpretation_failure=False,
        policy_failure=False,
        integration_failure=False,
    )


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return result.stdout.strip()


def _write_json(path: Path, value: object) -> bytes:
    raw = json.dumps(value, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def _prepared_attempt(tmp_path: Path) -> dict[str, Path | str]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init")
    _git(repo, "config", "user.email", "v8@example.invalid")
    _git(repo, "config", "user.name", "V8 Framework Test")
    fixture_path = repo / "fixture.json"
    framework_path = repo / "framework.py"
    thresholds_path = repo / "thresholds.json"
    fixture_bytes = _write_json(fixture_path, _fixture())
    framework_bytes = b"# opaque framework binding\n"
    framework_path.write_bytes(framework_bytes)
    threshold_bytes = _write_json(thresholds_path, FROZEN_THRESHOLDS)
    _git(repo, "add", "fixture.json", "framework.py", "thresholds.json")
    _git(repo, "commit", "-m", "freeze opaque source")
    source_commit = _git(repo, "rev-parse", "HEAD")
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "corpus_source_commit": source_commit,
        "fixture_path": "fixture.json",
        "fixture_sha256": sha256_bytes(fixture_bytes),
        "framework_path": "framework.py",
        "framework_sha256": sha256_bytes(framework_bytes),
        "thresholds_path": "thresholds.json",
        "thresholds_sha256": sha256_bytes(threshold_bytes),
    }
    manifest_path = repo / "manifest.json"
    manifest_bytes = _write_json(manifest_path, manifest)
    attempt_id = "lc4v8-framework-test"
    seal = {
        "schema_version": SEAL_SCHEMA_VERSION,
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "attempt_id": attempt_id,
        "state": "unconsumed",
    }
    seal_path = repo / "seal.json"
    _write_json(seal_path, seal)
    return {
        "repo_root": repo,
        "fixture_path": fixture_path,
        "manifest_path": manifest_path,
        "seal_path": seal_path,
        "thresholds_path": thresholds_path,
        "framework_path": framework_path,
        "marker_path": repo / "attempt.marker.json",
        "report_path": repo / "report.json",
        "expected_attempt_id": attempt_id,
    }


def _run(
    prepared: dict[str, Path | str],
    evaluator: Callable[[ScenarioInput], ScenarioOutput],
):
    return run_one_shot(evaluator=evaluator, **prepared)  # type: ignore[arg-type]


def test_exact_fixture_and_shape_pass() -> None:
    fixture = _fixture()
    assert validate_fixture_schema(fixture) == []
    assert validate_fixed_shape(fixture) == []
    assert len(convert_fixture_to_scenarios(fixture)) == 288


@pytest.mark.parametrize("field", ["schema_version", "total_groups", "total_scenarios", "groups"])
def test_fixture_rejects_missing_top_level_fields(field: str) -> None:
    fixture = _fixture()
    del fixture[field]
    assert validate_fixture_schema(fixture)


def test_fixture_rejects_unknown_nested_field() -> None:
    fixture = _fixture()
    fixture["groups"][0]["scenarios"][0]["case_id"] = "leak"  # type: ignore[index]
    assert any("unknown" in error for error in validate_fixture_schema(fixture))


def test_fixture_rejects_missing_gold_dimension() -> None:
    fixture = _fixture()
    del fixture["groups"][0]["scenarios"][0]["expected"]["safety"]  # type: ignore[index]
    assert validate_fixture_schema(fixture)


def test_fixture_rejects_turn_flag_disagreement() -> None:
    fixture = _fixture()
    fixture["groups"][0]["scenarios"][0]["multi_turn"] = False  # type: ignore[index]
    assert validate_fixture_schema(fixture)


def test_shape_rejects_duplicate_coverage_cell() -> None:
    fixture = _fixture()
    fixture["groups"][0]["scenarios"][1]["coverage_cell"] = "cell-00-00"  # type: ignore[index]
    assert any("duplicate" in error for error in validate_fixed_shape(fixture))


def test_shape_rejects_incorrect_language_distribution() -> None:
    fixture = _fixture()
    fixture["groups"][0]["scenarios"][0]["language_form"] = "interval"  # type: ignore[index]
    assert any("form" in error for error in validate_fixed_shape(fixture))


def test_shape_rejects_group_reordering() -> None:
    fixture = _fixture()
    fixture["groups"][0], fixture["groups"][1] = fixture["groups"][1], fixture["groups"][0]  # type: ignore[index]
    assert any("group IDs" in error for error in validate_fixed_shape(fixture))


def test_manifest_seal_and_frozen_thresholds_are_exact() -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "corpus_source_commit": "a" * 40,
        "fixture_path": "fixture.json",
        "fixture_sha256": "b" * 64,
        "framework_path": "framework.py",
        "framework_sha256": "c" * 64,
        "thresholds_path": "thresholds.json",
        "thresholds_sha256": "d" * 64,
    }
    seal = {
        "schema_version": SEAL_SCHEMA_VERSION,
        "manifest_sha256": "e" * 64,
        "attempt_id": "opaque-attempt",
        "state": "unconsumed",
    }
    assert validate_manifest_schema(manifest) == []
    assert validate_seal_schema(seal) == []
    assert validate_threshold_schema(FROZEN_THRESHOLDS) == []
    bad = dict(FROZEN_THRESHOLDS)
    bad["complete_min"] = 547
    assert validate_threshold_schema(bad)


def test_manifest_rejects_parent_path() -> None:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "corpus_source_commit": "a" * 40,
        "fixture_path": "../fixture.json",
        "fixture_sha256": "b" * 64,
        "framework_path": "framework.py",
        "framework_sha256": "c" * 64,
        "thresholds_path": "thresholds.json",
        "thresholds_sha256": "d" * 64,
    }
    assert validate_manifest_schema(manifest)


def test_evaluator_receives_no_gold_or_identity() -> None:
    scenario = convert_fixture_to_scenarios(_fixture())[0]
    observed: list[ScenarioInput] = []

    def evaluator(value: ScenarioInput) -> ScenarioOutput:
        observed.append(value)
        return _passing_output()

    first, second, variance = evaluate_scenario(evaluator, scenario)
    assert first.complete and second.complete and not variance
    assert not hasattr(observed[0], "expected")
    assert not hasattr(observed[0], "coverage_cell")
    assert not hasattr(observed[0], "group_id")
    assert not hasattr(observed[0], "language_form")


def test_raw_output_variance_is_detected_even_when_both_repeats_fail() -> None:
    scenario = convert_fixture_to_scenarios(_fixture())[0]
    calls = 0

    def evaluator(_value: ScenarioInput) -> ScenarioOutput:
        nonlocal calls
        calls += 1
        return _passing_output(intended_action=f"wrong-{calls}")

    first, second, variance = evaluate_scenario(evaluator, scenario)
    assert not first.complete and not second.complete and variance


def test_marker_is_exclusive_persistent_and_has_no_cleanup(tmp_path: Path) -> None:
    path = tmp_path / "attempt.marker"
    marker = AttemptMarker(path, "opaque-attempt")
    marker.create_exclusive()
    marker.consume(decision=CERTIFICATION_FAIL, report_hash="a" * 64)
    assert json.loads(path.read_text(encoding="utf-8"))["state"] == "consumed"
    assert not hasattr(marker, "cleanup")
    with pytest.raises(RuntimeError):
        marker.consume(decision=CERTIFICATION_PASS, report_hash="b" * 64)
    with pytest.raises(FileExistsError):
        AttemptMarker(path, "opaque-attempt").create_exclusive()


def test_one_shot_passes_and_writes_anonymous_valid_report(tmp_path: Path) -> None:
    prepared = _prepared_attempt(tmp_path)
    result = _run(prepared, lambda _value: _passing_output())
    assert result.decision == CERTIFICATION_PASS
    assert result.marker_created
    assert result.report is not None
    assert validate_report_schema(result.report) == []
    assert certify(result.report) == CERTIFICATION_PASS
    serialized = json.dumps(result.report).lower()
    for forbidden in (
        '"utterance"', '"utterances"', '"expected"', '"coverage_cell"',
        '"diary_state"', '"oracle"',
    ):
        assert forbidden not in serialized
    marker = json.loads(Path(prepared["marker_path"]).read_text(encoding="utf-8"))
    assert marker["state"] == "consumed"
    assert marker["decision"] == CERTIFICATION_PASS


def test_valid_product_miss_is_fail_not_invalid(tmp_path: Path) -> None:
    prepared = _prepared_attempt(tmp_path)
    result = _run(
        prepared,
        lambda _value: _passing_output(intended_action="wrong"),
    )
    assert result.decision == CERTIFICATION_FAIL
    assert result.report is not None
    assert result.report["evidence_failures"] == {
        "case_artifacts": 0,
        "missing_dimensions": 0,
        "oracle_leaks": 0,
        "repeat_variance": 0,
        "runtime_exceptions": 0,
        "validation_errors": 0,
    }


@pytest.mark.parametrize("failure_field", ["policy_failure", "integration_failure"])
def test_policy_and_integration_failures_are_product_results(
    tmp_path: Path, failure_field: str
) -> None:
    prepared = _prepared_attempt(tmp_path)

    def evaluator(_value: ScenarioInput) -> ScenarioOutput:
        kwargs = {
            "dimensions": _expected(),
            "interpretation_failure": False,
            "policy_failure": False,
            "integration_failure": False,
        }
        kwargs[failure_field] = True
        return ScenarioOutput(**kwargs)  # type: ignore[arg-type]

    result = _run(prepared, evaluator)
    assert result.decision == CERTIFICATION_FAIL
    assert result.report is not None
    assert not any(result.report["evidence_failures"].values())  # type: ignore[union-attr]


def test_runtime_exception_is_invalid_and_consumes(tmp_path: Path) -> None:
    prepared = _prepared_attempt(tmp_path)

    def evaluator(_value: ScenarioInput) -> ScenarioOutput:
        raise RuntimeError("opaque failure")

    result = _run(prepared, evaluator)
    assert result.decision == CERTIFICATION_INVALID
    assert result.report is not None
    assert result.report["evidence_failures"]["runtime_exceptions"] == 1  # type: ignore[index]
    marker = json.loads(Path(prepared["marker_path"]).read_text(encoding="utf-8"))
    assert marker["state"] == "consumed"


def test_missing_output_dimension_is_invalid_and_consumes(tmp_path: Path) -> None:
    prepared = _prepared_attempt(tmp_path)
    missing = _expected()
    del missing["safety"]
    result = _run(
        prepared,
        lambda _value: ScenarioOutput(missing, False, False, False),
    )
    assert result.decision == CERTIFICATION_INVALID
    assert result.report is not None
    assert result.report["evidence_failures"]["missing_dimensions"] == 1  # type: ignore[index]


def test_tampered_committed_binding_is_invalid_before_evaluation(tmp_path: Path) -> None:
    prepared = _prepared_attempt(tmp_path)
    Path(prepared["fixture_path"]).write_text("{}\n", encoding="utf-8")
    calls = 0

    def evaluator(_value: ScenarioInput) -> ScenarioOutput:
        nonlocal calls
        calls += 1
        return _passing_output()

    result = _run(prepared, evaluator)
    assert result.decision == CERTIFICATION_INVALID
    assert calls == 0


def test_second_attempt_cannot_evaluate_or_overwrite_report(tmp_path: Path) -> None:
    prepared = _prepared_attempt(tmp_path)
    first = _run(prepared, lambda _value: _passing_output())
    original_report = Path(prepared["report_path"]).read_bytes()
    calls = 0

    def evaluator(_value: ScenarioInput) -> ScenarioOutput:
        nonlocal calls
        calls += 1
        return _passing_output()

    second = _run(prepared, evaluator)
    assert first.decision == CERTIFICATION_PASS
    assert second.decision == CERTIFICATION_INVALID
    assert not second.marker_created and second.report is None
    assert calls == 0
    assert Path(prepared["report_path"]).read_bytes() == original_report


def test_preexisting_report_path_forces_invalid_and_consumes(tmp_path: Path) -> None:
    prepared = _prepared_attempt(tmp_path)
    Path(prepared["report_path"]).write_text("occupied\n", encoding="utf-8")
    result = _run(prepared, lambda _value: _passing_output())
    assert result.decision == CERTIFICATION_INVALID
    assert result.report is not None
    assert result.report["decision"] == CERTIFICATION_INVALID
    assert result.report["evidence_failures"]["validation_errors"] == 1  # type: ignore[index]
    marker = json.loads(Path(prepared["marker_path"]).read_text(encoding="utf-8"))
    assert marker["state"] == "consumed"
    assert Path(prepared["report_path"]).read_text(encoding="utf-8") == "occupied\n"


def test_report_rejects_missing_slice_and_hash_tampering(tmp_path: Path) -> None:
    prepared = _prepared_attempt(tmp_path)
    result = _run(prepared, lambda _value: _passing_output())
    assert result.report is not None
    missing_slice = copy.deepcopy(result.report)
    del missing_slice["group_counts"]["g24"]  # type: ignore[index]
    assert validate_report_schema(missing_slice)
    tampered = copy.deepcopy(result.report)
    tampered["complete_count"] = 575
    assert any("hash" in error for error in validate_report_schema(tampered))
    assert certify(tampered) == CERTIFICATION_INVALID


def test_report_hash_binds_final_product_failures(tmp_path: Path) -> None:
    first_prepared = _prepared_attempt(tmp_path / "first")
    second_prepared = _prepared_attempt(tmp_path / "second")
    passed = _run(first_prepared, lambda _value: _passing_output())
    failed = _run(second_prepared, lambda _value: _passing_output(intended_action="wrong"))
    assert passed.report is not None and failed.report is not None
    assert passed.report["report_hash"] != failed.report["report_hash"]
    assert deterministic_hash({
        key: value for key, value in passed.report.items() if key != "report_hash"
    }) == passed.report["report_hash"]


def test_module_remains_content_blind_and_runtime_isolated() -> None:
    source = Path("app/services/bernie/lc4v8_content_blind_framework.py").read_text(
        encoding="utf-8"
    ).lower()
    assert "lc4v7" not in source and "lc4v6" not in source
    assert "extract_semantics" not in source and "resolve_policy" not in source
    assert "cleanup" not in source
    for runtime in Path("app").rglob("*.py"):
        if runtime.name == "lc4v8_content_blind_framework.py":
            continue
        assert "lc4v8_content_blind_framework" not in runtime.read_text(
            encoding="utf-8", errors="ignore"
        )


def test_public_report_schema_version_is_frozen() -> None:
    assert REPORT_SCHEMA_VERSION == "bernie.lc4v8.report.v1"
    assert canonical_json_bytes({"b": 1, "a": 2}) == b'{"a":2,"b":1}'
