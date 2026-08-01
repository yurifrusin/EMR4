#!/usr/bin/env python3
"""Grounded-binding semantic repair of the receptionist-first packet."""

from __future__ import annotations

import copy
from datetime import datetime
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_proofreader_dialogue_v4 as dialogue
from scripts import reception_one_receptionist_first_v6 as v6
from scripts import reception_one_shared_typed_plan_language as shared
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v61"
)
MODEL_FORM_BODY_SCHEMA_PATH = v6.MODEL_FORM_BODY_SCHEMA_PATH
CORRECTION_TICKET_SCHEMA_PATH = v6.CORRECTION_TICKET_SCHEMA_PATH
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
DIALOGUE_PROTOCOL = "reception.one.bureau.receptionist-first.v6.1"
PROTOCOL_VERSION = "reception.one.bureau.receptionist-first-cell.v6.1"
CONTRACT_MODE = "receptionist-v61"
POLICY_ID = "reception-one-receptionist-first-v61-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = "reception.one.bureau.receptionist-and-form.v6.1"
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v61.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v61.parent_audit_event.v1"
)
PARENT_RESULT_PASS = "reception_one_receptionist_first_v61_occupied_pass"
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v61_occupied_no_release"
)
MAX_PROVIDER_CALLS = 2
MAX_CORRECTION_TURNS = 1
TEMPERATURE = v6.TEMPERATURE
THINKING_BUDGET = v6.THINKING_BUDGET
MAX_OUTPUT_TOKENS = v6.MAX_OUTPUT_TOKENS
INCLUDE_THOUGHTS = v6.INCLUDE_THOUGHTS
PREPRINTED_FIELDS = v6.PREPRINTED_FIELDS
MODEL_AUTHORED_FIELDS = v6.MODEL_AUTHORED_FIELDS
TYPED_FORM_FIELDS = v6.TYPED_FORM_FIELDS
BASELINE_METADATA = {
    **v6.BASELINE_METADATA,
    "targeted_grounded_binding_repair": True,
}
RECOGNISED_INTENT_CODE = "recognized_intent_goal_mismatch"
CORRECTION_ELIGIBLE_CODES = (
    v6.CORRECTION_ELIGIBLE_CODES | {RECOGNISED_INTENT_CODE}
)

SYSTEM_INSTRUCTION = (
    v6.SYSTEM_INSTRUCTION
    + """

The binding_table is a tray of broker-grounded, request-local stamped facts,
not a list of guesses. A row appears only when its meaning has already been
grounded outside the model. Use those rows exactly. In particular, when
binding:selected_appointment is present, it is the specific appointment
selected for this request. Do not ask which appointment is meant merely
because the utterance does not repeat its date or practitioner.

Treat an explicit action as decisive when its required grounded bindings are
present: reschedule/move/shift/change-time means move; longer/shorter/extend/
resize with a duration means resize; cancel/call-off/take-out/remove means
cancel; and set/mark with a supplied status means status_change. Do not replace
these actions with clarification simply to re-request a stamped binding.
Conversely, names, practitioner, date, time and duration by themselves do not
request creation: without an action verb, use clarification."""
)

ReceptionistFirstError = v6.ReceptionistFirstError
canonical_json = v6.canonical_json
canonical_hash = v6.canonical_hash
validate_exact = v6.validate_exact
assemble_program = v6.assemble_program
model_form_body = v6.model_form_body
vertex_response_schema = v6.vertex_response_schema
review_receptionist_output = v6.review_receptionist_output


def _validate_ticket(ticket: dict[str, Any]) -> None:
    validate_exact(ticket, CORRECTION_TICKET_SCHEMA_PATH)
    if (
        ticket["target_turn_code"] != 2
        or ticket["attempts_remaining"] != 1
        or not ticket["replacement_required"]
    ):
        raise ReceptionistFirstError("correction_ticket_budget_invalid")


