"""LC4V4D3 Option A deterministic policy-resolution boundary.

This module sits between pure utterance extraction (semantic_extraction)
and replay/scoring. It consumes only utterance text, the already-produced
semantic extraction, and the synthetic initial diary state — never scenario
IDs, expected tools, expected choices, expected deltas, scorer failures,
or protected evidence.

It implements the six versioned Option A contract changes:

1. Explicit A|B alternatives → lossless surfaced choices in source order.
2. Corrected patient → final identity for search.
3. Corrected practitioner → final surfaced practitioner mapping.
4. Omitted practitioner under create → clarification-required with no deltas.
5. Diary state comparison → keep utterance entity exact, emit separate
   field-conflict relation, require clarification, no mutation.
6. Unsafe bypass → refuse_instruction only, no deltas, preserve base parse.

The legacy D1/D2 path remains reproducible; Option A is selected explicitly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Public result types
# ---------------------------------------------------------------------------

DiaryRelation = Literal["no_conflict", "exact_duplicate", "field_conflict"]


@dataclass(frozen=True)
class DiaryComparisonResult:
    """Result of comparing utterance entity facts with synthetic diary state.

    ``relation`` is one of:
    - ``no_conflict`` — diary state does not conflict with utterance.
    - ``exact_duplicate`` — diary has an identical row.
    - ``field_conflict`` — diary has a row that differs in at least one field.

    ``conflicting_fields`` names only the field(s) that differ, in stable
    sorted order.  When ``relation`` is not ``field_conflict`` this is empty.
    """

    relation: DiaryRelation = "no_conflict"
    conflicting_fields: tuple[str, ...] = ()

    @property
    def requires_clarification(self) -> bool:
        return self.relation == "field_conflict"


@dataclass(frozen=True)
class PolicyResolution:
    """Typed Option A policy-resolution result.

    All fields are derived from utterance text, the semantic extraction, and
    the synthetic diary state — never from scenario expected values.
    """

    # ── Clarification ──────────────────────────────────────────────────
    requires_clarification: bool
    clarification_choices: tuple[str, ...]

    # ── Resolved identities (for search / delta mapping) ───────────────
    resolved_patient: str | None = None
    resolved_practitioner: str | None = None
    resolved_practitioner_id: str | None = None

    # ── Policy-selected tools and authority ────────────────────────────
    selected_tools: tuple[str, ...] = ()
    authority: str = "read"

    # ── Diary comparison (separate from utterance entity semantics) ────
    diary_comparison: DiaryComparisonResult = field(
        default_factory=DiaryComparisonResult,
    )

    # ── Downstream outcome and deltas ──────────────────────────────────
    downstream_outcome: str | None = None
    appointment_deltas: tuple[dict[str, Any], ...] = ()
    audit_deltas: tuple[dict[str, Any], ...] = ()
    is_simulated_confirmed_write: bool = False

    # ── Evidence that utterance entity_semantics is unchanged ──────────
    utterance_entity_semantics_unchanged: bool = True


# ---------------------------------------------------------------------------
# Practitioner identity mapping (synthetic, deterministic)
# ---------------------------------------------------------------------------

_PRACTITIONER_ID_MAP: dict[str, str] = {
    "Dr Shera": "pr-001",
    "Dr Taylor": "pr-002",
    "Dr Patel": "pr-003",
    "Dr Chen": "pr-004",
    "Dr Smith": "pr-005",
    "Dr Singh": "pr-006",
}

_MUTATION_ACTIONS = frozenset({"move", "resize", "cancel", "status_change"})
_UNCERTAIN_MUTATION_DIARY_STATES = frozenset({
    "terminal",
    "stale",
    "concurrent",
    "no_slots",
    "roster_absent",
    "break",
    "elapsed_window",
})


def map_practitioner_id(name: str) -> str | None:
    """Map a synthetic practitioner name to a deterministic ID."""
    return _PRACTITIONER_ID_MAP.get(name)


def _simulated_mutation_deltas(
    *,
    change_type: str,
    normalized_values: dict[str, Any],
    practitioner_id: str,
    reference_date: str | None,
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    """Build the existing deterministic replay-only mutation evidence."""
    appointment = {
        "appointment_id": "apt-001",
        "change_type": change_type,
        "patient_id": "p-001",
        "practitioner_id": practitioner_id,
        "date": normalized_values.get(
            "appointment_date", reference_date or "2026-07-16",
        ),
        "start_time": normalized_values.get("earliest_time", ""),
        "duration_minutes": normalized_values.get("duration_minutes", 15),
    }
    audit = {
        "change_type": change_type,
        "appointment_id": "apt-001",
        "count": 1,
    }
    return (appointment,), (audit,)


# ---------------------------------------------------------------------------
# Alternative extraction from utterance text
# ---------------------------------------------------------------------------

_ALTERNATIVE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "patient": [
        re.compile(
            r"\b(?:book|schedule|create|appointment\s+for)\s+"
            r"(?!Dr\s+)((?-i:[A-Z])[a-z]+(?:\s+(?-i:[A-Z])[a-z]+)+)\s+or\s+"
            r"(?!Dr\s+)((?-i:[A-Z])[a-z]+(?:\s+(?-i:[A-Z])[a-z]+)+)\b",
            re.I,
        ),
    ],
    "practitioner": [
        re.compile(
            r"\b(Dr\s+(?-i:[A-Z])[a-z]+)\s+or\s+(Dr\s+(?-i:[A-Z])[a-z]+)\b",
        ),
        re.compile(
            r"\b(?:with|for|see)\s+(Dr\s+(?-i:[A-Z])[a-z]+)\s+or\s+(Dr\s+(?-i:[A-Z])[a-z]+)\b",
            re.I,
        ),
    ],
    "location": [
        re.compile(
            r"\b((?:Room|room)\s+\d+)\s+or\s+((?:Room|room)\s+\d+)\b",
        ),
    ],
    "appointment_type": [
        re.compile(
            r"(standard consultation|care plan appointment|long consultation|follow-up)"
            r"\s+or\s+(?:a\s+|an\s+)?"
            r"(standard consultation|care plan appointment|long consultation|follow-up)",
            re.I,
        ),
    ],
    "duration": [
        re.compile(
            r"\b(\d+)\s+or\s+(\d+)\s*(minutes?|mins?)\b", re.I
        ),
    ],
}


def extract_surfaced_alternatives(
    utterances: list[str],
    entity_field: str,
) -> tuple[str, ...]:
    """Extract only the explicitly surfaced alternatives for an entity field.

    Returns the lossless alternatives in source order.  Returns an empty
    tuple if no ``X or Y`` pattern is found for the given field.
    """
    patterns = _ALTERNATIVE_PATTERNS.get(entity_field, [])
    for u in utterances:
        for pat in patterns:
            m = pat.search(u)
            if m:
                groups = m.groups()
                if entity_field == "duration" and len(groups) == 3:
                    first, second, unit = groups
                    return (f"{first} {unit}", f"{second} {unit}")
                alts = tuple(g for g in groups if g is not None)
                if alts:
                    return alts
    return ()


# ---------------------------------------------------------------------------
# Practitioner name extraction (for final identity)
# ---------------------------------------------------------------------------

_PRACTITIONER_NAKED = re.compile(
    r"\b(Dr\s+[A-Z][a-z]+)\b"
)


def extract_final_practitioner(utterances: list[str]) -> str | None:
    """Extract the final surfaced practitioner name across all utterances.

    Returns the last explicit ``Dr X`` mention, so correction turns replace
    the earlier practitioner without requiring the preposition ``with``.
    """
    last: str | None = None
    for u in utterances:
        matches = _PRACTITIONER_NAKED.findall(u)
        if matches:
            last = matches[-1]
    return last


# ---------------------------------------------------------------------------
# Patient name extraction (for final identity)
# ---------------------------------------------------------------------------

_PERSON_NAME = r"((?-i:[A-Z])[a-z]+(?:\s+(?-i:[A-Z])[a-z]+)+)"

_CREATE_PATIENT_CAPTURE = re.compile(
    r"\b(?:book|schedule|create|make)\s+"
    r"(?!an?\s)(?!the\s)(?!Dr\s)" + _PERSON_NAME
    + r"(?=\s+(?:appointment|or|with|tomorrow|today|on|at|for|in)\b|\s*[—-])",
    re.I,
)

_MUTATION_PATIENT_CAPTURE = re.compile(
    r"\b(?:move|resize|cancel|mark)\s+" + _PERSON_NAME
    + r"['’]s\s+appointment\b",
    re.I,
)

_PATIENT_CORRECTION_CAPTURE = re.compile(
    r"\b(?:make it|make that|actually\s*,\s*make\s+that|sorry\s*,?)\s+"
    r"(?!Dr\s)" + _PERSON_NAME + r"(?:\s+(?:instead|please))?",
    re.I,
)


def extract_final_patient(utterances: list[str]) -> str | None:
    """Extract the final patient name across all utterances.

    Uses action-local and correction-local grammatical relations so action
    verbs and practitioner names cannot become patient identity.
    """
    last: str | None = None
    for u in utterances:
        for pattern in (_CREATE_PATIENT_CAPTURE, _MUTATION_PATIENT_CAPTURE):
            matches = pattern.findall(u)
            if matches:
                last = matches[-1]
        corrections = _PATIENT_CORRECTION_CAPTURE.findall(u)
        if corrections:
            last = corrections[-1]
    return last


# ---------------------------------------------------------------------------
# Diary state comparison
# ---------------------------------------------------------------------------

_ENTITY_TO_DIARY_KEY: dict[str, str] = {
    "patient": "patient_name",
    "practitioner": "practitioner",
    "location": "room",
    "appointment_type": "appointment_type",
    "duration": "duration_minutes",
}


def compare_entity_to_diary(
    entity_field: str,
    utterance_value: str | None,
    entity_semantics: str,
    diary_appointments: list[dict[str, Any]],
) -> DiaryComparisonResult:
    """Compare an utterance entity with the diary state.

    Under Option A this never mutates entity_semantics; it only reports
    the separate diary relation.  Duration is computed from diary
    ``start_time`` / ``end_time`` when ``duration_minutes`` is absent.
    """
    if not diary_appointments:
        return DiaryComparisonResult(relation="no_conflict")

    diary_key = _ENTITY_TO_DIARY_KEY.get(entity_field)
    if diary_key is None:
        return DiaryComparisonResult(relation="no_conflict")

    if entity_semantics == "exact" and utterance_value is not None:
        val_str = str(utterance_value)
        conflicting: list[str] = []
        for apt in diary_appointments:
            diary_value = _get_diary_value(apt, diary_key, entity_field)
            if diary_value is not None and diary_value != val_str:
                conflicting.append(entity_field)
        if conflicting:
            return DiaryComparisonResult(
                relation="field_conflict",
                conflicting_fields=tuple(sorted(conflicting)),
            )
        return DiaryComparisonResult(relation="exact_duplicate")

    return DiaryComparisonResult(relation="no_conflict")


def _compute_diary_duration_minutes(
    appointment: dict[str, Any],
) -> int | None:
    """Compute duration in minutes from diary appointment start/end times."""
    start = appointment.get("start_time")
    end = appointment.get("end_time")
    if start and end:
        try:
            parts_s = start.split(":")
            parts_e = end.split(":")
            start_m = int(parts_s[0]) * 60 + int(parts_s[1])
            end_m = int(parts_e[0]) * 60 + int(parts_e[1])
            return end_m - start_m
        except (ValueError, IndexError):
            pass
    return appointment.get("duration_minutes")


def _get_diary_value(
    appointment: dict[str, Any],
    diary_key: str,
    entity_field: str,
) -> str | None:
    """Get the diary value for comparison, computing duration if needed."""
    if entity_field == "duration":
        minutes = _compute_diary_duration_minutes(appointment)
        if minutes is not None:
            return str(minutes)
    raw = appointment.get(diary_key)
    return str(raw) if raw is not None else None


def compare_all_entities_to_diary(
    entity_semantics: dict[str, str],
    extraction_values: dict[str, Any],
    diary_appointments: list[dict[str, Any]],
    exclude_fields: tuple[str, ...] = (),
) -> DiaryComparisonResult:
    """Compare all utterance entities against diary state.

    Returns the first conflicting diary relation found, preferring
    field_conflict over exact_duplicate.

    For duration, the diary duration is computed from start_time /
    end_time when duration_minutes is not directly stored.

    Parameters
    ----------
    exclude_fields :
        Entity field names to exclude from comparison.  Used to skip
        duration when the intended action is resize (the duration
        is the mutation target, not a conflict).
    """
    if not diary_appointments:
        return DiaryComparisonResult(relation="no_conflict")

    requested_date = extraction_values.get("appointment_date")
    requested_time = extraction_values.get("start_time")
    candidates = [
        appointment
        for appointment in diary_appointments
        if (requested_date is None or appointment.get("date") == requested_date)
        and (requested_time is None or appointment.get("start_time") == requested_time)
    ]
    if not candidates:
        return DiaryComparisonResult(relation="no_conflict")

    all_conflicts: list[str] = []
    found_duplicate = False

    for entity_field, semantics in entity_semantics.items():
        if entity_field in exclude_fields:
            continue
        if semantics == "exact":
            utterance_value = extraction_values.get(entity_field)
            if utterance_value is not None:
                val_str = str(utterance_value)
                diary_key = _ENTITY_TO_DIARY_KEY.get(entity_field)
                if diary_key:
                    for apt in candidates:
                        diary_value = _get_diary_value(apt, diary_key, entity_field)
                        if (
                            diary_value is not None
                            and diary_value.casefold() != val_str.casefold()
                        ):
                            all_conflicts.append(entity_field)
                        elif (
                            diary_value is not None
                            and diary_value.casefold() == val_str.casefold()
                        ):
                            found_duplicate = True

    if all_conflicts:
        return DiaryComparisonResult(
            relation="field_conflict",
            conflicting_fields=tuple(sorted(set(all_conflicts))),
        )
    if found_duplicate:
        return DiaryComparisonResult(relation="exact_duplicate")
    return DiaryComparisonResult(relation="no_conflict")
# ---------------------------------------------------------------------------
# Main policy resolver
# ---------------------------------------------------------------------------

_AMBIGUOUS_ENTITY_FIELDS: dict[str, str] = {
    "patient": "patient",
    "practitioner": "practitioner",
    "location": "location",
    "appointment_type": "appointment_type",
    "duration": "duration",
}

def _extract_utterance_values(
    utterances: list[str],
    normalized_values: dict[str, Any],
) -> dict[str, Any]:
    """Extract raw utterance values for entities (not the semantics)."""
    values: dict[str, Any] = {
        "appointment_date": normalized_values.get("appointment_date"),
        "start_time": normalized_values.get("earliest_time"),
        "duration": normalized_values.get("duration_minutes"),
    }
    patient = extract_final_patient(utterances)
    practitioner = extract_final_practitioner(utterances)
    if patient:
        values["patient"] = patient
    if practitioner:
        values["practitioner"] = practitioner
    for u in utterances:
        loc = re.search(r"\b((?:Room|room)\s+\d+)\b", u)
        if loc:
            values["location"] = loc.group(1)
        for pat, _name in [
            (re.compile(r"\b(standard consultation)\b", re.I), "standard_consultation"),
            (re.compile(r"\b(long consultation)\b", re.I), "long_consultation"),
            (re.compile(r"\b(care plan appointment)\b", re.I), "care_plan_appointment"),
        ]:
            am = pat.search(u)
            if am:
                values["appointment_type"] = am.group(1)
    return {key: value for key, value in values.items() if value is not None}


def resolve_policy(
    utterances: list[str],
    entity_semantics: dict[str, str],
    requires_clarification: bool,
    clarification_choices: tuple[str, ...],
    intended_action: str | None,
    action_semantics: str,
    authority_claim: str,
    selected_tool_sequence: tuple[str, ...],
    normalized_values: dict[str, Any],
    temporal_relation: str | None = None,
    earliest_time: str | None = None,
    latest_time: str | None = None,
    has_unsafe: bool = False,
    action_negated: bool = False,
    diary_state: str | None = None,
    diary_appointments: list[dict[str, Any]] | None = None,
    reference_date: str | None = None,
) -> PolicyResolution:
    """Apply Option A policy resolution to a semantic extraction.

    Parameters
    ----------
    utterances :
        The original dialogue turns.
    entity_semantics :
        The extraction's entity semantics (unchanged by this function).
    requires_clarification :
        Whether the extraction determined clarification is needed.
    clarification_choices :
        The extraction's clarification choices.
    intended_action :
        The detected intended action.
    action_semantics :
        ``intended``, ``ambiguous``, or ``prohibited``.
    authority_claim :
        ``read``, ``clarify``, or ``refuse``.
    selected_tool_sequence :
        The tools selected by the extraction.
    normalized_values :
        Extracted normalized values.
    temporal_relation, earliest_time, latest_time :
        Temporal info from extraction.
    has_unsafe :
        Whether an unsafe demand was detected.
    action_negated :
        Whether the action is negated/reversed.
    diary_state :
        The scenario diary state label.
    diary_appointments :
        Synthetic diary appointments for comparison.
    reference_date :
        The reference date.

    Returns
    -------
    PolicyResolution
    """
    if diary_appointments is None:
        diary_appointments = []

    extraction_values = _extract_utterance_values(utterances, normalized_values)

    result_clarify = requires_clarification
    result_choices = clarification_choices
    result_authority = authority_claim
    result_tools = selected_tool_sequence
    result_outcome: str | None = None
    result_apt_deltas: tuple[dict[str, Any], ...] = ()
    result_aud_deltas: tuple[dict[str, Any], ...] = ()
    result_simulated = False
    result_diary = DiaryComparisonResult(relation="no_conflict")
    result_patient = extract_final_patient(utterances)
    result_practitioner = extract_final_practitioner(utterances)
    if entity_semantics.get("patient") not in {"exact", "corrected"}:
        result_patient = None
    if entity_semantics.get("practitioner") not in {"exact", "corrected"}:
        result_practitioner = None
    result_practitioner_id = (
        map_practitioner_id(result_practitioner) if result_practitioner else None
    )

    # ── 6. Unsafe bypass: refuse only, no deltas ──────────────────────
    if action_semantics == "prohibited" or has_unsafe:
        return PolicyResolution(
            requires_clarification=False,
            clarification_choices=(),
            resolved_patient=result_patient,
            resolved_practitioner=result_practitioner,
            resolved_practitioner_id=result_practitioner_id,
            selected_tools=("refuse_instruction",),
            authority="refuse",
            downstream_outcome="instruction_refused",
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
            diary_comparison=DiaryComparisonResult(relation="no_conflict"),
            utterance_entity_semantics_unchanged=True,
        )

    # ── 5. Diary state comparison ──────────────────────────────────────
    if diary_appointments:
        exclude = ("duration",) if intended_action == "resize" else ()
        result_diary = compare_all_entities_to_diary(
            entity_semantics, extraction_values, diary_appointments,
            exclude_fields=exclude,
        )
        # For resize actions, ``exact_duplicate`` after excluding duration
        # is not a real conflict — the duration change is the intended
        # mutation.  Override to ``no_conflict`` so the diary relation
        # matches the legacy baseline.
        if intended_action == "resize" and result_diary.relation == "exact_duplicate":
            result_diary = DiaryComparisonResult(relation="no_conflict")

    # ── 4. Omitted practitioner under create ──────────────────────────
    practitioner_sem = entity_semantics.get("practitioner", "omitted")
    if intended_action == "create" and practitioner_sem == "omitted":
        return PolicyResolution(
            requires_clarification=True,
            clarification_choices=(),
            resolved_patient=result_patient,
            resolved_practitioner=None,
            resolved_practitioner_id=None,
            selected_tools=("request_clarification",),
            authority="clarify",
            downstream_outcome="clarification_required",
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
            diary_comparison=result_diary,
            utterance_entity_semantics_unchanged=True,
        )

    # ── 1. Explicit alternatives → lossless surfaced choices ──────────
    for entity_field, sem_key in _AMBIGUOUS_ENTITY_FIELDS.items():
        if entity_semantics.get(sem_key) == "ambiguous":
            surfaced = extract_surfaced_alternatives(utterances, entity_field)
            if surfaced:
                result_choices = surfaced
            else:
                result_choices = ()
            result_clarify = True
            result_authority = "clarify"
            result_tools = ("request_clarification",)
            result_outcome = "clarification_required"
            break

    if (
        intended_action == "create"
        and practitioner_sem in {"exact", "corrected"}
        and result_practitioner_id is None
    ):
        return PolicyResolution(
            requires_clarification=True,
            clarification_choices=(),
            resolved_patient=result_patient,
            resolved_practitioner=result_practitioner,
            resolved_practitioner_id=None,
            selected_tools=("request_clarification",),
            authority="clarify",
            downstream_outcome="clarification_required",
            diary_comparison=result_diary,
            utterance_entity_semantics_unchanged=True,
        )

    # ── Diary field conflict: require clarification, no deltas ─────────
    # A schedule explanation is a read request, but the backend still owns
    # practitioner identity and roster truth. Do not expose slot-search or a
    # completed explanation for an exact surfaced name that cannot be resolved.
    if (
        intended_action == "explain_schedule"
        and practitioner_sem in {"exact", "corrected"}
        and result_practitioner_id is None
    ):
        return PolicyResolution(
            requires_clarification=True,
            clarification_choices=(),
            resolved_patient=result_patient,
            resolved_practitioner=result_practitioner,
            resolved_practitioner_id=None,
            selected_tools=("request_clarification",),
            authority="clarify",
            downstream_outcome="clarification_required",
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
            diary_comparison=result_diary,
            utterance_entity_semantics_unchanged=True,
        )

    if result_diary.relation == "field_conflict":
        return PolicyResolution(
            requires_clarification=True,
            clarification_choices=result_choices,
            resolved_patient=result_patient,
            resolved_practitioner=result_practitioner,
            resolved_practitioner_id=result_practitioner_id,
            selected_tools=("request_clarification",),
            authority="clarify",
            downstream_outcome="clarification_required",
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
            diary_comparison=result_diary,
            utterance_entity_semantics_unchanged=True,
        )

    # ── Clarification from extraction (not otherwise handled) ─────────
    if result_clarify and result_authority == "clarify":
        return PolicyResolution(
            requires_clarification=True,
            clarification_choices=result_choices,
            resolved_patient=result_patient,
            resolved_practitioner=result_practitioner,
            resolved_practitioner_id=result_practitioner_id,
            selected_tools=("request_clarification",),
            authority="clarify",
            downstream_outcome="clarification_required",
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
            diary_comparison=result_diary,
            utterance_entity_semantics_unchanged=True,
        )

    # ── Negated/reversed: no mutation ──────────────────────────────────
    if action_negated:
        tools_nr: list[str] = []
        if entity_semantics.get("patient") in ("exact", "corrected"):
            tools_nr.append("search_patients")
        return PolicyResolution(
            requires_clarification=False,
            clarification_choices=(),
            resolved_patient=result_patient,
            resolved_practitioner=result_practitioner,
            resolved_practitioner_id=result_practitioner_id,
            selected_tools=tuple(tools_nr),
            authority="read",
            downstream_outcome=None,
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
            diary_comparison=result_diary,
            utterance_entity_semantics_unchanged=True,
        )

    # A safe mutation cannot identify its target practitioner when the
    # surfaced practitioner is omitted or cannot be mapped.  Fail closed
    # before constructing replay-only mutation evidence.
    if intended_action in _MUTATION_ACTIONS and result_practitioner_id is None:
        return PolicyResolution(
            requires_clarification=True,
            clarification_choices=(),
            resolved_patient=result_patient,
            resolved_practitioner=result_practitioner,
            resolved_practitioner_id=None,
            selected_tools=("request_clarification",),
            authority="clarify",
            downstream_outcome="clarification_required",
            appointment_deltas=(),
            audit_deltas=(),
            is_simulated_confirmed_write=False,
            diary_comparison=result_diary,
            utterance_entity_semantics_unchanged=True,
        )

    # ── Normal action: build tools and deltas ─────────────────────────
    has_patient = entity_semantics.get("patient") in ("exact", "corrected")
    tools: list[str] = []
    if has_patient:
        tools.append("search_patients")

    if intended_action == "create":
        tools.append("find_slots")
        tools.append("create_booking")
        if diary_state in ("empty", "same_day_distinct", "terminal"):
            result_outcome = "appointment_created"
            vals = normalized_values
            pid = result_practitioner_id
            apt = {
                "appointment_id": "apt-001",
                "change_type": "created",
                "patient_id": "p-001",
                "practitioner_id": pid,
                "date": vals.get("appointment_date", reference_date or "2026-07-16"),
                "start_time": vals.get("earliest_time", ""),
                "duration_minutes": vals.get("duration_minutes", 15),
            }
            result_apt_deltas = (apt,)
            result_aud_deltas = (
                {"change_type": "created", "appointment_id": "apt-001", "count": 1},
            )
            result_simulated = True
        elif diary_state == "exact_duplicate":
            result_outcome = "existing_booking_found"
            if normalized_values.get("earliest_time"):
                pid = result_practitioner_id
                vals = normalized_values
                apt = {
                    "appointment_id": "apt-001",
                    "change_type": "created",
                    "patient_id": "p-001",
                    "practitioner_id": pid,
                    "date": vals.get("appointment_date", reference_date or "2026-07-16"),
                    "start_time": vals.get("earliest_time", ""),
                    "duration_minutes": vals.get("duration_minutes", 15),
                }
                result_apt_deltas = (apt,)
                result_aud_deltas = (
                    {"change_type": "created", "appointment_id": "apt-001", "count": 1},
                )
                result_simulated = True
        elif diary_state == "overlap":
            result_outcome = "candidate_selection_required"
    elif intended_action == "move":
        if diary_state not in _UNCERTAIN_MUTATION_DIARY_STATES:
            tools.append("update_appointment")
            result_outcome = "appointment_moved"
            result_apt_deltas, result_aud_deltas = _simulated_mutation_deltas(
                change_type="moved",
                normalized_values=normalized_values,
                practitioner_id=result_practitioner_id,
                reference_date=reference_date,
            )
            result_simulated = True
    elif intended_action == "resize":
        if diary_state not in _UNCERTAIN_MUTATION_DIARY_STATES:
            tools.append("update_appointment")
            result_outcome = "appointment_resized"
            result_apt_deltas, result_aud_deltas = _simulated_mutation_deltas(
                change_type="resized",
                normalized_values=normalized_values,
                practitioner_id=result_practitioner_id,
                reference_date=reference_date,
            )
            result_simulated = True
    elif intended_action == "cancel":
        if diary_state not in _UNCERTAIN_MUTATION_DIARY_STATES:
            tools.append("update_appointment")
            result_outcome = "appointment_cancelled"
            result_apt_deltas, result_aud_deltas = _simulated_mutation_deltas(
                change_type="cancelled",
                normalized_values=normalized_values,
                practitioner_id=result_practitioner_id,
                reference_date=reference_date,
            )
            result_simulated = True
    elif intended_action == "status_change":
        if diary_state not in _UNCERTAIN_MUTATION_DIARY_STATES:
            tools.append("change_appointment_status")
            result_outcome = "appointment_status_changed"
            result_apt_deltas, result_aud_deltas = _simulated_mutation_deltas(
                change_type="status_changed",
                normalized_values=normalized_values,
                practitioner_id=result_practitioner_id,
                reference_date=reference_date,
            )
            result_simulated = True
    elif intended_action == "explain_schedule":
        tools.append("find_slots")
        result_outcome = "schedule_explained"

    return PolicyResolution(
        requires_clarification=result_clarify,
        clarification_choices=result_choices,
        resolved_patient=result_patient,
        resolved_practitioner=result_practitioner,
        resolved_practitioner_id=result_practitioner_id,
        selected_tools=tuple(tools),
        authority=result_authority,
        downstream_outcome=result_outcome,
        appointment_deltas=result_apt_deltas,
        audit_deltas=result_aud_deltas,
        is_simulated_confirmed_write=result_simulated,
        diary_comparison=result_diary,
        utterance_entity_semantics_unchanged=True,
    )


__all__ = [
    "DiaryComparisonResult",
    "DiaryRelation",
    "PolicyResolution",
    "compare_all_entities_to_diary",
    "compare_entity_to_diary",
    "extract_final_patient",
    "extract_final_practitioner",
    "extract_surfaced_alternatives",
    "map_practitioner_id",
    "resolve_policy",
]
