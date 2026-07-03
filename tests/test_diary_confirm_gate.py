"""Sprint N3 tests for the unified evidence-gated confirm-affordance contract.

Covers:
- Happy path (allowed)
- Each distinct block reason in isolation
- Precedence when multiple block conditions apply
- None/absent staleness does not block (staleness is optional)
- Absent staged proposal blocks with blocked_no_proposal
- schedule_reason_codes passthrough
- BernieFacade re-export parity
"""

from app.services.bernie_turn_evidence import StalenessResult, StalenessVerdict
from app.services.diary.confirm_gate import (
    ConfirmAffordanceDecision,
    ConfirmAffordanceGate,
    evaluate_confirm_affordance,
)
from app.services.diary.policy import BernieReceptionPolicyDecision


def _clean_policy(**overrides) -> BernieReceptionPolicyDecision:
    """Minimal policy that would allow confirm-grade UI (no blocks)."""
    defaults = dict(
        availability="search_ran_with_candidates",
        can_search_slots=True,
        must_ask_clarification=False,
        can_offer_candidates=True,
        can_prepare_proposal=True,
        must_block_confirmation=False,
        advisory_warnings_only=False,
        roster_unavailable=False,
        search_ran_no_candidates=False,
        reason_codes=[],
        schedule_reason_codes=[],
    )
    defaults.update(overrides)
    return BernieReceptionPolicyDecision(**defaults)


def _fresh() -> StalenessResult:
    return StalenessResult(verdict=StalenessVerdict.fresh, detail="")


def _stale() -> StalenessResult:
    return StalenessResult(verdict=StalenessVerdict.stale, detail="mismatch")


def _mismatched() -> StalenessResult:
    return StalenessResult(verdict=StalenessVerdict.mismatched_reference_date, detail="date differs")


# ── Happy path ─────────────────────────────────────────────────────────────────