def build_turn_input(
    frame: dict[str, Any],
    *,
    correction_ticket: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task = structured.build_model_input(frame)
    turn_code = 2 if correction_ticket is not None else 1
    if correction_ticket is not None:
        _validate_ticket(correction_ticket)
    value = {
        "contract_version": DIALOGUE_PROTOCOL,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "turn_code": turn_code,
        "task_sha256": canonical_hash(task),
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
    expected = structured.build_model_input(frame)
    if value["task"] != expected:
        raise ReceptionistFirstError("turn_task_frame_mismatch")
    if value["task_sha256"] != canonical_hash(expected):
        raise ReceptionistFirstError("turn_task_hash_mismatch")
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
        _validate_ticket(ticket)


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


def parse_vertex_output(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, int]]:
    return v6.parse_vertex_output(packet)


def parse_vertex_program(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    program, _, usage = parse_vertex_output(packet)
    return program, usage


def _provider_packet(body: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidates": [
            {"content": {"parts": [{"text": canonical_json(body)}]}}
        ],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 40,
            "thoughtsTokenCount": 20,
            "totalTokenCount": 160,
        },
    }


def _noun_only_no_action(frame: dict[str, Any]) -> bool:
    text = " ".join(frame.get("utterances") or []).casefold()
    action = re.compile(
        r"\b(?:arrange|book|schedule|create|move|reschedul|shift|"
        r"change|make|extend|shorten|resize|cancel|remove|call off|"
        r"take out|set|mark|squeeze|fit in|sort out)\b"
    )
    if action.search(text) is not None:
        return False
    grounded_leads: list[str] = []
    for collection in ("patients", "practitioners"):
        for row in frame.get("context", {}).get(collection, []):
            grounded_leads.extend(
                str(value).casefold()
                for value in (row.get("display"), *(row.get("aliases") or []))
                if isinstance(value, str)
            )
    stripped = text.lstrip()
    return any(
        stripped == lead
        or stripped.startswith(lead + " ")
        or stripped.startswith(lead + "'")
        for lead in grounded_leads
    )


