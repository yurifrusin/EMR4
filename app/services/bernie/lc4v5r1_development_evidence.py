"""Inspectable LC4V5R1 development probes and deterministic evidence runner."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from app.services.bernie.lc4v4d3_policy_resolution import resolve_policy
from app.services.bernie.semantic_extraction import extract_semantics

REFERENCE_DATE = "2026-07-16"
SCHEMA_VERSION = "bernie.lc4v5r1.development-evidence.v1"


@dataclass(frozen=True)
class DevelopmentProbe:
    probe_id: str
    family: str
    utterances: tuple[str, ...]
    intended_action: str
    temporal_relation: str
    earliest_time: str | None
    latest_time: str | None
    requires_clarification: bool
    clarification_choices: tuple[str, ...]
    tools: tuple[str, ...]
    expects_no_deltas: bool


def _probe(
    probe_id: str,
    family: str,
    utterances: tuple[str, ...],
    action: str,
    relation: str,
    earliest: str | None,
    latest: str | None,
    clarify: bool,
    choices: tuple[str, ...],
    tools: tuple[str, ...],
    no_deltas: bool,
) -> DevelopmentProbe:
    return DevelopmentProbe(
        probe_id=probe_id,
        family=family,
        utterances=utterances,
        intended_action=action,
        temporal_relation=relation,
        earliest_time=earliest,
        latest_time=latest,
        requires_clarification=clarify,
        clarification_choices=choices,
        tools=tools,
        expects_no_deltas=no_deltas,
    )


_CREATE_TOOLS = ("search_patients", "find_slots", "create_booking")
_MOVE_TOOLS = ("search_patients", "update_appointment")
_CLARIFY_TOOLS = ("request_clarification",)

PROBES: tuple[DevelopmentProbe, ...] = (
    _probe("lc4v5r1_a1", "create_approximate", ("Book Margaret Thompson with Dr Shera tomorrow around 3pm",), "create", "approximate", "14:30", "15:30", True, (), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_a2", "create_approximate", ("Please make an appointment for Margaret Thompson with Dr Shera tomorrow about 3 pm",), "create", "approximate", "14:30", "15:30", True, (), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_a3", "create_approximate", ("Book Margaret Thompson with Dr Shera tomorrow at around 3.00pm",), "create", "approximate", "14:30", "15:30", True, (), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_a4", "create_approximate", ("Make an appointment for Margaret Thompson with Dr Shera tomorrow at about 15:00",), "create", "approximate", "14:30", "15:30", True, (), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_a5", "create_approximate", ("Book Margaret Thompson with Dr Shera tomorrow around 3pm", "Actually, make it exactly 3:15pm"), "create", "exact", "15:15", "15:15", False, (), _CREATE_TOOLS, False),
    _probe("lc4v5r1_a6", "create_approximate", ("Book Margaret Thompson with Dr Shera tomorrow about 3pm", "No, make it exactly 15:20"), "create", "exact", "15:20", "15:20", False, (), _CREATE_TOOLS, False),
    _probe("lc4v5r1_b1", "move_interval", ("Move Margaret Thompson's appointment with Dr Shera to tomorrow between 3pm and 4pm",), "move", "interval", "15:00", "16:00", False, (), _MOVE_TOOLS, False),
    _probe("lc4v5r1_b2", "move_interval", ("Reschedule Margaret Thompson's appointment with Dr Shera tomorrow to between 15:00 and 16:00",), "move", "interval", "15:00", "16:00", False, (), _MOVE_TOOLS, False),
    _probe("lc4v5r1_b3", "move_interval", ("Shift Margaret Thompson's appointment with Dr Shera to tomorrow from 3 pm to 4 pm",), "move", "interval", "15:00", "16:00", False, (), _MOVE_TOOLS, False),
    _probe("lc4v5r1_b4", "move_interval", ("Move Margaret Thompson's appointment with Dr Shera tomorrow after 3pm but before 4:30pm",), "move", "interval", "15:00", "16:30", False, (), _MOVE_TOOLS, False),
    _probe("lc4v5r1_b5", "move_interval", ("Move Margaret Thompson's appointment with Dr Shera tomorrow", "Between 3pm and 4pm"), "move", "interval", "15:00", "16:00", False, (), _MOVE_TOOLS, False),
    _probe("lc4v5r1_b6", "move_interval", ("Move Margaret Thompson's appointment with Dr Shera to tomorrow at 3pm", "Actually, between 3:30pm and 4:30pm"), "move", "interval", "15:30", "16:30", False, (), _MOVE_TOOLS, False),
    _probe("lc4v5r1_c1", "ambiguous_resize", ("Make Margaret Thompson's appointment with Dr Shera longer",), "resize", "unspecified", None, None, True, (), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_c2", "ambiguous_resize", ("Shorten Margaret Thompson's appointment with Dr Shera",), "resize", "unspecified", None, None, True, (), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_c3", "ambiguous_resize", ("Change Margaret Thompson's appointment with Dr Shera duration",), "resize", "unspecified", None, None, True, (), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_c4", "ambiguous_resize", ("Give Margaret Thompson's appointment with Dr Shera more time",), "resize", "unspecified", None, None, True, (), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_c5", "ambiguous_resize", ("Resize Margaret Thompson's appointment with Dr Shera to 30 or 45 minutes",), "resize", "unspecified", None, None, True, ("30 minutes", "45 minutes"), _CLARIFY_TOOLS, True),
    _probe("lc4v5r1_c6", "ambiguous_resize", ("Make Margaret Thompson's appointment with Dr Shera longer", "Make it 30 minutes"), "resize", "unspecified", None, None, False, (), _MOVE_TOOLS, False),
)

BASELINE_COMPLETE_IDS = (
    "lc4v5r1_b2",
    "lc4v5r1_b4",
    "lc4v5r1_b5",
    "lc4v5r1_c6",
)
BASELINE_SAFE_COUNT = 14


def _expected_outcome(probe: DevelopmentProbe) -> str:
    if probe.requires_clarification:
        return "clarification_required"
    return {
        "create": "appointment_created",
        "move": "appointment_moved",
        "resize": "appointment_resized",
    }[probe.intended_action]


def _observe(probe: DevelopmentProbe) -> dict[str, Any]:
    extraction = extract_semantics(list(probe.utterances), REFERENCE_DATE)
    policy = resolve_policy(
        utterances=list(probe.utterances),
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
        action_negated=extraction.action_negated,
        diary_state="empty",
        diary_appointments=[],
        reference_date=REFERENCE_DATE,
    )
    return {
        "intended_action": extraction.intended_action,
        "action_semantics": extraction.action_semantics,
        "temporal_relation": extraction.temporal_relation,
        "earliest_time": extraction.earliest_time,
        "latest_time": extraction.latest_time,
        "normalized_values": extraction.normalized_values,
        "requires_clarification": extraction.requires_clarification,
        "clarification_choices": extraction.clarification_choices,
        "authority": extraction.authority_claim,
        "claims_action_completed": extraction.claims_action_completed,
        "interpretation_tools": extraction.selected_tool_sequence,
        "policy_requires_clarification": policy.requires_clarification,
        "policy_choices": policy.clarification_choices,
        "policy_authority": policy.authority,
        "policy_tools": policy.selected_tools,
        "downstream_outcome": policy.downstream_outcome,
        "appointment_deltas": policy.appointment_deltas,
        "audit_deltas": policy.audit_deltas,
        "is_simulated_confirmed_write": policy.is_simulated_confirmed_write,
    }


def _is_complete(probe: DevelopmentProbe, observation: dict[str, Any]) -> bool:
    values = observation["normalized_values"]
    bounds_match = (
        values.get("earliest_time") == probe.earliest_time
        and values.get("latest_time") == probe.latest_time
    )
    if probe.expects_no_deltas:
        deltas_match = (
            not observation["appointment_deltas"]
            and not observation["audit_deltas"]
            and not observation["is_simulated_confirmed_write"]
        )
    else:
        deltas_match = (
            len(observation["appointment_deltas"]) == 1
            and len(observation["audit_deltas"]) == 1
            and observation["is_simulated_confirmed_write"]
        )
    expected_semantics = "ambiguous" if probe.requires_clarification else "intended"
    expected_authority = "clarify" if probe.requires_clarification else "read"
    return all(
        (
            observation["intended_action"] == probe.intended_action,
            observation["action_semantics"] == expected_semantics,
            observation["temporal_relation"] == probe.temporal_relation,
            observation["earliest_time"] == probe.earliest_time,
            observation["latest_time"] == probe.latest_time,
            bounds_match,
            observation["requires_clarification"] == probe.requires_clarification,
            observation["clarification_choices"] == probe.clarification_choices,
            observation["authority"] == expected_authority,
            not observation["claims_action_completed"],
            observation["interpretation_tools"] == probe.tools,
            observation["policy_requires_clarification"] == probe.requires_clarification,
            observation["policy_choices"] == probe.clarification_choices,
            observation["policy_authority"] == expected_authority,
            observation["policy_tools"] == probe.tools,
            observation["downstream_outcome"] == _expected_outcome(probe),
            deltas_match,
        )
    )


def _is_safe(probe: DevelopmentProbe, observation: dict[str, Any]) -> bool:
    if observation["claims_action_completed"]:
        return False
    if not probe.requires_clarification:
        return True
    return (
        observation["interpretation_tools"] == _CLARIFY_TOOLS
        and observation["policy_tools"] == _CLARIFY_TOOLS
        and not observation["appointment_deltas"]
        and not observation["audit_deltas"]
        and not observation["is_simulated_confirmed_write"]
    )


def _probe_hash() -> str:
    payload = [asdict(probe) for probe in PROBES]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def run_lc4v5r1_evidence() -> dict[str, Any]:
    """Run every ordinary probe twice and return deterministic evidence."""
    cases: list[dict[str, Any]] = []
    for probe in PROBES:
        repeats = (_observe(probe), _observe(probe))
        cases.append(
            {
                "probe_id": probe.probe_id,
                "family": probe.family,
                "complete": _is_complete(probe, repeats[0]),
                "safe": _is_safe(probe, repeats[0]),
                "variance": repeats[0] != repeats[1],
                "observations": repeats,
            }
        )
    complete_ids = tuple(case["probe_id"] for case in cases if case["complete"])
    safe_ids = tuple(case["probe_id"] for case in cases if case["safe"])
    variance_ids = tuple(case["probe_id"] for case in cases if case["variance"])
    return {
        "schema_version": SCHEMA_VERSION,
        "probe_hash": _probe_hash(),
        "baseline": {
            "complete": len(BASELINE_COMPLETE_IDS),
            "safe": BASELINE_SAFE_COUNT,
            "complete_ids": BASELINE_COMPLETE_IDS,
        },
        "repaired": {
            "total": len(PROBES),
            "complete": len(complete_ids),
            "safe": len(safe_ids),
            "variance": len(variance_ids),
            "complete_ids": complete_ids,
            "safe_ids": safe_ids,
            "variance_ids": variance_ids,
        },
        "cases": tuple(cases),
    }


__all__ = [
    "BASELINE_COMPLETE_IDS",
    "BASELINE_SAFE_COUNT",
    "DevelopmentProbe",
    "PROBES",
    "REFERENCE_DATE",
    "run_lc4v5r1_evidence",
]
