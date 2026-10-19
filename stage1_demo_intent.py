"""Pure, deliberately narrow date and time suggestions for the local demo.

Words are advisory input. This module has no authority, state, I/O, or effects.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
import re


class IntentRejected(ValueError):
    pass


WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
DATE = re.compile(r"(?<!\w)20\d{2}-\d{2}-\d{2}(?!\w)")
DAY = re.compile(r"\b(?:(next)\s+)?(" + "|".join(WEEKDAYS) + r")\b", re.I)
TIME = re.compile(r"(?<!\w)(?:(?:[01]?\d|2[0-3]):[0-5]\d\s*(?:am|pm)?|(?:1[0-2]|[1-9])\s*(?:am|pm))(?!\w)", re.I)
WINDOW = re.compile(r"\b(?:between|from)\s+(.+?)\s+(?:and|to)\s+(.+?)(?:[.,;]|$)", re.I)
AFTER = re.compile(r"\b(?:after|at or after)\s+(.+?)(?:[.,;]|$)", re.I)
UNSAFE_WORDS = re.compile(r"\b(?:not|except|or(?!\s+after)|maybe|around|about|before|tomorrow|today|yesterday|noon|midnight|morning|afternoon|evening)\b", re.I)


def _clock(value: str, zone: str) -> date:
    if zone != "Australia/Brisbane" or type(value) is not str:
        raise IntentRejected("CLOCK_UNAVAILABLE")
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M").date()
    except ValueError:
        raise IntentRejected("CLOCK_UNAVAILABLE") from None


def _minute(value: str) -> str | None:
    match = re.fullmatch(r"\s*(\d{1,2})(?::([0-5]\d))?\s*(am|pm)?\s*", value, re.I)
    if not match:
        return None
    hour, minute, suffix = int(match[1]), int(match[2] or "0"), match[3]
    if suffix:
        if hour not in range(1, 13):
            return None
        hour = hour % 12 + (12 if suffix.lower() == "pm" else 0)
    elif match[2] is None or hour > 23:
        return None
    return f"{hour:02d}:{minute:02d}"


def interpret_words(kind: str, words: str, *, persona: str, demo_clock: str,
                    timezone: str) -> dict[str, object]:
    if (type(kind) is not str or kind not in {"request", "move"} or persona != ("patient" if kind == "request" else "staff")
            or type(words) is not str or not 1 <= len(words) <= 500
            or any(ord(char) < 32 or ord(char) == 127 for char in words)):
        raise IntentRejected("INTENT_SCOPE_INVALID")
    today = _clock(demo_clock, timezone)
    required = ("date", "earliest_local", "latest_local") if kind == "request" else (
        "target_date", "target_start_local")
    fields: dict[str, str] = {}
    ambiguous = bool(UNSAFE_WORDS.search(words))
    dates: set[date] = set()
    for match in DATE.finditer(words):
        try:
            dates.add(date.fromisoformat(match[0]))
        except ValueError:
            ambiguous = True
    for match in DAY.finditer(words):
        weekday = WEEKDAYS.index(match[2].lower())
        ahead = (weekday - today.weekday()) % 7
        if match[1] and ahead == 0:
            ahead = 7
        dates.add(today + timedelta(days=ahead))
    if len(dates) > 1:
        ambiguous = True
    elif dates:
        fields[required[0]] = next(iter(dates)).isoformat()
    times = [_minute(match[0]) for match in TIME.finditer(words)]
    if None in times or len(set(times)) != len(times):
        ambiguous = True
    if kind == "move":
        if len(times) == 1 and not WINDOW.search(words) and not AFTER.search(words):
            fields["target_start_local"] = times[0]
        elif times:
            ambiguous = True
    else:
        window = WINDOW.search(words)
        after = AFTER.search(words)
        if window and len(times) == 2 and not after:
            endpoints = [TIME.search(window[1]), TIME.search(window[2])]
            parsed = [_minute(item[0]) if item else None for item in endpoints]
            if None not in parsed and parsed[0] < parsed[1] and parsed == times:
                fields["earliest_local"], fields["latest_local"] = parsed
            else:
                ambiguous = True
        elif after and len(times) == 1 and not window:
            match = TIME.search(after[1])
            if match and _minute(match[0]) == times[0]:
                fields["earliest_local"] = times[0]
            else:
                ambiguous = True
        elif times:
            ambiguous = True
    consumed = words
    for pattern in (DATE, DAY, TIME):
        consumed = pattern.sub(" ", consumed)
    consumed = re.sub(r"\b(?:please|book|booking|appointment|move|reschedule|schedule|request|my|the|this|follow-up|to|on|at|for|between|from|and|after|or|i|want|need|a|an|time|is|would|like)\b", " ", consumed, flags=re.I)
    if re.search(r"[A-Za-z0-9]", consumed):
        ambiguous = True
    if ambiguous:
        fields.clear()
    missing = [key for key in required if key not in fields]
    status = "PROPOSED" if not missing and not ambiguous else "CLARIFICATION"
    return {"schema": "emr4.stage1_word_interpretation.v1",
            "status": status, "kind": kind, "method": "DETERMINISTIC_LOCAL",
            "fields": fields, "missing": missing,
            "message": "READY_FOR_HUMAN_REVIEW" if status == "PROPOSED" else (
                "AMBIGUOUS_OR_UNSUPPORTED_WORDS" if ambiguous else "MORE_DATE_OR_TIME_NEEDED")}
