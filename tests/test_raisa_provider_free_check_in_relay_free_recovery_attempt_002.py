from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_check_in_relay_free_recovery_attempt_002 as attempt,
)


ROOT = Path(__file__).resolve().parents[1]


def test_static_admission_preserves_accepted_harness_and_hostile_gates() -> None:
    result = attempt.static_check()
    assert result["status"] == "passed"
    assert result["accepted_harness_sha256"] == attempt.ACCEPTED_HARNESS_SHA256
    assert hashlib.sha256(Path(attempt.accepted.__file__).read_bytes()).hexdigest() == (
        attempt.ACCEPTED_HARNESS_SHA256
    )
    assert result["contract_mutations"]["attempted"] >= 256
    assert result["contract_mutations"]["attempted"] == result[
        "contract_mutations"
    ]["rejected"]
    assert result["manifest_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["state_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["classifier_mutations"] == {"attempted": 24, "rejected": 24}


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
    with attempt._attempt_002_terminal_bindings():
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
        with attempt._attempt_002_terminal_bindings():
            raise RuntimeError("injected_binding_failure")
    assert attempt._bindings_are_historical()


def test_terminal_collision_fails_closed(tmp_path: Path) -> None:
    collision = tmp_path / "attempt-002-execution-envelope.json"
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
    hostile = json.loads(json.dumps(envelope))
    hostile["automatic_retry_count"] = 1
    with pytest.raises(
        attempt.accepted.RehearsalFailure,
        match="execution_envelope_schema_invalid",
    ):
        attempt._validate_envelope(hostile)
