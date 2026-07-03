"""Tests for the N10 Bernie booking outcome classification contract.

Verifies:
(a) Each BernieBookingOutcomeKind is emitted from the correct policy/context.
(b) Precedence / mutual exclusivity: hard blocks dominate advisory warnings;
    roster_unavailable != no_matching_times.
(c) Outcome<->session_state consistency for every route branch via
    assert_outcome_matches_state().
(d) No-write / confirm boundary: can_confirm=True is a REPORT ONLY field and
    the outcome never sets confirm authority by itself.
(e) Stale / legacy compatibility: clients that omit server_session or outcome
    are unaffected by the additive field.
"""

import pytest
from datetime import date

from app.services.bernie.session import BernieSessionState
from app.services.diary.outcomes import (
    BernieBookingOutcome,
    BernieBookingOutcomeKind,
    OUTCOME_SESSION_STATE,
    assert_outcome_matches_state,
    classify_booking_outcome,
)
from app.services.diary.policy import BernieReceptionPolicyDecision


REFERENCE_DATE = date(2026, 7, 3)


# ── Policy factories ──────────────────────────────────────────────────────────

def _clean_policy(**overrides) -> BernieReceptionPolicyDecision:
    """A fully-clean policy with no adverse signals."""
    defaults = dict(
        availability="not_evaluated",
        can_search_slots=True,
        must_ask_clarification=False,
        can_offer_candidates=False,
        can_prepare_proposal=False,
        must_block_confirmation=False,
        advisory_warnings_only=False,
        roster_unavailable=False,
        search_ran_no_candidates=False,
        reason_codes=[],
        schedule_reason_codes=[],
    )
    defaults.update(overrides)
    return BernieReceptionPolicyDecision(**defaults)


def _blocked_policy(reason_codes=None) -> BernieReceptionPolicyDecision:
    return _clean_policy(
        availability="blocked",
        can_search_slots=False,
        must_block_confirmation=True,
        reason_codes=reason_codes or ["guardrail_test"],
    )


def _must_ask_policy() -> BernieReceptionPolicyDecision:
    return _clean_policy(must_ask_clarification=True, reason_codes=["patient_identity_uncertain"])


def _stale_policy() -> BernieReceptionPolicyDecision:
    return _clean_policy(must_block_confirmation=True, reason_codes=["context_reference_date_stale"])


def _roster_unavailable_policy() -> BernieReceptionPolicyDecision:
    return _clean_policy(
        roster_unavailable=True,
        availability="roster_unavailable",
        can_search_slots=False,
        reason_codes=["no_practitioner_schedule"],
    )


def _no_candidates_policy() -> BernieReceptionPolicyDecision:
    return _clean_policy(
        search_ran_no_candidates=True,
        availability="search_ran_no_candidates",
        reason_codes=["no_slot_candidates"],
    )


def _candidates_policy() -> BernieReceptionPolicyDecision:
    return _clean_policy(
        availability="search_ran_with_candidates",
        can_offer_candidates=True,
        can_prepare_proposal=False,
    )


def _advisory_policy() -> BernieReceptionPolicyDecision:
    return _clean_policy(
        advisory_warnings_only=True,
        reason_codes=["existing_future_follow_up"],
    )


# ── (a) Each kind from crafted policy/context ─────────────────────────────────

def test_interpreted_ready_clean_policy():
    outcome = classify_booking_outcome(_clean_policy())
    assert outcome.kind == BernieBookingOutcomeKind.interpreted_ready
    assert outcome.family == "proceed"
    assert outcome.session_state == BernieSessionState.context_enrichment
    assert not outcome.requires_confirmation
    assert not outcome.can_confirm
    assert not outcome.is_terminal


def test_interpreted_route_result_dominates_soft_model_uncertainty():
    """Accepted interpretation advances to context enrichment despite conservative checks."""
    outcome = classify_booking_outcome(
        _must_ask_policy(),
        route_result="interpreted",
    )

    assert outcome.kind == BernieBookingOutcomeKind.interpreted_ready
    assert outcome.session_state == BernieSessionState.context_enrichment


