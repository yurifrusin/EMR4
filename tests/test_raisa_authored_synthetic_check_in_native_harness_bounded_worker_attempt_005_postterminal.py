from __future__ import annotations

import json
from pathlib import Path
import subprocess

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "monitored-development-rehearsal"
    / "attempt-005"
)
ATTEMPT_ROOT = Path(
    "C:/Users/sarashera/EMR4-worktrees/deepseek-native-synthetic-window-worker-005"
)
TERMINAL_SOURCE = "0b2aebd104f4c9dcfd4603af5dd51a687bace555"
CLOSEOUT = (
    ROOT
    / "docs"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "attempt-005-closeout.md"
)
SOL = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-native-harness-attempt-005-sol-acceptance.md"
)
YURI = (
    ROOT
    / "orchestration"
    / "human_inbox"
    / "yuri"
    / "2026-08-21--native-harness-attempt-005-terminal.md"
)


def load(name: str) -> dict[str, object]:
    value = json.loads((EVIDENCE / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_attempt_five_outer_terminal_is_closed_and_fail_closed() -> None:
    terminal = load("occupied-terminal.json")
    schema = load("occupied-terminal.schema.json")
    Draft202012Validator(schema).validate(terminal)
    assert terminal["result"] == "failed_closed"
    assert terminal["failure_coordinate"] == "native_harness_terminal_failure"
    assert terminal["process"]["native_process_count"] == 1
    assert terminal["process"]["harness_exit_code"] == 1
    assert terminal["process"]["wall_clock_ms"] == 10929
    assert terminal["hmr_events"] == [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]
    assert terminal["pre_hmr_startup_terminal_sha256"] is None


def test_attempt_five_reached_the_custom_runner_but_not_a_model_request() -> None:
    terminal = load("occupied-terminal.json")
    assert terminal["runner"] == {
        "schema_version": "ariadne.synthetic_native_worker_runner_terminal.v1",
        "status": "failed",
        "failure_code": "CUSTOM_RUNNER_FAILURE",
        "request_count": 0,
        "tool_names": [],
        "tool_result_count": 0,
        "turn_kind": None,
        "conclusion_marked": False,
        "allowed_tool_names": ["edit", "glob", "read"],
    }
    assert terminal["broker"] == {
        "provider_call_started": 0,
        "provider_call_completed": 0,
        "provider_call_failed": 0,
        "request_rejected": 0,
    }


def test_attempt_five_changed_nothing_and_used_no_retry_or_fallback() -> None:
    terminal = load("occupied-terminal.json")
    assert terminal["candidate"]["changed_paths"] == []
    assert terminal["candidate"]["exact_expected_bytes"] is False
    assert terminal["candidate"]["final_sha256"] == (
        "9606d9341e6b7e53f4ee9007d7518145322968b2d0bc156622928c33ab97d4f8"
    )
    assert terminal["candidate"]["cases"] == {
        "executed": False,
        "public_passed": 0,
        "holdback_passed": 0,
    }
    assert terminal["automatic_retry_count"] == 0
    assert terminal["fallback_count"] == 0
    assert terminal["auxiliary_model_call_count"] == 0


def test_attempt_five_is_consumed_and_cleanup_is_complete() -> None:
    terminal = load("occupied-terminal.json")
    consumed = load("occupied-attempt-consumed.json")
    assert consumed["state"] == "consumed"
    assert consumed["resume_permitted"] is False
    assert consumed["automatic_retry_count"] == 0
    assert all(
        terminal["cleanup"][key]
        for key in ("harness_absent", "broker_absent", "attempt_root_absent")
    )
    assert terminal["cleanup"]["raw_logs_retained"] is False
    assert terminal["cleanup"]["raw_session_retained"] is False
    assert terminal["cleanup"]["provider_key_present_in_worker_environment"] is False
    assert not ATTEMPT_ROOT.exists()


def test_attempt_five_efficacy_reading_states_the_honest_conclusion() -> None:
    value = load("efficacy-reading.json")
    assert value["terminal_source"] == TERMINAL_SOURCE
    assert value["measurements"]["hmr_events"] == [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]
    assert value["measurements"]["runner_failure_code"] == "CUSTOM_RUNNER_FAILURE"
    assert value["efficacy"]["pre_hmr_startup_recovery_vs_attempt_004"] == (
        "improved"
    )
    assert value["efficacy"]["post_hmr_runner_cause_localization"] == (
        "insufficient"
    )
    assert value["efficacy"]["deepseek_reasoning_or_coding_evidence"] == (
        "not_reached"
    )
    assert value["efficacy"]["native_worker_success"] == "failed"


def test_attempt_five_closeout_documents_bind_timestamp_and_terminal_source() -> None:
    resolved = subprocess.check_output(
        ["git", "rev-parse", "--verify", f"{TERMINAL_SOURCE}^{{commit}}"],
        cwd=ROOT,
        text=True,
    ).strip()
    assert resolved == TERMINAL_SOURCE
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", TERMINAL_SOURCE, "HEAD"],
        cwd=ROOT,
        check=True,
    )
    for path in (CLOSEOUT, SOL, YURI, EVIDENCE / "diagnosis.md"):
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-21" in text
        assert "Timestamp: 2026-08-21T" in text
        assert "+10:00 (Australia/Brisbane)" in text
    for path in (CLOSEOUT, SOL, YURI):
        assert TERMINAL_SOURCE in path.read_text(encoding="utf-8")
