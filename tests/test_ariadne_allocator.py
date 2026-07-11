"""S4b replay coverage for the pure Ariadne allocation engine."""

from pathlib import Path

import yaml

from orchestration_harness.allocation import (
    AvailabilityProbe,
    GeneralistProfile,
    RolePreference,
    WorkerResource,
)
from orchestration_harness.allocator import allocate_roles


SETTINGS = Path("orchestration/harness_settings")
FIXTURE = Path("tests/fixtures/ariadne_harness/allocation_replay.yaml")


def _yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _settings():
    workers = [WorkerResource.from_dict(item) for item in _yaml(SETTINGS / "worker_pool.yaml")["workers"]]
    preferences = [RolePreference.from_dict(item) for item in _yaml(SETTINGS / "role_preferences.yaml")["roles"]]
    generalist_payload = _yaml(SETTINGS / "generalist.yaml")
    generalist = GeneralistProfile.from_dict({key: value for key, value in generalist_payload.items() if key != "schema_version"})
    return workers, preferences, generalist


def test_s4b_allocation_replay_is_deterministic_and_has_no_live_adapter():
    workers, preferences, generalist = _settings()
    scenarios = _yaml(FIXTURE)["scenarios"]

    for scenario in scenarios:
        probes = [AvailabilityProbe.from_dict(probe) for probe in scenario["probes"]]
        first = allocate_roles(resources=workers, preferences=preferences, probes=probes, generalist=generalist)
        second = allocate_roles(resources=workers, preferences=preferences, probes=probes, generalist=generalist)

        assert first == second
        assert {assignment.role.value: assignment.resource_id for assignment in first.assignments} == scenario["expected_assignments"]
        assert [role.value for role in first.unfilled_required_roles] == scenario["expected_unfilled_required_roles"]
        assert all(not assignment.orchestrator_substituted for assignment in first.assignments)


def test_s4b_labels_reduced_independence_when_generalist_is_required():
    workers, preferences, generalist = _settings()
    scenario = _yaml(FIXTURE)["scenarios"][1]
    outcome = allocate_roles(
        resources=workers,
        preferences=preferences,
        probes=[AvailabilityProbe.from_dict(probe) for probe in scenario["probes"]],
        generalist=generalist,
    )

    assignments = {assignment.role.value: assignment for assignment in outcome.assignments}
    for role in scenario["expected_reduced_independence_roles"]:
        assert assignments[role].independence_label == "self_review"
        assert assignments[role].fallback_reason == "generalist_fallback_required"
