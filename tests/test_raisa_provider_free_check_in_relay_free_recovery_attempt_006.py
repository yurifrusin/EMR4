from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_check_in_relay_free_recovery_attempt_006 as attempt,
)


ROOT = Path(__file__).resolve().parents[1]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bind_terminal_paths(
    monkeypatch: pytest.MonkeyPatch, root: Path
) -> tuple[Path, Path, Path, Path]:
    envelope = root / "attempt-006-execution-envelope.json"
    attestation = root / "transaction-attestation.json"
    evidence = root / "rehearsal-evidence.json"
    failure = root / "rehearsal-failure-evidence.json"
    monkeypatch.setattr(attempt, "ENVELOPE_PATH", envelope)
    monkeypatch.setattr(attempt, "ATTESTATION_PATH", attestation)
    monkeypatch.setattr(attempt, "EVIDENCE_PATH", evidence)
    monkeypatch.setattr(attempt, "FAILURE_PATH", failure)
    monkeypatch.setattr(
        attempt, "TERMINAL_PATHS", (envelope, attestation, evidence, failure)
    )
    return envelope, attestation, evidence, failure


def test_static_admission_binds_repaired_lifecycle_and_hostile_gates() -> None:
    result = attempt.static_check()
    assert result["status"] == "passed"
    assert result["plan_source"] == attempt.GIT_SOURCES["plan_source"]
    assert result["base_static_status"] == "passed"
    assert result["terminal_namespace_empty"] is True
    assert result["contract_mutations"]["attempted"] >= 256
    assert result["contract_mutations"]["attempted"] == result[
        "contract_mutations"
    ]["rejected"]
    assert result["manifest_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["state_mutations"] == {"attempted": 96, "rejected": 96}
    assert result["classifier_mutations"] == {"attempted": 24, "rejected": 24}


def test_all_git_sources_are_full_commit_ancestors() -> None:
    head = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD^{commit}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    for source in attempt.GIT_SOURCES.values():
        assert attempt.accepted.HEX40.fullmatch(source)
        assert subprocess.run(
            ["git", "cat-file", "-t", source],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip() == "commit"
        assert (
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", source, head],
                cwd=ROOT,
                check=False,
                capture_output=True,
            ).returncode
            == 0
        )


def test_hash_bindings_are_exact_and_predecessors_remain_immutable() -> None:
    before = {name: _digest(path) for name, (path, _) in attempt.HASH_BINDINGS.items()}
    for name, (path, expected) in attempt.HASH_BINDINGS.items():
        assert before[name] == expected
        assert attempt.accepted.HEX64.fullmatch(expected)
    attempt.static_check()
    after = {name: _digest(path) for name, (path, _) in attempt.HASH_BINDINGS.items()}
    assert after == before


def test_terminal_namespace_collision_is_denied(tmp_path: Path) -> None:
    paths = tuple(tmp_path / name for name in ("a", "b", "c", "d"))
    attempt._assert_terminal_namespace_empty(paths)
    paths[2].write_text("occupied", encoding="utf-8")
    with pytest.raises(attempt.accepted.RehearsalFailure) as caught:
        attempt._assert_terminal_namespace_empty(paths)
    assert caught.value.stage == "attempt_006_execution"
    assert caught.value.code == "terminal_artifact_already_exists"


def test_terminal_binding_context_restores_after_exception() -> None:
    originals = (
        attempt.accepted.ATTESTATION_PATH,
        attempt.accepted.EVIDENCE_PATH,
        attempt.accepted.FAILURE_PATH,
    )
    with pytest.raises(RuntimeError):
        with attempt._attempt_006_terminal_bindings():
            assert attempt.accepted.ATTESTATION_PATH == attempt.ATTESTATION_PATH
            assert attempt.accepted.EVIDENCE_PATH == attempt.EVIDENCE_PATH
            assert attempt.accepted.FAILURE_PATH == attempt.FAILURE_PATH
            raise RuntimeError("test")
    assert (
        attempt.accepted.ATTESTATION_PATH,
        attempt.accepted.EVIDENCE_PATH,
        attempt.accepted.FAILURE_PATH,
    ) == originals
    assert attempt._bindings_are_historical()


def test_envelope_schema_is_closed_and_rejects_retry_or_surplus() -> None:
    schema = json.loads(attempt.ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    example = attempt._example_envelope("f" * 40)
    assert not list(Draft202012Validator(schema).iter_errors(example))
    for field, value in (
        ("automatic_retry_count", 1),
        ("occupied_execution_count", 2),
        ("ambiguous_success_released", True),
    ):
        hostile = copy.deepcopy(example)
        hostile[field] = value
        assert list(Draft202012Validator(schema).iter_errors(hostile))
    hostile = {**example, "caller_output_path": "elsewhere"}
    assert list(Draft202012Validator(schema).iter_errors(hostile))


def test_pass_routes_exact_terminal_and_restores_bindings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    envelope, attestation, evidence, failure = _bind_terminal_paths(
        monkeypatch, tmp_path
    )
    monkeypatch.setattr(
        attempt,
        "static_check",
        lambda **_: {"source_head": "f" * 40, "status": "passed"},
    )

    def run() -> tuple[dict[str, object], dict[str, object]]:
        payload: dict[str, object] = {
            "result": attempt.accepted.PASS_RESULT,
            "cleanup": {"status": "cleanup_verified"},
            "ordinary_admission_release_count": 0,
            "product_record_count": 0,
        }
        attestation.write_text('{"attested":true}\n', encoding="utf-8")
        evidence.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        return payload, {"attested": True}

    monkeypatch.setattr(attempt.accepted, "run_rehearsal", run)
    result = attempt.run_attempt()
    assert result["result"] == attempt.PASS_RESULT
    assert result["base_result"] == attempt.accepted.PASS_RESULT
    assert result["cleanup_status"] == "cleanup_verified"
    assert result["occupied_execution_count"] == 1
    assert result["automatic_retry_count"] == 0
    assert result["terminal_artifact_kind"] == "rehearsal_evidence"
    assert result["terminal_artifact_sha256"] == _digest(evidence)
    assert result["transaction_attestation_sha256"] == _digest(attestation)
    assert envelope.exists()
    assert not failure.exists()
    assert attempt._bindings_are_historical()


def test_unexpected_controller_failure_routes_sanitized_terminal_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    envelope, attestation, evidence, failure = _bind_terminal_paths(
        monkeypatch, tmp_path
    )
    monkeypatch.setattr(
        attempt,
        "static_check",
        lambda **_: {"source_head": "e" * 40, "status": "passed"},
    )
    monkeypatch.setattr(
        attempt.accepted,
        "run_rehearsal",
        lambda: (_ for _ in ()).throw(RuntimeError("sensitive detail")),
    )
    result = attempt.run_attempt()
    terminal = json.loads(failure.read_text(encoding="utf-8"))
    assert result["result"] == "failed_closed"
    assert result["terminal_artifact_kind"] == "rehearsal_failure_evidence"
    assert result["terminal_artifact_sha256"] == _digest(failure)
    assert result["transaction_attestation_sha256"] is None
    assert result["automatic_retry_count"] == 0
    assert terminal["stage"] == "attempt_006_execution"
    assert terminal["code"] == "unexpected_controller_failure"
    assert "sensitive detail" not in json.dumps(terminal)
    assert envelope.exists()
    assert not attestation.exists()
    assert not evidence.exists()
    assert attempt._bindings_are_historical()


def test_cli_exposes_only_check_and_execute() -> None:
    source = Path(attempt.__file__).read_text(encoding="utf-8")
    assert 'mode.add_argument("--check"' in source
    assert 'mode.add_argument("--execute"' in source
    assert "--output" not in source
    assert "automatic_retry_count\": 0" in source
