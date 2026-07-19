"""Typed schedule-explanation reasons and copy catalog for diary consumers.

This module is deliberately pure contract code. It gives Bernie, the diary UI,
and future bounded agents one stable reason-code vocabulary for "no slot"
states without sniffing summary text or route-specific messages.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.services.diary.temporal import SameDayWindowKind

class DiaryScheduleExplanationReason(str, Enum):
    """Schedule/no-slot reasons that must remain semantically distinct."""

    no_roster_row = "no_roster_row"
    practitioner_unavailable = "practitioner_unavailable"
    outside_request_window = "outside_request_window"
    breaks_only_window = "breaks_only_window"
    fully_booked = "fully_booked"
    same_day_window_elapsed = "same_day_window_elapsed"
    searched_no_candidates = "searched_no_candidates"


class DiaryScheduleExplanationEvidence(BaseModel):
    """Pure facts used to classify why a requested schedule has no usable slot."""

    model_config = ConfigDict(extra="forbid")

    reference_date: str
    has_roster_row: bool = True
    practitioner_working: bool = True
    within_request_window: bool = True
    window_is_breaks_only: bool = False
    any_free_capacity: bool = True
    same_day_window_kind: SameDayWindowKind = "ok"
    search_ran: bool = False
    candidate_count: int | None = Field(default=None, ge=0)
    basis: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class DiaryScheduleExplanation(BaseModel):
    """Typed, copy-free explanation for a schedule/no-slot result."""

    model_config = ConfigDict(extra="forbid")

    reason_code: DiaryScheduleExplanationReason
    basis: str
    reference_date: str
    payload: dict[str, Any] = Field(default_factory=dict)


class DiaryScheduleCopy(BaseModel):
    """Default neutral copy keyed by a schedule explanation reason code."""

    model_config = ConfigDict(frozen=True)

    reason_code: DiaryScheduleExplanationReason
    title: str
    staff_prompt: str


DIARY_SCHEDULE_COPY_CATALOG: dict[DiaryScheduleExplanationReason, DiaryScheduleCopy] = {
    DiaryScheduleExplanationReason.no_roster_row: DiaryScheduleCopy(
        reason_code=DiaryScheduleExplanationReason.no_roster_row,
        title="No roster found",
        staff_prompt="Check the practitioner's roster or choose another day.",
    ),
    DiaryScheduleExplanationReason.practitioner_unavailable: DiaryScheduleCopy(
        reason_code=DiaryScheduleExplanationReason.practitioner_unavailable,
        title="Practitioner is away",
        staff_prompt="Choose another practitioner or another date.",
    ),
    DiaryScheduleExplanationReason.outside_request_window: DiaryScheduleCopy(
        reason_code=DiaryScheduleExplanationReason.outside_request_window,
        title="Requested time is outside rostered hours",
        staff_prompt="Choose a time within the practitioner's rostered hours.",
    ),
    DiaryScheduleExplanationReason.breaks_only_window: DiaryScheduleCopy(
        reason_code=DiaryScheduleExplanationReason.breaks_only_window,
        title="Break time",
        staff_prompt="Choose a time outside the break window.",
    ),
    DiaryScheduleExplanationReason.fully_booked: DiaryScheduleCopy(
        reason_code=DiaryScheduleExplanationReason.fully_booked,
        title="Fully booked",
        staff_prompt="Choose another time, practitioner, or date.",
    ),
    DiaryScheduleExplanationReason.same_day_window_elapsed: DiaryScheduleCopy(
        reason_code=DiaryScheduleExplanationReason.same_day_window_elapsed,
        title="No times left today",
        staff_prompt="Choose another date.",
    ),
    DiaryScheduleExplanationReason.searched_no_candidates: DiaryScheduleCopy(
        reason_code=DiaryScheduleExplanationReason.searched_no_candidates,
        title="No matching slots found",
        staff_prompt="Try a wider time window, another practitioner, or another date.",
    ),
}


DIARY_SCHEDULE_REASON_ALIASES: dict[str, DiaryScheduleExplanationReason] = {
    "no_practitioner_schedule": DiaryScheduleExplanationReason.no_roster_row,
    "slot_search_skipped_no_schedule": DiaryScheduleExplanationReason.no_roster_row,
    "no_roster": DiaryScheduleExplanationReason.no_roster_row,
    "day_off": DiaryScheduleExplanationReason.practitioner_unavailable,
    "outside_hours": DiaryScheduleExplanationReason.outside_request_window,
    "break_window": DiaryScheduleExplanationReason.breaks_only_window,
    "clinic_day_exhausted": DiaryScheduleExplanationReason.same_day_window_elapsed,
    "elapsed_same_day": DiaryScheduleExplanationReason.same_day_window_elapsed,
    "no_slot_candidates": DiaryScheduleExplanationReason.searched_no_candidates,
}


def parse_schedule_explanation_reason(
    reason_code: str | None,
) -> DiaryScheduleExplanationReason | None:
    """Return the typed schedule reason for a raw code, if it is in the catalog."""
    if reason_code is None:
        return None
    alias = DIARY_SCHEDULE_REASON_ALIASES.get(reason_code)
    if alias is not None:
        return alias
    try:
        return DiaryScheduleExplanationReason(reason_code)
    except ValueError:
        return None


def explain_schedule(evidence: DiaryScheduleExplanationEvidence) -> DiaryScheduleExplanation | None:
    """Classify a no-slot/schedule issue from deterministic evidence.

    Structural schedule facts take precedence over slot-search emptiness. In
    particular, ``searched_no_candidates`` is returned only when a valid search
    actually ran and returned zero candidates.
    """
    reason: DiaryScheduleExplanationReason | None = None

    if not evidence.has_roster_row:
        reason = DiaryScheduleExplanationReason.no_roster_row
    elif not evidence.practitioner_working:
        reason = DiaryScheduleExplanationReason.practitioner_unavailable
    elif evidence.same_day_window_kind == "window_fully_past":
        reason = DiaryScheduleExplanationReason.same_day_window_elapsed
    elif not evidence.within_request_window:
        reason = DiaryScheduleExplanationReason.outside_request_window
    elif evidence.window_is_breaks_only:
        reason = DiaryScheduleExplanationReason.breaks_only_window
    elif not evidence.any_free_capacity:
        reason = DiaryScheduleExplanationReason.fully_booked
    elif evidence.search_ran and evidence.candidate_count == 0:
        reason = DiaryScheduleExplanationReason.searched_no_candidates

    if reason is None:
        return None

    return DiaryScheduleExplanation(
        reason_code=reason,
        basis=evidence.basis or get_schedule_copy(reason).staff_prompt,
        reference_date=evidence.reference_date,
        payload=evidence.payload,
    )


def get_schedule_copy(reason_code: DiaryScheduleExplanationReason) -> DiaryScheduleCopy:
    """Return default copy for a typed schedule explanation reason."""
    return DIARY_SCHEDULE_COPY_CATALOG[reason_code]


__all__ = [
    "DIARY_SCHEDULE_COPY_CATALOG",
    "DIARY_SCHEDULE_REASON_ALIASES",
    "DiaryScheduleCopy",
    "DiaryScheduleExplanation",
    "DiaryScheduleExplanationEvidence",
    "DiaryScheduleExplanationReason",
    "explain_schedule",
    "get_schedule_copy",
    "parse_schedule_explanation_reason",
]
