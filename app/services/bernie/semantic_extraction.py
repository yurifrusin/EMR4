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
    re.compile(r"\btake out\b.*\b(?:appt|appointment|booking)\b", re.I),
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
    re.compile(r"\b(?:appt|appointment|booking)\s+length\b", re.I),
    re.compile(r"\bmake it\s+\d+\s*(?:mins?|minutes?|hours?)\b", re.I),
    re.compile(
        r"\bmake\s+[^,.;/]+['’]s\b.*\b(?:appt|appointment|booking)\b"
        r".*\b\d+\s*(?:mins?|minutes?|hours?)\b",
        re.I,
    ),
    # Explicit "resize" verb
    re.compile(r"\bresize\b", re.I),
]

# status_change
_STATUS_CHANGE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(mark .* (arrived|completed|dna|no show)|change .* status)\b", re.I),
    re.compile(r"\b(set .* (arrived|completed|dna|no.show))\b", re.I),
    re.compile(r"\b(update .* status)\b", re.I),
    re.compile(
        r"\bstatus(?:\s+one)?\b.*\b(?:arrived|completed|dna|no[ -]?show)\b",
        re.I,
    ),
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
    re.compile(r"\b(?:diary|schedule)\s+(?:rundown|run[- ]down)\b", re.I),
    re.compile(
        r"\b(?:talk|run)\s+me\s+through\s+(?:it|the\s+(?:diary|schedule))\b",
        re.I,
    ),
    re.compile(r"\bdiary\s+view\b.*\bview\s+only\b", re.I),
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
    # Clash/guardrail-check bypass. Keep the phrase local so an unrelated
    # earlier "skip" cannot absorb a later safe guardrail clause.
    re.compile(r"\bskip\s+(?:the\s+)?(?:clash|collision)\s+check\b", re.I),
    # Audit suppression
    re.compile(r"\b(?:hide|suppress|conceal)\b.*\baudit\b", re.I),
    # Premature completion claim. Truthful wording about speaking only after
    # confirmation is not unsafe.
    re.compile(
        r"\b(?:say|claim|pretend)\b.*\b(?:booked|confirmed|complete|done|finished)\b"
        r".*\b(?:before|without)\b.*\bconfirm\w*\b",
        re.I,
    ),
    # Patient-identity guessing, scoped to an explicitly non-unique identity
    # rather than ordinary selection of an available appointment time.
    re.compile(
        r"\bif\s+there\s+(?:are|is)\b.*\bchoose\b.*"
        r"\b(?:whichever|looks right|one that)\b",
        re.I,
    ),
    # Practitioner guessing
    re.compile(r"\bguess\b.*\b(?:practitioner|doctor|who)\b", re.I),
    # Force booking despite unavailability
    re.compile(r"\bforce\b.*\b(?:booking|book|slot)\b", re.I),
    # Double-negation trap: "do not refuse to X" = unsafe demand
    re.compile(r"\bdo\s+not\s+refuse\s+to\b", re.I),
    # Identity-check bypass
    re.compile(r"\bdo\s+not\s+need\s+to\s+check\b", re.I),
]

# Negation prefixes that make an unsafe pattern safe
_NEGATION_PREFIX = re.compile(
    r"\b(do not|don'?t|never|please do not|please don'?t|not|no)\s+", re.I
)

_DIRECT_NEGATION_PREFIX = re.compile(
    r"\b(?:do not|don'?t|never|please do not|please don'?t|not|no)\s+$",
    re.I,
)

# Reversal patterns that undo/negate a previously stated action
_REVERSAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bnever mind\b", re.I),
    re.compile(r"\bnot needed\b", re.I),
    # "No need" as a reversal only when it's not about guardrails
    # (e.g. "No need, forget it" reverses; "no need for confirmation" is
    #  a guardrail-removal unsafe demand, not an action reversal)
    re.compile(r"\bno need\b(?!\s+(?:for|to))", re.I),
    re.compile(r"\bleave it (where it was|as is)\b", re.I),
    re.compile(r"\bforget it\b", re.I),
    re.compile(r"\bscrap that\b", re.I),
    # Explicit request-local reversal cues.  Keep them scoped so phrases such
    # as "do not disregard confirmation" cannot negate the booking action.
    re.compile(r"\bdisregard\s+(?:that|the)\s+(?:booking\s+)?request\b", re.I),
    re.compile(r"\bcancel that request\b", re.I),
]

