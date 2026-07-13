"""Pure temporal policy for Bernie booking instructions.

This module is the bounded-domain home for Bernie's date/time policy. It is
deliberately pure: no DB, no network, no wall-clock reads. Callers pass the
clinic-local clock value in when same-day policy needs "now".
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Literal


DATE_RE = re.compile(r"\b(?:today|tomorrow|\d{4}-\d{2}-\d{2})\b", re.IGNORECASE)
WEEK_RELATIVE_RE = re.compile(
    r"\b(?:in\s+(?:a|one|1)\s+week(?:['`\\]s)?(?:\s+time)?|next\s+week)\b",
    re.IGNORECASE,
)
WEEKDAY_RE = re.compile(
    r"\b(?:(?P<modifier>next|on)\s+)?(?P<weekday>monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    re.IGNORECASE,
)
WEEKDAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# Natural language time phrase patterns (no DB, no network).
# Business-hours assumption: bare hour 1-11 without am/pm -> pm.
_NAT_TIME_PAT = r"(?:[01]?[0-9]|2[0-3])(?:[.:][0-5]\d)?(?:\s*(?:am|pm))?"
_BETWEEN_TIME_RE = re.compile(
    r"\bbetween\s+(" + _NAT_TIME_PAT + r")\s+and\s+(" + _NAT_TIME_PAT + r")\b",
    re.IGNORECASE,
)
_AT_TIME_RE = re.compile(
    r"\bat\s+(" + _NAT_TIME_PAT + r")\b",
    re.IGNORECASE,
)
_ABOUT_TIME_RE = re.compile(
    r"\b(?:around|about)\s+(" + _NAT_TIME_PAT + r")\b",
    re.IGNORECASE,
)
_BARE_EXPLICIT_TIME_RE = re.compile(
    r"\b((?:[01]?[0-9]|2[0-3])(?:[.:][0-5]\d)?\s*(?:am|pm)|"
    r"(?:[01]?[0-9]|2[0-3])[.:][0-5]\d)\b",
    re.IGNORECASE,
)
_AFTER_TIME_RE = re.compile(r"\bafter\s+(" + _NAT_TIME_PAT + r")\b", re.IGNORECASE)
_BEFORE_TIME_RE = re.compile(r"\bbefore\s+(" + _NAT_TIME_PAT + r")\b", re.IGNORECASE)
_TIME_FRAGMENT_RE = re.compile(
    r"^([01]?[0-9]|2[0-3])(?:[.:]([0-5]\d))?(?:\s*(am|pm))?$",
    re.IGNORECASE,
)

SameDayWindowKind = Literal[
    "ok",
    "not_same_day",
    "window_fully_past",
    "clamp_earliest",
]

RawMutationTemporalKind = Literal[
    "ok",
    "past_date",
    "window_fully_past",
]

TemporalRelationKind = Literal[
    "exact",
    "not_before",
    "not_after",
    "interval",
    "approximate",
    "unspecified",
]


@dataclass(frozen=True)
class TemporalExtraction:
    """Result of extracting temporal constraints from a natural-language instruction."""

    earliest: str | None = None
    latest: str | None = None
    temporal_relation: TemporalRelationKind = "unspecified"


def _hhmm_to_minutes(hhmm: str) -> int:
    """Convert HH:MM string to minutes since midnight."""
    parts = hhmm.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def _minutes_to_hhmm(mins: int) -> str:
    """Convert minutes since midnight to HH:MM string."""
    return f"{mins // 60:02d}:{mins % 60:02d}"


def evaluate_raw_mutation_temporal_guard(
    appointment_date: date,
    start_time_local: time,
    duration_minutes: int,
    clinic_now: datetime,
) -> RawMutationTemporalKind:
    """Determine whether a raw create/update slot is in the past.

    Returns 'ok' when the slot is future or same-day and still open.
    Returns 'past_date' when appointment_date is before today (clinic-local).
    Returns 'window_fully_past' when it is same-day but start+duration has
    fully elapsed (i.e. the appointment window end <= now).

    Uses clinic_now.tzinfo for tz-aware arithmetic so naive/aware comparisons
    are avoided.  The caller should pass _clinic_local_now(practice_tz).
    """
    clinic_date = clinic_now.date()
    if appointment_date < clinic_date:
        return "past_date"
    if appointment_date == clinic_date:
        tz = clinic_now.tzinfo
        start_dt = datetime.combine(appointment_date, start_time_local, tzinfo=tz)
        window_end = start_dt + timedelta(minutes=duration_minutes)
        if window_end <= clinic_now:
            return "window_fully_past"
    return "ok"


@dataclass(frozen=True)
class SameDayWindowDecision:
    """Pure same-day temporal decision shared by Bernie route adapters."""

    kind: SameDayWindowKind
    clamp_hhmm: str | None = None
    now_time: time | None = None


def parse_time_fragment(raw: str) -> str | None:
    """Convert a natural time fragment (e.g. '3', '3:45', '3 pm', '3.00pm') to HH:MM.

    Business-hours assumption: bare hours 1-11 without am/pm are treated as pm.
    Returns None when the fragment cannot be parsed.
    """
    m = _TIME_FRAGMENT_RE.match(raw.strip())
    if not m:
        return None
    hour_text = m.group(1)
    hour = int(hour_text)
    minute = int(m.group(2) or 0)
    meridiem = (m.group(3) or "").lower()
    if meridiem == "pm" and hour < 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0
    elif (
        not meridiem
        and 1 <= hour <= 11
        and not (len(hour_text) == 2 and (":" in raw or "." in raw))
    ):
        hour += 12
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"


def extract_natural_time_constraints(
    instruction: str,
) -> TemporalExtraction:
    """Extract earliest/latest times from receptionist phrases.

    Handles: 'after 3', 'after 3 pm', 'before 3:45', 'before 3.45',
    'between 2 pm and 3:45', 'at 3pm', 'at 15:00', 'around 3pm', 'about 3pm'.

    Returns TemporalExtraction with earliest, latest, and temporal_relation.

    Priority order: BETWEEN > AT > ABOUT > AFTER/BEFORE > positional HH:MM fallback.
    """
    earliest: str | None = None
    latest: str | None = None
    temporal_relation: TemporalRelationKind = "unspecified"

    # Priority 1: BETWEEN → interval
    between_m = _BETWEEN_TIME_RE.search(instruction)
    if between_m:
        earliest = parse_time_fragment(between_m.group(1))
        latest = parse_time_fragment(between_m.group(2))
        temporal_relation = "interval"
        return TemporalExtraction(
            earliest=earliest,
            latest=latest,
            temporal_relation=temporal_relation,
        )

    # Priority 2: AT → exact
    at_m = _AT_TIME_RE.search(instruction)
    if at_m:
        parsed = parse_time_fragment(at_m.group(1))
        if parsed:
            return TemporalExtraction(
                earliest=parsed,
                latest=parsed,
                temporal_relation="exact",
            )

    # Priority 3: ABOUT/AROUND → approximate (±30 min)
    about_m = _ABOUT_TIME_RE.search(instruction)
    if about_m:
        parsed = parse_time_fragment(about_m.group(1))
        if parsed:
            mins = _hhmm_to_minutes(parsed)
            earliest_mins = max(0, mins - 30)
            latest_mins = min((24 * 60) - 1, mins + 30)
            return TemporalExtraction(
                earliest=_minutes_to_hhmm(earliest_mins),
                latest=_minutes_to_hhmm(latest_mins),
                temporal_relation="approximate",
            )

    # Priority 4: AFTER → not_before
    after_m = _AFTER_TIME_RE.search(instruction)
    if after_m:
        earliest = parse_time_fragment(after_m.group(1))

    # Priority 5: BEFORE → not_after
    before_m = _BEFORE_TIME_RE.search(instruction)
    if before_m:
        latest = parse_time_fragment(before_m.group(1))

    if after_m or before_m:
        temporal_relation = infer_temporal_relation(earliest, latest)

    if earliest is not None or latest is not None:
        return TemporalExtraction(
            earliest=earliest,
            latest=latest,
            temporal_relation=temporal_relation,
        )

    # Priority 6: Positional HH:MM fallback → unspecified
    times = [match.group(1) for match in _BARE_EXPLICIT_TIME_RE.finditer(instruction)]
    parsed_times = [
        parsed
        for raw in times
        if (parsed := parse_time_fragment(raw)) is not None
    ]
    if parsed_times:
        return TemporalExtraction(
            earliest=parsed_times[0],
            latest=parsed_times[-1] if len(parsed_times) > 1 else None,
            temporal_relation="unspecified",
        )

    return TemporalExtraction()


def infer_temporal_relation(
    earliest: str | None,
    latest: str | None,
) -> TemporalRelationKind:
    """Infer temporal relation from raw time bounds for legacy callers.

    earliest==latest → exact
    only earliest → not_before
    only latest → not_after
    both different → interval
    none → unspecified
    """
    if earliest is not None and latest is not None:
        if earliest == latest:
            return "exact"
        return "interval"
    if earliest is not None:
        return "not_before"
    if latest is not None:
        return "not_after"
    return "unspecified"


def adjust_search_window_for_relation(
    earliest_time: str | None,
    latest_time: str | None,
    temporal_relation: str | None,
) -> tuple[str | None, str | None]:
    """Widen or preserve the slot-search window based on temporal relation.

    When temporal_relation == 'exact' and latest_time matches earliest_time,
    widen latest to earliest + 5 minutes so the half-open search captures
    the exact-time slot.

    When temporal_relation == 'approximate', the ±30 min window is already
    set in extraction; pass through unchanged.

    For all other relations, use bounds as-is (existing behaviour).

    Returns (adjusted_earliest, adjusted_latest).
    """
    if (
        temporal_relation == "exact"
        and earliest_time is not None
        and (latest_time is None or latest_time == earliest_time)
    ):
        earliest_mins = _hhmm_to_minutes(earliest_time)
        latest_mins = earliest_mins + 5
        if latest_mins >= 24 * 60:
            return earliest_time, None
        return earliest_time, _minutes_to_hhmm(latest_mins)
    return earliest_time, latest_time


def should_classify_exact_booking(temporal_relation: str | None) -> bool:
    """Whether the temporal relation allows exact existing-booking classification.

    Only 'exact' can produce existing_booking_found.
    'approximate', 'unspecified', 'not_before', 'not_after', and 'interval'
    must NOT classify as exact even if a booking exists in the window.
    """
    return temporal_relation == "exact"


def resolve_week_relative_date(
    instruction: str,
    reference_date: date | None,
) -> str | None:
    """Resolve 'in a week's time' / 'next week' relative to reference_date."""
    if reference_date is None:
        return None
    if WEEK_RELATIVE_RE.search(instruction):
        return (reference_date + timedelta(days=7)).isoformat()
    return None


