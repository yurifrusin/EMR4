from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "orchestration/harness_settings/orchestrator_requirements.yaml"
WORKER_POLICY = ROOT / "orchestration/harness_settings/sprint_worker_policy.yaml"
CONTINUATION = ROOT / "orchestration/harness_settings/autonomous_continuation.yaml"
HANDOVER = ROOT / "AGENTS.md"
CONTROL = ROOT / "docs/ariadne-mandatory-parallelism-efficacy-control.md"


def _yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_all_continuation_events_require_the_three_lane_assessment() -> None:
    settings = _yaml(REQUIREMENTS)
    policy = settings["parallelism_assessment"]
    assert policy["required_events"] == settings["continuation_events"]
    assert policy["required_lane_ids"] == [
        "deepseek_flash",
        "gemini_verifier",
        "native_subagents",
    ]
    assert policy["require_serial_constraints_or_positive_parallel_work"] is True


def test_plans_and_closeouts_must_record_expected_and_actual_worker_mix() -> None:
    policy = _yaml(WORKER_POLICY)
    fields = set(policy["required_plan_fields"])
    checks = set(policy["deterministic_plan_checks"])
    assert {
        "parallelism_efficacy_assessment",
        "deepseek_disposition",
        "gemini_disposition",
        "native_subagent_disposition",
        "concurrency_and_serial_dependency_map",
        "reassessment_triggers",
        "expected_and_actual_worker_mix",
    } <= fields
    assert "closeout_reports_expected_versus_actual_worker_mix" in checks


def test_new_task_windows_carry_the_assessment_without_expanding_authority() -> None:
    continuation = _yaml(CONTINUATION)["task_lifecycle"]["parallelism_assessment"]
    assert continuation["carry_forward_across_new_session_compaction_and_restoration"]
    assert continuation["solo_serial_is_never_implicit"]
    handover = HANDOVER.read_text(encoding="utf-8")
    control = CONTROL.read_text(encoding="utf-8")
    assert "Parallelism consideration is mandatory even when dispatch is not" in handover
    assert "does not allocate acceptance, integration, baton or protected-" in control
