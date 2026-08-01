#!/usr/bin/env python3
"""One mechanically lossless language for Reception One's model and proofreader."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as legacy_lane
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-shared-typed-language"
)
MODEL_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "model-input.schema.json"
PLAN_PROGRAM_SCHEMA_PATH = ARTIFACT_DIR / "plan-program.schema.json"
PROVIDER_BLOCKED_EVIDENCE_PATH = (
    ARTIFACT_DIR / "provider-blocked-evidence.json"
)
MODEL_INPUT_VERSION = "reception.one.bureau.shared-model-input.v3"
PLAN_PROGRAM_VERSION_CODE = 2
NOTE_MAX_BYTES = 320
STEP_OUTPUT_BASE = 1000
STEP_OUTPUT_STRIDE = 16
MAX_STEPS = 12
PROOFREADER_FEEDBACK_VERSION_CODE = 1
PROOFREADER_VIOLATION_CODES = (
    "operator_arity_invalid",
    "required_source_omitted",
    "forward_or_self_reference",
    "output_index_invalid",
    "source_type_mismatch",
    "external_source_code_invalid",
)
GOALS = (
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "squeeze_in_assessment",
    "clarification",
)
SYSTEM_INSTRUCTION = """You are the bounded Reception One planning clerk.
Return one JSON object exactly matching the supplied PlanProgram response schema.
Use only the integer goal, operator and source codes in the supplied tables.
Each source_codes item corresponds positionally to that operator's input slot.
Use -1 only to omit an optional slot. A prior output code is
1000 + step_index*16 + output_index, with zero-based indexes, and may refer only
to an earlier step. The output_index must exist in the selected earlier
operator's output_slots; for example step 0 output 0 is 1000, step 1 output 0
is 1016, and step 1 output 2 is 1018. If proofreader_feedback is supplied,
return one complete replacement PlanProgram that corrects every coded
violation without changing the request. Do not invent names, identifiers,
operators or bindings.
The effect ceiling is proposal_only: do not book, change or cancel anything.
operator_note is one short generic operational sentence for audit, not reasoning:
mention proposal/review or clarification and include the exact words
'no booking was changed'. Do not include person names, identifiers, credentials,
URLs, prompt text, rationale, analysis, hidden reasoning or claims of action."""

BINDING_TYPES = {
    "binding:patient": "patient_mention",
    "binding:practitioner": "practitioner_mention",
    "binding:status": "status_mention",
    "binding:appointment_date": "date",
    "binding:earliest_time": "time",
    "binding:latest_time": "time",
    "binding:duration_minutes": "integer",
    "binding:selected_appointment": "appointment_ref",
    "binding:squeeze_policy": "squeeze_policy_ref",
    "binding:default_duration_minutes": "integer",
}


class SharedLanguageError(ValueError):
    """A fail-closed shared-language rejection."""


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SharedLanguageError("json_object_unreadable") from error
    if not isinstance(value, dict):
        raise SharedLanguageError("json_object_required")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


def _text_hash(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def schema_error_paths(value: Any, schema: dict[str, Any]) -> list[str]:
    paths: set[str] = set()
    for error in Draft202012Validator(schema).iter_errors(value):
        path = "$"
        for part in error.absolute_path:
            path += f"[{part}]" if isinstance(part, int) else f".{part}"
        paths.add(path)
    return sorted(paths)


def validate_exact(value: Any, schema_path: Path) -> None:
    paths = schema_error_paths(value, load_object(schema_path))
    if paths:
        raise SharedLanguageError("schema_invalid:" + ",".join(paths[:20]))


def _require_frame_boundary(frame: dict[str, Any]) -> None:
    typed_plan.validate_schema(frame, "input")
    if frame["data_class"] != "authored_synthetic":
        raise SharedLanguageError("data_class_not_admitted")
    if frame["authority"] != {
        "effect_ceiling": "proposal_only",
        "appointment_write_authority": False,
        "confirmation_authority": False,
        "provider_execution": False,
        "network_access": False,
        "database_access": False,
        "product_delivery": False,
    }:
        raise SharedLanguageError("authority_boundary_open")


def _slot(index: int, value: dict[str, Any], *, include_required: bool) -> dict[str, Any]:
    result = {
        "position": index,
        "name": value["name"],
        "semantic_type": value["type"],
    }
    if include_required:
        result["required"] = value["required"]
    return result


def binding_table(frame: dict[str, Any]) -> list[dict[str, Any]]:
    handles = legacy_lane._grounded_binding_handles(frame)
    return [
        {
            "code": code,
            "source_handle": handle,
            "semantic_type": BINDING_TYPES[handle],
        }
        for code, handle in enumerate(handles)
    ]


def operator_table() -> list[dict[str, Any]]:
    catalog = typed_plan.load_json(typed_plan.CATALOG_PATH)
    return [
        {
            "code": code,
            "name": operator["id"],
            "effect": operator["effect"],
            "input_slots": [
                _slot(index, value, include_required=True)
                for index, value in enumerate(operator["inputs"])
            ],
            "output_slots": [
                _slot(index, value, include_required=False)
                for index, value in enumerate(operator["outputs"])
            ],
        }
        for code, operator in enumerate(catalog["operators"])
    ]


def build_proofreader_feedback(
    *,
    previous_program_hash: str,
    review: dict[str, Any],
) -> dict[str, Any]:
    """Encode only closed proofreader findings for a bounded replacement draft."""

    if not re.fullmatch(r"sha256:[0-9a-f]{64}", previous_program_hash):
        raise SharedLanguageError("feedback_program_hash_invalid")
    violations = review.get("violations")
    if (
        review.get("disposition") != "edge_abort"
        or not isinstance(violations, list)
        or not violations
        or len(violations) > 8
    ):
        raise SharedLanguageError("feedback_review_not_eligible")
    encoded: list[dict[str, int]] = []
    for violation in violations:
        if (
            not isinstance(violation, dict)
            or violation.get("path") != "$.steps"
            or violation.get("code") not in PROOFREADER_VIOLATION_CODES
        ):
            raise SharedLanguageError("feedback_violation_not_allowlisted")
        encoded.append(
            {
                "violation_code": PROOFREADER_VIOLATION_CODES.index(
                    violation["code"]
                ),
                "path_code": 0,
            }
        )
    return {
        "version_code": PROOFREADER_FEEDBACK_VERSION_CODE,
        "previous_program_hash": previous_program_hash,
        "replacement_required": True,
        "violations": encoded,
    }


def build_model_input(
    frame: dict[str, Any],
    *,
    proofreader_feedback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _require_frame_boundary(frame)
    result = {
        "contract_version": MODEL_INPUT_VERSION,
        "data_class": "authored_synthetic",
        "utterances": copy.deepcopy(frame["utterances"]),
        "effect_ceiling": "proposal_only",
        "source_encoding": {
            "external_binding": "binding_table_code",
            "prior_step_output": (
                "1000_plus_step_index_times_16_plus_output_index"
            ),
            "prior_output_validity": (
                "zero_based_output_index_must_exist_on_selected_earlier_operator"
            ),
            "prior_output_examples": [
                {
                    "source_step_index": 0,
                    "output_index": 0,
                    "source_code": 1000,
                },
                {
                    "source_step_index": 1,
                    "output_index": 0,
                    "source_code": 1016,
                },
                {
                    "source_step_index": 1,
                    "output_index": 2,
                    "source_code": 1018,
                },
            ],
            "optional_omission": -1,
        },
        "goal_table": [
            {"code": code, "name": goal} for code, goal in enumerate(GOALS)
        ],
        "binding_table": binding_table(frame),
        "operator_table": operator_table(),
    }
    if proofreader_feedback is not None:
        result["proofreader_feedback"] = copy.deepcopy(
            proofreader_feedback
        )
    validate_exact(result, MODEL_INPUT_SCHEMA_PATH)
    return result


def audit_typed_program(program: dict[str, Any]) -> dict[str, Any]:
    """Retain only the closed integer form; the separately gated note is omitted."""

    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    typed_form = {
        "version_code": program["version_code"],
        "goal_code": program["goal_code"],
        "steps": copy.deepcopy(program["steps"]),
    }
    if not all(
        type(value) is int
        for step in typed_form["steps"]
        for value in [step["operator_code"], *step["source_codes"]]
    ):
        raise SharedLanguageError("audit_typed_program_not_integer_only")
    return typed_form


def vertex_response_schema() -> dict[str, Any]:
    """Return the provider representation of the exact local PlanProgram."""

    return {
        "type": "OBJECT",
        "required": ["version_code", "operator_note", "goal_code", "steps"],
        "properties": {
            "version_code": {
                "type": "INTEGER",
                "minimum": 2,
                "maximum": 2,
            },
            "operator_note": {
                "type": "STRING",
                "minLength": 1,
                "maxLength": 320,
            },
            "goal_code": {
                "type": "INTEGER",
                "minimum": 0,
                "maximum": 6,
            },
            "steps": {
                "type": "ARRAY",
                "minItems": 1,
                "maxItems": 12,
                "items": {
                    "type": "OBJECT",
                    "required": ["operator_code", "source_codes"],
                    "properties": {
                        "operator_code": {
                            "type": "INTEGER",
                            "minimum": 0,
                            "maximum": 13,
                        },
                        "source_codes": {
                            "type": "ARRAY",
                            "maxItems": 8,
                            "items": {
                                "type": "INTEGER",
                                "minimum": -1,
                                "maximum": 1187,
                            },
                        },
                    },
                },
            },
        },
    }


def build_vertex_request(model_input: dict[str, Any]) -> dict[str, Any]:
    validate_exact(model_input, MODEL_INPUT_SCHEMA_PATH)
    request = {
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": canonical_json(model_input)}],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 768,
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
        raise SharedLanguageError("provider_request_forbidden_surface")
    return request


def _frame_names(frame: dict[str, Any]) -> list[str]:
    values: set[str] = set()
    context = frame.get("context")
    if not isinstance(context, dict):
        return []
    for collection in ("patients", "practitioners"):
        rows = context.get(collection)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            display = row.get("display")
            if isinstance(display, str) and len(display) >= 3:
                values.add(display.casefold())
            aliases = row.get("aliases")
            if isinstance(aliases, list):
                for alias in aliases:
                    if isinstance(alias, str) and len(alias) >= 3:
                        values.add(alias.casefold())
    return sorted(values)


def review_operator_note(frame: dict[str, Any], note: Any) -> dict[str, Any]:
    """Independently admit or discard the only retainable model prose field."""

    text = note if isinstance(note, str) else ""
    lowered = text.casefold()
    reasons: set[str] = set()
    if not isinstance(note, str):
        reasons.add("note_not_string")
    if not text:
        reasons.add("note_empty")
    if len(text.encode("utf-8")) > NOTE_MAX_BYTES:
        reasons.add("note_oversized")
    if "\n" in text or "\r" in text:
        reasons.add("note_multiline")
    if any(ord(character) < 32 or ord(character) > 126 for character in text):
        reasons.add("note_non_ascii_or_control")
    if any(character in text for character in "<>{}[]`\\"):
        reasons.add("note_markup_or_code_surface")
    if re.search(r"https?://|www\\.|\\b[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}\\b", lowered):
        reasons.add("note_network_or_email_identifier")
    if re.search(
        r"\\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\\b",
        lowered,
    ):
        reasons.add("note_uuid")
    if re.search(r"\\b(?:synthetic|binding|step)[-:][a-z0-9_-]+\\b", lowered):
        reasons.add("note_internal_identifier")
    forbidden_fragments = (
        "access token",
        "refresh token",
        "api key",
        "authorization",
        "bearer ",
        "credential",
        "service account",
        "bernie-emr4-dev",
        "aiplatform.googleapis.com",
        "chain of thought",
        "step by step",
        "my reasoning",
        "i reasoned",
        "analysis:",
        "rationale:",
    )
    if any(fragment in lowered for fragment in forbidden_fragments):
        reasons.add("note_secret_identity_or_hidden_reasoning")
    if any(name in lowered for name in _frame_names(frame)):
        reasons.add("note_person_name")
    action_claims = (
        "i booked",
        "i changed",
        "i moved",
        "i cancelled",
        "i canceled",
        "has been booked",
        "has been changed",
        "has been moved",
        "has been cancelled",
        "has been canceled",
        "was booked",
        "was changed",
        "was moved",
        "was cancelled",
        "was canceled",
    )
    claims_text = lowered.replace("no booking was changed", "")
    if any(fragment in claims_text for fragment in action_claims):
        reasons.add("note_claims_command_effect")
    if not any(term in lowered for term in ("proposal", "review", "clarification")):
        reasons.add("note_missing_bounded_purpose")
    if "no booking was changed" not in lowered:
        reasons.add("note_missing_no_change_statement")
    disposition = "admit" if not reasons else "reject"
    result = {
        "schema_version": "reception.one.operator_note_review.v1",
        "disposition": disposition,
        "reason_codes": sorted(reasons),
        "note_sha256": _text_hash(text),
        "retained_utf8_bytes": len(text.encode("utf-8")) if not reasons else 0,
    }
    if disposition == "admit":
        result["retained_text"] = text
    return result


def _binding_source(binding: dict[str, Any]) -> str:
    kind = binding["kind"]
    if kind == "utterance_ref":
        return f"binding:{binding['entity_type']}"
    if kind in {"semantic_ref", "context_ref"}:
        return f"binding:{binding['field']}"
    raise SharedLanguageError("binding_not_external")


def program_from_plan(
    frame: dict[str, Any],
    plan: dict[str, Any],
    *,
    operator_note: str,
) -> dict[str, Any]:
    """Encode a trusted fixture as the exact program the model must emit."""

    _require_frame_boundary(frame)
    typed_plan.validate_schema(plan, "plan")
    bindings = binding_table(frame)
    binding_codes = {
        item["source_handle"]: item["code"] for item in bindings
    }
    operators = operator_table()
    operator_codes = {item["name"]: item["code"] for item in operators}
    step_indexes = {step["id"]: index for index, step in enumerate(plan["steps"])}
    steps: list[dict[str, Any]] = []
    for step_index, step in enumerate(plan["steps"]):
        operator = operators[operator_codes[step["operator"]]]
        source_codes: list[int] = []
        for input_slot in operator["input_slots"]:
            binding = step["args"].get(input_slot["name"])
            if binding is None:
                if input_slot["required"]:
                    raise SharedLanguageError("trusted_plan_missing_required_input")
                source_codes.append(-1)
                continue
            if binding["kind"] == "step_output":
                source_step = step_indexes.get(binding["step_id"])
                if source_step is None or source_step >= step_index:
                    raise SharedLanguageError("trusted_plan_step_reference_invalid")
                source_operator = operators[
                    operator_codes[plan["steps"][source_step]["operator"]]
                ]
                outputs = source_operator["output_slots"]
                output_index = next(
                    (
                        item["position"]
                        for item in outputs
                        if item["name"] == binding["output"]
                    ),
                    None,
                )
                if output_index is None:
                    raise SharedLanguageError("trusted_plan_output_invalid")
                source_codes.append(
                    STEP_OUTPUT_BASE
                    + source_step * STEP_OUTPUT_STRIDE
                    + output_index
                )
            else:
                handle = _binding_source(binding)
                if handle not in binding_codes:
                    raise SharedLanguageError("trusted_plan_binding_not_grounded")
                source_codes.append(binding_codes[handle])
        steps.append(
            {
                "operator_code": operator["code"],
                "source_codes": source_codes,
            }
        )
    program = {
        "version_code": PLAN_PROGRAM_VERSION_CODE,
        "operator_note": operator_note,
        "goal_code": GOALS.index(plan["goal"]),
        "steps": steps,
    }
    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    return program


def compile_program(
    frame: dict[str, Any],
    program: dict[str, Any],
) -> dict[str, Any]:
    """Mechanically decode PlanProgram; perform no prose interpretation."""

    _require_frame_boundary(frame)
    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    bindings = binding_table(frame)
    operators = operator_table()
    candidate_steps: list[dict[str, Any]] = []
    for step_index, encoded_step in enumerate(program["steps"]):
        operator = operators[encoded_step["operator_code"]]
        sources = encoded_step["source_codes"]
        inputs = operator["input_slots"]
        if len(sources) != len(inputs):
            raise SharedLanguageError(
                f"operator_arity_invalid:$.steps[{step_index}].source_codes"
            )
        arguments: list[dict[str, str]] = []
        for source_position, (source_code, input_slot) in enumerate(
            zip(sources, inputs, strict=True)
        ):
            path = f"$.steps[{step_index}].source_codes[{source_position}]"
            if source_code == -1:
                if input_slot["required"]:
                    raise SharedLanguageError("required_source_omitted:" + path)
                continue
            if 0 <= source_code < len(bindings):
                source = bindings[source_code]
                source_type = source["semantic_type"]
                source_handle = source["source_handle"]
            elif source_code >= STEP_OUTPUT_BASE:
                encoded = source_code - STEP_OUTPUT_BASE
                source_step_index, output_index = divmod(
                    encoded, STEP_OUTPUT_STRIDE
                )
                if source_step_index >= step_index:
                    raise SharedLanguageError("forward_or_self_reference:" + path)
                source_operator_code = program["steps"][source_step_index][
                    "operator_code"
                ]
                source_operator = operators[source_operator_code]
                if output_index >= len(source_operator["output_slots"]):
                    raise SharedLanguageError("output_index_invalid:" + path)
                output = source_operator["output_slots"][output_index]
                source_type = output["semantic_type"]
                source_handle = (
                    "step:"
                    f"step-p{source_step_index + 1:02d}:"
                    f"{output['name']}"
                )
            else:
                raise SharedLanguageError("external_source_code_invalid:" + path)
            if source_type != input_slot["semantic_type"]:
                raise SharedLanguageError("source_type_mismatch:" + path)
            arguments.append(
                {
                    "name": input_slot["name"],
                    "source": source_handle,
                }
            )
        candidate_steps.append(
            {
                "id": f"step-p{step_index + 1:02d}",
                "operator": operator["name"],
                "arguments": arguments,
            }
        )
    candidate = {
        "contract_version": legacy_lane.CONTRACT_VERSION,
        "goal": GOALS[program["goal_code"]],
        "steps": candidate_steps,
    }
    legacy_lane.validate_exact(candidate, legacy_lane.CANDIDATE_SCHEMA_PATH)
    return candidate


def proofread_program(
    frame: dict[str, Any],
    program: dict[str, Any],
    *,
    attempt: int = 1,
) -> tuple[
    dict[str, Any],
    dict[str, Any] | None,
    dict[str, Any] | None,
    dict[str, Any],
]:
    """Run the direct language gate and then the accepted semantic proofreader."""

    note_review = review_operator_note(
        frame,
        program.get("operator_note") if isinstance(program, dict) else None,
    )
    if note_review["disposition"] != "admit":
        review = {
            "disposition": "edge_abort",
            "attempt": attempt,
            "revision_allowed": attempt < 2,
            "safe_repairs": [],
            "violations": [
                {"path": "$.operator_note", "code": code}
                for code in note_review["reason_codes"]
            ],
            "admitted_operator_ids": [],
            "reviewed_context_revision": frame.get("context_revision"),
        }
        return review, None, None, note_review
    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    try:
        candidate = compile_program(frame, program)
        review, normalized, _ = legacy_lane.proofread_candidate(
            frame, candidate, attempt=attempt
        )
    except (SharedLanguageError, legacy_lane.ModelLaneError, ValueError) as error:
        code = str(error).split(":", 1)[0]
        review = {
            "disposition": "edge_abort",
            "attempt": attempt,
            "revision_allowed": attempt < 2,
            "safe_repairs": [],
            "violations": [{"path": "$.steps", "code": code}],
            "admitted_operator_ids": [],
            "reviewed_context_revision": frame.get("context_revision"),
        }
        return review, None, None, note_review
    return review, normalized, candidate, note_review


def _usage(packet: dict[str, Any]) -> dict[str, int]:
    usage: dict[str, int] = {}
    raw_usage = packet.get("usageMetadata")
    if isinstance(raw_usage, dict):
        for name in (
            "promptTokenCount",
            "candidatesTokenCount",
            "thoughtsTokenCount",
            "totalTokenCount",
        ):
            value = raw_usage.get(name)
            if type(value) is int and value >= 0:
                usage[name] = value
    return usage


def parse_vertex_program(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise SharedLanguageError("provider_candidate_count_invalid")
    content = candidates[0].get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise SharedLanguageError("provider_content_invalid")
    text = parts[0].get("text") if isinstance(parts[0], dict) else None
    if not isinstance(text, str):
        raise SharedLanguageError("provider_text_missing")
    if len(text.encode("utf-8")) > 16384:
        raise SharedLanguageError("provider_text_oversized")
    try:
        program = json.loads(text)
    except json.JSONDecodeError as error:
        raise SharedLanguageError("provider_text_not_json") from error
    if not isinstance(program, dict):
        raise SharedLanguageError("provider_program_not_object")
    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    return program, _usage(packet)


def build_provider_blocked_evidence() -> dict[str, Any]:
    """Compute deterministic zero-call evidence across every supported goal."""

    document = typed_plan.load_json(typed_plan.CASES_PATH)
    positives: list[dict[str, Any]] = []
    for case in document["cases"]:
        frame = typed_plan.expand_case(document, case)
        plan = typed_plan.deterministic_plan(frame)
        goal = plan["goal"]
        program = program_from_plan(
            frame,
            plan,
            operator_note=(
                f"Prepared a {goal.replace('_', '-')} proposal for review; "
                "no booking was changed."
            ),
        )
        review, normalized, candidate, note_review = proofread_program(
            frame, program
        )
        if (
            review["disposition"] != "admit"
            or normalized is None
            or candidate is None
            or note_review["disposition"] != "admit"
        ):
            raise SharedLanguageError(
                "positive_case_not_admitted:" + case["case_id"]
            )
        execution = typed_plan.execute_plan(frame, normalized, review)
        positives.append(
            {
                "case_id": case["case_id"],
                "goal": goal,
                "program_sha256": canonical_hash(program),
                "candidate_sha256": canonical_hash(candidate),
                "normalized_plan_sha256": canonical_hash(normalized),
                "operator_note_disposition": note_review["disposition"],
                "operator_note_sha256": note_review["note_sha256"],
                "proofreader_disposition": review["disposition"],
                "released_proposal_family": execution["final_output"][
                    "proposal_family"
                ],
                "write_performed": execution["final_output"][
                    "write_performed"
                ],
            }
        )
    move_case = next(
        case for case in document["cases"] if case["case_id"] == "known-move"
    )
    move_frame = typed_plan.expand_case(document, move_case)
    model_input = build_model_input(move_frame)
    provider_request = build_vertex_request(model_input)
    return {
        "schema_version": (
            "reception.one.shared_typed.provider_blocked_evidence.v1"
        ),
        "result": (
            "reception_one_shared_typed_language_provider_blocked_pass"
        ),
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "shared_contract": {
            "model_input_version": MODEL_INPUT_VERSION,
            "plan_program_version_code": PLAN_PROGRAM_VERSION_CODE,
            "goal_code_count": len(GOALS),
            "operator_code_count": len(operator_table()),
            "provider_response_schema_sha256": canonical_hash(
                vertex_response_schema()
            ),
            "model_input_sha256": canonical_hash(model_input),
            "provider_request_sha256": canonical_hash(provider_request),
            "free_form_plan_identifiers": False,
            "semantic_safe_repairs": False,
        },
        "operator_note_policy": {
            "maximum_utf8_bytes": NOTE_MAX_BYTES,
            "independently_proofread": True,
            "audit_only": True,
            "parsed_into_plan": False,
            "product_delivered": False,
            "rejected_text_discarded": True,
            "raw_provider_response_retained": False,
            "hidden_reasoning_retained": False,
        },
        "positive_cases": positives,
        "negative_contract_classes": [
            "operator_arity_invalid",
            "required_source_omitted",
            "forward_or_self_reference",
            "output_index_invalid",
            "source_type_mismatch",
            "external_source_code_invalid",
            "note_person_name",
            "note_secret_identity_or_hidden_reasoning",
            "note_claims_command_effect",
            "note_missing_bounded_purpose",
            "note_missing_no_change_statement",
            "note_multiline",
            "note_oversized",
            "legacy_free_form_wire_schema_invalid",
        ],
        "boundary": {
            "api_key_authentication_used": False,
            "provider_tools": False,
            "grounding": False,
            "retrieval": False,
            "cache_creation": False,
            "database_access": False,
            "appointment_write_authority": False,
            "product_delivery": False,
            "fallback": False,
        },
    }


__all__ = [
    "ARTIFACT_DIR",
    "GOALS",
    "MODEL_INPUT_SCHEMA_PATH",
    "MODEL_INPUT_VERSION",
    "NOTE_MAX_BYTES",
    "PLAN_PROGRAM_SCHEMA_PATH",
    "PLAN_PROGRAM_VERSION_CODE",
    "PROOFREADER_FEEDBACK_VERSION_CODE",
    "PROOFREADER_VIOLATION_CODES",
    "PROVIDER_BLOCKED_EVIDENCE_PATH",
    "SharedLanguageError",
    "audit_typed_program",
    "binding_table",
    "build_proofreader_feedback",
    "build_provider_blocked_evidence",
    "build_model_input",
    "build_vertex_request",
    "canonical_hash",
    "compile_program",
    "operator_table",
    "parse_vertex_program",
    "program_from_plan",
    "proofread_program",
    "review_operator_note",
    "validate_exact",
    "vertex_response_schema",
]
