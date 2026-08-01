#!/usr/bin/env python3
"""Minimal desk-context descendant of the receptionist-first contract."""

from __future__ import annotations

import copy
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_receptionist_first_v61 as v61
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v62"
)
DESK_CONTEXT_SCHEMA_PATH = ARTIFACT_DIR / "desk-context.schema.json"
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
MODEL_FORM_BODY_SCHEMA_PATH = v61.MODEL_FORM_BODY_SCHEMA_PATH
CORRECTION_TICKET_SCHEMA_PATH = v61.CORRECTION_TICKET_SCHEMA_PATH
DIALOGUE_PROTOCOL = "reception.one.bureau.receptionist-first.v6.2"
PROTOCOL_VERSION = "reception.one.bureau.receptionist-first-cell.v6.2"
CONTRACT_MODE = "receptionist-v62"
POLICY_ID = "reception-one-receptionist-first-v62-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = "reception.one.bureau.receptionist-and-form.v6.2"
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v62.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v62.parent_audit_event.v1"
)
PARENT_RESULT_PASS = "reception_one_receptionist_first_v62_occupied_pass"
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v62_occupied_no_release"
)
MAX_PROVIDER_CALLS = 2
MAX_CORRECTION_TURNS = 1
TEMPERATURE = v61.TEMPERATURE
THINKING_BUDGET = v61.THINKING_BUDGET
MAX_OUTPUT_TOKENS = v61.MAX_OUTPUT_TOKENS
INCLUDE_THOUGHTS = v61.INCLUDE_THOUGHTS
PREPRINTED_FIELDS = v61.PREPRINTED_FIELDS
MODEL_AUTHORED_FIELDS = v61.MODEL_AUTHORED_FIELDS
TYPED_FORM_FIELDS = v61.TYPED_FORM_FIELDS
BASELINE_METADATA = {
    **v61.BASELINE_METADATA,
    "minimal_desk_context": True,
    "shared_model_proofreader_context_hash": True,
}
CORRECTION_ELIGIBLE_CODES = v61.CORRECTION_ELIGIBLE_CODES

SYSTEM_INSTRUCTION = (
    v61.SYSTEM_INSTRUCTION
    + """

The desk_context is a small, source-labelled view of what a careful medical
receptionist would have on the desk for this one authored-synthetic request.
Use it together with the staff utterances, never as independent authority.
Resolve references in this order: the latest staff utterance, an explicit
correction, earlier staff utterances, the staff-selected Diary appointment,
then clarification only if the request remains ambiguous.

The selected_appointment row is readable context for deictic or elliptical
requests such as 'shift Margaret's appointment'. It does not turn a request to
arrange or book a new appointment into a move. Explicit create language remains
create; explicit move, resize, cancel and status language remains that action.
Use the request-local binding_code stamped on the selected appointment when the
typed form needs binding:selected_appointment. Do not invent missing context,
dump the desk context, or treat it as permission to execute a command."""
)

ReceptionistFirstError = v61.ReceptionistFirstError
canonical_json = v61.canonical_json
canonical_hash = v61.canonical_hash
validate_exact = v61.validate_exact
assemble_program = v61.assemble_program
model_form_body = v61.model_form_body
vertex_response_schema = v61.vertex_response_schema
review_receptionist_output = v61.review_receptionist_output
parse_vertex_output = v61.parse_vertex_output
parse_vertex_program = v61.parse_vertex_program
evaluate_program = v61.evaluate_program
build_correction_ticket = v61.build_correction_ticket


def _rows_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in rows}


def _binding_code(task: dict[str, Any], source_handle: str) -> int:
    matches = [
        row["code"]
        for row in task["binding_table"]
        if row["source_handle"] == source_handle
    ]
    if len(matches) != 1:
        raise ReceptionistFirstError("desk_context_binding_not_exact")
    return matches[0]


def _grounded_mention(
    frame: dict[str, Any],
    *,
    entity_type: str,
) -> dict[str, Any] | None:
    try:
        mention = typed_plan.mention_binding(frame, entity_type)
    except ValueError:
        return None
    collection = "patients" if entity_type == "patient" else "practitioners"
    rows = frame["context"][collection]
    folded = mention["text"].casefold()
    matches = [
        row
        for row in rows
        if folded
        in {
            row["display"].casefold(),
            *(alias.casefold() for alias in row["aliases"]),
        }
    ]
    if len(matches) != 1:
        raise ReceptionistFirstError("desk_context_mention_not_exact")
    row = matches[0]
    return {
        "authority_label": "fixture_intercepted",
        "source": "utterance",
        "entity_type": entity_type,
        "entity_ref": row["id"],
        "display": row["display"],
        "utterance_index": mention["utterance_index"],
        "text": mention["text"],
    }


