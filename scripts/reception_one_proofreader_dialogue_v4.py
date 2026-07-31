#!/usr/bin/env python3
"""Closed two-turn proofreader dialogue for Reception One PlanProgram v3."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as legacy_lane
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-proofreader-dialogue-v4"
)
CORRECTION_TICKET_SCHEMA_PATH = ARTIFACT_DIR / "correction-ticket.schema.json"
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
RUNTIME_POLICY_PATH = ARTIFACT_DIR / "runtime-policy.json"
PROVIDER_BLOCKED_EVIDENCE_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
DIALOGUE_PROTOCOL = "reception.one.bureau.proofreader-dialogue.v4"
PROTOCOL_VERSION = "reception.one.bureau.proofreader-dialogue-cell.v4"
CONTRACT_MODE = "dialogue-v4"
POLICY_ID = "reception-one-proofreader-dialogue-v4-vertex-sydney-v1"
MAX_PROVIDER_CALLS = 2
MAX_CORRECTION_TURNS = 1

CORRECTION_ELIGIBLE_CODES = frozenset(
    {
        "operator_arity_invalid",
        "binding_sentinel_invalid",
        "prior_output_sentinel_invalid",
        "omit_sentinel_invalid",
        "required_source_omitted",
        "forward_or_self_reference",
        "output_name_invalid",
        "source_type_mismatch",
        "external_binding_invalid",
        "source_kind_invalid",
        "signature_mismatch",
        "duplicate_step_id",
        "binding_type_mismatch",
        "ungrounded_binding",
        "semantic_action_mismatch",
        "clarification_required",
        "semantic_value_missing",
        "note_not_string",
        "note_empty",
        "note_oversized",
        "note_multiline",
        "note_non_ascii_or_control",
        "note_markup_or_code_surface",
        "note_network_or_email_identifier",
        "note_uuid",
        "note_internal_identifier",
        "note_secret_identity_or_hidden_reasoning",
        "note_person_name",
        "note_claims_command_effect",
        "note_missing_bounded_purpose",
        "note_missing_no_change_statement",
    }
)
NON_CORRECTION_CODES = frozenset(
    {
        "scope_mismatch",
        "stale_context",
        "data_class_not_admitted",
        "catalogue_mismatch",
        "step_budget_exceeded",
        "unknown_operator",
        "effect_escalation",
        "forbidden_operator",
        "authority_boundary_open",
        "revision_budget_exhausted",
        "schema_invalid",
    }
)
_STEP_PATTERN = re.compile(r"\$\.steps\[(?P<step>[0-9]+)\]")
_SOURCE_PATTERN = re.compile(
    r"\$\.steps\[(?P<step>[0-9]+)\]\.source_refs\[(?P<source>[0-9]+)\]"
)
SYSTEM_INSTRUCTION = """You are the bounded Reception One planning clerk.
Return one complete JSON object exactly matching the supplied PlanProgram-v3
response schema. The task contains the frozen authored-synthetic request and
closed goal, binding, operator and source-reference tables. Use only published
codes and output names. Never invent identifiers, bindings, operators or data.
For turn 1, fill the form once. For turn 2, a closed correction_ticket identifies
constraint violations in your previous complete form. Reconsider those
constraints and return a complete replacement PlanProgram; never return a patch
or quote the ticket. The proofreader does not select an answer for you.
The effect ceiling is proposal_only: do not book, change or cancel anything.
operator_note is one short generic audit sentence, not reasoning: mention
proposal/review or clarification and include the exact words
'no booking was changed'. Do not include person names, identifiers, credentials,
URLs, prompt text, rationale, analysis, hidden reasoning or claims of action."""


class DialogueError(ValueError):
    """A fail-closed proofreader-dialogue rejection."""


canonical_json = structured.canonical_json
canonical_hash = structured.canonical_hash
load_object = structured.load_object


def validate_exact(value: Any, schema_path: Path) -> None:
    try:
        structured.validate_exact(value, schema_path)
    except structured.StructuredSourceError as error:
        raise DialogueError(str(error)) from error


def _validate_ticket(ticket: dict[str, Any]) -> None:
    validate_exact(ticket, CORRECTION_TICKET_SCHEMA_PATH)
    if ticket["target_turn_code"] != 2 or ticket["attempts_remaining"] != 1:
        raise DialogueError("correction_ticket_budget_invalid")
    if not ticket["replacement_required"]:
        raise DialogueError("correction_ticket_patch_forbidden")


def build_turn_input(
    frame: dict[str, Any],
    *,
    correction_ticket: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one exact turn input; turn and ticket presence are inseparable."""

    task = structured.build_model_input(frame)
    turn_code = 2 if correction_ticket is not None else 1
    if correction_ticket is not None:
        _validate_ticket(correction_ticket)
    result = {
        "contract_version": DIALOGUE_PROTOCOL,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "turn_code": turn_code,
        "task_sha256": canonical_hash(task),
        "task": task,
        "correction_ticket": copy.deepcopy(correction_ticket),
    }
    validate_exact(result, TURN_INPUT_SCHEMA_PATH)
    validate_turn_input(frame, result)
    return result


