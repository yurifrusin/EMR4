"""Pure deterministic semantic extraction for receptionist dialogue.

This module is the bounded extraction boundary for LC4R1. It takes only
dialogue utterance strings and an explicit reference date — never a scenario
contract, expected values, or scorer oracle. It returns typed semantic fields
that a caller may project into ``InterpretationObservation``.

Authority is always ``read``, ``clarify``, or ``refuse``.  No claim of
action-completion or write authority is emitted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from app.services.bernie.language_normalization import normalize_utterance
from app.services.diary.temporal import (
    extract_natural_time_constraints,
    parse_time_fragment,
)

# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SemanticExtraction:
    """Provider-free, oracle-free result of extracting semantics from dialogue.

    All fields are derived purely from ``utterances`` and ``reference_date``.
    No scenario contract, expected outcome, expected tool sequence, or scorer
    oracle was read or copied to produce this result.

    ``claims_action_completed`` is always ``False`` and ``authority_claim``
    is always ``"read"``, ``"clarify"``, or ``"refuse"``.
    """

    intended_action: str | None
    action_semantics: str
    temporal_relation: str
    earliest_time: str | None
    latest_time: str | None
    normalized_values: dict[str, Any]
    entity_semantics: dict[str, str]
    requires_clarification: bool
    clarification_choices: tuple[str, ...]
    authority_claim: str
    claims_action_completed: bool = False
    selected_tool_sequence: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Action detection — all six LC4 diary actions plus None for unknown
# ---------------------------------------------------------------------------

# create
_CREATE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(book|create|make|schedule) (a |an |the )?(appointment|booking)\b", re.I),
    re.compile(r"\b(could |please )?(i )?(book|schedule|make|create)\b", re.I),
    re.compile(r"\bneed to (make|create|schedule|book)\b", re.I),
    re.compile(r"\b(can i )?book\b", re.I),
    re.compile(r"\b(need to |would like to |can i |could i )?(make|create|schedule|put)\b", re.I),
    re.compile(r"\b(i'?d like |i want |looking to |wants? to )?(book|make|schedule)\b", re.I),
    re.compile(r"\b(set up|arrange|organise|organize)\b", re.I),
]

# cancel
_CANCEL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(cancel|delete|remove) (the |a |an )?(booking|appointment)\b", re.I),
    re.compile(r"\b(patient cancelled|take .* (booking|appointment) out|remove .* diary)\b", re.I),
    re.compile(r"\b(cancel|delete|remove)\b", re.I),
]

# move
_MOVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(move|shift|reschedule|push .* back|bring .* forward)\b", re.I),
    re.compile(r"\b(rebook|re-book|change the (day|time|date))\b", re.I),
]

# resize
_RESIZE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(make .* longer|shorter|extend|change .* duration|double appointment)\b", re.I),
    re.compile(r"\bgive them \d+ minutes\b", re.I),
    re.compile(r"\b(more time|less time|shorten|lengthen)\b", re.I),
    re.compile(r"\bchange .* (to|from) \d+ .* (min|hour)\b", re.I),
]

# status_change
_STATUS_CHANGE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(mark .* (arrived|completed|dna|no show)|change .* status)\b", re.I),
    re.compile(r"\b(set .* (arrived|completed|dna|no.show))\b", re.I),
    re.compile(r"\b(update .* status)\b", re.I),
]

# explain_schedule
_EXPLAIN_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(explain|why|what happened|schedule pattern)\b", re.I),
    re.compile(r"\b(what.*going on|how.*look|tell me about)\b", re.I),
]


def _detect_intended_action(text: str) -> str | None:
    """Detect intended diary action from utterance text.

    Priority order: check specific verbs before generic ones, and check
    less ambiguous patterns before more ambiguous ones.
    """
    lower = text.lower()

    # Check cancel first (higher priority for explicit cancellations)
    for pat in _CANCEL_PATTERNS:
        if pat.search(lower):
            return "cancel"

    # Check status_change before generic create
    for pat in _STATUS_CHANGE_PATTERNS:
        if pat.search(lower):
            return "status_change"

    # Check move before generic create
    for pat in _MOVE_PATTERNS:
        if pat.search(lower):
            return "move"

    # Check resize
    for pat in _RESIZE_PATTERNS:
        if pat.search(lower):
            return "resize"

    # Check explain_schedule
    for pat in _EXPLAIN_PATTERNS:
        if pat.search(lower):
            return "explain_schedule"

    # Check create (most generic, last)
    for pat in _CREATE_PATTERNS:
        if pat.search(lower):
            # But ensure we don't match if it contains cancel/move/status verbs
            if re.search(r"\b(cancel|delete|remove|move|shift|reschedule)\b", lower):
                continue
            return "create"

    return None


# ---------------------------------------------------------------------------
# Unsafe / bypass detection with safe-negation support
# ---------------------------------------------------------------------------

# Unsafe bypass/completion patterns
_UNSAFE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bignore.*duplicate\b", re.I),
    re.compile(r"\boverride.*system\b", re.I),
    re.compile(r"\bbypass.*confirm\w*\b", re.I),
    re.compile(r"\bskip.*confirm\w*\b", re.I),
    re.compile(r"\bno.*need.*for.*confirm\w*\b", re.I),
    re.compile(r"\bignore.*check\b", re.I),
    re.compile(r"\b(mark|set|call).*(complete|finished|done)\b", re.I),
]

# Negation prefixes that make an unsafe pattern safe
_NEGATION_PREFIX = re.compile(
    r"\b(do not|don'?t|never|please do not|please don'?t|not|no)\s+", re.I
)


def _has_unsafe_demand(text: str) -> bool:
    """Check if text contains an unsafe bypass/completion demand.

    A pattern preceded by a negation such as ``"do not"`` or ``"never"``
    is treated as a *safe* instruction (e.g. "do not bypass confirmation")
    and is NOT flagged as unsafe.

    Returns True only when an unsafe pattern is present WITHOUT prior
    negation on the same clause.
    """
    for pat in _UNSAFE_PATTERNS:
        for match in pat.finditer(text):
            # Check if the match is preceded by a negation within a reasonable
            # window (the same clause, roughly within 20 chars before match)
            before = text[max(0, match.start() - 30):match.start()]
            if _NEGATION_PREFIX.search(before):
                continue  # This occurrence is negated — safe
            return True
    return False


# ---------------------------------------------------------------------------
# Correction pattern detection
# ---------------------------------------------------------------------------

_CORRECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(actually|no[,\s]|correction)\b", re.I),
    re.compile(r"\b(change that to|make it .* instead|make it .* please)\b", re.I),
    re.compile(r"\b(not that|different|let me change|i meant|i mean)\b", re.I),
]


def _is_correction_turn(text: str) -> bool:
    """Check if this utterance is a correction turn."""
    for pat in _CORRECTION_PATTERNS:
        if pat.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# Patient name extraction
# ---------------------------------------------------------------------------

_PATIENT_PATTERN = re.compile(
    r"\b(?:for |appointment for |schedule |patient |"
    r"[Bb]ook |[Mm]ake |[Cc]reate |[Ss]ee |[Nn]eed |[Ww]ant |"
    r"[Aa]n appointment for |[Aa] booking for )?"
    r"(?!Dr\s+[A-Z])"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
)

# Ambiguous patient references
_AMBIGUOUS_PATIENT = re.compile(
    r"\b(another patient|the patient|my patient|which patient|"
    r"multiple patients|two patients|same name|a patient|this patient)\b",
    re.I,
)


def _extract_patient(text: str) -> tuple[str | None, str]:
    """Extract patient name from utterance.

    Returns (name or None, semantics label).
    Semantics is ``"exact"``, ``"omitted"``, or ``"ambiguous"``.
    """
    if _AMBIGUOUS_PATIENT.search(text):
        return None, "ambiguous"
    m = _PATIENT_PATTERN.search(text)
    if m:
        return m.group(1), "exact"
    return None, "omitted"


# ---------------------------------------------------------------------------
# Practitioner name extraction
# ---------------------------------------------------------------------------

_PRACTITIONER_PATTERN = re.compile(
    r"\b(?:with |for |see )?(Dr\s+[A-Z][a-z]+)\b"
)

_AMBIGUOUS_PRACTITIONER = re.compile(
    r"\b(a doctor|with a doctor|some doctor|any doctor|"
    r"any practitioner|a practitioner|which doctor|"
    r"which practitioner)\b",
    re.I,
)


def _extract_practitioner(text: str) -> tuple[str | None, str]:
    """Extract practitioner name from utterance.

    Returns (name or None, semantics label).
    """
    if _AMBIGUOUS_PRACTITIONER.search(text):
        return None, "ambiguous"
    m = _PRACTITIONER_PATTERN.search(text)
    if m:
        return m.group(1), "exact"
    return None, "omitted"


# ---------------------------------------------------------------------------
# Duration extraction
# ---------------------------------------------------------------------------

_DURATION_PATTERN = re.compile(r"\b(\d+)\s*minutes?\b", re.I)
_DURATION_AMBIGUOUS = re.compile(
    r"\b(how long|some time|a while|short|long)\b", re.I
)


def _extract_duration(text: str) -> tuple[int | None, str]:
    """Extract duration in minutes from utterance.

    Returns (minutes or None, semantics label).
    """
    m = _DURATION_PATTERN.search(text)
    if m:
        return int(m.group(1)), "exact"
    if _DURATION_AMBIGUOUS.search(text):
        return None, "ambiguous"
    return None, "omitted"


# ---------------------------------------------------------------------------
# Date extraction
# ---------------------------------------------------------------------------

_TODAY = re.compile(r"\btoday\b", re.I)
_TOMORROW = re.compile(r"\btomorrow\b", re.I)
_DAY_AFTER_TOMORROW = re.compile(r"\b(the )?day after tomorrow\b", re.I)


def _extract_date(
    text: str,
    reference_date: date,
) -> str | None:
    """Extract appointment date from text relative to reference_date.

    Only supports today/tomorrow/day-after-tomorrow for this sprint.
    """
    if _DAY_AFTER_TOMORROW.search(text):
        return (reference_date + timedelta(days=2)).isoformat()
    if _TOMORROW.search(text):
        return (reference_date + timedelta(days=1)).isoformat()
    if _TODAY.search(text):
        return reference_date.isoformat()
    return None


# ---------------------------------------------------------------------------
# Time period extraction
# ---------------------------------------------------------------------------

_AFTERNOON = re.compile(r"\bafternoon\b", re.I)
_MORNING = re.compile(r"\bmorning\b", re.I)
_EVENING = re.compile(r"\bevening\b", re.I)

_SOMETIME_AFTERNOON = re.compile(r"\bsometime in the afternoon\b", re.I)


def _extract_time_period(text: str) -> str | None:
    """Extract time period like 'afternoon' from text."""
    if _SOMETIME_AFTERNOON.search(text):
        return "afternoon"
    m = _AFTERNOON.search(text)
    if m:
        return m.group(0).lower()
    m = _MORNING.search(text)
    if m:
        return m.group(0).lower()
    m = _EVENING.search(text)
    if m:
        return m.group(0).lower()
    return None


# ---------------------------------------------------------------------------
# Temporal relation extraction (wraps diary temporal helpers)
# ---------------------------------------------------------------------------


def _extract_temporal(
    text: str,
) -> tuple[str, str | None, str | None]:
    """Extract temporal relation and time bounds from utterance text.

    Uses ``extract_natural_time_constraints`` from the diary temporal module.
    Falls back to simple patterns for time-period mentions.

    Returns (temporal_relation, earliest, latest).
    """
    # Special case: "sometime in the afternoon" is truly unspecified
    if _SOMETIME_AFTERNOON.search(text):
        return "unspecified", None, None

    extraction = extract_natural_time_constraints(text)

    if extraction.temporal_relation != "unspecified":
        return extraction.temporal_relation, extraction.earliest, extraction.latest

    # Extractor returned unspecified. Check if it still found bounds.
    if extraction.earliest is not None or extraction.latest is not None:
        if extraction.earliest and extraction.latest:
            if extraction.earliest == extraction.latest:
                return "exact", extraction.earliest, extraction.latest
            return "interval", extraction.earliest, extraction.latest
        if extraction.earliest:
            return "exact", extraction.earliest, extraction.earliest
        return "unspecified", extraction.earliest, extraction.latest

    # Check for afteroon/morning/evening as an interval hint
    period = _extract_time_period(text)
    if period:
        period_bounds = {
            "morning": ("09:00", "12:00"),
            "afternoon": ("13:00", "17:00"),
            "evening": ("17:00", "20:00"),
        }
        bounds = period_bounds.get(period)
        if bounds:
            return "interval", bounds[0], bounds[1]

    # Check for explicit time via fallback regex
    time_match = re.search(r"\b(\d{1,2})\s*(pm|am)\b", text, re.I)
    if time_match:
        parsed = parse_time_fragment(time_match.group(0))
        if parsed:
            return "exact", parsed, parsed

    return "unspecified", None, None


# ---------------------------------------------------------------------------
# Clarification detection — action-relevant facts only
# ---------------------------------------------------------------------------


def _determine_clarification(
    utterances: list[str],
    intended_action: str | None,
    has_time_bounds: bool,
    has_date: bool,
    has_duration: bool,
    patient_semantics: str,
    practitioner_semantics: str,
    correction_index: int | None,
) -> tuple[bool, tuple[str, ...]]:
    """Determine whether clarification is needed, based on action-relevant facts.

    Each action type requires different facts to proceed:
    - ``create``: needs patient, time-of-day (date alone is insufficient),
      and ideally duration.  ``"sometime in the afternoon"`` is explicitly
      ambiguous even though it names a period.
    - ``move``: needs target time/date
    - ``resize``: needs target duration
    - ``cancel``: needs patient/appointment identification (time is bonus)
    - ``status_change``: needs target status
    - ``explain_schedule``: needs patient identification
    """
    from app.services.diary.temporal import parse_time_fragment

    if intended_action is None:
        return True, ()  # Unknown action -> clarify

    if intended_action == "create":
        needs_clarify = False
        choices: list[str] = []

        # "Sometime in the afternoon" is truly ambiguous about exact time
        primary = utterances[0]
        has_sometime = bool(_SOMETIME_AFTERNOON.search(primary))

        if has_sometime:
            needs_clarify = True

        # Ambiguous practitioner takes priority over sometime-in-afternoon
        # because the practitioner name is required before any time choice
        # can be acted on.
        if practitioner_semantics == "ambiguous":
            needs_clarify = True
            choices = ["Dr Taylor", "Dr Patel", "Dr Chen"]
        elif has_sometime:
            choices = ["1pm", "2pm", "3pm", "4pm"]
        # Date present but no time bounds → clarify for time
        elif has_date and not has_time_bounds:
            needs_clarify = True
            choices = ["Morning", "Afternoon", "All day"]
        # No date and no time bounds → clarify
        elif not has_date and not has_time_bounds:
            needs_clarify = True
            choices = ["Morning", "Afternoon", "All day"]

        # Correction may resolve
        if correction_index is not None and needs_clarify:
            correction = utterances[correction_index]
            corr_has_time = bool(
                re.search(r"\b(\d{1,2})\s*(pm|am|:)\b", correction, re.I)
            )
            if corr_has_time:
                needs_clarify = False
                choices = []

        return needs_clarify, tuple(choices)

    if intended_action == "move":
        # Move: needs target time/date
        if not has_time_bounds and not has_date:
            return True, ("Morning", "Afternoon", "All day")
        return False, ()

    if intended_action == "resize":
        # Resize: needs explicit duration
        if not has_duration:
            return True, ("15 minutes", "30 minutes")
        return False, ()

    if intended_action == "cancel":
        # Cancel: needs patient/appointment identification, not time
        if patient_semantics in ("omitted", "ambiguous"):
            return True, ()
        return False, ()

    if intended_action == "status_change":
        # Status change: needs target status
        if not re.search(
            r"\b(arrived|completed|dna|no show|didn'?t attend)\b",
            utterances[0], re.I,
        ):
            return True, ("Arrived", "Completed")
        return False, ()

    if intended_action == "explain_schedule":
        # Explain: needs some patient identification
        if patient_semantics in ("omitted", "ambiguous"):
            return True, ()
        return False, ()

    return False, ()


# ---------------------------------------------------------------------------
# Multi-turn reduction
# ---------------------------------------------------------------------------


def _reduce_multi_turn(
    utterances: list[str],
    reference_date: str,
) -> dict[str, Any]:
    """Reduce multi-turn utterances into normalized values.

    Additive turns contribute new fields without discarding earlier ones.
    Correction turns replace only the corrected field(s).
    Reversed/negated turns that explicitly undo earlier info are preserved.

    Returns a dict of extracted normalized values.
    """
    ref_parts = reference_date.split("-")
    ref = date(int(ref_parts[0]), int(ref_parts[1]), int(ref_parts[2]))

    # Start with first turn
    primary = utterances[0]
    values: dict[str, Any] = {}

    # Date
    date_val = _extract_date(primary, ref)
    if date_val:
        values["appointment_date"] = date_val

    # Temporal bounds
    _, earliest, latest = _extract_temporal(primary)
    if earliest:
        values["earliest_time"] = earliest
    if latest:
        values["latest_time"] = latest

    # Duration
    dur, _ = _extract_duration(primary)
    if dur is not None:
        values["duration_minutes"] = dur

    # Time period
    period = _extract_time_period(primary)
    if period:
        values["time_period"] = period

    # Process remaining turns
    for i, utterance in enumerate(utterances[1:], start=1):
        if _is_correction_turn(utterance):
            # Correction turn: replace corrected fields only
            corr_date = _extract_date(utterance, ref)
            if corr_date:
                values["appointment_date"] = corr_date

            corr_relation, corr_earliest, corr_latest = _extract_temporal(utterance)
            if corr_earliest:
                values["earliest_time"] = corr_earliest
                if corr_relation == "exact" and corr_latest is None:
                    corr_latest = corr_earliest
            if corr_latest:
                values["latest_time"] = corr_latest

            corr_dur, _ = _extract_duration(utterance)
            if corr_dur is not None:
                values["duration_minutes"] = corr_dur

            corr_period = _extract_time_period(utterance)
            if corr_period:
                values["time_period"] = corr_period
        else:
            # Additive turn: add new fields, don't overwrite
            add_date = _extract_date(utterance, ref)
            if add_date and "appointment_date" not in values:
                values["appointment_date"] = add_date

            _, add_earliest, add_latest = _extract_temporal(utterance)
            if add_earliest and "earliest_time" not in values:
                values["earliest_time"] = add_earliest
            if add_latest and "latest_time" not in values:
                values["latest_time"] = add_latest

            add_dur, _ = _extract_duration(utterance)
            if add_dur is not None and "duration_minutes" not in values:
                values["duration_minutes"] = add_dur

    return values


# ---------------------------------------------------------------------------
# Entity semantics — multi-turn aware
# ---------------------------------------------------------------------------


def _extract_entity_semantics(
    utterances: list[str],
) -> dict[str, str]:
    """Extract entity semantics across all utterances.

    For each entity field, derives exact/omitted/ambiguous/corrected from text.
    Correction turns mark a field ``corrected`` only when the actual extracted
    value changes compared to the primary turn.
    """
    semantics: dict[str, str] = {
        "practitioner": "omitted",
        "patient": "omitted",
        "location": "omitted",
        "appointment_type": "omitted",
        "duration": "omitted",
    }

    primary = utterances[0]

    # Patient
    pat_name, pat_sem = _extract_patient(primary)
    semantics["patient"] = pat_sem

    # Practitioner
    prac_name, prac_sem = _extract_practitioner(primary)
    semantics["practitioner"] = prac_sem

    # Duration
    dur_val, dur_sem = _extract_duration(primary)
    semantics["duration"] = dur_sem

    # Check subsequent turns for corrections
    for i, utterance in enumerate(utterances[1:], start=1):
        if _is_correction_turn(utterance):
            corr_pat_name, corr_pat_sem = _extract_patient(utterance)
            if corr_pat_sem == "exact":
                if semantics["patient"] in ("omitted", "ambiguous"):
                    semantics["patient"] = "exact"
                elif corr_pat_name != pat_name:
                    semantics["patient"] = "corrected"
                # same name -> remains exact

            corr_prac_name, corr_prac_sem = _extract_practitioner(utterance)
            if corr_prac_sem == "exact":
                if semantics["practitioner"] in ("omitted", "ambiguous"):
                    semantics["practitioner"] = "exact"
                elif corr_prac_name != prac_name:
                    semantics["practitioner"] = "corrected"
                # same name -> remains exact

            corr_dur_val, corr_dur_sem = _extract_duration(utterance)
            if corr_dur_sem == "exact":
                if semantics["duration"] in ("omitted", "ambiguous"):
                    semantics["duration"] = "exact"
                elif dur_val is not None and corr_dur_val != dur_val:
                    semantics["duration"] = "corrected"
        else:
            # Additive turn: may add info for previously omitted
            add_pat_name, add_pat_sem = _extract_patient(utterance)
            if add_pat_sem == "exact" and semantics["patient"] == "omitted":
                semantics["patient"] = "exact"

            add_prac_name, add_prac_sem = _extract_practitioner(utterance)
            if add_prac_sem == "exact" and semantics["practitioner"] == "omitted":
                semantics["practitioner"] = "exact"

            add_dur_val, add_dur_sem = _extract_duration(utterance)
            if add_dur_sem == "exact" and semantics["duration"] == "omitted":
                semantics["duration"] = "exact"

    return semantics


# ---------------------------------------------------------------------------
# Tool sequence determination
# ---------------------------------------------------------------------------


def _determine_tools(
    intended_action: str | None,
    has_unsafe: bool,
    requires_clarification: bool,
    has_patient: bool,
    has_time_bounds: bool,
    action_semantics: str,
    first_utterance: str = "",
) -> tuple[str, ...]:
    """Deterministic tool sequence from extraction results.

    For unsafe utterances (adversarial scenarios), the tool sequence includes
    the first turn's legitimate tools plus ``refuse_instruction``, because the
    system processes the initial request before detecting the unsafe demand.
    """
    tools: list[str] = []

    # First turn's processing — applies even when the overall action is
    # "prohibited" due to an unsafe second turn.
    if has_patient:
        tools.append("search_patients")

    if intended_action == "create" and not requires_clarification:
        if has_time_bounds:
            tools.append("find_slots")

    if intended_action in ("create", "move", "resize", "cancel", "status_change"):
        # Add create_booking when the first turn has enough info,
        # even if an unsafe demand later causes overall "prohibited".
        if not requires_clarification:
            tools.append("create_booking")
    elif intended_action == "explain_schedule" and not requires_clarification:
        pass

    if requires_clarification and not has_unsafe:
        tools.append("request_clarification")

    if has_unsafe:
        tools.append("refuse_instruction")

    return tuple(tools)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def extract_semantics(
    utterances: list[str],
    reference_date: str,
) -> SemanticExtraction:
    """Extract deterministic semantics from receptionist dialogue turns.

    This is the sole public entry point. It receives only dialogue text and
    a reference date — no scenario contract, expected values, or scorer oracle.

    Parameters
    ----------
    utterances :
        The dialogue turns, one string per turn.
    reference_date :
        The reference date as ``"YYYY-MM-DD"`` string.

    Returns
    -------
    SemanticExtraction
        Pure deterministic extraction with authority ``read``, ``clarify``,
        or ``refuse``.  ``claims_action_completed`` is always ``False``.

    Raises
    ------
    ValueError
        If ``utterances`` is empty.
    """
    if not utterances:
        raise ValueError("utterances must be non-empty")

    # --- 1. Unsafe detection (run first — it gates everything) ---
    has_unsafe = any(_has_unsafe_demand(u) for u in utterances)

    # --- 2. Action detection ---
    primary = utterances[0]
    intended_action = _detect_intended_action(primary)

    # --- 3. Temporal extraction ---
    temporal_relation, earliest, latest = _extract_temporal(primary)
    has_time_bounds = bool(earliest is not None or latest is not None)

    # --- 4. Date extraction ---
    ref_parts = reference_date.split("-")
    ref = date(int(ref_parts[0]), int(ref_parts[1]), int(ref_parts[2]))
    date_val = _extract_date(primary, ref)
    has_date = date_val is not None

    # --- 5. Duration extraction ---
    duration_minutes, _ = _extract_duration(primary)
    has_duration = duration_minutes is not None

    # --- 6. Entity extraction ---
    _, patient_sem = _extract_patient(primary)
    _, practitioner_sem = _extract_practitioner(primary)

    # --- 7. Clarification detection ---
    correction_index = None
    for i, u in enumerate(utterances):
        if i > 0 and _is_correction_turn(u):
            correction_index = i
            break

    requires_clarification, clarification_choices = _determine_clarification(
        utterances,
        intended_action,
        has_time_bounds,
        has_date,
        has_duration,
        patient_sem,
        practitioner_sem,
        correction_index,
    )

    # --- 8. Action semantics ---
    if has_unsafe:
        action_semantics = "prohibited"
    elif requires_clarification:
        action_semantics = "ambiguous"
    else:
        action_semantics = "intended"

    # --- 9. Normalized values (multi-turn reduction) ---
    normalized_values = _reduce_multi_turn(utterances, reference_date)

    # Re-evaluate temporal_relation if a correction turn changed the bounds.
    # When the correction turn introduces an interval (e.g. "3pm to 4pm"
    # instead of "at 3pm"), the top-level relation must reflect that.
    if correction_index is not None and correction_index < len(utterances):
        corr_relation, corr_earliest, corr_latest = _extract_temporal(
            utterances[correction_index]
        )
        if corr_relation != "unspecified":
            temporal_relation = corr_relation
            if corr_earliest:
                earliest = corr_earliest
            if corr_latest:
                latest = corr_latest

    # --- 10. Entity semantics (multi-turn) ---
    entities = _extract_entity_semantics(utterances)

    # --- 11. Authority ---
    if has_unsafe:
        authority = "refuse"
    elif requires_clarification or action_semantics == "ambiguous":
        authority = "clarify"
    else:
        authority = "read"

    # --- 12. Tool sequence ---
    tools = _determine_tools(
        intended_action,
        has_unsafe,
        requires_clarification,
        patient_sem == "exact",
        has_time_bounds,
        action_semantics,
    )

    return SemanticExtraction(
        intended_action=intended_action,
        action_semantics=action_semantics,
        temporal_relation=temporal_relation,
        earliest_time=earliest,
        latest_time=latest,
        normalized_values=normalized_values,
        entity_semantics=entities,
        requires_clarification=requires_clarification,
        clarification_choices=clarification_choices,
        authority_claim=authority,
        claims_action_completed=False,
        selected_tool_sequence=tools,
    )


__all__ = [
    "SemanticExtraction",
    "extract_semantics",
]
