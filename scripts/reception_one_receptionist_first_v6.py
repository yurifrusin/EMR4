#!/usr/bin/env python3
"""Receptionist-first natural response plus pre-printed typed form contract."""

from __future__ import annotations

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

from scripts import reception_one_preprinted_form_v5 as v5
from scripts import reception_one_proofreader_dialogue_v4 as dialogue
from scripts import reception_one_shared_typed_plan_language as shared
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v6"
)
MODEL_FORM_BODY_SCHEMA_PATH = ARTIFACT_DIR / "model-output.schema.json"
CORRECTION_TICKET_SCHEMA_PATH = ARTIFACT_DIR / "correction-ticket.schema.json"
TURN_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "turn-input.schema.json"
RUNTIME_POLICY_PATH = ARTIFACT_DIR / "runtime-policy.json"
PROVIDER_BLOCKED_EVIDENCE_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
DIALOGUE_PROTOCOL = "reception.one.bureau.receptionist-first.v6"
PROTOCOL_VERSION = "reception.one.bureau.receptionist-first-cell.v6"
CONTRACT_MODE = "receptionist-v6"
POLICY_ID = "reception-one-receptionist-first-v6-vertex-sydney-v1"
MODEL_RESPONSE_CONTRACT = "reception.one.bureau.receptionist-and-form.v6"
PARENT_EVIDENCE_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v6.parent_evidence.v1"
)
PARENT_AUDIT_EVENT_SCHEMA_VERSION = (
    "reception.one.receptionist_first_v6.parent_audit_event.v1"
)
PARENT_RESULT_PASS = "reception_one_receptionist_first_v6_occupied_pass"
PARENT_RESULT_NO_RELEASE = (
    "reception_one_receptionist_first_v6_occupied_no_release"
)
MAX_PROVIDER_CALLS = 2
MAX_CORRECTION_TURNS = 1
TEMPERATURE = 0
THINKING_BUDGET = 1024
MAX_OUTPUT_TOKENS = 2048
INCLUDE_THOUGHTS = False
PREPRINTED_FIELDS = {"version_code": structured.PLAN_PROGRAM_VERSION_CODE}
MODEL_AUTHORED_FIELDS = (
    "receptionist_response",
    "decision_note",
    "evidence_utterance_indices",
    "typed_form",
)
TYPED_FORM_FIELDS = ("operator_note", "goal_code", "steps")
BASELINE_METADATA = {
    "few_shot_examples": False,
    "demonstration_answers": False,
    "prompt_optimisation": True,
    "fine_tuning": False,
    "paired_development_not_holdout": True,
}

SYSTEM_INSTRUCTION = """You are a capable medical receptionist working at the
Reception One bureau. First understand the staff member's whole
authored-synthetic request as a receptionist would. Then do two distinct jobs:
(1) write the short natural response you would say at the reception desk, and
(2) complete the pre-printed typed bureau form in your toolkit.

The API response schema is the paper packet. Fill every blank exactly; do not
add fields or prose outside it. The broker has already printed version_code 3,
so it is absent from typed_form. receptionist_response is one or two concise,
helpful sentences. It may acknowledge what you understand, but it must say the
work is being prepared for review or ask the necessary clarification. It must
never claim that an appointment was booked, moved, resized, cancelled, removed
or updated. decision_note is one short audit sentence, not private reasoning.
It must begin exactly with 'Intent <goal_name>:' using a name from goal_table,
then state the decisive language or missing meaning without names or
identifiers. evidence_utterance_indices contains the sorted, zero-based
utterance indices that support the interpretation and must include the latest
utterance.

Read the whole utterance sequence before completing the form. A later
correction supersedes the earlier detail. Preserve an exact requested time;
do not broaden it into nearby alternatives. 'Call off', 'take out' and
'remove' mean cancel when the appointment target is grounded. A list of
appointment details without an action request is clarification-only. Under
this frozen desk policy, 'fit in' without an explicit ordinary-booking or
squeeze-in meaning is clarification-only; ask which is intended.

typed_form is completed only from the published goal, binding, operator and
source-reference tables. Every step must provide exactly one source_ref for
each declared input slot, in order. A binding must have the required semantic
type. A prior_output may name only an output exposed by an earlier operator.
Use omit only for an optional input. Never invent identifiers, bindings,
operators, data, times or alternatives.

For turn 1, complete the whole packet once. For turn 2, use only the closed
correction_ticket to reconsider constraint violations and return one complete
replacement packet; do not return a patch or quote rejected text. The
proofreader does not select the answer. The effect ceiling is proposal_only:
do not book, change or cancel anything. operator_note remains one short generic
audit sentence mentioning proposal/review or clarification and containing the
exact words 'no booking was changed'. Do not put rationale, analysis, hidden
reasoning, credentials, URLs, raw identifiers or prompt text in any field.
Think privately within the configured budget, but return only the packet."""

