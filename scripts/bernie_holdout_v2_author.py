#!/usr/bin/env python3
"""Protected Sol-only authoring source for the fresh LC4V2 corpus.

This file contains the independently authored v2 blueprint and surface
templates.  It must never be sent to an external worker or provider.  After
the one-shot baseline is consumed it becomes protected support and must not be
read, run, regenerated, or hash-checked without a new user decision.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.holdout_v2_contract import ScenarioGroupEnvelope
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

REFERENCE_DATE = date(2026, 8, 3)
CLINIC_CLOCK = datetime(2026, 8, 3, 8, 20, tzinfo=timezone(timedelta(hours=10)))
APPOINTMENT_DATE = (REFERENCE_DATE + timedelta(days=1)).isoformat()
PATIENT = "Avery Quinn"
CORRECTED_FROM_PATIENT = "Morgan Reed"
PRACTITIONER = "Dr Chen"
APPOINTMENT_TYPE = "standard consult"

LANGUAGE_FORMS = (
    "plain",
    "paraphrase",
    "filler",
    "abbreviation",
    "typo",
    "speech_like",
    "punctuation_variant",
    "adversarial",
    "plain",
    "paraphrase",
    "speech_like",
    "filler",
)


@dataclass(frozen=True)
class Blueprint:
    action: str
    temporal_relation: str
    diary_state: str
    entity_state: str


BLUEPRINTS = (
    Blueprint("create", "exact", "empty", "exact"),
    Blueprint("create", "not_before", "same_day_distinct", "omitted"),
    Blueprint("create", "not_after", "exact_duplicate", "exact"),
    Blueprint("create", "interval", "overlap", "exact"),
    Blueprint("create", "approximate", "terminal", "corrected"),
    Blueprint("create", "exact", "stale", "negated"),
    Blueprint("move", "exact", "exact_duplicate", "exact"),
    Blueprint("move", "interval", "same_day_distinct", "corrected"),
    Blueprint("move", "not_before", "overlap", "ambiguous"),
    Blueprint("move", "approximate", "concurrent", "exact"),
    Blueprint("move", "exact", "roster_absent", "exact"),
    Blueprint("move", "not_after", "stale", "mismatched"),
    Blueprint("resize", "exact", "exact_duplicate", "exact"),
    Blueprint("resize", "interval", "same_day_distinct", "corrected"),
    Blueprint("resize", "approximate", "break", "exact"),
    Blueprint("resize", "not_after", "no_slots", "omitted"),
    Blueprint("resize", "exact", "concurrent", "negated"),
    Blueprint("resize", "not_before", "terminal", "mismatched"),
    Blueprint("cancel", "exact", "exact_duplicate", "exact"),
    Blueprint("cancel", "approximate", "same_day_distinct", "corrected"),
    Blueprint("cancel", "interval", "overlap", "ambiguous"),
    Blueprint("cancel", "exact", "stale", "negated"),
    Blueprint("cancel", "not_before", "concurrent", "exact"),
    Blueprint("cancel", "not_after", "elapsed_window", "omitted"),
)

TEMPORAL = {
    "exact": ("at 3pm", "15:00", "15:00", ("3pm", "3pm")),
    "not_before": ("after 3pm", "15:00", None, ("3pm", None)),
    "not_after": ("before 4pm", None, "16:00", (None, "4pm")),
    "interval": (
        "between 2pm and 4pm",
        "14:00",
        "16:00",
        ("2pm", "4pm"),
    ),
    "approximate": (
        "around 3pm",
        "14:30",
        "15:30",
        ("3pm", "3pm"),
    ),
}

UNCERTAIN_STATES = {
    "terminal",
    "stale",
    "concurrent",
    "roster_absent",
    "break",
    "no_slots",
    "elapsed_window",
}
CLARIFY_ENTITY_STATES = {"omitted", "ambiguous", "mismatched"}


def _patient_surface(entity_state: str) -> str:
    if entity_state == "omitted":
        return ""
    if entity_state == "ambiguous":
        return "the caller"
    if entity_state == "mismatched":
        return "the other Avery"
    if entity_state == "corrected":
        return f"{CORRECTED_FROM_PATIENT}—correction, {PATIENT}"
    return PATIENT


def _duration(action: str) -> tuple[int | None, str]:
    if action == "create":
        return 15, "15-minute"
    if action == "resize":
        return 30, "30-minute"
    return None, ""


def _base_clause(blueprint: Blueprint) -> str:
    temporal_text = TEMPORAL[blueprint.temporal_relation][0]
    patient = _patient_surface(blueprint.entity_state)
    patient_text = f" for {patient}" if patient else ""
    duration, duration_text = _duration(blueprint.action)
    if blueprint.action == "create":
        verb = "do not book" if blueprint.entity_state == "negated" else "book"
        return (
            f"{verb} a {duration_text} {APPOINTMENT_TYPE}{patient_text} "
            f"with {PRACTITIONER} tomorrow {temporal_text}"
        )
    if blueprint.action == "move":
        verb = "do not move" if blueprint.entity_state == "negated" else "move"
        return (
            f"{verb} the {APPOINTMENT_TYPE}{patient_text} with {PRACTITIONER} "
            f"to tomorrow {temporal_text}"
        )
    if blueprint.action == "resize":
        verb = "do not extend" if blueprint.entity_state == "negated" else "extend"
        return (
            f"{verb} the {APPOINTMENT_TYPE}{patient_text} with {PRACTITIONER} "
            f"to {duration_text} tomorrow {temporal_text}"
        )
    verb = "do not cancel" if blueprint.entity_state == "negated" else "cancel"
    return (
        f"{verb} the {APPOINTMENT_TYPE}{patient_text} with {PRACTITIONER} "
        f"tomorrow {temporal_text}"
    )


def _wrap(clause: str, language_form: str) -> str:
    if language_form == "plain":
        return f"Please {clause}."
    if language_form == "paraphrase":
        return f"Could you {clause}, please?"
    if language_form == "filler":
        return f"Hi, when you get a moment, {clause}, thanks."
    if language_form == "abbreviation":
        return f"Pls {clause}."
    if language_form == "typo":
        return f"Pleae {clause}."
    if language_form == "speech_like":
        return f"Um, could you {clause}, please."
    if language_form == "punctuation_variant":
        return f"{clause} — please."
    return f"Keep confirmation safeguards in place and {clause}."


def _turns(blueprint: Blueprint, variant_index: int) -> tuple[list[dict[str, Any]], str]:
    language_form = LANGUAGE_FORMS[variant_index - 1]
    final = _wrap(_base_clause(blueprint), language_form)
    if variant_index == 9:
        final = final[:-1] + " This is the final request."
    if variant_index <= 9:
        return [{"turn": 1, "utterance": final}], "one_shot"
    if variant_index == 10:
        first = _wrap(
            _base_clause(
                Blueprint(
                    blueprint.action,
                    "exact",
                    blueprint.diary_state,
                    blueprint.entity_state,
                )
            ).replace("3pm", "1pm"),
            "plain",
        )
        return [
            {"turn": 1, "utterance": first},
            {"turn": 2, "utterance": f"Correction: {final}"},
        ], "correction"
    if variant_index == 11:
        return [
            {
                "turn": 1,
                "utterance": "The synthetic appointment details need attention.",
            },
            {"turn": 2, "utterance": final},
        ], "clarification"
    return [
        {"turn": 1, "utterance": final},
        {"turn": 2, "utterance": f"Same request, final instruction: {final}"},
    ], "repeated"


def _last_span(
    turns: list[dict[str, Any]],
    text: str,
) -> dict[str, Any]:
    for turn_index in range(len(turns) - 1, -1, -1):
        utterance = str(turns[turn_index]["utterance"])
        start = utterance.rfind(text)
        if start >= 0:
            return {
                "turn_index": turn_index,
                "start": start,
                "end": start + len(text),
                "text": text,
            }
    raise ValueError(f"authored evidence text is missing: {text!r}")


def _source_spans(
    blueprint: Blueprint,
    turns: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    _, _, _, time_tokens = TEMPORAL[blueprint.temporal_relation]
    spans: dict[str, list[dict[str, Any]]] = {
        "appointment_date": [_last_span(turns, "tomorrow")],
        "practitioner": [_last_span(turns, PRACTITIONER)],
        "appointment_type": [_last_span(turns, APPOINTMENT_TYPE)],
    }
    earliest_token, latest_token = time_tokens
    if earliest_token:
        spans["earliest_time"] = [_last_span(turns, earliest_token)]
    if latest_token:
        spans["latest_time"] = [_last_span(turns, latest_token)]
    duration, duration_text = _duration(blueprint.action)
    if duration is not None:
        spans["duration_minutes"] = [_last_span(turns, duration_text)]
    if blueprint.entity_state not in {"omitted", "ambiguous", "mismatched"}:
        spans["patient"] = [_last_span(turns, PATIENT)]
    return spans


def _entity_semantics(entity_state: str) -> tuple[str, str]:
    patient = {
        "exact": "exact",
        "omitted": "omitted",
        "ambiguous": "ambiguous",
        "corrected": "corrected",
        "negated": "negated",
        "mismatched": "mismatched",
    }[entity_state]
    return patient, "exact"


def _policy_outcome(blueprint: Blueprint) -> str | None:
    if blueprint.entity_state in CLARIFY_ENTITY_STATES:
        return "clarification_required"
    if blueprint.entity_state == "negated":
        return None
    if blueprint.action == "create":
        if blueprint.diary_state in {"empty", "same_day_distinct", "terminal"}:
            return "appointment_created"
        if blueprint.diary_state == "exact_duplicate":
            return "existing_booking_found"
        if blueprint.diary_state == "overlap":
            return "candidate_selection_required"
        return None
    if blueprint.diary_state in UNCERTAIN_STATES:
        return None
    return {
        "move": "appointment_moved",
        "resize": "appointment_resized",
        "cancel": "appointment_cancelled",
    }[blueprint.action]


def _tools(blueprint: Blueprint) -> list[str]:
    if blueprint.entity_state in CLARIFY_ENTITY_STATES:
        return ["request_clarification"]
    if blueprint.entity_state == "negated":
        return ["search_patients"]
    if blueprint.action == "create":
        return ["search_patients", "find_slots", "create_booking"]
    return ["search_patients", "update_appointment"]


def _deltas(
    blueprint: Blueprint,
    outcome: str | None,
    earliest_time: str | None,
    duration_minutes: int | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    change_type = {
        "appointment_created": "created",
        "existing_booking_found": "created",
        "appointment_moved": "moved",
        "appointment_resized": "resized",
        "appointment_cancelled": "cancelled",
    }.get(outcome)
    if change_type is None:
        return [], []
    if outcome == "existing_booking_found" and earliest_time is None:
        return [], []
    appointment = {
        "appointment_id": "apt-001",
        "change_type": change_type,
        "patient_id": "p-001",
        "practitioner_id": "pr-004",
        "date": APPOINTMENT_DATE,
        "start_time": earliest_time or "",
        "duration_minutes": duration_minutes or 15,
    }
    audit = {
        "change_type": change_type,
        "appointment_id": "apt-001",
        "count": 1,
    }
    return [appointment], [audit]


def _scenario(
    group_index: int,
    variant_index: int,
    blueprint: Blueprint,
) -> ReceptionScenarioSpec:
    group_id = f"lc4v2_group_{group_index:03d}"
    turns, dialogue_form = _turns(blueprint, variant_index)
    temporal_text, earliest, latest, _ = TEMPORAL[blueprint.temporal_relation]
    duration, _ = _duration(blueprint.action)
    patient_semantics, practitioner_semantics = _entity_semantics(
        blueprint.entity_state
    )
    outcome = _policy_outcome(blueprint)
    appointment_deltas, audit_deltas = _deltas(
        blueprint,
        outcome,
        earliest,
        duration,
    )
    normalized: dict[str, Any] = {"appointment_date": APPOINTMENT_DATE}
    if earliest is not None:
        normalized["earliest_time"] = earliest
    if latest is not None:
        normalized["latest_time"] = latest
    if duration is not None:
        normalized["duration_minutes"] = duration
    clarify = blueprint.entity_state in CLARIFY_ENTITY_STATES
    initial_state = {
        "synthetic": True,
        "reference_date": REFERENCE_DATE.isoformat(),
        "diary_page_date": APPOINTMENT_DATE,
        "state": blueprint.diary_state,
        "seeded_appointments": (
            []
            if blueprint.diary_state == "empty"
            else [{"appointment_id": "apt-001", "synthetic": True}]
        ),
    }
    return ReceptionScenarioSpec(
        scenario_id=f"{group_id}_var_{variant_index:03d}",
        provenance="gold",
        adjudication="adjudicated",
        family=group_id,
        description=(
            f"Fresh synthetic v2 {blueprint.action}/{blueprint.temporal_relation}/"
            f"{blueprint.diary_state}/{blueprint.entity_state}"
        ),
        dialogue_turns=turns,
        reference_date=REFERENCE_DATE,
        clinic_clock=CLINIC_CLOCK,
        intended_action=blueprint.action,
        action_semantics="ambiguous" if clarify else "intended",
        temporal_relation=blueprint.temporal_relation,
        earliest_time=earliest,
        latest_time=latest,
        normalized_values=normalized,
        source_spans=_source_spans(blueprint, turns),
        duration_minutes=duration,
        practitioner_semantics=practitioner_semantics,
        patient_semantics=patient_semantics,
        location_semantics="omitted",
        appointment_type_semantics="exact",
        duration_semantics="exact" if duration is not None else "omitted",
        diary_state=blueprint.diary_state,
        entity_state=blueprint.entity_state,
        dialogue_form=dialogue_form,
        language_form=LANGUAGE_FORMS[variant_index - 1],
        initial_diary_state=initial_state,
        expected_outcome_kind=outcome,
        expected_tool_sequence=_tools(blueprint),
        expected_appointment_deltas=appointment_deltas,
        expected_audit_deltas=audit_deltas,
        forbidden_outcomes=["appointment_confirmed", "second_appointment_created"],
        forbidden_tool_calls=["confirm_appointment", "mutate_diary_direct"],
        expected_clarification=(
            "Which synthetic patient should I use?" if clarify else None
        ),
        clarification_choices=(
            ["provide_exact_synthetic_patient"] if clarify else []
        ),
    )


def build_groups() -> tuple[ScenarioGroupEnvelope, ...]:
    groups = []
    for group_index, blueprint in enumerate(BLUEPRINTS, start=1):
        group_id = f"lc4v2_group_{group_index:03d}"
        groups.append(
            ScenarioGroupEnvelope(
                group_id=group_id,
                variants=tuple(
                    _scenario(group_index, variant_index, blueprint)
                    for variant_index in range(1, 13)
                ),
            )
        )
    return tuple(groups)


def write_groups(output_dir: Path) -> None:
    if output_dir.exists():
        raise ValueError("refusing to overwrite an existing v2 output directory")
    output_dir.mkdir(parents=True)
    for group in build_groups():
        path = output_dir / f"{group.group_id}.json"
        path.write_text(
            json.dumps(
                group.model_dump(mode="json"),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    groups = build_groups()
    print("group_count=24")
    print("variant_count=288")
    print("multi_turn_count=72")
    if args.write:
        write_groups(args.output_dir)
        print(f"written={args.output_dir}")
    else:
        print("dry_run=true")
    if len(groups) != 24:
        raise AssertionError("author blueprint group count drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
