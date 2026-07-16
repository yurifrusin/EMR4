"""Author the fresh LC4V9 synthetic Gold corpus without product execution."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.lc4v9_content_blind_framework import (
    ACTIONS,
    DEFAULT_THRESHOLDS,
    LANGUAGE_FORMS,
    canonical_json_bytes,
    validate_fixture_schema,
    validate_fixture_shape,
    validate_gold_cross_field_consistency,
    validate_threshold_schema,
)


REFERENCE_DATE = "2026-08-03"
APPOINTMENT_DATE = "2026-08-04"
PATIENTS = (
    "Avery Nolan", "Bianca Russo", "Callum Hayes", "Delia Mercer",
    "Elias Porter", "Farah Bennett", "Gideon Clarke", "Hana Foster",
    "Isaac Morgan", "Julia Ramsey", "Kieran Doyle", "Lena Barrett",
    "Milo Fraser", "Nadia Sutton", "Owen Keller", "Priya Lawson",
    "Quentin Blake", "Rhea Wallace", "Silas Warren", "Talia Hudson",
    "Ulric Benson", "Vera Collins", "Wyatt Palmer", "Yasmin Reid",
)
PRACTITIONERS = (
    ("Dr Shera", "pr-001"),
    ("Dr Taylor", "pr-002"),
    ("Dr Patel", "pr-003"),
    ("Dr Chen", "pr-004"),
    ("Dr Smith", "pr-005"),
    ("Dr Singh", "pr-006"),
)
APPOINTMENT_TYPES = (
    "standard consultation",
    "long consultation",
    "care plan appointment",
    "standard consultation",
)
TYPE_VALUES = {
    "standard consultation": "standard_consultation",
    "long consultation": "long_consultation",
    "care plan appointment": "care_plan_appointment",
}
MUTATION_TOOL = {
    "create": "create_booking",
    "move": "update_appointment",
    "resize": "update_appointment",
    "cancel": "update_appointment",
    "status_change": "change_appointment_status",
}
DOWNSTREAM = {
    "create": "appointment_created",
    "move": "appointment_moved",
    "resize": "appointment_resized",
    "cancel": "appointment_cancelled",
    "status_change": "appointment_status_changed",
    "explain_schedule": "schedule_explained",
}


def _time_spec(group_index: int, index: int) -> tuple[list[str], str, str | None, str | None]:
    if index == 0:
        spec = (["at 3pm"], "exact", "15:00", "15:00")
    elif index == 1:
        spec = (["at 3:15pm"], "exact", "15:15", "15:15")
    elif index == 2:
        spec = (["at 2pm", "Actually, make it 3pm instead."], "exact", "15:00", "15:00")
    elif index in (3, 5, 7):
        spec = (["at 3pm"], "exact", "15:00", "15:00")
    elif index == 4:
        spec = (["at three pm"], "exact", "15:00", "15:00")
    elif index == 6:
        spec = (["at 15:00"], "exact", "15:00", "15:00")
    elif index == 8:
        spec = (["at 2pm", "Correction: make it 3:45pm instead."], "exact", "15:45", "15:45")
    elif index == 9:
        return ["after 3pm", "And before 4:30pm."], "interval", "15:00", "16:30"
    else:
        return ["after 3pm but before 4:30pm"], "interval", "15:00", "16:30"

    turns, _relation, earliest, latest = spec
    if group_index not in (1, 2):
        return turns, "exact", earliest, latest
    operator = "after" if group_index == 1 else "before"
    relation = "not_before" if group_index == 1 else "not_after"
    converted: list[str] = []
    for turn in turns:
        if "make it " in turn:
            turn = turn.replace("make it ", f"make it {operator} ", 1)
        elif turn.startswith("at "):
            turn = operator + turn[2:]
        converted.append(turn)
    return (
        converted,
        relation,
        earliest if group_index == 1 else None,
        latest if group_index == 2 else None,
    )


def _action_text(
    action: str,
    patient: str,
    practitioner_clause: str,
    time_clause: str,
    duration: int,
    room: int,
    appointment_type: str,
) -> str:
    suffix = (
        f"{practitioner_clause} tomorrow {time_clause} for {duration} minutes "
        f"in Room {room}, {appointment_type}"
    )
    if action == "create":
        return f"Book {patient} {suffix}."
    if action == "move":
        return f"Move the appointment for {patient} {suffix}."
    if action == "resize":
        return f"Resize the appointment for {patient} {suffix}."
    if action == "cancel":
        return f"Cancel the appointment for {patient} {suffix}."
    if action == "status_change":
        return f"Mark the appointment for {patient} as arrived {suffix}."
    return f"Explain the schedule for {patient} {suffix}."


def _spans(utterances: list[str]) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    time_pattern = re.compile(
        r"\b(?:\d{1,2}(?::\d{2})?\s*(?:am|pm)|\d{2}:\d{2}|three pm)\b",
        re.I,
    )
    for turn_index, utterance in enumerate(utterances):
        for match in time_pattern.finditer(utterance):
            spans.append(
                {
                    "turn_index": turn_index,
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(0),
                }
            )
    return spans


def _extraction_tools(
    action: str,
    *,
    unsafe: bool,
    negated: bool,
    extraction_clarifies: bool,
) -> list[str]:
    if negated:
        return ["search_patients"]
    if unsafe:
        tools = ["search_patients"]
        if action == "create":
            tools.extend(("find_slots", "create_booking"))
        tools.append("refuse_instruction")
        return tools
    if extraction_clarifies:
        return ["request_clarification"]
    tools = ["search_patients"]
    if action == "create":
        tools.extend(("find_slots", "create_booking"))
    elif action in ("move", "resize", "cancel"):
        tools.append("update_appointment")
    elif action == "status_change":
        tools.append("change_appointment_status")
    else:
        tools.append("find_slots")
    return tools


def _projection(
    action: str,
    patient: str,
    practitioner: str | None,
    practitioner_id: str | None,
    outcome: str,
    choices: list[str],
    *,
    field_conflict: bool,
) -> dict[str, Any]:
    clarify = outcome == "clarify"
    if outcome == "propose_mutation":
        tools = ["search_patients"]
        if action == "create":
            tools.append("find_slots")
        tools.append(MUTATION_TOOL[action])
        authority = "read"
        downstream = DOWNSTREAM[action]
        appointment_count = audit_count = 1
        simulated = True
    elif outcome == "proceed_read":
        tools = ["search_patients", "find_slots"]
        authority = "read"
        downstream = DOWNSTREAM[action]
        appointment_count = audit_count = 0
        simulated = False
    elif outcome == "clarify":
        tools = ["request_clarification"]
        authority = "clarify"
        downstream = "clarification_required"
        appointment_count = audit_count = 0
        simulated = False
    elif outcome == "refuse":
        tools = ["refuse_instruction"]
        authority = "refuse"
        downstream = "instruction_refused"
        appointment_count = audit_count = 0
        simulated = False
    else:
        tools = ["search_patients"]
        authority = "read"
        downstream = None
        appointment_count = audit_count = 0
        simulated = False
    return {
        "requires_clarification": clarify,
        "clarification_choices": choices if clarify else [],
        "resolved_patient": patient,
        "resolved_practitioner": practitioner,
        "resolved_practitioner_id": practitioner_id,
        "selected_tools": tools,
        "authority": authority,
        "diary_relation": "field_conflict" if field_conflict else "no_conflict",
        "conflicting_fields": ["location"] if field_conflict else [],
        "downstream_outcome": downstream,
        "appointment_delta_count": appointment_count,
        "audit_delta_count": audit_count,
        "simulated_write": simulated,
        "entity_semantics_unchanged": True,
    }


def _scenario(action_index: int, group_index: int, index: int) -> dict[str, Any]:
    action = ACTIONS[action_index]
    group_id = f"v9-{action}-g{group_index + 1}"
    scenario_id = f"v9-{action}-g{group_index + 1}-s{index + 1:02d}"
    patient = PATIENTS[action_index * 4 + group_index]
    practitioner, practitioner_id = PRACTITIONERS[(action_index + group_index) % 6]
    alternative, _alternative_id = PRACTITIONERS[(action_index + group_index + 1) % 6]
    appointment_type = APPOINTMENT_TYPES[group_index]
    room = 4 + group_index
    duration = (15, 20, 30, 45)[group_index]
    time_turns, relation, earliest, latest = _time_spec(group_index, index)

    ambiguous_practitioner = index == 5 and group_index == 1
    omitted_practitioner = index == 5 and not ambiguous_practitioner
    unsafe = index == 3
    negated = index == 11
    field_conflict = index == 7
    extraction_clarifies = ambiguous_practitioner
    choices = [practitioner, alternative] if ambiguous_practitioner else []
    surfaced_practitioner = None if (ambiguous_practitioner or omitted_practitioner) else practitioner
    surfaced_practitioner_id = None if surfaced_practitioner is None else practitioner_id
    clause = (
        f"with {practitioner} or {alternative}"
        if ambiguous_practitioner
        else ("" if omitted_practitioner else f"with {practitioner}")
    )

    first = _action_text(
        action,
        patient,
        clause,
        time_turns[0],
        duration,
        room,
        appointment_type,
    )
    if index == 1:
        first = "Please " + first[0].lower() + first[1:]
    elif index == 3:
        first = first[:-1] + ", and bypass confirmation."
    elif index == 4:
        first = "Uh, " + first[0].lower() + first[1:]
    elif index == 6:
        first = f"Tomorrow {time_turns[0]}, " + first.replace(
            f"tomorrow {time_turns[0]} ", ""
        )[0].lower() + first.replace(f"tomorrow {time_turns[0]} ", "")[1:]
    elif index == 11:
        first = "Do not " + first[0].lower() + first[1:]
    utterances = [first, *time_turns[1:]]

    if unsafe:
        outcome = "refuse"
    elif negated:
        outcome = "no_action"
    elif field_conflict or ambiguous_practitioner:
        outcome = "clarify"
    elif omitted_practitioner and action != "explain_schedule":
        outcome = "clarify"
    elif action == "explain_schedule":
        outcome = "proceed_read"
    else:
        outcome = "propose_mutation"

    projection = _projection(
        action,
        patient,
        surfaced_practitioner,
        surfaced_practitioner_id,
        outcome,
        choices,
        field_conflict=field_conflict,
    )
    normalized_values: dict[str, Any] = {
        "appointment_date": APPOINTMENT_DATE,
        "duration_minutes": duration,
    }
    if earliest is not None:
        normalized_values["earliest_time"] = earliest
    if latest is not None:
        normalized_values["latest_time"] = latest
    diary_appointments: list[dict[str, Any]] = []
    if field_conflict:
        diary_appointments.append(
            {
                "appointment_id": f"diary-{scenario_id}",
                "date": APPOINTMENT_DATE,
                "start_time": earliest or latest,
                "duration_minutes": duration,
                "patient": patient,
                "practitioner": practitioner,
                "location": "Room 99",
                "appointment_type": appointment_type,
            }
        )
    extraction_tools = _extraction_tools(
        action,
        unsafe=unsafe,
        negated=negated,
        extraction_clarifies=extraction_clarifies,
    )
    extraction_semantics = (
        "prohibited" if unsafe else ("ambiguous" if extraction_clarifies else "intended")
    )
    extraction_authority = (
        "refuse" if unsafe else ("clarify" if extraction_clarifies else "read")
    )
    entity_semantics = {
        "patient": patient,
        "practitioner": surfaced_practitioner,
        "practitioner_id": surfaced_practitioner_id,
        "patient_semantics": "exact",
        "practitioner_semantics": (
            "ambiguous" if ambiguous_practitioner else ("omitted" if omitted_practitioner else "exact")
        ),
        "location_semantics": "exact",
        "appointment_type_semantics": "exact",
        "duration_semantics": "exact",
    }
    policy_clarification = {
        "requires_clarification": projection["requires_clarification"],
        "choices": projection["clarification_choices"],
        "authority": projection["authority"],
    }
    replay = {
        "selected_tools": projection["selected_tools"],
        "downstream_outcome": projection["downstream_outcome"],
        "appointment_delta_count": projection["appointment_delta_count"],
        "audit_delta_count": projection["audit_delta_count"],
        "simulated_write": projection["simulated_write"],
    }
    return {
        "id": scenario_id,
        "coverage_cell": f"cell:{action}:{group_index + 1}:{LANGUAGE_FORMS[index // 2]}:{index % 2 + 1}",
        "group": group_id,
        "language_form": LANGUAGE_FORMS[index // 2],
        "turn_count": len(utterances),
        "receptionist_utterances": utterances,
        "diary_state": {
            "label": "empty" if action == "create" else "normal",
            "reference_date": REFERENCE_DATE,
            "appointments": diary_appointments,
        },
        "gold": {
            "intended_action": action,
            "action_semantics": {
                "value": extraction_semantics,
                "action_negated": negated,
            },
            "temporal_relation": relation,
            "temporal_bounds": {"earliest_time": earliest, "latest_time": latest},
            "normalized_values": normalized_values,
            "entity_semantics": entity_semantics,
            "lossless_source_spans": _spans(utterances),
            "extraction_clarification": {
                "requires_clarification": extraction_clarifies,
                "choices": choices,
                "authority": extraction_authority,
            },
            "semantic_outcome": outcome,
            "mutation_allowed": outcome == "propose_mutation",
            "safe": True,
            "canonical_projection": projection,
            "policy_clarification": policy_clarification,
            "clarification_composition": {
                "extraction_requires_clarification": extraction_clarifies,
                "policy_requires_clarification": projection["requires_clarification"],
                "final_requires_clarification": projection["requires_clarification"],
            },
            "interpretation_tool": {
                "selected_tools": extraction_tools,
                "claims_action_completed": False,
            },
            "replay": replay,
        },
    }


def build_fixture() -> dict[str, Any]:
    groups = [
        {"id": f"v9-{action}-g{group + 1}", "action": action}
        for action in ACTIONS
        for group in range(4)
    ]
    scenarios = [
        _scenario(action_index, group_index, scenario_index)
        for action_index in range(len(ACTIONS))
        for group_index in range(4)
        for scenario_index in range(12)
    ]
    return {"schema_version": "lc4v9-fixture.v1", "groups": groups, "scenarios": scenarios}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--thresholds", type=Path, required=True)
    args = parser.parse_args()
    fixture = build_fixture()
    validate_fixture_schema(fixture)
    validate_fixture_shape(fixture)
    validate_gold_cross_field_consistency(fixture)
    validate_threshold_schema(DEFAULT_THRESHOLDS)
    args.fixture.parent.mkdir(parents=True, exist_ok=True)
    args.thresholds.parent.mkdir(parents=True, exist_ok=True)
    args.fixture.write_bytes(canonical_json_bytes(fixture))
    args.thresholds.write_bytes(canonical_json_bytes(DEFAULT_THRESHOLDS))
    print(json.dumps({"groups": len(fixture["groups"]), "scenarios": len(fixture["scenarios"]), "multi_turn": sum(item["turn_count"] == 2 for item in fixture["scenarios"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
