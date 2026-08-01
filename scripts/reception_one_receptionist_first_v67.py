#!/usr/bin/env python3
"""Exact clarification-pattern descendant of receptionist-first v6.6."""

from __future__ import annotations

import copy
from datetime import datetime
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_receptionist_first_v61 as v61
from scripts import reception_one_receptionist_first_v65 as v65
from scripts import reception_one_receptionist_first_v66 as v66


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v67"
)
DESK_CONTEXT_SCHEMA_PATH = v66.DESK_CONTEXT_SCHEMA_PATH
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
MODEL_FORM_BODY_SCHEMA_PATH = v66.MODEL_FORM_BODY_SCHEMA_PATH
CORRECTION_TICKET_SCHEMA_PATH = v66.CORRECTION_TICKET_SCHEMA_PATH
DIALOGUE_PROTOCOL = "reception.one.bureau.receptionist-first.v6.7"
PROTOCOL_VERSION = "reception.one.bureau.receptionist-first-cell.v6.7"
CONTRACT_MODE = "receptionist-v67"
POLICY_ID = "reception-one-receptionist-first-v67-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = "reception.one.bureau.receptionist-and-form.v6.7"
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v67.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v67.parent_audit_event.v1"
)
PARENT_RESULT_PASS = "reception_one_receptionist_first_v67_occupied_pass"
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v67_occupied_no_release"
)
MAX_PROVIDER_CALLS = v66.MAX_PROVIDER_CALLS
MAX_CORRECTION_TURNS = v66.MAX_CORRECTION_TURNS
TEMPERATURE = v66.TEMPERATURE
THINKING_BUDGET = v66.THINKING_BUDGET
MAX_OUTPUT_TOKENS = v66.MAX_OUTPUT_TOKENS
INCLUDE_THOUGHTS = v66.INCLUDE_THOUGHTS
PREPRINTED_FIELDS = v66.PREPRINTED_FIELDS
MODEL_AUTHORED_FIELDS = v66.MODEL_AUTHORED_FIELDS
TYPED_FORM_FIELDS = v66.TYPED_FORM_FIELDS
RECOGNIZED_CONSTRAINT_CODE = v66.RECOGNIZED_CONSTRAINT_CODE
RECOGNIZED_CONSTRAINT_PATH_CODE = v66.RECOGNIZED_CONSTRAINT_PATH_CODE
CORRECTION_ELIGIBLE_CODES = v66.CORRECTION_ELIGIBLE_CODES
BASELINE_METADATA = {
    **v66.BASELINE_METADATA,
    "exact_clarification_response_pattern_taught": True,
    "proofreader_clarification_markers_changed": False,
}

SYSTEM_INSTRUCTION = (
    v66.SYSTEM_INSTRUCTION
    + """

For a clarification goal, use one exact receptionist clarification pattern.
Begin receptionist_response with exactly "Which do you mean:" or
"Could you clarify:". Ask one focused question using only the staff request
and typed desk context. If the ambiguity is fit-in versus ordinary booking,
name those two alternatives. End with exactly "No booking was changed."

If a correction ticket reports receptionist_response_goal_mismatch and the
required goal is clarification, replace the complete receptionist_response.
Do not preserve or paraphrase the rejected response. Use the exact pattern
above, for example: "Which do you mean: an ordinary booking or a squeeze-in
assessment? No booking was changed." """
)

ReceptionistFirstError = v66.ReceptionistFirstError
canonical_json = v66.canonical_json
canonical_hash = v66.canonical_hash
validate_exact = v66.validate_exact
assemble_program = v66.assemble_program
model_form_body = v66.model_form_body
vertex_response_schema = v66.vertex_response_schema
review_receptionist_output = v66.review_receptionist_output
parse_vertex_output = v66.parse_vertex_output
parse_vertex_program = v66.parse_vertex_program
evaluate_program = v66.evaluate_program
build_correction_ticket = v66.build_correction_ticket
build_desk_context = v66.build_desk_context
build_model_task = v66.build_model_task


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
    now: datetime | None = None,
) -> dict[str, Any]:
    """Apply the unchanged v6.6 proofreader to a v6.7-bound turn packet."""

    validate_turn_input(frame, turn_input)
    if turn_input["turn_code"] != turn_code:
        raise ReceptionistFirstError("proofreader_turn_code_mismatch")
    result = v61.evaluate_output(
        frame,
        program,
        body,
        turn_code=turn_code,
        now=now,
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
    if result["disposition"] != "admit":
        return result
    manifest, violations = v65._recognized_constraint_violations(
        frame,
        program,
        result["normalized_plan"],
    )
    manifest_hash = canonical_hash(manifest)
    if not violations:
        result["recognized_constraint_assertion"] = {
            "disposition": "admit",
            "manifest_sha256": manifest_hash,
            "constraint_count": len(manifest),
            "omitted_count": 0,
            "matching_mode": "typed_semantic_argument_role",
        }
        return result
    result.update(
        {
            "disposition": (
                "revision_required" if turn_code == 1 else "edge_abort"
            ),
            "correction_eligible": turn_code == 1,
            "correction_turns_remaining": 1 if turn_code == 1 else 0,
            "terminal": turn_code != 1,
            "violations": violations,
            "safe_repairs": [],
            "admitted_operator_ids": [],
            "candidate": None,
            "normalized_plan": None,
            "semantic_review": None,
            "recognized_constraint_assertion": {
                "disposition": "revision_required",
                "manifest_sha256": manifest_hash,
                "constraint_count": len(manifest),
                "omitted_count": len(violations),
                "matching_mode": "typed_semantic_argument_role",
            },
        }
    )
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
    if admitted["disposition"] != "admit":
        raise ReceptionistFirstError(
            "provider_blocked_v67_clarification_assertion_not_proven"
        )
    return {
        "schema_version": (
            "reception.one.receptionist_first_v67.provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v67_provider_blocked_pass"
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
        "recognized_constraint_assertion": admitted[
            "recognized_constraint_assertion"
        ],
        "thinking": {
            "budget": THINKING_BUDGET,
            "include_thoughts": INCLUDE_THOUGHTS,
            "thought_token_count_fixture": usage["thoughtsTokenCount"],
            "hidden_reasoning_retained": False,
        },
        "repair": {
            "exact_clarification_response_pattern_taught": True,
            "proofreader_clarification_markers_changed": False,
            "deidentified_decision_note_taught": True,
            "decision_note_identifier_safe_repair": False,
            "semantic_role_constraint_gate": True,
            "deterministic_operator_sequence_required": False,
            "required_goal_typed_feedback": True,
            "maximum_output_tokens": MAX_OUTPUT_TOKENS,
            "no_show_to_dna_alias_added": False,
            "output_schema_changed": False,
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
    "RECOGNIZED_CONSTRAINT_CODE",
    "RECOGNIZED_CONSTRAINT_PATH_CODE",
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