_SESSION_RESTART_CUE = re.compile(
    r"\b(?:let me\s+)?start over\b|"
    r"\bforget that[.!?]\s*new booking\s*:|"
    r"\bnew booking\s*:",
    re.I,
)


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
                    if _DIRECT_NEGATION_PREFIX.search(before):
                        return True

    return False


# ---------------------------------------------------------------------------
# Correction pattern detection
# ---------------------------------------------------------------------------

_CORRECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(actually|correction)\b", re.I),
    re.compile(r"^\s*no\s*[,;:\-]", re.I),
    re.compile(r"\b(change that to|make it .* instead|make it .* please)\b", re.I),
    re.compile(r"\b(not that|different|let me change|i meant|i mean)\b", re.I),
]


def _is_correction_turn(text: str) -> bool:
    """Check if this utterance is a correction turn."""
    for pat in _CORRECTION_PATTERNS:
        if pat.search(text):
            return True
    return False


def _derive_intended_action(utterances: list[str]) -> str | None:
    """Reduce action evidence across turns without inventing an action.

    Preserve the established first-turn contract. Only the explicit bounded
    receptionist preface used for a pending diary request may defer action
    evidence to a later turn. This prevents unrelated later corrections or
    session text from changing an already established action.
    """
    intended_action = _detect_intended_action(utterances[0])
    if intended_action is not None:
        return intended_action
    if not re.search(
        r"\bdiary request\b.*\bdetails may need clarifying\b",
        utterances[0],
        re.I,
    ):
        return None
    for utterance in utterances[1:]:
        detected = _detect_intended_action(utterance)
        if detected is not None:
            return detected
    return None


# ---------------------------------------------------------------------------
# Location extraction
# ---------------------------------------------------------------------------

_LOCATION_ROOM_PATTERN = re.compile(
    r"\b(?:in\s+)?(?:Room|room)\s+(\d+)\b",
)

_LOCATION_AMBIGUOUS = re.compile(
    r"\b(?:any\s+room|some\s+room|which\s+room)\b",
    re.I,
)

_LOCATION_NEGATION_PREFIX = re.compile(
    r"\bnot\s+in\s+", re.I
)


def _extract_location(text: str) -> tuple[str | None, str]:
    """Extract location (room reference) from utterance.

    Returns (location value or None, semantics label).
    Semantics is ``"exact"``, ``"omitted"``, ``"ambiguous"``, or ``"negated"``.
    """
    # Check for "Room X or Room Y" pattern for location ambiguity
    _LOCATION_OR = re.compile(
        r"\b(?:Room|room)\s+(\d+)\s+or\s+(?:Room|room)\s+(\d+)\b"
    )
    if _LOCATION_OR.search(text):
        return None, "ambiguous"

    # Check negation first: "not in Room 2"
    neg_scope = _LOCATION_NEGATION_PREFIX.search(text)
    if neg_scope:
        after_neg = text[neg_scope.end():]
        room_m = _LOCATION_ROOM_PATTERN.search(after_neg)
        if room_m:
            return room_m.group(1), "negated"

    if _LOCATION_AMBIGUOUS.search(text):
        return None, "ambiguous"

    m = _LOCATION_ROOM_PATTERN.search(text)
    if m:
        return m.group(1), "exact"

    return None, "omitted"


# ---------------------------------------------------------------------------
# Appointment type extraction
# ---------------------------------------------------------------------------

_APPOINTMENT_TYPE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bstandard consultation\b", re.I), "standard_consultation"),
    (re.compile(r"\blong consultation\b", re.I), "long_consultation"),
    (re.compile(r"\bcare plan appointment\b", re.I), "care_plan_appointment"),
]

_APPOINTMENT_TYPE_AMBIGUOUS = re.compile(
    r"\b(?:any\s+appointment\s+type|any\s+type|any\s+kind|"
    r"whatever\s+(?:type|kind)|doesn'?t\s+matter)\b",
    re.I,
)

_APPOINTMENT_TYPE_NEGATION_PREFIX = re.compile(
    r"\bnot\s+(?:a\s+|an\s+)?", re.I
)


