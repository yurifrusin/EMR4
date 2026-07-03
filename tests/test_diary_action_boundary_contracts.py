"""N1b boundary tests for diary action authorship and reception policy."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.services.diary import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieAdvisoryWarningFrame,
    BernieCapabilityTier,
    BernieGuardrailOutcomeFrame,
    BernieModelUncertaintyFrame,
    BernieReceptionContextFrameSet,
    BernieRosterScheduleFrame,
    BernieSlotSearchFrame,
    DiaryActionAuthor,
    DiaryActionChannel,
    DiaryActionSuggestion,
    evaluate_reception_context,
)


REFERENCE_DATE = date(2026, 7, 3)


def _frame_set(*frames):
    return BernieReceptionContextFrameSet(
        reference_date=REFERENCE_DATE,
        frames=list(frames),
    )


def test_every_catalog_entry_declares_authorship_policy():
    assert BERNIE_CAPABILITY_REGISTRY

    for capability in BERNIE_CAPABILITY_REGISTRY:
        assert capability.allowed_authors
        assert all(isinstance(author, DiaryActionAuthor) for author in capability.allowed_authors)

        if capability.tier in {BernieCapabilityTier.propose, BernieCapabilityTier.confirm}:
            assert capability.requires_staff_confirmation is True

        if capability.tier == BernieCapabilityTier.confirm:
            assert capability.allowed_authors == (DiaryActionAuthor.staff_ui,)


def test_suggest_next_actions_is_multi_author_read_only():
    capability = next(
        capability
        for capability in BERNIE_CAPABILITY_REGISTRY
        if capability.name == "suggest_next_actions"
    )

    assert capability.tier == BernieCapabilityTier.read_only
    assert capability.requires_staff_confirmation is False
    assert set(capability.allowed_authors) == {
        DiaryActionAuthor.staff_ui,
        DiaryActionAuthor.bernie,
        DiaryActionAuthor.rayleen,
        DiaryActionAuthor.davida,
        DiaryActionAuthor.system,
    }


def test_advisory_warning_cannot_fabricate_availability_or_block_confirmation():
    decision = evaluate_reception_context(
        _frame_set(
            BernieAdvisoryWarningFrame(
                basis="A retrieved or advisory fact claimed no appointments exist.",
                reference_date=REFERENCE_DATE,
                reason_code="retrieved_claimed_no_slots",
            )
        )
    )

    assert decision.availability == "not_evaluated"
    assert decision.search_ran_no_candidates is False
    assert decision.roster_unavailable is False
    assert decision.can_offer_candidates is False
    assert decision.must_block_confirmation is False
    assert decision.advisory_warnings_only is True


def test_model_uncertainty_cannot_fabricate_availability_or_offer_candidates():
    decision = evaluate_reception_context(
        _frame_set(
            BernieModelUncertaintyFrame(
                status="proceed_with_check",
                basis="The model guessed that tomorrow might be full.",
                reference_date=REFERENCE_DATE,
                reason_code="model_guess_only",
            )
        )
    )

    assert decision.availability == "not_evaluated"
    assert decision.search_ran_no_candidates is False
    assert decision.roster_unavailable is False
    assert decision.can_offer_candidates is False
    assert decision.must_block_confirmation is False


def test_type_layer_rejects_model_sourced_slot_or_roster_truth():
    with pytest.raises(ValidationError):
        BernieSlotSearchFrame(
            status="searched_no_candidates",
            source="model",
            basis="The model guessed there are no slots.",
            reference_date=REFERENCE_DATE,
            candidate_count=0,
        )

    with pytest.raises(ValidationError):
        BernieRosterScheduleFrame(
            status="unavailable",
            source="model",
            basis="The model guessed the practitioner is not rostered.",
            reference_date=REFERENCE_DATE,
        )


def test_advisory_frames_do_not_unblock_hard_guardrails():
    decision = evaluate_reception_context(
        _frame_set(
            BernieGuardrailOutcomeFrame(
                status="blocked",
                basis="Confirmation evidence is stale.",
                reference_date=REFERENCE_DATE,
                reason_code="stale_confirmation_evidence",
            ),
            BernieAdvisoryWarningFrame(
                basis="Advisory fact says the action sounds reasonable.",
                reference_date=REFERENCE_DATE,
                reason_code="advisory_only",
            ),
        )
    )

    assert decision.availability == "blocked"
    assert decision.must_block_confirmation is True
    assert decision.advisory_warnings_only is False


def test_suggestion_is_conversation_input_not_mutation_authority():
    suggestion = DiaryActionSuggestion(
        suggestion_id="suggestion-1",
        author=DiaryActionAuthor.staff_ui,
        channel=DiaryActionChannel.nl_text,
        action_name="suggest_next_actions",
        title="Try tomorrow morning",
        reason_code="try_alternative_day",
        payload={"intent_hint": {"action_name": "find_slots"}},
    )

    assert suggestion.writes_authorized is False
    assert suggestion.requires_staff_confirmation is False

    with pytest.raises(ValidationError):
        DiaryActionSuggestion(
            suggestion_id="suggestion-2",
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.agent_policy,
            action_name="suggest_next_actions",
            title="Book this",
            reason_code="unsafe",
            payload={"nested": {"proposal_freshness_id": "f" * 32}},
        )

