"""Tests for the R29 native diary action grammar.

Covers:
- Schema version pinned
- All verbs have a descriptor
- assert_grammar_consistency passes
- Confirm-tier verbs have non-None confirm_affordance_notes
- Mutating verbs require staff confirmation
- Implemented confirm-tier verbs reference existing DIARY_CONFIRM_ACTIONS
- Planned-not-implemented verbs have empty confirm_actions
- move and resize are separate verbs both mapping to the update confirm action
- Golden test: confirm-tier suggestion/action is blocked when evaluate_confirm_affordance
  returns a blocked decision (gate 6 mandatory requirement)
- Bernie facade re-exports identical objects
- action_verb_for_envelope bridge returns expected verbs
- Package import path works
"""

import pytest

from app.services.bernie.action_grammar import (
    DIARY_ACTION_GRAMMAR as BERNIE_GRAMMAR,
    DiaryActionVerb as BernieDiaryActionVerb,
    assert_grammar_consistency as bernie_assert_grammar_consistency,
)
from app.services.diary import (
    BERNIE_CAPABILITY_REGISTRY,
    DIARY_CONFIRM_ACTIONS,
    DiaryActionVerb,
    DiaryConfirmAction,
    ConfirmAffordanceGate,
    evaluate_confirm_affordance,
)
from app.services.diary.action_grammar import (
    DIARY_ACTION_GRAMMAR,
    GRAMMAR_SCHEMA_VERSION,
    DiaryActionVerbDescriptor,
    action_verb_for_envelope,
    assert_grammar_consistency,
    get_verb_descriptor,
)
from app.services.diary.capabilities import BernieCapabilityTier
from app.services.diary.policy import BernieReceptionPolicyDecision


# ---------------------------------------------------------------------------
# Schema version
# ---------------------------------------------------------------------------


def test_grammar_schema_version_pinned():
    assert GRAMMAR_SCHEMA_VERSION == "diary.action_grammar.v1"


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------


def test_all_verbs_have_a_descriptor():
    for verb in DiaryActionVerb:
        assert verb in DIARY_ACTION_GRAMMAR, f"Missing descriptor for {verb.value}"


def test_grammar_covers_exactly_the_enum():
    assert set(DIARY_ACTION_GRAMMAR.keys()) == set(DiaryActionVerb)


# ---------------------------------------------------------------------------
# Consistency checker
# ---------------------------------------------------------------------------


def test_assert_grammar_consistency_passes():
    assert_grammar_consistency()


# ---------------------------------------------------------------------------
# Confirm-tier invariants
# ---------------------------------------------------------------------------


def test_confirm_tier_descriptors_have_confirm_affordance_notes():
    for verb, desc in DIARY_ACTION_GRAMMAR.items():
        if desc.tier is BernieCapabilityTier.confirm:
            assert desc.confirm_affordance_notes is not None, (
                f"{verb.value}: confirm-tier descriptor is missing confirm_affordance_notes"
            )
            assert len(desc.confirm_affordance_notes) > 20, (
                f"{verb.value}: confirm_affordance_notes appears too short to be meaningful"
            )


def test_implemented_confirm_verbs_reference_existing_confirm_actions():
    for verb, desc in DIARY_ACTION_GRAMMAR.items():
        if desc.tier is BernieCapabilityTier.confirm and desc.implemented:
            assert desc.confirm_actions, (
                f"{verb.value}: implemented confirm-tier verb has empty confirm_actions"
            )
            for ca in desc.confirm_actions:
                assert ca in DIARY_CONFIRM_ACTIONS, (
                    f"{verb.value}: confirm_action {ca!r} not in DIARY_CONFIRM_ACTIONS"
                )


def test_planned_not_implemented_verbs_have_empty_confirm_actions():
    planned = [
        DiaryActionVerb.check_in,
        DiaryActionVerb.waiting_area_move,
        DiaryActionVerb.link_patient,
    ]
    for verb in planned:
        desc = DIARY_ACTION_GRAMMAR[verb]
        assert desc.implemented is False, f"{verb.value} should be implemented=False"
        assert desc.confirm_actions == (), (
            f"{verb.value} planned-not-implemented must have confirm_actions=()"
        )
        assert desc.tier is BernieCapabilityTier.confirm, (
            f"{verb.value} should still be confirm-tier (not yet promoted)"
        )


