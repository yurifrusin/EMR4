"""Tests for internal diary action envelope contracts."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.services.diary import (
    DiaryActionAuthor,
    DiaryActionChannel,
    DiaryActionConfirmation,
    DiaryActionIntent,
    DiaryActionProposal,
    DiaryActionSuggestion,
)


def test_diary_action_intent_round_trips_through_json():
    intent = DiaryActionIntent(
        intent_id="intent-1",
        author=DiaryActionAuthor.bernie,
        channel=DiaryActionChannel.diary_panel,
        action_name="find_slots",
        payload={"date_from": "2026-07-03", "duration_minutes": 15},
        turn_ref="turn-1",
        summary="Find a short appointment today.",
    )

    restored = DiaryActionIntent.model_validate_json(intent.model_dump_json())

    assert restored == intent
    assert restored.schema_version == "diary.action.intent.v1"
    assert restored.writes_authorized is False


def test_diary_action_proposal_round_trips_through_json():
    proposal = DiaryActionProposal(
        proposal_id="proposal-1",
        intent_id="intent-1",
        author=DiaryActionAuthor.bernie,
        channel=DiaryActionChannel.diary_panel,
        action_name="propose_booking",
        payload={"candidate_index": 0},
        evidence_refs=["slot-search:abc123"],
        review_reasons=["staff_review_required"],
    )

    restored = DiaryActionProposal.model_validate_json(proposal.model_dump_json())

    assert restored == proposal
    assert restored.schema_version == "diary.action.proposal.v1"
    assert restored.requires_staff_confirmation is True
    assert restored.writes_authorized is False


def test_diary_action_confirmation_round_trips_through_json():
    confirmed_at = datetime(2026, 7, 3, 9, 30, tzinfo=timezone.utc)
    confirmation = DiaryActionConfirmation(
        confirmation_id="confirmation-1",
        proposal_id="proposal-1",
        confirmed_by_user_id="user-1",
        confirmed_at=confirmed_at,
        author=DiaryActionAuthor.staff_ui,
        channel=DiaryActionChannel.diary_panel,
        action_name="confirm_booking",
        payload={"appointment_id": "pending"},
        confirmation_evidence={"proposal_freshness_id": "f" * 32},
        audit_evidence=["bernie_confirm_create_proposal"],
    )

    restored = DiaryActionConfirmation.model_validate_json(confirmation.model_dump_json())

    assert restored == confirmation
    assert restored.schema_version == "diary.action.confirmation.v1"
    assert restored.staff_confirmed is True
    assert restored.writes_authorized is True


def test_diary_action_suggestion_round_trips_as_read_only_json():
    suggestion = DiaryActionSuggestion(
        suggestion_id="suggestion-1",
        author=DiaryActionAuthor.bernie,
        channel=DiaryActionChannel.diary_panel,
        action_name="suggest_next_actions",
        title="Try tomorrow morning",
        reason_code="same_day_exhausted",
        payload={"next_search": {"date_from": "2026-07-04"}},
    )

    restored = DiaryActionSuggestion.model_validate_json(suggestion.model_dump_json())

    assert restored == suggestion
    assert restored.schema_version == "diary.action.suggestion.v1"
    assert restored.requires_staff_confirmation is False
    assert restored.writes_authorized is False


@pytest.mark.parametrize(
    "field_name, field_value",
    [
        ("audit_evidence", ["bernie_confirm_create_proposal"]),
        ("confirmation_evidence", {"proposal_freshness_id": "f" * 32}),
        ("confirmed_by_user_id", "user-1"),
        ("staff_confirmed", True),
    ],
)
def test_suggestion_rejects_confirm_grade_top_level_fields(field_name, field_value):
    body = {
        "suggestion_id": "suggestion-1",
        "author": "bernie",
        "channel": "diary_panel",
        "action_name": "suggest_next_actions",
        "title": "Try another day",
        "reason_code": "no_slots",
        field_name: field_value,
    }

    with pytest.raises(ValidationError):
        DiaryActionSuggestion.model_validate(body)


@pytest.mark.parametrize(
    "payload",
    [
        {"audit_evidence": ["bernie_confirm_create_proposal"]},
        {"nested": {"confirmation_evidence": {"proposal_freshness_id": "f" * 32}}},
        {"options": [{"candidate_freshness_ids": ["a" * 32]}]},
    ],
)
def test_suggestion_payload_cannot_smuggle_confirm_grade_evidence(payload):
    with pytest.raises(ValidationError):
        DiaryActionSuggestion(
            suggestion_id="suggestion-1",
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.diary_panel,
            action_name="suggest_next_actions",
            title="Try another day",
            reason_code="no_slots",
            payload=payload,
        )


def test_suggestion_cannot_claim_write_authority():
    with pytest.raises(ValidationError):
        DiaryActionSuggestion(
            suggestion_id="suggestion-1",
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.diary_panel,
            action_name="suggest_next_actions",
            title="Try another day",
            reason_code="no_slots",
            writes_authorized=True,
        )


def test_other_envelopes_enforce_write_and_confirm_boundaries():
    with pytest.raises(ValidationError):
        DiaryActionIntent(
            intent_id="intent-1",
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.diary_panel,
            action_name="find_slots",
            writes_authorized=True,
        )

    with pytest.raises(ValidationError):
        DiaryActionProposal(
            proposal_id="proposal-1",
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.diary_panel,
            action_name="propose_booking",
            writes_authorized=True,
        )

    with pytest.raises(ValidationError):
        DiaryActionProposal(
            proposal_id="proposal-1",
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.diary_panel,
            action_name="propose_booking",
            requires_staff_confirmation=False,
        )

    confirmed_at = datetime(2026, 7, 3, 9, 30, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        DiaryActionConfirmation(
            confirmation_id="confirmation-1",
            proposal_id="proposal-1",
            confirmed_by_user_id="user-1",
            confirmed_at=confirmed_at,
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="confirm_booking",
            writes_authorized=False,
        )

    with pytest.raises(ValidationError):
        DiaryActionConfirmation(
            confirmation_id="confirmation-1",
            proposal_id="proposal-1",
            confirmed_by_user_id="user-1",
            confirmed_at=confirmed_at,
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="confirm_booking",
            staff_confirmed=False,
        )