def test_guardrail_blocked_from_availability_blocked():
    outcome = classify_booking_outcome(_blocked_policy())
    assert outcome.kind == BernieBookingOutcomeKind.guardrail_blocked
    assert outcome.family == "blocked"
    assert not outcome.can_confirm
    assert "guardrail_test" in outcome.reason_codes


def test_clarification_required_from_must_ask():
    outcome = classify_booking_outcome(_must_ask_policy())
    assert outcome.kind == BernieBookingOutcomeKind.clarification_required
    assert outcome.family == "clarify"
    assert outcome.session_state == BernieSessionState.clarification
    assert not outcome.can_confirm


def test_clarification_required_from_stale_evidence():
    outcome = classify_booking_outcome(_stale_policy())
    assert outcome.kind == BernieBookingOutcomeKind.clarification_required
    assert outcome.family == "clarify"
    assert not outcome.can_confirm


def test_roster_unavailable_from_policy():
    outcome = classify_booking_outcome(_roster_unavailable_policy())
    assert outcome.kind == BernieBookingOutcomeKind.roster_unavailable
    assert outcome.family == "roster_gap"
    assert outcome.session_state == BernieSessionState.no_slot
    assert not outcome.can_confirm


def test_no_matching_times_from_searched_no_candidates():
    outcome = classify_booking_outcome(_no_candidates_policy())
    assert outcome.kind == BernieBookingOutcomeKind.no_matching_times
    assert outcome.family == "no_availability"
    assert outcome.session_state == BernieSessionState.no_slot
    assert not outcome.can_confirm


def test_clinic_day_exhausted_from_route_result():
    policy = _clean_policy()  # no adverse policy signals
    outcome = classify_booking_outcome(policy, route_result="clinic_day_exhausted")
    assert outcome.kind == BernieBookingOutcomeKind.clinic_day_exhausted
    assert outcome.family == "terminal"
    assert outcome.is_terminal
    assert not outcome.can_confirm


def test_confirmation_ready_from_staged_proposal():
    policy = _candidates_policy()
    outcome = classify_booking_outcome(
        policy, has_staged_proposal=True, has_candidates=True,
    )
    assert outcome.kind == BernieBookingOutcomeKind.confirmation_ready
    assert outcome.family == "proceed"
    assert outcome.requires_confirmation
    assert outcome.can_confirm  # REPORT ONLY
    assert outcome.session_state == BernieSessionState.proposal_preview


def test_candidate_selection_required_from_candidates():
    policy = _candidates_policy()
    outcome = classify_booking_outcome(policy, has_candidates=True)
    assert outcome.kind == BernieBookingOutcomeKind.candidate_selection_required
    assert outcome.family == "proceed"
    assert not outcome.requires_confirmation
    assert not outcome.can_confirm
    assert outcome.session_state == BernieSessionState.candidate_selection


def test_advisory_warnings_present_from_advisory_only():
    outcome = classify_booking_outcome(_advisory_policy())
    assert outcome.kind == BernieBookingOutcomeKind.advisory_warnings_present
    assert outcome.family == "advisory"
    assert not outcome.can_confirm
    assert "existing_future_follow_up" in outcome.reason_codes


def test_handed_off_from_route_result():
    policy = _clean_policy()
    outcome = classify_booking_outcome(policy, route_result="handed_off")
    assert outcome.kind == BernieBookingOutcomeKind.handed_off
    assert outcome.family == "terminal"
    assert outcome.is_terminal
    assert not outcome.can_confirm
    assert outcome.session_state == BernieSessionState.handed_off


# ── (b) Precedence / mutual exclusivity ──────────────────────────────────────

def test_blocked_dominates_must_ask_clarification():
    """Hard block must win over clarification requirement."""
    policy = _clean_policy(
        availability="blocked",
        must_block_confirmation=True,
        must_ask_clarification=True,
        reason_codes=["guardrail", "partial_request"],
    )
    outcome = classify_booking_outcome(policy)
    assert outcome.kind == BernieBookingOutcomeKind.guardrail_blocked


def test_blocked_dominates_roster_unavailable():
    policy = _clean_policy(
        availability="blocked",
        must_block_confirmation=True,
        roster_unavailable=True,
        reason_codes=["guardrail"],
    )
    outcome = classify_booking_outcome(policy)
    assert outcome.kind == BernieBookingOutcomeKind.guardrail_blocked


