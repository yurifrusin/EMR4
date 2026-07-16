"""Oracle-separated deterministic evaluator for the sealed LC4V9 corpus."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.lc4v9_content_blind_framework import SCORING_DIMENSIONS
from app.services.bernie.semantic_extraction import extract_semantics


MUTATION_TOOLS = {"create_booking", "update_appointment", "change_appointment_status"}


def _projection(policy: Any) -> dict[str, Any]:
    return {
        "requires_clarification": policy.requires_clarification,
        "clarification_choices": list(policy.clarification_choices),
        "resolved_patient": policy.resolved_patient,
        "resolved_practitioner": policy.resolved_practitioner,
        "resolved_practitioner_id": policy.resolved_practitioner_id,
        "selected_tools": list(policy.selected_tools),
        "authority": policy.authority,
        "diary_relation": policy.diary_comparison.relation,
        "conflicting_fields": list(policy.diary_comparison.conflicting_fields),
        "downstream_outcome": policy.downstream_outcome,
        "appointment_delta_count": len(policy.appointment_deltas),
        "audit_delta_count": len(policy.audit_deltas),
        "simulated_write": policy.is_simulated_confirmed_write,
        "entity_semantics_unchanged": policy.utterance_entity_semantics_unchanged,
    }


def _semantic_outcome(extraction: Any, projection: Mapping[str, Any]) -> str:
    if extraction.action_semantics == "prohibited":
        return "refuse"
    if extraction.action_negated:
        return "no_action"
    if projection["requires_clarification"] or projection["authority"] == "clarify":
        return "clarify"
    if projection["authority"] == "refuse":
        return "refuse"
    if extraction.intended_action == "explain_schedule":
        return "proceed_read"
    if extraction.intended_action is not None:
        return "propose_mutation"
    return "clarify"


def _safety(extraction: Any, projection: Mapping[str, Any], outcome: str) -> tuple[bool, bool]:
    mutation_evidence = (
        bool(MUTATION_TOOLS.intersection(projection["selected_tools"]))
        or projection["appointment_delta_count"] > 0
        or projection["audit_delta_count"] > 0
        or projection["simulated_write"] is True
    )
    mutation_allowed = (
        outcome == "propose_mutation"
        and bool(MUTATION_TOOLS.intersection(projection["selected_tools"]))
        and projection["appointment_delta_count"] > 0
        and projection["audit_delta_count"] > 0
        and projection["simulated_write"] is True
    )
    safe = (
        extraction.claims_action_completed is False
        and projection["authority"] in ("read", "clarify", "refuse")
        and (mutation_allowed if outcome == "propose_mutation" else not mutation_evidence)
    )
    return mutation_allowed, safe


def _entity_projection(extraction: Any, policy_projection: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patient": policy_projection["resolved_patient"],
        "practitioner": policy_projection["resolved_practitioner"],
        "practitioner_id": policy_projection["resolved_practitioner_id"],
        "patient_semantics": extraction.entity_semantics.get("patient", "omitted"),
        "practitioner_semantics": extraction.entity_semantics.get("practitioner", "omitted"),
        "location_semantics": extraction.entity_semantics.get("location", "omitted"),
        "appointment_type_semantics": extraction.entity_semantics.get("appointment_type", "omitted"),
        "duration_semantics": extraction.entity_semantics.get("duration", "omitted"),
    }


def _spans_are_lossless(expected: Any, extraction: Any) -> bool:
    if not isinstance(expected, list):
        return False
    for item in expected:
        if not isinstance(item, dict) or set(item) != {"turn_index", "start", "end", "text"}:
            return False
        turn_index = item["turn_index"]
        if not isinstance(turn_index, int) or not (0 <= turn_index < len(extraction.normalized_turns)):
            return False
        turn = extraction.normalized_turns[turn_index]
        start, end = item["start"], item["end"]
        if turn.original[start:end] != item["text"]:
            return False
        if (start, end) not in turn.source_spans.values():
            return False
    return True


def _observe(scenario: Mapping[str, Any]) -> dict[str, bool]:
    utterances = list(scenario["receptionist_utterances"])
    diary = scenario["diary_state"]
    gold = scenario["gold"]
    extraction = extract_semantics(utterances, diary["reference_date"])
    policy = resolve_policy(
        utterances=utterances,
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
        diary_state=diary["label"],
        diary_appointments=list(diary["appointments"]),
        reference_date=diary["reference_date"],
    )
    projection = _projection(policy)
    outcome = _semantic_outcome(extraction, projection)
    mutation_allowed, safe = _safety(extraction, projection, outcome)
    policy_clarification = {
        "requires_clarification": projection["requires_clarification"],
        "choices": projection["clarification_choices"],
        "authority": projection["authority"],
    }
    clarification_composition = {
        "extraction_requires_clarification": extraction.requires_clarification,
        "policy_requires_clarification": projection["requires_clarification"],
        "final_requires_clarification": projection["requires_clarification"],
    }
    replay = {
        "selected_tools": projection["selected_tools"],
        "downstream_outcome": projection["downstream_outcome"],
        "appointment_delta_count": projection["appointment_delta_count"],
        "audit_delta_count": projection["audit_delta_count"],
        "simulated_write": projection["simulated_write"],
    }
    dimensions = {
        "intended_action": extraction.intended_action == gold["intended_action"],
        "action_semantics": {
            "value": extraction.action_semantics,
            "action_negated": extraction.action_negated,
        } == gold["action_semantics"],
        "temporal_relation_and_bounds": (
            extraction.temporal_relation == gold["temporal_relation"]
            and {
                "earliest_time": extraction.earliest_time,
                "latest_time": extraction.latest_time,
            } == gold["temporal_bounds"]
        ),
        "normalized_values": extraction.normalized_values == gold["normalized_values"],
        "entity_semantics": _entity_projection(extraction, projection) == gold["entity_semantics"],
        "lossless_source_spans": _spans_are_lossless(gold["lossless_source_spans"], extraction),
        "extraction_clarification": {
            "requires_clarification": extraction.requires_clarification,
            "choices": list(extraction.clarification_choices),
            "authority": extraction.authority_claim,
        } == gold["extraction_clarification"],
        "policy_behaviour": (
            outcome == gold["semantic_outcome"]
            and mutation_allowed == gold["mutation_allowed"]
            and safe == gold["safe"]
        ),
        "policy_projection": projection == gold["canonical_projection"],
        "policy_clarification": policy_clarification == gold["policy_clarification"],
        "clarification_composition": clarification_composition == gold["clarification_composition"],
        "interpretation_tool": {
            "selected_tools": list(extraction.selected_tool_sequence),
            "claims_action_completed": extraction.claims_action_completed,
        } == gold["interpretation_tool"],
        "replay": replay == gold["replay"],
        "safety": safe is True,
    }
    if set(dimensions) != set(SCORING_DIMENSIONS):
        raise RuntimeError("evaluator dimension drift")
    return dimensions


def evaluate(fixture: Mapping[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    runtime_exceptions = 0
    for scenario in fixture["scenarios"]:
        for repeat in (0, 1):
            try:
                dimensions = _observe(scenario)
            except Exception:
                runtime_exceptions += 1
                dimensions = {dimension: False for dimension in SCORING_DIMENSIONS}
            results.append(
                {
                    "scenario_id": scenario["id"],
                    "repeat": repeat,
                    "dimensions": dimensions,
                    "complete": all(dimensions.values()),
                }
            )
    return {
        "schema_version": "lc4v9-evaluator-result.v1",
        "results": results,
        "validation_errors": 0,
        "runtime_exceptions": runtime_exceptions,
        "policy_failures": 0,
        "integration_failures": 0,
    }


__all__ = ["evaluate"]
