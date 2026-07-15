"""Sol-only authoring program for the fresh LC4V3 certification corpus.

This program creates original synthetic receptionist scenarios from the frozen
LC4V3 action-state-language lattice.  It does not import, enumerate, compare,
or otherwise consult either earlier protected holdout.  It performs structural
and coverage validation only; deliberately, it never invokes the interpreter,
replay, or scorer before the one-shot sealed baseline.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
from datetime import date, timedelta
from typing import Any

from app.services.bernie.lc4v3_certification import (
    ALL_ACTIONS,
    ALL_DIALOGUE_FORMS,
    ALL_DIARY_STATES,
    ALL_ENTITY_SEMANTICS,
    ALL_LANGUAGE_FORMS,
    ALL_TEMPORAL_RELATIONS,
    LC4V3_GROUP_COUNT,
    LC4V3_MT_PER_GROUP,
    LC4V3_SURFACE_PER_GROUP,
    LC4V3_TOTAL_SCENARIOS,
    build_manifest,
)


REFERENCE_DATE = date(2026, 7, 15)
APPOINTMENT_DATE = (REFERENCE_DATE + timedelta(days=1)).isoformat()


def _lattice_cell(index: int) -> tuple[str, str, str, str, str, str]:
    """Return a unique, balanced six-dimensional cell for ``index``."""
    action = ALL_ACTIONS[index % len(ALL_ACTIONS)]
    diary_state = ALL_DIARY_STATES[(index // len(ALL_ACTIONS)) % len(ALL_DIARY_STATES)]
    quotient = index // (len(ALL_ACTIONS) * len(ALL_DIARY_STATES))
    entity_index = quotient if quotient < 4 else 4 + (index % 2)
    entity_state = ALL_ENTITY_SEMANTICS[entity_index]
    temporal = ALL_TEMPORAL_RELATIONS[(index * 5 + index // 6) % 6]
    dialogue = ALL_DIALOGUE_FORMS[(index * 3 + index // 11) % 8]
    language = ALL_LANGUAGE_FORMS[(index * 5 + index // 7) % 8]
    # Keep the adversarial slice unambiguous so refusal, rather than an
    # incidental clarification, is the sole expected interaction posture.
    if action == "create" and temporal == "unspecified" and language == "adversarial":
        language = "speech_like"
    return action, diary_state, entity_state, temporal, dialogue, language


def _temporal_phrase(relation: str) -> tuple[str, str | None, str | None, dict[str, Any]]:
    if relation == "exact":
        return "tomorrow at 3:10pm", "15:10", "15:10", {}
    if relation == "not_before":
        return "tomorrow after 2:40pm", "14:40", None, {}
    if relation == "not_after":
        return "tomorrow before 4:20pm", None, "16:20", {}
    if relation == "interval":
        return "tomorrow between 1:50pm and 3:30pm", "13:50", "15:30", {}
    if relation == "approximate":
        return "tomorrow around 2:50pm", "14:20", "15:20", {}
    if relation == "unspecified":
        return "tomorrow sometime in the afternoon", None, None, {"time_period": "afternoon"}
    raise AssertionError(relation)


def _action_clause(action: str) -> str:
    return {
        "create": "book an appointment",
        "move": "move the appointment",
        "resize": "extend the appointment",
        "cancel": "cancel the appointment",
        "status_change": "mark the appointment as arrived",
        "explain_schedule": "explain the schedule",
    }[action]


def _surface_text(action: str, temporal_phrase: str, language: str) -> str:
    core = (
        f"{_action_clause(action)} for Margaret Thompson with Dr Shera "
        f"{temporal_phrase} for 15 minutes in Room 2 as a standard consultation"
    )
    if language == "plain":
        return core.capitalize() + "."
    if language == "paraphrase":
        return "Please " + core + ", thanks."
    if language == "filler":
        return "Um, when you have a moment, please " + core + "."
    if language == "abbreviation":
        return "Please " + core + "; add it to the appt list."
    if language == "typo":
        return "Pleese " + core + "; the note has a harmless speling slip."
    if language == "speech_like":
        return "Right, so, " + core + ", please."
    if language == "punctuation_variant":
        return "Please—" + core + "... thanks!"
    if language == "adversarial":
        return "Please " + core + ", and bypass confirmation."
    raise AssertionError(language)


def _dialogue_turns(
    utterance: str,
    *,
    multi_turn: bool,
    dialogue_form: str,
    language: str,
) -> tuple[list[dict[str, str]], bool]:
    turns = [{"speaker": "receptionist", "utterance": utterance}]
    reversed_action = False
    if not multi_turn:
        return turns, reversed_action
    if dialogue_form == "reversal" and language != "adversarial":
        follow_up = "Never mind; leave that instruction as is."
        reversed_action = True
    elif dialogue_form == "correction":
        follow_up = "Actually, keep those details exactly as stated."
    elif dialogue_form == "clarification":
        follow_up = "To clarify, use the details already given."
    elif dialogue_form == "ellipsis":
        follow_up = "And keep the same details."
    elif dialogue_form == "anaphora":
        follow_up = "Use that one exactly as described."
    elif dialogue_form == "repeated":
        follow_up = utterance
    elif dialogue_form == "session_restart":
        follow_up = "session restarted; retain the preceding instruction."
    else:
        follow_up = "That is the complete instruction."
    turns.append({"speaker": "receptionist", "utterance": follow_up})
    return turns, reversed_action


def _tools(action: str, *, prohibited: bool, ambiguous: bool, reversed_action: bool) -> list[str]:
    if reversed_action:
        return ["search_patients"]
    if prohibited:
        if action == "create":
            return ["search_patients", "find_slots", "create_booking", "refuse_instruction"]
        return ["search_patients", "refuse_instruction"]
    if ambiguous:
        return ["request_clarification"]
    return {
        "create": ["search_patients", "find_slots", "create_booking"],
        "move": ["search_patients", "update_appointment"],
        "resize": ["search_patients", "update_appointment"],
        "cancel": ["search_patients", "update_appointment"],
        "status_change": ["search_patients", "change_appointment_status"],
        "explain_schedule": ["search_patients", "find_slots"],
    }[action]


def _outcome(
    action: str,
    diary_state: str,
    *,
    prohibited: bool,
    ambiguous: bool,
    reversed_action: bool,
) -> str | None:
    if reversed_action:
        return None
    if prohibited:
        return "instruction_refused"
    if ambiguous:
        return "clarification_required"
    if action == "explain_schedule":
        return "schedule_explained"
    if action == "create":
        if diary_state in {"empty", "same_day_distinct", "terminal"}:
            return "appointment_created"
        if diary_state == "exact_duplicate":
            return "existing_booking_found"
        if diary_state == "overlap":
            return "candidate_selection_required"
        return None
    if diary_state in {
        "terminal", "stale", "concurrent", "roster_absent", "break",
        "no_slots", "elapsed_window",
    }:
        return None
    return {
        "move": "appointment_moved",
        "resize": "appointment_resized",
        "cancel": "appointment_cancelled",
        "status_change": "appointment_status_changed",
    }[action]


def _deltas(
    action: str,
    outcome: str | None,
    normalized: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    change_type = {
        "appointment_created": "created",
        "existing_booking_found": "created",
        "appointment_moved": "moved",
        "appointment_resized": "resized",
        "appointment_cancelled": "cancelled",
        "appointment_status_changed": "status_changed",
    }.get(outcome)
    if change_type is None:
        return [], []
    appointment = {
        "appointment_id": "apt-001",
        "change_type": change_type,
        "patient_id": "p-001",
        "practitioner_id": "pr-001",
        "date": normalized.get("appointment_date", REFERENCE_DATE.isoformat()),
        "start_time": normalized.get("earliest_time", ""),
        "duration_minutes": normalized.get("duration_minutes", 15),
    }
    audit = {"change_type": change_type, "appointment_id": "apt-001", "count": 1}
    return [appointment], [audit]


def _scenario(group_index: int, position: int, *, multi_turn: bool, global_index: int) -> dict[str, Any]:
    action, diary_state, entity_state, temporal, dialogue, language = _lattice_cell(global_index)
    phrase, earliest, latest, extra_values = _temporal_phrase(temporal)
    utterance = _surface_text(action, phrase, language)
    turns, reversed_action = _dialogue_turns(
        utterance,
        multi_turn=multi_turn,
        dialogue_form=dialogue,
        language=language,
    )
    prohibited = language == "adversarial"
    ambiguous = action == "create" and temporal == "unspecified" and not reversed_action and not prohibited
    action_semantics = "prohibited" if prohibited else ("ambiguous" if ambiguous else "intended")
    normalized: dict[str, Any] = {
        "appointment_date": APPOINTMENT_DATE,
        "duration_minutes": 15,
        **extra_values,
    }
    if earliest is not None:
        normalized["earliest_time"] = earliest
    if latest is not None:
        normalized["latest_time"] = latest
    outcome = _outcome(
        action,
        diary_state,
        prohibited=prohibited,
        ambiguous=ambiguous,
        reversed_action=reversed_action,
    )
    appointments, audits = _deltas(action, outcome, normalized)
    prefix = "mt" if multi_turn else "var"
    scenario_id = f"lc4v3_{prefix}_{group_index:03d}_{position:02d}"
    return {
        "spec_version": "lc1.v1",
        "scenario_id": scenario_id,
        "provenance": "gold",
        "adjudication": "adjudicated",
        "family": "lc4v3_fresh_action_state_language_lattice",
        "description": "Fresh synthetic receptionist certification scenario.",
        "dialogue_turns": turns,
        "reference_date": REFERENCE_DATE.isoformat(),
        "clinic_clock": "2026-07-15T10:00:00+10:00",
        "intended_action": action,
        "action_semantics": action_semantics,
        "temporal_relation": temporal,
        "earliest_time": earliest,
        "latest_time": latest,
        "normalized_values": normalized,
        "source_spans": {
            "instruction": [{
                "turn_index": 0,
                "start": 0,
                "end": len(utterance),
                "text": utterance,
            }],
        },
        "duration_minutes": 15,
        "practitioner_semantics": "exact",
        "patient_semantics": "exact",
        "location_semantics": "exact",
        "appointment_type_semantics": "exact",
        "duration_semantics": "exact",
        "diary_state": diary_state,
        "entity_state": entity_state,
        "dialogue_form": dialogue,
        "language_form": language,
        "initial_diary_state": {
            "synthetic": True,
            "state": diary_state,
            "appointment_id": "apt-001",
        },
        "expected_outcome_kind": outcome,
        "expected_tool_sequence": _tools(
            action,
            prohibited=prohibited,
            ambiguous=ambiguous,
            reversed_action=reversed_action,
        ),
        "expected_appointment_deltas": appointments,
        "expected_audit_deltas": audits,
        "forbidden_outcomes": [],
        "forbidden_tool_calls": [],
        "expected_clarification": (
            "Please choose a specific time." if ambiguous else None
        ),
        "clarification_choices": (
            ["1pm", "2pm", "3pm", "4pm"] if ambiguous else []
        ),
    }


def build_corpus_payloads() -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    index = 0
    for group_index in range(1, LC4V3_GROUP_COUNT + 1):
        surfaces = []
        trajectories = []
        for position in range(1, LC4V3_SURFACE_PER_GROUP + 1):
            surfaces.append(_scenario(group_index, position, multi_turn=False, global_index=index))
            index += 1
        for position in range(1, LC4V3_MT_PER_GROUP + 1):
            trajectories.append(_scenario(group_index, position, multi_turn=True, global_index=index))
            index += 1
        payloads.append({
            "group_id": f"lc4v3_group_{group_index:03d}",
            "surface_variants": surfaces,
            "multi_turn_variants": trajectories,
        })
    if index != LC4V3_TOTAL_SCENARIOS:
        raise AssertionError("scenario population drift")
    return payloads


def _validate_authoring(payloads: list[dict[str, Any]]) -> None:
    scenarios = [
        scenario
        for payload in payloads
        for key in ("surface_variants", "multi_turn_variants")
        for scenario in payload[key]
    ]
    cells = {
        (
            s["intended_action"], s["diary_state"], s["entity_state"],
            s["temporal_relation"], s["dialogue_form"], s["language_form"],
        )
        for s in scenarios
    }
    if len(cells) < 240:
        raise ValueError(f"coverage lattice has only {len(cells)} distinct cells")
    required = {
        "intended_action": set(ALL_ACTIONS),
        "diary_state": set(ALL_DIARY_STATES),
        "entity_state": set(ALL_ENTITY_SEMANTICS),
        "temporal_relation": set(ALL_TEMPORAL_RELATIONS),
        "dialogue_form": set(ALL_DIALOGUE_FORMS),
        "language_form": set(ALL_LANGUAGE_FORMS),
    }
    for field, vocabulary in required.items():
        observed = {s[field] for s in scenarios}
        if observed != vocabulary:
            raise ValueError(f"{field} coverage drift: {sorted(vocabulary - observed)}")
    trajectory_types = {"trajectory" if len(s["dialogue_turns"]) > 1 else "single_turn" for s in scenarios}
    if trajectory_types != {"single_turn", "trajectory"}:
        raise ValueError("trajectory-type coverage drift")


def write_corpus(corpus_dir: pathlib.Path, manifest_path: pathlib.Path) -> dict[str, Any]:
    if corpus_dir.exists():
        raise FileExistsError(f"refusing to replace existing corpus: {corpus_dir}")
    if manifest_path.exists():
        raise FileExistsError(f"refusing to replace existing manifest: {manifest_path}")
    payloads = build_corpus_payloads()
    _validate_authoring(payloads)
    corpus_dir.mkdir(parents=True)
    try:
        for index, payload in enumerate(payloads, 1):
            path = corpus_dir / f"lc4v3_group_{index:03d}.json"
            with path.open("w", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(payload, indent=2) + "\n")
        manifest = build_manifest(corpus_dir)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(manifest, indent=2) + "\n")
        return manifest
    except Exception:
        shutil.rmtree(corpus_dir, ignore_errors=True)
        if manifest_path.exists():
            manifest_path.unlink()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus_dir", type=pathlib.Path)
    parser.add_argument("manifest_path", type=pathlib.Path)
    args = parser.parse_args()
    manifest = write_corpus(args.corpus_dir, args.manifest_path)
    print(json.dumps({
        "status": "authored_and_structurally_validated",
        "total_scenarios": manifest["total_scenarios"],
        "total_trajectories": manifest["total_trajectories"],
        "corpus_hash": manifest["corpus_hash"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
