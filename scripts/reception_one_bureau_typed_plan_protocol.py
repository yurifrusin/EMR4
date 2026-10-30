#!/usr/bin/env python3
"""Provider-free verifier for Reception One's bounded typed plan language."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from datetime import date
from dataclasses import dataclass
from types import MappingProxyType
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.semantic_extraction import SemanticExtraction, extract_semantics


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-typed-plan-protocol"
)
CATALOG_PATH = ARTIFACT_DIR / "operator-catalog.json"
CASES_PATH = ARTIFACT_DIR / "authored-synthetic-cases.json"
SCHEMA_PATHS = {
    "catalog": ARTIFACT_DIR / "operator-catalog.schema.json",
    "input": ARTIFACT_DIR / "input-frame.schema.json",
    "plan": ARTIFACT_DIR / "plan-draft.schema.json",
    "packet": ARTIFACT_DIR / "plan-draft.schema.json",
    "review": ARTIFACT_DIR / "plan-review.schema.json",
    "execution": ARTIFACT_DIR / "execution-result.schema.json",
}
EVIDENCE_NOW = datetime(2026, 7, 29, 0, 30, tzinfo=timezone.utc)
ALLOWED_EFFECTS = {"pure", "authorised_read", "proposal_only"}
SEMANTIC_TYPES = {
    "appointment_date": "date",
    "earliest_time": "time",
    "latest_time": "time",
    "target_start_local": "time",
    "duration_minutes": "integer",
    "intended_action": "action",
}
CONTEXT_TYPES = {
    "selected_appointment": "appointment_ref",
    "squeeze_policy": "squeeze_policy_ref",
    "default_duration_minutes": "integer",
}
ACTION_GOALS = {
    "create": "create",
    "move": "move",
    "resize": "resize",
    "cancel": "cancel",
    "status_change": "status_change",
}
PROPOSAL_OPERATIONS = {
    "create": "proposeAppointmentCreate",
    "move": "proposeAppointmentUpdate",
    "resize": "proposeAppointmentUpdate",
    "cancel": "proposeAppointmentDelete",
    "status_change": "proposeAppointmentStatus",
}
SELECTED_PROPOSAL_FAMILIES = {
    "prepare_move_proposal": "move",
    "prepare_point_move_proposal": "move",
    "prepare_resize_proposal": "resize",
    "prepare_cancel_proposal": "cancel",
    "prepare_status_proposal": "status_change",
}
BOUNDARY = {
    "write_performed": False,
    "confirmation_performed": False,
    "provider_calls": 0,
    "network_access": False,
    "database_access": False,
    "product_delivery": False,
}
CHECK_NAMES = (
    "schema_exact",
    "scope_bound",
    "context_revision_current",
    "authored_synthetic",
    "catalogue_bound",
    "step_budget_bounded",
    "unique_step_ids",
    "operators_known",
    "topological_order",
    "signatures_exact",
    "binding_types_exact",
    "bindings_grounded",
    "effect_ceiling_preserved",
    "semantic_action_consistent",
    "authority_boundary_closed",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def schema_error_paths(value: Any, schema: dict[str, Any]) -> list[str]:
    if schema.get("$id") == "https://emr4.invalid/schemas/reception-one-bureau-plan-draft-dispatch.v1.json":
        # Closed discriminator also preserves legacy per-field error paths.
        version = value.get("contract_version") if isinstance(value, dict) else None
        branch = {"reception.one.bureau.plan-draft.v1": "legacyPlan",
                  "reception.one.bureau.plan-draft.model-first.v1": "modelFirstPlan",
                  "reception.one.bureau.plan-draft.model-first.point.v2": "pointModelPlan"}.get(version)
        if branch is not None:
            schema = {**schema["$defs"][branch], "$defs": schema["$defs"]}
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    paths = []
    for error in validator.iter_errors(value):
        path = "$"
        for part in error.absolute_path:
            if isinstance(part, int):
                path += f"[{part}]"
            else:
                path += f".{part}"
        paths.append(path)
    return sorted(set(paths))


def validate_schema(value: Any, schema_name: str) -> None:
    schema = load_json(SCHEMA_PATHS[schema_name])
    if schema_name == "packet":
        # Lookup only: adding this definition never admits a packet as a plan.
        branch = "semanticPacketV3" if isinstance(value, dict) and value.get("packet_schema") == POINT_PACKET_VERSION else "semanticPacket"
        schema = {"$schema": schema["$schema"], "$ref": "#/$defs/" + branch, "$defs": schema["$defs"]}
    failures = schema_error_paths(value, schema)
    if failures:
        raise ValueError(f"{schema_name} schema failed at {failures}")


def operator_map(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    validate_schema(catalog, "catalog")
    operators = catalog["operators"]
    result = {operator["id"]: operator for operator in operators}
    if len(result) != len(operators):
        raise ValueError("operator identifiers must be unique")
    for operator in operators:
        input_names = [field["name"] for field in operator["inputs"]]
        output_names = [field["name"] for field in operator["outputs"]]
        if len(set(input_names)) != len(input_names):
            raise ValueError(f"duplicate input name for {operator['id']}")
        if len(set(output_names)) != len(output_names):
            raise ValueError(f"duplicate output name for {operator['id']}")
        if operator["effect"] not in ALLOWED_EFFECTS:
            raise ValueError(f"forbidden effect for {operator['id']}")
    return result


def expand_case(cases_document: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    frame = copy.deepcopy(cases_document["shared_input"])
    frame["request_id"] = case["request_id"]
    frame["correlation_id"] = case["correlation_id"]
    frame["utterances"] = copy.deepcopy(case["utterances"])
    validate_schema(frame, "input")
    return frame


def extraction_for(frame: dict[str, Any]) -> SemanticExtraction:
    return extract_semantics(frame["utterances"], frame["reference_date"])


LEGACY_PLAN_VERSION = "reception.one.bureau.plan-draft.v1"
MODEL_PLAN_VERSION = "reception.one.bureau.plan-draft.model-first.v1"
POINT_PLAN_VERSION = "reception.one.bureau.plan-draft.model-first.point.v2"
POINT_PACKET_VERSION = "emr4.bureau_model_semantic_packet.v3"
POINT_CONSTRUCTOR_VERSION = "emr4.bureau_model_semantic_constructor.point.v3"


@dataclass(frozen=True)
class ValidatedModelIntent:
    """Untrusted proposed meaning, structurally bound to one immutable frame.

    Valid evidence proves origin, not that a proposed meaning is correct.
    Calendar dates and HH:MM values are practice-local; no zone is inferred.
    """
    intended_action: str
    normalized_values: Any


def validated_model_intent(frame: dict[str, Any], plan: dict[str, Any]) -> ValidatedModelIntent:
    """Validate the closed model contract without regex semantic extraction."""
    validate_schema(plan, "plan")
    if plan.get("contract_version") not in {MODEL_PLAN_VERSION, POINT_PLAN_VERSION}:
        raise ValueError("model contract required")
    intent = plan["interpretation"]
    if (intent["frame_sha256"] != canonical_sha256(frame)
            or type(intent["context_revision"]) is not int
            or intent["context_revision"] != frame["context_revision"]
            or intent["reference_date"] != frame["reference_date"]):
        raise ValueError("model frame binding refused")
    reference = intent["reference_date"]
    if date.fromisoformat(reference).isoformat() != reference:
        raise ValueError("model reference date refused")
    # JSON Schema accepts integer-valued floats; this boundary intentionally does not.
    for value in (plan["context_revision"], plan["attempt"], plan["revision_limit"],
                  frame["context_revision"]):
        if type(value) is not int:
            raise ValueError("strict integer required")
    candidates = intent["candidates"]
    by_id = {item["id"]: item for item in candidates}
    if len(by_id) != len(candidates):
        raise ValueError("duplicate model candidate")
    positions = {}
    for item in candidates:
        evidence = item["evidence"]
        index, start, end = (evidence[key] for key in ("utterance_index", "start", "end"))
        if (any(type(value) is not int for value in (index, start, end))
                or not 0 <= index < len(frame["utterances"])):
            raise ValueError("model evidence bounds refused")
        utterance = frame["utterances"][index]
        if not 0 <= start < end <= len(utterance) or utterance[start:end] != evidence["text"]:
            raise ValueError("model evidence substring refused")
        positions[item["id"]] = (index, end, start)
        field, value = item["field"], item["value"]
        if field == "duration_minutes":
            valid = type(value) is int and 5 <= value <= 180
        elif field == "appointment_date":
            valid = isinstance(value, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
            valid = valid and date.fromisoformat(value).isoformat() == value
        elif field in {"earliest_time", "latest_time", "target_start_local"}:
            valid = isinstance(value, str) and bool(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value))
        else:
            valid = field == "intended_action" and value in {
                "create", "move", "resize", "cancel", "status_change", "squeeze_in_assessment", "clarification"
            }
        if not valid:
            raise ValueError("model candidate value refused")
    selected = intent["selected"]
    fields = {item["field"] for item in candidates}
    if set(selected) != fields or "intended_action" not in selected:
        raise ValueError("model candidate choice incomplete")
    values = {}
    for field, winner_id in selected.items():
        if winner_id not in by_id or by_id[winner_id]["field"] != field:
            raise ValueError("model candidate choice refused")
        reached = set()
        pending = [winner_id]
        while pending:
            current = pending.pop()
            if current in reached:
                continue
            reached.add(current)
            item = by_id[current]
            for prior in item["supersedes"]:
                if (prior not in by_id or by_id[prior]["field"] != field
                        or positions[prior] >= positions[current]):
                    raise ValueError("model supersession refused")
                pending.append(prior)
        if reached != {item["id"] for item in candidates if item["field"] == field}:
            raise ValueError("competing model candidates unresolved")
        values[field] = by_id[winner_id]["value"]
    if values["intended_action"] != plan["goal"]:
        raise ValueError("model goal disagrees with chosen action")
    if ("earliest_time" in values and "latest_time" in values
            and values["earliest_time"] > values["latest_time"]):
        raise ValueError("model local time window refused")
    return ValidatedModelIntent(values["intended_action"], MappingProxyType(values))


def selected_model_patient(frame: dict[str, Any]) -> str | None:
    """Only this fixed selected-row link is exposed, never dotted traversal."""
    context = frame["context"]
    selected = context.get("selected_appointment")
    if not isinstance(selected, dict):
        return None
    patients = [row for row in context["patients"] if row["id"] == selected["patient_ref"]]
    practitioners = [row for row in context["practitioners"] if row["id"] == selected["practitioner_ref"]]
    if len(patients) != 1 or len(practitioners) != 1:
        return None
    return patients[0]["id"]


def model_plan_consistent(frame: dict[str, Any], plan: dict[str, Any], intent: ValidatedModelIntent | None) -> bool:
    if intent is None or plan.get("planner_class") != "untrusted_model_candidate":
        return False
    steps = plan.get("steps", [])
    if plan.get("contract_version") == POINT_PLAN_VERSION:
        selected = frame["context"].get("selected_appointment")
        if (not isinstance(selected, dict)
                or type(selected.get("duration_minutes")) is not int
                or not 1 <= selected["duration_minutes"] <= 480):
            return False
    if plan["goal"] == "clarification":
        return len(steps) == 1 and steps[0].get("operator") == "request_clarification"
    family_steps = [step for step in steps if step.get("operator") in SELECTED_PROPOSAL_FAMILIES]
    reads = [step for step in steps if step.get("operator") == "read_selected_appointment"]
    if plan["goal"] in SELECTED_PROPOSAL_FAMILIES.values() or family_steps or reads:
        if (len(family_steps) != 1 or steps[-1] is not family_steps[0]
                or SELECTED_PROPOSAL_FAMILIES[family_steps[0]["operator"]] != intent.intended_action
                or not reads or selected_model_patient(frame) is None):
            return False
        return all(step.get("args") == {
            "appointment": {"kind": "context_ref", "field": "selected_appointment"},
            "patient": {"kind": "context_ref", "field": "selected_appointment.patient_ref"},
        } for step in reads)
    # Other existing catalog operations retain signature/grounding/effect checks.
    final_operators = {"create": "prepare_create_proposal", "squeeze_in_assessment": "assess_squeeze_in_options"}
    return bool(steps) and steps[-1].get("operator") == final_operators.get(plan["goal"])


def model_dataflow_mismatches(plan: dict[str, Any], intent: ValidatedModelIntent) -> list[str]:
    """Closed catalog binding rules, not a second language interpreter.

    Chosen proposal values must actually govern the corresponding dataflow.
    Move deliberately preserves the selected row's practitioner and duration;
    those cannot simultaneously be presented as changed interpretation fields.
    """
    point = plan.get("contract_version") == POINT_PLAN_VERSION
    fields_by_goal = {
        "move": {"intended_action", "appointment_date", "earliest_time", "latest_time"},
        "resize": {"intended_action", "duration_minutes"},
        "cancel": {"intended_action"}, "status_change": {"intended_action"},
        "clarification": {"intended_action"},
        "create": {"intended_action", "appointment_date", "earliest_time", "latest_time", "duration_minutes"},
        "squeeze_in_assessment": {"intended_action", "appointment_date", "duration_minutes"},
    }
    if point:
        fields_by_goal["move"] = {"intended_action", "appointment_date", "target_start_local"}
    mismatches = []
    if point and (plan["goal"] != "move" or [step["operator"] for step in plan["steps"]] != ["read_selected_appointment", "prepare_point_move_proposal"]):
        mismatches.append("$.steps")
    if set(intent.normalized_values) != fields_by_goal[plan["goal"]]:
        mismatches.append("$.interpretation.selected")
    prior = {}

    def semantic(binding, field):
        if field not in intent.normalized_values:
            return False
        if binding == {"kind": "semantic_ref", "field": field}:
            return True
        # The existing date operator may pass the SAME chosen local date on.
        source = source_step(binding, "resolve_date_expression", "date") if field == "appointment_date" else None
        return source is not None and source["args"].get("date") == {"kind": "semantic_ref", "field": field}

    def source_step(binding, operator, output):
        if not isinstance(binding, dict) or set(binding) != {"kind", "step_id", "output"}:
            return None
        source = prior.get(binding["step_id"])
        return source if (binding["kind"] == "step_output" and binding["output"] == output
                          and source is not None and source["operator"] == operator) else None

    for index, step in enumerate(plan["steps"]):
        operator, args = step["operator"], step["args"]
        prefix = f"$.steps[{index}].args"

        def require_binding(name, valid):
            if not valid:
                mismatches.append(prefix + "." + name)

        if operator in {"resolve_date_expression", "read_practitioner_schedule"}:
            require_binding("date", semantic(args.get("date"), "appointment_date"))
        if operator == "search_available_slots":
            for name, field in (("date", "appointment_date"), ("earliest_time", "earliest_time"),
                                ("latest_time", "latest_time")):
                require_binding(name, semantic(args.get(name), field))
            if plan["goal"] == "move":
                require_binding("practitioner", source_step(args.get("practitioner"), "read_selected_appointment", "practitioner") is not None)
                require_binding("duration_minutes", source_step(args.get("duration_minutes"), "read_selected_appointment", "duration_minutes") is not None)
            else:
                require_binding("duration_minutes", semantic(args.get("duration_minutes"), "duration_minutes"))
        if operator in {"prepare_resize_proposal", "prepare_create_proposal", "assess_squeeze_in_options"}:
            require_binding("duration_minutes", semantic(args.get("duration_minutes"), "duration_minutes"))
        if operator in SELECTED_PROPOSAL_FAMILIES:
            require_binding("appointment", args.get("appointment") == {"kind": "context_ref", "field": "selected_appointment"}
                            or source_step(args.get("appointment"), "read_selected_appointment", "appointment") is not None)
        if operator == "prepare_point_move_proposal":
            require_binding("appointment", source_step(args.get("appointment"), "read_selected_appointment", "appointment") is not None)
            require_binding("date", args.get("date") == {"kind": "semantic_ref", "field": "appointment_date"})
            require_binding("target_start_local", args.get("target_start_local") == {"kind": "semantic_ref", "field": "target_start_local"})
            if not point:
                mismatches.append(prefix)
        if operator in {"prepare_move_proposal", "prepare_create_proposal"}:
            search = source_step(args.get("candidates"), "search_available_slots", "candidates")
            require_binding("candidates", search is not None)
            if operator == "prepare_create_proposal" and search is not None:
                require_binding("practitioner", args.get("practitioner") == search["args"].get("practitioner"))
        if operator == "assess_squeeze_in_options":
            require_binding("schedule", source_step(args.get("schedule"), "read_practitioner_schedule", "schedule") is not None)
        prior[step["id"]] = step
    return sorted(set(mismatches))


_SELECTED_MOVE_WORDS = re.compile(
    r"(?:please\s+)?(?:move|shift|reschedule)\s+"
    r"(?:this|the selected)\s+appointment\s+to\s+"
    r"(?P<date>[a-z0-9]+(?:\s+[a-z0-9]+){0,2})\s+at\s+"
    r"(?P<time>[a-z0-9:. ]+?)"
    r"(?:\s+please)?[.!?]?",
    re.I,
)


def _spoken_refs(frame: dict[str, Any], kind: str) -> set[str]:
    """Retain every known full-name match, including pre-selection matches."""
    rows = frame["context"]["patients" if kind == "patient" else "practitioners"]
    result: set[str] = set()
    for row in rows:
        terms = [row["display"]]
        if kind == "practitioner":
            terms.extend(alias for alias in row["aliases"] if alias.casefold().startswith("dr "))
        for term in terms:
            if any(
                re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", utterance, re.I)
                for utterance in frame["utterances"]
            ):
                result.add(row["id"])
                break
    return result


def _unresolved_person_cue(frame: dict[str, Any]) -> bool:
    """Fail closed on a remaining named or possessive person cue."""
    remaining = " ".join(frame["utterances"])
    terms = [
        row["display"]
        for row in frame["context"]["patients"]
    ] + [
        term
        for row in frame["context"]["practitioners"]
        for term in [row["display"], *row["aliases"]]
        if term.casefold().startswith("dr ")
    ]
    for term in sorted(set(terms), key=len, reverse=True):
        remaining = re.sub(
            r"(?<!\w)(?:(?:for|with|patient|doctor)\s+)?"
            + re.escape(term) + r"(?!\w)",
            " ",
            remaining,
            flags=re.I,
        )
    return bool(
        re.search(r"\b(?:for|with|patient|doctor|dr)\s+(?:dr\s+)?[a-z][a-z'-]*\b", remaining, re.I)
        or re.search(r"\b[a-z][a-z'-]*['’]s\s+(?:appointment|booking)\b", remaining, re.I)
    )


def selected_move_subject(frame: dict[str, Any], extraction: SemanticExtraction) -> str | None:
    """Classify only a uniquely grounded selected-row move subject."""
    selected = frame["context"].get("selected_appointment")
    if selected is None or extraction.intended_action != "move":
        return None
    if extraction.action_negated or extraction.requires_clarification or extraction.authority_claim != "read":
        return None
    if not extraction.normalized_values.get("appointment_date") or not extraction.normalized_values.get("earliest_time"):
        return None
    patient_semantics = extraction.entity_semantics.get("patient", "omitted")
    practitioner_semantics = extraction.entity_semantics.get("practitioner", "omitted")
    if patient_semantics in {"ambiguous", "negated", "corrected"} or practitioner_semantics in {"ambiguous", "negated", "corrected"}:
        return None
    patient_refs = _spoken_refs(frame, "patient")
    practitioner_refs = _spoken_refs(frame, "practitioner")
    if patient_refs - {selected["patient_ref"]} or practitioner_refs - {selected["practitioner_ref"]}:
        return None
    if patient_semantics == "exact":
        if patient_refs != {selected["patient_ref"]}:
            return None
        if practitioner_semantics == "exact" and practitioner_refs != {selected["practitioner_ref"]}:
            return None
        if _unresolved_person_cue(frame):
            return None
        return "named"
    if patient_semantics != "omitted" or practitioner_semantics != "omitted":
        return None
    if patient_refs or practitioner_refs or len(frame["utterances"]) != 1:
        return None
    if _unresolved_person_cue(frame):
        return None
    match = _SELECTED_MOVE_WORDS.fullmatch(frame["utterances"][0].strip())
    if match is None or not extraction.normalized_turns:
        return None
    spoken_time = match.group("time").strip().casefold()
    normalized_time = extraction.normalized_values.get("earliest_time")
    if not any(
        fragment.strip().casefold() == spoken_time and value == normalized_time
        for fragment, value in extraction.normalized_turns[0].time_forms.items()
    ):
        return None
    return "selected_only"


def semantic_value(
    extraction: SemanticExtraction | ValidatedModelIntent | None,
    field: str,
) -> Any:
    if extraction is None:
        return None
    if field == "intended_action":
        return extraction.intended_action
    return extraction.normalized_values.get(field)


def _candidate_terms(frame: dict[str, Any], entity_type: str) -> list[str]:
    context = frame["context"]
    if entity_type == "patient":
        rows = context["patients"]
        return [term for row in rows for term in [row["display"], *row["aliases"]]]
    if entity_type == "practitioner":
        rows = context["practitioners"]
        return [term for row in rows for term in [row["display"], *row["aliases"]]]
    if entity_type == "status":
        return list(context["allowed_statuses"])
    raise ValueError(f"unsupported entity type {entity_type}")


def mention_binding(frame: dict[str, Any], entity_type: str) -> dict[str, Any]:
    candidates: list[tuple[int, int, int, str]] = []
    for utterance_index, utterance in enumerate(frame["utterances"]):
        folded = utterance.casefold()
        for term in _candidate_terms(frame, entity_type):
            start = folded.find(term.casefold())
            if start >= 0:
                candidates.append(
                    (len(term), utterance_index, start, utterance[start : start + len(term)])
                )
    if not candidates:
        raise ValueError(f"no grounded {entity_type} mention")
    _, utterance_index, start, text = sorted(candidates, reverse=True)[0]
    return {
        "kind": "utterance_ref",
        "entity_type": entity_type,
        "utterance_index": utterance_index,
        "start": start,
        "end": start + len(text),
        "text": text,
    }


def semantic_binding(field: str) -> dict[str, str]:
    return {"kind": "semantic_ref", "field": field}


def context_binding(field: str) -> dict[str, str]:
    return {"kind": "context_ref", "field": field}


def step_binding(step_id: str, output: str) -> dict[str, str]:
    return {"kind": "step_output", "step_id": step_id, "output": output}


def base_plan(
    frame: dict[str, Any],
    *,
    planner_class: str,
    goal: str,
    attempt: int = 1,
) -> dict[str, Any]:
    return {
        "contract_version": "reception.one.bureau.plan-draft.v1",
        "catalog_version": load_json(CATALOG_PATH)["catalog_version"],
        "request_id": frame["request_id"],
        "practice_ref": frame["practice_ref"],
        "correlation_id": frame["correlation_id"],
        "context_revision": frame["context_revision"],
        "attempt": attempt,
        "revision_limit": 2,
        "planner_class": planner_class,
        "goal": goal,
        "effect_ceiling": "proposal_only",
        "steps": [],
    }


def is_squeeze_in_request(frame: dict[str, Any]) -> bool:
    """Recognise the one explicitly bounded assessment family.

    This is intentionally narrower than a general language interpreter. It
    enables a useful provider-free baseline while the model remains an
    untrusted alternative plan composer behind the same proofreader.
    """

    text = " ".join(str(item) for item in frame.get("utterances", [])).casefold()
    return "squeeze" in text and (
        "without moving" in text
        or "do not move" in text
        or "don't move" in text
    )


def squeeze_in_plan(
    frame: dict[str, Any],
    *,
    planner_class: str = "untrusted_model_candidate",
) -> dict[str, Any]:
    extraction = extraction_for(frame)
    duration_binding = (
        semantic_binding("duration_minutes")
        if semantic_value(extraction, "duration_minutes") is not None
        else context_binding("default_duration_minutes")
    )
    plan = base_plan(
        frame,
        planner_class=planner_class,
        goal="squeeze_in_assessment",
    )
    plan["steps"] = [
        {
            "id": "step-patient",
            "operator": "resolve_patient_reference",
            "args": {"mention": mention_binding(frame, "patient")},
        },
        {
            "id": "step-practitioner",
            "operator": "resolve_practitioner_reference",
            "args": {"mention": mention_binding(frame, "practitioner")},
        },
        {
            "id": "step-date",
            "operator": "resolve_date_expression",
            "args": {"date": semantic_binding("appointment_date")},
        },
        {
            "id": "step-schedule",
            "operator": "read_practitioner_schedule",
            "args": {
                "practitioner": step_binding(
                    "step-practitioner", "practitioner"
                ),
                "date": step_binding("step-date", "date"),
            },
        },
        {
            "id": "step-assess",
            "operator": "assess_squeeze_in_options",
            "args": {
                "patient": step_binding("step-patient", "patient"),
                "schedule": step_binding("step-schedule", "schedule"),
                "duration_minutes": duration_binding,
                "policy": context_binding("squeeze_policy"),
            },
        },
    ]
    return plan


def deterministic_plan(frame: dict[str, Any]) -> dict[str, Any]:
    extraction = extraction_for(frame)
    if is_squeeze_in_request(frame):
        return squeeze_in_plan(frame)
    duration_binding = (
        semantic_binding("duration_minutes")
        if semantic_value(extraction, "duration_minutes") is not None
        else context_binding("default_duration_minutes")
    )
    goal = ACTION_GOALS.get(extraction.intended_action or "", "clarification")
    plan = base_plan(
        frame,
        planner_class="deterministic_semantic_adapter",
        goal=goal,
    )
    if goal == "clarification":
        plan["steps"] = [
            {
                "id": "step-clarification",
                "operator": "request_clarification",
                "args": {},
            }
        ]
        return plan

    selected_subject = selected_move_subject(frame, extraction) if goal == "move" else None
    if goal == "move" and selected_subject is None:
        plan["steps"] = [{"id": "step-clarification", "operator": "request_clarification", "args": {}}]
        return plan
    patient_step = (
        {
            "id": "step-patient",
            "operator": "resolve_patient_reference",
            "args": {"mention": mention_binding(frame, "patient")},
        }
        if selected_subject != "selected_only"
        else None
    )

    if goal == "create":
        plan["steps"] = [
            patient_step,
            {
                "id": "step-practitioner",
                "operator": "resolve_practitioner_reference",
                "args": {"mention": mention_binding(frame, "practitioner")},
            },
            {
                "id": "step-date",
                "operator": "resolve_date_expression",
                "args": {"date": semantic_binding("appointment_date")},
            },
            {
                "id": "step-slots",
                "operator": "search_available_slots",
                "args": {
                    "practitioner": step_binding(
                        "step-practitioner", "practitioner"
                    ),
                    "date": step_binding("step-date", "date"),
                    "earliest_time": semantic_binding("earliest_time"),
                    "latest_time": semantic_binding("latest_time"),
                    "duration_minutes": duration_binding,
                },
            },
            {
                "id": "step-proposal",
                "operator": "prepare_create_proposal",
                "args": {
                    "patient": step_binding("step-patient", "patient"),
                    "practitioner": step_binding(
                        "step-practitioner", "practitioner"
                    ),
                    "candidates": step_binding("step-slots", "candidates"),
                    "duration_minutes": duration_binding,
                },
            },
        ]
        return plan

    selected_steps = [
        *([patient_step] if patient_step is not None else []),
        {
            "id": "step-selected",
            "operator": "read_selected_appointment",
            "args": {
                **({"patient": step_binding("step-patient", "patient")} if patient_step is not None else {}),
                "appointment": context_binding("selected_appointment"),
            },
        },
    ]
    if goal == "move":
        plan["steps"] = [
            *selected_steps,
            {
                "id": "step-date",
                "operator": "resolve_date_expression",
                "args": {"date": semantic_binding("appointment_date")},
            },
            {
                "id": "step-slots",
                "operator": "search_available_slots",
                "args": {
                    "practitioner": step_binding(
                        "step-selected", "practitioner"
                    ),
                    "date": step_binding("step-date", "date"),
                    "earliest_time": semantic_binding("earliest_time"),
                    "latest_time": semantic_binding("latest_time"),
                    "duration_minutes": step_binding(
                        "step-selected", "duration_minutes"
                    ),
                },
            },
            {
                "id": "step-proposal",
                "operator": "prepare_move_proposal",
                "args": {
                    "appointment": step_binding(
                        "step-selected", "appointment"
                    ),
                    "candidates": step_binding("step-slots", "candidates"),
                },
            },
        ]
    elif goal == "resize":
        plan["steps"] = [
            *selected_steps,
            {
                "id": "step-proposal",
                "operator": "prepare_resize_proposal",
                "args": {
                    "appointment": step_binding(
                        "step-selected", "appointment"
                    ),
                    "duration_minutes": semantic_binding("duration_minutes"),
                },
            },
        ]
    elif goal == "cancel":
        plan["steps"] = [
            *selected_steps,
            {
                "id": "step-proposal",
                "operator": "prepare_cancel_proposal",
                "args": {
                    "appointment": step_binding(
                        "step-selected", "appointment"
                    )
                },
            },
        ]
    elif goal == "status_change":
        plan["steps"] = [
            *selected_steps,
            {
                "id": "step-proposal",
                "operator": "prepare_status_proposal",
                "args": {
                    "appointment": step_binding(
                        "step-selected", "appointment"
                    ),
                    "status": mention_binding(frame, "status"),
                },
            },
        ]
    return plan


def normalize_plan(plan: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    normalized = copy.deepcopy(plan)
    repairs: set[str] = set()

    def normalize_identifier(container: dict[str, Any], field: str) -> None:
        value = container.get(field)
        if not isinstance(value, str):
            return
        trimmed = value.strip()
        if trimmed != value:
            repairs.add("trim_whitespace")
        lowered = trimmed.lower()
        if lowered != trimmed:
            repairs.add("canonical_identifier_casing")
        container[field] = lowered

    for field in ("planner_class", "goal", "effect_ceiling"):
        normalize_identifier(normalized, field)
    for step in normalized.get("steps", []):
        if not isinstance(step, dict):
            continue
        normalize_identifier(step, "id")
        normalize_identifier(step, "operator")
        args = step.get("args")
        if not isinstance(args, dict):
            continue
        for binding in args.values():
            if not isinstance(binding, dict):
                continue
            for field in ("kind", "field", "entity_type", "step_id", "output"):
                normalize_identifier(binding, field)
            text = binding.get("text")
            if isinstance(text, str) and text.strip() != text:
                binding["text"] = text.strip()
                repairs.add("trim_whitespace")
    return normalized, sorted(repairs)


def _entity_value(
    frame: dict[str, Any],
    binding: dict[str, Any],
) -> tuple[str | None, Any, bool]:
    utterance_index = binding.get("utterance_index")
    start = binding.get("start")
    end = binding.get("end")
    text = binding.get("text")
    entity_type = binding.get("entity_type")
    if (
        not isinstance(utterance_index, int)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or not isinstance(text, str)
        or not isinstance(entity_type, str)
        or utterance_index < 0
        or utterance_index >= len(frame["utterances"])
    ):
        return None, None, False
    utterance = frame["utterances"][utterance_index]
    if start < 0 or end <= start or end > len(utterance):
        return None, None, False
    if utterance[start:end] != text:
        return None, None, False
    if entity_type in {"patient", "practitioner"}:
        collection = (
            frame["context"]["patients"]
            if entity_type == "patient"
            else frame["context"]["practitioners"]
        )
        matches = [
            row
            for row in collection
            if text.casefold()
            in {row["display"].casefold(), *(alias.casefold() for alias in row["aliases"])}
        ]
        if len(matches) != 1:
            return None, None, False
        value_type = "patient_mention" if entity_type == "patient" else "practitioner_mention"
        return value_type, matches[0]["id"], True
    if entity_type == "status":
        status = text.casefold().replace("no show", "dna").replace("no-show", "dna")
        grounded = status in frame["context"]["allowed_statuses"]
        return "status_mention", status if grounded else None, grounded
    return None, None, False


def binding_type_and_value(
    binding: Any,
    *,
    frame: dict[str, Any],
    extraction: SemanticExtraction | ValidatedModelIntent | None,
    prior_types: dict[str, dict[str, str]],
    prior_values: dict[str, dict[str, Any]] | None = None,
) -> tuple[str | None, Any, bool, str | None]:
    if not isinstance(binding, dict):
        return None, None, False, "ungrounded_binding"
    kind = binding.get("kind")
    if kind == "semantic_ref":
        field = binding.get("field")
        value_type = SEMANTIC_TYPES.get(field)
        value = semantic_value(extraction, field) if isinstance(field, str) else None
        grounded = value_type is not None and value is not None
        return value_type, value, grounded, None if grounded else "semantic_value_missing"
    if kind == "utterance_ref":
        value_type, value, grounded = _entity_value(frame, binding)
        return value_type, value, grounded, None if grounded else "ungrounded_binding"
    if kind == "context_ref":
        field = binding.get("field")
        if field == "selected_appointment.patient_ref":
            value = selected_model_patient(frame) if isinstance(extraction, ValidatedModelIntent) else None
            return "patient_ref", value, value is not None, None if value is not None else "ungrounded_binding"
        value_type = CONTEXT_TYPES.get(field)
        value = frame["context"].get(field) if isinstance(field, str) else None
        grounded = value_type is not None and value is not None
        return value_type, value, grounded, None if grounded else "ungrounded_binding"
    if kind == "step_output":
        step_id = binding.get("step_id")
        output = binding.get("output")
        if step_id not in prior_types or output not in prior_types[step_id]:
            return None, None, False, "forward_reference"
        value = None
        if prior_values is not None:
            value = prior_values.get(step_id, {}).get(output)
        return prior_types[step_id][output], value, True, None
    return None, None, False, "ungrounded_binding"


def _violation(path: str, code: str) -> dict[str, str]:
    return {"path": path, "code": code}


def _forbidden_plan_surface(plan: dict[str, Any]) -> bool:
    if plan.get("effect_ceiling") != "proposal_only":
        return True
    forbidden_fragments = (
        "confirm_appointment",
        "confirmed_write",
        "database_write",
        "delete_database",
        "execute_sql",
        "provider_call",
        "shell_command",
    )
    for step in plan.get("steps", []):
        if not isinstance(step, dict):
            continue
        operator = str(step.get("operator", "")).casefold()
        if any(fragment in operator for fragment in forbidden_fragments):
            return True
    return False


def proofread_plan(
    frame: dict[str, Any],
    plan: dict[str, Any],
    *,
    now: datetime = EVIDENCE_NOW,
) -> tuple[dict[str, Any], dict[str, Any]]:
    catalog = load_json(CATALOG_PATH)
    operators = operator_map(catalog)
    normalized, repairs = normalize_plan(plan)
    input_schema_paths = schema_error_paths(frame, load_json(SCHEMA_PATHS["input"]))
    plan_schema_paths = schema_error_paths(
        normalized, load_json(SCHEMA_PATHS["plan"])
    )
    legacy_mode = normalized.get("contract_version") == LEGACY_PLAN_VERSION
    model_mode = normalized.get("contract_version") in {MODEL_PLAN_VERSION, POINT_PLAN_VERSION}
    model_invalid = False
    if legacy_mode:
        extraction = extraction_for(frame)
    else:
        # No unknown-version or invalid-model fallback into legacy extraction.
        extraction = None
        try:
            extraction = validated_model_intent(frame, normalized)
        except (KeyError, TypeError, ValueError):
            model_invalid = True
    violations: list[dict[str, str]] = []
    checks = {name: True for name in CHECK_NAMES}

    if input_schema_paths or plan_schema_paths or model_invalid:
        checks["schema_exact"] = False
        violations.extend(
            _violation(path, "schema_invalid")
            for path in [*input_schema_paths, *plan_schema_paths]
        )
        if model_invalid:
            violations.append(_violation("$.interpretation", "schema_invalid"))

    checks["scope_bound"] = all(
        normalized.get(field) == frame.get(field)
        for field in ("request_id", "practice_ref", "correlation_id")
    )
    if not checks["scope_bound"]:
        violations.append(_violation("$.request_id", "scope_mismatch"))

    checks["context_revision_current"] = (
        normalized.get("context_revision") == frame.get("context_revision")
    )
    try:
        observed_at = datetime.fromisoformat(frame["observed_at"].replace("Z", "+00:00"))
        expires_at = datetime.fromisoformat(frame["expires_at"].replace("Z", "+00:00"))
        checks["context_revision_current"] = (
            checks["context_revision_current"] and observed_at <= now < expires_at
        )
    except (KeyError, TypeError, ValueError):
        checks["context_revision_current"] = False
    if not checks["context_revision_current"]:
        violations.append(_violation("$.context_revision", "stale_context"))

    checks["authored_synthetic"] = frame.get("data_class") == "authored_synthetic"
    if not checks["authored_synthetic"]:
        violations.append(_violation("$.data_class", "data_class_not_admitted"))

    checks["catalogue_bound"] = (
        normalized.get("catalog_version") == catalog["catalog_version"]
    )
    if not checks["catalogue_bound"]:
        violations.append(_violation("$.catalog_version", "catalogue_mismatch"))

    steps = normalized.get("steps")
    step_list = steps if isinstance(steps, list) else []
    checks["step_budget_bounded"] = 1 <= len(step_list) <= 12
    if not checks["step_budget_bounded"]:
        violations.append(_violation("$.steps", "step_budget_exceeded"))

    step_ids = [
        step.get("id")
        for step in step_list
        if isinstance(step, dict) and isinstance(step.get("id"), str)
    ]
    checks["unique_step_ids"] = len(step_ids) == len(set(step_ids)) == len(step_list)
    if not checks["unique_step_ids"]:
        violations.append(_violation("$.steps", "duplicate_step_id"))

    checks["operators_known"] = True
    checks["topological_order"] = True
    checks["signatures_exact"] = True
    checks["binding_types_exact"] = True
    checks["bindings_grounded"] = True
    prior_types: dict[str, dict[str, str]] = {}

    for index, step in enumerate(step_list):
        if not isinstance(step, dict):
            continue
        operator_id = step.get("operator")
        operator = operators.get(operator_id)
        step_path = f"$.steps[{index}]"
        if operator is None:
            checks["operators_known"] = False
            violations.append(_violation(f"{step_path}.operator", "unknown_operator"))
            continue
        args = step.get("args")
        arg_map = args if isinstance(args, dict) else {}
        expected_inputs = {item["name"]: item for item in operator["inputs"]}
        required_inputs = {
            item["name"] for item in operator["inputs"] if item["required"]
        }
        if not required_inputs.issubset(arg_map) or not set(arg_map).issubset(
            expected_inputs
        ):
            checks["signatures_exact"] = False
            violations.append(_violation(f"{step_path}.args", "signature_mismatch"))
        for arg_name, binding in arg_map.items():
            if arg_name not in expected_inputs:
                continue
            actual_type, _, grounded, grounding_code = binding_type_and_value(
                binding,
                frame=frame,
                extraction=extraction,
                prior_types=prior_types,
            )
            if grounding_code == "forward_reference":
                checks["topological_order"] = False
                violations.append(
                    _violation(
                        f"{step_path}.args.{arg_name}",
                        "forward_reference",
                    )
                )
                continue
            if actual_type != expected_inputs[arg_name]["type"]:
                checks["binding_types_exact"] = False
                violations.append(
                    _violation(
                        f"{step_path}.args.{arg_name}",
                        "binding_type_mismatch",
                    )
                )
            if not grounded:
                checks["bindings_grounded"] = False
                violations.append(
                    _violation(
                        f"{step_path}.args.{arg_name}",
                        grounding_code or "ungrounded_binding",
                    )
                )
        step_id = step.get("id")
        if isinstance(step_id, str):
            prior_types[step_id] = {
                output["name"]: output["type"] for output in operator["outputs"]
            }

    checks["effect_ceiling_preserved"] = (
        normalized.get("effect_ceiling") == "proposal_only"
        and all(
            operators[step["operator"]]["effect"] in ALLOWED_EFFECTS
            for step in step_list
            if isinstance(step, dict) and step.get("operator") in operators
        )
        and not _forbidden_plan_surface(normalized)
    )
    if not checks["effect_ceiling_preserved"]:
        violations.append(_violation("$.effect_ceiling", "effect_escalation"))
        if _forbidden_plan_surface(normalized):
            violations.append(_violation("$.steps", "forbidden_operator"))

    point_operator = any(isinstance(step, dict) and step.get("operator") == "prepare_point_move_proposal" for step in step_list)
    if point_operator and normalized.get("contract_version") != POINT_PLAN_VERSION:
        checks["semantic_action_consistent"] = False
        violations.append(_violation("$.steps", "selected_operation_mismatch"))
    if normalized.get("contract_version") == POINT_PLAN_VERSION and repairs:
        violations.append(_violation("$.steps", "semantic_action_mismatch"))
    if not legacy_mode:
        checks["semantic_action_consistent"] = model_mode and model_plan_consistent(frame, normalized, extraction)
        if not checks["semantic_action_consistent"]:
            violations.append(_violation("$.goal", "selected_operation_mismatch"))
        if isinstance(extraction, ValidatedModelIntent):
            for path in model_dataflow_mismatches(normalized, extraction):
                checks["semantic_action_consistent"] = False
                violations.append(_violation(path, "semantic_action_mismatch"))
    else:
        planner_class = normalized.get("planner_class")
        if planner_class == "deterministic_semantic_adapter":
            expected_goal = ACTION_GOALS.get(extraction.intended_action or "")
            checks["semantic_action_consistent"] = (
                not extraction.requires_clarification
                and expected_goal is not None
                and normalized.get("goal") == expected_goal
                and extraction.authority_claim == "read"
                and extraction.claims_action_completed is False
            )
            if not checks["semantic_action_consistent"]:
                code = (
                    "clarification_required"
                    if extraction.requires_clarification
                    else "semantic_action_mismatch"
                )
                violations.append(_violation("$.goal", code))
        else:
            checks["semantic_action_consistent"] = (
                planner_class == "untrusted_model_candidate"
                and extraction.authority_claim != "refuse"
                and extraction.claims_action_completed is False
            )
            if not checks["semantic_action_consistent"]:
                violations.append(_violation("$.goal", "semantic_action_mismatch"))

        move_steps = any(
            isinstance(step, dict) and step.get("operator") == "prepare_move_proposal"
            for step in step_list
        )
        if normalized.get("goal") == "move" or move_steps:
            subject = selected_move_subject(frame, extraction)
            selected_reads = [
                step for step in step_list
                if isinstance(step, dict) and step.get("operator") == "read_selected_appointment"
            ]
            patient_arg_matches_mode = all(
                isinstance(step.get("args"), dict)
                and ("patient" in step["args"]) == (subject == "named")
                for step in selected_reads
            )
            if (
                subject is None
                or move_steps != (normalized.get("goal") == "move")
                or not patient_arg_matches_mode
                or not selected_reads
            ):
                checks["semantic_action_consistent"] = False
                clarification_step = (
                    planner_class == "deterministic_semantic_adapter"
                    and len(step_list) == 1
                    and isinstance(step_list[0], dict)
                    and step_list[0].get("operator") == "request_clarification"
                )
                if clarification_step:
                    violations.append(_violation("$.goal", "clarification_required"))
                else:
                    if subject is None or not patient_arg_matches_mode or not selected_reads:
                        violations.append(_violation("$.goal", "selected_identity_conflict"))
                    if move_steps != (normalized.get("goal") == "move"):
                        violations.append(_violation("$.goal", "selected_operation_mismatch"))

        selected_family_steps = [
            step for step in step_list
            if isinstance(step, dict) and step.get("operator") in SELECTED_PROPOSAL_FAMILIES
        ]
        selected_reads = [
            step for step in step_list
            if isinstance(step, dict) and step.get("operator") == "read_selected_appointment"
        ]
        selected_context_binding = any(
            isinstance(binding, dict)
            and binding.get("kind") == "context_ref"
            and binding.get("field") == "selected_appointment"
            for step in step_list if isinstance(step, dict)
            for binding in (
                step.get("args") if isinstance(step.get("args"), dict) else {}
            ).values()
        )
        if selected_family_steps or selected_reads or selected_context_binding:
            family = (
                SELECTED_PROPOSAL_FAMILIES[selected_family_steps[0]["operator"]]
                if len(selected_family_steps) == 1 else None
            )
            selected_family_consistent = (
                family is not None
                and step_list[-1] is selected_family_steps[0]
                and normalized.get("goal") == family == extraction.intended_action
                and extraction.authority_claim == "read"
                and not extraction.requires_clarification
                and not extraction.action_negated
                and bool(selected_reads)
                and all(
                    isinstance(step.get("args"), dict)
                    and ("patient" in step["args"] or family == "move")
                    for step in selected_reads
                )
            )
            if not selected_family_consistent:
                checks["semantic_action_consistent"] = False
                violations.append(_violation("$.goal", "selected_operation_mismatch"))

    authority = frame.get("authority", {})
    checks["authority_boundary_closed"] = authority == {
        "effect_ceiling": "proposal_only",
        "appointment_write_authority": False,
        "confirmation_authority": False,
        "provider_execution": False,
        "network_access": False,
        "database_access": False,
        "product_delivery": False,
    }
    if not checks["authority_boundary_closed"]:
        violations.append(
            _violation("$.authority", "authority_boundary_open")
        )

    violation_codes = {item["code"] for item in violations}
    attempt = normalized.get("attempt")
    revision_limit = normalized.get("revision_limit")
    attempt_valid = type(attempt) is int and type(revision_limit) is int
    revisionable_codes = {
        "schema_invalid",
        "signature_mismatch",
        "duplicate_step_id",
        "binding_type_mismatch",
    }
    immediate_reject_codes = {
        "scope_mismatch",
        "stale_context",
        "data_class_not_admitted",
        "catalogue_mismatch",
        "step_budget_exceeded",
        "unknown_operator",
        "forward_reference",
        "ungrounded_binding",
        "effect_escalation",
        "forbidden_operator",
        "semantic_action_mismatch",
        "selected_identity_conflict",
        "selected_operation_mismatch",
        "authority_boundary_open",
    }
    if not violations:
        disposition = "admit"
    elif "clarification_required" in violation_codes or (
        "semantic_value_missing" in violation_codes
        and not (violation_codes & immediate_reject_codes)
    ):
        disposition = "clarification_required"
    elif violation_codes & immediate_reject_codes:
        disposition = "reject"
    elif (
        violation_codes <= revisionable_codes
        and attempt_valid
        and attempt < revision_limit
    ):
        disposition = "revision_required"
    else:
        disposition = "reject"
        if (
            violation_codes & revisionable_codes
            and attempt_valid
            and attempt >= revision_limit
        ):
            violations.append(
                _violation("$.attempt", "revision_budget_exhausted")
            )

    unique_violations = {
        (item["path"], item["code"]): item for item in violations
    }
    violations = [
        unique_violations[key] for key in sorted(unique_violations)
    ][:20]
    review = {
        "contract_version": "reception.one.bureau.plan-review.v1",
        "request_id": frame["request_id"],
        "attempt": attempt if type(attempt) is int and attempt in {1, 2} else 1,
        "reviewed_context_revision": frame["context_revision"],
        "normalized_plan_sha256": canonical_sha256(normalized),
        "disposition": disposition,
        "checks": checks,
        "safe_repairs": repairs,
        "violations": violations,
        "admitted_operator_ids": (
            [step["operator"] for step in step_list] if disposition == "admit" else []
        ),
        "revision_allowed": disposition == "revision_required",
        "execution_authorized": disposition == "admit",
        "effect_ceiling": "proposal_only",
    }
    validate_schema(review, "review")
    return review, normalized


def _binding_runtime_value(
    binding: dict[str, Any],
    *,
    frame: dict[str, Any],
    extraction: SemanticExtraction | ValidatedModelIntent | None,
    prior_types: dict[str, dict[str, str]],
    prior_values: dict[str, dict[str, Any]],
) -> Any:
    _, value, grounded, code = binding_type_and_value(
        binding,
        frame=frame,
        extraction=extraction,
        prior_types=prior_types,
        prior_values=prior_values,
    )
    if not grounded or (binding.get("kind") == "step_output" and value is None):
        raise ValueError(f"runtime binding failed closed: {code}")
    return value


def _warning_union(rows: list[dict[str, Any]]) -> list[str]:
    return sorted(
        {
            warning
            for row in rows
            for warning in row.get("warning_codes", [])
        }
    )


def _proposal(
    family: str,
    *,
    operation_id: str | None,
    patient_ref: str | None = None,
    practitioner_ref: str | None = None,
    appointment_ref: str | None = None,
    candidate_slots: list[dict[str, Any]] | None = None,
    duration_minutes: int | None = None,
    status: str | None = None,
    extra_warnings: list[str] | None = None,
) -> dict[str, Any]:
    slots = candidate_slots or []
    warnings = set(_warning_union(slots))
    warnings.update(extra_warnings or [])
    if family != "clarification":
        warnings.add("staff_confirmation_required")
    if slots:
        warnings.add("staff_selection_required")
    return {
        "kind": (
            "squeeze_in_assessment"
            if family == "squeeze_in_assessment"
            else "clarification"
            if family == "clarification"
            else "proposal_candidate"
        ),
        "proposal_family": family,
        "api_spine_operation_id": operation_id,
        "patient_ref": patient_ref,
        "practitioner_ref": practitioner_ref,
        "appointment_ref": appointment_ref,
        "candidate_slot_ids": sorted(slot["id"] for slot in slots),
        "duration_minutes": duration_minutes,
        "status": status,
        "warning_codes": sorted(warnings),
        "requires_human_confirmation": family != "clarification",
        "write_performed": False,
    }


def execute_operator(
    operator_id: str,
    args: dict[str, Any],
    frame: dict[str, Any],
) -> dict[str, Any]:
    context = frame["context"]
    if operator_id == "resolve_patient_reference":
        return {"patient": args["mention"]}
    if operator_id == "resolve_practitioner_reference":
        return {"practitioner": args["mention"]}
    if operator_id == "resolve_date_expression":
        return {"date": args["date"]}
    if operator_id == "read_selected_appointment":
        appointment = args["appointment"]
        if "patient" in args and appointment["patient_ref"] != args["patient"]:
            raise ValueError("selected appointment patient binding failed closed")
        return {
            "appointment": appointment,
            "practitioner": appointment["practitioner_ref"],
            "duration_minutes": appointment["duration_minutes"],
        }
    if operator_id == "read_patient_appointment_timeline":
        return {
            "appointments": [
                appointment
                for appointment in context["appointments"]
                if appointment["patient_ref"] == args["patient"]
            ]
        }
    if operator_id == "read_practitioner_schedule":
        practitioner = args["practitioner"]
        date = args["date"]
        return {
            "schedule": {
                "practitioner_ref": practitioner,
                "date": date,
                "appointments": [
                    appointment
                    for appointment in context["appointments"]
                    if appointment["practitioner_ref"] == practitioner
                    and appointment["date"] == date
                ],
                "candidate_slots": [
                    slot
                    for slot in context["candidate_slots"]
                    if slot["practitioner_ref"] == practitioner
                    and slot["date"] == date
                ],
            }
        }
    if operator_id == "search_available_slots":
        earliest = args.get("earliest_time", "00:00")
        latest = args.get("latest_time", "23:59")
        candidates = [
            slot
            for slot in context["candidate_slots"]
            if slot["classification"] == "available"
            and slot["practitioner_ref"] == args["practitioner"]
            and slot["date"] == args["date"]
            and slot["duration_minutes"] == args["duration_minutes"]
            and earliest <= slot["start_time"] <= latest
        ]
        if not candidates:
            raise ValueError("authoritative synthetic slot read returned no candidate")
        return {"candidates": candidates}
    if operator_id == "assess_squeeze_in_options":
        policy = args["policy"]
        schedule = args["schedule"]
        if (
            policy["assessment_enabled"] is not True
            or policy["allow_move_existing"] is not False
            or policy["allow_overbook"] is not False
            or policy["requires_human_review"] is not True
        ):
            raise ValueError("squeeze-in policy failed closed")
        candidates = [
            slot
            for slot in schedule["candidate_slots"]
            if slot["classification"] == "squeeze_in_review"
            and slot["duration_minutes"] == args["duration_minutes"]
        ]
        return {
            "proposal": _proposal(
                "squeeze_in_assessment",
                operation_id=None,
                patient_ref=args["patient"],
                practitioner_ref=schedule["practitioner_ref"],
                candidate_slots=candidates,
                duration_minutes=args["duration_minutes"],
                extra_warnings=["manual_squeeze_in_review"],
            )
        }
    if operator_id == "prepare_create_proposal":
        return {
            "proposal": _proposal(
                "create",
                operation_id="proposeAppointmentCreate",
                patient_ref=args["patient"],
                practitioner_ref=args["practitioner"],
                candidate_slots=args["candidates"],
                duration_minutes=args["duration_minutes"],
            )
        }
    if operator_id == "prepare_point_move_proposal":
        appointment = args["appointment"]
        duration = appointment["duration_minutes"]
        if type(duration) is not int or not 1 <= duration <= 480:
            raise ValueError("point selected duration refused")
        proposal = _proposal(
            "move", operation_id="proposeAppointmentUpdate",
            patient_ref=appointment["patient_ref"],
            practitioner_ref=appointment["practitioner_ref"],
            appointment_ref=appointment["id"], duration_minutes=duration,
        )
        proposal.update(target_date=args["date"], target_start_local=args["target_start_local"])
        return {"proposal": proposal}
    if operator_id == "prepare_move_proposal":
        appointment = args["appointment"]
        return {
            "proposal": _proposal(
                "move",
                operation_id="proposeAppointmentUpdate",
                patient_ref=appointment["patient_ref"],
                practitioner_ref=appointment["practitioner_ref"],
                appointment_ref=appointment["id"],
                candidate_slots=args["candidates"],
                duration_minutes=appointment["duration_minutes"],
            )
        }
    if operator_id == "prepare_resize_proposal":
        appointment = args["appointment"]
        return {
            "proposal": _proposal(
                "resize",
                operation_id="proposeAppointmentUpdate",
                patient_ref=appointment["patient_ref"],
                practitioner_ref=appointment["practitioner_ref"],
                appointment_ref=appointment["id"],
                duration_minutes=args["duration_minutes"],
            )
        }
    if operator_id == "prepare_cancel_proposal":
        appointment = args["appointment"]
        return {
            "proposal": _proposal(
                "cancel",
                operation_id="proposeAppointmentDelete",
                patient_ref=appointment["patient_ref"],
                practitioner_ref=appointment["practitioner_ref"],
                appointment_ref=appointment["id"],
                duration_minutes=appointment["duration_minutes"],
            )
        }
    if operator_id == "prepare_status_proposal":
        appointment = args["appointment"]
        return {
            "proposal": _proposal(
                "status_change",
                operation_id="proposeAppointmentStatus",
                patient_ref=appointment["patient_ref"],
                practitioner_ref=appointment["practitioner_ref"],
                appointment_ref=appointment["id"],
                duration_minutes=appointment["duration_minutes"],
                status=args["status"],
            )
        }
    if operator_id == "request_clarification":
        return {
            "clarification": _proposal(
                "clarification",
                operation_id=None,
            )
        }
    raise ValueError("unknown operator reached executor")


def execute_plan(
    frame: dict[str, Any],
    normalized_plan: dict[str, Any],
    review: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    validate_schema(review, "review")
    if review["disposition"] != "admit" or review["execution_authorized"] is not True:
        raise ValueError("non-admitted plan cannot execute")
    plan_hash = canonical_sha256(normalized_plan)
    if review["normalized_plan_sha256"] != plan_hash:
        raise ValueError("reviewed plan hash mismatch")
    if normalized_plan["context_revision"] != frame["context_revision"]:
        raise ValueError("context revision changed before execution")

    operators = operator_map(load_json(CATALOG_PATH))
    if normalized_plan.get("contract_version") == LEGACY_PLAN_VERSION:
        extraction = extraction_for(frame)
    elif normalized_plan.get("contract_version") in {MODEL_PLAN_VERSION, POINT_PLAN_VERSION}:
        if now is None:
            raise ValueError("model-first execution requires explicit trusted clock")
        # Recheck same candidates/evidence/frame, expiry, signatures and effects.
        current_review, current_plan = proofread_plan(frame, normalized_plan, now=now)
        compared_fields = set(current_review) - {"safe_repairs"}
        if (current_review["disposition"] != "admit"
                or any(current_review[key] != review[key] for key in compared_fields)
                or canonical_sha256(current_plan) != plan_hash):
            raise ValueError("model-first review no longer current")
        extraction = validated_model_intent(frame, normalized_plan)
    else:
        raise ValueError("unknown plan contract")
    prior_types: dict[str, dict[str, str]] = {}
    prior_values: dict[str, dict[str, Any]] = {}
    trace: list[dict[str, str]] = []
    for step in normalized_plan["steps"]:
        operator = operators[step["operator"]]
        args = {
            name: _binding_runtime_value(
                binding,
                frame=frame,
                extraction=extraction,
                prior_types=prior_types,
                prior_values=prior_values,
            )
            for name, binding in step["args"].items()
        }
        outputs = execute_operator(step["operator"], args, frame)
        expected_outputs = {
            item["name"]: item["type"] for item in operator["outputs"]
        }
        if set(outputs) != set(expected_outputs):
            raise ValueError("operator output signature changed")
        prior_types[step["id"]] = expected_outputs
        prior_values[step["id"]] = outputs
        trace.append({"step_id": step["id"], "operator": step["operator"]})

    last_step = normalized_plan["steps"][-1]
    last_outputs = prior_values[last_step["id"]]
    if "proposal" in last_outputs:
        final_output = last_outputs["proposal"]
    elif "clarification" in last_outputs:
        final_output = last_outputs["clarification"]
    else:
        raise ValueError("final step did not emit an admitted egress type")
    result = {
        "contract_version": "reception.one.bureau.execution-result.v1",
        "request_id": frame["request_id"],
        "context_revision": frame["context_revision"],
        "reviewed_plan_sha256": plan_hash,
        "status": "executed",
        "operator_trace": trace,
        "final_output": final_output,
        "released_field_paths": [
            "$.final_output.api_spine_operation_id",
            "$.final_output.appointment_ref",
            "$.final_output.candidate_slot_ids",
            "$.final_output.duration_minutes",
            "$.final_output.kind",
            "$.final_output.patient_ref",
            "$.final_output.practitioner_ref",
            "$.final_output.proposal_family",
            "$.final_output.requires_human_confirmation",
            "$.final_output.status",
            "$.final_output.warning_codes",
            "$.final_output.write_performed",
        ],
        "boundary": copy.deepcopy(BOUNDARY),
    }
    if "target_start_local" in final_output:
        result["released_field_paths"].extend(["$.final_output.target_date", "$.final_output.target_start_local"])
    validate_schema(result, "execution")
    return result


def _negative_case(
    case_id: str,
    frame: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    review, normalized = proofread_plan(frame, plan)
    execution_blocked = False
    try:
        execute_plan(frame, normalized, review)
    except ValueError:
        execution_blocked = True
    return {
        "case_id": case_id,
        "disposition": review["disposition"],
        "violation_codes": sorted(
            {violation["code"] for violation in review["violations"]}
        ),
        "execution_blocked": execution_blocked,
    }


def build_evidence() -> dict[str, Any]:
    catalog = load_json(CATALOG_PATH)
    operators = operator_map(catalog)
    cases_document = load_json(CASES_PATH)
    positives = []
    known_plans: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}

    for case in cases_document["cases"]:
        frame = expand_case(cases_document, case)
        plan = (
            copy.deepcopy(case["plan"])
            if "plan" in case
            else deterministic_plan(frame)
        )
        review, normalized = proofread_plan(frame, plan)
        if review["disposition"] != "admit":
            raise ValueError(f"{case['case_id']} did not admit: {review}")
        execution = execute_plan(frame, normalized, review)
        if normalized["goal"] != case["expected_goal"]:
            raise ValueError(f"{case['case_id']} goal changed")
        if (
            execution["final_output"]["api_spine_operation_id"]
            != case["expected_operation_id"]
        ):
            raise ValueError(f"{case['case_id']} operation changed")
        positives.append(
            {
                "case_id": case["case_id"],
                "planner_class": normalized["planner_class"],
                "goal": normalized["goal"],
                "plan_sha256": canonical_sha256(normalized),
                "review_disposition": review["disposition"],
                "safe_repairs": review["safe_repairs"],
                "operator_trace": [
                    item["operator"] for item in execution["operator_trace"]
                ],
                "final_output": execution["final_output"],
                "boundary": execution["boundary"],
            }
        )
        known_plans[case["case_id"]] = (frame, normalized)

    create_frame, create_plan = known_plans["known-create"]
    first_draft = copy.deepcopy(create_plan)
    del first_draft["steps"][-1]["args"]["duration_minutes"]
    first_review, first_normalized = proofread_plan(create_frame, first_draft)
    if first_review["disposition"] != "revision_required":
        raise ValueError("first typed dialogue turn did not request revision")
    second_draft = copy.deepcopy(create_plan)
    second_draft["attempt"] = 2
    second_review, second_normalized = proofread_plan(create_frame, second_draft)
    second_execution = execute_plan(
        create_frame, second_normalized, second_review
    )

    negatives = []
    changed = copy.deepcopy(create_plan)
    changed["steps"][0]["operator"] = "delete_database"
    negatives.append(
        _negative_case("unknown-forbidden-operator", create_frame, changed)
    )

    changed = copy.deepcopy(create_plan)
    mention = changed["steps"][0]["args"]["mention"]
    mention["text"] = "Fabricated Person"
    negatives.append(
        _negative_case("fabricated-entity-reference", create_frame, changed)
    )

    changed = copy.deepcopy(create_plan)
    changed["steps"][0]["args"]["mention"] = step_binding(
        "step-practitioner", "patient"
    )
    negatives.append(
        _negative_case("forward-dataflow-reference", create_frame, changed)
    )

    changed = copy.deepcopy(create_plan)
    changed["context_revision"] = create_frame["context_revision"] - 1
    negatives.append(
        _negative_case("stale-context-revision", create_frame, changed)
    )

    changed = copy.deepcopy(create_plan)
    changed["effect_ceiling"] = "confirmed_write"
    negatives.append(
        _negative_case("write-effect-escalation", create_frame, changed)
    )

    changed = copy.deepcopy(first_normalized)
    changed["attempt"] = 2
    negatives.append(
        _negative_case("revision-budget-exhausted", create_frame, changed)
    )

    if any(not item["execution_blocked"] for item in negatives):
        raise ValueError("a rejected negative case reached execution")
    if any(item["disposition"] != "reject" for item in negatives):
        raise ValueError(f"negative case failed closed: {negatives}")

    return {
        "evidence_version": "reception.one.bureau.typed-plan-protocol-evidence.v1",
        "evidence_mode": "authored_synthetic_provider_free_repository_contract",
        "status": "pass",
        "catalogue": {
            "catalog_version": catalog["catalog_version"],
            "catalog_sha256": canonical_sha256(catalog),
            "operator_count": len(operators),
            "effect_classes": catalog["effect_classes"],
        },
        "positive_cases": positives,
        "typed_dialogue": {
            "first_attempt": {
                "attempt": first_review["attempt"],
                "disposition": first_review["disposition"],
                "violation_codes": sorted(
                    {item["code"] for item in first_review["violations"]}
                ),
                "execution_authorized": first_review["execution_authorized"],
            },
            "second_attempt": {
                "attempt": second_review["attempt"],
                "disposition": second_review["disposition"],
                "plan_sha256": canonical_sha256(second_normalized),
                "execution_authorized": second_review["execution_authorized"],
                "final_output": second_execution["final_output"],
            },
            "revision_count": 1,
            "revision_limit": 2,
        },
        "negative_cases": negatives,
        "watcher_supersession_seam": {
            "context_revision_required": True,
            "stale_plan_disposition": "reject",
            "fresh_read_performed": False,
            "event_runtime_changed": False,
        },
        "provider_boundary": {
            "execution_enabled": False,
            "provider_calls": 0,
            "credentials_requested": False,
            "network_access": False,
            "raw_prompt_persisted": False,
            "raw_response_persisted": False,
        },
        "product_boundary": {
            "database_access": False,
            "product_data_access": False,
            "appointment_write": False,
            "confirmation": False,
            "product_delivery": False,
            "new_api_route": False,
            "new_event_family": False,
        },
        "explicit_exclusions": [
            "live provider or model interpretation",
            "credentials or provider authentication",
            "network or database access",
            "raw historical Diary material",
            "patient, health, clinical or product-derived data",
            "appointment confirmation or mutation",
            "production, deployment or release",
        ],
    }


SEMANTIC_PACKET_VERSION = "emr4.bureau_model_semantic_packet.v2"
SEMANTIC_CONSTRUCTOR_VERSION = "emr4.bureau_model_semantic_constructor.four-routes.v2"

# This finite structural table is the independently reviewed four-route subset.
# Tokens describe typed links only; no utterance text selects a route or value.
_SEMANTIC_PACKET_ROUTES = {
    "clarification": (
        ("step-01-request-clarification", "request_clarification", {}),
    ),
    "move": (
        ("step-01-read-selected-appointment", "read_selected_appointment", {
            "appointment": ("target", "appointment"),
            "patient": ("target", "patient_for_selected_appointment"),
        }),
        ("step-02-search-available-slots", "search_available_slots", {
            "practitioner": ("output", "step-01-read-selected-appointment", "practitioner"),
            "date": ("semantic", "appointment_date"),
            "earliest_time": ("semantic", "earliest_time"),
            "latest_time": ("semantic", "latest_time"),
            "duration_minutes": ("output", "step-01-read-selected-appointment", "duration_minutes"),
        }),
        ("step-03-prepare-move-proposal", "prepare_move_proposal", {
            "appointment": ("output", "step-01-read-selected-appointment", "appointment"),
            "candidates": ("output", "step-02-search-available-slots", "candidates"),
        }),
    ),
    "resize": (
        ("step-01-read-selected-appointment", "read_selected_appointment", {
            "appointment": ("target", "appointment"),
            "patient": ("target", "patient_for_selected_appointment"),
        }),
        ("step-02-prepare-resize-proposal", "prepare_resize_proposal", {
            "appointment": ("output", "step-01-read-selected-appointment", "appointment"),
            "duration_minutes": ("semantic", "duration_minutes"),
        }),
    ),
    "cancel": (
        ("step-01-read-selected-appointment", "read_selected_appointment", {
            "appointment": ("target", "appointment"),
            "patient": ("target", "patient_for_selected_appointment"),
        }),
        ("step-02-prepare-cancel-proposal", "prepare_cancel_proposal", {
            "appointment": ("output", "step-01-read-selected-appointment", "appointment"),
        }),
    ),
}


_POINT_PACKET_ROUTE = (
    ("step-01-read-selected-appointment", "read_selected_appointment", {
        "appointment": ("target", "appointment"),
        "patient": ("target", "patient_for_selected_appointment"),
    }),
    ("step-02-prepare-point-move-proposal", "prepare_point_move_proposal", {
        "appointment": ("output", "step-01-read-selected-appointment", "appointment"),
        "date": ("semantic", "appointment_date"),
        "target_start_local": ("semantic", "target_start_local"),
    }),
)


class SemanticPacketRefusal(ValueError):
    """Fixed refusal code with provenance and any unchanged proofreader result.

    No untrusted model text, raw response or candidate plan is exposed on failure.
    The caller owns private retention; this pure helper persists nothing.
    """
    def __init__(self, code, provenance, review=None):
        super().__init__(code)
        self.provenance = copy.deepcopy(provenance)
        self.review = copy.deepcopy(review)


def compile_model_semantic_packet(
    frame: dict[str, Any], raw_response: bytes, *, case_id: str, now: datetime,
) -> dict[str, Any]:
    """Build one untrusted typed plan, then require the unchanged proofreader.

    Packet checks establish syntax/provenance/explicit selection. Clarification
    validates every original candidate before projecting only action bindings;
    this validation grants no admission. Whole-plan proofreader admission is
    still required. This function does not execute operators, confirm,
    display text, infer meaning, repair packets or retry.
    """
    provenance = {
        "raw_response_sha256": None, "packet_sha256": None, "frame_sha256": None,
        "context_revision": None, "packet_schema_version": SEMANTIC_PACKET_VERSION,
        "constructor_version": SEMANTIC_CONSTRUCTOR_VERSION, "compiled_plan_sha256": None,
    }
    if type(raw_response) is not bytes:
        raise SemanticPacketRefusal("packet_bytes_required", provenance)
    provenance["raw_response_sha256"] = hashlib.sha256(raw_response).hexdigest()
    # A private detached snapshot avoids mutating the caller's frame.
    frame = copy.deepcopy(frame)
    try:
        validate_schema(frame, "input")
    except (TypeError, ValueError):
        raise SemanticPacketRefusal("packet_frame_shape_refused", provenance) from None
    provenance["frame_sha256"] = canonical_sha256(frame)
    provenance["context_revision"] = frame["context_revision"]

    def unique_pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError("duplicate packet key")
            result[key] = value
        return result

    def reject_constant(_):
        raise ValueError("nonfinite packet number")

    try:
        packet = json.loads(raw_response.decode("utf-8"), object_pairs_hook=unique_pairs,
                            parse_constant=reject_constant)
        # Require UTF-8 encodability too: escaped lone surrogates are not an
        # alternate transport for text that cannot be canonically hashed.
        provenance["packet_sha256"] = canonical_sha256(packet)
    except (UnicodeError, TypeError, ValueError, RecursionError):
        raise SemanticPacketRefusal("packet_json_refused", provenance) from None
    try:
        validate_schema(packet, "packet")
    except (TypeError, ValueError):
        raise SemanticPacketRefusal("packet_shape_refused", provenance) from None
    if type(case_id) is not str or not case_id or packet["case_id"] != case_id:
        raise SemanticPacketRefusal("packet_case_refused", provenance)
    point = packet["packet_schema"] == POINT_PACKET_VERSION
    if point:
        provenance["packet_schema_version"] = POINT_PACKET_VERSION
        provenance["constructor_version"] = POINT_CONSTRUCTOR_VERSION
    interpretation = packet["interpretation"]
    if (interpretation["frame_sha256"] != provenance["frame_sha256"]
            or type(interpretation["context_revision"]) is not int
            or type(frame["context_revision"]) is not int
            or interpretation["context_revision"] != frame["context_revision"]
            or interpretation["reference_date"] != frame["reference_date"]):
        raise SemanticPacketRefusal("packet_frame_binding_refused", provenance)
    candidates = interpretation["candidates"]
    by_id = {item["id"]: item for item in candidates}
    selected = interpretation["selected"]
    if (len(by_id) != len(candidates)
            or set(selected) != {item["field"] for item in candidates}
            or any(identifier not in by_id or by_id[identifier]["field"] != field
                   for field, identifier in selected.items())):
        raise SemanticPacketRefusal("packet_selection_refused", provenance)
    # Resolve the selected action ID to its VALUE; never use the ID as goal.
    goal = by_id[selected["intended_action"]]["value"]
    if goal not in _SEMANTIC_PACKET_ROUTES:
        raise SemanticPacketRefusal("packet_action_unsupported", provenance)
    targets = packet["target_bindings"]
    expected_targets = {} if goal == "clarification" else {
        "appointment": {"kind": "context_ref", "field": "selected_appointment"},
        "patient_for_selected_appointment": {
            "kind": "context_ref", "field": "selected_appointment.patient_ref"},
    }
    if targets != expected_targets:
        raise SemanticPacketRefusal("packet_target_roles_refused", provenance)
    # Do not guess or pre-resolve identity here. The unchanged proofreader
    # requires exactly one actual patient and practitioner for the selected row.
    plan = base_plan(frame, planner_class="untrusted_model_candidate", goal=goal)
    plan["contract_version"] = POINT_PLAN_VERSION if point else MODEL_PLAN_VERSION
    plan["interpretation"] = copy.deepcopy(interpretation)
    if point and (goal != "move" or set(selected) != {"intended_action", "appointment_date", "target_start_local"}):
        raise SemanticPacketRefusal("packet_point_fields_refused", provenance)
    route = _POINT_PACKET_ROUTE if point else _SEMANTIC_PACKET_ROUTES[goal]
    for identifier, operator, tokens in route:
        args = {}
        for name, token in tokens.items():
            if token[0] == "target":
                args[name] = copy.deepcopy(targets[token[1]])
            elif token[0] == "semantic":
                args[name] = semantic_binding(token[1])
            else:
                args[name] = step_binding(token[1], token[2])
        plan["steps"].append({"id": identifier, "operator": operator, "args": args})
    if goal == "clarification":
        # Validate the COMPLETE original interpretation before omitting unused
        # fields from the action-only clarification plan. Never drop malformed
        # evidence, invalid values or unresolved supersession to obtain a pass.
        try:
            validated_model_intent(frame, plan)
        except (TypeError, ValueError):
            raise SemanticPacketRefusal("packet_interpretation_refused", provenance) from None
        plan["interpretation"]["candidates"] = [
            copy.deepcopy(item) for item in candidates
            if item["field"] == "intended_action"
        ]
        plan["interpretation"]["selected"] = {
            "intended_action": selected["intended_action"]
        }
    provenance["compiled_plan_sha256"] = canonical_sha256(plan)
    # The existing whole-plan path validates exact evidence, strict values,
    # supersession, complete goal-specific fields, identities, catalog signatures,
    # previous-output links, freshness, scope and proposal-only authority.
    review, normalized = proofread_plan(frame, plan, now=now)
    if review["disposition"] != "admit":
        raise SemanticPacketRefusal("packet_plan_refused", provenance, review)
    if review["safe_repairs"] or normalized != plan:
        raise SemanticPacketRefusal("packet_plan_repair_refused", provenance, review)
    # The sidecar remains separate and explicitly untrusted, without any display
    # or execution wiring. All four hashes bind it to this exact construction.
    sidecar = {"untrusted_text": packet.get("untrusted_text"),
               "display_authorized": False, "provenance": copy.deepcopy(provenance)}
    return {"plan": normalized, "review": review, "provenance": provenance,
            "untrusted_text_sidecar": sidecar,
            # Original selection coverage and evidence remain bound to the raw
            # packet hash, separately from the admitted plan. No prose wiring,
            # identity resolution, display or execution authority is added.
            "packet_interpretation_sidecar": {
                "interpretation": copy.deepcopy(interpretation),
                "display_authorized": False,
                "provenance": copy.deepcopy(provenance),
            },
            "execution_performed": False, "confirmation_performed": False}



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence = build_evidence()
    rendered = json.dumps(
        evidence,
        ensure_ascii=False,
        sort_keys=True,
        indent=None if args.compact else 2,
    )
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8", newline="\n")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
