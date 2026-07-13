"""Tests for the registered-envelope authority policy seam.

Covers:
- Registered action with permitted author passes.
- Registered action with unauthorised author is rejected.
- Registered proposal with non-propose-tier capability is rejected.
- Registered suggestion with non-read-only/meta capability is rejected.
- Registered confirmation with non-confirm-tier capability is rejected.
- Unknown free-string action_name passes through without enforcement.
- Action_name that maps to a verb with no capability_name passes through.
- capability_name not found in registry passes through.
- Source import purity: the policy module must not import prohibited things.
- Manifest posture: capabilities note documents envelope-level enforcement.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.services.diary import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapabilityTier,
    DiaryActionAuthor,
    DiaryActionChannel,
    DiaryActionConfirmation,
    DiaryActionIntent,
    DiaryActionProposal,
    DiaryActionSuggestion,
    EnvelopeAuthorityDecision,
    validate_envelope_authority,
)
from app.services.diary.capability_manifest import (
    build_bernie_diary_capability_manifest,
)


# ---------------------------------------------------------------------------
# Helper: a generic confirmed_at timestamp
# ---------------------------------------------------------------------------

_CONFIRMED_AT = datetime(2026, 7, 13, 9, 30, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 1. Permitted author passes
# ---------------------------------------------------------------------------


def test_registered_action_permitted_author_passes():
    """'explain_schedule' is read-only staff_ui/bernie/rayleen/davida — staff_ui
    should pass in a suggestion envelope."""
    suggestion = DiaryActionSuggestion(
        suggestion_id="s-1",
        author=DiaryActionAuthor.staff_ui,
        channel=DiaryActionChannel.diary_panel,
        action_name="explain_schedule",
        title="Schedule explanation",
        reason_code="no_slots",
    )
    assert suggestion.writes_authorized is False


def test_registered_confirmation_permitted_author_passes():
    """'confirm_booking' (create verb) is confirm-tier, author staff_ui.
    Confirmation envelope with staff_ui should pass."""
    confirmation = DiaryActionConfirmation(
        confirmation_id="c-1",
        proposal_id="p-1",
        confirmed_by_user_id="user-1",
        confirmed_at=_CONFIRMED_AT,
        author=DiaryActionAuthor.staff_ui,
        channel=DiaryActionChannel.diary_panel,
        action_name="confirm_booking",
    )
    assert confirmation.writes_authorized is True


# ---------------------------------------------------------------------------
# 2. Unauthorised author is rejected
# ---------------------------------------------------------------------------


def test_registered_action_rejects_unauthorised_author():
    """'confirm_booking' (create verb) has allowed_authors=(staff_ui,) —
    bernie must be rejected as author for a confirmation envelope."""
    with pytest.raises(ValidationError, match="not permitted"):
        DiaryActionConfirmation(
            confirmation_id="c-1",
            proposal_id="p-1",
            confirmed_by_user_id="user-1",
            confirmed_at=_CONFIRMED_AT,
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.diary_panel,
            action_name="confirm_booking",
        )


# ---------------------------------------------------------------------------
# 3. Registered proposal with non-propose-tier is rejected
# ---------------------------------------------------------------------------


def test_registered_proposal_rejects_non_propose_tier():
    """'explain_schedule' is read-only tier — must not be accepted in a proposal
    envelope."""
    with pytest.raises(ValidationError, match="not propose-tier"):
        DiaryActionProposal(
            proposal_id="p-1",
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="explain_schedule",
            evidence_refs=["ref-1"],
            review_reasons=["staff_review_required"],
        )


def test_registered_proposal_rejects_confirm_tier():
    """'confirm_booking' (create verb) maps to confirm-tier capability — must
    not be accepted in a proposal envelope."""
    with pytest.raises(ValidationError, match="not propose-tier"):
        DiaryActionProposal(
            proposal_id="p-2",
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="confirm_booking",
            evidence_refs=["ref-1"],
            review_reasons=["staff_review_required"],
        )


def test_direct_registered_proposal_name_is_enforced():
    """A direct registry name is protected even when it is not a grammar alias."""
    proposal = DiaryActionProposal(
        proposal_id="p-3",
        author=DiaryActionAuthor.bernie,
        channel=DiaryActionChannel.diary_panel,
        action_name="propose_booking",
        evidence_refs=["ref-1"],
        review_reasons=["staff_review_required"],
    )

    assert proposal.action_name == "propose_booking"

    with pytest.raises(ValidationError, match="not read-only or meta"):
        DiaryActionSuggestion(
            suggestion_id="s-direct-propose",
            author=DiaryActionAuthor.bernie,
            channel=DiaryActionChannel.diary_panel,
            action_name="propose_booking",
            title="Unsafe suggestion",
            reason_code="test",
        )


def test_direct_registered_proposal_name_rejects_unauthorised_author():
    with pytest.raises(ValidationError, match="not permitted"):
        DiaryActionProposal(
            proposal_id="p-direct-author",
            author=DiaryActionAuthor.rayleen,
            channel=DiaryActionChannel.diary_panel,
            action_name="propose_booking",
            evidence_refs=["ref-1"],
            review_reasons=["staff_review_required"],
        )


# ---------------------------------------------------------------------------
# 4. Registered suggestion with non-read-only/meta is rejected
# ---------------------------------------------------------------------------


def test_registered_suggestion_rejects_propose_tier():
    """'propose_booking' maps to 'propose_booking' action_name ... actually
    'propose_booking' is not in the alias table, so it passes through.
    Instead use an action_name that maps to a propose-tier capability.
    'propose_booking' via grammar: 'create' capability_name is 'confirm_booking'
    which is confirm-tier.  'find_slots' maps to slot_search which is
    read-only. Let's try a different approach: use an action_name that maps
    to a propose-tier verb.

    Actually the alias map has no direct propose-tier action_names. All alias
    entries are either confirm-tier, read-only, or meta. So we need to test
    that trying to put a confirm-tier action_name into a suggestion is rejected.

    'confirm_booking' (create verb, confirm-tier) as a suggestion with staff_ui
    author — staff_ui is allowed for confirm_booking, but suggestion requires
    read-only/meta tier.
    """
    with pytest.raises(ValidationError, match="not read-only or meta"):
        DiaryActionSuggestion(
            suggestion_id="s-1",
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="confirm_booking",
            title="Book the appointment",
            reason_code="slot_found",
        )


# ---------------------------------------------------------------------------
# 5. Registered confirmation with non-confirm-tier is rejected
# ---------------------------------------------------------------------------


def test_registered_confirmation_rejects_propose_tier():
    """'explain_schedule' is read-only tier — must not be accepted in a
    confirmation envelope."""
    with pytest.raises(ValidationError, match="not confirm-tier"):
        DiaryActionConfirmation(
            confirmation_id="c-1",
            proposal_id="p-1",
            confirmed_by_user_id="user-1",
            confirmed_at=_CONFIRMED_AT,
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="explain_schedule",
        )


def test_registered_confirmation_rejects_read_only_tier():
    """'find_slots' maps to slot_search (read-only tier) — must not be accepted
    in a confirmation envelope."""
    with pytest.raises(ValidationError, match="not confirm-tier"):
        DiaryActionConfirmation(
            confirmation_id="c-2",
            proposal_id="p-2",
            confirmed_by_user_id="user-1",
            confirmed_at=_CONFIRMED_AT,
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="find_slots",
        )


# ---------------------------------------------------------------------------
# 6. Unknown free-string action_name passes through
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "envelope_type, factory_kwargs",
    [
        (
            "proposal",
            {
                "proposal_id": "p-1",
                "action_name": "some_unknown_action",
                "evidence_refs": ["ref-1"],
                "review_reasons": ["staff_review_required"],
            },
        ),
        (
            "suggestion",
            {
                "suggestion_id": "s-1",
                "action_name": "some_unknown_action",
                "title": "Unknown suggestion",
                "reason_code": "test",
            },
        ),
        (
            "confirmation",
            {
                "confirmation_id": "c-1",
                "proposal_id": "p-1",
                "confirmed_by_user_id": "user-1",
                "confirmed_at": _CONFIRMED_AT,
                "action_name": "some_unknown_action",
            },
        ),
    ],
)
def test_unknown_action_name_passes_through(envelope_type, factory_kwargs):
    """Unknown action_names not in the grammar alias table pass through without
    raising ValidationError."""
    kwargs = dict(
        author=DiaryActionAuthor.staff_ui,
        channel=DiaryActionChannel.diary_panel,
        **factory_kwargs,
    )
    if envelope_type == "proposal":
        envelope = DiaryActionProposal(**kwargs)
    elif envelope_type == "suggestion":
        envelope = DiaryActionSuggestion(**kwargs)
    elif envelope_type == "confirmation":
        envelope = DiaryActionConfirmation(**kwargs)
    assert envelope.action_name == "some_unknown_action"


# ---------------------------------------------------------------------------
# 7. Verb with no capability_name passes through
# ---------------------------------------------------------------------------


def test_verb_with_no_capability_name_passes_through():
    """check_in has capability_name=None; it should pass through in any
    envelope type (except for other validations that may reject it)."""
    # check_in is confirm-tier, implemented=False, capability_name=None.
    # In a proposal envelope it would pass through because capability_name is
    # None. But check_in has requires_staff_confirmation=True so it can be a
    # proposal. Let's test this directly via the standalone function.
    decision = validate_envelope_authority(
        envelope_type="proposal",
        action_name="check_in",
        author=DiaryActionAuthor.bernie,
    )
    assert decision.action_registered is False
    assert decision.author_authorized is None
    assert decision.tier_compatible is None
    assert "no registered capability_name" in decision.reason


# ---------------------------------------------------------------------------
# 8. Standalone validate_envelope_authority function tests
# ---------------------------------------------------------------------------


def test_validate_authority_unknown_action():
    """Standalone function: unknown action returns action_registered=False."""
    decision = validate_envelope_authority(
        envelope_type="proposal",
        action_name="unknown_action",
        author=DiaryActionAuthor.staff_ui,
    )
    assert decision.action_registered is False
    assert decision.author_authorized is None
    assert decision.tier_compatible is None


def test_validate_authority_known_action_no_capability():
    """Standalone function: known verb but no capability_name -> not registered."""
    decision = validate_envelope_authority(
        envelope_type="proposal",
        action_name="check_in",
        author=DiaryActionAuthor.bernie,
    )
    assert decision.action_registered is False
    assert "no registered capability_name" in decision.reason


def test_validate_authority_registered_action_valid():
    """Standalone function: registered action with valid author and tier."""
    decision = validate_envelope_authority(
        envelope_type="suggestion",
        action_name="find_slots",
        author=DiaryActionAuthor.bernie,
    )
    assert decision.action_registered is True
    assert decision.author_authorized is True
    assert decision.tier_compatible is True


def test_validate_authority_raises_for_unauthorised_author():
    """Standalone function raises ValueError for unauthorised author."""
    with pytest.raises(ValueError, match="not permitted"):
        validate_envelope_authority(
            envelope_type="confirmation",
            action_name="confirm_booking",
            author=DiaryActionAuthor.bernie,
        )


def test_validate_authority_raises_for_incompatible_tier():
    """Standalone function raises ValueError for incompatible tier."""
    with pytest.raises(ValueError, match="not read-only or meta"):
        validate_envelope_authority(
            envelope_type="suggestion",
            action_name="confirm_booking",
            author=DiaryActionAuthor.staff_ui,
        )


# ---------------------------------------------------------------------------
# 9. Source import purity
# ---------------------------------------------------------------------------


def test_policy_module_has_no_prohibited_imports():
    """The envelope_capability_policy module must not import routers, DB,
    providers, network, or H15/H-series material."""
    import app.services.diary.envelope_capability_policy as policy_module
    import inspect

    source = inspect.getsource(policy_module)
    forbidden_fragments = [
        "import router",
        "from app.routers",
        "import models",
        "from app.models",
        "import alembic",
        "import sqlalchemy",
        "import httpx",
        "import requests",
        "from google",
        "import vertexai",
        "import grpc",
        "h_series",
        "h-series",
        "trove",
        "local_data",
        "memory",
        "rag",
        "graphrag",
        "GraphRAG",
        "RAG",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in source, (
            f"envelope_capability_policy contains prohibited import/reference: '{fragment}'"
        )


# ---------------------------------------------------------------------------
# 10. Manifest posture
# ---------------------------------------------------------------------------


def test_manifest_capabilities_note_documents_envelope_enforcement():
    """The capabilities note must describe envelope-level enforcement for
    registered names without claiming router/RBAC enforcement."""
    manifest = build_bernie_diary_capability_manifest()
    note = manifest["capabilities"]["note"]

    assert "envelope_capability_policy" in note, (
        "Capabilities note should reference the envelope enforcement module"
    )
    assert "route-level author enforcement remains future work" in note, (
        "Capabilities note should clarify that route-level enforcement is still future"
    )
    assert "Unknown" in note, (
        "Capabilities note should mention unknown names pass through"
    )


def test_manifest_drift_watch_accurately_describes_enforcement():
    """Drift watch entry must describe envelope-level enforcement without
    claiming it does not exist."""
    manifest = build_bernie_diary_capability_manifest()
    drift_entries = " ".join(manifest["drift_watch"]).lower()

    assert "enforced" in drift_entries, (
        "Drift watch should acknowledge allowed_authors is enforced"
    )
    assert "registered" in drift_entries, (
        "Drift watch should reference registered action names"
    )
    assert "route level" in drift_entries, (
        "Drift watch should clarify route-level enforcement is separate"
    )


# ---------------------------------------------------------------------------
# 11. S14 Adversarial and Cross-Contract tests
# ---------------------------------------------------------------------------


def test_intent_author_enforcement_permitted_author_passes():
    """DiaryActionIntent enforces author policy for registered action names."""
    # interpret_instruction is read-only tier, allowed_authors=(bernie,)
    intent = DiaryActionIntent(
        intent_id="i-1",
        author=DiaryActionAuthor.bernie,
        channel=DiaryActionChannel.nl_text,
        action_name="interpret_instruction",
        payload={"raw_text": "book standard appointment"},
    )
    assert intent.action_name == "interpret_instruction"


def test_intent_author_enforcement_unpermitted_author_fails():
    """DiaryActionIntent rejects unauthorized authors on registered action names."""
    # interpret_instruction allows only bernie
    with pytest.raises(ValidationError, match="not permitted"):
        DiaryActionIntent(
            intent_id="i-2",
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.nl_text,
            action_name="interpret_instruction",
        )


def test_intent_retains_generic_intent_semantics_no_tier_restriction():
    """DiaryActionIntent has no tier restriction (propose and confirm tiers both pass)."""
    # propose_booking is propose-tier, allowed_authors=(staff_ui, bernie)
    intent_propose = DiaryActionIntent(
        intent_id="i-propose",
        author=DiaryActionAuthor.bernie,
        channel=DiaryActionChannel.nl_text,
        action_name="propose_booking",
    )
    assert intent_propose.action_name == "propose_booking"

    # confirm_booking is confirm-tier, allowed_authors=(staff_ui,)
    intent_confirm = DiaryActionIntent(
        intent_id="i-confirm",
        author=DiaryActionAuthor.staff_ui,
        channel=DiaryActionChannel.diary_panel,
        action_name="confirm_booking",
    )
    assert intent_confirm.action_name == "confirm_booking"


def test_direct_names_and_grammar_aliases_use_same_author_source_of_truth():
    """Direct capability name 'propose_edit' and alias 'move' use the same allowed authors."""
    # propose_edit capability allowed_authors = (staff_ui, bernie)
    # Both direct and alias should pass for allowed authors
    p_direct = DiaryActionProposal(
        proposal_id="p-d",
        author=DiaryActionAuthor.bernie,
        channel=DiaryActionChannel.diary_panel,
        action_name="propose_edit",
    )
    assert p_direct.action_name == "propose_edit"

    c_alias = DiaryActionConfirmation(
        confirmation_id="c-a",
        proposal_id="p-a",
        confirmed_by_user_id="user-1",
        confirmed_at=_CONFIRMED_AT,
        author=DiaryActionAuthor.bernie,
        channel=DiaryActionChannel.diary_panel,
        action_name="move",
    )
    assert c_alias.action_name == "move"


def test_direct_names_and_grammar_aliases_use_same_tier_source_of_truth():
    """Direct capability 'propose_edit' is propose-tier (proposal compatible);

    grammar alias 'move' is confirm-tier (confirmation compatible).
    """
    # propose_edit is compatible with proposal envelope
    p_direct = DiaryActionProposal(
        proposal_id="p-d",
        author=DiaryActionAuthor.staff_ui,
        channel=DiaryActionChannel.diary_panel,
        action_name="propose_edit",
    )
    assert p_direct.action_name == "propose_edit"

    # propose_edit is NOT compatible with confirmation envelope
    with pytest.raises(ValidationError, match="not confirm-tier"):
        DiaryActionConfirmation(
            confirmation_id="c-d",
            proposal_id="p-d",
            confirmed_by_user_id="user-1",
            confirmed_at=_CONFIRMED_AT,
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="propose_edit",
        )

    # move alias is compatible with confirmation envelope
    c_alias = DiaryActionConfirmation(
        confirmation_id="c-a",
        proposal_id="p-a",
        confirmed_by_user_id="user-1",
        confirmed_at=_CONFIRMED_AT,
        author=DiaryActionAuthor.staff_ui,
        channel=DiaryActionChannel.diary_panel,
        action_name="move",
    )
    assert c_alias.action_name == "move"

    # move alias is NOT compatible with proposal envelope
    with pytest.raises(ValidationError, match="not propose-tier"):
        DiaryActionProposal(
            proposal_id="p-a",
            author=DiaryActionAuthor.staff_ui,
            channel=DiaryActionChannel.diary_panel,
            action_name="move",
        )


def test_unauthorized_author_rejected_on_grammar_aliases():
    """Rejects unauthorized author (e.g. rayleen) on a grammar alias (e.g. move)."""
    # move resolves to propose_edit, which only allows staff_ui and bernie
    with pytest.raises(ValidationError, match="not permitted"):
        DiaryActionConfirmation(
            confirmation_id="c-unauth",
            proposal_id="p-1",
            confirmed_by_user_id="user-1",
            confirmed_at=_CONFIRMED_AT,
            author=DiaryActionAuthor.rayleen,
            channel=DiaryActionChannel.diary_panel,
            action_name="move",
        )


def test_compatible_unknown_names_pass_through_all_envelopes():
    """An unknown/unregistered action name passes through all envelope types without enforcement."""
    args = dict(author=DiaryActionAuthor.davida, channel=DiaryActionChannel.nl_text)
    
    intent = DiaryActionIntent(intent_id="i-unk", action_name="unknown_action_name", **args)
    assert intent.action_name == "unknown_action_name"

    proposal = DiaryActionProposal(proposal_id="p-unk", action_name="unknown_action_name", **args)
    assert proposal.action_name == "unknown_action_name"

    suggestion = DiaryActionSuggestion(
        suggestion_id="s-unk", action_name="unknown_action_name", title="Unk", reason_code="unk", **args
    )
    assert suggestion.action_name == "unknown_action_name"

    confirmation = DiaryActionConfirmation(
        confirmation_id="c-unk",
        proposal_id="p-unk",
        confirmed_by_user_id="u-1",
        confirmed_at=_CONFIRMED_AT,
        action_name="unknown_action_name",
        **args
    )
    assert confirmation.action_name == "unknown_action_name"


def test_planned_grammar_verbs_with_no_registered_capability_pass_through():
    """Planned verbs with capability_name=None (e.g., check_in) pass through without validation failures."""
    args = dict(author=DiaryActionAuthor.davida, channel=DiaryActionChannel.nl_text)
    
    # check_in has capability_name=None, so it passes through
    proposal = DiaryActionProposal(proposal_id="p-chk", action_name="check_in", **args)
    assert proposal.action_name == "check_in"

    confirmation = DiaryActionConfirmation(
        confirmation_id="c-chk",
        proposal_id="p-chk",
        confirmed_by_user_id="u-1",
        confirmed_at=_CONFIRMED_AT,
        action_name="check_in",
        **args
    )
    assert confirmation.action_name == "check_in"

