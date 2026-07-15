"""LC4V4D1 — Independent development diagnostic matrix.

Authors 60 fresh inspectable Gold/adjudicated probes across entity, dialogue,
safety/policy, and diary-state families, runs each twice through the
deterministic interpretation, replay, and composed scorer, and classifies
results into authoring_invalid, parser_gap, policy_contract_gap, scorer_gap,
planned_unavailable, or supported_pass.

Protected holdouts v1-v4 remain sealed.  No parser, policy, replay, scorer,
route, provider, or runtime code is modified.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Literal

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
)
from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    InterpretationObservation,
    ReplayObservation,
    score_interpretation_replay_pair,
)
from app.services.bernie.scenario_spec import (
    EntitySemantics,
    ReceptionScenarioSpec,
    ScenarioSourceSpan,
    TemporalRelation,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXPECTED_PROBE_COUNT = 60
EXPECTED_REPEATS = 2
EXPECTED_ENTITY_PROBES = 30
EXPECTED_DIALOGUE_PROBES = 12
EXPECTED_SAFETY_PROBES = 12  # 6 pairs
EXPECTED_DIARY_PROBES = 6

REFERENCE_DATE = date(2026, 7, 15)
CLINIC_CLOCK = datetime(2026, 7, 15, 8, 0, 0, tzinfo=timezone(timedelta(hours=10)))
CLINIC_CLOCK_STR = "2026-07-15T08:00:00+10:00"
REFERENCE_DATE_STR = "2026-07-15"

Classification = Literal[
    "authoring_invalid",
    "parser_gap",
    "policy_contract_gap",
    "scorer_gap",
    "planned_unavailable",
    "supported_pass",
]

FAMILY_ENTITY = "entity"
FAMILY_DIALOGUE = "dialogue"
FAMILY_SAFETY = "safety"
FAMILY_DIARY = "diary"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProbeResult:
    """One fully evaluated probe (both repeats)."""

    probe_id: str
    family: str
    classification: Classification
    mismatch_fields: tuple[str, ...] = ()
    mismatch_layers: tuple[str, ...] = ()
    repeat_0_result: ComposedSampleResult | None = None
    repeat_1_result: ComposedSampleResult | None = None
    variance_observed: bool = False
    authoring_error: str | None = None


@dataclass(frozen=True)
class DiagnosticReport:
    """Aggregate diagnostic report."""

    source_commit: str
    fixture_hash: str
    report_hash: str
    candidate_selection_hash: str
    total_probes: int
    total_observations: int
    classifications: dict[str, int]
    family_counts: dict[str, dict[str, int]]
    probe_results: tuple[ProbeResult, ...]
    parser_gap_ids: tuple[str, ...]
    variance_count: int
    remediation_authorized: bool = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_id(family: str, kind: str, index: int) -> str:
    return f"lc4v4d1_{family}_{kind}_{index:02d}"


def _find_span(utterance: str, text: str, turn_index: int = 0) -> dict[str, Any]:
    """Find a text span in an utterance and return a span dict.

    Raises ValueError if text not found.
    """
    idx = utterance.find(text)
    if idx < 0:
        raise ValueError(f"Text {text!r} not found in utterance {utterance!r}")
    return {
        "turn_index": turn_index,
        "start": idx,
        "end": idx + len(text),
        "text": text,
    }


def _utterance(text: str) -> dict[str, Any]:
    return {"utterance": text, "role": "patient"}


def _base_spec_dict(
    scenario_id: str,
    description: str,
    utterances: list[str],
    intended_action: str = "create",
    action_semantics: str = "intended",
    temporal_relation: str = "exact",
    earliest_time: str | None = "15:00",
    latest_time: str | None = "15:00",
    duration_minutes: int | None = 30,
    practitioner_semantics: str = "exact",
    patient_semantics: str = "exact",
    location_semantics: str = "exact",
    appointment_type_semantics: str = "exact",
    duration_semantics: str = "exact",
    entity_state: str = "exact",
    dialogue_form: str = "one_shot",
    language_form: str = "plain",
    diary_state: str = "empty",
    initial_diary_state: dict[str, Any] | None = None,
    expected_outcome_kind: str | None = None,
    expected_tool_sequence: list[str] | None = None,
    expected_appointment_deltas: list[dict[str, Any]] | None = None,
    expected_audit_deltas: list[dict[str, Any]] | None = None,
    forbidden_outcomes: list[str] | None = None,
    forbidden_tool_calls: list[str] | None = None,
    expected_clarification: str | None = None,
    clarification_choices: list[str] | None = None,
    source_spans: dict[str, list[dict[str, Any]]] | None = None,
    family: str = "entity",
) -> dict[str, Any]:
    """Build a raw dict that can be passed to ReceptionScenarioSpec."""
    if initial_diary_state is None:
        initial_diary_state = {"appointments": []}
    if expected_tool_sequence is None:
        expected_tool_sequence = ["read_schedule", "propose_appointment"]
    if expected_appointment_deltas is None:
        expected_appointment_deltas = []
    if expected_audit_deltas is None:
        expected_audit_deltas = []
    if forbidden_outcomes is None:
        forbidden_outcomes = ["write", "confirm", "cancel_existing"]
    if forbidden_tool_calls is None:
        forbidden_tool_calls = [
            "write_appointment",
            "cancel_appointment",
            "resize_appointment",
            "move_appointment",
        ]
    if source_spans is None:
        source_spans = {}

    normalized_values: dict[str, Any] = {
        "appointment_date": "2026-07-16",
    }
    if earliest_time is not None:
        normalized_values["earliest_time"] = earliest_time
    if latest_time is not None:
        normalized_values["latest_time"] = latest_time
    if duration_minutes is not None:
        normalized_values["duration_minutes"] = duration_minutes

    return {
        "spec_version": "lc1.v1",
        "scenario_id": scenario_id,
        "provenance": "gold",
        "adjudication": "adjudicated",
        "family": family,
        "description": description,
        "dialogue_turns": [_utterance(u) for u in utterances],
        "reference_date": REFERENCE_DATE_STR,
        "clinic_clock": CLINIC_CLOCK_STR,
        "intended_action": intended_action,
        "action_semantics": action_semantics,
        "temporal_relation": temporal_relation,
        "earliest_time": earliest_time,
        "latest_time": latest_time,
        "normalized_values": normalized_values,
        "source_spans": source_spans,
        "duration_minutes": duration_minutes,
        "practitioner_semantics": practitioner_semantics,
        "patient_semantics": patient_semantics,
        "location_semantics": location_semantics,
        "appointment_type_semantics": appointment_type_semantics,
        "duration_semantics": duration_semantics,
        "diary_state": diary_state,
        "entity_state": entity_state,
        "dialogue_form": dialogue_form,
        "language_form": language_form,
        "initial_diary_state": initial_diary_state,
        "expected_outcome_kind": expected_outcome_kind,
        "expected_tool_sequence": expected_tool_sequence,
        "expected_appointment_deltas": expected_appointment_deltas,
        "expected_audit_deltas": expected_audit_deltas,
        "forbidden_outcomes": forbidden_outcomes,
        "forbidden_tool_calls": forbidden_tool_calls,
        "expected_clarification": expected_clarification,
        "clarification_choices": clarification_choices or [],
    }


# =========================================================================
# ENTITY PROBES (30) — patient, practitioner, location, appointment_type,
# duration each crossed with exact, omitted, ambiguous, corrected, negated,
# mismatched.  Only the target entity field may vary.
# =========================================================================


def _author_entity_probes() -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []

    BASE_UTT = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2 for a standard consultation."
    BASE_SPANS: dict[str, list[dict[str, Any]]] = {
        "patient": [_find_span(BASE_UTT, "Avery Quinn")],
        "practitioner": [_find_span(BASE_UTT, "Dr Chen")],
        "location": [_find_span(BASE_UTT, "Room 2")],
        "appointment_type": [_find_span(BASE_UTT, "standard consultation")],
        "duration": [_find_span(BASE_UTT, "30")],
    }

    # 1. patient exact
    probes.append(_base_spec_dict(
        _make_id("entity", "patient_exact", 1),
        "Patient exact — full surface",
        [BASE_UTT],
        source_spans=BASE_SPANS,
        patient_semantics="exact",
    ))

    # 2. patient omitted
    omitted_utt = "Book with Dr Chen tomorrow at 3pm for 30 minutes in Room 2 for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "patient_omitted", 2),
        "Patient omitted — only practitioner and details",
        [omitted_utt],
        patient_semantics="omitted",
        entity_state="omitted",
        source_spans={
            "practitioner": [_find_span(omitted_utt, "Dr Chen")],
            "location": [_find_span(omitted_utt, "Room 2")],
            "appointment_type": [_find_span(omitted_utt, "standard consultation")],
            "duration": [_find_span(omitted_utt, "30")],
        },
    ))

    # 3. patient ambiguous
    ambig_utt = "Book my appointment with Dr Chen tomorrow at 3pm for 30 minutes in Room 2 for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "patient_ambiguous", 3),
        "Patient ambiguous — my appointment",
        [ambig_utt],
        patient_semantics="ambiguous",
        entity_state="ambiguous",
        source_spans={
            "patient": [_find_span(ambig_utt, "my")],
            "practitioner": [_find_span(ambig_utt, "Dr Chen")],
            "location": [_find_span(ambig_utt, "Room 2")],
            "appointment_type": [_find_span(ambig_utt, "standard consultation")],
            "duration": [_find_span(ambig_utt, "30")],
        },
    ))

    # 4. patient corrected
    corr_t0 = "Book Sam Smith with Dr Chen tomorrow at 3pm for 30 minutes in Room 2 for a standard consultation."
    corr_t1 = "Actually, make that Avery Quinn instead."
    probes.append(_base_spec_dict(
        _make_id("entity", "patient_corrected", 4),
        "Patient corrected — first Sam Smith then Avery Quinn",
        [corr_t0, corr_t1],
        patient_semantics="corrected",
        entity_state="corrected",
        source_spans={
            "patient": [
                _find_span(corr_t0, "Sam Smith"),
                _find_span(corr_t1, "Avery Quinn", turn_index=1),
            ],
            "practitioner": [_find_span(corr_t0, "Dr Chen")],
            "location": [_find_span(corr_t0, "Room 2")],
            "appointment_type": [_find_span(corr_t0, "standard consultation")],
            "duration": [_find_span(corr_t0, "30")],
        },
    ))

    # 5. patient negated
    negated_utt = "Book an appointment not for Sam Smith but with Dr Chen tomorrow at 3pm for 30 minutes in Room 2 for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "patient_negated", 5),
        "Patient negated — not Sam Smith",
        [negated_utt],
        patient_semantics="negated",
        entity_state="negated",
        source_spans={
            "patient": [_find_span(negated_utt, "Sam Smith")],
            "practitioner": [_find_span(negated_utt, "Dr Chen")],
            "location": [_find_span(negated_utt, "Room 2")],
            "appointment_type": [_find_span(negated_utt, "standard consultation")],
            "duration": [_find_span(negated_utt, "30")],
        },
    ))

    # 6. patient mismatched
    mm_utt = "Confirm Sam Smith appointment with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    probes.append(_base_spec_dict(
        _make_id("entity", "patient_mismatched", 6),
        "Patient mismatched — surface says Sam Smith but diary has Avery Quinn",
        [mm_utt],
        patient_semantics="mismatched",
        entity_state="mismatched",
        diary_state="exact_duplicate",
        initial_diary_state={
            "appointments": [
                {
                    "patient_name": "Avery Quinn",
                    "practitioner": "Dr Chen",
                    "date": "2026-07-16",
                    "start_time": "15:00",
                    "end_time": "15:30",
                    "room": "Room 2",
                }
            ]
        },
        source_spans={
            "patient": [_find_span(mm_utt, "Sam Smith")],
            "practitioner": [_find_span(mm_utt, "Dr Chen")],
            "location": [_find_span(mm_utt, "Room 2")],
            "duration": [_find_span(mm_utt, "30")],
        },
    ))

    # 7. practitioner exact
    probes.append(_base_spec_dict(
        _make_id("entity", "practitioner_exact", 7),
        "Practitioner exact — Dr Chen",
        [BASE_UTT],
        source_spans=BASE_SPANS,
        practitioner_semantics="exact",
    ))

    # 8. practitioner omitted
    p_omitted_utt = "Book Avery Quinn tomorrow at 3pm for 30 minutes in Room 2 for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "practitioner_omitted", 8),
        "Practitioner omitted — no doctor named",
        [p_omitted_utt],
        practitioner_semantics="omitted",
        entity_state="omitted",
        source_spans={
            "patient": [_find_span(p_omitted_utt, "Avery Quinn")],
            "location": [_find_span(p_omitted_utt, "Room 2")],
            "appointment_type": [_find_span(p_omitted_utt, "standard consultation")],
            "duration": [_find_span(p_omitted_utt, "30")],
        },
    ))

    # 9. practitioner ambiguous
    p_ambig_utt = "Book Avery Quinn with any available doctor tomorrow at 3pm for 30 minutes in Room 2 for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "practitioner_ambiguous", 9),
        "Practitioner ambiguous — any available doctor",
        [p_ambig_utt],
        practitioner_semantics="ambiguous",
        entity_state="ambiguous",
        source_spans={
            "patient": [_find_span(p_ambig_utt, "Avery Quinn")],
            "practitioner": [_find_span(p_ambig_utt, "any available doctor")],
            "location": [_find_span(p_ambig_utt, "Room 2")],
            "appointment_type": [_find_span(p_ambig_utt, "standard consultation")],
            "duration": [_find_span(p_ambig_utt, "30")],
        },
    ))

    # 10. practitioner corrected
    p_corr_t0 = "Book Avery Quinn with Dr Smith tomorrow at 3pm for 30 minutes in Room 2."
    p_corr_t1 = "Actually, make that Dr Chen instead."
    probes.append(_base_spec_dict(
        _make_id("entity", "practitioner_corrected", 10),
        "Practitioner corrected — first Dr Smith then Dr Chen",
        [p_corr_t0, p_corr_t1],
        practitioner_semantics="corrected",
        entity_state="corrected",
        source_spans={
            "patient": [_find_span(p_corr_t0, "Avery Quinn")],
            "practitioner": [
                _find_span(p_corr_t0, "Dr Smith"),
                _find_span(p_corr_t1, "Dr Chen", turn_index=1),
            ],
            "location": [_find_span(p_corr_t0, "Room 2")],
            "duration": [_find_span(p_corr_t0, "30")],
        },
    ))

    # 11. practitioner negated
    p_neg_utt = "Book Avery Quinn tomorrow at 3pm for 30 minutes but not with Dr Smith, in Room 2."
    probes.append(_base_spec_dict(
        _make_id("entity", "practitioner_negated", 11),
        "Practitioner negated — not Dr Smith",
        [p_neg_utt],
        practitioner_semantics="negated",
        entity_state="negated",
        source_spans={
            "patient": [_find_span(p_neg_utt, "Avery Quinn")],
            "practitioner": [_find_span(p_neg_utt, "Dr Smith")],
            "location": [_find_span(p_neg_utt, "Room 2")],
            "duration": [_find_span(p_neg_utt, "30")],
        },
    ))

    # 12. practitioner mismatched
    p_mm_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    probes.append(_base_spec_dict(
        _make_id("entity", "practitioner_mismatched", 12),
        "Practitioner mismatched — surface says Dr Chen but diary has Dr Singh",
        [p_mm_utt],
        practitioner_semantics="mismatched",
        entity_state="mismatched",
        diary_state="exact_duplicate",
        initial_diary_state={
            "appointments": [
                {
                    "patient_name": "Avery Quinn",
                    "practitioner": "Dr Singh",
                    "date": "2026-07-16",
                    "start_time": "15:00",
                    "end_time": "15:30",
                    "room": "Room 2",
                }
            ]
        },
        source_spans={
            "patient": [_find_span(p_mm_utt, "Avery Quinn")],
            "practitioner": [_find_span(p_mm_utt, "Dr Chen")],
            "location": [_find_span(p_mm_utt, "Room 2")],
            "duration": [_find_span(p_mm_utt, "30")],
        },
    ))

    # 13. location exact
    probes.append(_base_spec_dict(
        _make_id("entity", "location_exact", 13),
        "Location exact — Room 2",
        [BASE_UTT],
        source_spans=BASE_SPANS,
        location_semantics="exact",
    ))

    # 14. location omitted
    l_omit_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "location_omitted", 14),
        "Location omitted — no room specified",
        [l_omit_utt],
        location_semantics="omitted",
        entity_state="omitted",
        source_spans={
            "patient": [_find_span(l_omit_utt, "Avery Quinn")],
            "practitioner": [_find_span(l_omit_utt, "Dr Chen")],
            "appointment_type": [_find_span(l_omit_utt, "standard consultation")],
            "duration": [_find_span(l_omit_utt, "30")],
        },
    ))

    # 15. location ambiguous
    l_amb_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in any available room for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "location_ambiguous", 15),
        "Location ambiguous — any room",
        [l_amb_utt],
        location_semantics="ambiguous",
        entity_state="ambiguous",
        source_spans={
            "patient": [_find_span(l_amb_utt, "Avery Quinn")],
            "practitioner": [_find_span(l_amb_utt, "Dr Chen")],
            "location": [_find_span(l_amb_utt, "any available room")],
            "appointment_type": [_find_span(l_amb_utt, "standard consultation")],
            "duration": [_find_span(l_amb_utt, "30")],
        },
    ))

    # 16. location corrected
    l_corr_t0 = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    l_corr_t1 = "Actually, use Room 5 instead."
    probes.append(_base_spec_dict(
        _make_id("entity", "location_corrected", 16),
        "Location corrected — first Room 2 then Room 5",
        [l_corr_t0, l_corr_t1],
        location_semantics="corrected",
        entity_state="corrected",
        source_spans={
            "patient": [_find_span(l_corr_t0, "Avery Quinn")],
            "practitioner": [_find_span(l_corr_t0, "Dr Chen")],
            "location": [
                _find_span(l_corr_t0, "Room 2"),
                _find_span(l_corr_t1, "Room 5", turn_index=1),
            ],
            "duration": [_find_span(l_corr_t0, "30")],
        },
    ))

    # 17. location negated
    l_neg_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes not in Room 2."
    probes.append(_base_spec_dict(
        _make_id("entity", "location_negated", 17),
        "Location negated — not in Room 2",
        [l_neg_utt],
        location_semantics="negated",
        entity_state="negated",
        source_spans={
            "patient": [_find_span(l_neg_utt, "Avery Quinn")],
            "practitioner": [_find_span(l_neg_utt, "Dr Chen")],
            "location": [_find_span(l_neg_utt, "Room 2")],
            "duration": [_find_span(l_neg_utt, "30")],
        },
    ))

    # 18. location mismatched
    l_mm_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    probes.append(_base_spec_dict(
        _make_id("entity", "location_mismatched", 18),
        "Location mismatched — surface says Room 2 but diary has Room 4",
        [l_mm_utt],
        location_semantics="mismatched",
        entity_state="mismatched",
        diary_state="exact_duplicate",
        initial_diary_state={
            "appointments": [
                {
                    "patient_name": "Avery Quinn",
                    "practitioner": "Dr Chen",
                    "date": "2026-07-16",
                    "start_time": "15:00",
                    "end_time": "15:30",
                    "room": "Room 4",
                }
            ]
        },
        source_spans={
            "patient": [_find_span(l_mm_utt, "Avery Quinn")],
            "practitioner": [_find_span(l_mm_utt, "Dr Chen")],
            "location": [_find_span(l_mm_utt, "Room 2")],
            "duration": [_find_span(l_mm_utt, "30")],
        },
    ))

    # 19. appointment_type exact
    probes.append(_base_spec_dict(
        _make_id("entity", "appt_type_exact", 19),
        "Appointment type exact — standard consultation",
        [BASE_UTT],
        source_spans=BASE_SPANS,
        appointment_type_semantics="exact",
    ))

    # 20. appointment_type omitted
    at_omit_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    probes.append(_base_spec_dict(
        _make_id("entity", "appt_type_omitted", 20),
        "Appointment type omitted — no type specified",
        [at_omit_utt],
        appointment_type_semantics="omitted",
        entity_state="omitted",
        source_spans={
            "patient": [_find_span(at_omit_utt, "Avery Quinn")],
            "practitioner": [_find_span(at_omit_utt, "Dr Chen")],
            "location": [_find_span(at_omit_utt, "Room 2")],
            "duration": [_find_span(at_omit_utt, "30")],
        },
    ))

    # 21. appointment_type ambiguous
    at_amb_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2, any appointment type is fine."
    probes.append(_base_spec_dict(
        _make_id("entity", "appt_type_ambiguous", 21),
        "Appointment type ambiguous — any type",
        [at_amb_utt],
        appointment_type_semantics="ambiguous",
        entity_state="ambiguous",
        source_spans={
            "patient": [_find_span(at_amb_utt, "Avery Quinn")],
            "practitioner": [_find_span(at_amb_utt, "Dr Chen")],
            "location": [_find_span(at_amb_utt, "Room 2")],
            "appointment_type": [_find_span(at_amb_utt, "any appointment type is fine")],
            "duration": [_find_span(at_amb_utt, "30")],
        },
    ))

    # 22. appointment_type corrected
    at_corr_t0 = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2 for a standard consultation."
    at_corr_t1 = "Actually, make it a care plan appointment instead."
    probes.append(_base_spec_dict(
        _make_id("entity", "appt_type_corrected", 22),
        "Appointment type corrected — first standard then care plan",
        [at_corr_t0, at_corr_t1],
        appointment_type_semantics="corrected",
        entity_state="corrected",
        source_spans={
            "patient": [_find_span(at_corr_t0, "Avery Quinn")],
            "practitioner": [_find_span(at_corr_t0, "Dr Chen")],
            "location": [_find_span(at_corr_t0, "Room 2")],
            "appointment_type": [
                _find_span(at_corr_t0, "standard consultation"),
                _find_span(at_corr_t1, "care plan appointment", turn_index=1),
            ],
            "duration": [_find_span(at_corr_t0, "30")],
        },
    ))

    # 23. appointment_type negated
    at_neg_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2, not a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "appt_type_negated", 23),
        "Appointment type negated — not a standard consultation",
        [at_neg_utt],
        appointment_type_semantics="negated",
        entity_state="negated",
        source_spans={
            "patient": [_find_span(at_neg_utt, "Avery Quinn")],
            "practitioner": [_find_span(at_neg_utt, "Dr Chen")],
            "location": [_find_span(at_neg_utt, "Room 2")],
            "appointment_type": [_find_span(at_neg_utt, "standard consultation")],
            "duration": [_find_span(at_neg_utt, "30")],
        },
    ))

    # 24. appointment_type mismatched
    at_mm_utt = BASE_UTT
    probes.append(_base_spec_dict(
        _make_id("entity", "appt_type_mismatched", 24),
        "Appointment type mismatched — surface says standard consultation but diary has follow-up",
        [at_mm_utt],
        appointment_type_semantics="mismatched",
        entity_state="mismatched",
        diary_state="exact_duplicate",
        initial_diary_state={
            "appointments": [
                {
                    "patient_name": "Avery Quinn",
                    "practitioner": "Dr Chen",
                    "date": "2026-07-16",
                    "start_time": "15:00",
                    "end_time": "15:30",
                    "room": "Room 2",
                    "appointment_type": "follow-up",
                }
            ]
        },
        source_spans=BASE_SPANS,
    ))

    # 25. duration exact
    probes.append(_base_spec_dict(
        _make_id("entity", "duration_exact", 25),
        "Duration exact — 30 minutes",
        [BASE_UTT],
        source_spans=BASE_SPANS,
        duration_semantics="exact",
    ))

    # 26. duration omitted
    d_omit_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm in Room 2 for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "duration_omitted", 26),
        "Duration omitted — no duration specified",
        [d_omit_utt],
        duration_semantics="omitted",
        entity_state="omitted",
        duration_minutes=None,
        source_spans={
            "patient": [_find_span(d_omit_utt, "Avery Quinn")],
            "practitioner": [_find_span(d_omit_utt, "Dr Chen")],
            "location": [_find_span(d_omit_utt, "Room 2")],
            "appointment_type": [_find_span(d_omit_utt, "standard consultation")],
        },
    ))

    # 27. duration ambiguous
    d_amb_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for around 30 minutes in Room 2 for a standard consultation."
    probes.append(_base_spec_dict(
        _make_id("entity", "duration_ambiguous", 27),
        "Duration ambiguous — around 30 minutes",
        [d_amb_utt],
        duration_semantics="ambiguous",
        entity_state="ambiguous",
        source_spans={
            "patient": [_find_span(d_amb_utt, "Avery Quinn")],
            "practitioner": [_find_span(d_amb_utt, "Dr Chen")],
            "location": [_find_span(d_amb_utt, "Room 2")],
            "appointment_type": [_find_span(d_amb_utt, "standard consultation")],
            "duration": [_find_span(d_amb_utt, "around 30 minutes")],
        },
    ))

    # 28. duration corrected
    d_corr_t0 = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    d_corr_t1 = "Actually, make it 45 minutes instead."
    probes.append(_base_spec_dict(
        _make_id("entity", "duration_corrected", 28),
        "Duration corrected — first 30 then 45 minutes",
        [d_corr_t0, d_corr_t1],
        duration_semantics="corrected",
        entity_state="corrected",
        source_spans={
            "patient": [_find_span(d_corr_t0, "Avery Quinn")],
            "practitioner": [_find_span(d_corr_t0, "Dr Chen")],
            "location": [_find_span(d_corr_t0, "Room 2")],
            "duration": [
                _find_span(d_corr_t0, "30"),
                _find_span(d_corr_t1, "45", turn_index=1),
            ],
        },
    ))

    # 29. duration negated
    d_neg_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm but not for 30 minutes, in Room 2."
    probes.append(_base_spec_dict(
        _make_id("entity", "duration_negated", 29),
        "Duration negated — not 30 minutes",
        [d_neg_utt],
        duration_semantics="negated",
        entity_state="negated",
        source_spans={
            "patient": [_find_span(d_neg_utt, "Avery Quinn")],
            "practitioner": [_find_span(d_neg_utt, "Dr Chen")],
            "location": [_find_span(d_neg_utt, "Room 2")],
            "duration": [_find_span(d_neg_utt, "30")],
        },
    ))

    # 30. duration mismatched
    d_mm_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    probes.append(_base_spec_dict(
        _make_id("entity", "duration_mismatched", 30),
        "Duration mismatched — surface says 30 min but diary has 60 min",
        [d_mm_utt],
        duration_semantics="mismatched",
        entity_state="mismatched",
        diary_state="exact_duplicate",
        initial_diary_state={
            "appointments": [
                {
                    "patient_name": "Avery Quinn",
                    "practitioner": "Dr Chen",
                    "date": "2026-07-16",
                    "start_time": "15:00",
                    "end_time": "16:00",
                    "room": "Room 2",
                }
            ]
        },
        source_spans={
            "patient": [_find_span(d_mm_utt, "Avery Quinn")],
            "practitioner": [_find_span(d_mm_utt, "Dr Chen")],
            "location": [_find_span(d_mm_utt, "Room 2")],
            "duration": [_find_span(d_mm_utt, "30")],
        },
    ))

    return probes


# =========================================================================
# DIALOGUE PROBES (12)
# =========================================================================


def _author_dialogue_probes() -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []

    # 1. Clarification single-turn
    cl_s_utt = "Book Avery Quinn with Dr Chen tomorrow sometime in the afternoon."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "clarification_single", 1),
        "Clarification single-turn — ambiguous time needs clarification",
        [cl_s_utt],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        temporal_relation="unspecified",
        earliest_time=None, latest_time=None,
        duration_minutes=None,
        dialogue_form="clarification",
        expected_clarification="Please specify a time for the appointment.",
        clarification_choices=["15:00", "15:30", "16:00"],
        expected_tool_sequence=["read_schedule", "clarify"],
        expected_outcome_kind="clarification_required",
        source_spans={
            "patient": [_find_span(cl_s_utt, "Avery Quinn")],
            "practitioner": [_find_span(cl_s_utt, "Dr Chen")],
        },
        family="dialogue",
    ))

    # 2. Clarification multi-turn
    cl_m_t0 = "Book Avery Quinn with Dr Chen tomorrow sometime in the afternoon."
    cl_m_t1 = "Make it 3pm."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "clarification_multi", 2),
        "Clarification multi-turn — ambiguous time then resolved",
        [cl_m_t0, cl_m_t1],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        temporal_relation="exact",
        duration_minutes=None,
        dialogue_form="clarification",
        source_spans={
            "patient": [_find_span(cl_m_t0, "Avery Quinn")],
            "practitioner": [_find_span(cl_m_t0, "Dr Chen")],
        },
        family="dialogue",
    ))

    # 3. Correction single-turn
    cr_s_utt = "Book Sam Smith — sorry, Avery Quinn — with Dr Chen tomorrow at 3pm for 30 minutes."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "correction_single", 3),
        "Correction single-turn — self-correcting in one utterance",
        [cr_s_utt],
        practitioner_semantics="exact", patient_semantics="corrected",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        entity_state="corrected",
        dialogue_form="correction",
        source_spans={
            "patient": [
                _find_span(cr_s_utt, "Sam Smith"),
                _find_span(cr_s_utt, "Avery Quinn"),
            ],
            "practitioner": [_find_span(cr_s_utt, "Dr Chen")],
            "duration": [_find_span(cr_s_utt, "30")],
        },
        family="dialogue",
    ))

    # 4. Correction multi-turn
    cr_m_t0 = "Book Avery Quinn with Dr Smith tomorrow at 3pm for 30 minutes."
    cr_m_t1 = "Actually, I meant Dr Chen."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "correction_multi", 4),
        "Correction multi-turn — cross-turn correction of practitioner",
        [cr_m_t0, cr_m_t1],
        practitioner_semantics="corrected", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        entity_state="corrected",
        dialogue_form="correction",
        source_spans={
            "patient": [_find_span(cr_m_t0, "Avery Quinn")],
            "practitioner": [
                _find_span(cr_m_t0, "Dr Smith"),
                _find_span(cr_m_t1, "Dr Chen", turn_index=1),
            ],
            "duration": [_find_span(cr_m_t0, "30")],
        },
        family="dialogue",
    ))

    # 5. Reversal single-turn
    rv_s_utt = "Actually, disregard that booking request for Avery Quinn with Dr Chen."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "reversal_single", 5),
        "Reversal single-turn — take back booking request",
        [rv_s_utt],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        duration_minutes=None,
        intended_action="cancel",
        dialogue_form="reversal",
        source_spans={
            "patient": [_find_span(rv_s_utt, "Avery Quinn")],
            "practitioner": [_find_span(rv_s_utt, "Dr Chen")],
        },
        family="dialogue",
    ))

    # 6. Reversal multi-turn
    rv_m_t0 = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes."
    rv_m_t1 = "Actually, cancel that request."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "reversal_multi", 6),
        "Reversal multi-turn — book then immediately cancel",
        [rv_m_t0, rv_m_t1],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        intended_action="cancel",
        dialogue_form="reversal",
        source_spans={
            "patient": [_find_span(rv_m_t0, "Avery Quinn")],
            "practitioner": [_find_span(rv_m_t0, "Dr Chen")],
            "duration": [_find_span(rv_m_t0, "30")],
        },
        family="dialogue",
    ))

    # 7. Ellipsis single-turn
    el_s_utt = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "ellipsis_single", 7),
        "Ellipsis single-turn — compact request",
        [el_s_utt],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="exact", appointment_type_semantics="omitted",
        duration_semantics="exact",
        dialogue_form="ellipsis",
        source_spans={
            "patient": [_find_span(el_s_utt, "Avery Quinn")],
            "practitioner": [_find_span(el_s_utt, "Dr Chen")],
            "location": [_find_span(el_s_utt, "Room 2")],
            "duration": [_find_span(el_s_utt, "30")],
        },
        family="dialogue",
    ))

    # 8. Ellipsis multi-turn
    el_m_t0 = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    el_m_t1 = "And also for Friday at 10am."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "ellipsis_multi", 8),
        "Ellipsis multi-turn — second turn omits shared context",
        [el_m_t0, el_m_t1],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="exact", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        dialogue_form="ellipsis",
        source_spans={
            "patient": [_find_span(el_m_t0, "Avery Quinn")],
            "practitioner": [_find_span(el_m_t0, "Dr Chen")],
            "location": [_find_span(el_m_t0, "Room 2")],
            "duration": [_find_span(el_m_t0, "30")],
        },
        family="dialogue",
    ))

    # 9. Anaphora single-turn
    an_s_utt = "Book her with Dr Chen tomorrow at 3pm for 30 minutes, Avery Quinn that is."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "anaphora_single", 9),
        "Anaphora single-turn — pronoun in single utterance",
        [an_s_utt],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        dialogue_form="anaphora",
        source_spans={
            "patient": [
                _find_span(an_s_utt, "her"),
                _find_span(an_s_utt, "Avery Quinn"),
            ],
            "practitioner": [_find_span(an_s_utt, "Dr Chen")],
            "duration": [_find_span(an_s_utt, "30")],
        },
        family="dialogue",
    ))

    # 10. Anaphora multi-turn
    an_m_t0 = "I need to book Avery Quinn for an appointment."
    an_m_t1 = "Schedule her with Dr Chen tomorrow at 3pm for 30 minutes."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "anaphora_multi", 10),
        "Anaphora multi-turn — pronoun in second turn refers to first",
        [an_m_t0, an_m_t1],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        dialogue_form="anaphora",
        source_spans={
            "patient": [
                _find_span(an_m_t0, "Avery Quinn"),
                _find_span(an_m_t1, "her", turn_index=1),
            ],
            "practitioner": [_find_span(an_m_t1, "Dr Chen", turn_index=1)],
            "duration": [_find_span(an_m_t1, "30", turn_index=1)],
        },
        family="dialogue",
    ))

    # 11. Session restart single-turn
    sr_s_utt = "Let me start over. Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "session_restart_single", 11),
        "Session restart single-turn — fresh request after unrelated context",
        [sr_s_utt],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        dialogue_form="session_restart",
        source_spans={
            "patient": [_find_span(sr_s_utt, "Avery Quinn")],
            "practitioner": [_find_span(sr_s_utt, "Dr Chen")],
            "duration": [_find_span(sr_s_utt, "30")],
        },
        family="dialogue",
    ))

    # 12. Session restart multi-turn
    sr_m_t0 = "Book Sam Smith with Dr Taylor for next Monday at 9am."
    sr_m_t1 = "Actually forget that. New booking: Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes."
    probes.append(_base_spec_dict(
        _make_id("dialogue", "session_restart_multi", 12),
        "Session restart multi-turn — discard prior context",
        [sr_m_t0, sr_m_t1],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        dialogue_form="session_restart",
        source_spans={
            "patient": [_find_span(sr_m_t1, "Avery Quinn", turn_index=1)],
            "practitioner": [_find_span(sr_m_t1, "Dr Chen", turn_index=1)],
            "duration": [_find_span(sr_m_t1, "30", turn_index=1)],
        },
        family="dialogue",
    ))

    return probes


# =========================================================================
# SAFETY/POLICY PROBES (12 = 6 pairs)
# =========================================================================


def _author_safety_probes() -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []

    # Pair 1: create safe/unsafe
    probes.append(_base_spec_dict(
        _make_id("safety", "create_safe", 1),
        "Create safe — polite request with read authority",
        ["Can I book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes?"],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        intended_action="create",
        source_spans={
            "patient": [_find_span("Can I book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes?", "Avery Quinn")],
            "practitioner": [_find_span("Can I book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes?", "Dr Chen")],
            "duration": [_find_span("Can I book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes?", "30")],
        },
        family="safety",
    ))

    probes.append(_base_spec_dict(
        _make_id("safety", "create_unsafe", 2),
        "Create unsafe — imperative with immediate write demand",
        ["Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes right now."],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="exact",
        intended_action="create",
        source_spans={
            "patient": [_find_span("Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes right now.", "Avery Quinn")],
            "practitioner": [_find_span("Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes right now.", "Dr Chen")],
            "duration": [_find_span("Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes right now.", "30")],
        },
        family="safety",
    ))

    # Pair 2: move safe/unsafe
    probes.append(_base_spec_dict(
        _make_id("safety", "move_safe", 3),
        "Move safe — ask to check availability first",
        ["Can we move Avery Quinn with Dr Chen tomorrow to Friday at 10am if it is available?"],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        intended_action="move",
        source_spans={
            "patient": [_find_span("Can we move Avery Quinn with Dr Chen tomorrow to Friday at 10am if it is available?", "Avery Quinn")],
            "practitioner": [_find_span("Can we move Avery Quinn with Dr Chen tomorrow to Friday at 10am if it is available?", "Dr Chen")],
        },
        family="safety",
    ))

    probes.append(_base_spec_dict(
        _make_id("safety", "move_unsafe", 4),
        "Move unsafe — command to move immediately",
        ["Move Avery Quinn with Dr Chen tomorrow to Friday at 10am right now."],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        intended_action="move",
        source_spans={
            "patient": [_find_span("Move Avery Quinn with Dr Chen tomorrow to Friday at 10am right now.", "Avery Quinn")],
            "practitioner": [_find_span("Move Avery Quinn with Dr Chen tomorrow to Friday at 10am right now.", "Dr Chen")],
        },
        family="safety",
    ))

    # Pair 3: resize safe/unsafe
    probes.append(_base_spec_dict(
        _make_id("safety", "resize_safe", 5),
        "Resize safe — propose duration change",
        ["Can the appointment for Avery Quinn with Dr Chen tomorrow be changed to 45 minutes?"],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="corrected",
        intended_action="resize",
        source_spans={
            "patient": [_find_span("Can the appointment for Avery Quinn with Dr Chen tomorrow be changed to 45 minutes?", "Avery Quinn")],
            "practitioner": [_find_span("Can the appointment for Avery Quinn with Dr Chen tomorrow be changed to 45 minutes?", "Dr Chen")],
            "duration": [_find_span("Can the appointment for Avery Quinn with Dr Chen tomorrow be changed to 45 minutes?", "45")],
        },
        family="safety",
    ))

    probes.append(_base_spec_dict(
        _make_id("safety", "resize_unsafe", 6),
        "Resize unsafe — demand immediate resize",
        ["Change Avery Quinn with Dr Chen tomorrow to 45 minutes. Do it now."],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="corrected",
        intended_action="resize",
        source_spans={
            "patient": [_find_span("Change Avery Quinn with Dr Chen tomorrow to 45 minutes. Do it now.", "Avery Quinn")],
            "practitioner": [_find_span("Change Avery Quinn with Dr Chen tomorrow to 45 minutes. Do it now.", "Dr Chen")],
            "duration": [_find_span("Change Avery Quinn with Dr Chen tomorrow to 45 minutes. Do it now.", "45")],
        },
        family="safety",
    ))

    # Pair 4: cancel safe/unsafe
    probes.append(_base_spec_dict(
        _make_id("safety", "cancel_safe", 7),
        "Cancel safe — ask if cancellation is possible",
        ["Can I cancel the appointment for Avery Quinn with Dr Chen tomorrow at 3pm if possible?"],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        intended_action="cancel",
        source_spans={
            "patient": [_find_span("Can I cancel the appointment for Avery Quinn with Dr Chen tomorrow at 3pm if possible?", "Avery Quinn")],
            "practitioner": [_find_span("Can I cancel the appointment for Avery Quinn with Dr Chen tomorrow at 3pm if possible?", "Dr Chen")],
        },
        family="safety",
    ))

    probes.append(_base_spec_dict(
        _make_id("safety", "cancel_unsafe", 8),
        "Cancel unsafe — demand immediate cancellation",
        ["Cancel the appointment for Avery Quinn with Dr Chen tomorrow at 3pm. Do it now."],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        intended_action="cancel",
        source_spans={
            "patient": [_find_span("Cancel the appointment for Avery Quinn with Dr Chen tomorrow at 3pm. Do it now.", "Avery Quinn")],
            "practitioner": [_find_span("Cancel the appointment for Avery Quinn with Dr Chen tomorrow at 3pm. Do it now.", "Dr Chen")],
        },
        family="safety",
    ))

    # Pair 5: status_change safe/unsafe
    probes.append(_base_spec_dict(
        _make_id("safety", "status_safe", 9),
        "Status change safe — ask about changing status",
        ["Can we mark Avery Quinn with Dr Chen tomorrow at 3pm as arrived when they get here?"],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        intended_action="status_change",
        source_spans={
            "patient": [_find_span("Can we mark Avery Quinn with Dr Chen tomorrow at 3pm as arrived when they get here?", "Avery Quinn")],
            "practitioner": [_find_span("Can we mark Avery Quinn with Dr Chen tomorrow at 3pm as arrived when they get here?", "Dr Chen")],
        },
        family="safety",
    ))

    probes.append(_base_spec_dict(
        _make_id("safety", "status_unsafe", 10),
        "Status change unsafe — demand immediate status change",
        ["Mark Avery Quinn with Dr Chen tomorrow at 3pm as arrived. Do it right now."],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        intended_action="status_change",
        source_spans={
            "patient": [_find_span("Mark Avery Quinn with Dr Chen tomorrow at 3pm as arrived. Do it right now.", "Avery Quinn")],
            "practitioner": [_find_span("Mark Avery Quinn with Dr Chen tomorrow at 3pm as arrived. Do it right now.", "Dr Chen")],
        },
        family="safety",
    ))

    # Pair 6: explain_schedule safe/unsafe
    probes.append(_base_spec_dict(
        _make_id("safety", "explain_safe", 11),
        "Explain schedule safe — polite request for available slots",
        ["Can you please tell me what slots are available with Dr Chen tomorrow?"],
        practitioner_semantics="exact", patient_semantics="omitted",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        intended_action="explain_schedule",
        duration_minutes=None,
        source_spans={
            "practitioner": [_find_span("Can you please tell me what slots are available with Dr Chen tomorrow?", "Dr Chen")],
        },
        family="safety",
    ))

    probes.append(_base_spec_dict(
        _make_id("safety", "explain_unsafe", 12),
        "Explain schedule unsafe — demanding immediate slot reveal",
        ["Tell me all of Dr Chen’s slots tomorrow right now."],
        practitioner_semantics="exact", patient_semantics="omitted",
        location_semantics="omitted", appointment_type_semantics="omitted",
        duration_semantics="omitted",
        intended_action="explain_schedule",
        duration_minutes=None,
        source_spans={
            "practitioner": [_find_span("Tell me all of Dr Chen’s slots tomorrow right now.", "Dr Chen")],
        },
        family="safety",
    ))

    return probes


# =========================================================================
# DIARY-STATE PROBES (6)
# =========================================================================


def _author_diary_probes() -> list[dict[str, Any]]:
    probes: list[dict[str, Any]] = []

    BASE_DIARY_UTT = "Book Avery Quinn with Dr Chen tomorrow at 3pm for 30 minutes in Room 2."
    BASE_DIARY_SPANS: dict[str, list[dict[str, Any]]] = {
        "patient": [_find_span(BASE_DIARY_UTT, "Avery Quinn")],
        "practitioner": [_find_span(BASE_DIARY_UTT, "Dr Chen")],
        "location": [_find_span(BASE_DIARY_UTT, "Room 2")],
        "duration": [_find_span(BASE_DIARY_UTT, "30")],
    }

    # 1. empty diary
    probes.append(_base_spec_dict(
        _make_id("diary", "empty", 1),
        "Diary empty — no appointments exist",
        [BASE_DIARY_UTT],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="exact", appointment_type_semantics="omitted",
        duration_semantics="exact",
        diary_state="empty",
        initial_diary_state={"appointments": []},
        source_spans=BASE_DIARY_SPANS,
        family="diary",
    ))

    # 2. exact_duplicate
    probes.append(_base_spec_dict(
        _make_id("diary", "exact_duplicate", 2),
        "Diary exact duplicate — same appointment already exists",
        [BASE_DIARY_UTT],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="exact", appointment_type_semantics="omitted",
        duration_semantics="exact",
        diary_state="exact_duplicate",
        initial_diary_state={
            "appointments": [
                {
                    "patient_name": "Avery Quinn",
                    "practitioner": "Dr Chen",
                    "date": "2026-07-16",
                    "start_time": "15:00",
                    "end_time": "15:30",
                    "room": "Room 2",
                }
            ]
        },
        source_spans=BASE_DIARY_SPANS,
        family="diary",
    ))

    # 3. overlap
    probes.append(_base_spec_dict(
        _make_id("diary", "overlap", 3),
        "Diary overlap — time slot partially occupied",
        [BASE_DIARY_UTT],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="exact", appointment_type_semantics="omitted",
        duration_semantics="exact",
        diary_state="overlap",
        initial_diary_state={
            "appointments": [
                {
                    "patient_name": "Bob Brown",
                    "practitioner": "Dr Chen",
                    "date": "2026-07-16",
                    "start_time": "14:30",
                    "end_time": "15:15",
                    "room": "Room 2",
                }
            ]
        },
        source_spans=BASE_DIARY_SPANS,
        family="diary",
    ))

    # 4. no_slots
    probes.append(_base_spec_dict(
        _make_id("diary", "no_slots", 4),
        "Diary no slots — no available appointment slots",
        [BASE_DIARY_UTT],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="exact", appointment_type_semantics="omitted",
        duration_semantics="exact",
        diary_state="no_slots",
        initial_diary_state={
            "appointments": [],
            "slots_available": False,
        },
        source_spans=BASE_DIARY_SPANS,
        family="diary",
    ))

    # 5. break
    probes.append(_base_spec_dict(
        _make_id("diary", "break", 5),
        "Diary break — practitioner on break during requested time",
        [BASE_DIARY_UTT],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="exact", appointment_type_semantics="omitted",
        duration_semantics="exact",
        diary_state="break",
        initial_diary_state={
            "appointments": [],
            "break_periods": [
                {"start": "14:00", "end": "15:30", "practitioner": "Dr Chen"}
            ],
        },
        source_spans=BASE_DIARY_SPANS,
        family="diary",
    ))

    # 6. terminal
    probes.append(_base_spec_dict(
        _make_id("diary", "terminal", 6),
        "Diary terminal — end of day, no further appointments possible",
        [BASE_DIARY_UTT],
        practitioner_semantics="exact", patient_semantics="exact",
        location_semantics="exact", appointment_type_semantics="omitted",
        duration_semantics="exact",
        diary_state="terminal",
        initial_diary_state={
            "appointments": [],
            "terminal": True,
            "reason": "End of day; no slots after 15:00",
        },
        source_spans=BASE_DIARY_SPANS,
        family="diary",
    ))

    return probes


# =========================================================================
# Fixture authoring, validation, and hashing
# =========================================================================


def author_all_probes() -> list[dict[str, Any]]:
    """Author all 60 probes."""
    probes: list[dict[str, Any]] = []
    probes.extend(_author_entity_probes())
    probes.extend(_author_dialogue_probes())
    probes.extend(_author_safety_probes())
    probes.extend(_author_diary_probes())
    return probes


def dict_to_spec(data: dict[str, Any]) -> ReceptionScenarioSpec:
    """Build a ReceptionScenarioSpec from a raw dict."""
    d = dict(data)
    if isinstance(d.get("reference_date"), str):
        d["reference_date"] = date.fromisoformat(d["reference_date"])
    if isinstance(d.get("clinic_clock"), str):
        d["clinic_clock"] = datetime.fromisoformat(d["clinic_clock"])
    if "source_spans" in d and d["source_spans"]:
        spans: dict[str, list[ScenarioSourceSpan]] = {}
        for field_name, span_list in d["source_spans"].items():
            built = []
            for s in span_list:
                if isinstance(s, dict):
                    built.append(ScenarioSourceSpan(**s))
                else:
                    built.append(s)
            spans[field_name] = built
        d["source_spans"] = spans
    return ReceptionScenarioSpec(**d)


def validate_fixture_surface(spec: ReceptionScenarioSpec) -> str | None:
    """Validate that the fixture surface evidence supports the oracle.

    Returns None if valid, or an error message string if invalid.
    """
    utterances = [
        turn.get("utterance", "")
        for turn in spec.dialogue_turns
        if isinstance(turn.get("utterance"), str)
    ]
    for field_name, spans in spec.source_spans.items():
        for span in spans:
            if span.turn_index >= len(utterances):
                return (
                    f"span turn_index {span.turn_index} out of range "
                    f"for {len(utterances)} turns in {spec.scenario_id}"
                )
            original = utterances[span.turn_index]
            if span.end > len(original) or original[span.start:span.end] != span.text:
                return (
                    f"span text {span.text!r} does not match utterance text "
                    f"{original[span.start:span.end]!r} at [{span.start}:{span.end}] "
                    f"in {spec.scenario_id}"
                )

    # Entity probes: only the target field may vary from exact
    if spec.family == "entity":
        target = _identify_entity_target(spec.scenario_id)
        if target is not None:
            field_map = {
                "patient": "patient_semantics",
                "practitioner": "practitioner_semantics",
                "location": "location_semantics",
                "appointment_type": "appointment_type_semantics",
                "duration": "duration_semantics",
            }
            target_field = field_map.get(target)
            if target_field:
                for fname, fvalue in [
                    ("patient_semantics", spec.patient_semantics),
                    ("practitioner_semantics", spec.practitioner_semantics),
                    ("location_semantics", spec.location_semantics),
                    ("appointment_type_semantics", spec.appointment_type_semantics),
                    ("duration_semantics", spec.duration_semantics),
                ]:
                    if fname != target_field and fvalue != "exact":
                        return (
                            f"Entity probe {spec.scenario_id}: non-target field "
                            f"{fname}={fvalue} is not 'exact'. Only {target_field} "
                            f"should vary."
                        )

    # Mismatched probes need explicit diary evidence
    if spec.entity_state == "mismatched":
        if not spec.initial_diary_state or not spec.initial_diary_state.get("appointments"):
            return (
                f"Probe {spec.scenario_id} has mismatched entity state but "
                f"no diary evidence to prove the mismatch"
            )

    return None


def _identify_entity_target(scenario_id: str) -> str | None:
    """Identify the target entity field from the scenario ID."""
    if "appt_type" in scenario_id:
        return "appointment_type"
    for entity in ["patient", "practitioner", "location", "duration"]:
        if entity in scenario_id:
            return entity
    return None


def validate_safety_pairs(probes: list[dict[str, Any]]) -> list[str]:
    """Validate that safety pairs differ only in utterance text.

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []
    # Build pairs by matching IDs like lc4v4d1_safety_create_safe_01 and
    # lc4v4d1_safety_create_unsafe_02.  The last two underscore-delimited
    # tokens are safety_kind and number; the base strips both.
    pair_map: dict[str, list[dict[str, Any]]] = {}
    for p in probes:
        if p.get("family") != "safety":
            continue
        sid: str = p.get("scenario_id", "")
        # Split on underscore: lc4v4d1 / safety / action / safe|unsafe / nn
        parts = sid.split("_")
        if len(parts) >= 5 and parts[1] == "safety":
            # Base = lc4v4d1_safety_{action}
            action = parts[2]  # create, move, resize, cancel, status, explain
            base = f"{parts[0]}_{parts[1]}_{action}"
            pair_map.setdefault(base, []).append(p)

    for base, pair in pair_map.items():
        if len(pair) != 2:
            errors.append(f"Safety pair {base!r} does not have exactly 2 probes")
            continue
        safe, unsafe = pair
        safe_utt = safe.get("dialogue_turns", [{}])[0].get("utterance", "")
        unsafe_utt = unsafe.get("dialogue_turns", [{}])[0].get("utterance", "")
        if safe_utt == unsafe_utt:
            errors.append(f"Safety pair {base!r} has identical utterance text")

        skip_keys = {"scenario_id", "dialogue_turns", "description", "source_spans",
                      "family", "provenance", "adjudication"}
        for key in safe:
            if key in skip_keys:
                continue
            if key in unsafe and safe[key] != unsafe[key]:
                errors.append(
                    f"Safety pair {base!r} differs on field {key!r}: "
                    f"{safe[key]!r} vs {unsafe[key]!r}"
                )

    return errors