def test_blocked_dominates_advisory_warnings():
    policy = _clean_policy(
        availability="blocked",
        must_block_confirmation=True,
        advisory_warnings_only=False,
        reason_codes=["guardrail"],
    )
    outcome = classify_booking_outcome(policy)
    assert outcome.kind == BernieBookingOutcomeKind.guardrail_blocked


def test_roster_unavailable_distinct_from_no_matching_times():
    """roster_unavailable != no_matching_times — different families, different session states."""
    roster_out = classify_booking_outcome(_roster_unavailable_policy())
    no_match_out = classify_booking_outcome(_no_candidates_policy())
    assert roster_out.kind == BernieBookingOutcomeKind.roster_unavailable
    assert no_match_out.kind == BernieBookingOutcomeKind.no_matching_times
    assert roster_out.kind != no_match_out.kind
    assert roster_out.family == "roster_gap"
    assert no_match_out.family == "no_availability"


def test_no_matching_times_requires_roster_present():
    """no_matching_times must NOT fire when roster is unavailable."""
    policy = _clean_policy(
        roster_unavailable=True,
        search_ran_no_candidates=True,  # both flags set
        availability="roster_unavailable",
        can_search_slots=False,
        reason_codes=["no_practitioner_schedule"],
    )
    outcome = classify_booking_outcome(policy)
    # roster_unavailable wins over search_ran_no_candidates (higher precedence)
    assert outcome.kind == BernieBookingOutcomeKind.roster_unavailable


def test_roster_unavailable_dominates_generic_blocked_route_result():
    """A generic blocked route label must not erase typed roster/schedule truth."""
    outcome = classify_booking_outcome(
        _roster_unavailable_policy(),
        route_result="blocked",
    )

    assert outcome.kind == BernieBookingOutcomeKind.roster_unavailable
    assert outcome.family == "roster_gap"
    assert "no_practitioner_schedule" in outcome.reason_codes


def test_blocked_route_result_fallbacks_to_guardrail_when_policy_has_no_reason():
    outcome = classify_booking_outcome(_clean_policy(), route_result="blocked")

    assert outcome.kind == BernieBookingOutcomeKind.guardrail_blocked
    assert outcome.family == "blocked"


def test_clinic_day_exhausted_dominates_search_zero_candidates():
    """Same-day exhaustion is distinct from a normal searched-zero-slot result."""
    outcome = classify_booking_outcome(
        _no_candidates_policy(),
        route_result="clinic_day_exhausted",
    )

    assert outcome.kind == BernieBookingOutcomeKind.clinic_day_exhausted
    assert outcome.family == "terminal"
    assert outcome.is_terminal


def test_advisory_rides_on_candidates_not_standalone():
    """Advisory warnings alongside candidates produce candidate_selection_required."""
    policy = _clean_policy(
        availability="search_ran_with_candidates",
        can_offer_candidates=True,
        advisory_warnings_only=False,  # advisory not standalone when candidates present
        reason_codes=["existing_future_follow_up"],
    )
    outcome = classify_booking_outcome(policy, has_candidates=True)
    assert outcome.kind == BernieBookingOutcomeKind.candidate_selection_required
    assert "existing_future_follow_up" in outcome.reason_codes


def test_confirmation_ready_dominates_candidates():
    """Staged proposal wins over bare candidate presence."""
    policy = _candidates_policy()
    outcome = classify_booking_outcome(
        policy, has_staged_proposal=True, has_candidates=True,
    )
    assert outcome.kind == BernieBookingOutcomeKind.confirmation_ready


def test_clinic_day_exhausted_not_emitted_without_route_result():
    """clinic_day_exhausted only when route_result signals it."""
    policy = _no_candidates_policy()  # policy shows no candidates
    outcome = classify_booking_outcome(policy)
    # Without route_result="clinic_day_exhausted" we classify no_matching_times
    assert outcome.kind == BernieBookingOutcomeKind.no_matching_times


# ── (c) Outcome<->session_state consistency ───────────────────────────────────

