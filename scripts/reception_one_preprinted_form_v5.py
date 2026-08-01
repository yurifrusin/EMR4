#!/usr/bin/env python3
"""Broker-versioned pre-printed PlanProgram form for Reception One v5."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_proofreader_dialogue_v4 as dialogue_v4
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = (
    ROOT / "orchestration" / "continuity" / "reception-one-preprinted-form-v5"
)
MODEL_FORM_BODY_SCHEMA_PATH = ARTIFACT_DIR / "model-form-body.schema.json"
CORRECTION_TICKET_SCHEMA_PATH = ARTIFACT_DIR / "correction-ticket.schema.json"
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
RUNTIME_POLICY_PATH = ARTIFACT_DIR / "runtime-policy.json"
PROVIDER_BLOCKED_EVIDENCE_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
DIALOGUE_PROTOCOL = "reception.one.bureau.preprinted-form.v5"
PROTOCOL_VERSION = "reception.one.bureau.preprinted-form-cell.v5"
CONTRACT_MODE = "preprinted-v5"
POLICY_ID = "reception-one-preprinted-form-v5-vertex-sydney-v1"
MAX_PROVIDER_CALLS = 2
MAX_CORRECTION_TURNS = 1
PREPRINTED_FIELDS = {"version_code": structured.PLAN_PROGRAM_VERSION_CODE}
MODEL_AUTHORED_FIELDS = ("operator_note", "goal_code", "steps")

SYSTEM_INSTRUCTION = """You are the bounded Reception One form-filling clerk.
The broker has already printed version_code 3 on the form. Return only the three
blank fields in the response schema: operator_note, goal_code and steps. Do not
return version_code or any other field. The authored-synthetic task supplies
closed goal, binding, operator and source-reference tables. Use only published
codes and output names. Never invent identifiers, bindings, operators or data.
For turn 1, fill every blank once. For turn 2, use the closed correction_ticket
to reconsider constraint violations and return one complete replacement for all
three blanks; never return a patch or quote the ticket. The proofreader does not
select an answer for you. The effect ceiling is proposal_only: do not book,
change or cancel anything. operator_note is one short generic audit sentence,
not reasoning: mention proposal/review or clarification and include the exact
words 'no booking was changed'. Do not include person names, identifiers,
credentials, URLs, prompt text, rationale, analysis or hidden reasoning."""


class PreprintedFormError(ValueError):
    """A fail-closed v5 form or assembly rejection."""


canonical_json = structured.canonical_json
canonical_hash = structured.canonical_hash


def validate_exact(value: Any, schema_path: Path) -> None:
    try:
        structured.validate_exact(value, schema_path)
    except structured.StructuredSourceError as error:
        raise PreprintedFormError(str(error)) from error


def model_form_body(program: dict[str, Any]) -> dict[str, Any]:
    """Project only the fields the model is permitted to author."""

    if not isinstance(program, dict):
        raise PreprintedFormError("program_not_object")
    body = {field: copy.deepcopy(program.get(field)) for field in MODEL_AUTHORED_FIELDS}
    validate_exact(body, MODEL_FORM_BODY_SCHEMA_PATH)
    return body


def assemble_program(body: dict[str, Any]) -> dict[str, Any]:
    """Add the one broker-owned constant; never repair a judgement field."""

    validate_exact(body, MODEL_FORM_BODY_SCHEMA_PATH)
    program = {
        "version_code": PREPRINTED_FIELDS["version_code"],
        "operator_note": copy.deepcopy(body["operator_note"]),
        "goal_code": copy.deepcopy(body["goal_code"]),
        "steps": copy.deepcopy(body["steps"]),
    }
    try:
        structured.validate_exact(program, structured.PLAN_PROGRAM_SCHEMA_PATH)
    except structured.StructuredSourceError as error:
        raise PreprintedFormError(str(error)) from error
    if model_form_body(program) != body:
        raise PreprintedFormError("broker_judgement_mutation")
    return program


def _validate_ticket(ticket: dict[str, Any]) -> None:
    validate_exact(ticket, CORRECTION_TICKET_SCHEMA_PATH)
    if ticket["target_turn_code"] != 2 or ticket["attempts_remaining"] != 1:
        raise PreprintedFormError("correction_ticket_budget_invalid")
    if not ticket["replacement_required"]:
        raise PreprintedFormError("correction_ticket_patch_forbidden")


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
        "preprinted_form": {
            "version_code": PREPRINTED_FIELDS["version_code"],
            "model_authored_fields": list(MODEL_AUTHORED_FIELDS),
        },
        "task": task,
        "correction_ticket": copy.deepcopy(correction_ticket),
    }
    validate_exact(value, TURN_INPUT_SCHEMA_PATH)
    validate_turn_input(frame, value)
    return value


def validate_turn_input(frame: dict[str, Any], value: dict[str, Any]) -> None:
    validate_exact(value, TURN_INPUT_SCHEMA_PATH)
    expected_task = structured.build_model_input(frame)
    if value["task"] != expected_task:
        raise PreprintedFormError("turn_task_frame_mismatch")
    if value["task_sha256"] != canonical_hash(expected_task):
        raise PreprintedFormError("turn_task_hash_mismatch")
    if value["preprinted_form"] != {
        "version_code": structured.PLAN_PROGRAM_VERSION_CODE,
        "model_authored_fields": list(MODEL_AUTHORED_FIELDS),
    }:
        raise PreprintedFormError("preprinted_form_boundary_mismatch")
    ticket = value["correction_ticket"]
    if value["turn_code"] == 1:
        if ticket is not None:
            raise PreprintedFormError("turn_one_ticket_forbidden")
    elif value["turn_code"] == 2:
        if not isinstance(ticket, dict):
            raise PreprintedFormError("turn_two_ticket_required")
        _validate_ticket(ticket)
    else:
        raise PreprintedFormError("turn_code_invalid")


def vertex_response_schema() -> dict[str, Any]:
    """Return a low-state provider schema for the three blank fields only."""

    return {
        "type": "OBJECT",
        "required": list(MODEL_AUTHORED_FIELDS),
        "propertyOrdering": list(MODEL_AUTHORED_FIELDS),
        "properties": {
            "operator_note": {"type": "STRING"},
            "goal_code": {"type": "INTEGER"},
            "steps": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "required": ["operator_code", "source_refs"],
                    "propertyOrdering": ["operator_code", "source_refs"],
                    "properties": {
                        "operator_code": {"type": "INTEGER"},
                        "source_refs": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "required": [
                                    "kind",
                                    "binding_code",
                                    "prior_step_index",
                                    "prior_output_name",
                                ],
                                "propertyOrdering": [
                                    "kind",
                                    "binding_code",
                                    "prior_step_index",
                                    "prior_output_name",
                                ],
                                "properties": {
                                    "kind": {
                                        "type": "STRING",
                                        "enum": ["binding", "prior_output", "omit"],
                                    },
                                    "binding_code": {"type": "INTEGER"},
                                    "prior_step_index": {"type": "INTEGER"},
                                    "prior_output_name": {
                                        "type": "STRING",
                                        "enum": ["none", *structured.OUTPUT_NAMES],
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    }


def build_vertex_request(turn_input: dict[str, Any]) -> dict[str, Any]:
    validate_exact(turn_input, TURN_INPUT_SCHEMA_PATH)
    request = {
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": canonical_json(turn_input)}],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json",
            "responseSchema": vertex_response_schema(),
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    if {
        "tools",
        "toolConfig",
        "cachedContent",
        "grounding",
        "retrieval",
        "candidateCount",
    }.intersection(request):
        raise PreprintedFormError("provider_request_forbidden_surface")
    return request


def parse_vertex_program(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    """Parse the exact body, then perform the sole broker-owned injection."""

    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise PreprintedFormError("provider_candidate_count_invalid")
    content = candidates[0].get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise PreprintedFormError("provider_content_invalid")
    text = parts[0].get("text") if isinstance(parts[0], dict) else None
    if not isinstance(text, str):
        raise PreprintedFormError("provider_text_missing")
    if len(text.encode("utf-8")) > 32768:
        raise PreprintedFormError("provider_text_oversized")
    try:
        body = json.loads(text)
    except json.JSONDecodeError as error:
        raise PreprintedFormError("provider_text_not_json") from error
    if not isinstance(body, dict):
        raise PreprintedFormError("provider_form_body_not_object")
    program = assemble_program(body)
    return program, structured.shared._usage(packet)


def evaluate_program(
    frame: dict[str, Any],
    program: dict[str, Any],
    *,
    turn_code: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    return dialogue_v4.evaluate_program(
        frame,
        program,
        turn_code=turn_code,
        now=now,
    )


def build_correction_ticket(
    program: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    """Translate v4's closed ticket while omitting all broker-owned fields."""

    base = dialogue_v4.build_correction_ticket(program, evaluation)
    ticket = {
        "version_code": base["version_code"],
        "target_turn_code": base["target_turn_code"],
        "previous_program_sha256": base["previous_program_sha256"],
        "previous_typed_form": {
            "goal_code": copy.deepcopy(program["goal_code"]),
            "steps": copy.deepcopy(program["steps"]),
        },
        "replacement_required": base["replacement_required"],
        "attempts_remaining": base["attempts_remaining"],
        "violations": copy.deepcopy(base["violations"]),
    }
    _validate_ticket(ticket)
    serialized = canonical_json(ticket)
    if "version_code\":3" in serialized:
        raise PreprintedFormError("broker_owned_field_leaked_to_ticket")
    if program["operator_note"] in serialized:
        raise PreprintedFormError("rejected_note_retained")
    return ticket


