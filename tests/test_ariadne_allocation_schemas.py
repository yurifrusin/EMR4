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
        "openai-primary-orchestrator", "claude-fable-conductor", "claude-opus-conductor",
        "gpt-sol-conductor-fallback",
        "deepseek-pro-conductor-fallback",
        "deepseek-pro-routine-coordinator",
        "openai-terra-tranche-executor", "openai-luna-mechanical-coordinator",
        "antigravity-gemini-flash-3-7-high-verifier", "deepseek-flash-verifier", "deepseek-flash-workers",
    }
    assert any(worker.transport.value == "cli_headless" for worker in workers)
    assert Role.CONDUCTOR in next(worker.capabilities for worker in workers if worker.resource_id == "claude-fable-conductor")
    coordinator = next(
        worker for worker in workers
        if worker.resource_id == "deepseek-pro-routine-coordinator"
    )
    flash = next(
        worker for worker in workers if worker.resource_id == "deepseek-flash-workers"
    )
    gemini = next(
        worker
        for worker in workers
        if worker.resource_id == "antigravity-gemini-flash-3-7-high-verifier"
    )
    assert Role.IMPLEMENTER not in coordinator.capabilities
    assert Role.IMPLEMENTER in flash.capabilities
    assert Role.IMPLEMENTER not in gemini.capabilities


def test_role_preferences_and_generalist_profile_are_schema_valid():
    preferences = _yaml("role_preferences.yaml")
    roles = [RolePreference.from_dict(item) for item in preferences["roles"]]
    generalist_payload = _yaml("generalist.yaml")
    generalist = GeneralistProfile.from_dict(
        {key: value for key, value in generalist_payload.items() if key != "schema_version"}
    )

    assert next(item for item in roles if item.role is Role.CONDUCTOR).required is False
    assert next(item for item in roles if item.role is Role.ORCHESTRATOR).required is True
    assert next(item for item in roles if item.role is Role.VERIFIER).required is False
    assert generalist.independence == "self_review"
    assert Role.ORCHESTRATOR in generalist.covers
    assert set(generalist.covers) == set(Role) - {Role.GENERALIST}
    conductor = next(item for item in roles if item.role is Role.CONDUCTOR)
    assert conductor.preferences == (
        "deepseek-pro-conductor-fallback",
        "claude-fable-conductor",
        "claude-opus-conductor",
        "gpt-sol-conductor-fallback",
    )


def test_sprint_worker_policy_defines_bounded_antigravity_and_deepseek_lanes():
    policy = _yaml("sprint_worker_policy.yaml")

    assert policy["schema_version"] == "ariadne.sprint_worker_policy.v1"
    assert policy["worker_mix"]["antigravity"]["platform"] == "antigravity"
    assert policy["worker_mix"]["antigravity"]["default_model"] == "gemini-3.7-flash-high"
    assert policy["worker_mix"]["antigravity"]["default_reasoning"] == "high"
    assert policy["worker_mix"]["antigravity"]["maximum_instances"] == 1
    assert policy["worker_mix"]["deepseek_flash"]["minimum_instances"] == 0
    assert policy["worker_mix"]["deepseek_flash"]["maximum_instances"] == 3
    assert "no_orchestrator_substitution" in policy["deterministic_plan_checks"]
    assert policy["workspace_preflight"]["failure_posture"] == "revision_required_before_packet_dispatch"
    assert "workspace_receipts" in policy["required_plan_fields"]

    verifier_id = "antigravity-gemini-flash-3-7-high-verifier"
    adapters = _yaml("transport_adapters.yaml")
    antigravity = next(
        item
        for item in adapters["adapters"]
        if item["adapter_id"] == "antigravity_cli_print"
    )
    security = _yaml("security_review_protocol.yaml")
    assert policy["worker_mix"]["antigravity"]["default_resource_id"] == verifier_id
    assert antigravity["resource_ids"] == [verifier_id]
    assert security["roles"]["red"]["preferred_resource_id"] == verifier_id


def test_transport_adapters_record_headless_primary_and_deepcode_fallback():
    adapters = _yaml("transport_adapters.yaml")
    headless = next(item for item in adapters["adapters"] if item["adapter_id"] == "deepseek_via_claude_code_bare")
    deepseek = next(item for item in adapters["adapters"] if item["adapter_id"] == "deepcode_cli")
    profile = _yaml("deepcode_model_profile.yaml")

    assert adapters["schema_version"] == "ariadne.transport_adapters.v1"
    assert headless["invocation"] == "claude_print_bare_deepseek_api"
    assert "deepseek_claude_cli_observation" in headless["allowed_probe_methods"]
    assert deepseek["invocation"] == "deepcode_prompt_tui"
    assert deepseek["shell_probe_applicable"] is True
    assert "deepcode_cli_observation" in deepseek["allowed_probe_methods"]
    assert profile["models"]["default"] == "deepseek-v4-flash"
    assert profile["reasoning"]["allowed"] == ["high", "max"]
    assert profile["execution_mode"] == "interactive_tty_required"


def test_user_override_schema_is_strict_and_compaction_safe():
    overrides = _yaml("user_overrides.yaml")

    assert overrides == {"schema_version": "ariadne.user_overrides.v1", "overrides": []}
    override = UserOverride.from_dict({
        "override_id": "override-1", "scope": "sprint", "target": "role:verifier",
        "value": "openai-primary-orchestrator", "expiry": "2026-08-11", "recorded_at": "2026-07-11",
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
