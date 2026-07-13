from pathlib import Path

import yaml


SETTINGS = Path(__file__).resolve().parents[1] / "orchestration" / "harness_settings"


def load(name: str) -> dict:
    return yaml.safe_load((SETTINGS / name).read_text(encoding="utf-8"))


def test_orchestrator_selects_planning_mode_and_protects_master() -> None:
    model = load("operating_model.yaml")
    boundary = model["sprint_boundary"]
    assert boundary["orchestrator"]["default_planning_mode"] == "sol_direct_routine"
    assert "authorize_protected_master_integration" in boundary["orchestrator"]["exclusive_authority"]
    direct = boundary["sol_direct_routine"]
    assert direct["resource_id"] == "openai-primary-orchestrator"
    assert direct["deepseek_pro_consultation"] == "optional_compact_challenge_only"
    executor = boundary["routine_delegated_executor"]
    assert "self_authorize_protected_master_integration" in executor["may_not"]
    assert executor["protected_master_execution"]["allowed_when"] == "orchestrator_issued_exact_integration_manifest"
    assert boundary["conductor"]["mode"] == "optional_orchestrator_selected"
    assert model["within_sprint"]["executive_role"] == "selected_executor"
    assert "waiting_for_worker" in model["within_sprint"]["conductor_reentry_not_required_for"]
    assert "rerunning_same_lane" in model["within_sprint"]["conductor_reentry_not_required_for"]


def test_verifier_is_risk_triggered_not_mandatory() -> None:
    model = load("operating_model.yaml")
    roles = {entry["role"]: entry for entry in load("role_preferences.yaml")["roles"]}
    assert model["verifier"]["mode"] == "risk_triggered_optional"
    assert model["verifier"]["deterministic_plan_checks_always_run"] is True
    assert roles["verifier"]["required"] is False


def test_time_limits_are_inactive_and_progress_is_preferred() -> None:
    controls = load("operating_model.yaml")["execution_controls"]
    assert controls["wall_clock_deadlines"] == "inactive"
    assert controls["prefer_progress_observation_over_elapsed_time"] is True
    assert controls["worker_may_continue_while_progress_is_observable"] is True


def test_sprint_engine_cycles_without_conversational_handback() -> None:
    engine = load("operating_model.yaml")["continuous_sprint_engine"]
    assert engine["enabled"] is True
    assert engine["conversational_handback_between_sprints"] is False
    assert engine["cycle"][0] == "orchestrator_closes_current_sprint"
    assert "orchestrator_selects_planning_mode" in engine["cycle"]
    assert "selected_planner_defines_and_allocates_next_sprint" in engine["cycle"]
    assert "orchestrator_authorizes_exact_integration_manifest" in engine["cycle"]
    assert "selected_executor_integrates_protected_master_or_stops_on_variance" in engine["cycle"]


def test_orchestrator_commits_and_pushes_regular_checkpoints() -> None:
    checkpoints = load("operating_model.yaml")["integration_checkpoints"]
    assert checkpoints["authorization_owner"] == "orchestrator"
    assert checkpoints["execution_owner"] == "selected_executor_after_exact_authorization"
    assert checkpoints["commit_and_push_regularly"] is True
    assert checkpoints["advance_handoff_current_after_accepted_checkpoint"] is True
    assert checkpoints["workers_may_push_master"] is False
    assert checkpoints["executor_may_push_master_without_authorization"] is False
