from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_check_in_relay_free_recovery_attempt_003 as attempt,
)


def test_static_admission_binds_corrected_harness_and_consumed_predecessors() -> None:
    result = attempt.static_check(require_empty_namespace=False)
    assert result["status"] == "passed"
    assert result["source_head"] and len(str(result["source_head"])) == 40
    assert result["corrected_harness_sha256"] == attempt.CORRECTED_HARNESS_SHA256
    assert hashlib.sha256(Path(attempt.accepted.__file__).read_bytes()).hexdigest() == (
        attempt.CORRECTED_HARNESS_SHA256
    )
    assert result["contract_mutations"] == {"attempted": 366, "rejected": 366}
    assert result["manifest_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["state_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["classifier_mutations"] == {"attempted": 24, "rejected": 24}
    assert result["terminal_namespace_empty"] is False


def test_wrapper_exposes_no_output_path_argument() -> None:
    source = Path(attempt.__file__).read_text(encoding="utf-8")
    module = ast.parse(source)
    option_strings = {
        argument.value
        for node in ast.walk(module)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_argument"
        for argument in node.args
        if isinstance(argument, ast.Constant) and isinstance(argument.value, str)
    }
    assert option_strings == {"--check", "--execute"}


def test_terminal_binding_is_exact_and_restored_on_success() -> None:
    originals = (
        attempt.accepted.ATTESTATION_PATH,
        attempt.accepted.EVIDENCE_PATH,
        attempt.accepted.FAILURE_PATH,
    )
    with attempt._attempt_003_terminal_bindings():
        assert attempt.accepted.ATTESTATION_PATH == attempt.ATTESTATION_PATH
        assert attempt.accepted.EVIDENCE_PATH == attempt.EVIDENCE_PATH
        assert attempt.accepted.FAILURE_PATH == attempt.FAILURE_PATH
    assert (
        attempt.accepted.ATTESTATION_PATH,
        attempt.accepted.EVIDENCE_PATH,
        attempt.accepted.FAILURE_PATH,
    ) == originals
    assert attempt._bindings_are_historical()


def test_terminal_binding_is_restored_on_exception() -> None:
    with pytest.raises(RuntimeError, match="injected_binding_failure"):
        with attempt._attempt_003_terminal_bindings():
            raise RuntimeError("injected_binding_failure")
    assert attempt._bindings_are_historical()


def test_terminal_collision_fails_closed(tmp_path: Path) -> None:
    collision = tmp_path / "attempt-003-execution-envelope.json"
    collision.write_text("occupied", encoding="utf-8")
    with pytest.raises(
        attempt.accepted.RehearsalFailure,
        match="terminal_artifact_already_exists",
    ):
        attempt._assert_terminal_namespace_empty((collision,))


def test_execution_envelope_is_closed_and_binds_one_attempt(tmp_path: Path) -> None:
    terminal = tmp_path / "rehearsal-failure-evidence.json"
    terminal.write_text('{"result":"failed_closed"}\n', encoding="utf-8")
    envelope = attempt._build_execution_envelope(
        source_head="a" * 40,
        evidence={
            "result": "failed_closed",
            "cleanup": {"status": "cleanup_verified"},
            "ordinary_admission_release_count": 0,
            "product_record_count": 0,
        },
        terminal_path=terminal,
        terminal_kind="rehearsal_failure_evidence",
    )
    attempt._validate_envelope(envelope)
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["ambiguous_success_released"] is False
    assert envelope["created_state_correction_source"] == (
        attempt.CREATED_STATE_CORRECTION_SOURCE
    )
    hostile = json.loads(json.dumps(envelope))
    hostile["automatic_retry_count"] = 1
    with pytest.raises(
        attempt.accepted.RehearsalFailure,
        match="execution_envelope_schema_invalid",
    ):
        attempt._validate_envelope(hostile)


def test_consumed_attempt_002_is_immutable_and_attempt_003_is_terminal() -> None:
    assert attempt._sha256(attempt.PREDECESSOR_002_FAILURE_PATH) == (
        attempt.PREDECESSOR_002_FAILURE_SHA256
    )
    assert attempt._sha256(attempt.PREDECESSOR_002_ENVELOPE_PATH) == (
        attempt.PREDECESSOR_002_ENVELOPE_SHA256
    )
    assert attempt.ENVELOPE_PATH.exists()
    assert attempt.FAILURE_PATH.exists()
    assert not attempt.EVIDENCE_PATH.exists()
    assert not attempt.ATTESTATION_PATH.exists()
    envelope = json.loads(attempt.ENVELOPE_PATH.read_text(encoding="utf-8"))
    attempt._validate_envelope(envelope)
    assert envelope["result"] == "failed_closed"
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["ambiguous_success_released"] is False


def test_cleanup_recovery_is_closed_and_binds_terminal_artifacts() -> None:
    recovery_path = attempt.TOPIC / "attempt-003-cleanup-recovery.json"
    schema_path = attempt.TOPIC / "attempt-003-cleanup-recovery.schema.json"
    recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(recovery)
    assert recovery["failure_artifact_sha256"] == attempt._sha256(
        attempt.FAILURE_PATH
    )
    assert recovery["execution_envelope_sha256"] == attempt._sha256(
        attempt.ENVELOPE_PATH
    )
    assert recovery["matching_owned_resources"] == 0
    assert recovery["proof_rerun"] is False
