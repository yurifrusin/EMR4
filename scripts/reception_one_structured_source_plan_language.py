#!/usr/bin/env python3
"""Reception One PlanProgram v3 with explicit typed source references."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as legacy_lane
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_shared_typed_plan_language as shared


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-structured-source-language"
)
MODEL_INPUT_SCHEMA_PATH = ARTIFACT_DIR / "model-input.schema.json"
PLAN_PROGRAM_SCHEMA_PATH = ARTIFACT_DIR / "plan-program.schema.json"
PROVIDER_BLOCKED_EVIDENCE_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
MODEL_INPUT_VERSION = "reception.one.bureau.structured-source-model-input.v4"
PLAN_PROGRAM_VERSION_CODE = 3
PROTOCOL_VERSION = "reception.one.bureau.structured-source-cell.v3"
CONTRACT_MODE = "structured-v3"
MAX_STEPS = 12
OUTPUT_NAMES = (
    "patient",
    "practitioner",
    "date",
    "appointment",
    "duration_minutes",
    "appointments",
    "schedule",
    "candidates",
    "proposal",
    "clarification",
)
SYSTEM_INSTRUCTION = """You are the bounded Reception One planning clerk.
Return one JSON object exactly matching the supplied PlanProgram response schema.
Use only goal_code, operator_code, binding_code and prior_output_name values
published in the supplied tables. Each source_refs item corresponds positionally
to that operator's input slot and must contain fields in this order:
kind, binding_code, prior_step_index, prior_output_name.
For kind binding, use a real request-local binding_code and use -1 and "none"
for both prior-output fields. For kind prior_output, use binding_code -1, an
earlier zero-based prior_step_index, and the exact named output property exposed
by that earlier step's selected operator. For kind omit, use -1, -1 and "none";
omit is valid only for an optional input. Never calculate or emit composite
source codes. Do not invent identifiers, properties, operators or bindings.
The effect ceiling is proposal_only: do not book, change or cancel anything.
operator_note is one short generic operational sentence for audit, not reasoning:
mention proposal/review or clarification and include the exact words
'no booking was changed'. Do not include person names, identifiers, credentials,
URLs, prompt text, rationale, analysis, hidden reasoning or claims of action."""


class StructuredSourceError(ValueError):
    """A fail-closed PlanProgram-v3 rejection."""


def load_object(path: Path) -> dict[str, Any]:
    try:
        return shared.load_object(path)
    except shared.SharedLanguageError as error:
        raise StructuredSourceError(str(error)) from error


canonical_json = shared.canonical_json
canonical_hash = shared.canonical_hash
binding_table = shared.binding_table
operator_table = shared.operator_table
review_operator_note = shared.review_operator_note


def validate_exact(value: Any, schema_path: Path) -> None:
    try:
        shared.validate_exact(value, schema_path)
    except shared.SharedLanguageError as error:
        raise StructuredSourceError(str(error)) from error


def _require_frame_boundary(frame: dict[str, Any]) -> None:
    try:
        shared._require_frame_boundary(frame)
    except shared.SharedLanguageError as error:
        raise StructuredSourceError(str(error)) from error


def _binding_ref(code: int) -> dict[str, Any]:
    return {
        "kind": "binding",
        "binding_code": code,
        "prior_step_index": -1,
        "prior_output_name": "none",
    }


def _prior_ref(step_index: int, output_name: str) -> dict[str, Any]:
    return {
        "kind": "prior_output",
        "binding_code": -1,
        "prior_step_index": step_index,
        "prior_output_name": output_name,
    }


def _omit_ref() -> dict[str, Any]:
    return {
        "kind": "omit",
        "binding_code": -1,
        "prior_step_index": -1,
        "prior_output_name": "none",
    }


def source_reference_contract() -> dict[str, Any]:
    return {
        "field_order": [
            "kind",
            "binding_code",
            "prior_step_index",
            "prior_output_name",
        ],
        "binding": (
            "kind_binding_uses_request_local_binding_code_and_requires_"
            "other_coordinates_to_be_sentinels"
        ),
        "prior_output": (
            "kind_prior_output_uses_an_earlier_zero_based_step_and_an_"
            "output_name_exposed_by_that_steps_operator"
        ),
        "omit": (
            "kind_omit_is_valid_only_for_an_optional_input_and_requires_"
            "all_coordinates_to_be_sentinels"
        ),
        "examples": [
            _binding_ref(4),
            _prior_ref(3, "candidates"),
            _omit_ref(),
        ],
    }


def _catalog_output_names() -> tuple[str, ...]:
    names = {
        output["name"]
        for operator in operator_table()
        for output in operator["output_slots"]
    }
    return tuple(name for name in OUTPUT_NAMES if name in names)


def build_model_input(frame: dict[str, Any]) -> dict[str, Any]:
    _require_frame_boundary(frame)
    if set(_catalog_output_names()) != set(OUTPUT_NAMES):
        raise StructuredSourceError("frozen_output_name_catalog_drift")
    result = {
        "contract_version": MODEL_INPUT_VERSION,
        "data_class": "authored_synthetic",
        "utterances": copy.deepcopy(frame["utterances"]),
        "effect_ceiling": "proposal_only",
        "source_reference_contract": source_reference_contract(),
        "goal_table": [
            {"code": code, "name": goal}
            for code, goal in enumerate(shared.GOALS)
        ],
        "binding_table": binding_table(frame),
        "operator_table": operator_table(),
    }
    validate_exact(result, MODEL_INPUT_SCHEMA_PATH)
    return result


def audit_typed_program(program: dict[str, Any]) -> dict[str, Any]:
    """Retain the closed typed form while omitting the separately gated note."""

    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    typed_form = {
        "version_code": program["version_code"],
        "goal_code": program["goal_code"],
        "steps": copy.deepcopy(program["steps"]),
    }
    for step in typed_form["steps"]:
        if type(step["operator_code"]) is not int:
            raise StructuredSourceError("audit_operator_code_not_integer")
        for source in step["source_refs"]:
            if (
                source["kind"] not in {"binding", "prior_output", "omit"}
                or type(source["binding_code"]) is not int
                or type(source["prior_step_index"]) is not int
                or source["prior_output_name"] not in {"none", *OUTPUT_NAMES}
            ):
                raise StructuredSourceError("audit_source_reference_not_closed")
    return typed_form


def _source_ref_provider_schema() -> dict[str, Any]:
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
            "binding_code": {
                "type": "INTEGER",
                "minimum": -1,
                "maximum": 9,
            },
            "prior_step_index": {
                "type": "INTEGER",
                "minimum": -1,
                "maximum": 11,
            },
            "prior_output_name": {
                "type": "STRING",
                "enum": ["none", *OUTPUT_NAMES],
            },
        },
    }


def vertex_response_schema() -> dict[str, Any]:
    """Provider subset of the exact local PlanProgram-v3 contract."""

    return {
        "type": "OBJECT",
        "required": ["version_code", "operator_note", "goal_code", "steps"],
        "propertyOrdering": [
            "version_code",
            "operator_note",
            "goal_code",
            "steps",
        ],
        "properties": {
            "version_code": {
                "type": "INTEGER",
                "minimum": 3,
                "maximum": 3,
            },
            "operator_note": {
                "type": "STRING",
                "minLength": 1,
                "maxLength": shared.NOTE_MAX_BYTES,
            },
            "goal_code": {
                "type": "INTEGER",
                "minimum": 0,
                "maximum": len(shared.GOALS) - 1,
            },
            "steps": {
                "type": "ARRAY",
                "minItems": 1,
                "maxItems": MAX_STEPS,
                "items": {
                    "type": "OBJECT",
                    "required": ["operator_code", "source_refs"],
                    "propertyOrdering": ["operator_code", "source_refs"],
                    "properties": {
                        "operator_code": {
                            "type": "INTEGER",
                            "minimum": 0,
                            "maximum": len(operator_table()) - 1,
                        },
                        "source_refs": {
                            "type": "ARRAY",
                            "maxItems": 8,
                            "items": _source_ref_provider_schema(),
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
        raise StructuredSourceError("provider_request_forbidden_surface")
    return request


def _binding_source(binding: dict[str, Any]) -> str:
    try:
        return shared._binding_source(binding)
    except shared.SharedLanguageError as error:
        raise StructuredSourceError(str(error)) from error


def program_from_plan(
    frame: dict[str, Any],
    plan: dict[str, Any],
    *,
    operator_note: str,
) -> dict[str, Any]:
    """Encode a trusted PlanDraft as the exact provider-emittable v3 form."""

    _require_frame_boundary(frame)
    typed_plan.validate_schema(plan, "plan")
    bindings = binding_table(frame)
    binding_codes = {
        item["source_handle"]: item["code"] for item in bindings
    }
    operators = operator_table()
    operator_codes = {item["name"]: item["code"] for item in operators}
    step_indexes = {
        step["id"]: index for index, step in enumerate(plan["steps"])
    }
    steps: list[dict[str, Any]] = []
    for step_index, step in enumerate(plan["steps"]):
        operator = operators[operator_codes[step["operator"]]]
        source_refs: list[dict[str, Any]] = []
        for input_slot in operator["input_slots"]:
            binding = step["args"].get(input_slot["name"])
            if binding is None:
                if input_slot["required"]:
                    raise StructuredSourceError(
                        "trusted_plan_missing_required_input"
                    )
                source_refs.append(_omit_ref())
                continue
            if binding["kind"] == "step_output":
                source_step = step_indexes.get(binding["step_id"])
                if source_step is None or source_step >= step_index:
                    raise StructuredSourceError(
                        "trusted_plan_step_reference_invalid"
                    )
                source_operator = operators[
                    operator_codes[plan["steps"][source_step]["operator"]]
                ]
                output_names = {
                    output["name"]
                    for output in source_operator["output_slots"]
                }
                if binding["output"] not in output_names:
                    raise StructuredSourceError(
                        "trusted_plan_output_invalid"
                    )
                source_refs.append(
                    _prior_ref(source_step, binding["output"])
                )
            else:
                handle = _binding_source(binding)
                if handle not in binding_codes:
                    raise StructuredSourceError(
                        "trusted_plan_binding_not_grounded"
                    )
                source_refs.append(_binding_ref(binding_codes[handle]))
        steps.append(
            {
                "operator_code": operator["code"],
                "source_refs": source_refs,
            }
        )
    program = {
        "version_code": PLAN_PROGRAM_VERSION_CODE,
        "operator_note": operator_note,
        "goal_code": shared.GOALS.index(plan["goal"]),
        "steps": steps,
    }
    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    return program


def _decode_source_ref(
    *,
    source_ref: dict[str, Any],
    input_slot: dict[str, Any],
    step_index: int,
    path: str,
    bindings: list[dict[str, Any]],
    operators: list[dict[str, Any]],
    program: dict[str, Any],
) -> tuple[str, str] | None:
    kind = source_ref["kind"]
    binding_code = source_ref["binding_code"]
    prior_step_index = source_ref["prior_step_index"]
    prior_output_name = source_ref["prior_output_name"]

    if kind == "omit":
        if (
            binding_code != -1
            or prior_step_index != -1
            or prior_output_name != "none"
        ):
            raise StructuredSourceError("omit_sentinel_invalid:" + path)
        if input_slot["required"]:
            raise StructuredSourceError("required_source_omitted:" + path)
        return None

    if kind == "binding":
        if prior_step_index != -1 or prior_output_name != "none":
            raise StructuredSourceError("binding_sentinel_invalid:" + path)
        if binding_code < 0 or binding_code >= len(bindings):
            raise StructuredSourceError("external_binding_invalid:" + path)
        source = bindings[binding_code]
        return source["semantic_type"], source["source_handle"]

    if kind == "prior_output":
        if binding_code != -1 or prior_output_name == "none":
            raise StructuredSourceError(
                "prior_output_sentinel_invalid:" + path
            )
        if prior_step_index < 0 or prior_step_index >= step_index:
            raise StructuredSourceError("forward_or_self_reference:" + path)
        source_operator_code = program["steps"][prior_step_index][
            "operator_code"
        ]
        source_operator = operators[source_operator_code]
        output = next(
            (
                candidate
                for candidate in source_operator["output_slots"]
                if candidate["name"] == prior_output_name
            ),
            None,
        )
        if output is None:
            raise StructuredSourceError("output_name_invalid:" + path)
        return (
            output["semantic_type"],
            (
                "step:"
                f"step-p{prior_step_index + 1:02d}:"
                f"{prior_output_name}"
            ),
        )

    raise StructuredSourceError("source_kind_invalid:" + path)


def compile_program(
    frame: dict[str, Any],
    program: dict[str, Any],
) -> dict[str, Any]:
    """Mechanically decode v3; never infer or repair a source."""

    _require_frame_boundary(frame)
    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    bindings = binding_table(frame)
    operators = operator_table()
    candidate_steps: list[dict[str, Any]] = []
    for step_index, encoded_step in enumerate(program["steps"]):
        operator = operators[encoded_step["operator_code"]]
        sources = encoded_step["source_refs"]
        inputs = operator["input_slots"]
        if len(sources) != len(inputs):
            raise StructuredSourceError(
                f"operator_arity_invalid:$.steps[{step_index}].source_refs"
            )
        arguments: list[dict[str, str]] = []
        for source_position, (source_ref, input_slot) in enumerate(
            zip(sources, inputs, strict=True)
        ):
            path = f"$.steps[{step_index}].source_refs[{source_position}]"
            decoded = _decode_source_ref(
                source_ref=source_ref,
                input_slot=input_slot,
                step_index=step_index,
                path=path,
                bindings=bindings,
                operators=operators,
                program=program,
            )
            if decoded is None:
                continue
            source_type, source_handle = decoded
            if source_type != input_slot["semantic_type"]:
                raise StructuredSourceError("source_type_mismatch:" + path)
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
        "goal": shared.GOALS[program["goal_code"]],
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
    """Run the v3 form gate followed by the unchanged semantic proofreader."""

    note_review = review_operator_note(
        frame,
        program.get("operator_note") if isinstance(program, dict) else None,
    )
    if note_review["disposition"] != "admit":
        review = {
            "disposition": "edge_abort",
            "attempt": attempt,
            "revision_allowed": False,
            "safe_repairs": [],
            "violations": [
                {"path": "$.operator_note", "code": code}
                for code in note_review["reason_codes"]
            ],
            "admitted_operator_ids": [],
            "reviewed_context_revision": frame.get("context_revision"),
        }
        return review, None, None, note_review
    try:
        validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
        candidate = compile_program(frame, program)
        review, normalized, _ = legacy_lane.proofread_candidate(
            frame, candidate, attempt=attempt
        )
    except (
        StructuredSourceError,
        legacy_lane.ModelLaneError,
        ValueError,
    ) as error:
        code = str(error).split(":", 1)[0]
        review = {
            "disposition": "edge_abort",
            "attempt": attempt,
            "revision_allowed": False,
            "safe_repairs": [],
            "violations": [{"path": "$.steps", "code": code}],
            "admitted_operator_ids": [],
            "reviewed_context_revision": frame.get("context_revision"),
        }
        return review, None, None, note_review
    return review, normalized, candidate, note_review


def parse_vertex_program(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise StructuredSourceError("provider_candidate_count_invalid")
    content = candidates[0].get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise StructuredSourceError("provider_content_invalid")
    text = parts[0].get("text") if isinstance(parts[0], dict) else None
    if not isinstance(text, str):
        raise StructuredSourceError("provider_text_missing")
    if len(text.encode("utf-8")) > 32768:
        raise StructuredSourceError("provider_text_oversized")
    try:
        program = json.loads(text)
    except json.JSONDecodeError as error:
        raise StructuredSourceError("provider_text_not_json") from error
    if not isinstance(program, dict):
        raise StructuredSourceError("provider_program_not_object")
    validate_exact(program, PLAN_PROGRAM_SCHEMA_PATH)
    return program, shared._usage(packet)


def build_provider_blocked_evidence() -> dict[str, Any]:
    """Run every supported authored-synthetic case without provider access."""

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
            raise StructuredSourceError(
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
        case
        for case in document["cases"]
        if case["case_id"] == "known-move"
    )
    move_frame = typed_plan.expand_case(document, move_case)
    model_input = build_model_input(move_frame)
    provider_request = build_vertex_request(model_input)
    return {
        "schema_version": (
            "reception.one.structured_source.provider_blocked_evidence.v1"
        ),
        "result": (
            "reception_one_structured_source_language_provider_blocked_pass"
        ),
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "contract": {
            "model_input_version": MODEL_INPUT_VERSION,
            "plan_program_version_code": PLAN_PROGRAM_VERSION_CODE,
            "goal_code_count": len(shared.GOALS),
            "operator_code_count": len(operator_table()),
            "output_name_count": len(OUTPUT_NAMES),
            "source_kinds": ["binding", "prior_output", "omit"],
            "arithmetic_prior_output_codes": False,
            "provider_response_schema_sha256": canonical_hash(
                vertex_response_schema()
            ),
            "model_input_sha256": canonical_hash(model_input),
            "provider_request_sha256": canonical_hash(provider_request),
            "free_form_plan_identifiers": False,
            "semantic_safe_repairs": False,
        },
        "operator_note_policy": {
            "maximum_utf8_bytes": shared.NOTE_MAX_BYTES,
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
            "binding_sentinel_invalid",
            "prior_output_sentinel_invalid",
            "omit_sentinel_invalid",
            "required_source_omitted",
            "forward_or_self_reference",
            "output_name_invalid",
            "source_type_mismatch",
            "external_binding_invalid",
            "note_rejected",
            "legacy_arithmetic_program_schema_invalid",
        ],
        "boundary": {
            "api_key_authentication_used": False,
            "provider_tools": False,
            "function_calling": False,
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
    "CONTRACT_MODE",
    "MODEL_INPUT_SCHEMA_PATH",
    "MODEL_INPUT_VERSION",
    "OUTPUT_NAMES",
    "PLAN_PROGRAM_SCHEMA_PATH",
    "PLAN_PROGRAM_VERSION_CODE",
    "PROTOCOL_VERSION",
    "PROVIDER_BLOCKED_EVIDENCE_PATH",
    "StructuredSourceError",
    "audit_typed_program",
    "binding_table",
    "build_model_input",
    "build_provider_blocked_evidence",
    "build_vertex_request",
    "canonical_hash",
    "compile_program",
    "operator_table",
    "parse_vertex_program",
    "program_from_plan",
    "proofread_program",
    "review_operator_note",
    "source_reference_contract",
    "validate_exact",
    "vertex_response_schema",
]