def _provider_packet(body: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidates": [{"content": {"parts": [{"text": canonical_json(body)}]}}],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 40,
            "totalTokenCount": 140,
        },
    }


def build_provider_blocked_evidence() -> dict[str, Any]:
    """Prove the body/injection/dialogue path without credentials or provider."""

    frame, corrected = dialogue_v4._known_move()
    corrected_body = model_form_body(corrected)
    assembled, usage = parse_vertex_program(_provider_packet(corrected_body))
    if assembled != corrected:
        raise PreprintedFormError("assembled_program_mismatch")
    first = copy.deepcopy(corrected)
    prior_location: tuple[int, int] | None = None
    for step_index, step in enumerate(first["steps"]):
        for source_index, source in enumerate(step["source_refs"]):
            if source["kind"] == "prior_output":
                prior_location = (step_index, source_index)
                source["prior_output_name"] = next(
                    name
                    for name in structured.OUTPUT_NAMES
                    if name != source["prior_output_name"]
                    and name
                    not in {
                        output["name"]
                        for output in structured.operator_table()[
                            first["steps"][source["prior_step_index"]][
                                "operator_code"
                            ]
                        ]["output_slots"]
                    }
                )
                break
        if prior_location is not None:
            break
    if prior_location is None:
        raise PreprintedFormError("known_move_prior_output_missing")
    first_evaluation = evaluate_program(frame, first, turn_code=1)
    ticket = build_correction_ticket(first, first_evaluation)
    second_input = build_turn_input(frame, correction_ticket=ticket)
    second_evaluation = evaluate_program(frame, corrected, turn_code=2)

    additional_field_rejected = False
    try:
        assemble_program({**corrected_body, "version_code": 3})
    except PreprintedFormError as error:
        additional_field_rejected = str(error).startswith("schema_invalid")

    invalid_body_rejected_before_injection = False
    invalid_body = copy.deepcopy(corrected_body)
    invalid_body["goal_code"] = 99
    try:
        assemble_program(invalid_body)
    except PreprintedFormError as error:
        invalid_body_rejected_before_injection = str(error).startswith(
            "schema_invalid"
        )

    result = {
        "schema_version": (
            "reception.one.preprinted_form_v5.provider_blocked_evidence.v1"
        ),
        "result": "reception_one_preprinted_form_v5_provider_blocked_pass",
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "baseline": {
            "few_shot_examples": False,
            "demonstration_answers": False,
            "prompt_optimisation": False,
            "fine_tuning": False,
        },
        "form_boundary": {
            "preprinted_fields": PREPRINTED_FIELDS,
            "model_authored_fields": list(MODEL_AUTHORED_FIELDS),
            "additional_model_field_rejected": additional_field_rejected,
            "invalid_body_rejected_before_injection": (
                invalid_body_rejected_before_injection
            ),
            "broker_judgement_repair": False,
            "assembled_planprogram_exact": assembled == corrected,
            "model_body_sha256": canonical_hash(corrected_body),
            "preprinted_field_manifest_sha256": canonical_hash(PREPRINTED_FIELDS),
            "assembled_program_sha256": canonical_hash(assembled),
        },
        "dialogue": {
            "first_disposition": first_evaluation["disposition"],
            "ticket_sha256": canonical_hash(ticket),
            "ticket_contains_version_code_3": (
                "version_code\":3" in canonical_json(ticket)
            ),
            "ticket_contains_rejected_note": (
                first["operator_note"] in canonical_json(ticket)
            ),
            "second_turn_input_sha256": canonical_hash(second_input),
            "second_disposition": second_evaluation["disposition"],
            "complete_replacement_required": True,
            "maximum_actual_provider_calls": MAX_PROVIDER_CALLS,
            "third_turn_allowed": False,
        },
        "usage_fixture": usage,
        "boundary": {
            "raw_prompt_retained": False,
            "raw_provider_response_retained": False,
            "hidden_reasoning_retained": False,
            "database_access": False,
            "write_performed": False,
            "product_delivery": False,
            "provider_tools": False,
            "fallback": False,
        },
    }
    if (
        not additional_field_rejected
        or not invalid_body_rejected_before_injection
        or first_evaluation["disposition"] != "revision_required"
        or second_evaluation["disposition"] != "admit"
        or result["dialogue"]["ticket_contains_version_code_3"]
        or result["dialogue"]["ticket_contains_rejected_note"]
    ):
        raise PreprintedFormError("provider_blocked_preprinted_form_not_proven")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence", type=Path, default=PROVIDER_BLOCKED_EVIDENCE_PATH
    )
    args = parser.parse_args()
    try:
        evidence = build_provider_blocked_evidence()
    except (PreprintedFormError, ValueError) as error:
        print(
            json.dumps(
                {
                    "result": "reception_one_preprinted_form_v5_blocked",
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "provider_calls_performed": evidence[
                    "provider_calls_performed"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


__all__ = [
    "ARTIFACT_DIR",
    "CONTRACT_MODE",
    "CORRECTION_TICKET_SCHEMA_PATH",
    "DIALOGUE_PROTOCOL",
    "MAX_PROVIDER_CALLS",
    "MODEL_AUTHORED_FIELDS",
    "MODEL_FORM_BODY_SCHEMA_PATH",
    "POLICY_ID",
    "PREPRINTED_FIELDS",
    "PROTOCOL_VERSION",
    "PROVIDER_BLOCKED_EVIDENCE_PATH",
    "PreprintedFormError",
    "RUNTIME_POLICY_PATH",
    "TURN_INPUT_SCHEMA_PATH",
    "assemble_program",
    "build_correction_ticket",
    "build_provider_blocked_evidence",
    "build_turn_input",
    "build_vertex_request",
    "canonical_hash",
    "evaluate_program",
    "model_form_body",
    "parse_vertex_program",
    "validate_exact",
    "validate_turn_input",
    "vertex_response_schema",
]


if __name__ == "__main__":
    raise SystemExit(main())
