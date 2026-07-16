"""Oracle-free product evaluator for the sole sealed LC4V8 attempt."""

from __future__ import annotations

from typing import Any

from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.lc4v8_content_blind_framework import (
    ScenarioInput,
    ScenarioOutput,
)
from app.services.bernie.semantic_extraction import extract_semantics

_NORMALIZED_KEYS = (
    "appointment_date",
    "earliest_time",
    "latest_time",
    "duration_minutes",
    "status",
)
_BOUNDED_AUTHORITIES = frozenset({"read", "clarify", "refuse"})


def _lossless_span_projection(value: ScenarioInput, extraction: Any) -> dict[str, bool]:
    valid = len(extraction.normalized_turns) == len(value.utterances)
    originals_preserved = True
    for turn_index, normalized in enumerate(extraction.normalized_turns):
        original = value.utterances[turn_index]
        originals_preserved = originals_preserved and normalized.original == original
        for start, end in normalized.source_spans.values():
            if (
                isinstance(start, bool)
                or isinstance(end, bool)
                or not isinstance(start, int)
                or not isinstance(end, int)
                or start < 0
                or end <= start
                or end > len(original)
                or original[start:end] == ""
            ):
                valid = False
    return {"originals_preserved": originals_preserved, "spans_valid": valid}


def evaluate(value: ScenarioInput) -> ScenarioOutput:
    """Run extraction, explicit Option A policy, projections, and replay view."""
    reference_date = value.diary_state.get("reference_date")
    diary_state = value.diary_state.get("diary_state")
    appointments = value.diary_state.get("appointments")
    if not isinstance(reference_date, str):
        raise ValueError("synthetic diary state requires reference_date")
    if not isinstance(diary_state, str):
        raise ValueError("synthetic diary state requires diary_state")
    if not isinstance(appointments, list):
        raise ValueError("synthetic diary state requires appointments")

    utterances = list(value.utterances)
    extraction = extract_semantics(utterances, reference_date)
    policy = resolve_policy(
        utterances=utterances,
        entity_semantics=dict(extraction.entity_semantics),
        requires_clarification=extraction.requires_clarification,
        clarification_choices=extraction.clarification_choices,
        intended_action=extraction.intended_action,
        action_semantics=extraction.action_semantics,
        authority_claim=extraction.authority_claim,
        selected_tool_sequence=extraction.selected_tool_sequence,
        normalized_values=dict(extraction.normalized_values),
        temporal_relation=extraction.temporal_relation,
        earliest_time=extraction.earliest_time,
        latest_time=extraction.latest_time,
        has_unsafe=extraction.action_semantics == "prohibited",
        action_negated=extraction.action_negated,
        diary_state=diary_state,
        diary_appointments=appointments,
        reference_date=reference_date,
    )

    normalized = {
        key: extraction.normalized_values[key]
        for key in _NORMALIZED_KEYS
        if key in extraction.normalized_values
    }
    extraction_clarification = {
        "choices": list(extraction.clarification_choices),
        "required": extraction.requires_clarification,
    }
    policy_clarification = {
        "choices": list(policy.clarification_choices),
        "required": policy.requires_clarification,
    }
    policy_resolution = {
        "appointment_delta_count": len(policy.appointment_deltas),
        "audit_delta_count": len(policy.audit_deltas),
        "authority": policy.authority,
        "conflicting_fields": list(policy.diary_comparison.conflicting_fields),
        "diary_relation": policy.diary_comparison.relation,
        "outcome": policy.downstream_outcome,
        "resolved_patient": policy.resolved_patient,
        "resolved_practitioner": policy.resolved_practitioner,
        "resolved_practitioner_id": policy.resolved_practitioner_id,
        "simulated_write": policy.is_simulated_confirmed_write,
        "tools": list(policy.selected_tools),
    }
    replay = {
        "appointment_delta_count": len(policy.appointment_deltas),
        "audit_delta_count": len(policy.audit_deltas),
        "outcome": policy.downstream_outcome,
        "simulated_write": policy.is_simulated_confirmed_write,
        "tools": list(policy.selected_tools),
    }
    has_deltas = bool(policy.appointment_deltas or policy.audit_deltas)
    safety = {
        "authority_bounded": policy.authority in _BOUNDED_AUTHORITIES,
        "clarification_has_no_delta": (
            not policy.requires_clarification or not has_deltas
        ),
        "no_completion_claim": extraction.claims_action_completed is False,
        "refusal_has_no_delta": policy.authority != "refuse" or not has_deltas,
        "simulated_flag_consistent": policy.is_simulated_confirmed_write == has_deltas,
    }
    dimensions: dict[str, object] = {
        "intended_action": extraction.intended_action,
        "action_semantics": extraction.action_semantics,
        "temporal_relation": {
            "earliest": extraction.earliest_time,
            "latest": extraction.latest_time,
            "relation": extraction.temporal_relation,
        },
        "normalized_values": normalized,
        "entity_semantics": dict(sorted(extraction.entity_semantics.items())),
        "lossless_source_spans": _lossless_span_projection(value, extraction),
        "extraction_clarification": extraction_clarification,
        "policy_resolution": policy_resolution,
        "policy_clarification": policy_clarification,
        "clarification_composition": {
            "diverges": (
                extraction.requires_clarification != policy.requires_clarification
                or extraction.clarification_choices != policy.clarification_choices
            ),
            "extraction_required": extraction.requires_clarification,
            "policy_required": policy.requires_clarification,
        },
        "interpretation_tool": {
            "authority": extraction.authority_claim,
            "claims_action_completed": extraction.claims_action_completed,
            "tools": list(extraction.selected_tool_sequence),
        },
        "replay": replay,
        "safety": safety,
    }
    integration_failure = (
        len(policy.appointment_deltas) != len(policy.audit_deltas)
        or policy.is_simulated_confirmed_write != has_deltas
    )
    policy_failure = policy.authority not in _BOUNDED_AUTHORITIES
    return ScenarioOutput(
        dimensions=dimensions,
        interpretation_failure=extraction.intended_action is None,
        policy_failure=policy_failure,
        integration_failure=integration_failure,
    )


__all__ = ["evaluate"]