def test_allowed_when_all_guards_pass():
    decision = evaluate_confirm_affordance(
        _clean_policy(),
        staleness=_fresh(),
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is True
    assert decision.can_show_confirm_ui is True
    assert decision.model_dump()["can_show_confirm_ui"] is True
    assert decision.gate == ConfirmAffordanceGate.allowed
    assert decision.blocking_reason_codes == []


def test_allowed_when_staleness_absent():
    """staleness=None means no staleness evidence; gate does not block on it."""
    decision = evaluate_confirm_affordance(
        _clean_policy(),
        staleness=None,
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is True
    assert decision.gate == ConfirmAffordanceGate.allowed


# ── Block: guardrail ──────────────────────────────────────────────────────────


def test_blocked_guardrail_when_must_block_confirmation():
    decision = evaluate_confirm_affordance(
        _clean_policy(must_block_confirmation=True),
        staleness=_fresh(),
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_guardrail


def test_blocked_guardrail_when_availability_blocked():
    decision = evaluate_confirm_affordance(
        _clean_policy(availability="blocked"),
        staleness=_fresh(),
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_guardrail


# ── Block: stale ──────────────────────────────────────────────────────────────


def test_blocked_stale_when_verdict_stale():
    decision = evaluate_confirm_affordance(
        _clean_policy(),
        staleness=_stale(),
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.can_show_confirm_ui is False
    assert decision.gate == ConfirmAffordanceGate.blocked_stale


def test_blocked_stale_when_verdict_mismatched_reference_date():
    decision = evaluate_confirm_affordance(
        _clean_policy(),
        staleness=_mismatched(),
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_stale


# ── Block: advisory_only ──────────────────────────────────────────────────────


def test_blocked_advisory_only():
    decision = evaluate_confirm_affordance(
        _clean_policy(advisory_warnings_only=True),
        staleness=None,
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_advisory_only


# ── Block: model uncertain ────────────────────────────────────────────────────


def test_blocked_model_uncertain_when_must_ask_clarification():
    decision = evaluate_confirm_affordance(
        _clean_policy(must_ask_clarification=True),
        staleness=None,
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_model_uncertain


# ── Block: schedule or roster ─────────────────────────────────────────────────


def test_blocked_schedule_or_roster_when_roster_unavailable():
    decision = evaluate_confirm_affordance(
        _clean_policy(roster_unavailable=True),
        staleness=None,
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_schedule_or_roster


# ── Block: no candidates ──────────────────────────────────────────────────────


def test_blocked_no_candidates_when_search_ran_no_candidates():
    decision = evaluate_confirm_affordance(
        _clean_policy(search_ran_no_candidates=True),
        staleness=None,
        has_staged_proposal=True,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_no_candidates


# ── Block: no proposal ────────────────────────────────────────────────────────


def test_blocked_no_proposal_when_has_staged_proposal_false():
    decision = evaluate_confirm_affordance(
        _clean_policy(),
        staleness=None,
        has_staged_proposal=False,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_no_proposal


def test_blocked_no_proposal_even_when_staleness_fresh():
    decision = evaluate_confirm_affordance(
        _clean_policy(),
        staleness=_fresh(),
        has_staged_proposal=False,
    )
    assert decision.confirm_grade_allowed is False
    assert decision.gate == ConfirmAffordanceGate.blocked_no_proposal


# ── Precedence: guardrail beats stale ─────────────────────────────────────────


def test_guardrail_beats_stale_in_precedence():
    """must_block_confirmation takes precedence over stale verdict."""
    decision = evaluate_confirm_affordance(
        _clean_policy(must_block_confirmation=True),
        staleness=_stale(),
        has_staged_proposal=True,
    )
    assert decision.gate == ConfirmAffordanceGate.blocked_guardrail


def test_guardrail_beats_no_proposal():
    decision = evaluate_confirm_affordance(
        _clean_policy(must_block_confirmation=True),
        staleness=None,
        has_staged_proposal=False,
    )
    assert decision.gate == ConfirmAffordanceGate.blocked_guardrail


def test_stale_beats_advisory_only():
    """Stale verdict takes precedence over advisory_only."""
    decision = evaluate_confirm_affordance(
        _clean_policy(advisory_warnings_only=True),
        staleness=_stale(),
        has_staged_proposal=True,
    )
    assert decision.gate == ConfirmAffordanceGate.blocked_stale


def test_roster_beats_no_candidates():
    """roster_unavailable takes precedence over search_ran_no_candidates."""
    decision = evaluate_confirm_affordance(
        _clean_policy(roster_unavailable=True, search_ran_no_candidates=True),
        staleness=None,
        has_staged_proposal=True,
    )
    assert decision.gate == ConfirmAffordanceGate.blocked_schedule_or_roster


# ── Reason code passthrough ───────────────────────────────────────────────────


def test_blocking_reason_codes_passed_through_on_block():
    policy = _clean_policy(
        must_block_confirmation=True,
        reason_codes=["conflict_overlap", "outside_booking_window"],
        schedule_reason_codes=["fully_booked"],
    )
    decision = evaluate_confirm_affordance(policy, staleness=None, has_staged_proposal=True)
    assert "conflict_overlap" in decision.blocking_reason_codes
    assert "outside_booking_window" in decision.blocking_reason_codes
    assert decision.schedule_reason_codes == ["fully_booked"]


def test_schedule_reason_codes_passed_through_on_allowed():
    policy = _clean_policy(
        schedule_reason_codes=["searched_no_candidates"],
    )
    decision = evaluate_confirm_affordance(policy, staleness=None, has_staged_proposal=True)
    assert decision.confirm_grade_allowed is True
    assert decision.schedule_reason_codes == ["searched_no_candidates"]


def test_blocking_reason_codes_empty_on_allowed():
    decision = evaluate_confirm_affordance(
        _clean_policy(),
        staleness=_fresh(),
        has_staged_proposal=True,
    )
    assert decision.blocking_reason_codes == []


# ── Bernie facade parity ──────────────────────────────────────────────────────


def test_bernie_facade_exports_same_objects():
    from app.services.bernie.confirm_gate import (
        ConfirmAffordanceDecision as BDecision,
        ConfirmAffordanceGate as BGate,
        evaluate_confirm_affordance as b_eval,
    )
    assert BDecision is ConfirmAffordanceDecision
    assert BGate is ConfirmAffordanceGate
    assert b_eval is evaluate_confirm_affordance


def test_bernie_package_exports_gate_symbols():
    import app.services.bernie as bernie_domain
    assert hasattr(bernie_domain, "ConfirmAffordanceDecision")
    assert hasattr(bernie_domain, "ConfirmAffordanceGate")
    assert hasattr(bernie_domain, "evaluate_confirm_affordance")
    assert bernie_domain.ConfirmAffordanceDecision is ConfirmAffordanceDecision
    assert bernie_domain.evaluate_confirm_affordance is evaluate_confirm_affordance


def test_diary_package_exports_gate_symbols():
    import app.services.diary as diary_domain
    assert hasattr(diary_domain, "ConfirmAffordanceDecision")
    assert hasattr(diary_domain, "evaluate_confirm_affordance")
    assert diary_domain.ConfirmAffordanceDecision is ConfirmAffordanceDecision