def test_assert_outcome_matches_state_passes_for_valid_pairs():
    valid_pairs = [
        (BernieBookingOutcomeKind.guardrail_blocked, BernieSessionState.no_slot),
        (BernieBookingOutcomeKind.guardrail_blocked, BernieSessionState.handed_off),
        (BernieBookingOutcomeKind.clarification_required, BernieSessionState.clarification),
        (BernieBookingOutcomeKind.roster_unavailable, BernieSessionState.no_slot),
        (BernieBookingOutcomeKind.no_matching_times, BernieSessionState.no_slot),
        (BernieBookingOutcomeKind.clinic_day_exhausted, BernieSessionState.clinic_day_exhausted),
        (BernieBookingOutcomeKind.confirmation_ready, BernieSessionState.proposal_preview),
        (BernieBookingOutcomeKind.candidate_selection_required, BernieSessionState.candidate_selection),
        (BernieBookingOutcomeKind.candidate_selection_required, BernieSessionState.no_slot),
        (BernieBookingOutcomeKind.advisory_warnings_present, BernieSessionState.context_enrichment),
        (BernieBookingOutcomeKind.advisory_warnings_present, BernieSessionState.candidate_selection),
        (BernieBookingOutcomeKind.interpreted_ready, BernieSessionState.context_enrichment),
        (BernieBookingOutcomeKind.handed_off, BernieSessionState.handed_off),
    ]
    for kind, state in valid_pairs:
        assert_outcome_matches_state(kind, state)  # must not raise


def test_assert_outcome_matches_state_fails_for_invalid_pair():
    with pytest.raises(AssertionError, match="not consistent"):
        assert_outcome_matches_state(
            BernieBookingOutcomeKind.confirmation_ready,
            BernieSessionState.no_slot,
        )


def test_assert_outcome_matches_state_fails_roster_unavailable_vs_candidate_selection():
    with pytest.raises(AssertionError):
        assert_outcome_matches_state(
            BernieBookingOutcomeKind.roster_unavailable,
            BernieSessionState.candidate_selection,
        )


def test_interpret_route_clarification_state_consistent():
    outcome = classify_booking_outcome(_must_ask_policy())
    assert_outcome_matches_state(
        outcome.kind,
        BernieSessionState.clarification,
    )


def test_interpret_route_blocked_state_consistent_with_handed_off():
    outcome = classify_booking_outcome(_blocked_policy())
    # The interpret route advances to handed_off when result=="blocked"
    assert_outcome_matches_state(
        outcome.kind,
        BernieSessionState.handed_off,
    )


def test_supervised_blocked_state_consistent_with_no_slot():
    outcome = classify_booking_outcome(_blocked_policy())
    # The supervised route advances to no_slot on block
    assert_outcome_matches_state(
        outcome.kind,
        BernieSessionState.no_slot,
    )


def test_supervised_confirmation_ready_state_consistent():
    outcome = classify_booking_outcome(
        _candidates_policy(), has_staged_proposal=True, has_candidates=True,
    )
    assert_outcome_matches_state(
        outcome.kind,
        BernieSessionState.proposal_preview,
    )


def test_all_kinds_have_session_state_mapping():
    """Every outcome kind must have at least one valid session state."""
    for kind in BernieBookingOutcomeKind:
        assert kind in OUTCOME_SESSION_STATE, f"{kind} missing from OUTCOME_SESSION_STATE"
        assert len(OUTCOME_SESSION_STATE[kind]) >= 1


# ── (d) No-write / confirm boundary ──────────────────────────────────────────