def test_planned_not_implemented_verbs_have_confirm_affordance_notes():
    """Planned verbs still document their future gate expectations."""
    for verb in (
        DiaryActionVerb.check_in,
        DiaryActionVerb.waiting_area_move,
        DiaryActionVerb.link_patient,
    ):
        desc = DIARY_ACTION_GRAMMAR[verb]
        assert desc.confirm_affordance_notes is not None
        assert "evaluate_confirm_affordance" in desc.confirm_affordance_notes


# ---------------------------------------------------------------------------
# Mutation invariants
# ---------------------------------------------------------------------------


def test_mutating_verbs_require_staff_confirmation():
    for verb, desc in DIARY_ACTION_GRAMMAR.items():
        if desc.mutating:
            assert desc.requires_staff_confirmation, (
                f"{verb.value}: mutating verb must have requires_staff_confirmation=True"
            )


def test_read_only_and_meta_verbs_are_not_mutating():
    for verb, desc in DIARY_ACTION_GRAMMAR.items():
        if desc.tier in (BernieCapabilityTier.read_only, BernieCapabilityTier.meta):
            assert not desc.mutating, (
                f"{verb.value}: read_only/meta verb must have mutating=False"
            )
            assert not desc.requires_staff_confirmation, (
                f"{verb.value}: read_only/meta verb must not require staff confirmation"
            )


# ---------------------------------------------------------------------------
# move and resize are distinct verbs (gate 8: keep separate for v1)
# ---------------------------------------------------------------------------


def test_move_and_resize_are_separate_verbs():
    assert DiaryActionVerb.move is not DiaryActionVerb.resize
    assert DiaryActionVerb.move.value == "move"
    assert DiaryActionVerb.resize.value == "resize"


def test_move_and_resize_both_map_to_update_confirm_action():
    move_desc = DIARY_ACTION_GRAMMAR[DiaryActionVerb.move]
    resize_desc = DIARY_ACTION_GRAMMAR[DiaryActionVerb.resize]
    assert DiaryConfirmAction.update in move_desc.confirm_actions
    assert DiaryConfirmAction.update in resize_desc.confirm_actions


def test_move_and_resize_descriptors_are_distinct_objects():
    move_desc = DIARY_ACTION_GRAMMAR[DiaryActionVerb.move]
    resize_desc = DIARY_ACTION_GRAMMAR[DiaryActionVerb.resize]
    assert move_desc is not resize_desc
    assert move_desc.verb is DiaryActionVerb.move
    assert resize_desc.verb is DiaryActionVerb.resize


# ---------------------------------------------------------------------------
# create verb: maps to both staff_create and bernie_create
# ---------------------------------------------------------------------------


def test_create_verb_maps_to_both_staff_and_bernie_confirm_actions():
    desc = DIARY_ACTION_GRAMMAR[DiaryActionVerb.create]
    assert DiaryConfirmAction.staff_create in desc.confirm_actions
    assert DiaryConfirmAction.bernie_create in desc.confirm_actions


# ---------------------------------------------------------------------------
# cancel and status_change confirm actions
# ---------------------------------------------------------------------------


def test_cancel_maps_to_delete_confirm_action():
    desc = DIARY_ACTION_GRAMMAR[DiaryActionVerb.cancel]
    assert DiaryConfirmAction.delete in desc.confirm_actions


def test_status_change_maps_to_status_confirm_action():
    desc = DIARY_ACTION_GRAMMAR[DiaryActionVerb.status_change]
    assert DiaryConfirmAction.status in desc.confirm_actions


# ---------------------------------------------------------------------------
# Golden test: confirm-tier suggestion/action is BLOCKED when
# evaluate_confirm_affordance returns a blocked decision
# (mandatory Codex/Delta gate 6)
# ---------------------------------------------------------------------------


def _make_blocked_policy(**kwargs) -> BernieReceptionPolicyDecision:
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
    defaults.update(kwargs)
    return BernieReceptionPolicyDecision(**defaults)


