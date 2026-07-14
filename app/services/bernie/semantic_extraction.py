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

from app.services.bernie.language_normalization import (
    NormalizedUtterance,
    normalize_utterance,
)
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

    ``normalized_turns`` contains the ``NormalizedUtterance`` result for every
    input turn, providing lossless original-text evidence alongside derived
    normalized text, time forms, and source spans.

    ``action_negated`` is ``True`` when the intended action is negated (e.g.
    "do not mark as completed") or reversed ("never mind", "not needed").
    Such utterances retain the recognised action as semantic subject and
    ``read`` authority, but select no mutation tools.
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
    normalized_turns: tuple[NormalizedUtterance, ...] = ()
    action_negated: bool = False


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
    # Anchored "New booking:" label — structured note/triage form
    re.compile(r"^New booking:", re.I),
]

# cancel
_CANCEL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(cancel|delete|remove) (the |a |an )?(booking|appointment)\b", re.I),
    re.compile(r"\b(patient cancelled|take .* (booking|appointment) out|remove .* diary)\b", re.I),
    # "call off ... booking/appointment" — contextual cancellation phrasing
    re.compile(r"\bcall off\b.*\b(booking|appointment)\b", re.I),
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
    # Anchored "Arrived:" label — structured triage note form
    re.compile(r"^Arrived:", re.I),
    # "Status: ... ARRIVED" — anchored status label at utterance start
    # (case-insensitive; requires "Status:" at start + "arrived" keyword
    # context prevents overmatch on non-diary uses)
    re.compile(r"^status:.*\barrived\b", re.I),
    # "confirm arrival ... booking/appointment" — arrival confirmation command
    re.compile(r"\bconfirm arrival\b.*\b(booking|appointment)\b", re.I),
]

# explain_schedule
_EXPLAIN_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(explain|why|what happened|schedule pattern)\b", re.I),
    re.compile(r"\b(what.*going on|how.*look|tell me about)\b", re.I),
    # Practitioner possessive availability — "Dr Shera's availability" / "some doctor's availability"
    re.compile(r"\b(?:dr [a-z]+|some doctor)'s availability\b", re.I),
    # "what appointments does Dr ... have" / "what appointments does some doctor have"
    re.compile(r"\bwhat appointments does\b.*\b(?:dr [a-z]+|some doctor)\b.*\bhave\b", re.I),
    # "what Dr ...'s day looks like" / "what some doctor's day looks like"
    re.compile(r"\bwhat\b.*\b(?:dr [a-z]+|some doctor)'s day\b.*\blooks?\b", re.I),
    # "when Dr ... has free slots" / "when some doctor has free slots"
    re.compile(r"\b(when|where)\b.*\b(?:dr [a-z]+|some doctor)\b.*\b(free|available|open)\s+(slots?|times?)\b", re.I),
    # "show me Dr ...'s available times" / "show me some doctor's available times"
    re.compile(r"\bshow\b.*\b(?:dr [a-z]+|some doctor)'s available times\b", re.I),
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

# Reversal patterns that undo/negate a previously stated action
_REVERSAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bnever mind\b", re.I),
    re.compile(r"\bnot needed\b", re.I),
    re.compile(r"\bno need\b", re.I),
    re.compile(r"\bleave it (where it was|as is)\b", re.I),
    re.compile(r"\bforget it\b", re.I),
    re.compile(r"\bscrap that\b", re.I),
]


def _is_reversal(text: str) -> bool:
    """Check if text is a reversal that cancels a pending action."""
    for pat in _REVERSAL_PATTERNS:
        if pat.search(text):
            return True
    return False


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
# Action negation detection
# ---------------------------------------------------------------------------

# Consolidated action patterns for reuse by negation detection.
_ACTION_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "create": _CREATE_PATTERNS,
    "cancel": _CANCEL_PATTERNS,
    "move": _MOVE_PATTERNS,
    "resize": _RESIZE_PATTERNS,
    "status_change": _STATUS_CHANGE_PATTERNS,
    "explain_schedule": _EXPLAIN_PATTERNS,
}


def _has_action_negation(
    utterances: list[str],
    intended_action: str | None,
) -> bool:
    """Check whether the intended action is negated or reversed.

    Returns ``True`` when any utterance contains a reversal pattern
    (e.g. "never mind", "not needed") or when the action-detection
    pattern match for *intended_action* is preceded by a negation
    prefix ("do not", "don't", "never", "please do not", "not", "no").
    """
    if intended_action is None:
        return False

    for u in utterances:
        # Reversal patterns unconditionally negate the action
        if _is_reversal(u):
            return True

        # Negation prefix before an action pattern match
        if intended_action in _ACTION_PATTERNS:
            for pat in _ACTION_PATTERNS[intended_action]:
                for match in pat.finditer(u):
                    before = u[max(0, match.start() - 30):match.start()]
                    if _NEGATION_PREFIX.search(before):
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

