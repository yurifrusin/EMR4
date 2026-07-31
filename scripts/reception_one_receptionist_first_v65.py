#!/usr/bin/env python3
"""Semantic-role and typed-feedback descendant of receptionist-first v6.4."""

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
from scripts import reception_one_receptionist_first_v64 as v64
from scripts import reception_one_shared_typed_plan_language as shared


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v65"
)
DESK_CONTEXT_SCHEMA_PATH = v64.DESK_CONTEXT_SCHEMA_PATH
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
MODEL_FORM_BODY_SCHEMA_PATH = v64.MODEL_FORM_BODY_SCHEMA_PATH
CORRECTION_TICKET_SCHEMA_PATH = v64.CORRECTION_TICKET_SCHEMA_PATH
DIALOGUE_PROTOCOL = "reception.one.bureau.receptionist-first.v6.5"
PROTOCOL_VERSION = "reception.one.bureau.receptionist-first-cell.v6.5"
CONTRACT_MODE = "receptionist-v65"
POLICY_ID = "reception-one-receptionist-first-v65-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = "reception.one.bureau.receptionist-and-form.v6.5"
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v65.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v65.parent_audit_event.v1"
)
PARENT_RESULT_PASS = "reception_one_receptionist_first_v65_occupied_pass"
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v65_occupied_no_release"
)
MAX_PROVIDER_CALLS = v64.MAX_PROVIDER_CALLS
MAX_CORRECTION_TURNS = v64.MAX_CORRECTION_TURNS
TEMPERATURE = v64.TEMPERATURE
THINKING_BUDGET = v64.THINKING_BUDGET
MAX_OUTPUT_TOKENS = v64.MAX_OUTPUT_TOKENS
INCLUDE_THOUGHTS = v64.INCLUDE_THOUGHTS
PREPRINTED_FIELDS = v64.PREPRINTED_FIELDS
MODEL_AUTHORED_FIELDS = v64.MODEL_AUTHORED_FIELDS
TYPED_FORM_FIELDS = v64.TYPED_FORM_FIELDS
RECOGNIZED_CONSTRAINT_CODE = v64.RECOGNIZED_CONSTRAINT_CODE
RECOGNIZED_CONSTRAINT_PATH_CODE = v64.RECOGNIZED_CONSTRAINT_PATH_CODE
CORRECTION_ELIGIBLE_CODES = v64.CORRECTION_ELIGIBLE_CODES
BASELINE_METADATA = {
    **v64.BASELINE_METADATA,
    "semantic_role_constraint_gate": True,
    "deterministic_operator_sequence_required": False,
    "required_goal_typed_feedback": True,
    "clarification_desk_form_taught": True,
}

SYSTEM_INSTRUCTION = (
    v64.SYSTEM_INSTRUCTION
    + """

The proofreader checks recognized facts by their typed argument roles, not by
requiring one fixed operator sequence. You may use a shorter coherent form,
but every named argument/source/field constraint must appear somewhere in a
compatible typed input. For example, selected_appointment may feed the
appointment argument of the final resize or cancel proposal directly.

A correction ticket may place exactly one goal name in allowed_output_names
for a goal_code or receptionist_response finding. That name is the required
goal for the complete replacement answer. Make the typed form, decision note
and receptionist response all use it.

Clarification is a normal receptionist task, not a failed form. A line that
only supplies appointment details without asking to book, move, resize,
cancel, change status or assess a squeeze-in does not authorize you to infer a
booking goal: ask what the staff member wants done. Under this frozen desk
policy, ambiguous “fit in” wording must clarify whether staff mean an ordinary
new booking or a true squeeze-in review. For clarification, use goal_code 6
and the clarification operator, ask one focused question, briefly name the
ambiguity, and include the exact sentence “No booking was changed.” Do not say
that a proposal is being prepared."""
)