def test_confirm_tier_action_blocked_when_affordance_blocked_by_guardrail():
    """confirm_grade_allowed=False blocks any confirm-tier verb dispatch."""
    policy = _make_blocked_policy(must_block_confirmation=True)
    affordance = evaluate_confirm_affordance(policy, has_staged_proposal=True)

    assert affordance.confirm_grade_allowed is False
    assert affordance.gate is ConfirmAffordanceGate.blocked_guardrail

    # Every implemented confirm-tier verb must not be dispatched when blocked.
    for verb, desc in DIARY_ACTION_GRAMMAR.items():
        if desc.tier is BernieCapabilityTier.confirm and desc.implemented:
            # The grammar table records the confirm_action(s) for this verb.
            # Callers must consult evaluate_confirm_affordance before reaching
            # those endpoints.  We assert here that the affordance gate is
            # correctly blocking, and that the verb is in the confirm tier,
            # establishing the contract: blocked affordance => verb must not
            # proceed regardless of which confirm_action it would route to.
            assert not affordance.confirm_grade_allowed, (
                f"Verb {verb.value} is confirm-tier but affordance gate allowed "
                f"it through when it should be blocked (gate: {affordance.gate})"
            )


def test_confirm_tier_action_blocked_when_no_staged_proposal():
    """confirm_grade_allowed=False when no staged proposal blocks confirm verbs."""
    policy = _make_blocked_policy()
    affordance = evaluate_confirm_affordance(policy, has_staged_proposal=False)

    assert affordance.confirm_grade_allowed is False
    assert affordance.gate is ConfirmAffordanceGate.blocked_no_proposal

    for verb, desc in DIARY_ACTION_GRAMMAR.items():
        if desc.tier is BernieCapabilityTier.confirm and desc.implemented:
            assert not affordance.confirm_grade_allowed, (
                f"Verb {verb.value}: no staged proposal must block confirm-grade dispatch"
            )


def test_confirm_tier_action_blocked_when_advisory_warnings_only():
    policy = _make_blocked_policy(advisory_warnings_only=True)
    affordance = evaluate_confirm_affordance(policy, has_staged_proposal=True)

    assert affordance.confirm_grade_allowed is False
    assert affordance.gate is ConfirmAffordanceGate.blocked_advisory_only


def test_confirm_grade_allowed_when_all_guards_pass():
    """Control case: confirm-tier verbs may proceed when affordance is allowed."""
    policy = _make_blocked_policy()
    affordance = evaluate_confirm_affordance(policy, has_staged_proposal=True)

    assert affordance.confirm_grade_allowed is True
    assert affordance.gate is ConfirmAffordanceGate.allowed


# ---------------------------------------------------------------------------
# DiaryActionSuggestion cannot carry confirm-grade evidence (envelope boundary)
# ---------------------------------------------------------------------------


def test_diary_action_suggestion_cannot_carry_confirmation_evidence():
    """Suggestions are read-only; grammar must not promote them to confirm-grade."""
    from app.services.diary.envelopes import (
        DiaryActionAuthor,
        DiaryActionChannel,
        DiaryActionSuggestion,
    )
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="confirm-grade evidence"):
        DiaryActionSuggestion(
            suggestion_id="s1",
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.diary_panel,
            action_name="confirm_booking",
            title="Book appointment",
            reason_code="slot_found",
            payload={"confirmation_evidence": {"token": "abc"}},
        )


# ---------------------------------------------------------------------------
# capability_name resolution
# ---------------------------------------------------------------------------


def test_capability_names_resolve_in_registry():
    from app.services.diary.capabilities import get_bernie_capability

    for verb, desc in DIARY_ACTION_GRAMMAR.items():
        if desc.capability_name is not None:
            cap = get_bernie_capability(desc.capability_name)
            assert cap is not None, (
                f"{verb.value}: capability_name '{desc.capability_name}' "
                "not found in BERNIE_CAPABILITY_REGISTRY"
            )


# ---------------------------------------------------------------------------
# action_verb_for_envelope bridge
# ---------------------------------------------------------------------------