def _extract_appointment_type(text: str) -> tuple[str | None, str]:
    """Extract appointment type from utterance.

    Returns (type value or None, semantics label).
    Semantics is ``"exact"``, ``"omitted"``, ``"ambiguous"``, or ``"negated"``.
    """
    # Check for "X or Y" pattern for appointment type ambiguity
    # before checking individual types (must handle optional "a/an" after "or").
    _APPOINTMENT_TYPE_OR = re.compile(
        r"(?:standard consultation|care plan appointment|long consultation|follow-up)"
        r"\s+or\s+(?:a\s+|an\s+)?"
        r"(?:standard consultation|care plan appointment|long consultation|follow-up)",
        re.I,
    )
    if _APPOINTMENT_TYPE_OR.search(text):
        return None, "ambiguous"

    if _APPOINTMENT_TYPE_AMBIGUOUS.search(text):
        return None, "ambiguous"

    for pat, type_name in _APPOINTMENT_TYPE_PATTERNS:
        m = pat.search(text)
        if m:
            # Check for local negation prefix near the match
            before = text[max(0, m.start() - 15):m.start()]
            if re.search(r"\bnot\s+(?:a\s+|an\s+)?$", before, re.I):
                return type_name, "negated"
            return type_name, "exact"

    return None, "omitted"


# ---------------------------------------------------------------------------
# Patient name extraction
# ---------------------------------------------------------------------------

_PATIENT_PATTERN = re.compile(
    r"\b(?:for |appointment for |schedule |patient |"
    r"[Bb]ook |[Mm]ake |[Cc]reate |[Ss]ee |[Nn]eed |[Ww]ant |"
    r"[Aa]n appointment for |[Aa] booking for )?"
    r"(?!Dr\s+[A-Z])"
    r"(?!(?:Book|Make|Create|Schedule|See|Move|Resize|Cancel|Mark|Explain|Tell)\s)"
    r"([A-Z][a-z]+(?:\s+(?!Dr\b)[A-Z][a-z]+)+)\b",
)

# Single given name after a booking verb (e.g. "Book Alex") — inherently
# ambiguous because a single given name does not uniquely identify a patient.
_SINGLE_PATIENT_PATTERN = re.compile(
    r"\b(?:[Bb]ook|[Ss]ee)\s+(?!Dr\b)([A-Z][a-z]+)\s+(?=with\b|for\b)",
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
    Semantics is ``"exact"``, ``"omitted"``, ``"ambiguous"``, or ``"negated"``.

    A single given name (e.g. "Book Alex") is inherently ambiguous and
    returns ``ambiguous`` semantics.
    """
    if _AMBIGUOUS_PATIENT.search(text):
        return None, "ambiguous"

    # Check for "X or Y" pattern for patient ambiguity
    # Exclude "Dr" titles from being captured as patient names.
    _PATIENT_OR = re.compile(
        r"\b(?:book|schedule|create|appointment\s+for)\s+"
        r"(?!Dr\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+or\s+"
        r"(?!Dr\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
        re.I,
    )
    if _PATIENT_OR.search(text):
        return None, "ambiguous"

    m = _PATIENT_PATTERN.search(text)
    if m:
        # Check if "not" or "not for" precedes the captured name
        before = text[max(0, m.start(1) - 12):m.start(1)]
        if re.search(r"\bnot\s+(?:for\s+)?$", before, re.I):
            return m.group(1), "negated"
        return m.group(1), "exact"
    # Single given name after a booking verb is ambiguous
    single_m = _SINGLE_PATIENT_PATTERN.search(text)
    if single_m:
        return single_m.group(1), "ambiguous"
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
    Semantics is ``"exact"``, ``"omitted"``, ``"ambiguous"``, or ``"negated"``.
    """
    if _AMBIGUOUS_PRACTITIONER.search(text):
        return None, "ambiguous"

    # Check for "Dr X or Dr Y" pattern for practitioner ambiguity
    _PRACTITIONER_OR = re.compile(
        r"\b(Dr\s+[A-Z][a-z]+)\s+or\s+(Dr\s+[A-Z][a-z]+)\b"
    )
    if _PRACTITIONER_OR.search(text):
        return None, "ambiguous"

    m = _PRACTITIONER_PATTERN.search(text)
    if m:
        # Check if "not" or "not with" precedes the captured name
        before = text[max(0, m.start(1) - 14):m.start(1)]
        if re.search(r"\bnot\s+(?:with\s+)?$", before, re.I):
            return m.group(1), "negated"
        return m.group(1), "exact"
    return None, "omitted"


# ---------------------------------------------------------------------------
# Duration extraction
# ---------------------------------------------------------------------------

# Matches "15 minutes", "15 minute", "15 mins", "15 min"
_DURATION_PATTERN = re.compile(r"\b(\d+)\s*(minutes?|mins?)\b", re.I)
_DURATION_AMBIGUOUS = re.compile(
    r"\b(how long|some time|a while|"
    r"short(?!\s+(?:consultation|appointment))|"
    r"long(?!\s+(?:consultation|appointment)))\b",
    re.I,
)

_DURATION_OR_PATTERN = re.compile(
    r"\b(\d+)\s+or\s+(\d+)\s*(minutes?|mins?)\b", re.I
)

# Lexical duration forms mapped to minutes
_LEXICAL_DURATION: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"\bhalf\s+an?\s+hour\b", re.I), 30),
    (re.compile(r"\bone\s+hour\b", re.I), 60),
    (re.compile(r"\ba\s+quarter\s+of\s+an\s+hour\b", re.I), 15),
    (re.compile(r"\bquarter\s+of\s+an\s+hour\b", re.I), 15),
]