def resolve_weekday_date(
    instruction: str,
    reference_date: date | None,
) -> str | None:
    """Resolve simple receptionist weekday phrases relative to reference_date.

    "next Monday" always means the next future Monday. "on Monday" or a bare
    weekday means the upcoming occurrence, including today if the reference date
    is already that weekday.
    """
    if reference_date is None:
        return None
    match = WEEKDAY_RE.search(instruction)
    if not match:
        return None
    target_weekday = WEEKDAY_INDEX[match.group("weekday").lower()]
    days_ahead = (target_weekday - reference_date.weekday()) % 7
    modifier = (match.group("modifier") or "").lower()
    if modifier == "next" and days_ahead == 0:
        days_ahead = 7
    return (reference_date + timedelta(days=days_ahead)).isoformat()


def extract_natural_date_constraint(
    instruction: str,
    reference_date: date | None,
) -> str | None:
    """Extract today/tomorrow/ISO/week-relative date text from an instruction."""
    date_match = DATE_RE.search(instruction)
    if date_match:
        return date_match.group(0).lower()
    week_relative = resolve_week_relative_date(instruction, reference_date)
    if week_relative:
        return week_relative
    return resolve_weekday_date(instruction, reference_date)


def evaluate_same_day_window(
    resolved_date: date | None,
    earliest_time: time | None,
    latest_time: time | None,
    clinic_now: datetime,
) -> SameDayWindowDecision:
    """Evaluate same-day window freshness against a supplied clinic-local now.

    The returned fact is intentionally route-neutral. Existing route adapters
    decide whether to ask, block, clamp, or continue so public response copy and
    JSON stay stable while the temporal predicate is shared.
    """
    now_time = clinic_now.time().replace(second=0, microsecond=0)
    if resolved_date != clinic_now.date():
        return SameDayWindowDecision(kind="not_same_day", now_time=now_time)
    if latest_time is not None and latest_time <= now_time:
        return SameDayWindowDecision(kind="window_fully_past", now_time=now_time)
    if earliest_time is not None and earliest_time < now_time:
        return SameDayWindowDecision(
            kind="clamp_earliest",
            clamp_hhmm=now_time.strftime("%H:%M"),
            now_time=now_time,
        )
    return SameDayWindowDecision(kind="ok", now_time=now_time)


__all__ = [
    "SameDayWindowDecision",
    "SameDayWindowKind",
    "RawMutationTemporalKind",
    "TemporalRelationKind",
    "TemporalExtraction",
    "DATE_RE",
    "WEEK_RELATIVE_RE",
    "WEEKDAY_RE",
    "evaluate_raw_mutation_temporal_guard",
    "evaluate_same_day_window",
    "parse_time_fragment",
    "extract_natural_time_constraints",
    "extract_natural_date_constraint",
    "infer_temporal_relation",
    "adjust_search_window_for_relation",
    "should_classify_exact_booking",
    "resolve_week_relative_date",
    "resolve_weekday_date",
]
