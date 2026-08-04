from pathlib import Path

import yaml


SETTINGS = Path(__file__).resolve().parents[1] / "orchestration" / "harness_settings"
ROOT = SETTINGS.parents[1]


def load_policy() -> dict:
    return yaml.safe_load((SETTINGS / "autonomous_continuation.yaml").read_text(encoding="utf-8"))


def test_continuation_is_default_without_active_execution_limits() -> None:
    policy = load_policy()
    assert policy["schema_version"] == "ariadne.autonomous_continuation.v2"
    assert policy["default_posture"] == "continue_without_user_permission"
    assert policy["execution_limits"]["enforcement"] == "inactive"
    assert policy["execution_limits"]["wall_clock_deadlines"] == "inactive"
    assert policy["execution_limits"]["retry_counts"] == "advisory_evidence_only"


def test_failure_does_not_transfer_allocation_authority() -> None:
    policy = load_policy()
    assert "reallocate_workers" in policy["authority"]["orchestrator_may_not"]
    assert "revise_worker_assignment" in policy["authority"]["conductor_exclusive"]
    assert policy["failure_loop"][-1] == "orchestrator_resumes_execution"


def test_user_pause_surface_is_narrow() -> None:
    policy = load_policy()
    assert "dependency_satisfied_transition_to_next_planned_gate" in policy[
        "must_not_pause_for"
    ]
    assert "fresh_authority_request_for_already_planned_gate" in policy[
        "must_not_pause_for"
    ]
    assert (
        "unplanned_material_product_clinical_privacy_security_regulatory_"
        "architecture_authority_or_economic_fork"
        in policy["pause_for_user_only_when"]
    )
    assert "ordinary_worker_timeout" in policy["must_not_pause_for"]
    assert "verifier_requested_plan_revision" in policy["must_not_pause_for"]
    assert "same_lane_execution_retry" in policy["must_not_pause_for"]


def test_internal_checkpoint_cannot_end_the_task() -> None:
    policy = load_policy()
    lifecycle = policy["task_lifecycle"]
    assert lifecycle["terminal_handback_prohibited_when_no_user_decision_required"] is True
    assert lifecycle["continue_tools_in_same_task"] is True
    assert lifecycle["awaiting_worker_or_verifier_is_not_terminal"] is True
    assert lifecycle["committed_internal_plan_is_not_terminal"] is True
    assert lifecycle["next_step_known_is_not_terminal"] is True
    assert lifecycle["single_gate_closeout_is_not_terminal"] is True
    assert (
        lifecycle[
            "accepted_gate_with_dependency_satisfied_successor_is_not_terminal"
        ]
        is True
    )


def test_standing_programme_authority_is_exact_and_not_self_authorizing() -> None:
    policy = load_policy()
    standing = policy["standing_programme_authority"]
    assert policy["policy_decision"] == {
        "owner": "Yuri",
        "recorded_date": "2026-08-04",
        "status": "active",
    }
    assert (
        standing["gate_transition_permission"]
        == "continue_without_additional_user_message"
    )
    assert "accepted_descendant_plans" in standing["applies_to"]
    assert "no_explicit_closure_or_user_owned_choice_remains_unresolved" in standing[
        "gate_is_executable_only_when_all"
    ]
    assert "immediate_transition_to_next_qualifying_gate" in standing["authorizes"]
    assert "generic_future_candidate" in standing["does_not_self_authorize"]
    assert "protected_evidence_access" in standing["does_not_self_authorize"]


def test_live_handover_and_active_plan_record_the_standing_policy() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = (
        ROOT / "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
    ).read_text(encoding="utf-8")
    policy_doc = (ROOT / "docs/ariadne-autonomous-continuation.md").read_text(
        encoding="utf-8"
    )

    for text in (agents, plan, policy_doc):
        assert "standing" in text.lower()
        assert "dependency-satisfied" in text
        assert "generic future" in text.lower()

    assert "without another permission request" in agents
    assert "Run the fresh exact-HEAD Gemini 3.6 Flash/high veto" in plan
    assert "material Yuri decision" in " ".join(plan.split())
