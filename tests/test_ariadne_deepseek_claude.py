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


def test_command_uses_bare_headless_mode_and_no_session_persistence():
    command = build_command(packet="bounded", model="deepseek-v4-flash", effort="high")

    assert command[:3] == ["claude", "-p", "bounded"]
    assert "--bare" in command
    assert "--no-session-persistence" in command
    assert command[command.index("--permission-mode") + 1] == "dontAsk"
    assert command[command.index("--output-format") + 1] == "json"


def test_environment_uses_only_process_local_deepseek_configuration(monkeypatch):
    monkeypatch.setenv("UNRELATED", "preserved")
    env = deepseek_environment(api_key="test-key", model="deepseek-v4-pro", effort="max")

    assert env["ANTHROPIC_BASE_URL"] == BASE_URL
    assert env["ANTHROPIC_API_KEY"] == "test-key"
    assert env["ANTHROPIC_AUTH_TOKEN"] == "test-key"
    assert env["ANTHROPIC_MODEL"] == "deepseek-v4-pro"
    assert env["UNRELATED"] == "preserved"


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
    monkeypatch.setattr(
        "scripts.ariadne_deepseek_claude.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout=json.dumps(raw), stderr="sensitive terminal detail"
        ),
    )

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
        "antigravity-gemini-flash-3-5-worker",
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
