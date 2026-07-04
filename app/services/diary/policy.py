"""Deterministic reception-skill policy for Bernie context frames.

The policy layer turns typed evidence into small predicates the router/UI can
trust. It does not generate user-facing copy and it never calls the LLM.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.services.diary.frames import BernieReceptionContextFrameSet
from app.services.diary.schedule_explanations import parse_schedule_explanation_reason


BernieAvailabilityClassification = Literal[
    "not_evaluated",
    "roster_unavailable",
    "search_ran_no_candidates",
    "search_ran_with_candidates",
    "blocked",
]


class BernieReceptionPolicyDecision(BaseModel):
    """Small deterministic facts derived from a typed context frame set."""

    availability: BernieAvailabilityClassification
    can_search_slots: bool
    must_ask_clarification: bool
    can_offer_candidates: bool
    can_prepare_proposal: bool
    must_block_confirmation: bool
    advisory_warnings_only: bool
    roster_unavailable: bool
    search_ran_no_candidates: bool
    reason_codes: list[str] = Field(default_factory=list)
    schedule_reason_codes: list[str] = Field(default_factory=list)


def evaluate_reception_context(
    frame_set: BernieReceptionContextFrameSet,
) -> BernieReceptionPolicyDecision:
    """Evaluate typed Bernie context frames without scenario-specific copy.

    The central guardrail: "no matching times" is true only when a slot-search
    frame proves a valid search ran and returned no candidates. Roster/schedule
    absence, stale evidence, model uncertainty, and advisory warnings remain
    distinct classifications.
    """
    reason_codes: list[str] = []
    schedule_reason_codes: list[str] = []

    def add_reason(reason_code: str | None) -> None:
        if reason_code and reason_code not in reason_codes:
            reason_codes.append(reason_code)
        schedule_reason = parse_schedule_explanation_reason(reason_code)
        if schedule_reason and schedule_reason.value not in schedule_reason_codes:
            schedule_reason_codes.append(schedule_reason.value)

    hard_block = False
    stale = False
    must_ask = False
    roster_unavailable = False
    searched_no_candidates = False
    searched_with_candidates = False
    advisory_count = 0

    for frame in frame_set.frames:
        add_reason(frame.reason_code)
        if frame.frame_type == "guardrail_outcome" and frame.status == "blocked":
            hard_block = True
        elif frame.frame_type == "stale_evidence" and frame.status == "stale":
            stale = True
        elif frame.frame_type == "model_uncertainty" and frame.status == "ask":
            must_ask = True
        elif frame.frame_type == "requested_appointment" and frame.status in {"partial", "missing"}:
            must_ask = True
        elif frame.frame_type == "roster_schedule" and frame.status == "unavailable":
            roster_unavailable = True
            # Guarantee a self-explaining schedule reason so roster_unavailable
            # always carries at least one schedule reason code.
            if not frame.reason_code:
                add_reason("no_roster_row")
        elif frame.frame_type == "slot_search" and frame.status == "searched_no_candidates":
            searched_no_candidates = True
        elif frame.frame_type == "slot_search" and frame.status == "searched_with_candidates":
            searched_with_candidates = True
        elif frame.frame_type == "advisory_warning":
            advisory_count += 1

    if hard_block:
        availability: BernieAvailabilityClassification = "blocked"
    elif roster_unavailable:
        availability = "roster_unavailable"
    elif searched_no_candidates:
        availability = "search_ran_no_candidates"
    elif searched_with_candidates:
        availability = "search_ran_with_candidates"
    else:
        availability = "not_evaluated"

    terminal_non_search = hard_block or stale or must_ask or roster_unavailable
    can_search_slots = not terminal_non_search
    can_offer_candidates = searched_with_candidates and not (hard_block or stale)
    can_prepare_proposal = can_offer_candidates
    must_block_confirmation = hard_block or stale
    advisory_warnings_only = (
        advisory_count > 0
        and not hard_block
        and not stale
        and not must_ask
        and not roster_unavailable
        and not searched_no_candidates
        and not searched_with_candidates
    )

    return BernieReceptionPolicyDecision(
        availability=availability,
        can_search_slots=can_search_slots,
        must_ask_clarification=must_ask,
        can_offer_candidates=can_offer_candidates,
        can_prepare_proposal=can_prepare_proposal,
        must_block_confirmation=must_block_confirmation,
        advisory_warnings_only=advisory_warnings_only,
        roster_unavailable=roster_unavailable,
        search_ran_no_candidates=searched_no_candidates,
        reason_codes=reason_codes,
        schedule_reason_codes=schedule_reason_codes,
    )


__all__ = [
    "BernieAvailabilityClassification",
    "BernieReceptionPolicyDecision",
    "evaluate_reception_context",
]