def build_desk_context(
    frame: dict[str, Any],
    *,
    base_task: dict[str, Any] | None = None,
) -> dict[str, Any]:
    typed_plan.validate_schema(frame, "input")
    if frame["data_class"] != "authored_synthetic":
        raise ReceptionistFirstError("desk_context_data_class_not_admitted")
    if len(frame["utterances"]) > 4:
        raise ReceptionistFirstError("desk_context_dialogue_too_large")
    task = (
        copy.deepcopy(base_task)
        if base_task is not None
        else structured.build_model_input(frame)
    )
    context = frame["context"]
    patients = _rows_by_id(context["patients"])
    practitioners = _rows_by_id(context["practitioners"])
    selected = context.get("selected_appointment")
    selected_context = None
    if selected is not None:
        patient = patients.get(selected["patient_ref"])
        practitioner = practitioners.get(selected["practitioner_ref"])
        if patient is None or practitioner is None:
            raise ReceptionistFirstError(
                "desk_context_selected_appointment_not_grounded"
            )
        selected_context = {
            "authority_label": "staff_selected",
            "source": "appointment",
            "binding_code": _binding_code(
                task,
                "binding:selected_appointment",
            ),
            "appointment_ref": selected["id"],
            "patient_ref": selected["patient_ref"],
            "patient_display": patient["display"],
            "practitioner_ref": selected["practitioner_ref"],
            "practitioner_display": practitioner["display"],
            "date": selected["date"],
            "start_time": selected["start_time"],
            "duration_minutes": selected["duration_minutes"],
            "status": selected["status"],
        }
    mentions = [
        value
        for value in (
            _grounded_mention(frame, entity_type="patient"),
            _grounded_mention(frame, entity_type="practitioner"),
        )
        if value is not None
    ]
    value = {
        "contract_version": "reception.one.bureau.desk-context.v1",
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "authority": "context_only_no_command_authority",
        "current_diary": {
            "authority_label": "fixture_intercepted",
            "source": "diary",
            "practice_ref": frame["practice_ref"],
            "reference_date": frame["reference_date"],
        },
        "recent_dialogue": {
            "authority_label": "staff_selected",
            "source": "bernie_session",
            "turns": [
                {
                    "utterance_index": index,
                    "speaker": "reception_staff",
                    "text": text,
                }
                for index, text in enumerate(frame["utterances"])
            ],
        },
        "selected_appointment": selected_context,
        "grounded_mentions": mentions,
        "freshness": {
            "context_revision": frame["context_revision"],
            "observed_at": frame["observed_at"],
            "expires_at": frame["expires_at"],
            "clock": "frozen_authored_synthetic_scenario",
        },
        "resolution_precedence": [
            "latest_staff_utterance",
            "explicit_correction",
            "earlier_staff_utterance",
            "selected_diary_context",
            "clarify_if_still_ambiguous",
        ],
        "excluded_context": [
            "unselected_appointments",
            "full_diary",
            "patient_history",
            "clinical_data",
            "database_access",
            "command_authority",
        ],
    }
    validate_exact(value, DESK_CONTEXT_SCHEMA_PATH)
    return value


def build_model_task(frame: dict[str, Any]) -> dict[str, Any]:
    task = structured.build_model_input(frame)
    task["desk_context"] = build_desk_context(frame, base_task=task)
    return task


def build_turn_input(
    frame: dict[str, Any],
    *,
    correction_ticket: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task = build_model_task(frame)
    turn_code = 2 if correction_ticket is not None else 1
    if correction_ticket is not None:
        v61._validate_ticket(correction_ticket)
    value = {
        "contract_version": DIALOGUE_PROTOCOL,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "turn_code": turn_code,
        "task_sha256": canonical_hash(task),
        "desk_context_sha256": canonical_hash(task["desk_context"]),
        "bureau_packet": {
            "broker_owned_fields": PREPRINTED_FIELDS,
            "model_authored_sections": list(MODEL_AUTHORED_FIELDS),
        },
        "task": task,
        "correction_ticket": copy.deepcopy(correction_ticket),
    }
    validate_turn_input(frame, value)
    return value


def validate_turn_input(frame: dict[str, Any], value: dict[str, Any]) -> None:
    validate_exact(value, TURN_INPUT_SCHEMA_PATH)
    validate_exact(value["task"]["desk_context"], DESK_CONTEXT_SCHEMA_PATH)
    expected = build_model_task(frame)
    if value["task"] != expected:
        raise ReceptionistFirstError("turn_task_frame_mismatch")
    if value["task_sha256"] != canonical_hash(expected):
        raise ReceptionistFirstError("turn_task_hash_mismatch")
    if value["desk_context_sha256"] != canonical_hash(
        expected["desk_context"]
    ):
        raise ReceptionistFirstError("desk_context_hash_mismatch")
    if value["bureau_packet"] != {
        "broker_owned_fields": PREPRINTED_FIELDS,
        "model_authored_sections": list(MODEL_AUTHORED_FIELDS),
    }:
        raise ReceptionistFirstError("bureau_packet_boundary_mismatch")
    ticket = value["correction_ticket"]
    if value["turn_code"] == 1 and ticket is not None:
        raise ReceptionistFirstError("turn_one_ticket_forbidden")
    if value["turn_code"] == 2:
        if not isinstance(ticket, dict):
            raise ReceptionistFirstError("turn_two_ticket_required")
        v61._validate_ticket(ticket)


def build_vertex_request(turn_input: dict[str, Any]) -> dict[str, Any]:
    validate_exact(turn_input, TURN_INPUT_SCHEMA_PATH)
    return {
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": canonical_json(turn_input)}],
            }
        ],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "responseMimeType": "application/json",
            "responseSchema": vertex_response_schema(),
            "thinkingConfig": {
                "thinkingBudget": THINKING_BUDGET,
                "includeThoughts": INCLUDE_THOUGHTS,
            },
        },
    }


