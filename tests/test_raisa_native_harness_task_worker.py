from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from scripts.raisa_native_harness_task_worker import (
    CONFIG_SCHEMA,
    TaskWorkerError,
    full_source,
    profile_patch,
    runner_source,
    validate_config,
    validate_runner_and_profile,
)


def _config() -> dict:
    return {
        "schema_version": CONFIG_SCHEMA,
        "operation_id": "raisa-provider-free-unmounted-default-off-canonical-check-in-environment-evidence-admission-input-seam-rehearsal",
        "attempt_id": "deepseek-native-check-in-evidence-seam-001",
        "attempt_root": "C:/Users/sarashera/EMR4-worktrees/deepseek-native-check-in-evidence-seam-001",
        "evidence_root": "orchestration/continuity/raisa-provider-free-unmounted-default-off-canonical-check-in-environment-evidence-admission-input-seam-rehearsal",
        "owned_paths": [
            "orchestration_harness/check_in_environment_evidence_admission.py",
            "tests/test_check_in_environment_evidence_admission.py",
        ],
        "read_only_packet_paths": [
            "AGENTS.md",
            "docs/raisa-provider-free-unmounted-default-off-canonical-check-in-environment-evidence-admission-input-seam-rehearsal-plan.md",
            "orchestration/continuity/raisa-provider-free-unmounted-default-off-canonical-check-in-environment-evidence-admission-input-seam-rehearsal/contract.json",
        ],
        "focused_test_paths": ["tests/test_check_in_environment_evidence_admission.py"],
        "task": "Work at exact source {source_commit}. " + "x" * 300,
        "maximum_wall_clock_seconds": 900,
    }


def test_valid_config_is_exactly_bounded() -> None:
    config = validate_config(_config())
    assert config["owned_paths"] == _config()["owned_paths"]
    assert config["maximum_wall_clock_seconds"] == 900


def test_abbreviated_source_is_rejected_before_git_resolution() -> None:
    with pytest.raises(TaskWorkerError, match="source_not_full_git_object"):
        full_source("9dbe72d")


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("maximum_wall_clock_seconds", 901),
        ("owned_paths", ["outside.py"]),
        ("read_only_packet_paths", [".env", "AGENTS.md", "docs/a.md"]),
        ("focused_test_paths", ["tests/outside.py"]),
    ],
)
def test_config_widening_fails_closed(field: str, replacement: object) -> None:
    config = deepcopy(_config())
    config[field] = replacement
    with pytest.raises(TaskWorkerError):
        validate_config(config)


def test_runner_has_exact_tools_owned_edit_gate_and_no_forced_one_edit_turn() -> None:
    source = runner_source().decode("utf-8")
    assert 'Object.freeze(["edit", "glob", "read"])' in source
    assert "owned.has(normalized(args.file_path))" in source
    assert "concludeTurn" not in source
    assert "summary.request_count >= 1" in source
    assert "child_process" not in source


def test_profile_uses_stock_headless_hmr_handoff_and_zero_retry(tmp_path: Path) -> None:
    (tmp_path / "task-config.json").write_text(
        __import__("json").dumps(_config()), encoding="utf-8"
    )
    initial = profile_patch(tmp_path, 43123, runner=False).decode("utf-8")
    changed = profile_patch(tmp_path, 43123, runner=True).decode("utf-8")
    assert "- id: headless-runner\n  disabled: true" in initial
    assert "- id: emr4-task-worker-runner" not in initial
    assert changed.count("- id: emr4-task-worker-runner") == 1
    assert "maxParallelToolCalls: 1" in changed
    assert "maxRetries: 0" in changed
    assert "policy: never" in changed


def test_zero_provider_effective_tool_preflight_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "task-config.json").write_text(
        __import__("json").dumps(_config()), encoding="utf-8"
    )
    reading = validate_runner_and_profile(tmp_path)
    assert reading and all(reading.values())
