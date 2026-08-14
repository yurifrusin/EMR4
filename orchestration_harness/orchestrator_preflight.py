"""Pure, project-neutral orchestrator continuation and worker-pool checks."""

from __future__ import annotations

from typing import Any

from orchestration_harness.active_operation import receipt_projection


def _bounded_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value == value.strip()
        and "\r" not in value
        and "\n" not in value
        and len(value) <= 500
    )


def _parallelism_projection(
    *,
    runtime_state: dict[str, Any],
    policy: dict[str, Any],
    continuation_event: Any,
    active_operation: dict[str, Any],
    reasons: list[str],
) -> dict[str, Any]:
    """Validate an explicit three-lane efficacy decision for this continuation."""
    if continuation_event not in policy.get("required_events", []):
        return {}
    field = policy.get("runtime_state_field")
    value = runtime_state.get(field) if isinstance(field, str) else None
    if not isinstance(value, dict):
        reasons.append("parallelism_assessment_missing")
        return {}
    expected_keys = {
        "schema_version",
        "operation_id",
        "assessed_stage",
        "lanes",
        "parallel_work_packages",
        "serial_constraints",
        "reassessment_triggers",
    }
    if set(value) != expected_keys:
        reasons.append("parallelism_assessment_keys_invalid")
        return {}
    if value.get("schema_version") != policy.get("schema_version"):
        reasons.append("parallelism_assessment_schema_invalid")
    if value.get("operation_id") != active_operation.get("operation_id"):
        reasons.append("parallelism_assessment_operation_mismatch")
    if not _bounded_text(value.get("assessed_stage")):
        reasons.append("parallelism_assessment_stage_invalid")

    required_lane_ids = policy.get("required_lane_ids", [])
    dispositions = set(policy.get("admitted_dispositions", []))
    leverages = set(policy.get("admitted_leverage", []))
    lanes = value.get("lanes")
    lane_by_id: dict[Any, Any] = {}
    if isinstance(lanes, list):
        lane_by_id = {
            lane.get("lane_id"): lane for lane in lanes if isinstance(lane, dict)
        }
    if (
        not isinstance(lanes, list)
        or len(lanes) != len(required_lane_ids)
        or set(lane_by_id) != set(required_lane_ids)
    ):
        reasons.append("parallelism_lane_inventory_invalid")
    else:
        rationales: list[str] = []
        for lane_id in required_lane_ids:
            lane = lane_by_id[lane_id]
            if set(lane) != {
                "lane_id",
                "disposition",
                "expected_leverage",
                "rationale",
                "work_packages",
            }:
                reasons.append(f"parallelism_lane_keys_invalid:{lane_id}")
                continue
            if lane.get("disposition") not in dispositions:
                reasons.append(f"parallelism_lane_disposition_invalid:{lane_id}")
            if lane.get("expected_leverage") not in leverages:
                reasons.append(f"parallelism_lane_leverage_invalid:{lane_id}")
            rationale = lane.get("rationale")
            if not _bounded_text(rationale):
                reasons.append(f"parallelism_lane_rationale_missing:{lane_id}")
            else:
                rationales.append(rationale)
            work_packages = lane.get("work_packages")
            if (
                not isinstance(work_packages, list)
                or any(not _bounded_text(item) for item in work_packages)
                or len(work_packages) != len(set(work_packages))
            ):
                reasons.append(f"parallelism_work_packages_invalid:{lane_id}")
            elif lane.get("disposition") in {"planned", "dispatched", "completed"} and not work_packages:
                reasons.append(f"parallelism_work_package_missing:{lane_id}")
        if policy.get("require_distinct_rationale_per_lane") is True and len(
            rationales
        ) != len(set(rationales)):
            reasons.append("parallelism_lane_rationales_not_distinct")

    list_fields = (
        "parallel_work_packages",
        "serial_constraints",
        "reassessment_triggers",
    )
    for list_field in list_fields:
        items = value.get(list_field)
        if (
            not isinstance(items, list)
            or any(not _bounded_text(item) for item in items)
            or len(items) != len(set(items))
        ):
            reasons.append(f"parallelism_{list_field}_invalid")
    if not value.get("reassessment_triggers"):
        reasons.append("parallelism_reassessment_triggers_missing")
    if (
        policy.get("require_serial_constraints_or_positive_parallel_work") is True
        and not value.get("parallel_work_packages")
        and not value.get("serial_constraints")
    ):
        reasons.append("parallelism_efficacy_basis_missing")
    return value


