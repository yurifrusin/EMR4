from pathlib import Path

import yaml


SETTINGS = Path(__file__).resolve().parents[1] / "orchestration" / "harness_settings"


def load_policy() -> dict:
    return yaml.safe_load((SETTINGS / "autonomous_continuation.yaml").read_text(encoding="utf-8"))


def test_continuation_is_default_but_bounded() -> None:
    policy = load_policy()
    assert policy["default_posture"] == "continue_without_user_permission"
    assert policy["retry_budget"]["maximum_replans_per_failure_class"] > 0
    assert policy["retry_budget"]["repeated_failure_requires_distinct_remediation"] is True


def test_failure_does_not_transfer_allocation_authority() -> None:
    policy = load_policy()
    assert "reallocate_workers" in policy["authority"]["orchestrator_may_not"]
    assert "revise_worker_assignment" in policy["authority"]["conductor_exclusive"]
    assert policy["failure_loop"][-1] == "orchestrator_resumes_verified_execution"


def test_user_pause_surface_is_narrow() -> None:
    policy = load_policy()
    assert "retry_budget_exhausted" in policy["pause_for_user_only_when"]
    assert "ordinary_worker_timeout" in policy["must_not_pause_for"]
    assert "verifier_requested_plan_revision" in policy["must_not_pause_for"]


def test_internal_checkpoint_cannot_end_the_task() -> None:
    policy = load_policy()
    lifecycle = policy["task_lifecycle"]
    assert lifecycle["terminal_handback_prohibited_when_no_user_decision_required"] is True
    assert lifecycle["continue_tools_in_same_task"] is True
    assert lifecycle["awaiting_worker_or_verifier_is_not_terminal"] is True
    assert lifecycle["committed_internal_plan_is_not_terminal"] is True
    assert lifecycle["next_step_known_is_not_terminal"] is True
