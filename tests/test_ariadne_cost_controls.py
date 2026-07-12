from pathlib import Path
import subprocess
import sys

import yaml


SETTINGS = Path(__file__).resolve().parents[1] / "orchestration" / "harness_settings"


def policy() -> dict:
    return yaml.safe_load((SETTINGS / "cost_controls.yaml").read_text(encoding="utf-8"))


def test_current_subscription_profile_has_no_monetary_enforcement() -> None:
    controls = policy()
    current = controls["current_profile"]
    assert controls["feature_available"] is True
    assert current["monetary_budget_enforcement"] == "inactive"
    assert current["pass_cli_max_budget_usd"] is False
    assert controls["activation"]["requires_explicit_user_override"] is True


def test_estimated_cost_cannot_trigger_conductor_fallback() -> None:
    semantics = policy()["fallback_semantics"]
    assert semantics["estimated_cost_or_local_cap_exceeded_triggers_fallback"] is False
    assert semantics["actual_provider_usage_limit_triggers_fallback"] is True


def test_deepseek_pro_is_routine_conductor_and_claude_is_escalation() -> None:
    assert policy()["routine_conductor_order"] == [
        "deepseek-pro-conductor-fallback",
        "claude-fable-conductor",
        "claude-opus-conductor",
        "gpt-sol-conductor-fallback",
    ]
    assert policy()["claude_escalation_order"] == [
        "claude-fable-conductor",
        "claude-opus-conductor",
    ]


def test_headless_driver_rejects_inactive_cli_budget_cap() -> None:
    root = SETTINGS.parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "scripts/drive_agent_headless.py",
            "--cwd",
            str(root),
            "--prompt",
            "dry run",
            "--max-budget-usd",
            "1",
            "--dry-run",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "inactive for this project profile" in result.stderr
