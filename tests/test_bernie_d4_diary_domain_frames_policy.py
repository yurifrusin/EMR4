"""Sprint D4 diary-domain frames/policy bounded tests.

Verifies the safe D4 slice (Ariadne amendment applied):
(a) BernieSlotSearchFrame.search_horizon round-trips without changing any
    outcome classification — a real searched_no_candidates result stays
    no_matching_times regardless of search_horizon value.
(b) roster_schedule unavailable with no reason_code yields schedule_reason_codes
    containing no_roster_row so roster_unavailable always self-explains.
(c) no_matching_times is gated by a real slot_search searched_no_candidates
    frame; search_horizon never fabricates no-candidate copy or converts a
    non-search frame into a no_availability outcome.
"""

from datetime import date

import pytest

from app.services.diary.frames import (
    BernieReceptionContextFrameSet,
    BernieRosterScheduleFrame,
    BernieSlotSearchFrame,
)
from app.services.diary.outcomes import (
    BernieBookingOutcomeKind,
    BernieScheduleExplanationPayload,
    classify_booking_outcome,
)
from app.services.diary.policy import evaluate_reception_context


REFERENCE_DATE = date(2026, 7, 4)


def _frame_set(*frames):
    return BernieReceptionContextFrameSet(
        reference_date=REFERENCE_DATE,
        frames=list(frames),
    )


def _slot_search_no_candidates(search_horizon=None):
    return BernieSlotSearchFrame(
        status="searched_no_candidates",
        reason_code="no_slot_candidates",
        basis="Search ran, zero candidates.",
        reference_date=REFERENCE_DATE,
        candidate_count=0,
        search_horizon=search_horizon,
    )


def _roster_available_frame():
    return BernieRosterScheduleFrame(
        status="available",
        basis="Roster is available.",
        reference_date=REFERENCE_DATE,
    )


# ── search_horizon field round-trips ──────────────────────────────────────────

def test_search_horizon_defaults_to_none():
    frame = BernieSlotSearchFrame(
        status="searched_no_candidates",
        basis="Search ran.",
        reference_date=REFERENCE_DATE,
        candidate_count=0,
    )
    assert frame.search_horizon is None


def test_search_horizon_same_day_round_trips():
    frame = BernieSlotSearchFrame(
        status="searched_no_candidates",
        basis="Same-day search ran.",
        reference_date=REFERENCE_DATE,
        candidate_count=0,
        search_horizon="same_day",
    )
    assert frame.search_horizon == "same_day"


def test_search_horizon_advance_round_trips():
    frame = BernieSlotSearchFrame(
        status="searched_no_candidates",
        basis="Advance search ran.",
        reference_date=REFERENCE_DATE,
        candidate_count=0,
        search_horizon="advance",
    )
    assert frame.search_horizon == "advance"


# ── search_horizon does NOT change outcome semantics ──────────────────────────

@pytest.mark.parametrize("horizon", [None, "same_day", "advance"])
def test_searched_no_candidates_stays_no_matching_times_regardless_of_horizon(horizon):
    """A real slot search that found zero candidates is no_matching_times — always.

    The Ariadne amendment prohibits downgrading genuine slot_search
    searched_no_candidates to advisory for future/advance searches.
    """
    fs = _frame_set(_roster_available_frame(), _slot_search_no_candidates(horizon))
    policy = evaluate_reception_context(fs)

    assert policy.search_ran_no_candidates is True
    assert policy.roster_unavailable is False
    assert policy.availability == "search_ran_no_candidates"

    outcome = classify_booking_outcome(policy)
    assert outcome.kind == BernieBookingOutcomeKind.no_matching_times
    assert outcome.family == "no_availability"


@pytest.mark.parametrize("horizon", [None, "same_day", "advance"])
def test_search_horizon_does_not_change_policy_predicates(horizon):
    fs = _frame_set(_roster_available_frame(), _slot_search_no_candidates(horizon))
    policy = evaluate_reception_context(fs)

    assert policy.search_ran_no_candidates is True
    assert policy.can_search_slots is True  # hard_block/stale/must_ask = False
    assert policy.advisory_warnings_only is False
    assert "searched_no_candidates" in policy.schedule_reason_codes


# ── roster_unavailable always self-explains ───────────────────────────────────

def test_roster_unavailable_no_reason_code_yields_no_roster_row_in_schedule_codes():
    """roster_schedule unavailable with no reason_code must synthesize no_roster_row."""
    fs = _frame_set(
        BernieRosterScheduleFrame(
            status="unavailable",
            basis="No roster row found for this practitioner.",
            reference_date=REFERENCE_DATE,
            # reason_code intentionally omitted
        )
    )
    policy = evaluate_reception_context(fs)

    assert policy.roster_unavailable is True
    assert "no_roster_row" in policy.schedule_reason_codes


