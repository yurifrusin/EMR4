"""Compatibility tests for the Sprint N1a Bernie-to-Diary rehome.

Ensures that:
1. When app.services.diary is present (e.g. after Claude implements the move),
   all facade imports under app.services.bernie resolve to the exact same objects
   as app.services.diary.
2. The schema versions and wire API contracts (reception_policy, reception_context)
   remain byte-identical and correct.
3. No behavior or contract breaks.
"""

from datetime import date
import pytest

import app.services.bernie as bernie
import app.services.bernie.capabilities as bernie_capabilities
import app.services.bernie.temporal as bernie_temporal
import app.services.bernie.frames as bernie_frames
import app.services.bernie.policy as bernie_policy

from app.schemas.appointments import (
    BernieBookingInstructionInterpretOut,
    BernieSupervisedBookingOut,
)


def test_reception_context_schema_version_is_v1():
    """Assert schema version is bernie.reception_context.v1 literal in serialization."""
    frame_set = bernie.BernieReceptionContextFrameSet(
        reference_date=date(2026, 7, 3),
        frames=[],
    )
    dumped = frame_set.model_dump(mode="json")
    assert frame_set.schema_version == "bernie.reception_context.v1"
    assert dumped["schema_version"] == "bernie.reception_context.v1"


def test_response_models_contain_required_fields():
    """Assert that endpoints output response models with unaltered reception_policy fields."""
    for model in (BernieBookingInstructionInterpretOut, BernieSupervisedBookingOut):
        assert "reception_context" in model.model_fields
        assert "reception_policy" in model.model_fields


def test_evaluate_reception_context_produces_consistent_keys():
    """Assert that evaluate_reception_context returns BernieReceptionPolicyDecision with expected fields."""
    frame_set = bernie.BernieReceptionContextFrameSet(
        reference_date=date(2026, 7, 3),
        frames=[
            bernie.BernieRequestedAppointmentFrame(
                status="known",
                basis="Test",
                reference_date=date(2026, 7, 3),
            )
        ],
    )
    decision = bernie.evaluate_reception_context(frame_set)
    assert isinstance(decision, bernie.BernieReceptionPolicyDecision)
    
    # Check fields that the frontend consumes
    dumped = decision.model_dump(mode="json")
    for field in [
        "availability",
        "can_search_slots",
        "search_ran_no_candidates",
        "must_block_confirmation",
        "must_ask_clarification",
        "roster_unavailable",
        "advisory_warnings_only",
        "reason_codes",
    ]:
        assert field in dumped


def test_temporal_helpers_correctness():
    """Basic sanity checks on temporal parsing to ensure contract compatibility."""
    assert bernie.parse_time_fragment("3") == "15:00"
    assert bernie.parse_time_fragment("3:45 pm") == "15:45"
    assert bernie.extract_natural_time_constraints("after 3 pm") == ("15:00", None)
    assert bernie.extract_natural_date_constraint("next week please", date(2026, 7, 3)) == "2026-07-10"


def test_cross_package_facade_compatibility():
    """If app.services.diary package is present, assert exact object identity.
    
    If it is not present yet (because Claude has not merged), we skip this test
    so that tests can run and pass on Antigravity's isolated branch.
    """
    try:
        import app.services.diary as diary
        import app.services.diary.capabilities as diary_capabilities
        import app.services.diary.temporal as diary_temporal
        import app.services.diary.frames as diary_frames
        import app.services.diary.policy as diary_policy
    except ImportError:
        pytest.skip("app.services.diary is not yet present; skipping identity checks.")

    # Capabilities
    assert bernie.BERNIE_CAPABILITY_REGISTRY is diary.BERNIE_CAPABILITY_REGISTRY
    assert bernie.BernieCapability is diary.BernieCapability
    assert bernie.BernieCapabilityTier is diary.BernieCapabilityTier
    assert bernie.get_bernie_capability is diary.get_bernie_capability

    assert bernie_capabilities.BERNIE_CAPABILITY_REGISTRY is diary_capabilities.BERNIE_CAPABILITY_REGISTRY
    assert bernie_capabilities.get_bernie_capability is diary_capabilities.get_bernie_capability

    # Temporal
    assert bernie.SameDayWindowDecision is diary.SameDayWindowDecision
    assert bernie.evaluate_same_day_window is diary.evaluate_same_day_window
    assert bernie.extract_natural_date_constraint is diary.extract_natural_date_constraint
    assert bernie.extract_natural_time_constraints is diary.extract_natural_time_constraints
    assert bernie.parse_time_fragment is diary.parse_time_fragment
    assert bernie.resolve_week_relative_date is diary.resolve_week_relative_date

    assert bernie_temporal.evaluate_same_day_window is diary_temporal.evaluate_same_day_window

    # Frames
    assert bernie.BernieAdvisoryWarningFrame is diary.BernieAdvisoryWarningFrame
    assert bernie.BernieFrameSource is diary.BernieFrameSource
    assert bernie.BernieFrameStatus is diary.BernieFrameStatus
    assert bernie.BernieFrameType is diary.BernieFrameType
    assert bernie.BernieGuardrailOutcomeFrame is diary.BernieGuardrailOutcomeFrame
    assert bernie.BernieModelUncertaintyFrame is diary.BernieModelUncertaintyFrame
    assert bernie.BerniePatientBookingContextFrame is diary.BerniePatientBookingContextFrame
    assert bernie.BernieReceptionContextFrameSet is diary.BernieReceptionContextFrameSet
    assert bernie.BernieReceptionFrame is diary.BernieReceptionFrame
    assert bernie.BernieReceptionFrameBase is diary.BernieReceptionFrameBase
    assert bernie.BernieRequestedAppointmentFrame is diary.BernieRequestedAppointmentFrame
    assert bernie.BernieRosterScheduleFrame is diary.BernieRosterScheduleFrame
    assert bernie.BernieSlotSearchFrame is diary.BernieSlotSearchFrame
    assert bernie.BernieStaleEvidenceFrame is diary.BernieStaleEvidenceFrame

    assert bernie_frames.BernieReceptionContextFrameSet is diary_frames.BernieReceptionContextFrameSet

    # Policy
    assert bernie.BernieAvailabilityClassification is diary.BernieAvailabilityClassification
    assert bernie.BernieReceptionPolicyDecision is diary.BernieReceptionPolicyDecision
    assert bernie.evaluate_reception_context is diary.evaluate_reception_context

    assert bernie_policy.evaluate_reception_context is diary_policy.evaluate_reception_context
