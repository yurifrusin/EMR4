"""Deterministic confirm-affordance gate for the diary/reception domain.

Fuses reception policy + staleness evidence + staged-proposal presence into
a single backend-owned decision on whether a booking proposal may expose
confirm-grade UI. Fail-closed: any missing or adverse signal blocks.

Designed to be a pure contract: no DB, no network, no wall-clock, no LLM.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.services.diary.policy import BernieReceptionPolicyDecision
from app.services.bernie_turn_evidence import StalenessResult, StalenessVerdict


class ConfirmAffordanceGate(str, Enum):
    """Reason code for the confirm-affordance gate decision."""

    allowed = "allowed"
    blocked_stale = "blocked_stale"
    blocked_advisory_only = "blocked_advisory_only"
    blocked_model_uncertain = "blocked_model_uncertain"
    blocked_no_candidates = "blocked_no_candidates"
    blocked_schedule_or_roster = "blocked_schedule_or_roster"
    blocked_guardrail = "blocked_guardrail"
    blocked_no_proposal = "blocked_no_proposal"


class ConfirmAffordanceDecision(BaseModel):
    """Backend-owned single decision on confirm-grade booking UI affordance.

    ``confirm_grade_allowed`` is the only field callers should act on for
    showing/hiding confirm UI. The remaining fields are diagnostic.
    """

    confirm_grade_allowed: bool
    gate: ConfirmAffordanceGate
    blocking_reason_codes: list[str]
    schedule_reason_codes: list[str]


def evaluate_confirm_affordance(
    policy: BernieReceptionPolicyDecision,
    *,
    staleness: Optional[StalenessResult] = None,
    has_staged_proposal: bool,
) -> ConfirmAffordanceDecision:
    """Evaluate whether confirm-grade booking UI may be shown.

    Fail-closed semantics:
    - confirm_grade_allowed is True ONLY when every guard below passes.
    - Any absent or adverse signal returns False with a distinct gate.

    Guard precedence (first match wins; preserves semantic distinctness):
    1. ``must_block_confirmation`` or ``availability == "blocked"``
       → blocked_guardrail
    2. Staleness is given and verdict is not fresh
       → blocked_stale (stale or mismatched_reference_date both map here)
    3. ``advisory_warnings_only``
       → blocked_advisory_only
    4. ``must_ask_clarification``
       → blocked_model_uncertain
    5. ``search_ran_no_candidates`` or ``roster_unavailable``
       → blocked_no_candidates / blocked_schedule_or_roster (roster checked first)
    6. ``has_staged_proposal`` is False
       → blocked_no_proposal
    7. All guards pass → allowed
    """
    blocking_reason_codes: list[str] = list(policy.reason_codes)
    schedule_reason_codes: list[str] = list(policy.schedule_reason_codes)

    if policy.must_block_confirmation or policy.availability == "blocked":
        return ConfirmAffordanceDecision(
            confirm_grade_allowed=False,
            gate=ConfirmAffordanceGate.blocked_guardrail,
            blocking_reason_codes=blocking_reason_codes,
            schedule_reason_codes=schedule_reason_codes,
        )

    if staleness is not None and staleness.verdict != StalenessVerdict.fresh:
        return ConfirmAffordanceDecision(
            confirm_grade_allowed=False,
            gate=ConfirmAffordanceGate.blocked_stale,
            blocking_reason_codes=blocking_reason_codes,
            schedule_reason_codes=schedule_reason_codes,
        )

    if policy.advisory_warnings_only:
        return ConfirmAffordanceDecision(
            confirm_grade_allowed=False,
            gate=ConfirmAffordanceGate.blocked_advisory_only,
            blocking_reason_codes=blocking_reason_codes,
            schedule_reason_codes=schedule_reason_codes,
        )

    if policy.must_ask_clarification:
        return ConfirmAffordanceDecision(
            confirm_grade_allowed=False,
            gate=ConfirmAffordanceGate.blocked_model_uncertain,
            blocking_reason_codes=blocking_reason_codes,
            schedule_reason_codes=schedule_reason_codes,
        )

    if policy.roster_unavailable:
        return ConfirmAffordanceDecision(
            confirm_grade_allowed=False,
            gate=ConfirmAffordanceGate.blocked_schedule_or_roster,
            blocking_reason_codes=blocking_reason_codes,
            schedule_reason_codes=schedule_reason_codes,
        )

    if policy.search_ran_no_candidates:
        return ConfirmAffordanceDecision(
            confirm_grade_allowed=False,
            gate=ConfirmAffordanceGate.blocked_no_candidates,
            blocking_reason_codes=blocking_reason_codes,
            schedule_reason_codes=schedule_reason_codes,
        )

    if not has_staged_proposal:
        return ConfirmAffordanceDecision(
            confirm_grade_allowed=False,
            gate=ConfirmAffordanceGate.blocked_no_proposal,
            blocking_reason_codes=blocking_reason_codes,
            schedule_reason_codes=schedule_reason_codes,
        )

    return ConfirmAffordanceDecision(
        confirm_grade_allowed=True,
        gate=ConfirmAffordanceGate.allowed,
        blocking_reason_codes=[],
        schedule_reason_codes=schedule_reason_codes,
    )


__all__ = [
    "ConfirmAffordanceDecision",
    "ConfirmAffordanceGate",
    "evaluate_confirm_affordance",
]