def _has_evidence(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(
            isinstance(item, str) and bool(item.strip()) for item in value
        )
    return False


def _source_evidence(
    *,
    runtime_state: dict[str, Any],
    observation_by_id: dict[Any, dict[str, Any]],
) -> tuple[dict[str, Any], set[str]]:
    """Return explicit evidence, with typed primary-session prefixes as fallback."""
    supplied = runtime_state.get("source_evidence")
    evidence = dict(supplied) if isinstance(supplied, dict) else {}
    explicit_sources = set(evidence)
    prefixed_sources: set[str] = set()
    ambiguous_sources: set[str] = set()
    primary = observation_by_id.get("codex_primary_session", {})
    observations = primary.get("evidence", [])
    if isinstance(observations, list):
        for observation in observations:
            if not isinstance(observation, str) or ":" not in observation:
                continue
            source, detail = observation.split(":", 1)
            source = source.strip()
            detail = detail.strip()
            if source in prefixed_sources and source not in explicit_sources:
                ambiguous_sources.add(source)
            prefixed_sources.add(source)
            if source and detail and source not in evidence:
                evidence[source] = detail
    return evidence, ambiguous_sources


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
    if requirements.get("schema_version") != "ariadne.orchestrator_requirements.v2":
        reasons.append("orchestrator_requirements_invalid")
    if adapters.get("schema_version") != "ariadne.transport_adapters.v1":
        reasons.append("transport_adapters_invalid")
    if worker_pool.get("schema_version") != "ariadne.worker_pool.v1":
        reasons.append("worker_pool_invalid")
    if runtime_state.get("schema_version") != "ariadne.orchestrator_runtime_state.v1":
        reasons.append("runtime_state_invalid")

    allowed_events = requirements.get("continuation_events", [])
    continuation_event = runtime_state.get("continuation_event")
    if continuation_event not in allowed_events:
        reasons.append("continuation_event_missing_or_unapproved")

    latch_policy = requirements.get("active_operation_latch", {})
    latch_required_events = latch_policy.get("required_events", [])
    active_operation: dict[str, Any] = {}
    if continuation_event in latch_required_events:
        if "active_operation" not in runtime_state:
            reasons.append("active_operation_latch_missing")
        else:
            try:
                active_operation = receipt_projection(runtime_state["active_operation"])
            except ValueError:
                reasons.append("active_operation_latch_invalid")

    parallelism_assessment = _parallelism_projection(
        runtime_state=runtime_state,
        policy=requirements.get("parallelism_assessment", {}),
        continuation_event=continuation_event,
        active_operation=active_operation,
        reasons=reasons,
    )

    adapter_by_id = {
        item.get("adapter_id"): item
        for item in adapters.get("adapters", [])
        if isinstance(item, dict)
    }
    observations = runtime_state.get("adapter_observations", [])
    observation_by_id = {
        item.get("adapter_id"): item for item in observations if isinstance(item, dict)
    }
    if requirements.get("required_adapter_observations") == "all_declared":
        for adapter_id, adapter in adapter_by_id.items():
            observation = observation_by_id.get(adapter_id)
            if observation is None:
                reasons.append(f"adapter_observation_missing:{adapter_id}")
                continue
            if observation.get("method") not in adapter.get(
                "allowed_probe_methods", []
            ):
                reasons.append(f"adapter_probe_method_invalid:{adapter_id}")
            if observation.get("reachability") not in {
                "reachable",
                "unreachable",
                "unknown",
            }:
                reasons.append(f"adapter_reachability_invalid:{adapter_id}")
            if (
                not isinstance(observation.get("evidence"), list)
                or not observation["evidence"]
            ):
                reasons.append(f"adapter_evidence_missing:{adapter_id}")

    resources = {
        item.get("resource_id"): item
        for item in worker_pool.get("workers", [])
        if isinstance(item, dict)
    }
    slots = runtime_state.get("worker_slots", [])
    slots_by_resource = {
        item.get("resource_id"): item for item in slots if isinstance(item, dict)
    }
    managed_resources = requirements.get("worker_slot_management", {}).get(
        "managed_resource_ids", []
    )
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
    if isinstance(context_state, dict) and isinstance(
        context_state.get("agent_contexts"), list
    ):
        contexts_by_agent = {
            item.get("agent_id"): item
            for item in context_state["agent_contexts"]
            if isinstance(item, dict)
        }
    else:
        reasons.append("context_health_missing")

    planned_action = runtime_state.get("planned_action")
    hard_event = continuation_event in context_policy.get("hard_rehydration_events", [])
    required_sources_by_event = context_policy.get(
        "required_rehydration_sources_by_event", {}
    )
    required_rehydration_sources = (
        required_sources_by_event.get(continuation_event, [])
        if isinstance(required_sources_by_event, dict)
        else []
    )
    source_evidence, ambiguous_source_evidence = _source_evidence(
        runtime_state=runtime_state,
        observation_by_id=observation_by_id,
    )
    source_policy_missing = hard_event and not required_rehydration_sources
    if source_policy_missing:
        reasons.append(f"rehydration_source_policy_missing:{continuation_event}")
    high_authority = planned_action in context_policy.get("high_authority_actions", [])
    mandatory_ratio = context_policy.get("provider_meter", {}).get(
        "mandatory_rehydration_ratio"
    )
    receipt_sources: list[str] = []
    source_gate_passed = not source_policy_missing
    for agent_id in context_policy.get("required_agent_ids", []):
        context = contexts_by_agent.get(agent_id)
        if context is None:
            reasons.append(f"context_observation_missing:{agent_id}")
            source_gate_passed = False
            continue
        if hard_event and context.get("rehydrated_from_receipt") is not True:
            reasons.append(f"context_rehydration_required:{agent_id}")
            source_gate_passed = False
        if required_rehydration_sources:
            observed_sources = context.get("rehydration_sources")
            if not isinstance(observed_sources, list):
                observed_sources = []
            for required_source in required_rehydration_sources:
                if required_source not in observed_sources:
                    reasons.append(
                        f"rehydration_source_missing:{agent_id}:{required_source}"
                    )
                    source_gate_passed = False
                    continue
                if required_source not in receipt_sources:
                    receipt_sources.append(required_source)
                if not _has_evidence(source_evidence.get(required_source)):
                    reasons.append(
                        "rehydration_source_evidence_missing:"
                        f"{agent_id}:{required_source}"
                    )
                    source_gate_passed = False
                if required_source in ambiguous_source_evidence:
                    reasons.append(
                        "rehydration_source_evidence_ambiguous:"
                        f"{agent_id}:{required_source}"
                    )
                    source_gate_passed = False
        source = context.get("measurement_source")
        if source == "provider_reported":
            input_tokens = context.get("input_tokens")
            context_limit = context.get("context_limit_tokens")
            if (
                not isinstance(input_tokens, int)
                or not isinstance(context_limit, int)
                or context_limit < 1
            ):
                reasons.append(f"provider_context_measurement_invalid:{agent_id}")
            elif (
                isinstance(mandatory_ratio, (int, float))
                and input_tokens / context_limit >= mandatory_ratio
            ):
                reasons.append(f"context_mandatory_rehydration_threshold:{agent_id}")
        elif (
            source == "unknown"
            and high_authority
            and context.get("rehydrated_from_receipt") is not True
        ):
            reasons.append(f"context_rehydration_required:{agent_id}")

    receipt_evidence = {
        source: source_evidence[source]
        for source in receipt_sources
        if _has_evidence(source_evidence.get(source))
    }
    return {
        "schema_version": "ariadne.orchestrator_receipt.v1",
        "status": "passed" if not reasons else "revision_required",
        "settings_fingerprint": settings_fingerprint,
        "continuation_event": runtime_state.get("continuation_event"),
        "planned_action": planned_action,
        "reasons": reasons,
        "rehydrated_from_receipt": source_gate_passed
        and bool(required_rehydration_sources),
        "rehydration_sources": receipt_sources,
        "source_evidence": receipt_evidence,
        "active_operation": active_operation,
        "parallelism_assessment": parallelism_assessment,
        "terminal_handback_permitted": active_operation.get(
            "terminal_handback_permitted"
        ),
        "worker_dispatch_permitted": not reasons,
        "authority_boundary": "receipt_only_no_worker_control_or_integration_authority",
    }
