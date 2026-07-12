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
    required_agent_ids = set(receipt_policy.get("required_agent_ids", []))
    if receipt_policy.get("require_assigned_agent_ids") is True:
        assigned_agent_ids = runtime_state.get("assigned_agent_ids", [])
        if not isinstance(assigned_agent_ids, list):
            reasons.append("assigned_agent_ids_invalid")
            assigned_agent_ids = []
        required_agent_ids.update(assigned_agent_ids)
    for agent_id in sorted(required_agent_ids):
        receipt = receipt_by_agent.get(agent_id)
        if receipt is None:
            reasons.append(f"workspace_receipt_missing:{agent_id}")
            continue
        if receipt.get("clean") is not True:
            reasons.append(f"workspace_not_clean:{agent_id}")
        if receipt.get("at_handoff_current") is not True:
            reasons.append(f"workspace_not_at_handoff:{agent_id}")

    context_policy = requirements.get("context_health", {})
    context_state = runtime_state.get("context_health")
    contexts_by_agent = {}
    if isinstance(context_state, dict) and isinstance(context_state.get("agent_contexts"), list):
        contexts_by_agent = {
            item.get("agent_id"): item
            for item in context_state["agent_contexts"]
            if isinstance(item, dict)
        }
    else:
        reasons.append("context_health_missing")

    planned_action = runtime_state.get("planned_action")
    hard_event = runtime_state.get("continuation_event") in context_policy.get("hard_rehydration_events", [])
    high_authority = planned_action in context_policy.get("high_authority_actions", [])
    mandatory_ratio = context_policy.get("provider_meter", {}).get("mandatory_rehydration_ratio")
    for agent_id in context_policy.get("required_agent_ids", []):
        context = contexts_by_agent.get(agent_id)
        if context is None:
            reasons.append(f"context_observation_missing:{agent_id}")
            continue
        if hard_event and context.get("rehydrated_from_receipt") is not True:
            reasons.append(f"context_rehydration_required:{agent_id}")
        source = context.get("measurement_source")
        if source == "provider_reported":
            input_tokens = context.get("input_tokens")
            context_limit = context.get("context_limit_tokens")
            if not isinstance(input_tokens, int) or not isinstance(context_limit, int) or context_limit < 1:
                reasons.append(f"provider_context_measurement_invalid:{agent_id}")
            elif isinstance(mandatory_ratio, (int, float)) and input_tokens / context_limit >= mandatory_ratio:
                reasons.append(f"context_mandatory_rehydration_threshold:{agent_id}")
        elif source == "unknown" and high_authority and context.get("rehydrated_from_receipt") is not True:
            reasons.append(f"context_rehydration_required:{agent_id}")

    return {
        "schema_version": "ariadne.orchestrator_receipt.v1",
        "status": "passed" if not reasons else "revision_required",
        "settings_fingerprint": settings_fingerprint,
        "continuation_event": runtime_state.get("continuation_event"),
        "planned_action": planned_action,
        "reasons": reasons,
        "worker_dispatch_permitted": not reasons,
        "authority_boundary": "receipt_only_no_worker_control_or_integration_authority",
    }