def test_can_confirm_is_true_only_for_confirmation_ready():
    """can_confirm is True ONLY for confirmation_ready kind; all others False."""
    policy_with_proposal = _candidates_policy()
    for kind in BernieBookingOutcomeKind:
        if kind == BernieBookingOutcomeKind.confirmation_ready:
            outcome = classify_booking_outcome(
                policy_with_proposal, has_staged_proposal=True, has_candidates=True,
            )
        elif kind == BernieBookingOutcomeKind.guardrail_blocked:
            outcome = classify_booking_outcome(_blocked_policy())
        elif kind == BernieBookingOutcomeKind.clarification_required:
            outcome = classify_booking_outcome(_must_ask_policy())
        elif kind == BernieBookingOutcomeKind.roster_unavailable:
            outcome = classify_booking_outcome(_roster_unavailable_policy())
        elif kind == BernieBookingOutcomeKind.no_matching_times:
            outcome = classify_booking_outcome(_no_candidates_policy())
        elif kind == BernieBookingOutcomeKind.clinic_day_exhausted:
            outcome = classify_booking_outcome(_clean_policy(), route_result="clinic_day_exhausted")
        elif kind == BernieBookingOutcomeKind.candidate_selection_required:
            outcome = classify_booking_outcome(_candidates_policy(), has_candidates=True)
        elif kind == BernieBookingOutcomeKind.advisory_warnings_present:
            outcome = classify_booking_outcome(_advisory_policy())
        elif kind == BernieBookingOutcomeKind.interpreted_ready:
            outcome = classify_booking_outcome(_clean_policy())
        elif kind == BernieBookingOutcomeKind.handed_off:
            outcome = classify_booking_outcome(_clean_policy(), route_result="handed_off")
        else:
            continue

        if kind == BernieBookingOutcomeKind.confirmation_ready:
            assert outcome.can_confirm, f"{kind} should have can_confirm=True"
        else:
            assert not outcome.can_confirm, (
                f"{kind} must have can_confirm=False (REPORT ONLY; never a grant)"
            )


def test_outcome_model_is_frozen():
    """BernieBookingOutcome is frozen; mutations must raise."""
    outcome = classify_booking_outcome(_clean_policy())
    with pytest.raises(Exception):
        outcome.kind = BernieBookingOutcomeKind.guardrail_blocked  # type: ignore[misc]


def test_outcome_never_creates_proposal_or_booking():
    """The outcome object has no methods or fields that could write to DB/slots."""
    outcome = classify_booking_outcome(
        _candidates_policy(), has_staged_proposal=True, has_candidates=True,
    )
    assert outcome.kind == BernieBookingOutcomeKind.confirmation_ready
    # The outcome itself carries no create_proposal, no slot coordinates, no DB id.
    assert not hasattr(outcome, "create_proposal")
    assert not hasattr(outcome, "slot_id")
    assert not hasattr(outcome, "appointment_id")
    assert not hasattr(outcome, "confirm")


# ── (e) Stale / legacy compatibility ─────────────────────────────────────────

def test_classify_booking_outcome_no_route_result():
    """route_result=None is always safe; function returns a deterministic outcome."""
    outcome = classify_booking_outcome(_clean_policy(), route_result=None)
    assert outcome.kind == BernieBookingOutcomeKind.interpreted_ready


def test_outcome_session_state_map_covers_all_kinds():
    """OUTCOME_SESSION_STATE must cover every BernieBookingOutcomeKind."""
    for kind in BernieBookingOutcomeKind:
        assert kind in OUTCOME_SESSION_STATE, (
            f"OUTCOME_SESSION_STATE is missing entry for {kind.value!r}"
        )


def test_classify_with_unknown_route_result_fallbacks_gracefully():
    """Unrecognised route_result values should not raise; classifier uses policy."""
    outcome = classify_booking_outcome(_clean_policy(), route_result="unrecognised_future_value")
    # No special kind for unknown strings; falls through to interpreted_ready
    assert outcome.kind == BernieBookingOutcomeKind.interpreted_ready


def test_outcome_out_schema_additive_fields_default_none():
    """BernieBookingOutcomeOut is additive; import and round-trip a minimal dict."""
    from app.schemas.appointments import BernieBookingOutcomeOut
    from app.services.diary.outcomes import classify_booking_outcome, BernieReceptionPolicyDecision
    policy = BernieReceptionPolicyDecision(
        availability="not_evaluated",
        can_search_slots=True,
        must_ask_clarification=False,
        can_offer_candidates=False,
        can_prepare_proposal=False,
        must_block_confirmation=False,
        advisory_warnings_only=False,
        roster_unavailable=False,
        search_ran_no_candidates=False,
        reason_codes=[],
        schedule_reason_codes=[],
    )
    domain_outcome = classify_booking_outcome(policy)
    schema_out = BernieBookingOutcomeOut(**domain_outcome.model_dump())
    assert schema_out.kind == BernieBookingOutcomeKind.interpreted_ready
    assert schema_out.can_confirm is False
    assert schema_out.is_terminal is False
