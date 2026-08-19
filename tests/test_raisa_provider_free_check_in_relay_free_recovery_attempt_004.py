from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from scripts import raisa_provider_free_check_in_relay_free_recovery_attempt_004 as attempt


def test_static_admission_binds_repaired_harness_and_all_predecessors() -> None:
    result = attempt.static_check(require_empty_namespace=False)
    assert result["status"] == "passed"
    assert len(str(result["source_head"])) == 40
    assert result["plan_source"] == "7bbc0eb6466811c323006ddb6bcc80a3a6fcb679"
    assert result["corrected_harness_sha256"] == (
        "eda68427b87db48064bcfb82762d55c51b600cf2ba5d4724a0faae24d8a3db5b"
    )
    assert hashlib.sha256(Path(attempt.accepted.__file__).read_bytes()).hexdigest() == (
        result["corrected_harness_sha256"]
    )
    assert result["contract_mutations"] == {"attempted": 366, "rejected": 366}
    assert result["manifest_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["state_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["classifier_mutations"] == {"attempted": 24, "rejected": 24}
    assert result["terminal_namespace_empty"] is False


def test_wrapper_exposes_only_check_and_execute() -> None:
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
    with attempt._attempt_004_terminal_bindings():
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
        with attempt._attempt_004_terminal_bindings():
            raise RuntimeError("injected_binding_failure")
    assert attempt._bindings_are_historical()


def test_terminal_collision_fails_closed(tmp_path: Path) -> None:
    collision = tmp_path / "attempt-004-execution-envelope.json"
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
    assert envelope["attempt_id"] == "attempt-004"
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["ambiguous_success_released"] is False
    assert envelope["predecessor_003_cleanup_sha256"] == (
        "048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71"
    )
    hostile = json.loads(json.dumps(envelope))
    hostile["automatic_retry_count"] = 1
    with pytest.raises(
        attempt.accepted.RehearsalFailure,
        match="execution_envelope_schema_invalid",
    ):
        attempt._validate_envelope(hostile)


def test_consumed_attempts_and_attempt_004_terminal_evidence_are_immutable() -> None:
    assert attempt._sha256(
        attempt.PREDECESSOR_003_TOPIC / "rehearsal-failure-evidence.json"
    ) == attempt.HASH_BINDINGS["predecessor_003_failure_sha256"][1]
    assert attempt._sha256(
        attempt.PREDECESSOR_003_TOPIC / "attempt-003-execution-envelope.json"
    ) == attempt.HASH_BINDINGS["predecessor_003_envelope_sha256"][1]
    assert attempt._sha256(
        attempt.PREDECESSOR_003_TOPIC / "attempt-003-cleanup-recovery.json"
    ) == attempt.HASH_BINDINGS["predecessor_003_cleanup_sha256"][1]
    assert attempt._sha256(attempt.FAILURE_PATH) == (
        "1ccc86c76826aa805a48a8823186f5b0eee6e0b571f6deff59ece0474f5df4d3"
    )
    assert attempt._sha256(attempt.ENVELOPE_PATH) == (
        "415f054f10639c2dba2466842ad7b957ce9a66f71f48bf07abe5bfdf4e47e7d5"
    )


def test_attempt_004_failure_envelope_is_closed_sanitized_and_non_retriable() -> None:
    failure = json.loads(attempt.FAILURE_PATH.read_text(encoding="utf-8"))
    envelope = json.loads(attempt.ENVELOPE_PATH.read_text(encoding="utf-8"))
    attempt.accepted._assert_redacted(failure, forbidden_values=())
    attempt._validate_envelope(envelope)
    assert failure["code"] == "server_not_ready_or_identity_mismatch"
    assert failure["stage"] == "environment"
    assert failure["retry_count"] == 0
    assert failure["success_released"] is False
    assert failure["cleanup"]["status"] == "cleanup_verified"
    assert failure["cleanup"]["matching_owned_resources"] == 0
    assert envelope["source_head"] == (
        "932ae6ce02e0e973a22dfe999601087295001d1b"
    )
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["ambiguous_success_released"] is False
    assert envelope["ordinary_admission_release_count"] == 0
    assert envelope["product_record_count"] == 0
    assert envelope["terminal_artifact_sha256"] == attempt._sha256(
        attempt.FAILURE_PATH
    )
    assert envelope["cleanup_status"] == "cleanup_verified"
    assert envelope["terminal_binding_restored"] is True


def test_failure_evidence_is_sanitized_and_attempt_scoped() -> None:
    value = attempt._sanitized_failure(
        attempt.accepted.RehearsalFailure("attempt_004_static", "injected_denial")
    )
    attempt.accepted._assert_redacted(value, forbidden_values=())
    serialized = json.dumps(value, sort_keys=True)
    assert "attempt_004_wrapper_failed_closed" in serialized
    assert "injected_denial" in serialized