def evaluate_output(
    frame: dict[str, Any],
    program: dict[str, Any],
    body: dict[str, Any],
    *,
    turn_code: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    result = v6.evaluate_output(
        frame,
        program,
        body,
        turn_code=turn_code,
        now=now,
    )
    if result["disposition"] != "admit":
        return result
    recognised = typed_plan.deterministic_plan(frame)["goal"]
    actual = shared.GOALS[program["goal_code"]]
    mismatch = (
        recognised != "clarification" and actual != recognised
    ) or (
        recognised == "clarification"
        and _noun_only_no_action(frame)
        and actual != "clarification"
    )
    if not mismatch:
        result["recognized_intent_assertion"] = {
            "disposition": "admit",
            "recognized_goal": recognised,
            "model_goal": actual,
            "unknown_novel_composition_closed": False,
        }
        return result
    violation = {
        "path": "$.typed_form.goal_code",
        "code": RECOGNISED_INTENT_CODE,
    }
    result.update(
        {
            "disposition": (
                "revision_required" if turn_code == 1 else "edge_abort"
            ),
            "correction_eligible": turn_code == 1,
            "correction_turns_remaining": 1 if turn_code == 1 else 0,
            "terminal": turn_code != 1,
            "violations": [violation],
            "safe_repairs": [],
            "admitted_operator_ids": [],
            "candidate": None,
            "normalized_plan": None,
            "semantic_review": None,
            "recognized_intent_assertion": {
                "disposition": "revision_required",
                "recognized_goal": recognised,
                "model_goal": actual,
                "unknown_novel_composition_closed": False,
            },
        }
    )
    return result


def evaluate_program(
    frame: dict[str, Any],
    program: dict[str, Any],
    *,
    turn_code: int,
) -> dict[str, Any]:
    return v6.evaluate_program(frame, program, turn_code=turn_code)


def build_correction_ticket(
    body: dict[str, Any],
    program: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    if (
        evaluation.get("turn_code") != 1
        or evaluation.get("disposition") != "revision_required"
        or evaluation.get("correction_eligible") is not True
    ):
        raise ReceptionistFirstError("correction_ticket_not_authorised")
    findings: list[dict[str, Any]] = []
    for violation in evaluation["violations"][:20]:
        code = violation["code"]
        if code not in CORRECTION_ELIGIBLE_CODES:
            raise ReceptionistFirstError(
                "correction_ticket_violation_not_allowlisted"
            )
        if violation["path"] == "$.typed_form.goal_code":
            field_code, step_index, source_index = "goal_code", -1, -1
        else:
            field_code, step_index, source_index = v6._ticket_coordinates(
                violation["path"],
                program,
            )
        findings.append(
            {
                "violation_code": code,
                "field_code": field_code,
                "step_index": step_index,
                "source_index": source_index,
                "allowed_output_names": (
                    dialogue._allowed_output_names(
                        program,
                        step_index=step_index,
                        source_index=source_index,
                    )
                    if field_code == "source_ref"
                    else []
                ),
            }
        )
    ticket = {
        "version_code": 2,
        "target_turn_code": 2,
        "previous_output_sha256": canonical_hash(body),
        "previous_typed_form": {
            "goal_code": copy.deepcopy(program["goal_code"]),
            "steps": copy.deepcopy(program["steps"]),
        },
        "replacement_required": True,
        "attempts_remaining": 1,
        "violations": findings,
    }
    _validate_ticket(ticket)
    serialized = canonical_json(ticket)
    for rejected in (
        body["receptionist_response"],
        body["decision_note"],
        body["typed_form"]["operator_note"],
    ):
        if rejected in serialized:
            raise ReceptionistFirstError("rejected_text_retained")
    return ticket


def build_provider_blocked_evidence() -> dict[str, Any]:
    frame, correct_program = dialogue._known_move()
    correct_body = model_form_body(correct_program, frame=frame)
    assembled, parsed_body, usage = parse_vertex_output(
        _provider_packet(correct_body)
    )
    admitted = evaluate_output(
        frame,
        assembled,
        parsed_body,
        turn_code=1,
    )
    wrong_program = copy.deepcopy(correct_program)
    wrong_program["goal_code"] = shared.GOALS.index("clarification")
    wrong_program["steps"] = [
        {
            "operator_code": 13,
            "source_refs": [],
        }
    ]
    wrong_body = model_form_body(wrong_program, frame=frame)
    wrong_evaluation = evaluate_output(
        frame,
        assemble_program(wrong_body),
        wrong_body,
        turn_code=1,
    )
    ticket = build_correction_ticket(
        wrong_body,
        assemble_program(wrong_body),
        wrong_evaluation,
    )
    if (
        admitted["disposition"] != "admit"
        or wrong_evaluation["disposition"] != "revision_required"
        or wrong_evaluation["violations"]
        != [
            {
                "path": "$.typed_form.goal_code",
                "code": RECOGNISED_INTENT_CODE,
            }
        ]
    ):
        raise ReceptionistFirstError(
            "provider_blocked_v61_semantic_assertion_not_proven"
        )
    return {
        "schema_version": (
            "reception.one.receptionist_first_v61.provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v61_provider_blocked_pass"
        ),
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "system_instruction_sha256": canonical_hash(
            {"text": SYSTEM_INSTRUCTION}
        ),
        "response_schema_sha256": canonical_hash(vertex_response_schema()),
        "thinking": {
            "budget": THINKING_BUDGET,
            "include_thoughts": INCLUDE_THOUGHTS,
            "thought_token_count_fixture": usage["thoughtsTokenCount"],
            "hidden_reasoning_retained": False,
        },
        "form_boundary": {
            "natural_response_separate": True,
            "typed_form_separate": True,
            "natural_response_parsed_into_form": False,
            "correct_form_admitted": True,
            "recognized_wrong_goal_rejected": True,
            "correction_ticket_issued": True,
            "ticket_sha256": canonical_hash(ticket),
            "proofreader_selected_replacement": False,
            "unknown_novel_composition_closed": False,
        },
        "boundary": {
            "raw_prompt_retained": False,
            "raw_provider_response_retained": False,
            "credentials_or_tokens_retained": False,
            "api_key_information_retained": False,
            "product_or_database_access": False,
            "appointment_write": False,
            "product_delivery": False,
            "provider_tools": False,
            "fallback": False,
        },
    }


__all__ = [
    "ARTIFACT_DIR",
    "BASELINE_METADATA",
    "CONTRACT_MODE",
    "CORRECTION_ELIGIBLE_CODES",
    "CORRECTION_TICKET_SCHEMA_PATH",
    "DIALOGUE_PROTOCOL",
    "INCLUDE_THOUGHTS",
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
    "assemble_program",
    "build_correction_ticket",
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