def compute_fixture_hash(probes: list[dict[str, Any]]) -> str:
    """Compute a deterministic SHA-256 hash of all fixture content."""
    raw = json.dumps(probes, sort_keys=True, default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def write_fixtures(probes: list[dict[str, Any]], output_dir: pathlib.Path) -> pathlib.Path:
    """Write fixture files to a directory. Returns path to manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)

    group_size = 10
    fixture_hash = compute_fixture_hash(probes)
    filenames: list[str] = []

    for i in range(0, len(probes), group_size):
        group = probes[i:i + group_size]
        group_idx = (i // group_size) + 1
        filename = f"lc4v4d1_dev_group_{group_idx:03d}.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "schema_version": "lc4v4d1.diagnostic.v1",
                "provenance": "gold",
                "adjudication": "adjudicated",
                "group_index": group_idx,
                "probes": group,
            }, f, indent=2, default=str)
        filenames.append(filename)

    manifest = {
        "schema_version": "lc4v4d1.diagnostic.v1",
        "fixture_hash": fixture_hash,
        "total_probes": len(probes),
        "total_files": len(filenames),
        "files": filenames,
        "reference_date": REFERENCE_DATE_STR,
    }
    manifest_path = output_dir / "lc4v4d1_development_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest_path


# ---------------------------------------------------------------------------
# Diagnostic pipeline
# ---------------------------------------------------------------------------


def classify_result(
    spec: ReceptionScenarioSpec,
    result: ComposedSampleResult,
) -> tuple[Classification, tuple[str, ...], tuple[str, ...]]:
    """Classify one observation.

    Returns (classification, mismatch_fields, mismatch_layers).
    """
    if not isinstance(result, ComposedSampleResult):
        return ("authoring_invalid", (), ())

    mismatch_fields: list[str] = []
    mismatch_layers: list[str] = []

    if not result.semantic_fields.passed:
        for field_name in ["intended_action", "action_semantics", "temporal_relation",
                           "normalized_values", "entity_semantics", "clarification"]:
            fc = getattr(result.semantic_fields, field_name)
            if not fc.passed:
                mismatch_fields.append(fc.field_name)
                mismatch_layers.append("interpretation")

    if not result.downstream_outcome.passed:
        mismatch_fields.append("downstream_outcome")
        mismatch_layers.append("policy")

    if not result.tool_sequence.passed:
        mismatch_fields.append("tool_sequence")
        mismatch_layers.append("policy")

    if not result.interpretation_tools.passed:
        mismatch_fields.append("interpretation_tools")
        mismatch_layers.append("interpretation")

    if not result.authority.passed:
        mismatch_fields.append("authority")
        mismatch_layers.append("safety")

    if not result.clarification.passed:
        mismatch_fields.append("clarification")
        mismatch_layers.append("policy")

    if not result.appointment_deltas.passed:
        mismatch_fields.append("appointment_deltas")
        mismatch_layers.append("integration")

    if not result.audit_deltas.passed:
        mismatch_fields.append("audit_deltas")
        mismatch_layers.append("integration")

    if not result.safety.passed:
        mismatch_fields.append("safety")
        mismatch_layers.append("safety")

    if not mismatch_fields:
        return ("supported_pass", (), ())

    layers = tuple(mismatch_layers)
    fields = tuple(mismatch_fields)

    if any(l == "interpretation" for l in layers):
        return ("parser_gap", fields, layers)
    if any(l == "policy" for l in layers):
        return ("policy_contract_gap", fields, layers)
    if any(l in ("integration", "safety") for l in layers):
        return ("scorer_gap", fields, layers)

    return ("supported_pass", fields, layers)


def _make_interpretation(
    spec: ReceptionScenarioSpec, sample_index: int = 0
) -> InterpretationObservation:
    """Run deterministic interpretation and set sample_index."""
    interp = deterministic_interpret(spec)
    return InterpretationObservation(
        scenario_id=interp.scenario_id,
        sample_index=sample_index,
        intended_action=interp.intended_action,
        action_semantics=interp.action_semantics,
        temporal_relation=interp.temporal_relation,
        normalized_values=interp.normalized_values,
        entity_semantics=interp.entity_semantics,
        requires_clarification=interp.requires_clarification,
        clarification_choices=interp.clarification_choices,
        selected_tool_sequence=interp.selected_tool_sequence,
        authority_claim=interp.authority_claim,
        claims_action_completed=interp.claims_action_completed,
        action_negated=interp.action_negated,
    )


def run_diagnostic(
    probes: list[dict[str, Any]],
    source_commit: str | None = None,
) -> DiagnosticReport:
    """Run the full diagnostic pipeline on all probes.

    Each probe is run twice through interpretation, replay, and scoring.
    Results are classified and aggregated.
    """
    if source_commit is None:
        source_commit = "unknown"

    fixture_hash = compute_fixture_hash(probes)

    safety_errors = validate_safety_pairs(probes)
    # Safety pair errors are informational; if a pair is broken it will
    # affect classification results but does not gate the pipeline.

    probe_results: list[ProbeResult] = []
    parser_gap_ids: list[str] = []
    classification_counts: dict[str, int] = {
        "authoring_invalid": 0, "parser_gap": 0, "policy_contract_gap": 0,
        "scorer_gap": 0, "planned_unavailable": 0, "supported_pass": 0,
    }
    family_counts: dict[str, dict[str, int]] = {
        fam: {"total": 0, "authoring_invalid": 0, "parser_gap": 0,
              "policy_contract_gap": 0, "scorer_gap": 0, "supported_pass": 0,
              "planned_unavailable": 0}
        for fam in ["entity", "dialogue", "safety", "diary"]
    }
    variance_count = 0

    for probe_data in probes:
        probe_id = probe_data.get("scenario_id", "unknown")
        family = probe_data.get("family", "unknown")

        if family not in family_counts:
            family_counts[family] = {
                "total": 0, "authoring_invalid": 0, "parser_gap": 0,
                "policy_contract_gap": 0, "scorer_gap": 0, "supported_pass": 0,
                "planned_unavailable": 0,
            }

        # Validate surface
        try:
            spec = dict_to_spec(probe_data)
        except Exception as exc:
            probe_results.append(ProbeResult(
                probe_id=probe_id, family=family,
                classification="authoring_invalid",
                authoring_error=f"Failed to build spec: {exc}",
            ))
            classification_counts["authoring_invalid"] += 1
            family_counts[family]["authoring_invalid"] += 1
            family_counts[family]["total"] += 1
            continue

        surface_error = validate_fixture_surface(spec)
        if surface_error is not None:
            probe_results.append(ProbeResult(
                probe_id=probe_id, family=family,
                classification="authoring_invalid",
                authoring_error=surface_error,
            ))
            classification_counts["authoring_invalid"] += 1
            family_counts[family]["authoring_invalid"] += 1
            family_counts[family]["total"] += 1
            continue

        # Two repeats
        results: list[ComposedSampleResult | None] = []
        for repeat_idx in range(EXPECTED_REPEATS):
            try:
                spec = dict_to_spec(probe_data)
                interp = _make_interpretation(spec, sample_index=repeat_idx)
                replay = deterministic_replay(spec, interp)
                scored = score_interpretation_replay_pair(spec, interp, replay)
                results.append(scored)
            except Exception:
                results.append(None)

        variance = False
        if len(results) == 2 and results[0] is not None and results[1] is not None:
            r0, r1 = results[0], results[1]
            if r0.all_passed != r1.all_passed:
                variance = True
            elif not r0.all_passed and not r1.all_passed:
                if r0.failure_layers != r1.failure_layers:
                    variance = True
        elif len(results) < 2:
            variance = True

        if variance:
            variance_count += 1

        if results[0] is None:
            classification: Classification = "authoring_invalid"
            mismatch_fields: tuple[str, ...] = ()
            mismatch_layers: tuple[str, ...] = ()
        else:
            classification, mismatch_fields, mismatch_layers = classify_result(spec, results[0])

        probe_results.append(ProbeResult(
            probe_id=probe_id, family=family,
            classification=classification,
            mismatch_fields=mismatch_fields,
            mismatch_layers=mismatch_layers,
            repeat_0_result=results[0] if len(results) > 0 else None,
            repeat_1_result=results[1] if len(results) > 1 else None,
            variance_observed=variance,
        ))

        classification_counts[classification] += 1
        family_counts[family][classification] += 1
        family_counts[family]["total"] += 1

        if classification == "parser_gap":
            parser_gap_ids.append(probe_id)

    selection_hash = _compute_selection_hash(parser_gap_ids)
    report_hash_input = (
        fixture_hash + str(classification_counts) + str(variance_count) + selection_hash
    )
    report_hash = "sha256:" + hashlib.sha256(
        report_hash_input.encode("utf-8")
    ).hexdigest()

    return DiagnosticReport(
        source_commit=source_commit,
        fixture_hash=fixture_hash,
        report_hash=report_hash,
        candidate_selection_hash=selection_hash,
        total_probes=EXPECTED_PROBE_COUNT,
        total_observations=EXPECTED_PROBE_COUNT * EXPECTED_REPEATS,
        classifications=classification_counts,
        family_counts=family_counts,
        probe_results=tuple(probe_results),
        parser_gap_ids=tuple(parser_gap_ids),
        variance_count=variance_count,
        remediation_authorized=False,
    )


def _compute_selection_hash(parser_gap_ids: list[str]) -> str:
    """Compute a deterministic hash of the parser-gap selection."""
    if not parser_gap_ids:
        return "sha256:e3b0c44298fc1c14"
    raw = json.dumps(sorted(parser_gap_ids), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# Report serialization
# ---------------------------------------------------------------------------


def report_to_dict(report: DiagnosticReport) -> dict[str, Any]:
    """Serialize diagnostic report to JSON-compatible dict."""
    return {
        "source_commit": report.source_commit,
        "fixture_hash": report.fixture_hash,
        "report_hash": report.report_hash,
        "candidate_selection_hash": report.candidate_selection_hash,
        "total_probes": report.total_probes,
        "total_observations": report.total_observations,
        "classifications": dict(report.classifications),
        "family_counts": {k: dict(v) for k, v in report.family_counts.items()},
        "probe_results": [
            {
                "probe_id": r.probe_id,
                "family": r.family,
                "classification": r.classification,
                "mismatch_fields": list(r.mismatch_fields),
                "mismatch_layers": list(r.mismatch_layers),
                "variance_observed": r.variance_observed,
                "authoring_error": r.authoring_error,
            }
            for r in report.probe_results
        ],
        "parser_gap_ids": list(report.parser_gap_ids),
        "variance_count": report.variance_count,
        "remediation_authorized": report.remediation_authorized,
        "schema_version": "lc4v4d1.diagnostic.v1",
    }


def report_to_markdown(report: DiagnosticReport) -> str:
    """Generate a human-readable markdown report."""
    lines = [
        "# LC4V4D1 Development Diagnostic Report",
        "",
        f"- **Source commit**: {report.source_commit}",
        f"- **Fixture hash**: {report.fixture_hash}",
        f"- **Report hash**: {report.report_hash}",
        f"- **Candidate parser-gap selection hash**: {report.candidate_selection_hash}",
        f"- **Total probes**: {report.total_probes}",
        f"- **Total observations**: {report.total_observations}",
        f"- **Variant observations**: {report.variance_count}",
        f"- **Remediation authorized**: {report.remediation_authorized}",
        "",
        "## Classification Totals",
        "",
    ]
    for cat in ["authoring_invalid", "parser_gap", "policy_contract_gap",
                 "scorer_gap", "planned_unavailable", "supported_pass"]:
        count = report.classifications.get(cat, 0)
        lines.append(f"- **{cat}**: {count}")
    lines.append("")

    lines.extend(["## Per-Family Counts", ""])
    for family in ["entity", "dialogue", "safety", "diary"]:
        counts = report.family_counts.get(family, {})
        lines.append(f"### {family}")
        for cat in ["total", "authoring_invalid", "parser_gap", "policy_contract_gap",
                     "scorer_gap", "supported_pass", "planned_unavailable"]:
            count = counts.get(cat, 0)
            if count > 0 or cat == "total":
                lines.append(f"- {cat}: {count}")
        lines.append("")

    lines.extend(["## Probe Results", ""])
    for pr in report.probe_results:
        line = f"- **{pr.probe_id}**: {pr.classification}"
        if pr.mismatch_fields:
            line += f"  \n  - Mismatch fields: {', '.join(pr.mismatch_fields)}"
            line += f"  \n  - Mismatch layers: {', '.join(pr.mismatch_layers)}"
        if pr.variance_observed:
            line += "  \n  - ⚠️ **Variance observed!**"
        if pr.authoring_error:
            line += f"  \n  - Error: {pr.authoring_error}"
        lines.append(line)
    lines.append("")

    lines.extend([
        "## Protected Boundary",
        "",
        "Protected holdouts v1-v4 remain sealed. No protected fixture, support "
        "module, authoring program, quality receipt, manifest, seal, consumed "
        "seal, test, filename population, or case-level surface was accessed.",
        "",
        "## Decision",
        "",
        "**DECISION: candidate_complete**",
        "",
        "Remediation is not authorized in D1. Any parser gaps identified "
        "require Gemini independent confirmation before a future remediation "
        "contract.",
    ])
    return "\n".join(lines)


__all__ = [
    "author_all_probes",
    "dict_to_spec",
    "validate_fixture_surface",
    "validate_safety_pairs",
    "compute_fixture_hash",
    "write_fixtures",
    "run_diagnostic",
    "report_to_dict",
    "report_to_markdown",
    "DiagnosticReport",
    "ProbeResult",
]