def _extract_duration(text: str) -> tuple[int | None, str]:
    """Extract duration in minutes from utterance.

    Returns (minutes or None, semantics label).
    Supports numeric patterns (e.g. ``"30 minutes"``) and lexical forms
    (``"half an hour"``, ``"one hour"``, ``"quarter of an hour"``).

    When a numeric or lexical duration is preceded by a negation prefix,
    the semantics is ``"negated"`` and the value is not returned as a
    normalized duration.
    """
    # Check negation before any match
    def _check_negation(match_start: int) -> bool:
        before = text[max(0, match_start - 30):match_start]
        return bool(
            re.search(
                r"\b(?:but\s+not|not|except)\s+(?:for\s+)?$",
                before,
                re.I,
            )
        )

    # Check for "X or Y minutes" pattern for duration ambiguity
    if _DURATION_OR_PATTERN.search(text):
        return None, "ambiguous"

    # Try lexical forms first (before numeric, so "half an hour" is not confused)
    for pat, minutes in _LEXICAL_DURATION:
        m = pat.search(text)
        if m:
            if _check_negation(m.start()):
                return None, "negated"
            return minutes, "exact"

    # Try numeric pattern
    m = _DURATION_PATTERN.search(text)
    if m:
        if _check_negation(m.start()):
            return None, "negated"
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
# Weekday names for relative date resolution
_WEEKDAY_NAMES = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def _weekday_to_date(weekday: str, reference_date: date) -> str | None:
    """Resolve a weekday name to an ISO date relative to reference_date.

    Returns the next occurrence of the given weekday (today or later).
    """
    target = _WEEKDAY_NAMES.get(weekday.lower())
    if target is None:
        return None
    current_weekday = reference_date.weekday()
    days_ahead = target - current_weekday
    if days_ahead <= 0:
        days_ahead += 7
    return (reference_date + timedelta(days=days_ahead)).isoformat()


def _extract_date(
    text: str,
    reference_date: date,
) -> str | None:
    """Extract appointment date from text relative to reference_date.

    Supports today, tomorrow, day-after-tomorrow, and weekday names.
    """
    if _DAY_AFTER_TOMORROW.search(text):
        return (reference_date + timedelta(days=2)).isoformat()
    if _TOMORROW.search(text):
        return (reference_date + timedelta(days=1)).isoformat()
    if _TODAY.search(text):
        return reference_date.isoformat()
    # Check weekday names
    for wd_name in _WEEKDAY_NAMES:
        if re.search(rf"\b{wd_name}\b", text, re.I):
            result = _weekday_to_date(wd_name, reference_date)
            if result is not None:
                return result
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

_NEGATED_BOUND_TIME = re.compile(
    r"\bnot\s+(?P<operator>before|after)\s+"
    r"(?P<time>(?:[01]?\d|2[0-3])(?:[:.][0-5]\d)?\s*(?:am|pm)?)\b",
    re.I,
)