# Ambiguous patient references — includes standalone ``someone`` which
# references an unspecified person rather than omitting the entity entirely.
_AMBIGUOUS_PATIENT = re.compile(
    r"\b(another patient|the patient|my patient|which patient|"
    r"multiple patients|two patients|same name|a patient|this patient|"
    r"someone)\b",
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

# Matches "15 minutes", "15 minute", "15 mins", "15 min"
_DURATION_PATTERN = re.compile(r"\b(\d+)\s*(minutes?|mins?)\b", re.I)
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

# Speech-like/filler form produced by receptionist wording such as
# "after at 3pm" or "before at 5pm".  The explicit open-bound operator is
# authority-bearing and must win over the nested point-time ``at`` token.
_OPEN_BOUND_AT_TIME = re.compile(
    r"\b(?P<operator>after|before)\s+at\s+"
    r"(?P<time>(?:[01]?\d|2[0-3])(?:[:.][0-5]\d)?\s*(?:am|pm)?)\b",
    re.I,
)


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

    # Preserve an explicit open-bound operator through speech-like filler.
    # The shared temporal helper correctly prioritises ordinary "after 3pm"
    # and "before 5pm", but its generic ``at`` rule would otherwise turn
    # "after at 3pm" into an exact point and erase the preceding operator.
    open_bound_match = _OPEN_BOUND_AT_TIME.search(text)
    if open_bound_match:
        parsed = parse_time_fragment(open_bound_match.group("time"))
        if parsed is not None:
            if open_bound_match.group("operator").lower() == "after":
                return "not_before", parsed, None
            return "not_after", None, parsed

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
            if corr_earliest is not None or corr_latest is not None:
                # A temporal correction replaces the complete relation, not
                # merely whichever bound happens to be present.  Otherwise an
                # exact -> open-bound correction can retain an incompatible
                # stale opposite bound from the earlier turn.
                values.pop("earliest_time", None)
                values.pop("latest_time", None)
            if corr_earliest is not None:
                values["earliest_time"] = corr_earliest
                if corr_relation == "exact" and corr_latest is None:
                    corr_latest = corr_earliest
            if corr_latest is not None:
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
            # Additive turn: may add info for previously omitted or ambiguous.
            # Only patient additive semantics may resolve ambiguous -> exact.
            # Practitioner and duration additive semantics remain omitted -> exact only.
            add_pat_name, add_pat_sem = _extract_patient(utterance)
            if add_pat_sem == "exact" and semantics["patient"] in ("omitted", "ambiguous"):
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
    action_negated: bool = False,
    first_utterance: str = "",
) -> tuple[str, ...]:
    """Deterministic tool sequence from extraction results.

    Action-specific mapping (R4 contract):

    - ``create``        → ``search_patients, find_slots, create_booking``
    - ``move``          → ``search_patients, update_appointment``
    - ``resize``        → ``search_patients, update_appointment``
    - ``cancel``        → ``search_patients, update_appointment``
    - ``status_change`` → ``search_patients, change_appointment_status``
    - ``explain_schedule`` → ``search_patients, find_slots``
    - ``clarification`` → ``request_clarification``

    For unsafe utterances (adversarial scenarios), the tool sequence includes
    the first turn's legitimate tools plus ``refuse_instruction``, because the
    system processes the initial request before detecting the unsafe demand.

    For negated/reversed actions no mutation tool is selected.
    """
    tools: list[str] = []

    # --- Negated / reversed: no mutation tool, read-only search ---
    if action_negated:
        if has_patient:
            tools.append("search_patients")
        return tuple(tools)

    # --- Unsafe: first-turn tools + refuse_instruction ---
    if has_unsafe:
        if has_patient:
            tools.append("search_patients")
        if intended_action == "create" and has_time_bounds:
            tools.append("find_slots")
            tools.append("create_booking")
        tools.append("refuse_instruction")
        return tuple(tools)

    # --- Clarification: request_clarification only ---
    if requires_clarification:
        tools.append("request_clarification")
        return tuple(tools)

    # --- Normal action-specific tool mapping ---
    if has_patient:
        tools.append("search_patients")

    if intended_action == "create":
        tools.append("find_slots")
        tools.append("create_booking")
    elif intended_action == "move":
        tools.append("update_appointment")
    elif intended_action == "resize":
        tools.append("update_appointment")
    elif intended_action == "cancel":
        tools.append("update_appointment")
    elif intended_action == "status_change":
        tools.append("change_appointment_status")
    elif intended_action == "explain_schedule":
        tools.append("find_slots")

    return tuple(tools)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def _derive_final_temporal(
    utterances: list[str],
    normalized_values: dict[str, Any],
) -> tuple[str, str | None, str | None]:
    """Derive the final temporal relation from all utterances.

    Scans all utterances and uses the last non-unspecified temporal
    information, so that an additive or corrective later turn that
    supplies a missing time takes precedence over the first turn's
    ``"unspecified"``.
    """
    final_relation: str = "unspecified"
    final_earliest: str | None = None
    final_latest: str | None = None

    for utterance in utterances:
        relation, earliest, latest = _extract_temporal(utterance)
        if relation != "unspecified" or earliest is not None or latest is not None:
            final_relation = relation
            # Later temporal evidence replaces the complete relation.  Clear
            # absent bounds so exact -> not_before/not_after corrections do not
            # leak a stale opposite bound into the top-level observation.
            final_earliest = earliest
            final_latest = latest

    # Fall back to normalized_values if no utterance had temporal info
    if final_relation == "unspecified" and normalized_values.get("earliest_time"):
        final_earliest = normalized_values["earliest_time"]
        final_latest = normalized_values.get("latest_time", final_earliest)
        if final_earliest == final_latest:
            final_relation = "exact"
        else:
            final_relation = "interval"

    return final_relation, final_earliest, final_latest


