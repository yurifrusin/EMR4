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
_NAT_TIME_PAT = r"(?:1?[0-9]|2[0-3])(?:[.:][0-5]\d)?(?:\s*(?:am|pm))?"
_BETWEEN_TIME_RE = re.compile(
    r"\bbetween\s+(" + _NAT_TIME_PAT + r")\s+and\s+(" + _NAT_TIME_PAT + r")\b",
    re.IGNORECASE,
)
_AFTER_TIME_RE = re.compile(r"\bafter\s+(" + _NAT_TIME_PAT + r")\b", re.IGNORECASE)
_BEFORE_TIME_RE = re.compile(r"\bbefore\s+(" + _NAT_TIME_PAT + r")\b", re.IGNORECASE)
_TIME_FRAGMENT_RE = re.compile(
    r"^(1?[0-9]|2[0-3])(?:[.:]([0-5]\d))?(?:\s*(am|pm))?$",
    re.IGNORECASE,
)

SameDayWindowKind = Literal[
    "ok",
    "not_same_day",
    "window_fully_past",
    "clamp_earliest",
]


@dataclass(frozen=True)
class SameDayWindowDecision:
    """Pure same-day temporal decision shared by Bernie route adapters."""

    kind: SameDayWindowKind
    clamp_hhmm: str | None = None
    now_time: time | None = None


def parse_time_fragment(raw: str) -> str | None:
    """Convert a natural time fragment (e.g. '3', '3:45', '3 pm') to HH:MM.

    Business-hours assumption: bare hours 1-11 without am/pm are treated as pm.
    Returns None when the fragment cannot be parsed.
    """
    m = _TIME_FRAGMENT_RE.match(raw.strip())
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    meridiem = (m.group(3) or "").lower()
    if meridiem == "pm" and hour < 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0
    elif not meridiem and 1 <= hour <= 11:
        hour += 12
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"


def extract_natural_time_constraints(
    instruction: str,
) -> tuple[str | None, str | None]:
    """Extract earliest/latest times from receptionist phrases.

    Handles: 'after 3', 'after 3 pm', 'before 3:45', 'before 3.45',
    'between 2 pm and 3:45'. Returns (earliest_time, latest_time) as HH:MM
    strings or None when not found.
    """
    earliest: str | None = None
    latest: str | None = None

    between_m = _BETWEEN_TIME_RE.search(instruction)
    if between_m:
        earliest = parse_time_fragment(between_m.group(1))
        latest = parse_time_fragment(between_m.group(2))
        return earliest, latest

    after_m = _AFTER_TIME_RE.search(instruction)
    if after_m:
        earliest = parse_time_fragment(after_m.group(1))

    before_m = _BEFORE_TIME_RE.search(instruction)
    if before_m:
        latest = parse_time_fragment(before_m.group(1))

    return earliest, latest


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
    "DATE_RE",
    "WEEK_RELATIVE_RE",
    "WEEKDAY_RE",
    "evaluate_same_day_window",
    "parse_time_fragment",
    "extract_natural_time_constraints",
    "extract_natural_date_constraint",
    "resolve_week_relative_date",
    "resolve_weekday_date",
]
