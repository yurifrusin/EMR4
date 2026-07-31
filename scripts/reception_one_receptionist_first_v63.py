#!/usr/bin/env python3
"""Form-toolkit repair descendant of the receptionist-first v6.2 contract."""

from __future__ import annotations

import copy
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_receptionist_first_v61 as v61
from scripts import reception_one_receptionist_first_v62 as v62


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v63"
)
DESK_CONTEXT_SCHEMA_PATH = v62.DESK_CONTEXT_SCHEMA_PATH
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
MODEL_FORM_BODY_SCHEMA_PATH = v62.MODEL_FORM_BODY_SCHEMA_PATH
CORRECTION_TICKET_SCHEMA_PATH = v62.CORRECTION_TICKET_SCHEMA_PATH
DIALOGUE_PROTOCOL = "reception.one.bureau.receptionist-first.v6.3"
PROTOCOL_VERSION = "reception.one.bureau.receptionist-first-cell.v6.3"
CONTRACT_MODE = "receptionist-v63"
POLICY_ID = "reception-one-receptionist-first-v63-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = "reception.one.bureau.receptionist-and-form.v6.3"
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v63.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v63.parent_audit_event.v1"
)
PARENT_RESULT_PASS = "reception_one_receptionist_first_v63_occupied_pass"
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v63_occupied_no_release"
)
MAX_PROVIDER_CALLS = 2
MAX_CORRECTION_TURNS = 1
TEMPERATURE = v62.TEMPERATURE
THINKING_BUDGET = v62.THINKING_BUDGET
MAX_OUTPUT_TOKENS = 3072
INCLUDE_THOUGHTS = v62.INCLUDE_THOUGHTS
PREPRINTED_FIELDS = v62.PREPRINTED_FIELDS
MODEL_AUTHORED_FIELDS = v62.MODEL_AUTHORED_FIELDS
TYPED_FORM_FIELDS = v62.TYPED_FORM_FIELDS
BASELINE_METADATA = {
    **v62.BASELINE_METADATA,
    "form_toolkit_guidance": True,
    "response_ceiling_repair": True,
}
CORRECTION_ELIGIBLE_CODES = v62.CORRECTION_ELIGIBLE_CODES

SYSTEM_INSTRUCTION = (
    v62.SYSTEM_INSTRUCTION
    + """

Treat the typed form as a receptionist's exact toolkit. A name or phrase in a
staff utterance is evidence to resolve; it is not itself an already resolved
entity. First use the matching resolver operator and then use that operator's
typed output wherever the form requires a patient, practitioner, appointment
or slot.

For an explicit move of the staff-selected appointment, use this sequence:
resolve the named patient when present; read the selected appointment using
binding:selected_appointment; search typed candidate slots using the resolved
appointment, requested constraints and any resolved practitioner; then prepare
the move from those typed results. Do not label a mention binding as a patient
or appointment entity.

Status words are not free-form aliases. Use a requested status only when the
binding table contains the exact request-local binding:status entry. If it
does not, ask a concise clarification rather than inventing a mapping. In
particular, do not assume that 'no-show' means the typed status 'dna' unless
that exact alias is stamped into the request."""
)

ReceptionistFirstError = v62.ReceptionistFirstError
canonical_json = v62.canonical_json
canonical_hash = v62.canonical_hash
validate_exact = v62.validate_exact
assemble_program = v62.assemble_program
model_form_body = v62.model_form_body
vertex_response_schema = v62.vertex_response_schema
review_receptionist_output = v62.review_receptionist_output
parse_vertex_output = v62.parse_vertex_output
parse_vertex_program = v62.parse_vertex_program
evaluate_program = v62.evaluate_program
build_correction_ticket = v62.build_correction_ticket
build_desk_context = v62.build_desk_context
build_model_task = v62.build_model_task


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
            "provider_blocked_v63_context_assertion_not_proven"
        )
    return {
        "schema_version": (
            "reception.one.receptionist_first_v63.provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v63_provider_blocked_pass"
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
        "repair": {
            "maximum_output_tokens": MAX_OUTPUT_TOKENS,
            "form_toolkit_guidance": True,
            "no_show_to_dna_alias_added": False,
            "output_schema_changed": False,
            "proofreader_changed": False,
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
