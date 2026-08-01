#!/usr/bin/env python3
"""Exact-constraint proofreader descendant of receptionist-first v6.3."""

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
from scripts import reception_one_receptionist_first_v63 as v63


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v64"
)
DESK_CONTEXT_SCHEMA_PATH = v63.DESK_CONTEXT_SCHEMA_PATH
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
MODEL_FORM_BODY_SCHEMA_PATH = v63.MODEL_FORM_BODY_SCHEMA_PATH
CORRECTION_TICKET_SCHEMA_PATH = v63.CORRECTION_TICKET_SCHEMA_PATH
DIALOGUE_PROTOCOL = "reception.one.bureau.receptionist-first.v6.4"
PROTOCOL_VERSION = "reception.one.bureau.receptionist-first-cell.v6.4"
CONTRACT_MODE = "receptionist-v64"
POLICY_ID = "reception-one-receptionist-first-v64-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = "reception.one.bureau.receptionist-and-form.v6.4"
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v64.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v64.parent_audit_event.v1"
)
PARENT_RESULT_PASS = "reception_one_receptionist_first_v64_occupied_pass"
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v64_occupied_no_release"
)
MAX_PROVIDER_CALLS = 2
MAX_CORRECTION_TURNS = 1
TEMPERATURE = v63.TEMPERATURE
THINKING_BUDGET = v63.THINKING_BUDGET
MAX_OUTPUT_TOKENS = v63.MAX_OUTPUT_TOKENS
INCLUDE_THOUGHTS = v63.INCLUDE_THOUGHTS
PREPRINTED_FIELDS = v63.PREPRINTED_FIELDS
MODEL_AUTHORED_FIELDS = v63.MODEL_AUTHORED_FIELDS
TYPED_FORM_FIELDS = v63.TYPED_FORM_FIELDS
RECOGNIZED_CONSTRAINT_CODE = "recognized_constraint_omitted"
RECOGNIZED_CONSTRAINT_PATH_CODE = "recognized_constraint_path_missing"
CORRECTION_ELIGIBLE_CODES = v63.CORRECTION_ELIGIBLE_CODES | {
    RECOGNIZED_CONSTRAINT_CODE,
    RECOGNIZED_CONSTRAINT_PATH_CODE,
}
BASELINE_METADATA = {
    **v63.BASELINE_METADATA,
    "exact_recognized_constraint_gate": True,
    "natural_typed_same_goal_prompt": True,
}

SYSTEM_INSTRUCTION = (
    v63.SYSTEM_INSTRUCTION
    + """

The receptionist response, decision note and typed form are three bounded
parts of one piece of work. They must describe the same goal. If the typed form
prepares a move, the receptionist response must say that a move proposal is
being prepared; it must not ask an unrelated clarification. Apply this same
rule after a correction ticket and replace the whole prior answer.

Every exact request constraint printed in the binding table is part of the
form. Do not omit a recognized appointment date, earliest time, latest time,
duration, status or selected-appointment source. When staff correct a time,
use both the request-local earliest_time and latest_time bindings so the slot
search cannot broaden the corrected instant. A correction ticket reporting
recognized_constraint_omitted means the named source position must be restored
from the binding table; do not merely revise the prose."""
)

ReceptionistFirstError = v63.ReceptionistFirstError
canonical_json = v63.canonical_json
canonical_hash = v63.canonical_hash
validate_exact = v63.validate_exact
assemble_program = v63.assemble_program
model_form_body = v63.model_form_body
vertex_response_schema = v63.vertex_response_schema
review_receptionist_output = v63.review_receptionist_output
parse_vertex_output = v63.parse_vertex_output
parse_vertex_program = v63.parse_vertex_program
evaluate_program = v63.evaluate_program
build_desk_context = v63.build_desk_context
build_model_task = v63.build_model_task


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
    manifest: list[dict[str, Any]] = []
    occurrence_by_operator: dict[str, int] = {}
    for step in reference["steps"]:
        operator = step["operator"]
        occurrence = occurrence_by_operator.get(operator, 0)
        occurrence_by_operator[operator] = occurrence + 1
        for argument, source in step["args"].items():
            if source.get("kind") not in {"semantic_ref", "context_ref"}:
                continue
            manifest.append(
                {
                    "operator": operator,
                    "operator_occurrence": occurrence,
                    "argument": argument,
                    "source_kind": source["kind"],
                    "field": source["field"],
                }
            )
    return manifest


def _recognized_constraint_violations(
    frame: dict[str, Any],
    program: dict[str, Any],
    normalized_plan: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    manifest = _recognized_constraint_manifest(frame)
    task = build_model_task(frame)
    operator_rows = {row["name"]: row for row in task["operator_table"]}
    candidate_steps = normalized_plan["steps"]
    violations: list[dict[str, Any]] = []
    for required in manifest:
        matches = [
            (index, step)
            for index, step in enumerate(candidate_steps)
            if step["operator"] == required["operator"]
        ]
        occurrence = required["operator_occurrence"]
        if occurrence >= len(matches):
            violations.append(
                {
                    "path": "$.typed_form.goal_code",
                    "code": RECOGNIZED_CONSTRAINT_PATH_CODE,
                }
            )
            continue
        step_index, step = matches[occurrence]
        actual = step["args"].get(required["argument"])
        if (
            isinstance(actual, dict)
            and actual.get("kind") == required["source_kind"]
            and actual.get("field") == required["field"]
        ):
            continue
        row = operator_rows[required["operator"]]
        source_index = next(
            slot["position"]
            for slot in row["input_slots"]
            if slot["name"] == required["argument"]
        )
        if (
            step_index >= len(program["steps"])
            or source_index
            >= len(program["steps"][step_index]["source_refs"])
        ):
            path = "$.typed_form.goal_code"
            code = RECOGNIZED_CONSTRAINT_PATH_CODE
        else:
            path = (
                f"$.steps[{step_index}]."
                f"source_refs[{source_index}]"
            )
            code = RECOGNIZED_CONSTRAINT_CODE
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
            },
        }
    )
    return result


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
            field_code, step_index, source_index = v61.v6._ticket_coordinates(
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
                    v61.dialogue._allowed_output_names(
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
    v61._validate_ticket(ticket)
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
            "provider_blocked_v64_constraint_assertion_not_proven"
        )
    return {
        "schema_version": (
            "reception.one.receptionist_first_v64.provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v64_provider_blocked_pass"
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
            "exact_constraint_gate": True,
            "natural_typed_same_goal_prompt": True,
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
