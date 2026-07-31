#!/usr/bin/env python3
"""Provider-blocked model adapter for Reception One's typed plan protocol."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_typed_plan_protocol as typed_plan


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-model-text-lane"
)
INPUT_SCHEMA_PATH = ARTIFACT_DIR / "model-input.schema.json"
CANDIDATE_SCHEMA_PATH = ARTIFACT_DIR / "model-plan-candidate.schema.json"
WIRE_SCHEMA_PATH = ARTIFACT_DIR / "provider-wire-response.schema.json"
FIXTURE_PATH = ARTIFACT_DIR / "model-output-fixture.json"
PROFILE_PATH = ARTIFACT_DIR / "provider-profile.json"
EVIDENCE_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"

CONTRACT_VERSION = "reception.one.bureau.model-plan-candidate.v1"
MODEL_INPUT_VERSION = "reception.one.bureau.model-input.v1"
MODEL = "gemini-2.5-flash"
LOCATION = "australia-southeast1"
HOSTNAME = "australia-southeast1-aiplatform.googleapis.com"
MAX_PROVIDER_TEXT_BYTES = 32768
ALLOWED_GOALS = (
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "squeeze_in_assessment",
    "clarification",
)

SYSTEM_INSTRUCTION = (
    "You are the untrusted plan composer inside Reception One. Return exactly "
    "one JSON object matching the supplied response schema. Compose only from "
    "the supplied operators and source handles. For an external argument use "
    "one exact available_bindings string. For an earlier step output use "
    "step:<step-id>:<output-name>. Use unique step-* ids, exact operator input "
    "names, every required input, no undeclared input, and only earlier typed "
    "outputs. Never invent a literal, "
    "identity, operator, completed action, write, confirmation, tool call or "
    "authority. Preserve proposal_only. If a safe composition is unavailable, "
    "use request_clarification. The deterministic proofreader, not you, decides "
    "whether anything is admitted."
    " The goal must be exactly one of: create, move, resize, cancel, "
    "status_change, squeeze_in_assessment, clarification."
    " Apply this closed vocabulary literally: book or create maps to create; "
    "move, reschedule or rebook maps to move; extend, shorten or change "
    "duration maps to resize; cancel maps to cancel; mark or change status "
    "maps to status_change; squeeze in without moving an existing appointment "
    "maps to squeeze_in_assessment. Never output reschedule, rebook, "
    "move_appointment or another synonym as the goal."
    " Return plan_lines in this exact grammar: "
    "step-id|operator|argument-name=source,argument-name=source. Use an empty "
    "third segment only for a zero-input operator. Each source is either one "
    "exact available_bindings value or step:<earlier-step-id>:<output-name>."
    " A prior-step source must contain exactly three colon-separated segments "
    "and must literally start with step:. Example: "
    "step-schedule|read_practitioner_schedule|practitioner="
    "step:step-practitioner:practitioner,date=step:step-date:date. Never use "
    "step-id:output, dot notation, an output label by itself, or omit the "
    "literal step: prefix."
)


class ModelLaneError(ValueError):
    """A bounded candidate or provider-contract rejection."""


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ModelLaneError("json_object_required")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_json(value).encode("utf-8")
    ).hexdigest()


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
        raise ModelLaneError("schema_invalid:" + ",".join(paths[:20]))


def _grounded_binding_handles(frame: dict[str, Any]) -> list[str]:
    handles: list[str] = []
    for entity in ("patient", "practitioner", "status"):
        try:
            typed_plan.mention_binding(frame, entity)
        except ValueError:
            continue
        handles.append(f"binding:{entity}")
    extraction = typed_plan.extraction_for(frame)
    for field in (
        "appointment_date",
        "earliest_time",
        "latest_time",
        "duration_minutes",
    ):
        if typed_plan.semantic_value(extraction, field) is not None:
            handles.append(f"binding:{field}")
    for field in (
        "selected_appointment",
        "squeeze_policy",
        "default_duration_minutes",
    ):
        if frame.get("context", {}).get(field) is not None:
            handles.append(f"binding:{field}")
    return sorted(handles)


def build_model_input(frame: dict[str, Any]) -> dict[str, Any]:
    typed_plan.validate_schema(frame, "input")
    if frame["data_class"] != "authored_synthetic":
        raise ModelLaneError("data_class_not_admitted")
    if frame["authority"] != {
        "effect_ceiling": "proposal_only",
        "appointment_write_authority": False,
        "confirmation_authority": False,
        "provider_execution": False,
        "network_access": False,
        "database_access": False,
        "product_delivery": False,
    }:
        raise ModelLaneError("authority_boundary_open")
    catalog = typed_plan.load_json(typed_plan.CATALOG_PATH)
    operators = []
    for operator in catalog["operators"]:
        operators.append(
            {
                "id": operator["id"],
                "effect": operator["effect"],
                "inputs": [
                    {
                        "name": item["name"],
                        "type": item["type"],
                        "required": item["required"],
                    }
                    for item in operator["inputs"]
                ],
                "outputs": [
                    {"name": item["name"], "type": item["type"]}
                    for item in operator["outputs"]
                ],
            }
        )
    result = {
        "contract_version": MODEL_INPUT_VERSION,
        "data_class": "authored_synthetic",
        "utterances": copy.deepcopy(frame["utterances"]),
        "effect_ceiling": "proposal_only",
        "available_bindings": _grounded_binding_handles(frame),
        "operator_catalog": operators,
    }
    validate_exact(result, INPUT_SCHEMA_PATH)
    return result


def vertex_response_schema() -> dict[str, Any]:
    """Return a low-state Vertex schema; the decoded candidate is stricter."""

    return {
        "type": "OBJECT",
        "required": ["goal", "plan_lines"],
        "properties": {
            "goal": {"type": "STRING"},
            "plan_lines": {
                "type": "ARRAY",
                "minItems": 1,
                "maxItems": 12,
                "items": {"type": "STRING", "maxLength": 512},
            },
        },
    }


def build_vertex_request(model_input: dict[str, Any]) -> dict[str, Any]:
    validate_exact(model_input, INPUT_SCHEMA_PATH)
    request = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": canonical_json(model_input)}],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 1024,
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
        raise ModelLaneError("provider_request_forbidden_surface")
    return request


def _source_binding(frame: dict[str, Any], source: str) -> dict[str, Any]:
    if source.startswith("step:"):
        parts = source.split(":")
        if len(parts) != 3:
            raise ModelLaneError("source_handle_invalid")
        return typed_plan.step_binding(parts[1], parts[2])
    if not source.startswith("binding:"):
        raise ModelLaneError("source_handle_invalid")
    field = source.removeprefix("binding:")
    if field in {"patient", "practitioner", "status"}:
        return typed_plan.mention_binding(frame, field)
    if field in {
        "appointment_date",
        "earliest_time",
        "latest_time",
        "duration_minutes",
    }:
        return typed_plan.semantic_binding(field)
    if field in {
        "selected_appointment",
        "squeeze_policy",
        "default_duration_minutes",
    }:
        return typed_plan.context_binding(field)
    raise ModelLaneError("source_handle_not_allowlisted")


def adapt_candidate(
    frame: dict[str, Any],
    candidate: dict[str, Any],
    *,
    attempt: int = 1,
) -> dict[str, Any]:
    validate_exact(candidate, CANDIDATE_SCHEMA_PATH)
    allowed = set(_grounded_binding_handles(frame))
    plan = typed_plan.base_plan(
        frame,
        planner_class="untrusted_model_candidate",
        goal=candidate["goal"],
        attempt=attempt,
    )
    for step in candidate["steps"]:
        args: dict[str, dict[str, Any]] = {}
        for argument in step["arguments"]:
            name = argument["name"]
            source = argument["source"]
            if name in args:
                raise ModelLaneError("duplicate_argument")
            if source.startswith("binding:") and source not in allowed:
                raise ModelLaneError("source_handle_not_grounded")
            args[name] = _source_binding(frame, source)
        plan["steps"].append(
            {
                "id": step["id"],
                "operator": step["operator"],
                "args": args,
            }
        )
    typed_plan.validate_schema(plan, "plan")
    return plan


def candidate_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    steps = []
    for step in plan["steps"]:
        arguments = []
        for name, binding in step["args"].items():
            kind = binding["kind"]
            if kind == "utterance_ref":
                source = f"binding:{binding['entity_type']}"
            elif kind in {"semantic_ref", "context_ref"}:
                source = f"binding:{binding['field']}"
            elif kind == "step_output":
                source = f"step:{binding['step_id']}:{binding['output']}"
            else:
                raise ModelLaneError("binding_kind_not_exportable")
            arguments.append({"name": name, "source": source})
        steps.append(
            {
                "id": step["id"],
                "operator": step["operator"],
                "arguments": arguments,
            }
        )
    candidate = {
        "contract_version": CONTRACT_VERSION,
        "goal": plan["goal"],
        "steps": steps,
    }
    validate_exact(candidate, CANDIDATE_SCHEMA_PATH)
    return candidate


def candidate_to_wire(candidate: dict[str, Any]) -> dict[str, Any]:
    validate_exact(candidate, CANDIDATE_SCHEMA_PATH)
    lines = []
    for step in candidate["steps"]:
        arguments = ",".join(
            f"{item['name']}={item['source']}" for item in step["arguments"]
        )
        lines.append(f"{step['id']}|{step['operator']}|{arguments}")
    wire = {"goal": candidate["goal"], "plan_lines": lines}
    validate_exact(wire, WIRE_SCHEMA_PATH)
    return wire


def normalize_provider_wire(
    wire: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    """Apply only authorised casing and separator-whitespace normalization."""

    normalized = copy.deepcopy(wire)
    repairs: list[dict[str, str]] = []
    goal = normalized.get("goal")
    if isinstance(goal, str):
        canonical_goal = goal.strip().casefold()
        if canonical_goal != goal:
            repairs.append(
                {"path": "$.goal", "code": "canonical_enum_casing_or_whitespace"}
            )
        normalized["goal"] = canonical_goal
    lines = normalized.get("plan_lines")
    if isinstance(lines, list):
        normalized_lines: list[Any] = []
        for index, line in enumerate(lines):
            if not isinstance(line, str):
                normalized_lines.append(line)
                continue
            stripped = line.strip()
            parts = stripped.split("|")
            if len(parts) == 3:
                step_id, operator, raw_arguments = (part.strip() for part in parts)
                arguments: list[str] = []
                if raw_arguments:
                    for raw_argument in raw_arguments.split(","):
                        argument = raw_argument.strip()
                        if argument.count("=") == 1:
                            name, source = argument.split("=", 1)
                            argument = f"{name.strip()}={source.strip()}"
                        arguments.append(argument)
                canonical_line = (
                    f"{step_id}|{operator}|{','.join(arguments)}"
                )
            else:
                canonical_line = stripped
            if canonical_line != line:
                repairs.append(
                    {
                        "path": f"$.plan_lines[{index}]",
                        "code": "separator_whitespace",
                    }
                )
            normalized_lines.append(canonical_line)
        normalized["plan_lines"] = normalized_lines
    validate_exact(normalized, WIRE_SCHEMA_PATH)
    if normalized.get("goal") not in ALLOWED_GOALS:
        raise ModelLaneError("goal_not_allowlisted")
    return normalized, repairs


def wire_to_candidate(wire: dict[str, Any]) -> dict[str, Any]:
    validate_exact(wire, WIRE_SCHEMA_PATH)
    steps = []
    for line in wire["plan_lines"]:
        parts = line.split("|")
        if len(parts) != 3:
            raise ModelLaneError("wire_line_invalid")
        step_id, operator, raw_arguments = parts
        arguments = []
        if raw_arguments:
            for raw_argument in raw_arguments.split(","):
                if raw_argument.count("=") != 1:
                    raise ModelLaneError("wire_argument_invalid")
                name, source = raw_argument.split("=", 1)
                arguments.append({"name": name, "source": source})
        steps.append(
            {
                "id": step_id,
                "operator": operator,
                "arguments": arguments,
            }
        )
    candidate = {
        "contract_version": CONTRACT_VERSION,
        "goal": wire["goal"],
        "steps": steps,
    }
    validate_exact(candidate, CANDIDATE_SCHEMA_PATH)
    return candidate


def proofread_candidate(
    frame: dict[str, Any],
    candidate: dict[str, Any],
    *,
    attempt: int = 1,
    now: datetime | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    plan = adapt_candidate(frame, candidate, attempt=attempt)
    review, normalized = (
        typed_plan.proofread_plan(frame, plan, now=now)
        if now is not None
        else typed_plan.proofread_plan(frame, plan)
    )
    return review, normalized, plan


def safe_revision_feedback(review: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_version": "reception.one.bureau.model-revision-feedback.v1",
        "attempt": review["attempt"],
        "revision_allowed": review["revision_allowed"],
        "violations": [
            {"path": item["path"], "code": item["code"]}
            for item in review["violations"][:20]
        ],
    }


def parse_vertex_candidate(packet: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    candidate, usage, _ = parse_vertex_candidate_with_repairs(packet)
    return candidate, usage


def parse_vertex_candidate_with_repairs(
    packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int], list[dict[str, str]]]:
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise ModelLaneError("provider_candidate_count_invalid")
    content = candidates[0].get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise ModelLaneError("provider_content_invalid")
    text = parts[0].get("text") if isinstance(parts[0], dict) else None
    if not isinstance(text, str):
        raise ModelLaneError("provider_text_missing")
    encoded = text.encode("utf-8")
    if len(encoded) > MAX_PROVIDER_TEXT_BYTES:
        raise ModelLaneError("provider_text_oversized")
    try:
        wire = json.loads(text)
    except json.JSONDecodeError as error:
        raise ModelLaneError("provider_text_not_json") from error
    if not isinstance(wire, dict):
        raise ModelLaneError("provider_candidate_not_object")
    normalized_wire, wire_safe_repairs = normalize_provider_wire(wire)
    candidate = wire_to_candidate(normalized_wire)
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
    return candidate, usage, wire_safe_repairs


def _positive_cases() -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    cases_document = typed_plan.load_json(typed_plan.CASES_PATH)
    known_case_ids = (
        "known-create",
        "known-move",
        "known-resize",
        "known-cancel",
    )
    known_cases = [
        next(
            item
            for item in cases_document["cases"]
            if item["case_id"] == case_id
        )
        for case_id in known_case_ids
    ]
    squeeze_case = next(
        item
        for item in cases_document["cases"]
        if item["case_id"] == "novel-squeeze-in"
    )
    squeeze_frame = typed_plan.expand_case(cases_document, squeeze_case)
    squeeze_candidate = load_object(FIXTURE_PATH)
    positives = []
    for case in known_cases:
        frame = typed_plan.expand_case(cases_document, case)
        positives.append(
            (
                case["case_id"],
                frame,
                candidate_from_plan(typed_plan.deterministic_plan(frame)),
            )
        )
    positives.append(("novel-squeeze-in", squeeze_frame, squeeze_candidate))
    return positives


def _negative_candidates(
    candidate: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    cases: list[tuple[str, dict[str, Any]]] = []

    unknown = copy.deepcopy(candidate)
    unknown["steps"][-1]["operator"] = "confirm_appointment"
    cases.append(("unknown-write-operator", unknown))

    literal = copy.deepcopy(candidate)
    literal["steps"][-1]["arguments"][-1]["source"] = "literal:15"
    cases.append(("free-literal", literal))

    forward = copy.deepcopy(candidate)
    forward["steps"][0]["arguments"][0]["source"] = "step:step-later:patient"
    cases.append(("forward-reference", forward))

    forged = copy.deepcopy(candidate)
    forged["project"] = "different-project"
    cases.append(("forged-scope-field", forged))

    too_many = copy.deepcopy(candidate)
    too_many["steps"] = [
        {
            "id": f"step-extra-{index}",
            "operator": "request_clarification",
            "arguments": [],
        }
        for index in range(13)
    ]
    cases.append(("step-budget", too_many))

    duplicate = copy.deepcopy(candidate)
    duplicate["steps"][0]["arguments"].append(
        copy.deepcopy(duplicate["steps"][0]["arguments"][0])
    )
    cases.append(("duplicate-argument", duplicate))
    return cases


def build_provider_blocked_evidence() -> dict[str, Any]:
    positives = []
    for case_id, frame, candidate in _positive_cases():
        model_input = build_model_input(frame)
        provider_request = build_vertex_request(model_input)
        review, normalized, _ = proofread_candidate(frame, candidate)
        if review["disposition"] != "admit":
            raise ModelLaneError(f"positive_case_not_admitted:{case_id}")
        execution = typed_plan.execute_plan(frame, normalized, review)
        positives.append(
            {
                "case_id": case_id,
                "model_input_sha256": canonical_hash(model_input),
                "provider_request_sha256": canonical_hash(provider_request),
                "candidate_sha256": canonical_hash(candidate),
                "plan_sha256": canonical_hash(normalized),
                "review_disposition": review["disposition"],
                "execution_disposition": execution["status"],
                "effect_ceiling": review["effect_ceiling"],
                "write_performed": execution["boundary"]["write_performed"],
            }
        )

    fixture = load_object(FIXTURE_PATH)
    squeeze_frame = _positive_cases()[-1][1]
    negatives = []
    for case_id, candidate in _negative_candidates(fixture):
        reason = "unexpected_admission"
        try:
            review, _, _ = proofread_candidate(squeeze_frame, candidate)
            reason = review["disposition"]
            if reason == "admit":
                raise ModelLaneError(f"negative_case_admitted:{case_id}")
        except ModelLaneError as error:
            reason = str(error).split(":", 1)[0]
        negatives.append({"case_id": case_id, "disposition": reason})

    revision = copy.deepcopy(fixture)
    revision["steps"][-1]["arguments"] = revision["steps"][-1]["arguments"][:-1]
    revision_review, _, _ = proofread_candidate(squeeze_frame, revision)
    feedback = safe_revision_feedback(revision_review)
    if revision_review["disposition"] != "revision_required":
        raise ModelLaneError("bounded_revision_not_requested")
    repaired_review, _, _ = proofread_candidate(
        squeeze_frame, fixture, attempt=2
    )
    if repaired_review["disposition"] != "admit":
        raise ModelLaneError("bounded_revision_not_admitted")

    profile = load_object(PROFILE_PATH)
    return {
        "schema_version": "reception.one.bureau.model_text_lane_evidence.v1",
        "result": "reception_one_bureau_model_text_lane_provider_blocked_pass",
        "evidence_mode": "authored_synthetic_provider_blocked",
        "provider_profile_sha256": canonical_hash(profile),
        "provider": profile["provider"],
        "model": profile["model"],
        "location": profile["location"],
        "endpoint_hostname": profile["endpoint_hostname"],
        "positive_cases": positives,
        "negative_cases": negatives,
        "bounded_revision": {
            "first_disposition": revision_review["disposition"],
            "feedback_sha256": canonical_hash(feedback),
            "feedback_fields": sorted(feedback),
            "second_attempt": 2,
            "second_disposition": repaired_review["disposition"],
        },
        "provider_request_contract": {
            "structured_json": True,
            "temperature": 0,
            "max_output_tokens": 1024,
            "thinking_budget": 0,
            "candidate_count_sent": False,
            "tools_sent": False,
            "function_calling_sent": False,
            "grounding_sent": False,
            "retrieval_sent": False,
            "cache_reference_sent": False,
            "global_endpoint": False,
            "automatic_fallback": False,
        },
        "boundary": {
            "provider_calls_performed": 0,
            "credential_reads_performed": 0,
            "api_key_authentication_used": False,
            "network_access_performed": False,
            "database_access_performed": False,
            "product_data_used": False,
            "historical_diary_material_access_performed": False,
            "appointment_writes_performed": 0,
            "confirmation_performed": False,
            "product_delivery_performed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-evidence", action="store_true")
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args()
    try:
        evidence = build_provider_blocked_evidence()
    except (OSError, json.JSONDecodeError, ModelLaneError, ValueError) as error:
        print(
            json.dumps(
                {
                    "status": "revision_required",
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    if args.write_evidence:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
