from __future__ import annotations

import inspect
import subprocess

import pytest

from scripts import (
    raisa_authored_synthetic_native_harness_bounded_worker_attempt_004_readiness_and_preexecution_decision
    as subject,
)


def test_plan_and_threat_have_brisbane_timestamp_and_exact_boundary() -> None:
    plan = (subject.REPO_ROOT / "docs" / f"{subject.OPERATION_ID}-plan.md").read_text(
        encoding="utf-8"
    )
    threat = (
        subject.REPO_ROOT / "docs" / "security" / f"{subject.OPERATION_ID}-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for text in (plan, threat):
        assert "Date: 2026-08-21" in text
        assert "Timestamp: 2026-08-21T" in text
        assert "+10:00" in text
    assert "no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting" in plan
    assert "no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting" in threat


def test_attempt_identity_is_fourth_fresh_and_exact() -> None:
    value = subject.attempt_configuration()
    assert value["operation_id"].endswith("attempt-004")
    assert value["attempt_id"] == "deepseek-native-synthetic-window-worker-004"
    assert value["work_order_id"] == "wo-synthetic-native-window-worker-004"
    assert value["lease_id"] == "lease-synthetic-native-window-worker-004"
    assert len(value["paths"]) == 12
    assert all(path.parent == subject.ATTEMPT_EVIDENCE_ROOT for path in value["paths"])


def test_git_reader_only_launches_git(monkeypatch: pytest.MonkeyPatch) -> None:
    original = subprocess.run
    calls: list[list[str]] = []

    def guarded(argv: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert argv[0] == "git"
        calls.append(argv)
        return original(argv, *args, **kwargs)

    monkeypatch.setattr(subject.subprocess, "run", guarded)
    assert len(subject.git("rev-parse", "HEAD")) == 40
    assert calls


def test_stored_deterministic_gate_has_zero_occupied_processes() -> None:
    value = subject.validate_artifacts()
    assert value["result"] == "pass"
    assert set(value["process_boundary"].values()) == {0}
    assert value["occupied_attempt_authorized"] is False


def test_consumed_history_and_new_root_are_fail_closed() -> None:
    value = subject.validate_artifacts()
    assert len(value["consumed_history"]) == 7
    assert value["fresh_attempt"]["attempt_root_absent"] is True
    assert value["fresh_attempt"]["attempt_evidence_root_absent"] is True
    assert value["fresh_attempt"]["output_paths_absent"] is True
    assert value["readiness_clockwork_reusable_for_execution"] is False
    assert value["fresh_post_closeout_clockwork_reading_required"] is True


def test_one_execution_limits_are_exact_and_zero_retry() -> None:
    limits = subject.load_contract()["limits"]
    assert limits == {
        "native_processes": 1,
        "sessions": 1,
        "turns": 1,
        "provider_requests": 1,
        "model_tool_calls": 1,
        "maximum_output_tokens": 4096,
        "upstream_timeout_seconds": 300,
        "native_deadline_seconds": 420,
        "automatic_retries": 0,
        "resumes": 0,
        "fallbacks": 0,
        "second_workers": 0,
    }


def test_readiness_source_contains_no_native_process_launcher() -> None:
    source = inspect.getsource(subject)
    assert "subprocess.Popen" not in source
    assert "api.deepseek.com" not in source
    assert "DEEPSEEK_API_KEY" not in source


def test_stored_evidence_schema_and_report_are_bound() -> None:
    value = subject.validate_artifacts()
    assert value["decision"] == "ready_for_one_separately_checkpointed_occupied_attempt_004"
    assert value["clockwork_reading"]["lease_sequence"] == 103
    assert value["components"]["package_version"] == "0.1.0-rc.7"


def test_closeout_documents_bind_machine_resolved_full_commits_and_timestamps() -> None:
    paths = (
        subject.REPO_ROOT / "docs" / f"{subject.OPERATION_ID}-closeout.md",
        subject.REPO_ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-native-harness-attempt-004-readiness-sol-acceptance.md",
        subject.REPO_ROOT
        / "orchestration"
        / "human_inbox"
        / "yuri"
        / "2026-08-21--native-harness-attempt-004-readiness.md",
    )
    candidate = subject.git("rev-parse", "0ef8ab13")
    binding = subject.git("rev-parse", "a96448a1")
    assert len(candidate) == len(binding) == 40
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-21" in text
        assert "Timestamp: 2026-08-21T" in text
        assert "+10:00" in text
    assert candidate in paths[0].read_text(encoding="utf-8")
    assert binding in paths[0].read_text(encoding="utf-8")
    assert candidate in paths[1].read_text(encoding="utf-8")
    assert binding in paths[1].read_text(encoding="utf-8")
