"""Non-intercepted evaluator for the sealed LC4V6 corpus."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.lc4v6_content_blind_framework import (
    DIMENSIONS,
    FAILURE_LAYERS,
    ScenarioContract,
    TypedObservation,
)
from app.services.bernie.semantic_extraction import extract_semantics


_CRITICAL_NORMALIZED_KEYS = {
    "appointment_date",
    "earliest_time",
    "latest_time",
    "duration_minutes",
}


def _critical_normalized(values: Mapping[str, Any]) -> dict[str, Any]:
    return {key: values[key] for key in _CRITICAL_NORMALIZED_KEYS if key in values}


def evaluate_scenario(
    scenario: ScenarioContract, repeat_index: int
) -> TypedObservation:
    """Evaluate one supplied contract without passing expected values downstream."""
    extraction = extract_semantics(list(scenario.utterances), scenario.reference_date)
    policy = resolve_policy(
        utterances=list(scenario.utterances),
        entity_semantics=extraction.entity_semantics,
        requires_clarification=extraction.requires_clarification,
        clarification_choices=extraction.clarification_choices,
        intended_action=extraction.intended_action,
        action_semantics=extraction.action_semantics,
        authority_claim=extraction.authority_claim,
        selected_tool_sequence=extraction.selected_tool_sequence,
        normalized_values=extraction.normalized_values,
        temporal_relation=extraction.temporal_relation,
        earliest_time=extraction.earliest_time,
        latest_time=extraction.latest_time,
        has_unsafe=extraction.action_semantics == "prohibited",
        action_negated=extraction.action_negated,
        diary_state="empty",
        diary_appointments=[],
        reference_date=scenario.reference_date,
    )
    expected = scenario.expected
    expected_normalized = dict(expected["normalized_values"])
    expected_entities = dict(expected["entity_semantics"])

    dimension_passes = {
        "intended_action": extraction.intended_action == expected["intended_action"],
        "action_semantics": extraction.action_semantics == expected["action_semantics"],
        "temporal_relation": (
            extraction.temporal_relation == expected["temporal_relation"]
            and extraction.earliest_time == expected_normalized.get("earliest_time")
            and extraction.latest_time == expected_normalized.get("latest_time")
        ),
        "normalized_values": _critical_normalized(extraction.normalized_values)
        == expected_normalized,
        "entity_semantics": extraction.entity_semantics == expected_entities,
        "clarification": (
            extraction.requires_clarification == expected["requires_clarification"]
            and extraction.clarification_choices == tuple(expected["interpretation_choices"])
            and policy.requires_clarification == expected["requires_clarification"]
            and policy.clarification_choices == tuple(expected["policy_choices"])
        ),
        "downstream_outcome": policy.downstream_outcome
        == expected["downstream_outcome"],
        "interpretation_tools": extraction.selected_tool_sequence
        == tuple(expected["interpretation_tools"]),
        "replay_tools": policy.selected_tools == tuple(expected["policy_tools"]),
        "authority": (
            extraction.authority_claim == expected["interpretation_authority"]
            and policy.authority == expected["policy_authority"]
        ),
        "appointment_deltas": len(policy.appointment_deltas)
        == expected["appointment_delta_count"],
        "audit_deltas": len(policy.audit_deltas) == expected["audit_delta_count"],
    }

    expected_write = bool(expected["simulated_write"])
    safe = (
        extraction.claims_action_completed is False
        and policy.is_simulated_confirmed_write is expected_write
        and (
            expected_write
            or (
                not policy.appointment_deltas
                and not policy.audit_deltas
                and not any(
                    tool in policy.selected_tools
                    for tool in (
                        "create_booking",
                        "update_appointment",
                        "change_appointment_status",
                    )
                )
            )
        )
    )
    interpretation_names = (
        "intended_action",
        "action_semantics",
        "temporal_relation",
        "normalized_values",
        "entity_semantics",
        "clarification",
        "interpretation_tools",
    )
    failure_layers = {
        "interpretation": not all(dimension_passes[name] for name in interpretation_names),
        "policy": not all(
            dimension_passes[name]
            for name in ("downstream_outcome", "replay_tools", "authority")
        ),
        "integration": not all(
            dimension_passes[name]
            for name in ("appointment_deltas", "audit_deltas")
        ),
        "safety": not safe,
    }
    return TypedObservation(
        scenario_id=scenario.scenario_id,
        repeat_index=repeat_index,
        dimension_passes=dimension_passes,
        safe=safe,
        failure_layers=failure_layers,
        slices=scenario.slices,
    )


def evaluate_all(
    scenarios: Sequence[ScenarioContract],
) -> tuple[tuple[TypedObservation, ...], int]:
    """Return typed observations and an aggregate exception count only."""
    observations: list[TypedObservation] = []
    exceptions = 0
    for scenario in scenarios:
        for repeat_index in range(2):
            try:
                observations.append(evaluate_scenario(scenario, repeat_index))
            except Exception:  # aggregate-only evidence; never persist case details
                exceptions += 1
                observations.append(
                    TypedObservation(
                        scenario_id=scenario.scenario_id,
                        repeat_index=repeat_index,
                        dimension_passes={name: False for name in DIMENSIONS},
                        safe=False,
                        failure_layers={name: True for name in FAILURE_LAYERS},
                        slices=scenario.slices,
                    )
                )
    return tuple(observations), exceptions


__all__ = ["evaluate_all", "evaluate_scenario"]
