"""Pure, project-neutral orchestrator continuation and worker-pool checks."""

from __future__ import annotations

from typing import Any


def build_orchestrator_receipt(
    *,
    requirements: dict[str, Any],
    adapters: dict[str, Any],
    worker_pool: dict[str, Any],
    runtime_state: dict[str, Any],
    settings_fingerprint: str,
) -> dict[str, Any]:
    """Validate supplied evidence only; never inspect or control an agent."""
    reasons: list[str] = []
    if requirements.get("schema_version") != "ariadne.orchestrator_requirements.v1":
        reasons.append("orchestrator_requirements_invalid")
    if adapters.get("schema_version") != "ariadne.transport_adapters.v1":
        reasons.append("transport_adapters_invalid")
    if worker_pool.get("schema_version") != "ariadne.worker_pool.v1":
        reasons.append("worker_pool_invalid")
    if runtime_state.get("schema_version") != "ariadne.orchestrator_runtime_state.v1":
        reasons.append("runtime_state_invalid")

    allowed_events = requirements.get("continuation_events", [])
    if runtime_state.get("continuation_event") not in allowed_events:
        reasons.append("continuation_event_missing_or_unapproved")

    adapter_by_id = {item.get("adapter_id"): item for item in adapters.get("adapters", []) if isinstance(item, dict)}
    observations = runtime_state.get("adapter_observations", [])
    observation_by_id = {item.get("adapter_id"): item for item in observations if isinstance(item, dict)}
    if requirements.get("required_adapter_observations") == "all_declared":
        for adapter_id, adapter in adapter_by_id.items():
            observation = observation_by_id.get(adapter_id)
            if observation is None:
                reasons.append(f"adapter_observation_missing:{adapter_id}")
                continue
            if observation.get("method") not in adapter.get("allowed_probe_methods", []):
                reasons.append(f"adapter_probe_method_invalid:{adapter_id}")
            if observation.get("reachability") not in {"reachable", "unreachable", "unknown"}:
                reasons.append(f"adapter_reachability_invalid:{adapter_id}")
            if not isinstance(observation.get("evidence"), list) or not observation["evidence"]:
                reasons.append(f"adapter_evidence_missing:{adapter_id}")

    resources = {item.get("resource_id"): item for item in worker_pool.get("workers", []) if isinstance(item, dict)}
    slots = runtime_state.get("worker_slots", [])
    slots_by_resource = {item.get("resource_id"): item for item in slots if isinstance(item, dict)}
    managed_resources = requirements.get("worker_slot_management", {}).get("managed_resource_ids", [])
    for resource_id in managed_resources:
        slot = slots_by_resource.get(resource_id)
        resource = resources.get(resource_id)
        if slot is None or resource is None:
            reasons.append(f"worker_slot_inventory_missing:{resource_id}")
            continue
        active = slot.get("active_instance_ids")
        stale = slot.get("stale_instance_ids")
        if not isinstance(active, list) or not isinstance(stale, list):
            reasons.append(f"worker_slot_inventory_invalid:{resource_id}")
            continue
        if len(active) > resource.get("max_instances", 0):
            reasons.append(f"worker_slot_limit_exceeded:{resource_id}")
        if stale:
            reasons.append(f"stale_worker_resolution_required:{resource_id}")

    receipt_policy = requirements.get("workspace_receipts", {})
    receipt_by_agent = {
        item.get("agent_id"): item
        for item in runtime_state.get("workspace_receipts", [])
        if isinstance(item, dict)
    }
    for agent_id in receipt_policy.get("required_agent_ids", []):
        receipt = receipt_by_agent.get(agent_id)
        if receipt is None:
            reasons.append(f"workspace_receipt_missing:{agent_id}")
            continue
        if receipt.get("clean") is not True:
            reasons.append(f"workspace_not_clean:{agent_id}")
        if receipt.get("at_handoff_current") is not True:
            reasons.append(f"workspace_not_at_handoff:{agent_id}")

    return {
        "schema_version": "ariadne.orchestrator_receipt.v1",
        "status": "passed" if not reasons else "revision_required",
        "settings_fingerprint": settings_fingerprint,
        "continuation_event": runtime_state.get("continuation_event"),
        "reasons": reasons,
        "worker_dispatch_permitted": not reasons,
        "authority_boundary": "receipt_only_no_worker_control_or_integration_authority",
    }