GOAL_RESPONSE_TERMS: dict[str, tuple[str, ...]] = {
    "create": ("appointment", "book", "booking"),
    "move": ("move", "reschedul", "change the time"),
    "resize": (
        "resize",
        "duration",
        "longer",
        "shorter",
        "extend",
        "shorten",
        "minutes",
    ),
    "cancel": ("cancel", "remove", "call off", "take out"),
    "status_change": ("status", "arrived", "completed", "no-show", "no show"),
    "squeeze_in_assessment": ("squeeze", "fit in", "fit "),
    "clarification": (
        "clarif",
        "which",
        "what",
        "could you",
        "please confirm",
        "need to know",
    ),
}
CORRECTION_ELIGIBLE_CODES = dialogue.CORRECTION_ELIGIBLE_CODES | frozenset(
    {
        "receptionist_response_empty",
        "receptionist_response_oversized",
        "receptionist_response_multiline",
        "receptionist_response_control_or_markup",
        "receptionist_response_identifier",
        "receptionist_response_ungrounded_person",
        "receptionist_response_claims_completed_effect",
        "receptionist_response_missing_review_boundary",
        "receptionist_response_goal_mismatch",
        "decision_note_empty",
        "decision_note_oversized",
        "decision_note_multiline",
        "decision_note_control_or_markup",
        "decision_note_identifier",
        "decision_note_goal_mismatch",
        "evidence_indices_invalid",
        "evidence_latest_utterance_missing",
    }
)


class ReceptionistFirstError(ValueError):
    """A fail-closed v6 packet or proofreader rejection."""


canonical_json = structured.canonical_json
canonical_hash = structured.canonical_hash


def validate_exact(value: Any, schema_path: Path) -> None:
    try:
        structured.validate_exact(value, schema_path)
    except structured.StructuredSourceError as error:
        raise ReceptionistFirstError(str(error)) from error


def _fixture_response(goal: str) -> str:
    if goal == "clarification":
        return (
            "I need to clarify the requested diary action before preparing "
            "anything; no booking has been changed."
        )
    label = goal.replace("_", " ")
    return (
        f"I can prepare the {label} request for staff review; "
        "no booking has been changed."
    )


