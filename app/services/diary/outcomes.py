"""Typed booking-outcome classification for the Bernie reception domain.

The outcome is a READ-ONLY label derived from the typed reception policy
and route-context signals. It makes "no matching times", "roster unavailable",
"clarification/review blocks", and "advisory warnings" four mutually-exclusive
first-class outcome kinds the state machine determines — not scripted UI guesses.

Design constraints:
- Pure function (no DB, no clock, no LLM): classify_booking_outcome() takes
  evidence already computed by the route and returns a deterministic label.
- Never a confirm grant: can_confirm=True is a REPORT ONLY field. Confirm
  authority still requires the existing gate, signed evidence, and session
  binding.
- Consistent with the N9 session statechart: OUTCOME_SESSION_STATE maps each
  kind to the valid session states a route may advance to.
  assert_outcome_matches_state() fails loudly when an outcome/state pair would
  silently disagree.
- No-write boundary preserved: the classifier never reads DB rows, never calls
  external services, and never creates slot truth, roster truth, or confirmation
  authority. Evidence must be passed in.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.services.diary.policy import BernieReceptionPolicyDecision
from app.services.diary.schedule_explanations import (
    get_schedule_copy,
    parse_schedule_explanation_reason,
)

# Session-state string literals used in outcome maps. Kept as plain strings to
# avoid a circular import with app.services.bernie (bernie/__init__ re-exports
# outcomes, diary/outcomes must not import through that package init).
# These values must stay in sync with BernieSessionState in bernie/session.py.
_SS_NO_SLOT = "no_slot"
_SS_HANDED_OFF = "handed_off"
_SS_CLARIFICATION = "clarification"
_SS_CLINIC_DAY_EXHAUSTED = "clinic_day_exhausted"
_SS_PROPOSAL_PREVIEW = "proposal_preview"
_SS_CANDIDATE_SELECTION = "candidate_selection"
_SS_CONTEXT_ENRICHMENT = "context_enrichment"


class BernieBookingOutcomeKind(str, Enum):
    """First-class discriminated outcome kinds for a Bernie booking turn.

    Each kind belongs to exactly one family and maps to a set of valid
    N9 session states (OUTCOME_SESSION_STATE). The precedence order used
    by classify_booking_outcome() ensures mutual exclusivity.
    """

    # "proceed" family — booking can continue
    interpreted_ready = "interpreted_ready"
    """Interpretation succeeded with no adverse signals; next step is context enrichment."""

    candidate_selection_required = "candidate_selection_required"
    """Slot candidates were found; staff must select one before a proposal can be staged."""

    confirmation_ready = "confirmation_ready"
    """A create proposal is staged; explicit staff confirmation is required to proceed."""

    # "clarify" family — more information needed
    clarification_required = "clarification_required"
    """Missing/partial request, model uncertainty, or stale evidence requires clarification."""

    # "advisory" family — warnings present, otherwise can proceed
    advisory_warnings_present = "advisory_warnings_present"
    """Only advisory warnings are present; no hard block or search result yet."""

    # "no_availability" family — search ran, no slots
    no_matching_times = "no_matching_times"
    """A slot search ran against an available roster but found no matching slots."""

    # "roster_gap" family — roster/schedule not available
    roster_unavailable = "roster_unavailable"
    """No practitioner schedule/roster is available to search against."""

    # "blocked" family — hard guardrail
    guardrail_blocked = "guardrail_blocked"
    """A guardrail outcome frame hard-blocked the request."""

    # "terminal" family — session-terminal states
    clinic_day_exhausted = "clinic_day_exhausted"
    """No bookable slots remain for the requested same-day window."""

    handed_off = "handed_off"
    """The session has been handed off to staff; no further booking steps are possible."""

    existing_booking_found = "existing_booking_found"
    """An exact duplicate booking exists; no new booking was created."""


OutcomeFamily = Literal[
    "proceed",
    "clarify",
    "advisory",
    "no_availability",
    "roster_gap",
    "blocked",
    "terminal",
]


class BernieScheduleExplanationPayload(BaseModel):
    """Display-only schedule explanation attached to an outcome.

    This payload is intentionally non-authoritative. It may help clients render
    clearer receptionist-facing copy, but it must not decide availability,
    confirmation, freshness, or write payloads.
    """

    model_config = {"frozen": True}

    reason_code: str
    title: str
    staff_prompt: str
    basis: str = ""
    authority: Literal["display_only"] = "display_only"

_KIND_FAMILY: dict[BernieBookingOutcomeKind, OutcomeFamily] = {
    BernieBookingOutcomeKind.interpreted_ready: "proceed",
    BernieBookingOutcomeKind.candidate_selection_required: "proceed",
    BernieBookingOutcomeKind.confirmation_ready: "proceed",
    BernieBookingOutcomeKind.clarification_required: "clarify",
    BernieBookingOutcomeKind.advisory_warnings_present: "advisory",
    BernieBookingOutcomeKind.no_matching_times: "no_availability",
    BernieBookingOutcomeKind.roster_unavailable: "roster_gap",
    BernieBookingOutcomeKind.guardrail_blocked: "blocked",
    BernieBookingOutcomeKind.clinic_day_exhausted: "terminal",
    BernieBookingOutcomeKind.handed_off: "terminal",
    BernieBookingOutcomeKind.existing_booking_found: "advisory",
}

_KIND_REQUIRES_CONFIRMATION: dict[BernieBookingOutcomeKind, bool] = {
    BernieBookingOutcomeKind.confirmation_ready: True,
}

# can_confirm is REPORT ONLY — never itself a grant of confirm authority.
# Confirm authority still requires the existing gate + signed evidence + session binding.
_KIND_CAN_CONFIRM: dict[BernieBookingOutcomeKind, bool] = {
    BernieBookingOutcomeKind.confirmation_ready: True,
}

_KIND_IS_TERMINAL: dict[BernieBookingOutcomeKind, bool] = {
    BernieBookingOutcomeKind.clinic_day_exhausted: True,
    BernieBookingOutcomeKind.handed_off: True,
}

# Primary session state (as string) each outcome kind corresponds to.
# String literals avoid importing from app.services.bernie which would create
# a circular import through bernie/__init__. Values must stay in sync with
# BernieSessionState enum values in app.services.bernie.session.
_KIND_PRIMARY_SESSION_STATE: dict[BernieBookingOutcomeKind, str] = {
    BernieBookingOutcomeKind.guardrail_blocked: _SS_NO_SLOT,
    BernieBookingOutcomeKind.clarification_required: _SS_CLARIFICATION,
    BernieBookingOutcomeKind.roster_unavailable: _SS_NO_SLOT,
    BernieBookingOutcomeKind.no_matching_times: _SS_NO_SLOT,
    BernieBookingOutcomeKind.clinic_day_exhausted: _SS_CLINIC_DAY_EXHAUSTED,
    BernieBookingOutcomeKind.confirmation_ready: _SS_PROPOSAL_PREVIEW,
    BernieBookingOutcomeKind.candidate_selection_required: _SS_CANDIDATE_SELECTION,
    BernieBookingOutcomeKind.advisory_warnings_present: _SS_CONTEXT_ENRICHMENT,
    BernieBookingOutcomeKind.interpreted_ready: _SS_CONTEXT_ENRICHMENT,
    BernieBookingOutcomeKind.handed_off: _SS_HANDED_OFF,
    BernieBookingOutcomeKind.existing_booking_found: _SS_NO_SLOT,
}

#: Maps each outcome kind to the FULL set of valid session-state STRINGS a
#: route may advance to when that outcome is classified. String values match
#: BernieSessionState enum values. Used by assert_outcome_matches_state() to
#: catch outcome/state disagreements that would otherwise be silent bugs.
OUTCOME_SESSION_STATE: dict[BernieBookingOutcomeKind, frozenset[str]] = {
    BernieBookingOutcomeKind.guardrail_blocked: frozenset({
        _SS_NO_SLOT,
        _SS_HANDED_OFF,   # interpret route: blocked result → handed_off
    }),
    BernieBookingOutcomeKind.clarification_required: frozenset({
        _SS_CLARIFICATION,
    }),
    BernieBookingOutcomeKind.roster_unavailable: frozenset({
        _SS_NO_SLOT,
    }),
    BernieBookingOutcomeKind.no_matching_times: frozenset({
        _SS_NO_SLOT,
    }),
    BernieBookingOutcomeKind.clinic_day_exhausted: frozenset({
        _SS_CLINIC_DAY_EXHAUSTED,
    }),
    BernieBookingOutcomeKind.confirmation_ready: frozenset({
        _SS_PROPOSAL_PREVIEW,
    }),
    BernieBookingOutcomeKind.candidate_selection_required: frozenset({
        _SS_CANDIDATE_SELECTION,
        _SS_NO_SLOT,   # zero-candidate path: session targets no_slot
    }),
    BernieBookingOutcomeKind.advisory_warnings_present: frozenset({
        _SS_CONTEXT_ENRICHMENT,
        _SS_CANDIDATE_SELECTION,
    }),
    BernieBookingOutcomeKind.interpreted_ready: frozenset({
        _SS_CONTEXT_ENRICHMENT,
    }),
    BernieBookingOutcomeKind.handed_off: frozenset({
        _SS_HANDED_OFF,
    }),
    BernieBookingOutcomeKind.existing_booking_found: frozenset({
        _SS_NO_SLOT,
    }),
}


class BernieBookingOutcome(BaseModel):
    """Read-only typed outcome label for a single Bernie booking turn.

    Attached to route envelopes as an additive field so callers can read one
    authoritative label instead of reconciling the result literal,
    reception_policy flags, and server_session state.

    session_state holds a BernieSessionState string value (the enum is str-based
    so instances compare equal to the corresponding plain strings).

    can_confirm is REPORT ONLY and never itself a confirm grant. Confirm
    authority still requires the existing gate, signed evidence, and session
    binding — none of which this model creates or stores.
    """

    model_config = {"frozen": True}

    kind: BernieBookingOutcomeKind
    family: OutcomeFamily
    session_state: str
    requires_confirmation: bool
    can_confirm: bool = False
    is_terminal: bool = False
    reason_codes: list[str] = Field(default_factory=list)
    basis: str = ""
    schedule_explanation: BernieScheduleExplanationPayload | None = None


def _build_schedule_explanation_payload(
    policy: BernieReceptionPolicyDecision,
) -> BernieScheduleExplanationPayload | None:
    for code in [*policy.schedule_reason_codes, *policy.reason_codes]:
        reason = parse_schedule_explanation_reason(code)
        if reason is None:
            continue
        copy = get_schedule_copy(reason)
        return BernieScheduleExplanationPayload(
            reason_code=reason.value,
            title=copy.title,
            staff_prompt=copy.staff_prompt,
            basis=f"Typed schedule reason: {reason.value}.",
        )
    return None


def classify_booking_outcome(
    policy: BernieReceptionPolicyDecision,
    *,
    has_staged_proposal: bool = False,
    has_candidates: bool = False,
    route_result: Optional[str] = None,
) -> BernieBookingOutcome:
    """Classify a Bernie booking turn into one mutually-exclusive outcome kind.

    Precedence (first match wins; hard blocks dominate advisory warnings):

    1. handed_off           — route_result == "handed_off"
    2. existing_booking_found — route_result == "existing_booking_found"
    3. clarification_required — route_result == "clarification_required"
    4. guardrail_blocked    — availability == "blocked"
    5. interpreted_ready    — route_result == "interpreted" and no hard availability fact
    6. clarification_required — must_ask or must_block_confirmation (stale/missing)
    7. roster_unavailable   — no practitioner schedule available to search against
    8. clinic_day_exhausted — route signals same-day window exhausted
    9. no_matching_times    — search ran with available roster, found zero candidates
    10. confirmation_ready  — staged proposal present with no adverse signals
    11. candidate_selection_required — candidates found but no staged proposal
    12. advisory_warnings_present — only advisory warnings, nothing stronger
    13. interpreted_ready   — no adverse signals; interpretation succeeded

    Advisories alongside candidates ride as reason_codes on
    candidate_selection_required rather than becoming a standalone advisory
    outcome (advisory is only emitted when nothing stronger is present).

    Pure: no DB, no clock, no LLM. All evidence must be passed in as typed
    policy predicates and route-context hints.
    """
    reason_codes = list(policy.reason_codes)

    if route_result == "handed_off":
        kind = BernieBookingOutcomeKind.handed_off
        basis = "Session has been handed off to staff."
    elif route_result == "existing_booking_found":
        kind = BernieBookingOutcomeKind.existing_booking_found
        basis = "An exact duplicate booking already exists; no new booking was created."
    elif route_result == "clarification_required":
        kind = BernieBookingOutcomeKind.clarification_required
        basis = "The route requires clarification before proceeding."
    elif policy.availability == "blocked":
        kind = BernieBookingOutcomeKind.guardrail_blocked
        basis = "A guardrail outcome frame hard-blocked the request."
    elif route_result == "interpreted" and not policy.advisory_warnings_only:
        kind = BernieBookingOutcomeKind.interpreted_ready
        basis = "Interpretation succeeded with no adverse signals; ready for context enrichment."
    elif policy.must_ask_clarification or policy.must_block_confirmation:
        kind = BernieBookingOutcomeKind.clarification_required
        basis = (
            "Missing or partial request, model uncertainty, or stale evidence "
            "requires clarification before proceeding."
        )
    elif policy.roster_unavailable:
        kind = BernieBookingOutcomeKind.roster_unavailable
        basis = "No practitioner schedule or roster is available to search against."
    elif route_result == "clinic_day_exhausted":
        kind = BernieBookingOutcomeKind.clinic_day_exhausted
        basis = "No bookable slots remain in the requested same-day window."
    elif policy.search_ran_no_candidates:
        kind = BernieBookingOutcomeKind.no_matching_times
        basis = (
            "Slot search ran against an available roster but found no matching slots "
            "for the requested criteria."
        )
    elif route_result == "blocked":
        kind = BernieBookingOutcomeKind.guardrail_blocked
        basis = "The route blocked the request before it could proceed."
    elif has_staged_proposal:
        kind = BernieBookingOutcomeKind.confirmation_ready
        basis = "A create proposal is staged; explicit staff confirmation is required."
    elif has_candidates:
        kind = BernieBookingOutcomeKind.candidate_selection_required
        basis = "Slot candidates were found; staff must select one before staging a proposal."
    elif policy.advisory_warnings_only:
        kind = BernieBookingOutcomeKind.advisory_warnings_present
        basis = "Only advisory warnings are present; no hard block or search result yet."
    else:
        kind = BernieBookingOutcomeKind.interpreted_ready
        basis = "Interpretation succeeded with no adverse signals; ready for context enrichment."

    return BernieBookingOutcome(
        kind=kind,
        family=_KIND_FAMILY[kind],
        session_state=_KIND_PRIMARY_SESSION_STATE[kind],
        requires_confirmation=_KIND_REQUIRES_CONFIRMATION.get(kind, False),
        can_confirm=_KIND_CAN_CONFIRM.get(kind, False),
        is_terminal=_KIND_IS_TERMINAL.get(kind, False),
        reason_codes=reason_codes,
        basis=basis,
        schedule_explanation=_build_schedule_explanation_payload(policy),
    )


def assert_outcome_matches_state(
    kind: BernieBookingOutcomeKind,
    target_state: str,
) -> None:
    """Assert that an outcome kind is consistent with the route's target session state.

    target_state is a BernieSessionState string value (the enum is str-based so
    enum members compare equal to their plain string equivalents).

    Raises AssertionError when the pair disagrees. In tests this is a hard
    failure; in the router the caller may choose to log+continue so a mismatch
    never silently hides a wiring bug. The mismatch should never occur if routes
    are correctly wired.
    """
    valid_states = OUTCOME_SESSION_STATE.get(kind, frozenset())
    # Convert to str so BernieSessionState enum values and plain strings both match.
    state_str = str(target_state) if not isinstance(target_state, str) else target_state
    assert state_str in valid_states, (
        f"Outcome kind {kind.value!r} is not consistent with session target "
        f"{state_str!r}. Valid targets for this kind: {sorted(valid_states)}"
    )


__all__ = [
    "BernieBookingOutcome",
    "BernieBookingOutcomeKind",
    "BernieScheduleExplanationPayload",
    "OutcomeFamily",
    "OUTCOME_SESSION_STATE",
    "assert_outcome_matches_state",
    "classify_booking_outcome",
]
