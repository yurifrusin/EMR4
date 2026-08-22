from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    raisa_authored_synthetic_native_harness_integrated_runner_first_controlled_development_rehearsal
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
    assert reading["bytes"] > subject.ACCEPTED_RUNNER_BYTES
    assert all(reading["checks"].values())


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
    with subject.configured_accepted_attempt():
        assert subject.accepted_controller.runner_source is subject.integrated_runner_source
        assert (
            subject.accepted_controller.validate_runner_source
            is subject.validate_integrated_runner_source
        )
        assert subject.accepted_attempt.OPERATION_ID == subject.OPERATION_ID
    assert subject.accepted_controller.runner_source is original_source
    assert subject.accepted_controller.validate_runner_source is original_validator


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
