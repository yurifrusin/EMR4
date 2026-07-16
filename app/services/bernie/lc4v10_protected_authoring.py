"""Sol-only protected authorship for the fresh LC4V10 Gold corpus.

This module constructs Gold from an explicit semantic design.  It does not
call semantic extraction, policy resolution, interpretation, replay, or the
ordinary V10 observer.  Its only framework dependency is the frozen public
schema validator used after independent construction.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from app.services.bernie.lc4v10_content_blind_framework import (
    ACTIONS,
    FIXTURE_SCHEMA,
    LANGUAGE_FORMS,
    THRESHOLD_SCHEMA,
    THRESHOLDS,
    validate_fixture,
    validate_thresholds,
)

ATTEMPT_ID = "lc4v10-fresh-certification-001"
REFERENCE_DATE = "2026-07-17"
APPOINTMENT_DATE = "2026-07-18"
PROVENANCE = "fresh_sol_synthetic_gold_lc4v10_only"

PROTECTED_ROOT = Path("tests/fixtures/bernie_lc4v10_protected")
FIXTURE_PATH = PROTECTED_ROOT / "scenarios.json"
THRESHOLDS_PATH = PROTECTED_ROOT / "thresholds.json"

FIRST_NAMES = (
    "Aster", "Briony", "Cora", "Della", "Elio", "Freya",
    "Gideon", "Hana", "Ivo", "Juno", "Kellan", "Liora",
    "Milo", "Nessa", "Orin", "Pippa", "Quinn", "Rhea",
    "Soren", "Talia", "Una", "Veda", "Willa", "Xander",
)
LAST_NAMES = (
    "Rowan", "Mercer", "Calder", "Vale", "Harlow", "Linden",
    "Marlow", "Perrin", "Sutton", "Keane", "Hollis", "Arden",
)
PRACTITIONERS = (
    ("Dr Shera", "pr-001", "3 pm", "15:00", "2 pm"),
    ("Dr Taylor", "pr-002", "9 am", "09:00", "8 am"),
    ("Dr Patel", "pr-003", "11 am", "11:00", "10 am"),
    ("Dr Chen", "pr-004", "2 pm", "14:00", "1 pm"),
)

_OPERATORS = frozenset(
    {"at", "before", "after", "from", "to", "not", "without", "around", "about", "between", "and"}
)
_TIME = re.compile(r"\b(?:[1-9]|1[0-2])(?:[:.]\d{2})?\s*(?:am|pm)\b", re.I)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8") + b"\n"


def _clock_plus_one(canonical: str) -> str:
    hour, minute = (int(part) for part in canonical.split(":"))
    return f"{(hour + 1) % 24:02d}:{minute:02d}"


def _surface_plus_one(canonical: str) -> str:
    hour = (int(canonical[:2]) + 1) % 24
    suffix = "am" if hour < 12 else "pm"
    display = hour % 12 or 12
    return f"{display} {suffix}"


def _gold_source_spans(utterances: list[str]) -> list[dict[str, Any]]:
    """Independently locate the exact evidence forms used in authored text."""
    turns: list[dict[str, Any]] = []
    for index, original in enumerate(utterances):
        spans: dict[str, list[int]] = {}
        seen_time_fragments: set[str] = set()
        for match in _TIME.finditer(original):
            fragment = match.group(0).strip()
            if fragment not in seen_time_fragments:
                spans[f"time:{fragment}"] = [match.start(), match.end()]
                seen_time_fragments.add(fragment)
        for operator in sorted(_OPERATORS):
            for occurrence, match in enumerate(
                re.finditer(rf"\b{re.escape(operator)}\b", original, re.I)
            ):
                spans[f"operator:{operator}:{occurrence}"] = [
                    match.start(), match.end()
                ]
        turns.append(
            {"turn": index, "original": original, "source_spans": spans}
        )
    return turns


def _action_clause(action: str, patient: str, practitioner: str) -> str:
    clauses = {
        "create": f"Book an appointment for {patient} with {practitioner}",
        "move": f"Move the appointment for {patient} with {practitioner}",
        "resize": (
            "Change the appointment duration to 30 minutes for the appointment "
            f"for {patient} with {practitioner}"
        ),
        "cancel": f"Cancel the appointment for {patient} with {practitioner}",
        "status_change": (
            f"Mark {patient}'s appointment with {practitioner} as arrived"
        ),
        "explain_schedule": (
            f"Explain the appointment schedule for {patient} with {practitioner}"
        ),
    }
    return clauses[action]


def _word_order_clause(action: str, patient: str, practitioner: str) -> str:
    clauses = {
        "create": f"please book an appointment with {practitioner}",
        "move": f"please move the appointment with {practitioner}",
        "resize": f"please change the duration to 30 minutes with {practitioner}",
        "cancel": f"please cancel the appointment with {practitioner}",
        "status_change": f"please mark it as arrived with {practitioner}",
        "explain_schedule": f"please explain it with {practitioner}",
    }
    noun = "appointment schedule" if action == "explain_schedule" else "appointment"
    return f"{patient}'s {noun}: {clauses[action]}"


def _utterances(
    action: str,
    form: str,
    occurrence: int,
    patient: str,
    practitioner: str,
    surface_time: str,
    canonical_time: str,
    correction_time: str,
) -> tuple[list[str], str, str, str]:
    clause = _action_clause(action, patient, practitioner)
    point = f"{clause} tomorrow at {surface_time}."
    if form == "plain":
        turns = [point]
    elif form == "paraphrase":
        turns = [f"Please {point[0].lower()}{point[1:]}"]
    elif form == "speech_like":
        turns = [f"Um, could you please {point[0].lower()}{point[1:]}"]
    elif form == "word_order":
        turns = [
            f"{_word_order_clause(action, patient, practitioner)} tomorrow at {surface_time}."
        ]
    elif form == "correction":
        turns = [
            f"{clause} tomorrow at {correction_time}.",
            f"Actually, make it {surface_time} instead.",
        ]
    elif form == "interval":
        later_surface = _surface_plus_one(canonical_time)
        if occurrence == 0:
            turns = [
                f"{clause} tomorrow after {surface_time}.",
                f"And before {later_surface}.",
            ]
        else:
            turns = [
                f"{clause} tomorrow after {surface_time} but before {later_surface}."
            ]
        return turns, "interval", canonical_time, _clock_plus_one(canonical_time)
    else:  # pragma: no cover - guarded by fixed LANGUAGE_FORMS
        raise ValueError(form)
    return turns, "exact", canonical_time, canonical_time


def _policy_projection(
    action: str, patient: str, practitioner: str, practitioner_id: str
) -> dict[str, Any]:
    mutation = action != "explain_schedule"
    tools = ["search_patients"]
    tools.extend(
        {
            "create": ["find_slots", "create_booking"],
            "move": ["update_appointment"],
            "resize": ["update_appointment"],
            "cancel": ["update_appointment"],
            "status_change": ["change_appointment_status"],
            "explain_schedule": ["find_slots"],
        }[action]
    )
    outcome = {
        "create": "appointment_created",
        "move": "appointment_moved",
        "resize": "appointment_resized",
        "cancel": "appointment_cancelled",
        "status_change": "appointment_status_changed",
        "explain_schedule": "schedule_explained",
    }[action]
    return {
        "requires_clarification": False,
        "clarification_choices": [],
        "resolved_patient": patient,
        "resolved_practitioner": practitioner,
        "resolved_practitioner_id": practitioner_id,
        "selected_tools": tools,
        "authority": "read",
        "diary_relation": "no_conflict",
        "conflicting_fields": [],
        "downstream_outcome": outcome,
        "appointment_delta_count": 1 if mutation else 0,
        "audit_delta_count": 1 if mutation else 0,
        "simulated_write": mutation,
        "entity_semantics_unchanged": True,
    }


def _expected(
    action: str,
    patient: str,
    practitioner: str,
    practitioner_id: str,
    utterances: list[str],
    relation: str,
    earliest: str,
    latest: str,
) -> dict[str, Any]:
    projection = _policy_projection(action, patient, practitioner, practitioner_id)
    mutation = action != "explain_schedule"
    normalized_values: dict[str, Any] = {
        "appointment_date": APPOINTMENT_DATE,
        "earliest_time": earliest,
        "latest_time": latest,
    }
    entity_semantics = {
        "practitioner": "exact",
        "patient": "exact",
        "location": "omitted",
        "appointment_type": "omitted",
        "duration": "omitted",
    }
    if action == "resize":
        normalized_values["duration_minutes"] = 30
        entity_semantics["duration"] = "exact"
    return {
        "intended_action": action,
        "action_semantics": "intended",
        "temporal_relation_and_bounds": {
            "relation": relation,
            "earliest": earliest,
            "latest": latest,
        },
        "normalized_values": normalized_values,
        "entity_semantics": entity_semantics,
        "lossless_source_spans": _gold_source_spans(utterances),
        "extraction_clarification": {"required": False, "choices": []},
        "policy_behavior": {
            "resolution": "propose_mutation" if mutation else "proceed_read",
            "mutation_allowed": mutation,
            "safe": True,
        },
        "exact_policy_projection": projection,
        "policy_clarification": {"required": False, "choices": []},
        "clarification_composition": {
            "extraction_required": False,
            "policy_required": False,
            "choices": [],
        },
        "interpretation_tool": {
            "verb": action,
            "authority": "signed_confirm" if mutation else "read_only",
            "dispatch": "route_to_confirm" if mutation else "route_read_only",
            "clarification_kind": None,
        },
        "replay": {
            "downstream_outcome": projection["downstream_outcome"],
            "appointment_delta_count": projection["appointment_delta_count"],
            "audit_delta_count": projection["audit_delta_count"],
            "simulated_write": projection["simulated_write"],
        },
        "safety": True,
    }


def build_fixture() -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    scenario_number = 0
    for action_index, action in enumerate(ACTIONS):
        for group_within_action, practitioner_data in enumerate(PRACTITIONERS):
            practitioner, practitioner_id, surface_time, canonical_time, correction_time = practitioner_data
            group_number = action_index * 4 + group_within_action + 1
            first_name = FIRST_NAMES[group_number - 1]
            for local_index in range(12):
                scenario_number += 1
                form = LANGUAGE_FORMS[local_index // 2]
                occurrence = local_index % 2
                patient = f"{first_name} {LAST_NAMES[local_index]}"
                turns, relation, earliest, latest = _utterances(
                    action,
                    form,
                    occurrence,
                    patient,
                    practitioner,
                    surface_time,
                    canonical_time,
                    correction_time,
                )
                scenarios.append(
                    {
                        "scenario_id": f"s{scenario_number:03d}",
                        "group_id": f"g{group_number:02d}",
                        "action": action,
                        "language_form": form,
                        "turn_count": len(turns),
                        "coverage_cell": f"c{scenario_number:03d}",
                        "utterances": turns,
                        "diary_state": {"state_kind": "empty", "appointments": []},
                        "expected": _expected(
                            action,
                            patient,
                            practitioner,
                            practitioner_id,
                            turns,
                            relation,
                            earliest,
                            latest,
                        ),
                    }
                )
    return {
        "schema_version": FIXTURE_SCHEMA,
        "attempt_id": ATTEMPT_ID,
        "reference_date": REFERENCE_DATE,
        "provenance": PROVENANCE,
        "scenarios": scenarios,
    }


def build_thresholds() -> dict[str, Any]:
    return {"schema_version": THRESHOLD_SCHEMA, **THRESHOLDS}


def validate_authored_fixture(fixture: dict[str, Any]) -> tuple[str, ...]:
    errors = Counter(validate_fixture(fixture, ATTEMPT_ID))
    scenarios = fixture.get("scenarios", [])
    if isinstance(scenarios, list):
        patients: list[str] = []
        for scenario in scenarios:
            expected = scenario.get("expected", {})
            projection = expected.get("exact_policy_projection", {})
            patient = projection.get("resolved_patient")
            if isinstance(patient, str):
                patients.append(patient)
            if scenario.get("utterances") and any(
                token in json.dumps(scenario, ensure_ascii=False)
                for token in ("Opaque Person", "Synthetic patient option")
            ):
                errors["non_fresh_placeholder_content"] += 1
        if len(set(patients)) != 288:
            errors["patient_identity_population"] += 1
    return tuple(sorted(errors.elements()))


def write_authored_artifacts(repo_root: Path) -> dict[str, str]:
    fixture = build_fixture()
    errors = validate_authored_fixture(fixture)
    if errors:
        raise ValueError(f"authored fixture invalid: {errors}")
    thresholds = build_thresholds()
    threshold_errors = validate_thresholds(thresholds)
    if threshold_errors:
        raise ValueError(f"thresholds invalid: {dict(threshold_errors)}")
    fixture_path = repo_root / FIXTURE_PATH
    thresholds_path = repo_root / THRESHOLDS_PATH
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_payload = _canonical(fixture)
    thresholds_payload = _canonical(thresholds)
    fixture_path.write_bytes(fixture_payload)
    thresholds_path.write_bytes(thresholds_payload)
    return {
        "fixture_sha256": hashlib.sha256(fixture_payload).hexdigest(),
        "thresholds_sha256": hashlib.sha256(thresholds_payload).hexdigest(),
    }


__all__ = [
    "ATTEMPT_ID",
    "FIXTURE_PATH",
    "PROTECTED_ROOT",
    "THRESHOLDS_PATH",
    "build_fixture",
    "build_thresholds",
    "validate_authored_fixture",
    "write_authored_artifacts",
]