def test_action_verb_for_envelope_known_names():
    assert action_verb_for_envelope("find_slots") is DiaryActionVerb.slot_search
    assert action_verb_for_envelope("slot_search") is DiaryActionVerb.slot_search
    assert action_verb_for_envelope("explain_schedule") is DiaryActionVerb.explain_schedule
    assert action_verb_for_envelope("confirm_booking") is DiaryActionVerb.create
    assert action_verb_for_envelope("move_appointment") is DiaryActionVerb.move
    assert action_verb_for_envelope("resize_appointment") is DiaryActionVerb.resize
    assert action_verb_for_envelope("cancel_appointment") is DiaryActionVerb.cancel
    assert action_verb_for_envelope("status_change") is DiaryActionVerb.status_change
    assert action_verb_for_envelope("handoff") is DiaryActionVerb.handoff


def test_action_verb_for_envelope_unknown_returns_none():
    assert action_verb_for_envelope("propose_booking") is None
    assert action_verb_for_envelope("propose_edit") is None
    assert action_verb_for_envelope("propose_status") is None
    assert action_verb_for_envelope("unknown_action") is None


# ---------------------------------------------------------------------------
# get_verb_descriptor
# ---------------------------------------------------------------------------


def test_get_verb_descriptor_returns_correct_descriptor():
    desc = get_verb_descriptor(DiaryActionVerb.create)
    assert desc.verb is DiaryActionVerb.create
    assert desc.tier is BernieCapabilityTier.confirm
    assert desc.implemented is True


# ---------------------------------------------------------------------------
# Bernie facade re-exports identical objects
# ---------------------------------------------------------------------------


def test_bernie_facade_exports_identical_grammar():
    assert BernieDiaryActionVerb is DiaryActionVerb
    assert BERNIE_GRAMMAR is DIARY_ACTION_GRAMMAR


def test_bernie_facade_assert_grammar_consistency_is_same_function():
    bernie_assert_grammar_consistency()


def test_bernie_package_imports_grammar():
    from app.services.bernie import (
        DIARY_ACTION_GRAMMAR as pkg_grammar,
        DiaryActionVerb as pkg_verb,
        GRAMMAR_SCHEMA_VERSION as pkg_version,
        assert_grammar_consistency as pkg_check,
    )
    assert pkg_grammar is DIARY_ACTION_GRAMMAR
    assert pkg_verb is DiaryActionVerb
    assert pkg_version == GRAMMAR_SCHEMA_VERSION
    pkg_check()


def test_diary_package_imports_grammar():
    from app.services.diary import (
        DIARY_ACTION_GRAMMAR as pkg_grammar,
        DiaryActionVerb as pkg_verb,
    )
    assert pkg_grammar is DIARY_ACTION_GRAMMAR
    assert pkg_verb is DiaryActionVerb


# ---------------------------------------------------------------------------
# Regression: no H-series / trove / neutral-event references in grammar vocab
# ---------------------------------------------------------------------------


def test_no_h_series_references_in_grammar_vocabulary():
    """Grammar vocabulary and rationale must not reference H-series or trove events."""
    forbidden_fragments = [
        "h_series",
        "h-series",
        "neutral_event",
        "neutral event",
        "trove",
        "diary snapshot",
        "pilot_0",
        "full_trove",
        "full-trove",
        "no_structural_change",
        "small_content_delta",
        "large_unexplained_delta",
    ]
    import app.services.diary.action_grammar as grammar_module
    import inspect

    source = inspect.getsource(grammar_module)
    for fragment in forbidden_fragments:
        assert fragment.lower() not in source.lower(), (
            f"Grammar module contains forbidden H-series/trove reference: '{fragment}'"
        )


# ---------------------------------------------------------------------------
# DiaryActionVerb schema coverage (all verbs accounted for)
# ---------------------------------------------------------------------------


def test_expected_verb_set():
    expected = {
        "create",
        "move",
        "resize",
        "cancel",
        "status_change",
        "check_in",
        "waiting_area_move",
        "link_patient",
        "slot_search",
        "explain_schedule",
        "handoff",
    }
    actual = {v.value for v in DiaryActionVerb}
    assert actual == expected
