"""Strict YAML schema checks for Ariadne S4a worker allocation artifacts."""

from pathlib import Path

import pytest
import yaml

from orchestration_harness.allocation import (
    AssignmentRecord,
    AvailabilityProbe,
    ConductorPlan,
    GeneralistProfile,
    Role,
    RolePreference,
    UserOverride,
    VerifierDecision,
    VerifierResult,
    WorkerResource,
)

SETTINGS = Path("orchestration/harness_settings")


def _yaml(name: str) -> dict:
    return yaml.safe_load((SETTINGS / name).read_text(encoding="utf-8"))


def test_worker_pool_is_strict_and_declares_transport_separately_from_capability():
    pool = _yaml("worker_pool.yaml")
    workers = [WorkerResource.from_dict(item) for item in pool["workers"]]

    assert pool["schema_version"] == "ariadne.worker_pool.v1"
    assert {worker.resource_id for worker in workers} == {
        "gpt-terra-primary", "claude-fable-conductor", "claude-opus-conductor",
        "antigravity-gemini-flash-3-5-worker", "deepseek-flash-verifier", "deepseek-flash-workers",
    }
    assert any(worker.transport.value == "bridge_subagent" for worker in workers)
    assert Role.CONDUCTOR in next(worker.capabilities for worker in workers if worker.resource_id == "claude-fable-conductor")


def test_role_preferences_and_generalist_profile_are_schema_valid():
    preferences = _yaml("role_preferences.yaml")
    roles = [RolePreference.from_dict(item) for item in preferences["roles"]]
    generalist_payload = _yaml("generalist.yaml")
    generalist = GeneralistProfile.from_dict(
        {key: value for key, value in generalist_payload.items() if key != "schema_version"}
    )

    assert all(preference.required for preference in roles)
    assert generalist.independence == "self_review"
    assert Role.ORCHESTRATOR in generalist.covers
    assert set(generalist.covers) == set(Role) - {Role.GENERALIST}


def test_sprint_worker_policy_defines_bounded_antigravity_and_deepseek_lanes():
    policy = _yaml("sprint_worker_policy.yaml")

    assert policy["schema_version"] == "ariadne.sprint_worker_policy.v1"
    assert policy["worker_mix"]["antigravity"]["platform"] == "antigravity"
    assert policy["worker_mix"]["antigravity"]["default_model"] == "gemini-flash-3.5"
    assert policy["worker_mix"]["antigravity"]["maximum_instances"] == 1
    assert policy["worker_mix"]["deepseek_flash"]["minimum_instances"] == 1
    assert policy["worker_mix"]["deepseek_flash"]["maximum_instances"] == 3
    assert "no_orchestrator_substitution" in policy["verifier_checks"]
    assert policy["workspace_preflight"]["failure_posture"] == "revision_required_before_packet_dispatch"
    assert "workspace_receipts" in policy["required_plan_fields"]


def test_transport_adapters_record_codex_local_deepseek_spawn_as_non_shell_transport():
    adapters = _yaml("transport_adapters.yaml")
    deepseek = next(item for item in adapters["adapters"] if item["adapter_id"] == "codex_local_deepseek_spawn")

    assert adapters["schema_version"] == "ariadne.transport_adapters.v1"
    assert deepseek["invocation"] == "local_codex_call_or_spawn"
    assert deepseek["shell_probe_applicable"] is False
    assert "codex_local_spawn" in deepseek["allowed_probe_methods"]


def test_user_override_schema_is_strict_and_compaction_safe():
    overrides = _yaml("user_overrides.yaml")

    assert overrides == {"schema_version": "ariadne.user_overrides.v1", "overrides": []}
    override = UserOverride.from_dict({
        "override_id": "override-1", "scope": "sprint", "target": "role:verifier",
        "value": "gpt-terra-primary", "expiry": "2026-08-11", "recorded_at": "2026-07-11",
    })
    assert override.target == "role:verifier"


def test_conductor_plan_and_verifier_result_are_exact_and_traceable():
    assignment = {
        "role": "verifier", "resource_id": "deepseek-flash-verifier",
        "model": "deepseek-4-flash", "reasoning": "medium",
        "selection_basis": ["role_preference", "available_probe"],
        "fallback_reason": "", "independence_label": "independent_provider",
        "user_override_ref": "", "orchestrator_substituted": False,
        "unfilled_obligations": [],
    }
    plan = ConductorPlan.from_dict({
        "plan_id": "ariadne-s4b-dry-run", "sprint_id": "s4b",
        "settings_fingerprint": "sha256:settings", "assignments": [assignment],
    })
    result = VerifierResult.from_dict({
        "plan_id": plan.plan_id, "settings_fingerprint": plan.settings_fingerprint,
        "decision": "pass", "reasons": ["all settings matched"],
        "verified_at": "2026-07-11T00:00:00Z",
    })

    assert isinstance(plan.assignments[0], AssignmentRecord)
    assert not plan.assignments[0].orchestrator_substituted
    assert result.decision is VerifierDecision.PASS


@pytest.mark.parametrize(
    "payload",
    [
        {"resource_id": "bad"},
        {"resource_id": "bad", "probed_at": "now", "method": "manual", "reachability": "reachable", "availability": "available", "ttl_seconds": 0, "evidence": ["manual"]},
    ],
)
def test_allocation_schemas_fail_closed_for_incomplete_or_invalid_probe_data(payload: dict):
    with pytest.raises(ValueError):
        AvailabilityProbe.from_dict(payload)