def test_roster_unavailable_no_reason_code_outcome_has_schedule_explanation():
    """roster_unavailable outcome always attaches a schedule_explanation."""
    fs = _frame_set(
        BernieRosterScheduleFrame(
            status="unavailable",
            basis="No roster row.",
            reference_date=REFERENCE_DATE,
        )
    )
    policy = evaluate_reception_context(fs)
    outcome = classify_booking_outcome(policy)

    assert outcome.kind == BernieBookingOutcomeKind.roster_unavailable
    assert outcome.schedule_explanation is not None
    assert isinstance(outcome.schedule_explanation, BernieScheduleExplanationPayload)
    assert outcome.schedule_explanation.authority == "display_only"
    assert outcome.schedule_explanation.reason_code == "no_roster_row"


def test_roster_unavailable_with_explicit_reason_code_keeps_that_reason():
    """An explicit reason_code on roster_schedule is preserved as-is."""
    fs = _frame_set(
        BernieRosterScheduleFrame(
            status="unavailable",
            reason_code="practitioner_unavailable",
            basis="Practitioner is on leave.",
            reference_date=REFERENCE_DATE,
        )
    )
    policy = evaluate_reception_context(fs)
    outcome = classify_booking_outcome(policy)

    assert outcome.kind == BernieBookingOutcomeKind.roster_unavailable
    assert outcome.schedule_explanation is not None
    assert outcome.schedule_explanation.reason_code == "practitioner_unavailable"
    # fallback no_roster_row must NOT clobber the explicit reason
    assert "no_roster_row" not in policy.schedule_reason_codes


def test_roster_unavailable_with_alias_reason_code_resolves_to_catalog():
    """Legacy alias codes on roster_schedule also resolve to a schedule_explanation."""
    fs = _frame_set(
        BernieRosterScheduleFrame(
            status="unavailable",
            reason_code="no_practitioner_schedule",
            basis="No practitioner schedule row.",
            reference_date=REFERENCE_DATE,
        )
    )
    policy = evaluate_reception_context(fs)
    outcome = classify_booking_outcome(policy)

    assert outcome.kind == BernieBookingOutcomeKind.roster_unavailable
    assert outcome.schedule_explanation is not None
    # Alias resolves to no_roster_row
    assert outcome.schedule_explanation.reason_code == "no_roster_row"


# ── no_matching_times gated by real searched_no_candidates ────────────────────

def test_no_matching_times_requires_real_slot_search_frame():
    """A roster_schedule-only unavailable frame must NOT yield no_matching_times."""
    fs = _frame_set(
        BernieRosterScheduleFrame(
            status="unavailable",
            basis="No roster row.",
            reference_date=REFERENCE_DATE,
        )
    )
    policy = evaluate_reception_context(fs)

    assert policy.search_ran_no_candidates is False
    outcome = classify_booking_outcome(policy)
    assert outcome.kind != BernieBookingOutcomeKind.no_matching_times
    assert outcome.kind == BernieBookingOutcomeKind.roster_unavailable


def test_no_matching_times_not_emitted_without_any_slot_search_frame():
    """With only advisory frames, outcome is advisory_warnings_present, not no_matching_times."""
    from app.services.diary.frames import BernieAdvisoryWarningFrame

    fs = _frame_set(
        BernieAdvisoryWarningFrame(
            status="advisory",
            reason_code="future_advance_check",
            basis="Advisory: confirm roster for the advance date.",
            reference_date=REFERENCE_DATE,
        )
    )
    policy = evaluate_reception_context(fs)

    assert policy.search_ran_no_candidates is False
    outcome = classify_booking_outcome(policy)
    assert outcome.kind == BernieBookingOutcomeKind.advisory_warnings_present
    assert outcome.kind != BernieBookingOutcomeKind.no_matching_times


def test_legacy_frames_without_search_horizon_classify_identically_to_pre_d4():
    """Existing callers that omit search_horizon must produce the same outcome."""
    legacy_fs = _frame_set(_roster_available_frame(), _slot_search_no_candidates(None))
    new_fs = _frame_set(_roster_available_frame(), _slot_search_no_candidates("same_day"))

    legacy_policy = evaluate_reception_context(legacy_fs)
    new_policy = evaluate_reception_context(new_fs)

    assert legacy_policy.availability == new_policy.availability
    assert legacy_policy.search_ran_no_candidates == new_policy.search_ran_no_candidates
    assert legacy_policy.schedule_reason_codes == new_policy.schedule_reason_codes

    legacy_outcome = classify_booking_outcome(legacy_policy)
    new_outcome = classify_booking_outcome(new_policy)

    assert legacy_outcome.kind == new_outcome.kind
    assert legacy_outcome.family == new_outcome.family
