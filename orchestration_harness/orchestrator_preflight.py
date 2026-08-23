"""Pure, project-neutral orchestrator continuation and worker-pool checks."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Any

from orchestration_harness.active_operation import (
    receipt_projection,
    validate_active_operation,
)


SERIAL_CONTINUATION_INTENT_VERSION = "ariadne.serial_continuation_intent.v1"
SERIAL_CONTINUATION_PRESET = "provider_free_serial_observed_empty_workers"
SERIAL_CONTINUATION_INTENT_KEYS = {
    "schema_version",
    "preset",
    "continuation_event",
    "planned_action",
    "assessed_stage",
    "active_evidence_paths",
    "lane_decision_overrides",
}
SERIAL_CONTINUATION_LANE_IDS = (
    "deepseek_flash",
    "gemini_verifier",
    "native_subagents",
)
SERIAL_CONTINUATION_DEFAULT_DECISIONS = {
    "deepseek_flash": "declined_negative",
    "gemini_verifier": "declined_neutral",
    "native_subagents": "declined_negative",
}
SERIAL_CONTINUATION_DECISIONS = {
    "declined_negative": ("declined", "negative"),
    "declined_neutral": ("declined", "neutral"),
    "not_applicable_neutral": ("not_applicable", "neutral"),
    "reserved_required_independence": ("reserved", "required_independence"),
}
SERIAL_CONTINUATION_REHYDRATION_SOURCES = (
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
)


class SerialContinuationIntentError(ValueError):
    """A compact serial-continuation intent is not safe to materialize."""


def _serial_reject(reason: str) -> None:
    raise SerialContinuationIntentError(reason)


def _bounded_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value == value.strip()
        and "\r" not in value
        and "\n" not in value
        and len(value) <= 500
    )


def _serial_evidence_path(raw: object, *, repo_root: Path) -> str:
    if (
        not isinstance(raw, str)
        or not raw
        or raw != raw.strip()
        or "\\" in raw
        or ":" in raw
        or len(raw) > 240
    ):
        _serial_reject("serial_continuation_evidence_path_invalid")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        _serial_reject("serial_continuation_evidence_path_invalid")
    admitted = bool(
        raw == "implementation_plan.md"
        or (path.parts and path.parts[0] == "docs")
        or path.parts[:2] == ("orchestration", "continuity")
        or path.parts[:2] == ("orchestration", "agent_inbox")
    )
    if not admitted:
        _serial_reject("serial_continuation_evidence_path_root_forbidden")
    root = repo_root.resolve()
    candidate = (root / Path(*path.parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        _serial_reject("serial_continuation_evidence_path_escape")
    if not candidate.is_file():
        _serial_reject("serial_continuation_evidence_path_missing")
    return path.as_posix()


def _serial_intent(
    value: object,
    *,
    repo_root: Path,
    requirements: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != SERIAL_CONTINUATION_INTENT_KEYS:
        _serial_reject("serial_continuation_intent_keys_invalid")
    if value.get("schema_version") != SERIAL_CONTINUATION_INTENT_VERSION:
        _serial_reject("serial_continuation_intent_schema_invalid")
    if value.get("preset") != SERIAL_CONTINUATION_PRESET:
        _serial_reject("serial_continuation_preset_invalid")
    event = value.get("continuation_event")
    if event not in requirements.get("continuation_events", []):
        _serial_reject("serial_continuation_event_invalid")
    if event == "pre_worker_dispatch":
        _serial_reject("serial_continuation_worker_dispatch_forbidden")
    if not _bounded_text(value.get("planned_action")):
        _serial_reject("serial_continuation_planned_action_invalid")
    if not _bounded_text(value.get("assessed_stage")):
        _serial_reject("serial_continuation_assessed_stage_invalid")

    raw_paths = value.get("active_evidence_paths")
    if not isinstance(raw_paths, list) or not 1 <= len(raw_paths) <= 32:
        _serial_reject("serial_continuation_evidence_paths_invalid")
    paths = [
        _serial_evidence_path(item, repo_root=repo_root) for item in raw_paths
    ]
    if len(paths) != len(set(paths)):
        _serial_reject("serial_continuation_evidence_paths_duplicate")

    overrides = value.get("lane_decision_overrides")
    if not isinstance(overrides, list) or len(overrides) > len(
        SERIAL_CONTINUATION_LANE_IDS
    ):
        _serial_reject("serial_continuation_lane_overrides_invalid")
    decisions = dict(SERIAL_CONTINUATION_DEFAULT_DECISIONS)
    seen_lanes: set[str] = set()
    for override in overrides:
        if not isinstance(override, dict) or set(override) != {
            "lane_id",
            "decision_code",
        }:
            _serial_reject("serial_continuation_lane_override_keys_invalid")
        lane_id = override.get("lane_id")
        decision_code = override.get("decision_code")
        if lane_id not in SERIAL_CONTINUATION_LANE_IDS:
            _serial_reject("serial_continuation_lane_id_invalid")
        if lane_id in seen_lanes:
            _serial_reject("serial_continuation_lane_override_duplicate")
        if decision_code not in SERIAL_CONTINUATION_DECISIONS:
            _serial_reject("serial_continuation_lane_decision_invalid")
        seen_lanes.add(lane_id)
        decisions[lane_id] = decision_code

    return {
        **value,
        "active_evidence_paths": paths,
        "lane_decisions": decisions,
    }


def materialize_serial_continuation_runtime_state(
    *,
    intent: object,
    requirements: dict[str, Any],
    adapters: dict[str, Any],
    worker_pool: dict[str, Any],
    active_operation: object,
    repo_root: Path,
) -> dict[str, Any]:
    """Expand one closed serial preset into the existing runtime-state schema."""
    normalized = _serial_intent(
        intent,
        repo_root=repo_root,
        requirements=requirements,
    )
    event = normalized["continuation_event"]
    required_sources_by_event = requirements.get("context_health", {}).get(
        "required_rehydration_sources_by_event"
    )
    required_sources = (
        required_sources_by_event.get(event)
        if isinstance(required_sources_by_event, dict)
        else None
    )
    if required_sources != list(SERIAL_CONTINUATION_REHYDRATION_SOURCES):
        _serial_reject("serial_continuation_rehydration_sources_invalid")

    latch = validate_active_operation(active_operation)
    lanes = []
    for lane_id in SERIAL_CONTINUATION_LANE_IDS:
        decision_code = normalized["lane_decisions"][lane_id]
        disposition, leverage = SERIAL_CONTINUATION_DECISIONS[decision_code]
        lanes.append(
            {
                "lane_id": lane_id,
                "disposition": disposition,
                "expected_leverage": leverage,
                "rationale": (
                    f"{lane_id} uses {decision_code}; the observed-empty serial "
                    "preset assigns it no work package."
                ),
                "work_packages": [],
            }
        )

    declared_adapters = adapters.get("adapters")
    if not isinstance(declared_adapters, list) or not declared_adapters:
        _serial_reject("serial_continuation_adapter_inventory_invalid")
    observations = []
    seen_adapters: set[str] = set()
    for adapter in declared_adapters:
        if not isinstance(adapter, dict):
            _serial_reject("serial_continuation_adapter_inventory_invalid")
        adapter_id = adapter.get("adapter_id")
        allowed_methods = adapter.get("allowed_probe_methods")
        if (
            not isinstance(adapter_id, str)
            or not adapter_id
            or adapter_id in seen_adapters
            or not isinstance(allowed_methods, list)
        ):
            _serial_reject("serial_continuation_adapter_inventory_invalid")
        seen_adapters.add(adapter_id)
        if adapter_id == "codex_primary_session":
            if "codex_session_observation" not in allowed_methods:
                _serial_reject("serial_continuation_primary_adapter_method_missing")
            observations.append(
                {
                    "adapter_id": adapter_id,
                    "method": "codex_session_observation",
                    "reachability": "reachable",
                    "evidence": [
                        "Primary orchestrator selected the typed serial preset."
                    ],
                }
            )
        else:
            if "synthetic_fixture" not in allowed_methods:
                _serial_reject("serial_continuation_adapter_method_missing")
            observations.append(
                {
                    "adapter_id": adapter_id,
                    "method": "synthetic_fixture",
                    "reachability": "unknown",
                    "evidence": [
                        "Observed-empty serial preset performed no live adapter probe."
                    ],
                }
            )

    managed_resource_ids = requirements.get("worker_slot_management", {}).get(
        "managed_resource_ids"
    )
    resources = worker_pool.get("workers")
    if (
        not isinstance(managed_resource_ids, list)
        or not managed_resource_ids
        or len(managed_resource_ids) != len(set(managed_resource_ids))
        or any(not isinstance(item, str) or not item for item in managed_resource_ids)
        or not isinstance(resources, list)
    ):
        _serial_reject("serial_continuation_worker_inventory_invalid")
    resource_ids = {
        item.get("resource_id")
        for item in resources
        if isinstance(item, dict) and isinstance(item.get("resource_id"), str)
    }
    if any(resource_id not in resource_ids for resource_id in managed_resource_ids):
        _serial_reject("serial_continuation_managed_worker_missing")

    return {
        "schema_version": "ariadne.orchestrator_runtime_state.v1",
        "continuation_event": event,
        "planned_action": normalized["planned_action"],
        "source_evidence": {
            "live_handover_current_baton": "AGENTS.md#3 Current Baton",
            "current_authority_allocation": (
                "AGENTS.md#4 Authority Allocation and the current harness settings"
            ),
            "active_plan_and_acceptance": normalized["active_evidence_paths"],
            "protected_evidence_boundaries": (
                "AGENTS.md#5 Protected Evidence and Closed Gates; "
                "AGENTS.md#6 User Decision Boundaries; canonical active latch"
            ),
            "git_refs_and_worktree": "machine_snapshot_only",
        },
        "active_operation": latch,
        "parallelism_assessment": {
            "schema_version": "ariadne.parallelism_assessment.v1",
            "operation_id": latch["operation_id"],
            "assessed_stage": normalized["assessed_stage"],
            "lanes": lanes,
            "parallel_work_packages": [],
            "serial_constraints": [
                "typed serial preset declares every managed worker slot observed empty",
                "worker dispatch requires a separate non-serial runtime state",
                "the current continuation completes before any external verifier",
            ],
            "reassessment_triggers": [
                "if the deterministic continuation fails",
                "before any worker dispatch",
                "at the next named tranche boundary",
            ],
        },
        "context_health": {
            "agent_contexts": [
                {
                    "agent_id": "orchestrator",
                    "measurement_source": "typed_serial_continuation_projection",
                    "rehydrated_from_receipt": True,
                    "rehydration_sources": list(
                        SERIAL_CONTINUATION_REHYDRATION_SOURCES
                    ),
                }
            ]
        },
        "adapter_observations": observations,
        "worker_slots": [
            {
                "resource_id": resource_id,
                "active_instance_ids": [],
                "stale_instance_ids": [],
            }
            for resource_id in managed_resource_ids
        ],
        "workspace_receipts": [],
        "assigned_agent_ids": [],
    }


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
        "worker_dispatch_permitted": (
            not reasons
            and active_operation.get("status") == "in_progress"
            and active_operation.get("user_attention_required") is False
        ),
        "authority_boundary": "receipt_only_no_worker_control_or_integration_authority",
    }
