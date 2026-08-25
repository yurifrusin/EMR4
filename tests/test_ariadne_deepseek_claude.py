from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.ariadne_deepseek_claude import (
    BASE_URL,
    build_command,
    deepseek_environment,
    run_worker,
)


@pytest.fixture(autouse=True)
def _admit_direct_worker_unit_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "scripts.ariadne_deepseek_claude.require_programme_admission",
        lambda **_kwargs: None,
    )


def test_command_uses_bare_headless_mode_and_no_session_persistence():
    command = build_command(packet="bounded", model="deepseek-v4-flash", effort="high")

    assert command[:3] == ["claude", "-p", "bounded"]
    assert "--bare" in command
    assert "--no-session-persistence" in command
    assert command[command.index("--permission-mode") + 1] == "dontAsk"
    assert command[command.index("--output-format") + 1] == "json"


def test_environment_uses_only_process_local_deepseek_configuration(monkeypatch):
    monkeypatch.setenv("UNRELATED", "preserved")
    monkeypatch.setenv("VIRTUAL_ENV", "C:/primary/.venv")
    monkeypatch.setenv("PYTHONPATH", "C:/primary")
    monkeypatch.setenv("PIP_INDEX_URL", "https://packages.example.invalid")
    monkeypatch.setenv("UV_DEFAULT_INDEX", "https://uv.example.invalid")
    env = deepseek_environment(api_key="test-key", model="deepseek-v4-pro", effort="max")

    assert env["ANTHROPIC_BASE_URL"] == BASE_URL
    assert env["ANTHROPIC_API_KEY"] == "test-key"
    assert env["ANTHROPIC_AUTH_TOKEN"] == "test-key"
    assert env["ANTHROPIC_MODEL"] == "deepseek-v4-pro"
    assert env["UNRELATED"] == "preserved"
    assert "VIRTUAL_ENV" not in env
    assert "PYTHONPATH" not in env
    assert "PIP_INDEX_URL" not in env
    assert "UV_DEFAULT_INDEX" not in env
    assert env["PIP_NO_INDEX"] == "1"
    assert env["PIP_NO_INPUT"] == "1"
    assert env["PYTHONNOUSERSITE"] == "1"
    assert env["UV_OFFLINE"] == "1"
    assert env["NPM_CONFIG_OFFLINE"] == "true"
    assert env["YARN_ENABLE_NETWORK"] == "0"


def test_environment_pins_shell_directory_signals_to_worker(tmp_path: Path):
    worktree = tmp_path / "worker"
    worktree.mkdir()

    env = deepseek_environment(
        api_key="test-key",
        model="deepseek-v4-flash",
        effort="high",
        cwd=worktree,
    )

    assert env["PWD"] == str(worktree.resolve())
    assert env["INIT_CWD"] == str(worktree.resolve())


@pytest.mark.parametrize("model", ["deepseek-chat", "claude-opus"])
def test_command_rejects_unregistered_models(model: str):
    with pytest.raises(ValueError, match="unsupported DeepSeek model"):
        build_command(packet="bounded", model=model, effort="high")