def validate_turn_input(frame: dict[str, Any], value: dict[str, Any]) -> None:
    """Apply cross-field checks intentionally absent from JSON Schema."""

    validate_exact(value, TURN_INPUT_SCHEMA_PATH)
    expected_task = structured.build_model_input(frame)
    if value["task"] != expected_task:
        raise DialogueError("turn_task_frame_mismatch")
    if value["task_sha256"] != canonical_hash(expected_task):
        raise DialogueError("turn_task_hash_mismatch")
    ticket = value["correction_ticket"]
    if value["turn_code"] == 1:
        if ticket is not None:
            raise DialogueError("turn_one_ticket_forbidden")
    elif value["turn_code"] == 2:
        if not isinstance(ticket, dict):
            raise DialogueError("turn_two_ticket_required")
        _validate_ticket(ticket)
    else:
        raise DialogueError("turn_code_invalid")


def vertex_response_schema() -> dict[str, Any]:
    """Use a low-state provider subset of unchanged local PlanProgram v3.

    Vertex rejected the first occupied v4 request before a candidate because
    nested array and numeric/string bounds generated too many serving states.
    Those bounds remain exact in the local JSON Schema and proofreader. The
    provider schema retains the same object, fields, types, required fields,
    property ordering and closed string enums, but delegates all bounds to the
    decisive local gate.
    """

    schema = copy.deepcopy(structured.vertex_response_schema())
    state_bound_keywords = {
        "minimum",
        "maximum",
        "minLength",
        "maxLength",
        "minItems",
        "maxItems",
    }

    def remove_bounds(value: Any) -> None:
        if not isinstance(value, dict):
            return
        for keyword in state_bound_keywords:
            value.pop(keyword, None)
        properties = value.get("properties")
        if isinstance(properties, dict):
            for child in properties.values():
                remove_bounds(child)
        remove_bounds(value.get("items"))

    remove_bounds(schema)
    return schema


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
    forbidden = {
        "tools",
        "toolConfig",
        "cachedContent",
        "grounding",
        "retrieval",
        "candidateCount",
    }
    if forbidden.intersection(request):
        raise DialogueError("provider_request_forbidden_surface")
    return request


