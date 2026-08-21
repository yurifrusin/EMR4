from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from orchestration_harness import native_pre_hmr_diagnostic as diagnostic


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "monitored-development-rehearsal"
    / "attempt-004"
)
ATTEMPT_ROOT = Path(
    "C:/Users/sarashera/EMR4-worktrees/deepseek-native-synthetic-window-worker-004"
)


def load(name: str) -> dict[str, object]:
    value = json.loads((EVIDENCE / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_attempt_four_outer_terminal_is_closed_and_fail_closed() -> None:
    terminal = load("occupied-terminal.json")
    schema = load("occupied-terminal.schema.json")
    Draft202012Validator(schema).validate(terminal)
    assert terminal["result"] == "failed_closed"
    assert terminal["failure_coordinate"] == "native_harness_terminal_failure"
    assert terminal["process"]["native_process_count"] == 1
    assert terminal["process"]["harness_exit_code"] == 1
    assert terminal["process"]["wall_clock_ms"] == 11150
    assert terminal["hmr_events"] == []


def test_attempt_four_structured_terminal_is_digest_bound_and_sanitized() -> None:
    outer = load("occupied-terminal.json")
    path = EVIDENCE / "pre-hmr-startup-terminal.json"
    value = load("pre-hmr-startup-terminal.json")
    diagnostic.validate_structured_pre_hmr_terminal(value)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == outer[
        "pre_hmr_startup_terminal_sha256"
    ]
    assert value["cause"] == "structured_entrypoint_import_rejected"
    assert value["stage"] == "native_process_started_before_first_hmr_event"
    assert value["controller_coordinate"] == "native_process_exited_nonzero"
    assert value["raw_streams_retained"] is False
    structured = value["structured_diagnostic"]
    assert structured["phase"] == "entrypoint_import_rejected"
    assert len(structured["cause_chain"]) == 4
    assert structured["cause_chain"][0]["message_coordinate"] == (
        "plugin_tree_failed_to_load"
    )
    assert structured["cause_chain"][-1]["code_coordinate"] == "unrecognized"
    assert structured["raw_error_message_retained"] is False
    assert structured["raw_stack_retained"] is False
    assert structured["raw_paths_retained"] is False


def test_attempt_four_never_reached_provider_model_tool_or_candidate_change() -> None:
    terminal = load("occupied-terminal.json")
    assert terminal["broker"] == {
        "provider_call_started": 0,
        "provider_call_completed": 0,
        "provider_call_failed": 0,
        "request_rejected": 0,
    }
    assert terminal["runner"] == {}
    assert terminal["candidate"]["changed_paths"] == []
    assert terminal["candidate"]["exact_expected_bytes"] is False
    assert terminal["candidate"]["final_sha256"] == (
        "9606d9341e6b7e53f4ee9007d7518145322968b2d0bc156622928c33ab97d4f8"
    )
    assert terminal["automatic_retry_count"] == 0
    assert terminal["fallback_count"] == 0
    assert terminal["auxiliary_model_call_count"] == 0


def test_attempt_four_is_consumed_and_cleanup_is_complete() -> None:
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
    assert not ATTEMPT_ROOT.exists()
