"""Small transition-table helpers for Bernie workflow state.

The goal is to keep world-state assumptions out of ad hoc route conditionals.
The LLM extracts intent; these tables resolve how that intent interacts with
the current diary/session context.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Optional


@dataclass(frozen=True)
class DateResolutionTransition:
    transition_id: str
    action: str
    date_from: Optional[str] = None
    source: Optional[str] = None
    basis: str = ""
    clarifying_question: Optional[str] = None
    warning_code: Optional[str] = None


def _parse_iso_date(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None


def _frame_date(frame: dict[str, Any], keys: tuple[str, ...]) -> Optional[str]:
    for key in keys:
        parsed = _parse_iso_date(frame.get(key))
        if parsed:
            return parsed
    return None


def resolve_booking_date_transition(
    *,
    date_from: Any,
    context_frames: list[dict[str, Any]],
) -> DateResolutionTransition:
    """Resolve an omitted booking date from an explicit transition table.

    Priority is deliberate:
    1. explicit date from the interpreter;
    2. selected proposal/provisional booking context;
    3. selected diary appointment context;
    4. visible diary page context;
    5. ask the receptionist.
    """

    if date_from not in (None, ""):
        return DateResolutionTransition(
            transition_id="date.explicit",
            action="preserve",
            date_from=str(date_from),
            source="instruction",
            basis="The instruction supplied a date.",
        )

    table: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
        (
            "date.from_selected_proposal",
            ("date_from", "appointment_date", "selected_date"),
            "selected_proposal",
            "I used the date from the selected proposed booking.",
        ),
        (
            "date.from_selected_diary_appointment",
            ("appointment_date", "date_from", "selected_date"),
            "selected_diary_appointment",
            "I used the date from the selected diary appointment.",
        ),
        (
            "date.from_visible_diary_page",
            ("visible_date", "diary_date", "date", "appointment_date"),
            "visible_diary_page",
            "I used the date from the diary page that is open.",
        ),
    )

    for transition_id, keys, frame_type, basis in table:
        for frame in context_frames:
            if not isinstance(frame, dict) or frame.get("type") != frame_type:
                continue
            resolved = _frame_date(frame, keys)
            if resolved:
                return DateResolutionTransition(
                    transition_id=transition_id,
                    action="assume",
                    date_from=resolved,
                    source=frame_type,
                    basis=basis,
                    warning_code="date_assumed_from_visible_diary"
                    if frame_type == "visible_diary_page"
                    else "date_assumed_from_selected_context",
                )

    return DateResolutionTransition(
        transition_id="date.ask_missing_context",
        action="ask",
        basis="No date was supplied and no diary/session date context was available.",
        clarifying_question="Which day would you like me to check?",
    )