def evaluate_output(
    frame: dict[str, Any],
    program: dict[str, Any],
    body: dict[str, Any],
    *,
    turn_code: int,
    turn_input: dict[str, Any],
) -> dict[str, Any]:
    validate_turn_input(frame, turn_input)
    if turn_input["turn_code"] != turn_code:
        raise ReceptionistFirstError("proofreader_turn_code_mismatch")
    result = v61.evaluate_output(
        frame,
        program,
        body,
        turn_code=turn_code,
    )
    context = turn_input["task"]["desk_context"]
    result["context_frame_review"] = {
        "disposition": "admit",
        "task_sha256": turn_input["task_sha256"],
        "desk_context_sha256": turn_input["desk_context_sha256"],
        "reviewed_context_revision": context["freshness"][
            "context_revision"
        ],
        "source_labels": [
            context["current_diary"]["authority_label"],
            context["recent_dialogue"]["authority_label"],
            (
                context["selected_appointment"]["authority_label"]
                if context["selected_appointment"] is not None
                else "selected_appointment_absent"
            ),
        ],
        "command_authority": False,
        "same_packet_seen_by_model_and_proofreader": True,
    }
    return result


def build_provider_blocked_evidence() -> dict[str, Any]:
    frame, correct_program = v61.dialogue._known_move()
    turn_input = build_turn_input(frame)
    body = model_form_body(correct_program, frame=frame)
    program, parsed_body, usage = parse_vertex_output(
        v61._provider_packet(body)
    )
    admitted = evaluate_output(
        frame,
        program,
        parsed_body,
        turn_code=1,
        turn_input=turn_input,
    )
    if (
        admitted["disposition"] != "admit"
        or admitted["context_frame_review"]["disposition"] != "admit"
    ):
        raise ReceptionistFirstError(
            "provider_blocked_v62_context_assertion_not_proven"
        )
    return {
        "schema_version": (
            "reception.one.receptionist_first_v62.provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v62_provider_blocked_pass"
        ),
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "system_instruction_sha256": canonical_hash(
            {"text": SYSTEM_INSTRUCTION}
        ),
        "response_schema_sha256": canonical_hash(vertex_response_schema()),
        "turn_input_sha256": canonical_hash(turn_input),
        "task_sha256": turn_input["task_sha256"],
        "desk_context_sha256": turn_input["desk_context_sha256"],
        "context_frame_review": admitted["context_frame_review"],
        "thinking": {
            "budget": THINKING_BUDGET,
            "include_thoughts": INCLUDE_THOUGHTS,
            "thought_token_count_fixture": usage["thoughtsTokenCount"],
            "hidden_reasoning_retained": False,
        },
        "scope": {
            "all_twenty_four_v6_cases_required": True,
            "raw_authored_synthetic_utterances_retained": True,
            "full_diary_exposed": False,
            "unselected_appointments_exposed": False,
            "command_authority": False,
        },
    }


__all__ = [
    "ARTIFACT_DIR",
    "BASELINE_METADATA",
    "CONTRACT_MODE",
    "CORRECTION_ELIGIBLE_CODES",
    "CORRECTION_TICKET_SCHEMA_PATH",
    "DESK_CONTEXT_SCHEMA_PATH",
    "DIALOGUE_PROTOCOL",
    "INCLUDE_THOUGHTS",
    "MAX_CORRECTION_TURNS",
    "MAX_OUTPUT_TOKENS",
    "MAX_PROVIDER_CALLS",
    "MODEL_AUTHORED_FIELDS",
    "MODEL_FORM_BODY_SCHEMA_PATH",
    "MODEL_RESPONSE_CONTRACT",
    "PARENT_AUDIT_EVENT_SCHEMA_VERSION",
    "PARENT_EVIDENCE_SCHEMA_VERSION",
    "PARENT_RESULT_NO_RELEASE",
    "PARENT_RESULT_PASS",
    "POLICY_ID",
    "PREPRINTED_FIELDS",
    "PROTOCOL_VERSION",
    "ReceptionistFirstError",
    "SYSTEM_INSTRUCTION",
    "TEMPERATURE",
    "THINKING_BUDGET",
    "TURN_INPUT_SCHEMA_PATH",
    "TYPED_FORM_FIELDS",
    "assemble_program",
    "build_correction_ticket",
    "build_desk_context",
    "build_model_task",
    "build_provider_blocked_evidence",
    "build_turn_input",
    "build_vertex_request",
    "canonical_hash",
    "canonical_json",
    "evaluate_output",
    "evaluate_program",
    "model_form_body",
    "parse_vertex_output",
    "parse_vertex_program",
    "review_receptionist_output",
    "validate_exact",
    "validate_turn_input",
    "vertex_response_schema",
]