_OR_LATER_TIME = re.compile(
    r"\b(?P<time>(?:[01]?\d|2[0-3])(?:[:.][0-5]\d)?\s*(?:am|pm)?)"
    r"\s+or\s+later\b",
    re.I,
)

_BY_TIME = re.compile(
    r"\bby\s+(?P<time>(?:[01]?\d|2[0-3])(?:[:.][0-5]\d)?\s*(?:am|pm)?)\b",
    re.I,
)

_CORRECTED_APPROXIMATE_TIME = re.compile(
    r"\b(?:sorry|actually|correction|i mean|i meant)\b[^.!?]*?"
    r"\b(?:around|about)\s+"
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

    corrected_approximate = _CORRECTED_APPROXIMATE_TIME.search(text)
    if corrected_approximate:
        parsed = parse_time_fragment(corrected_approximate.group("time"))
        if parsed is not None:
            return "approximate", parsed, parsed

    or_later = _OR_LATER_TIME.search(text)
    if or_later:
        parsed = parse_time_fragment(or_later.group("time"))
        if parsed is not None:
            return "not_before", parsed, None

    by_time = _BY_TIME.search(text)
    if by_time:
        parsed = parse_time_fragment(by_time.group("time"))
        if parsed is not None:
            return "not_after", None, parsed

    # ``not before`` is a lower bound and ``not after`` is an upper bound.
    # Handle these authority-bearing phrases before the shared helper, whose
    # generic negation treatment otherwise reverses them.
    negated_bound_match = _NEGATED_BOUND_TIME.search(text)
    if negated_bound_match:
        parsed = parse_time_fragment(negated_bound_match.group("time"))
        if parsed is not None:
            if negated_bound_match.group("operator").lower() == "before":
                return "not_before", parsed, None
            return "not_after", None, parsed

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

    # Lossless normalization retains spoken fragments and their source spans
    # while supplying canonical HH:MM values. Consume only derived values;
    # never replace the original utterance evidence.
    normalized = normalize_utterance(text)
    spoken_times = [
        (fragment, canonical)
        for fragment, canonical in normalized.time_forms.items()
        if not any(character.isdigit() for character in fragment)
    ]
    if spoken_times:
        spoken_times.sort(
            key=lambda item: normalized.source_spans.get(
                f"time:{item[0]}", (len(text), len(text))
            )[0]
        )
        values = [canonical for _fragment, canonical in spoken_times]
        if len(values) >= 2 and re.search(r"\bbetween\b", text, re.I):
            return "interval", values[0], values[1]
        canonical = values[0]
        if re.search(r"\b(?:after|not\s+before)\b", text, re.I):
            return "not_before", canonical, None
        if re.search(r"\b(?:before|not\s+after)\b", text, re.I):
            return "not_after", None, canonical
        if re.search(r"\b(?:around|about)\b", text, re.I):
            return "approximate", canonical, canonical
        return "exact", canonical, canonical

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


def _extract_duration_alternatives(utterances: list[str]) -> tuple[str, ...]:
    """Return only duration alternatives explicitly present in the dialogue."""
    for utterance in utterances:
        match = _DURATION_OR_PATTERN.search(utterance)
        if match:
            unit = match.group(3)
            return (
                f"{match.group(1)} {unit}",
                f"{match.group(2)} {unit}",
            )
    return ()


def _extract_practitioner_alternatives(
    utterances: list[str],
) -> tuple[str, ...]:
    """Return only explicit ``Dr X or Dr Y`` alternatives in source order."""
    pattern = re.compile(
        r"\b(Dr\s+(?-i:[A-Z])[a-z]+)\s+or\s+"
        r"(Dr\s+(?-i:[A-Z])[a-z]+)\b"
    )
    for utterance in utterances:
        match = pattern.search(utterance)
        if match:
            return match.group(1), match.group(2)
    return ()


def _determine_clarification(
    utterances: list[str],
    intended_action: str | None,
    has_time_bounds: bool,
    has_date: bool,
    has_duration: bool,
    patient_semantics: str,
    practitioner_semantics: str,
    correction_index: int | None,
    duration_semantics: str = "omitted",
    entities: dict[str, str] | None = None,
    temporal_relation: str = "unspecified",
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

    Negated required entities (patient, practitioner, duration) fail closed
    into clarification.
    """
    from app.services.diary.temporal import parse_time_fragment

    if intended_action is None:
        return True, ()  # Unknown action -> clarify

    # Practitioner ambiguity is action-independent. Surface only choices
    # actually present in the dialogue; generic ``some doctor`` wording has
    # no lossless alternatives to invent.
    if practitioner_semantics == "ambiguous":
        return True, _extract_practitioner_alternatives(utterances)

    if intended_action == "create":
        needs_clarify = False
        choices: list[str] = []

        # "Sometime in the afternoon" is truly ambiguous about exact time
        primary = utterances[0]
        has_sometime = bool(_SOMETIME_AFTERNOON.search(primary))

        # If first turn has "sometime" but overall we have time bounds from
        # a later turn, the time has been resolved (Rule 5).
        if has_sometime and not has_time_bounds:
            needs_clarify = True
        elif has_sometime:
            needs_clarify = False

        # Negated, ambiguous, or omitted patient requires clarification
        # (omitted required patient identity fails closed, Rule 1)
        if patient_semantics in ("ambiguous", "negated", "omitted"):
            needs_clarify = True
            choices = []
        # Negated or ambiguous practitioner requires clarification
        elif practitioner_semantics == "negated":
            needs_clarify = True
            choices = []
        elif has_sometime and not has_time_bounds:
            choices = ["1pm", "2pm", "3pm", "4pm"]
        # Date present but no time bounds → clarify for time
        elif has_date and not has_time_bounds:
            needs_clarify = True
            choices = ["Morning", "Afternoon", "All day"]
        # No date and no time bounds → clarify
        elif not has_date and not has_time_bounds:
            needs_clarify = True
            choices = ["Morning", "Afternoon", "All day"]

        # Negated duration requires clarification (user must provide replacement)
        if duration_semantics == "negated":
            needs_clarify = True
            choices = []

        # Any other negated entity on create requires clarification
        # (location, appointment_type — Rule 3)
        if not needs_clarify and entities is not None:
            for entity_key in ("location", "appointment_type"):
                if entities.get(entity_key) == "negated":
                    needs_clarify = True
                    choices = []
                    break

        # Ambiguous location, appointment_type, or duration on create also
        # requires clarification (Rule 2, Rule 4)
        if not needs_clarify and entities is not None:
            for entity_key in ("location", "appointment_type", "duration"):
                if entities.get(entity_key) == "ambiguous":
                    needs_clarify = True
                    choices = []
                    break

        # An approximate window is useful search evidence, but it is not an
        # exact create target. Preserve the bounds and ask for an exact choice
        # before exposing any create authority.
        if temporal_relation == "approximate" and not has_sometime:
            needs_clarify = True
            choices = []

        # Correction may resolve (but not for negated entities)
        if correction_index is not None and needs_clarify and duration_semantics != "negated" \
                and patient_semantics not in ("ambiguous", "negated") \
                and practitioner_semantics not in ("ambiguous", "negated"):
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
            return True, _extract_duration_alternatives(utterances)
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
        # Explain: a resolved practitioner (exact or corrected) is sufficient
        # read-only context for a practitioner schedule question.  Patient
        # identity is only required when no practitioner is resolved.
        if practitioner_semantics in ("exact", "corrected"):
            return False, ()
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
    dur, dur_sem = _extract_duration(primary)
    if dur is not None and dur_sem != "negated":
        values["duration_minutes"] = dur

    # Time period
    period = _extract_time_period(primary)
    if period:
        values["time_period"] = period

    # Process remaining turns
    for i, utterance in enumerate(utterances[1:], start=1):
        # Session restart: discard all prior context and re-extract
        if _SESSION_RESTART_CUE.search(utterance):
            values = {}
            restart_date = _extract_date(utterance, ref)
            if restart_date:
                values["appointment_date"] = restart_date
            _, restart_earliest, restart_latest = _extract_temporal(utterance)
            if restart_earliest:
                values["earliest_time"] = restart_earliest
            if restart_latest:
                values["latest_time"] = restart_latest
            restart_dur, restart_dur_sem = _extract_duration(utterance)
            if restart_dur is not None and restart_dur_sem != "negated":
                values["duration_minutes"] = restart_dur
            restart_period = _extract_time_period(utterance)
            if restart_period:
                values["time_period"] = restart_period
            continue

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

            corr_dur, corr_dur_sem = _extract_duration(utterance)
            if corr_dur_sem == "negated":
                # Negated duration: remove any previously stored duration value
                values.pop("duration_minutes", None)
            elif corr_dur is not None:
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

            add_dur, add_dur_sem = _extract_duration(utterance)
            if add_dur_sem == "negated":
                values.pop("duration_minutes", None)
            elif add_dur is not None and "duration_minutes" not in values:
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

    # Location
    loc_val, loc_sem = _extract_location(primary)
    semantics["location"] = loc_sem

    # Appointment type
    apt_val, apt_sem = _extract_appointment_type(primary)
    semantics["appointment_type"] = apt_sem

    # Duration
    dur_val, dur_sem = _extract_duration(primary)
    semantics["duration"] = dur_sem

    # --- Session restart detection ---
    # If any turn contains a session-restart cue, discard prior context and
    # re-extract from that turn as a fresh request.
    restart_index: int | None = None
    for i, u in enumerate(utterances):
        if i > 0 and _SESSION_RESTART_CUE.search(u):
            restart_index = i
            break

    if restart_index is not None:
        # Discard prior context and re-extract from the restart turn as primary
        fresh_utterance = utterances[restart_index]
        semantics = {
            "practitioner": "omitted",
            "patient": "omitted",
            "location": "omitted",
            "appointment_type": "omitted",
            "duration": "omitted",
        }
        fresh_pat, fresh_pat_sem = _extract_patient(fresh_utterance)
        semantics["patient"] = fresh_pat_sem
        fresh_prac, fresh_prac_sem = _extract_practitioner(fresh_utterance)
        semantics["practitioner"] = fresh_prac_sem
        fresh_loc, fresh_loc_sem = _extract_location(fresh_utterance)
        semantics["location"] = fresh_loc_sem
        fresh_apt, fresh_apt_sem = _extract_appointment_type(fresh_utterance)
        semantics["appointment_type"] = fresh_apt_sem
        fresh_dur, fresh_dur_sem = _extract_duration(fresh_utterance)
        semantics["duration"] = fresh_dur_sem
        # Keep tuple values for the caller's use of pat_name etc.
        pat_name = fresh_pat
        prac_name = fresh_prac
        return semantics

    # --- Inline correction detection (single-turn) ---
    # Check if the primary utterance itself contains a correction of a named
    # entity (e.g. "Book Sam Smith — sorry, Avery Quinn — with Dr Chen...").
    _INLINE_CORRECTION_CUE = re.compile(
        r"\b(?:sorry|actually|correction|i mean|i meant|instead|make it)\b", re.I
    )
    if _INLINE_CORRECTION_CUE.search(primary):
        # Try to find a corrected patient after the correction cue
        cue_match = _INLINE_CORRECTION_CUE.search(primary)
        after_cue = primary[cue_match.end():]
        corr_pat, corr_pat_sem = _extract_patient(after_cue)
        if corr_pat_sem == "exact" and pat_sem == "exact" and corr_pat != pat_name:
            semantics["patient"] = "corrected"

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

            corr_loc_val, corr_loc_sem = _extract_location(utterance)
            if corr_loc_sem == "exact":
                if semantics["location"] in ("omitted", "ambiguous"):
                    semantics["location"] = "exact"
                elif corr_loc_val != loc_val:
                    semantics["location"] = "corrected"
                # same value -> remains exact

            corr_apt_val, corr_apt_sem = _extract_appointment_type(utterance)
            if corr_apt_sem == "exact":
                if semantics["appointment_type"] in ("omitted", "ambiguous"):
                    semantics["appointment_type"] = "exact"
                elif corr_apt_val != apt_val:
                    semantics["appointment_type"] = "corrected"
                # same value -> remains exact

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

            # Location and appointment type can also be added in additive turns
            add_loc_val, add_loc_sem = _extract_location(utterance)
            if add_loc_sem == "exact" and semantics["location"] == "omitted":
                semantics["location"] = "exact"

            add_apt_val, add_apt_sem = _extract_appointment_type(utterance)
            if add_apt_sem == "exact" and semantics["appointment_type"] == "omitted":
                semantics["appointment_type"] = "exact"

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

    Complementary open bounds in additive turns compose into an interval.
    Corrections and session restarts replace the complete prior relation so a
    stale opposite bound cannot leak into the final state.
    """
    final_relation: str = "unspecified"
    final_earliest: str | None = None
    final_latest: str | None = None

    for index, utterance in enumerate(utterances):
        relation, earliest, latest = _extract_temporal(utterance)
        if relation != "unspecified" or earliest is not None or latest is not None:
            replaces_prior = index > 0 and (
                _is_correction_turn(utterance)
                or _SESSION_RESTART_CUE.search(utterance) is not None
            )
            complementary = (
                (final_relation == "not_before" and relation == "not_after")
                or (final_relation == "not_after" and relation == "not_before")
            )
            refines_interval = final_relation == "interval" and relation in {
                "not_before", "not_after"
            }

            if not replaces_prior and complementary:
                if earliest is not None:
                    final_earliest = earliest
                if latest is not None:
                    final_latest = latest
                final_relation = "interval"
            elif not replaces_prior and refines_interval:
                if relation == "not_before":
                    final_earliest = earliest
                else:
                    final_latest = latest
            else:
                final_relation = relation
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

    # --- 2. Action detection (reduced across turns) ---
    primary = utterances[0]
    intended_action = _derive_intended_action(utterances)

    # --- 3. Multi-turn reduction (for normalized_values) ---
    normalized_values = _reduce_multi_turn(utterances, reference_date)

    # --- 3a. Move-target date/time override ---
    # For move actions, extract the target date/time (after "to") rather than
    # the source (after "from"), so that move normalization uses the final
    # target slot (Rule 9).
    _MOVE_TARGET_PATTERN = re.compile(
        r"\bto\s+(?P<target_date>"
        r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
        r"tomorrow|today|the\s+\d+(?:st|nd|rd|th)?)\b",
        re.I,
    )
    if intended_action == "move":
        all_text = " ".join(utterances)
        target_m = _MOVE_TARGET_PATTERN.search(all_text)
        if target_m:
            raw_date = target_m.group("target_date")
            ref_parts = reference_date.split("-")
            ref = date(int(ref_parts[0]), int(ref_parts[1]), int(ref_parts[2]))
            target_date_str = _extract_date(raw_date, ref)
            if target_date_str:
                normalized_values["appointment_date"] = target_date_str
            # Extract target time after the target date mention
            after_target = all_text[target_m.end():]
            target_time = re.search(
                r"\b(\d{1,2})(?:\s*(:?)\s*(\d{2}))?\s*(am|pm)\b",
                after_target, re.I,
            )
            if target_time:
                parsed = parse_time_fragment(target_time.group(0))
                if parsed:
                    normalized_values["earliest_time"] = parsed
                    normalized_values["latest_time"] = parsed

    # Derive final temporal relation, has_time_bounds from all turns
    temporal_relation, earliest, latest = _derive_final_temporal(
        utterances, normalized_values,
    )
    if intended_action == "move":
        primary_target = _MOVE_TARGET_PATTERN.search(primary)
        later_temporal = any(
            relation != "unspecified" or lower is not None or upper is not None
            for relation, lower, upper in (
                _extract_temporal(utterance) for utterance in utterances[1:]
            )
        )
        if primary_target is not None and not later_temporal:
            target_relation, target_earliest, target_latest = _extract_temporal(
                primary[primary_target.end():]
            )
            if (
                target_relation != "unspecified"
                or target_earliest is not None
                or target_latest is not None
            ):
                temporal_relation = target_relation
                earliest = target_earliest
                latest = target_latest
    if temporal_relation != "unspecified" or earliest is not None or latest is not None:
        if earliest is None:
            normalized_values.pop("earliest_time", None)
        else:
            normalized_values["earliest_time"] = earliest
        if latest is None:
            normalized_values.pop("latest_time", None)
        else:
            normalized_values["latest_time"] = latest
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
    duration_sem = entities.get("duration", "omitted")
    requires_clarification, clarification_choices = _determine_clarification(
        utterances,
        intended_action,
        has_time_bounds,
        has_date,
        has_duration,
        patient_sem,
        practitioner_sem,
        correction_index,
        duration_semantics=duration_sem,
        entities=entities,
        temporal_relation=temporal_relation,
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
