from __future__ import annotations

import json
from pathlib import Path

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer_rehearsal as subject,
)


def _load(name: str):
    return json.loads((subject.OPERATION_ROOT / name).read_text(encoding="utf-8"))


def test_attempt_001_corrects_inferred_exit_code() -> None:
    attempt = _load("attempt-001-consumed.json")
    assert attempt["candidate_source"] == "475a5b6c210a1bc98f75234f544b5c619a94b704"
    assert attempt["safe_controller_terminal"] == "node_fixture_exit_nonzero"
    assert attempt["numeric_exit_code_retained"] is False
    assert attempt["fixture_self_check_exit_2_was_inferred_not_observed"] is True
    assert attempt["consumed"] is True


def test_attempt_002_preserves_unknown_numeric_exit() -> None:
    attempt = _load("attempt-002-consumed.json")
    assert attempt["candidate_source"] == "50a17beba7ea3a461cc2dd2154f747b307119f20"
    assert attempt["numeric_exit_code_retained"] is False
    assert attempt["stream_content_retained"] is False
    assert attempt["consumed"] is True


def test_attempt_003_binds_exact_content_free_abort_envelope() -> None:
    envelope = _load("attempt-003-process-envelope.json")
    attempt = _load("attempt-003-consumed.json")
    assert envelope["candidate_source"] == "03a53c5b6f5e487b991e465a73c6368aa9759d74"
    assert envelope["numeric_exit_code"] == 134
    assert envelope["stdout_bytes"] == 0
    assert envelope["stderr_bytes"] == 715
    assert envelope["stream_content_retained"] is False
    assert attempt["process_envelope_sha256"] == subject.sha256_bytes(
        subject.canonical_bytes(envelope)
    )
    assert attempt["consumed"] is True


def test_all_attempts_preserve_zero_harness_and_provider_activity() -> None:
    for number in (1, 2, 3):
        attempt = _load(f"attempt-{number:03d}-consumed.json")
        assert attempt["native_harness_process_count"] == 0
        assert attempt["provider_request_count"] == 0
        assert attempt["runner_integrated"] is False
        assert attempt["repair_selected"] is False


def test_success_outputs_are_absent() -> None:
    assert not subject.EVIDENCE_PATH.exists()
    assert not subject.REPORT_PATH.exists()
    assert not subject.SAFE_VECTOR_REJECTION_PATH.exists()
    assert not subject.WRAPPER_TERMINAL_PATH.exists()


def test_empty_environment_is_exact_shared_launch_difference() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    assert "env={}," in source
    assert source.count("env={},") == 1


def test_next_recovery_is_minimum_environment_only() -> None:
    plan = (
        subject.REPO_ROOT
        / "docs"
        / "deepseek-native-harness-provider-free-preset-mount-sanitizer-windows-minimum-environment-recovery-plan.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "SystemRoot" in plan
    assert "WINDIR" in plan
    assert "ComSpec" in plan
    assert "TEMP" in plan
    assert "TMP" in plan
    assert "Preserve the sanitizer and wrapper bytes exactly" in normalized
    assert "one local Node process in this successor" in normalized
