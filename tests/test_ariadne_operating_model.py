from pathlib import Path

import yaml


SETTINGS = Path(__file__).resolve().parents[1] / "orchestration" / "harness_settings"


def load(name: str) -> dict:
    return yaml.safe_load((SETTINGS / name).read_text(encoding="utf-8"))


def test_conductor_governs_sprint_boundary_and_orchestrator_executes() -> None:
    model = load("operating_model.yaml")
    assert "define_next_sprint" in model["sprint_boundary"]["conductor"]["exclusive_authority"]
    assert model["within_sprint"]["executive_role"] == "orchestrator"
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
