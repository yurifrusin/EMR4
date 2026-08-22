from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    raisa_authored_synthetic_native_harness_corrected_guard_graph_first_useful_development_recovery_rehearsal
    as subject,
)


def test_integrated_runner_derivation_is_exact_and_keeps_typed_controls() -> None:
    target = (
        subject.ATTEMPT_ROOT
        / "workspace"
        / subject.accepted_controller.SYNTHETIC_PATH
    ).resolve().as_posix()
    reading = subject.validate_integrated_runner_source(
        subject.integrated_runner_source(target)
    )
    assert reading["bytes"] != subject.ACCEPTED_RUNNER_BYTES
    assert all(reading["checks"].values())
    accepted_literal = (
        f"const TARGET_PATH = {json.dumps(subject.ACCEPTED_RUNNER_TARGET)};"
    )
    derived_literal = f"const TARGET_PATH = {json.dumps(target)};"
    restored = (
        subject.integrated_runner_source(target)
        .decode("utf-8")
        .replace(derived_literal, accepted_literal)
        .encode("utf-8")
    )
    assert restored == subject.accepted_graph_sources()["runner"]


def test_runner_rejects_unfrozen_target() -> None:
    with pytest.raises(subject.IntegratedDevelopmentError, match="not_exact"):
        subject.validate_integrated_runner_source(
            subject.integrated_runner_source("C:/unfrozen/other.py")
        )


def test_contract_schema_is_closed() -> None:
    schema = json.loads(subject.CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["planning_source"]["const"] == subject.PLANNING_SOURCE


def test_terminal_schema_binds_exact_identity() -> None:
    schema = json.loads(subject.TERMINAL_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["operation_id"]["const"] == subject.OPERATION_ID
    assert schema["properties"]["attempt_id"]["const"] == subject.ATTEMPT_ID


def test_work_package_retains_public_and_holdback_behavior(tmp_path: Path) -> None:
    target = tmp_path / subject.accepted_controller.SYNTHETIC_PATH
    target.write_text(
        subject.accepted_controller.EXPECTED_SOURCE,
        encoding="utf-8",
        newline="\n",
    )
    assert subject.accepted_controller._run_synthetic_cases(target) == {
        "executed": True,
        "public_passed": 4,
        "holdback_passed": 3,
    }


def test_context_rebinds_and_restores_runner_functions() -> None:
    original_source = subject.accepted_controller.runner_source
    original_validator = subject.accepted_controller.validate_runner_source
    original_materializer = subject.accepted_controller.materialize_profile
    original_guard = subject.accepted_controller.guard.build_guard_source
    with subject.configured_accepted_attempt():
        assert subject.accepted_controller.runner_source is subject.integrated_runner_source
        assert (
            subject.accepted_controller.validate_runner_source
            is subject.validate_integrated_runner_source
        )
        assert subject.accepted_controller.materialize_profile is not original_materializer
        assert (
            subject.accepted_controller.guard.build_guard_source()
            == subject.accepted_graph_sources()["guard"]
        )
        assert subject.accepted_attempt.OPERATION_ID == subject.OPERATION_ID
    assert subject.accepted_controller.runner_source is original_source
    assert subject.accepted_controller.validate_runner_source is original_validator
    assert subject.accepted_controller.materialize_profile is original_materializer
    assert subject.accepted_controller.guard.build_guard_source is original_guard


def test_context_resolves_graph_before_guard_rebinding(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subject, "_ACCEPTED_GRAPH_CACHE", None)
    with subject.configured_accepted_attempt():
        assert (
            subject.accepted_controller.guard.build_guard_source()
            == subject.accepted_graph_sources()["guard"]
        )


def test_corrected_graph_materialization_is_exact_and_import_closed(
    tmp_path: Path,
) -> None:
    proof = tmp_path / "proof"
    proof.mkdir()
    target = "C:/synthetic-native-worker/synthetic_window_coalescer.py"
    sources = subject.accepted_graph_sources()
    (proof / "runner.mjs").write_bytes(subject.integrated_runner_source(target))
    for name, filename in subject.GRAPH_FILENAMES.items():
        (proof / filename).write_bytes(sources[name])
    reading = subject.validate_corrected_graph_directory(proof, target)
    assert set(reading) == {"runner", "guard", "bridge", "sanitizer"}
    assert reading["guard"] == subject.ACCEPTED_GRAPH_INVENTORY["guard"]


def test_plan_freezes_one_request_and_terminal_harness_stop() -> None:
    plan = subject.PLAN_PATH.read_text(encoding="utf-8")
    assert "maximum DeepSeek provider requests: one" in plan
    assert "Never retry or resume" in plan
    assert "returns to unavailable for EMR4" in plan


def test_provider_free_boundary_ceiling_is_closed() -> None:
    expected = {
        "native_processes": 1,
        "sessions": 1,
        "turns": 1,
        "provider_requests": 1,
        "direct_literal_edits": 1,
        "retries": 0,
        "resumes": 0,
        "fallbacks": 0,
        "auxiliary_models": 0,
    }
    assert subject.contract_value()["ceilings"] == expected