def test_run_worker_writes_compact_receipt_without_session_id_or_raw_stderr(
    tmp_path: Path, monkeypatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Implement the bounded change.", encoding="utf-8")
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    output = tmp_path / "receipt.json"
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    raw = {
        "subtype": "success",
        "result": "done",
        "session_id": "must-not-persist",
        "usage": {"input_tokens": 12, "output_tokens": 3},
        "total_cost_usd": 0.001,
        "permission_denials": [],
        "terminal_reason": "completed",
    }
    captured: dict[str, object] = {}

    def fake_run(*args, **kwargs):
        captured["command"] = args[0]
        captured["cwd"] = kwargs["cwd"]
        captured["env"] = kwargs["env"]
        return SimpleNamespace(
            returncode=0, stdout=json.dumps(raw), stderr="sensitive terminal detail"
        )

    monkeypatch.setattr("scripts.ariadne_deepseek_claude.subprocess.run", fake_run)

    receipt = run_worker(
        packet_path=packet,
        cwd=worktree,
        output_path=output,
        model="deepseek-v4-flash",
        effort="high",
    )

    assert receipt["status"] == "completed"
    assert receipt["result"] == "done"
    assert receipt["adapter_cost_estimate_usd"] == 0.001
    assert receipt["adapter_cost_estimate_authoritative"] is False
    assert receipt["authoritative_billing_source"] == "deepseek_provider_usage"
    assert receipt["provider_billed_cost_usd"] is None
    assert captured["cwd"] == worktree.resolve()
    env = captured["env"]
    assert isinstance(env, dict)
    assert env["PWD"] == str(worktree.resolve())
    assert env["INIT_CWD"] == str(worktree.resolve())
    command = captured["command"]
    assert isinstance(command, list)
    packet_argument = command[command.index("-p") + 1]
    assert packet_argument.startswith(
        f"AUTHORIZED_WORKTREE_ROOT: {worktree.resolve()}\n"
    )
    assert "PACKAGE_AND_ENVIRONMENT_MUTATION: FORBIDDEN" in packet_argument
    system_prompt = command[command.index("--system-prompt") + 1]
    assert "Do not run a package manager" in system_prompt
    rendered = output.read_text(encoding="utf-8")
    assert '"total_cost_usd"' not in rendered
    assert "session_id" not in rendered
    assert "sensitive terminal detail" not in rendered


def test_evidence_policy_commits_only_tranche_level_routine_artifacts():
    policy_path = (
        Path(__file__).resolve().parents[1]
        / "orchestration"
        / "harness_settings"
        / "evidence_policy.yaml"
    )
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))

    assert policy["default_mode"] == "compact_tranche_ledger"
    assert policy["routine_committed_artifacts"] == [
        "tranche_contract",
        "tranche_integration_manifest",
        "tranche_closeout",
    ]
    assert "worker_receipt" in policy["local_ignored_artifacts"]
    assert policy["acceptance_review_frequency"] == "exception_only"


def test_economical_pool_keeps_gemini_as_a_peer_worker():
    settings_path = (
        Path(__file__).resolve().parents[1]
        / "orchestration"
        / "harness_settings"
        / "operating_model.yaml"
    )
    model = yaml.safe_load(settings_path.read_text(encoding="utf-8"))
    economical = model["economical_execution"]

    assert economical["preferred_workers"] == [
        "deepseek-flash-workers",
        "antigravity-gemini-flash-3-7-high-verifier",
    ]
    assert economical["worker_allocation_rule"].startswith(
        "allocate_only_distinct_bounded_surfaces"
    )
    assert economical["preferred_routine_planner"] == "openai-primary-orchestrator"
    assert economical["deepseek_pro_planning_role"] == (
        "compact_high_leverage_consultant_not_default_coordinator"
    )
    assert economical["preferred_coding_worker"] == "deepseek-flash-workers"


def test_deepseek_pro_cost_calibration_is_provisional_and_model_specific():
    calibration_path = (
        Path(__file__).resolve().parents[1]
        / "orchestration"
        / "harness_settings"
        / "deepseek_cost_calibration.yaml"
    )
    payload = yaml.safe_load(calibration_path.read_text(encoding="utf-8"))
    calibration = next(
        item
        for item in payload["calibrations"]
        if item["calibration_id"] == "deepseek-v4-pro-claude-bare-s16-s18"
    )

    assert calibration["adapter_estimate_usd"] == pytest.approx(2.905994)
    assert calibration["actual_from_adapter_multiplier"]["midpoint"] == pytest.approx(
        0.024088143
    )
    assert calibration["provider_billed_usd"]["low"] == pytest.approx(0.06)
    assert calibration["provider_billed_usd"]["high"] == pytest.approx(0.08)
    assert "do_not_apply_to_deepseek_v4_flash" in calibration["restrictions"]