ReceptionistFirstError = v64.ReceptionistFirstError
canonical_json = v64.canonical_json
canonical_hash = v64.canonical_hash
validate_exact = v64.validate_exact
assemble_program = v64.assemble_program
model_form_body = v64.model_form_body
vertex_response_schema = v64.vertex_response_schema
review_receptionist_output = v64.review_receptionist_output
parse_vertex_output = v64.parse_vertex_output
parse_vertex_program = v64.parse_vertex_program
evaluate_program = v64.evaluate_program
build_desk_context = v64.build_desk_context
build_model_task = v64.build_model_task


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


def _recognized_constraint_manifest(
    frame: dict[str, Any],
) -> list[dict[str, Any]]:
    reference = typed_plan.deterministic_plan(frame)
    if reference["goal"] == "clarification":
        return []
    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for step in reference["steps"]:
        for argument, source in step["args"].items():
            if source.get("kind") not in {"semantic_ref", "context_ref"}:
                continue
            key = (argument, source["kind"], source["field"])
            unique[key] = {
                "argument": argument,
                "source_kind": source["kind"],
                "field": source["field"],
            }
    return [unique[key] for key in sorted(unique)]


def _repair_path(
    required: dict[str, Any],
    program: dict[str, Any],
    normalized_plan: dict[str, Any],
    operator_rows: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    for step_index, step in enumerate(normalized_plan["steps"]):
        row = operator_rows[step["operator"]]
        for slot in row["input_slots"]:
            if slot["name"] != required["argument"]:
                continue
            source_index = slot["position"]
            if (
                step_index < len(program["steps"])
                and source_index
                < len(program["steps"][step_index]["source_refs"])
            ):
                return (
                    f"$.steps[{step_index}].source_refs[{source_index}]",
                    RECOGNIZED_CONSTRAINT_CODE,
                )
    return "$.typed_form.goal_code", RECOGNIZED_CONSTRAINT_PATH_CODE


def _recognized_constraint_violations(
    frame: dict[str, Any],
    program: dict[str, Any],
    normalized_plan: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    manifest = _recognized_constraint_manifest(frame)
    operator_rows = {
        row["name"]: row for row in build_model_task(frame)["operator_table"]
    }
    actual = {
        (argument, source.get("kind"), source.get("field"))
        for step in normalized_plan["steps"]
        for argument, source in step["args"].items()
        if isinstance(source, dict)
        and source.get("kind") in {"semantic_ref", "context_ref"}
    }
    violations: list[dict[str, Any]] = []
    for required in manifest:
        key = (
            required["argument"],
            required["source_kind"],
            required["field"],
        )
        if key in actual:
            continue
        path, code = _repair_path(
            required,
            program,
            normalized_plan,
            operator_rows,
        )
        violations.append({"path": path, "code": code})
    unique = [
        dict(item)
        for item in {
            (value["path"], value["code"]): value
            for value in violations
        }.values()
    ]
    unique.sort(key=lambda value: (value["path"], value["code"]))
    return manifest, unique


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
    if result["disposition"] != "admit":
        return result
    manifest, violations = _recognized_constraint_violations(
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


def _required_goal(
    program: dict[str, Any],
    evaluation: dict[str, Any],
) -> str:
    assertion = evaluation.get("recognized_intent_assertion")
    if isinstance(assertion, dict):
        recognized = assertion.get("recognized_goal")
        if recognized in shared.GOALS:
            return str(recognized)
    return shared.GOALS[program["goal_code"]]


def build_correction_ticket(
    body: dict[str, Any],
    program: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    ticket = v64.build_correction_ticket(body, program, evaluation)
    required_goal = _required_goal(program, evaluation)
    goal_codes = {
        "recognized_intent_goal_mismatch",
        "receptionist_response_goal_mismatch",
    }
    for finding in ticket["violations"]:
        if finding["violation_code"] in goal_codes:
            finding["allowed_output_names"] = [required_goal]
    v61._validate_ticket(ticket)
    return ticket


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
            "provider_blocked_v65_constraint_assertion_not_proven"
        )
    return {
        "schema_version": (
            "reception.one.receptionist_first_v65.provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v65_provider_blocked_pass"
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
            "semantic_role_constraint_gate": True,
            "deterministic_operator_sequence_required": False,
            "required_goal_typed_feedback": True,
            "clarification_desk_form_taught": True,
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