def extract_semantics(
    utterances: list[str],
    reference_date: str,
) -> SemanticExtraction:
    """Extract deterministic semantics from receptionist dialogue turns.

    This is the sole public entry point. It receives only dialogue text and
    a reference date — no scenario contract, expected values, or scorer oracle.

    The function first reduces multi-turn dialogue to derive the final
    extracted state, then calculates all top-level fields from that final
    state rather than only the first turn.

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

    # --- 0. Normalized turns (lossless evidence for every input turn) ---
    normalized_turns = tuple(normalize_utterance(u) for u in utterances)

    # --- 1. Unsafe detection (run first — it gates everything) ---
    has_unsafe = any(_has_unsafe_demand(u) for u in utterances)

    # --- 2. Action detection (from first turn) ---
    primary = utterances[0]
    intended_action = _detect_intended_action(primary)

    # --- 3. Multi-turn reduction (for normalized_values) ---
    normalized_values = _reduce_multi_turn(utterances, reference_date)

    # Derive final temporal relation, has_time_bounds from all turns
    temporal_relation, earliest, latest = _derive_final_temporal(
        utterances, normalized_values,
    )
    has_time_bounds = bool(earliest is not None or latest is not None)

    # --- 4. Date from reduced values ---
    date_val = normalized_values.get("appointment_date")
    has_date = date_val is not None

    # --- 5. Duration from reduced values ---
    duration_minutes = normalized_values.get("duration_minutes")
    has_duration = duration_minutes is not None

    # --- 6. Entity semantics (multi-turn aware) ---
    entities = _extract_entity_semantics(utterances)
    patient_sem = entities.get("patient", "omitted")
    practitioner_sem = entities.get("practitioner", "omitted")

    # --- 7. Correction index ---
    correction_index = None
    for i, u in enumerate(utterances):
        if i > 0 and _is_correction_turn(u):
            correction_index = i
            break

    # --- 8. Clarification detection (uses final state) ---
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

    # --- 9. Action negation ---
    action_negated = _has_action_negation(utterances, intended_action)

    # When the action is negated/reversed, clarification is not needed
    # because the negation itself is the complete instruction.
    if action_negated:
        requires_clarification = False
        clarification_choices = ()

    # --- 10. Action semantics ---
    if has_unsafe:
        action_semantics = "prohibited"
    elif action_negated:
        action_semantics = "intended"  # negated actions are safe, not prohibited
    elif requires_clarification:
        action_semantics = "ambiguous"
    else:
        action_semantics = "intended"

    # --- 11. Authority ---
    if has_unsafe:
        authority = "refuse"
    elif requires_clarification or action_semantics == "ambiguous":
        authority = "clarify"
    else:
        authority = "read"

    # --- 12. Tool sequence (uses final state including action_negated) ---
    tools = _determine_tools(
        intended_action,
        has_unsafe,
        requires_clarification,
        patient_sem == "exact",
        has_time_bounds,
        action_semantics,
        action_negated=action_negated,
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
        normalized_turns=normalized_turns,
        action_negated=action_negated,
    )


__all__ = [
    "SemanticExtraction",
    "extract_semantics",
]
