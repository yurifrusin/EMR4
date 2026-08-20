from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from scripts import raisa_provider_free_check_in_relay_free_recovery_attempt_005 as attempt


def test_static_admission_binds_repaired_harness_and_full_commit_lineage() -> None:
    result = attempt.static_check(require_empty_namespace=False)
    assert result["status"] == "passed"
    assert len(str(result["source_head"])) == 40
    assert result["plan_source"] == "d8eec606735ed7d1b5ab089c0c33b8d4469d612f"
    assert result["repaired_harness_sha256"] == (
        "62a18d9ce2a29eb417f491c8ce341416f03183375f042f8c41bcb1f4674df77c"
    )
    assert hashlib.sha256(Path(attempt.accepted.__file__).read_bytes()).hexdigest() == (
        result["repaired_harness_sha256"]
    )
    for source in attempt.GIT_SOURCES.values():
        assert attempt.accepted.HEX40.fullmatch(source)
    for category in (
        "contract_mutations",
        "manifest_mutations",
        "state_mutations",
        "classifier_mutations",
    ):
        counts = result[category]
        assert counts["attempted"] > 0
        assert counts["rejected"] == counts["attempted"]


def test_abbreviated_git_binding_fails_before_object_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shortened = dict(attempt.GIT_SOURCES)
    shortened["plan_source"] = shortened["plan_source"][:7]
    monkeypatch.setattr(attempt, "GIT_SOURCES", shortened)
    with pytest.raises(
        attempt.accepted.RehearsalFailure,
        match="source_binding_not_full_commit",
    ):
        attempt._source_head()


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


def test_terminal_binding_is_exact_and_restored() -> None:
    originals = (
        attempt.accepted.ATTESTATION_PATH,
        attempt.accepted.EVIDENCE_PATH,
        attempt.accepted.FAILURE_PATH,
    )
    with attempt._attempt_005_terminal_bindings():
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
        with attempt._attempt_005_terminal_bindings():
            raise RuntimeError("injected_binding_failure")
    assert attempt._bindings_are_historical()


def test_terminal_collision_fails_closed(tmp_path: Path) -> None:
    collision = tmp_path / "attempt-005-execution-envelope.json"
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
    assert envelope["attempt_id"] == "attempt-005"
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["ambiguous_success_released"] is False
    assert envelope["terminal_binding_restored"] is True
    hostile = json.loads(json.dumps(envelope))
    hostile["automatic_retry_count"] = 1
    with pytest.raises(
        attempt.accepted.RehearsalFailure,
        match="execution_envelope_schema_invalid",
    ):
        attempt._validate_envelope(hostile)


def test_attempt_004_terminal_evidence_and_all_hash_bindings_are_immutable() -> None:
    for _, (path, expected) in attempt.HASH_BINDINGS.items():
        assert attempt._sha256(path) == expected
    assert attempt._sha256(attempt.ATTEMPT_004_TOPIC / "rehearsal-failure-evidence.json") == (
        "1ccc86c76826aa805a48a8823186f5b0eee6e0b571f6deff59ece0474f5df4d3"
    )
    assert attempt._sha256(
        attempt.ATTEMPT_004_TOPIC / "attempt-004-execution-envelope.json"
    ) == "415f054f10639c2dba2466842ad7b957ce9a66f71f48bf07abe5bfdf4e47e7d5"


def test_run_attempt_routes_exact_paths_and_restores_globals(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    envelope_path = tmp_path / "attempt-005-execution-envelope.json"
    attestation_path = tmp_path / "transaction-attestation.json"
    evidence_path = tmp_path / "rehearsal-evidence.json"
    failure_path = tmp_path / "rehearsal-failure-evidence.json"
    monkeypatch.setattr(attempt, "ENVELOPE_PATH", envelope_path)
    monkeypatch.setattr(attempt, "ATTESTATION_PATH", attestation_path)
    monkeypatch.setattr(attempt, "EVIDENCE_PATH", evidence_path)
    monkeypatch.setattr(attempt, "FAILURE_PATH", failure_path)
    monkeypatch.setattr(
        attempt,
        "TERMINAL_PATHS",
        (envelope_path, attestation_path, evidence_path, failure_path),
    )

    def fake_run_rehearsal() -> tuple[dict[str, object], dict[str, object]]:
        assert attempt.accepted.ATTESTATION_PATH == attestation_path
        assert attempt.accepted.EVIDENCE_PATH == evidence_path
        assert attempt.accepted.FAILURE_PATH == failure_path
        evidence: dict[str, object] = {
            "result": attempt.accepted.PASS_RESULT,
            "cleanup": {"status": "cleanup_verified"},
            "ordinary_admission_release_count": 0,
            "product_record_count": 0,
        }
        attempt.accepted._write_json(evidence_path, evidence)
        return evidence, None

    monkeypatch.setattr(attempt.accepted, "run_rehearsal", fake_run_rehearsal)
    result = attempt.run_attempt()
    assert result["result"] == attempt.PASS_RESULT
    assert result["terminal_artifact_kind"] == "rehearsal_evidence"
    assert result["terminal_artifact_sha256"] == attempt._sha256(evidence_path)
    assert envelope_path.exists()
    assert not failure_path.exists()
    assert attempt._bindings_are_historical()


def test_failure_evidence_is_sanitized_and_attempt_scoped() -> None:
    value = attempt._sanitized_failure(
        attempt.accepted.RehearsalFailure("attempt_005_static", "injected_denial")
    )
    attempt.accepted._assert_redacted(value, forbidden_values=())
    serialized = json.dumps(value, sort_keys=True)
    assert "attempt_005_wrapper_failed_closed" in serialized
    assert "injected_denial" in serialized