def parse_vertex_program(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    try:
        return structured.parse_vertex_program(packet)
    except structured.StructuredSourceError as error:
        raise DialogueError(str(error)) from error


def _review(
    *,
    frame: dict[str, Any],
    disposition: str,
    turn_code: int,
    violations: list[dict[str, str]],
    note_review: dict[str, Any],
    candidate: dict[str, Any] | None = None,
    normalized: dict[str, Any] | None = None,
    semantic_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    codes = {item["code"] for item in violations}
    correction_eligible = (
        turn_code == 1
        and bool(codes)
        and codes <= CORRECTION_ELIGIBLE_CODES
        and not bool(codes & NON_CORRECTION_CODES)
    )
    return {
        "schema_version": "reception.one.proofreader_dialogue_evaluation.v1",
        "turn_code": turn_code,
        "disposition": disposition,
        "correction_eligible": correction_eligible,
        "correction_turns_remaining": 1 if correction_eligible else 0,
        "terminal": disposition == "admit" or not correction_eligible,
        "violations": violations[:20],
        "safe_repairs": (
            semantic_review.get("safe_repairs", [])
            if semantic_review is not None
            else []
        ),
        "admitted_operator_ids": (
            semantic_review.get("admitted_operator_ids", [])
            if semantic_review is not None
            else []
        ),
        "reviewed_context_revision": frame.get("context_revision"),
        "operator_note": note_review,
        "candidate": candidate,
        "normalized_plan": normalized,
        "semantic_review": semantic_review,
    }


def evaluate_program(
    frame: dict[str, Any],
    program: dict[str, Any],
    *,
    turn_code: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Run note, exact form, compiler and semantic gates without repair."""

    if turn_code not in {1, 2}:
        raise DialogueError("turn_code_invalid")
    note_review = structured.review_operator_note(
        frame,
        program.get("operator_note") if isinstance(program, dict) else None,
    )
    try:
        structured.validate_exact(program, structured.PLAN_PROGRAM_SCHEMA_PATH)
    except structured.StructuredSourceError as error:
        # A response that cannot reduce to the exact form is never ticketed.
        return _review(
            frame=frame,
            disposition="edge_abort",
            turn_code=turn_code,
            violations=[
                {
                    "path": "$.program",
                    "code": str(error).split(":", 1)[0],
                }
            ],
            note_review=note_review,
        )
    if note_review["disposition"] != "admit":
        return _review(
            frame=frame,
            disposition="revision_required" if turn_code == 1 else "edge_abort",
            turn_code=turn_code,
            violations=[
                {"path": "$.operator_note", "code": code}
                for code in note_review["reason_codes"]
            ],
            note_review=note_review,
        )
    try:
        candidate = structured.compile_program(frame, program)
    except (
        structured.StructuredSourceError,
        legacy_lane.ModelLaneError,
        ValueError,
    ) as error:
        code, _, path = str(error).partition(":")
        code = {
            "forward_reference": "forward_or_self_reference",
            "source_handle_not_grounded": "ungrounded_binding",
        }.get(code, code)
        violations = [{"path": path or "$.steps", "code": code}]
        return _review(
            frame=frame,
            disposition="revision_required" if (
                turn_code == 1 and code in CORRECTION_ELIGIBLE_CODES
            ) else "edge_abort",
            turn_code=turn_code,
            violations=violations,
            note_review=note_review,
        )
    try:
        semantic_review, normalized, _ = legacy_lane.proofread_candidate(
            frame,
            candidate,
            attempt=turn_code,
            now=now,
        )
    except (legacy_lane.ModelLaneError, ValueError) as error:
        code = {
            "source_handle_not_grounded": "ungrounded_binding",
        }.get(str(error).split(":", 1)[0], str(error).split(":", 1)[0])
        return _review(
            frame=frame,
            disposition="revision_required" if (
                turn_code == 1 and code in CORRECTION_ELIGIBLE_CODES
            ) else "edge_abort",
            turn_code=turn_code,
            violations=[{"path": "$.steps", "code": code}],
            note_review=note_review,
            candidate=candidate,
        )
    disposition = semantic_review["disposition"]
    if disposition == "admit":
        dialogue_disposition = "admit"
    else:
        codes = {item["code"] for item in semantic_review["violations"]}
        dialogue_disposition = (
            "revision_required"
            if turn_code == 1
            and bool(codes)
            and codes <= CORRECTION_ELIGIBLE_CODES
            and not bool(codes & NON_CORRECTION_CODES)
            else "edge_abort"
        )
    return _review(
        frame=frame,
        disposition=dialogue_disposition,
        turn_code=turn_code,
        violations=[
            {
                "path": item["path"],
                "code": {
                    "forward_reference": "forward_or_self_reference",
                }.get(item["code"], item["code"]),
            }
            for item in semantic_review["violations"]
        ],
        note_review=note_review,
        candidate=candidate,
        normalized=normalized if dialogue_disposition == "admit" else None,
        semantic_review=semantic_review,
    )


def _coordinates(
    path: str,
    program: dict[str, Any],
) -> tuple[str, int, int]:
    source_match = _SOURCE_PATTERN.search(path)
    if source_match:
        return (
            "source_ref",
            int(source_match.group("step")),
            int(source_match.group("source")),
        )
    step_match = _STEP_PATTERN.search(path)
    if step_match:
        step_index = int(step_match.group("step"))
        if ".operator" in path:
            return "operator_code", step_index, -1
        if ".args." in path and 0 <= step_index < len(program["steps"]):
            operator_code = program["steps"][step_index]["operator_code"]
            operators = structured.operator_table()
            if 0 <= operator_code < len(operators):
                argument_name = path.rsplit(".", 1)[-1]
                for source_index, slot in enumerate(
                    operators[operator_code]["input_slots"]
                ):
                    if slot["name"] == argument_name:
                        return "source_ref", step_index, source_index
        return "steps", step_index, -1
    if path.startswith("$.operator_note"):
        return "operator_note", -1, -1
    if path.startswith("$.goal"):
        return "goal_code", -1, -1
    if path.startswith("$.steps"):
        return "steps", -1, -1
    return "program", -1, -1


def _allowed_output_names(
    program: dict[str, Any],
    *,
    step_index: int,
    source_index: int,
) -> list[str]:
    if not (
        0 <= step_index < len(program["steps"])
        and 0 <= source_index < len(program["steps"][step_index]["source_refs"])
    ):
        return []
    source = program["steps"][step_index]["source_refs"][source_index]
    if source["kind"] != "prior_output":
        return []
    prior_index = source["prior_step_index"]
    if prior_index < 0 or prior_index >= step_index:
        return []
    operators = structured.operator_table()
    prior_code = program["steps"][prior_index]["operator_code"]
    if prior_code < 0 or prior_code >= len(operators):
        return []
    exposed = {
        output["name"] for output in operators[prior_code]["output_slots"]
    }
    return [name for name in structured.OUTPUT_NAMES if name in exposed]


def build_correction_ticket(
    program: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    """Emit closed constraint feedback, never a replacement selection."""

    structured.validate_exact(program, structured.PLAN_PROGRAM_SCHEMA_PATH)
    if (
        evaluation.get("turn_code") != 1
        or evaluation.get("disposition") != "revision_required"
        or evaluation.get("correction_eligible") is not True
    ):
        raise DialogueError("correction_ticket_not_authorised")
    findings: list[dict[str, Any]] = []
    for violation in evaluation["violations"][:20]:
        code = violation["code"]
        if code not in CORRECTION_ELIGIBLE_CODES:
            raise DialogueError("correction_ticket_violation_not_allowlisted")
        field_code, step_index, source_index = _coordinates(
            violation["path"], program
        )
        findings.append(
            {
                "violation_code": code,
                "field_code": field_code,
                "step_index": step_index,
                "source_index": source_index,
                "allowed_output_names": _allowed_output_names(
                    program,
                    step_index=step_index,
                    source_index=source_index,
                ),
            }
        )
    ticket = {
        "version_code": 1,
        "target_turn_code": 2,
        "previous_program_sha256": canonical_hash(program),
        "previous_typed_form": structured.audit_typed_program(program),
        "replacement_required": True,
        "attempts_remaining": 1,
        "violations": findings,
    }
    _validate_ticket(ticket)
    if program["operator_note"] in canonical_json(ticket):
        raise DialogueError("rejected_note_retained")
    return ticket


def _known_move() -> tuple[dict[str, Any], dict[str, Any]]:
    document = typed_plan.load_json(typed_plan.CASES_PATH)
    case = next(item for item in document["cases"] if item["case_id"] == "known-move")
    frame = typed_plan.expand_case(document, case)
    plan = typed_plan.deterministic_plan(frame)
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=(
            "Prepared a move proposal for review; no booking was changed."
        ),
    )
    return frame, program


def build_provider_blocked_evidence() -> dict[str, Any]:
    """Exercise reject-ticket-replace-admit with zero provider contact."""

    frame, corrected = _known_move()
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
        raise DialogueError("known_move_prior_output_missing")
    first_evaluation = evaluate_program(frame, first, turn_code=1)
    ticket = build_correction_ticket(first, first_evaluation)
    second_input = build_turn_input(frame, correction_ticket=ticket)
    second_evaluation = evaluate_program(frame, corrected, turn_code=2)
    repeated_evaluation = evaluate_program(frame, first, turn_code=2)
    unsafe_frame = copy.deepcopy(frame)
    unsafe_frame["expires_at"] = "2026-07-20T00:00:00Z"
    unsafe_program = structured.program_from_plan(
        unsafe_frame,
        typed_plan.deterministic_plan(unsafe_frame),
        operator_note=(
            "Prepared a move proposal for review; no booking was changed."
        ),
    )
    unsafe_evaluation = evaluate_program(
        unsafe_frame, unsafe_program, turn_code=1
    )
    unsafe_ticket_denied = False
    try:
        build_correction_ticket(unsafe_program, unsafe_evaluation)
    except DialogueError as error:
        unsafe_ticket_denied = str(error) == "correction_ticket_not_authorised"
    note_program = copy.deepcopy(corrected)
    note_program["operator_note"] = "Margaret proposal."
    note_evaluation = evaluate_program(frame, note_program, turn_code=1)
    note_ticket = build_correction_ticket(note_program, note_evaluation)
    result = {
        "schema_version": (
            "reception.one.proofreader_dialogue_v4.provider_blocked_evidence.v1"
        ),
        "result": "reception_one_proofreader_dialogue_v4_provider_blocked_pass",
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "dialogue": {
            "protocol": DIALOGUE_PROTOCOL,
            "response_contract": structured.PLAN_PROGRAM_VERSION_CODE,
            "first_disposition": first_evaluation["disposition"],
            "first_violation_codes": [
                item["code"] for item in first_evaluation["violations"]
            ],
            "ticket_sha256": canonical_hash(ticket),
            "second_turn_input_sha256": canonical_hash(second_input),
            "second_disposition": second_evaluation["disposition"],
            "repeated_second_failure_terminal": (
                repeated_evaluation["disposition"] == "edge_abort"
                and repeated_evaluation["terminal"]
                and not repeated_evaluation["correction_eligible"]
            ),
            "unsafe_boundary_ticket_denied": unsafe_ticket_denied,
            "rejected_note_text_retained": (
                note_program["operator_note"] in canonical_json(note_ticket)
            ),
            "complete_replacement_required": True,
            "maximum_actual_provider_calls": MAX_PROVIDER_CALLS,
            "third_turn_allowed": False,
        },
        "hashes": {
            "task_sha256": second_input["task_sha256"],
            "first_program_sha256": canonical_hash(first),
            "corrected_program_sha256": canonical_hash(corrected),
            "corrected_candidate_sha256": canonical_hash(
                second_evaluation["candidate"]
            ),
            "corrected_plan_sha256": canonical_hash(
                second_evaluation["normalized_plan"]
            ),
        },
        "boundary": {
            "proofreader_selected_replacement": False,
            "semantic_safe_repair": False,
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
        first_evaluation["disposition"] != "revision_required"
        or second_evaluation["disposition"] != "admit"
        or not result["dialogue"]["repeated_second_failure_terminal"]
        or not unsafe_ticket_denied
        or result["dialogue"]["rejected_note_text_retained"]
    ):
        raise DialogueError("provider_blocked_dialogue_not_proven")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=PROVIDER_BLOCKED_EVIDENCE_PATH)
    args = parser.parse_args()
    try:
        evidence = build_provider_blocked_evidence()
    except (DialogueError, ValueError) as error:
        print(
            json.dumps(
                {
                    "result": "reception_one_proofreader_dialogue_v4_blocked",
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
    "CORRECTION_ELIGIBLE_CODES",
    "CORRECTION_TICKET_SCHEMA_PATH",
    "DIALOGUE_PROTOCOL",
    "DialogueError",
    "MAX_PROVIDER_CALLS",
    "POLICY_ID",
    "PROTOCOL_VERSION",
    "PROVIDER_BLOCKED_EVIDENCE_PATH",
    "RUNTIME_POLICY_PATH",
    "TURN_INPUT_SCHEMA_PATH",
    "build_correction_ticket",
    "build_provider_blocked_evidence",
    "build_turn_input",
    "build_vertex_request",
    "canonical_hash",
    "evaluate_program",
    "parse_vertex_program",
    "validate_exact",
    "validate_turn_input",
    "vertex_response_schema",
]


if __name__ == "__main__":
    raise SystemExit(main())