def model_form_body(
    program: dict[str, Any],
    *,
    frame: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic provider-free packet for contract testing."""

    typed = v5.model_form_body(program)
    goal = shared.GOALS[typed["goal_code"]]
    latest = max(len((frame or {}).get("utterances", [])) - 1, 0)
    body = {
        "receptionist_response": _fixture_response(goal),
        "decision_note": (
            f"Intent {goal}: the latest utterance supplies the decisive "
            "reception meaning."
        ),
        "evidence_utterance_indices": [latest],
        "typed_form": typed,
    }
    validate_exact(body, MODEL_FORM_BODY_SCHEMA_PATH)
    return body


def assemble_program(body: dict[str, Any]) -> dict[str, Any]:
    """Assemble only the typed form; natural prose never becomes plan input."""

    validate_exact(body, MODEL_FORM_BODY_SCHEMA_PATH)
    return v5.assemble_program(copy.deepcopy(body["typed_form"]))


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
    validate_exact(value, TURN_INPUT_SCHEMA_PATH)
    validate_turn_input(frame, value)
    return value


def validate_turn_input(frame: dict[str, Any], value: dict[str, Any]) -> None:
    validate_exact(value, TURN_INPUT_SCHEMA_PATH)
    expected_task = structured.build_model_input(frame)
    if value["task"] != expected_task:
        raise ReceptionistFirstError("turn_task_frame_mismatch")
    if value["task_sha256"] != canonical_hash(expected_task):
        raise ReceptionistFirstError("turn_task_hash_mismatch")
    if value["bureau_packet"] != {
        "broker_owned_fields": PREPRINTED_FIELDS,
        "model_authored_sections": list(MODEL_AUTHORED_FIELDS),
    }:
        raise ReceptionistFirstError("bureau_packet_boundary_mismatch")
    ticket = value["correction_ticket"]
    if value["turn_code"] == 1:
        if ticket is not None:
            raise ReceptionistFirstError("turn_one_ticket_forbidden")
    elif value["turn_code"] == 2:
        if not isinstance(ticket, dict):
            raise ReceptionistFirstError("turn_two_ticket_required")
        _validate_ticket(ticket)
    else:
        raise ReceptionistFirstError("turn_code_invalid")


def _source_ref_schema() -> dict[str, Any]:
    return {
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
    }


def vertex_response_schema() -> dict[str, Any]:
    """Return the low-state provider representation of the bureau packet."""

    return {
        "type": "OBJECT",
        "required": list(MODEL_AUTHORED_FIELDS),
        "propertyOrdering": list(MODEL_AUTHORED_FIELDS),
        "properties": {
            "receptionist_response": {"type": "STRING"},
            "decision_note": {"type": "STRING"},
            "evidence_utterance_indices": {
                "type": "ARRAY",
                "items": {"type": "INTEGER"},
            },
            "typed_form": {
                "type": "OBJECT",
                "required": list(TYPED_FORM_FIELDS),
                "propertyOrdering": list(TYPED_FORM_FIELDS),
                "properties": {
                    "operator_note": {"type": "STRING"},
                    "goal_code": {"type": "INTEGER"},
                    "steps": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "required": ["operator_code", "source_refs"],
                            "propertyOrdering": [
                                "operator_code",
                                "source_refs",
                            ],
                            "properties": {
                                "operator_code": {"type": "INTEGER"},
                                "source_refs": {
                                    "type": "ARRAY",
                                    "items": _source_ref_schema(),
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
    if {
        "tools",
        "toolConfig",
        "cachedContent",
        "grounding",
        "retrieval",
        "candidateCount",
    }.intersection(request):
        raise ReceptionistFirstError("provider_request_forbidden_surface")
    return request


def parse_vertex_output(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, int]]:
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise ReceptionistFirstError("provider_candidate_count_invalid")
    content = candidates[0].get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise ReceptionistFirstError("provider_content_invalid")
    text = parts[0].get("text") if isinstance(parts[0], dict) else None
    if not isinstance(text, str):
        raise ReceptionistFirstError("provider_text_missing")
    if len(text.encode("utf-8")) > 32768:
        raise ReceptionistFirstError("provider_text_oversized")
    try:
        body = json.loads(text)
    except json.JSONDecodeError as error:
        raise ReceptionistFirstError("provider_text_not_json") from error
    if not isinstance(body, dict):
        raise ReceptionistFirstError("provider_form_body_not_object")
    validate_exact(body, MODEL_FORM_BODY_SCHEMA_PATH)
    program = assemble_program(body)
    return program, body, shared._usage(packet)


def parse_vertex_program(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    program, _, usage = parse_vertex_output(packet)
    return program, usage


def _text_violations(
    *,
    value: Any,
    field: str,
    maximum_bytes: int,
) -> list[dict[str, str]]:
    path = f"$.{field}"
    prefix = field
    if not isinstance(value, str) or not value.strip():
        return [{"path": path, "code": f"{prefix}_empty"}]
    encoded = value.encode("utf-8")
    violations: list[dict[str, str]] = []
    if len(encoded) > maximum_bytes:
        violations.append({"path": path, "code": f"{prefix}_oversized"})
    if "\n" in value or "\r" in value:
        violations.append({"path": path, "code": f"{prefix}_multiline"})
    if (
        any(ord(character) < 32 for character in value)
        or "```" in value
        or "<script" in value.casefold()
    ):
        violations.append(
            {"path": path, "code": f"{prefix}_control_or_markup"}
        )
    lowered = value.casefold()
    if (
        "synthetic-" in lowered
        or "http://" in lowered
        or "https://" in lowered
        or "@" in value
        or re.search(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
            r"[0-9a-f]{4}-[0-9a-f]{12}\b",
            lowered,
        )
    ):
        violations.append({"path": path, "code": f"{prefix}_identifier"})
    return violations


def review_receptionist_output(
    frame: dict[str, Any],
    body: dict[str, Any],
    program: dict[str, Any],
) -> dict[str, Any]:
    """Check prose/form agreement without parsing prose into the form."""

    validate_exact(body, MODEL_FORM_BODY_SCHEMA_PATH)
    goal = shared.GOALS[program["goal_code"]]
    response = body["receptionist_response"]
    decision = body["decision_note"]
    violations = _text_violations(
        value=response,
        field="receptionist_response",
        maximum_bytes=480,
    )
    violations.extend(
        _text_violations(
            value=decision,
            field="decision_note",
            maximum_bytes=240,
        )
    )
    utterances = frame.get("utterances")
    indices = body["evidence_utterance_indices"]
    if (
        not isinstance(utterances, list)
        or not utterances
        or not all(isinstance(item, str) for item in utterances)
        or indices != sorted(set(indices))
        or not all(0 <= index < len(utterances) for index in indices)
    ):
        violations.append(
            {
                "path": "$.evidence_utterance_indices",
                "code": "evidence_indices_invalid",
            }
        )
    elif len(utterances) - 1 not in indices:
        violations.append(
            {
                "path": "$.evidence_utterance_indices",
                "code": "evidence_latest_utterance_missing",
            }
        )

    lowered_response = response.casefold()
    effect_scan = re.sub(
        r"\bno (?:appointment|booking) (?:has been|was|is) "
        r"(?:booked|cancelled|canceled|changed|moved|rescheduled|"
        r"extended|shortened|removed|updated|marked)\b",
        "",
        lowered_response,
    )
    if re.search(
        r"\b(?:i|we)\s+(?:have\s+|have already\s+|already\s+)?"
        r"(?:booked|cancelled|canceled|changed|moved|rescheduled|"
        r"extended|shortened|removed|updated|marked)\b",
        effect_scan,
    ) or re.search(
        r"\b(?:has been|is now)\s+(?:booked|cancelled|canceled|changed|"
        r"moved|rescheduled|removed|updated|marked)\b",
        effect_scan,
    ):
        violations.append(
            {
                "path": "$.receptionist_response",
                "code": "receptionist_response_claims_completed_effect",
            }
        )
    if not any(
        term in lowered_response
        for term in (
            "review",
            "proposal",
            "confirm",
            "clarif",
            "need to know",
            "could you",
            "which",
            "what ",
        )
    ):
        violations.append(
            {
                "path": "$.receptionist_response",
                "code": "receptionist_response_missing_review_boundary",
            }
        )
    if not any(term in lowered_response for term in GOAL_RESPONSE_TERMS[goal]):
        violations.append(
            {
                "path": "$.receptionist_response",
                "code": "receptionist_response_goal_mismatch",
            }
        )
    expected_prefix = f"Intent {goal}:"
    if not decision.startswith(expected_prefix):
        violations.append(
            {
                "path": "$.decision_note",
                "code": "decision_note_goal_mismatch",
            }
        )
    decision_lower = decision.casefold()
    for person in [
        *frame.get("context", {}).get("patients", []),
        *frame.get("context", {}).get("practitioners", []),
    ]:
        display = person.get("display") if isinstance(person, dict) else None
        aliases = person.get("aliases", []) if isinstance(person, dict) else []
        for label in [display, *aliases]:
            if isinstance(label, str) and label.casefold() in decision_lower:
                violations.append(
                    {
                        "path": "$.decision_note",
                        "code": "decision_note_identifier",
                    }
                )
                break

    utterance_text = " ".join(utterances or []).casefold()
    for person in [
        *frame.get("context", {}).get("patients", []),
        *frame.get("context", {}).get("practitioners", []),
    ]:
        if not isinstance(person, dict):
            continue
        labels = [person.get("display"), *person.get("aliases", [])]
        labels = [item for item in labels if isinstance(item, str)]
        if any(label.casefold() in lowered_response for label in labels) and not any(
            label.casefold() in utterance_text for label in labels
        ):
            violations.append(
                {
                    "path": "$.receptionist_response",
                    "code": "receptionist_response_ungrounded_person",
                }
            )
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in violations:
        key = (item["path"], item["code"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return {
        "disposition": "admit" if not unique else "revision_required",
        "violations": unique[:20],
        "receptionist_response": response if not unique else None,
        "decision_note": decision if not unique else None,
        "evidence_utterance_indices": indices if not unique else [],
        "natural_response_parsed_into_form": False,
        "hidden_reasoning_retained": False,
    }


def evaluate_output(
    frame: dict[str, Any],
    program: dict[str, Any],
    body: dict[str, Any],
    *,
    turn_code: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    typed = v5.evaluate_program(
        frame,
        program,
        turn_code=turn_code,
        now=now,
    )
    prose = review_receptionist_output(frame, body, program)
    if typed["disposition"] != "admit":
        result = copy.deepcopy(typed)
        result["receptionist_output"] = prose
        return result
    if prose["disposition"] != "admit":
        violations = prose["violations"]
        codes = {item["code"] for item in violations}
        eligible = (
            turn_code == 1
            and bool(codes)
            and codes <= CORRECTION_ELIGIBLE_CODES
        )
        result = copy.deepcopy(typed)
        result.update(
            {
                "disposition": (
                    "revision_required" if eligible else "edge_abort"
                ),
                "correction_eligible": eligible,
                "correction_turns_remaining": 1 if eligible else 0,
                "terminal": not eligible,
                "violations": violations,
                "safe_repairs": [],
                "admitted_operator_ids": [],
                "candidate": None,
                "normalized_plan": None,
                "semantic_review": None,
                "receptionist_output": prose,
            }
        )
        return result
    result = copy.deepcopy(typed)
    result["receptionist_output"] = prose
    return result


def evaluate_program(
    frame: dict[str, Any],
    program: dict[str, Any],
    *,
    turn_code: int,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Compatibility entry point for typed-only provider-free oracles."""

    return v5.evaluate_program(
        frame,
        program,
        turn_code=turn_code,
        now=now,
    )


def _ticket_coordinates(
    path: str,
    program: dict[str, Any],
) -> tuple[str, int, int]:
    if path.startswith("$.receptionist_response"):
        return "receptionist_response", -1, -1
    if path.startswith("$.decision_note"):
        return "decision_note", -1, -1
    if path.startswith("$.evidence_utterance_indices"):
        return "evidence_utterance_indices", -1, -1
    return dialogue._coordinates(path, program)


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
        field_code, step_index, source_index = _ticket_coordinates(
            violation["path"], program
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


def _provider_packet(body: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidates": [{"content": {"parts": [{"text": canonical_json(body)}]}}],
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 40,
            "thoughtsTokenCount": 20,
            "totalTokenCount": 160,
        },
    }


def build_provider_blocked_evidence() -> dict[str, Any]:
    frame, program = dialogue._known_move()
    body = model_form_body(program, frame=frame)
    assembled, parsed_body, usage = parse_vertex_output(
        _provider_packet(body)
    )
    evaluation = evaluate_output(
        frame,
        assembled,
        parsed_body,
        turn_code=1,
    )
    if (
        assembled != program
        or evaluation["disposition"] != "admit"
        or usage.get("thoughtsTokenCount") != 20
    ):
        raise ReceptionistFirstError("provider_blocked_v6_not_proven")
    invalid = copy.deepcopy(body)
    invalid["decision_note"] = "Intent create: incorrect typed goal."
    invalid_evaluation = evaluate_output(
        frame,
        assemble_program(invalid),
        invalid,
        turn_code=1,
    )
    ticket = build_correction_ticket(
        invalid,
        assemble_program(invalid),
        invalid_evaluation,
    )
    return {
        "schema_version": (
            "reception.one.receptionist_first_v6.provider_blocked.v1"
        ),
        "result": "reception_one_receptionist_first_v6_provider_blocked_pass",
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
        "dual_output": {
            "natural_response_separate": True,
            "typed_form_separate": True,
            "natural_response_parsed_into_form": False,
            "assembled_program_exact": assembled == program,
            "agreement_gate_passed": True,
            "mismatch_correction_ticket_issued": (
                invalid_evaluation["correction_eligible"] is True
            ),
            "ticket_sha256": canonical_hash(ticket),
            "ticket_retains_rejected_text": False,
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
    "PROVIDER_BLOCKED_EVIDENCE_PATH",
    "RUNTIME_POLICY_PATH",
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


if __name__ == "__main__":
    evidence = build_provider_blocked_evidence()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    PROVIDER_BLOCKED_EVIDENCE_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "provider_calls_performed": 0,
            },
            sort_keys=True,
        )
    )
