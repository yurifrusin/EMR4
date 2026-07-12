from pathlib import Path

import yaml

SETTINGS = Path("orchestration/harness_settings")


def _yaml(name: str) -> dict:
    return yaml.safe_load((SETTINGS / name).read_text(encoding="utf-8"))


def test_direction_dialogue_is_optional_bounded_and_ends_on_agreement():
    policy = _yaml("direction_collaboration.yaml")

    assert policy["mode"] == "optional_bounded_dialogue"
    assert policy["dialogue"]["orchestrator_initial_proposal"] == "optional"
    assert policy["dialogue"]["maximum_orchestrator_rejoinders"] == 1
    assert policy["early_exit"]["agreement_ends_direction_dialogue"] is True
    assert policy["early_exit"]["conductor_may_plan_directly_when_direction_is_obvious"] is True


def test_orchestrator_can_suggest_direction_but_cannot_allocate():
    orchestrator = _yaml("direction_collaboration.yaml")["participants"]["orchestrator"]

    assert "propose_sprint_direction" in orchestrator["may"]
    assert "issue_one_rejoinder" in orchestrator["may"]
    assert "allocate_or_reallocate_workers" in orchestrator["may_not"]
    assert "publish_final_sprint_definition" in orchestrator["may_not"]


def test_conductor_retains_final_sprint_and_worker_allocation_authority():
    policy = _yaml("direction_collaboration.yaml")
    authority = policy["participants"]["conductor"]["exclusive_authority"]

    assert policy["dialogue"]["conductor_final_say"] is True
    assert "publish_final_sprint_definition" in authority
    assert "divide_sprint_work" in authority
    assert "allocate_workers" in authority
    assert policy["verification"]["final_plan_must_be_authored_by_conductor"] is True


def test_sprint_policy_requires_dialogue_disposition_and_deterministic_authority_checks():
    policy = _yaml("sprint_worker_policy.yaml")

    assert "direction_dialogue_disposition" in policy["required_plan_fields"]
    assert "final_sprint_and_allocation_authored_by_conductor" in policy["deterministic_plan_checks"]
    assert "direction_dialogue_did_not_transfer_allocation_authority" in policy["deterministic_plan_checks"]
