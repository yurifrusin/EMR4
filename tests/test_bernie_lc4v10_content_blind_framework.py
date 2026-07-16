"""Fail-closed tests for the genuinely content-blind LC4V10 framework."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

import app.services.bernie.lc4v10_content_blind_framework as framework
from app.services.bernie.lc4v10_content_blind_framework import (
    ACTIONS,
    AttemptUnavailable,
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    DIMENSIONS,
    FIXTURE_SCHEMA,
    LANGUAGE_FORMS,
    MANIFEST_SCHEMA,
    MARKER_SCHEMA,
    PROJECTION_FIELDS,
    REPORT_SCHEMA,
    RunPaths,
    SEAL_SCHEMA,
    THRESHOLD_SCHEMA,
    THRESHOLDS,
    run_one_shot,
    score_observation,
    validate_expected,
    validate_fixture,
    validate_observation,
    validate_projection,
    validate_thresholds,
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _write_json(path: Path, value: Any) -> bytes:
    payload = _canonical(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return payload


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _blob(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()  # noqa: S324 -- Git identity


def _projection(action: str) -> dict[str, Any]:
    mutation = action != "explain_schedule"
    tool = {
        "create": "create_booking",
        "move": "update_appointment",
        "resize": "update_appointment",
        "cancel": "change_appointment_status",
        "status_change": "change_appointment_status",
        "explain_schedule": "find_slots",
    }[action]
    return {
        "requires_clarification": False,
        "clarification_choices": [],
        "resolved_patient": None,
        "resolved_practitioner": None,
        "resolved_practitioner_id": None,
        "selected_tools": [tool],
        "authority": "read",
        "diary_relation": "no_conflict",
        "conflicting_fields": [],
        "downstream_outcome": "propose_mutation" if mutation else "proceed_read",
        "appointment_delta_count": 1 if mutation else 0,
        "audit_delta_count": 1 if mutation else 0,
        "simulated_write": mutation,
        "entity_semantics_unchanged": True,
    }


def _expected(action: str) -> dict[str, Any]:
    projection = _projection(action)
    mutation = action != "explain_schedule"
    return {
        "intended_action": action,
        "action_semantics": "requested",
        "temporal_relation_and_bounds": {
            "relation": "unspecified",
            "earliest": None,
            "latest": None,
        },
        "normalized_values": {},
        "entity_semantics": {},
        "lossless_source_spans": [],
        "extraction_clarification": {"required": False, "choices": []},
        "policy_behavior": {
            "resolution": "propose_mutation" if mutation else "proceed_read",
            "mutation_allowed": mutation,
            "safe": True,
        },
        "exact_policy_projection": projection,
        "policy_clarification": {"required": False, "choices": []},
        "clarification_composition": {
            "extraction_required": False,
            "policy_required": False,
            "choices": [],
        },
        "interpretation_tool": {
            "verb": action,
            "authority": "read_only" if action == "explain_schedule" else "signed_confirm",
            "dispatch": "route_read_only" if action == "explain_schedule" else "route_to_confirm",
            "clarification_kind": None,
        },
        "replay": {
            "downstream_outcome": projection["downstream_outcome"],
            "appointment_delta_count": projection["appointment_delta_count"],
            "audit_delta_count": projection["audit_delta_count"],
            "simulated_write": projection["simulated_write"],
        },
        "safety": True,
    }


def _fixture(attempt_id: str = "lc4v10-fresh-certification-001") -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    number = 0
    for action_index, action in enumerate(ACTIONS):
        for within_action in range(4):
            group_number = action_index * 4 + within_action + 1
            group = f"g{group_number:02d}"
            for local_index in range(12):
                number += 1
                form = LANGUAGE_FORMS[local_index // 2]
                turns = [action] if local_index >= 3 else [action, "opaque-context"]
                scenarios.append(
                    {
                        "scenario_id": f"s{number:03d}",
                        "group_id": group,
                        "action": action,
                        "language_form": form,
                        "turn_count": len(turns),
                        "coverage_cell": f"c{number:03d}",
                        "utterances": turns,
                        "diary_state": {"state_kind": "empty", "appointments": []},
                        "expected": _expected(action),
                    }
                )
    return {
        "schema_version": FIXTURE_SCHEMA,
        "attempt_id": attempt_id,
        "reference_date": "2026-07-17",
        "provenance": "fresh_sol_synthetic_gold_lc4v10_only",
        "scenarios": scenarios,
    }


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


def _bundle(tmp_path: Path) -> tuple[RunPaths, str, dict[str, Any]]:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "tests@emr4.local")
    _git(root, "config", "user.name", "EMR4 Tests")

    fixture_path = root / "protected" / "fixture.json"
    framework_path = root / "app" / "services" / "bernie" / "lc4v10_content_blind_framework.py"
    evaluator_path = framework_path
    thresholds_path = root / "protected" / "thresholds.json"
    manifest_path = root / "protected" / "manifest.json"
    seal_path = root / "protected" / "seal.json"
    marker_path = root / "protected" / "attempt.marker.json"
    report_path = root / "protected" / "aggregate.json"
    attempt_id = "lc4v10-fresh-certification-001"

    fixture = _fixture(attempt_id)
    fixture_bytes = _write_json(fixture_path, fixture)
    framework_path.parent.mkdir(parents=True, exist_ok=True)
    framework_bytes = Path(framework.__file__).read_bytes()
    framework_path.write_bytes(framework_bytes)
    threshold_bytes = _write_json(
        thresholds_path, {"schema_version": THRESHOLD_SCHEMA, **THRESHOLDS}
    )
    _git(root, "add", "--", "protected/fixture.json", "protected/thresholds.json", framework_path.relative_to(root).as_posix())
    _git(root, "commit", "-q", "-m", "freeze opaque source")
    source = _git(root, "rev-parse", "HEAD")

    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "attempt_id": attempt_id,
        "corpus_source_commit": source,
        "fixture_path": "protected/fixture.json",
        "fixture_sha256": _sha(fixture_bytes),
        "fixture_git_blob": _blob(fixture_bytes),
        "framework_path": framework_path.relative_to(root).as_posix(),
        "framework_sha256": _sha(framework_bytes),
        "framework_git_blob": _blob(framework_bytes),
        "evaluator_path": evaluator_path.relative_to(root).as_posix(),
        "evaluator_sha256": _sha(framework_bytes),
        "evaluator_git_blob": _blob(framework_bytes),
        "thresholds_path": "protected/thresholds.json",
        "thresholds_sha256": _sha(threshold_bytes),
        "thresholds_git_blob": _blob(threshold_bytes),
    }
    manifest_bytes = _write_json(manifest_path, manifest)
    _write_json(
        seal_path,
        {
            "schema_version": SEAL_SCHEMA,
            "attempt_id": attempt_id,
            "manifest_sha256": _sha(manifest_bytes),
            "thresholds_sha256": _sha(threshold_bytes),
            "state": "unconsumed",
        },
    )
    return (
        RunPaths(
            repo_root=root,
            attempt_id=attempt_id,
            fixture_path=fixture_path,
            framework_path=framework_path,
            evaluator_path=evaluator_path,
            manifest_path=manifest_path,
            thresholds_path=thresholds_path,
            seal_path=seal_path,
            marker_path=marker_path,
            report_path=report_path,
        ),
        source,
        fixture,
    )


def _opaque_observer(payload: dict[str, Any]) -> dict[str, Any]:
    assert set(payload) == {"utterances", "diary_state", "reference_date"}
    return _expected(payload["utterances"][0])


def test_fixture_has_288_scenarios_without_repeat_rows() -> None:
    fixture = _fixture()
    assert len(fixture["scenarios"]) == 288
    assert all("repeat_index" not in scenario for scenario in fixture["scenarios"])
    assert not validate_fixture(fixture, fixture["attempt_id"])


@pytest.mark.parametrize(
    "mutation, failure",
    [
        (lambda value: value.update({"unknown": 1}), "fixture_schema_errors"),
        (lambda value: value["scenarios"].pop(), "scenario_population_errors"),
        (lambda value: value["scenarios"][0].update({"repeat_index": 0}), "scenario_schema_errors"),
        (lambda value: value["scenarios"][0].update({"scenario_id": "s002"}), "scenario_identity_errors"),
        (lambda value: value["scenarios"][0].update({"coverage_cell": "c002"}), "coverage_identity_errors"),
        (lambda value: value["scenarios"][0].update({"turn_count": 1}), "turn_shape_errors"),
        (lambda value: value["scenarios"][0]["expected"].pop("safety"), "expected_schema_errors"),
    ],
)
def test_fixture_validation_fails_closed(mutation, failure: str) -> None:
    fixture = _fixture()
    mutation(fixture)
    assert validate_fixture(fixture, fixture["attempt_id"])[failure] > 0


def test_projection_and_expected_cross_fields_fail_closed() -> None:
    projection = _projection("move")
    projection["selected_tools"] = []
    expected = _expected("move")
    expected["exact_policy_projection"] = projection
    assert validate_expected(expected, "move")["expected_cross_field_errors"] > 0
    projection["unknown"] = True
    assert validate_projection(projection)["projection_schema_errors"] > 0


def test_thresholds_are_exact() -> None:
    valid = {"schema_version": THRESHOLD_SCHEMA, **THRESHOLDS}
    assert not validate_thresholds(valid)
    invalid = {**valid, "complete_min": 0}
    assert validate_thresholds(invalid)["threshold_value_errors"] == 1


def test_missing_dimensions_never_pass() -> None:
    assert validate_observation({})["missing_or_unknown_dimensions"] == 1
    with pytest.raises(ValueError):
        score_observation({}, {})


def test_valid_one_shot_passes_and_consumes(monkeypatch, tmp_path: Path) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)
    monkeypatch.setattr(framework, "ordinary_product_observer", _opaque_observer)
    result = run_one_shot(paths, source)
    assert result["decision"] == CERTIFICATION_PASS
    assert result["attempted_samples"] == 576
    assert result["dimension_counts"]["complete"] == 576
    assert not result["evidence_failures"]
    assert not result["product_gate_failures"]
    assert json.loads(paths.marker_path.read_text(encoding="utf-8"))["state"] == "consumed"
    assert json.loads(paths.seal_path.read_text(encoding="utf-8"))["state"] == "consumed"
    assert json.loads(paths.report_path.read_text(encoding="utf-8")) == result


def test_observer_receives_no_oracle_or_identity_metadata(monkeypatch, tmp_path: Path) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)
    observed_keys: list[set[str]] = []

    def observer(payload: dict[str, Any]) -> dict[str, Any]:
        observed_keys.append(set(payload))
        return _opaque_observer(payload)

    monkeypatch.setattr(framework, "ordinary_product_observer", observer)
    result = run_one_shot(paths, source)
    assert result["decision"] == CERTIFICATION_PASS
    assert observed_keys and all(
        keys == {"utterances", "diary_state", "reference_date"}
        for keys in observed_keys
    )


def test_marker_exists_before_fixture_read(monkeypatch, tmp_path: Path) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)
    original = Path.read_bytes

    def guarded(path: Path) -> bytes:
        if path.resolve() == paths.fixture_path.resolve():
            assert paths.marker_path.exists()
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    monkeypatch.setattr(framework, "ordinary_product_observer", _opaque_observer)
    assert run_one_shot(paths, source)["decision"] == CERTIFICATION_PASS


def test_existing_marker_blocks_before_fixture_read(monkeypatch, tmp_path: Path) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)
    _write_json(
        paths.marker_path,
        {"schema_version": MARKER_SCHEMA, "attempt_id": paths.attempt_id, "state": "consumed"},
    )
    reads = 0
    original = Path.read_bytes

    def guarded(path: Path) -> bytes:
        nonlocal reads
        if path.resolve() == paths.fixture_path.resolve():
            reads += 1
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    with pytest.raises(AttemptUnavailable):
        run_one_shot(paths, source)
    assert reads == 0


def test_runtime_exception_consumes_attempt(monkeypatch, tmp_path: Path) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)

    def explode(_payload: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("opaque failure")

    monkeypatch.setattr(framework, "ordinary_product_observer", explode)
    result = run_one_shot(paths, source)
    assert result["decision"] == CERTIFICATION_INVALID
    assert result["evidence_failures"] == {"runtime_exceptions": 1}
    assert json.loads(paths.marker_path.read_text(encoding="utf-8"))["state"] == "consumed"
    assert json.loads(paths.seal_path.read_text(encoding="utf-8"))["state"] == "consumed"


def test_missing_dimension_consumes_as_invalid(monkeypatch, tmp_path: Path) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)

    def missing(payload: dict[str, Any]) -> dict[str, Any]:
        value = _opaque_observer(payload)
        value.pop("safety")
        return value

    monkeypatch.setattr(framework, "ordinary_product_observer", missing)
    result = run_one_shot(paths, source)
    assert result["decision"] == CERTIFICATION_INVALID
    assert result["evidence_failures"]["missing_or_unknown_dimensions"] > 0


def test_repeat_variance_is_evidence_invalid(monkeypatch, tmp_path: Path) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)
    calls = 0

    def variable(payload: dict[str, Any]) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        value = _opaque_observer(payload)
        value["action_semantics"] = "requested" if calls % 2 else "different"
        return value

    monkeypatch.setattr(framework, "ordinary_product_observer", variable)
    result = run_one_shot(paths, source)
    assert result["decision"] == CERTIFICATION_INVALID
    assert result["evidence_failures"]["repeat_variance"] == 288


def test_valid_evidence_product_miss_is_certification_fail(monkeypatch, tmp_path: Path) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)

    def wrong(payload: dict[str, Any]) -> dict[str, Any]:
        value = _opaque_observer(payload)
        value["action_semantics"] = "wrong"
        return value

    monkeypatch.setattr(framework, "ordinary_product_observer", wrong)
    result = run_one_shot(paths, source)
    assert result["decision"] == CERTIFICATION_FAIL
    assert not result["evidence_failures"]
    assert result["product_gate_failures"]


@pytest.mark.parametrize("kind", ["fixture", "framework", "evaluator", "thresholds"])
def test_every_source_blob_is_bound(monkeypatch, tmp_path: Path, kind: str) -> None:
    paths, source, _fixture_value = _bundle(tmp_path)
    manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
    manifest[f"{kind}_sha256"] = "0" * 64
    manifest_bytes = _write_json(paths.manifest_path, manifest)
    seal = json.loads(paths.seal_path.read_text(encoding="utf-8"))
    seal["manifest_sha256"] = _sha(manifest_bytes)
    _write_json(paths.seal_path, seal)
    monkeypatch.setattr(framework, "ordinary_product_observer", _opaque_observer)
    result = run_one_shot(paths, source)
    assert result["decision"] == CERTIFICATION_INVALID
    assert result["evidence_failures"]["byte_binding_errors"] > 0


def test_git_ancestry_is_mandatory(monkeypatch, tmp_path: Path) -> None:
    paths, _source, _fixture_value = _bundle(tmp_path)
    monkeypatch.setattr(framework, "ordinary_product_observer", _opaque_observer)
    result = run_one_shot(paths, "0" * 40)
    assert result["decision"] == CERTIFICATION_INVALID
    assert result["evidence_failures"]["git_ancestry_errors"] == 1


def test_report_is_exact_aggregate_only(monkeypatch, tmp_path: Path) -> None:
    paths, source, fixture = _bundle(tmp_path)
    sentinel = "never-emit-this-opaque-value"
    fixture["scenarios"][0]["utterances"] = [sentinel, "opaque-context"]
    fixture_bytes = _write_json(paths.fixture_path, fixture)
    _git(paths.repo_root, "add", "--", "protected/fixture.json")
    _git(paths.repo_root, "commit", "-q", "-m", "replace opaque source")
    new_source = _git(paths.repo_root, "rev-parse", "HEAD")
    manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
    manifest["corpus_source_commit"] = new_source
    manifest["fixture_sha256"] = _sha(fixture_bytes)
    manifest["fixture_git_blob"] = _blob(fixture_bytes)
    manifest_bytes = _write_json(paths.manifest_path, manifest)
    seal = json.loads(paths.seal_path.read_text(encoding="utf-8"))
    seal["manifest_sha256"] = _sha(manifest_bytes)
    _write_json(paths.seal_path, seal)
    monkeypatch.setattr(framework, "ordinary_product_observer", _opaque_observer)
    result = run_one_shot(paths, new_source)
    encoded = json.dumps(result, sort_keys=True)
    assert set(result) == {
        "schema_version",
        "attempt_id",
        "attempted_samples",
        "dimension_counts",
        "group_complete_counts",
        "language_form_complete_counts",
        "evidence_failures",
        "product_gate_failures",
        "decision",
        "seal_state",
        "marker_state",
        "report_hash",
    }
    assert result["schema_version"] == REPORT_SCHEMA
    assert sentinel not in encoded
    assert "scenario_id" not in encoded
    assert "expected" not in encoded


def test_ordinary_observer_has_exact_dimension_contract() -> None:
    result = framework.ordinary_product_observer(
        {
            "utterances": ["Book an appointment for Opaque Person with Dr Shera tomorrow at 3 pm"],
            "diary_state": {"state_kind": "empty", "appointments": []},
            "reference_date": "2026-07-17",
        }
    )
    assert set(result) == set(DIMENSIONS)
    assert not validate_observation(result)


def test_classifier_is_imported_not_reimplemented() -> None:
    source = Path(framework.__file__).read_text(encoding="utf-8")
    assert "from app.services.bernie.certification_decision_taxonomy import" in source
    assert "def classify_certification" not in source
