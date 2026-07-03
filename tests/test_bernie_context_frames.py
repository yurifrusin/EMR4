from datetime import date

import app.services.bernie as bernie
from app.services.bernie import (
    BernieAdvisoryWarningFrame,
    BernieGuardrailOutcomeFrame,
    BernieModelUncertaintyFrame,
    BernieReceptionContextFrameSet,
    BernieRequestedAppointmentFrame,
    BernieRosterScheduleFrame,
    BernieSlotSearchFrame,
    BernieStaleEvidenceFrame,
    evaluate_reception_context,
)


REFERENCE_DATE = date(2026, 7, 3)


def frame_set(*frames):
    return BernieReceptionContextFrameSet(
        reference_date=REFERENCE_DATE,
        frames=list(frames),
    )


def test_frame_set_round_trips_typed_discriminated_frames():
    context = frame_set(
        BernieRequestedAppointmentFrame(
            status="known",
            basis="Instruction included patient, practitioner, date, and time window.",
            reference_date=REFERENCE_DATE,
            payload={"patient_label": "Margaret Thompson", "date_from": "2026-07-04"},
        ),
        BernieSlotSearchFrame(
            status="searched_with_candidates",
            basis="Slot search ran and returned candidates.",
            reference_date=REFERENCE_DATE,
            candidate_count=2,
        ),
    )

    restored = BernieReceptionContextFrameSet.model_validate_json(
        context.model_dump_json()
    )

    assert restored == context
    assert restored.schema_version == "bernie.reception_context.v1"
    assert restored.first_frame("requested_appointment").status == "known"
    assert restored.first_frame("slot_search").candidate_count == 2


def test_domain_package_exports_context_frame_contract():
    assert bernie.BernieReceptionContextFrameSet is BernieReceptionContextFrameSet
    assert bernie.BernieSlotSearchFrame is BernieSlotSearchFrame
    assert bernie.evaluate_reception_context is evaluate_reception_context


def test_future_booking_advisory_does_not_block_search_or_create_no_slot():
    context = frame_set(
        BernieRequestedAppointmentFrame(
            status="known",
            basis="Instruction has enough detail to search.",
            reference_date=REFERENCE_DATE,
        ),
        BernieAdvisoryWarningFrame(
            reason_code="existing_future_follow_up",
            basis="Patient has another future booking.",
            reference_date=REFERENCE_DATE,
            source="patient_context",
        ),
    )

    decision = evaluate_reception_context(context)

    assert decision.availability == "not_evaluated"
    assert decision.can_search_slots
    assert not decision.search_ran_no_candidates
    assert not decision.must_block_confirmation
    assert decision.advisory_warnings_only
    assert decision.reason_codes == ["existing_future_follow_up"]


def test_advisory_warning_with_candidates_is_not_advisory_only():
    context = frame_set(
        BernieRequestedAppointmentFrame(
            status="known",
            basis="Instruction has enough detail to search.",
            reference_date=REFERENCE_DATE,
        ),
        BernieAdvisoryWarningFrame(
            reason_code="practice_knowledge_retrieval",
            basis="practice_knowledge_retrieval",
            reference_date=REFERENCE_DATE,
        ),
        BernieSlotSearchFrame(
            status="searched_with_candidates",
            reason_code="slot_candidates_found",
            basis="Slot search ran and returned candidates.",
            reference_date=REFERENCE_DATE,
            candidate_count=2,
        ),
    )

    decision = evaluate_reception_context(context)

    assert decision.availability == "search_ran_with_candidates"
    assert decision.can_offer_candidates
    assert decision.can_prepare_proposal
    assert not decision.advisory_warnings_only


def test_roster_unavailable_is_not_true_no_slot():
    context = frame_set(
        BernieRequestedAppointmentFrame(
            status="known",
            basis="Instruction has enough detail to search.",
            reference_date=REFERENCE_DATE,
        ),
        BernieRosterScheduleFrame(
            status="unavailable",
            reason_code="practitioner_not_rostered",
            basis="Practitioner is not rostered on the requested day.",
            reference_date=REFERENCE_DATE,
        ),
    )

    decision = evaluate_reception_context(context)

    assert decision.availability == "roster_unavailable"
    assert decision.roster_unavailable
    assert not decision.search_ran_no_candidates
    assert not decision.can_search_slots


def test_true_no_slot_requires_search_ran_no_candidates_frame():
    context = frame_set(
        BernieRequestedAppointmentFrame(
            status="known",
            basis="Instruction has enough detail to search.",
            reference_date=REFERENCE_DATE,
        ),
        BernieRosterScheduleFrame(
            status="available",
            basis="Practitioner has a schedule on the requested day.",
            reference_date=REFERENCE_DATE,
        ),
        BernieSlotSearchFrame(
            status="searched_no_candidates",
            reason_code="no_slot_candidates",
            basis="Slot search ran against an available roster window and found no candidates.",
            reference_date=REFERENCE_DATE,
            candidate_count=0,
        ),
    )

    decision = evaluate_reception_context(context)

    assert decision.availability == "search_ran_no_candidates"
    assert decision.search_ran_no_candidates
    assert "no_slot_candidates" in decision.reason_codes


def test_model_uncertainty_requires_clarification_not_no_slot():
    context = frame_set(
        BernieRequestedAppointmentFrame(
            status="partial",
            basis="Instruction is missing a date.",
            reference_date=REFERENCE_DATE,
            reason_code="date_missing",
        ),
        BernieModelUncertaintyFrame(
            status="ask",
            reason_code="temporal_unclear",
            basis="Model could not safely resolve the requested date.",
            reference_date=REFERENCE_DATE,
        ),
    )

    decision = evaluate_reception_context(context)

    assert decision.must_ask_clarification
    assert decision.availability == "not_evaluated"
    assert not decision.search_ran_no_candidates
    assert not decision.can_search_slots
    assert decision.reason_codes == ["date_missing", "temporal_unclear"]


def test_stale_evidence_blocks_confirmation_without_becoming_no_slot():
    context = frame_set(
        BernieRequestedAppointmentFrame(
            status="known",
            basis="Instruction has enough detail to search.",
            reference_date=REFERENCE_DATE,
        ),
        BernieStaleEvidenceFrame(
            status="stale",
            reason_code="candidate_freshness_mismatch",
            basis="Selected candidate did not match the latest server evidence.",
            reference_date=REFERENCE_DATE,
            fresh_for_turn_ref="turn-older",
        ),
    )

    decision = evaluate_reception_context(context)

    assert decision.must_block_confirmation
    assert not decision.search_ran_no_candidates
    assert decision.availability == "not_evaluated"


def test_hard_guardrail_blocks_confirmation_and_search():
    context = frame_set(
        BernieGuardrailOutcomeFrame(
            status="blocked",
            reason_code="unsafe_autonomous_booking",
            basis="Instruction attempted to book without staff confirmation.",
            reference_date=REFERENCE_DATE,
        )
    )

    decision = evaluate_reception_context(context)

    assert decision.availability == "blocked"
    assert decision.must_block_confirmation
    assert not decision.can_search_slots
    assert not decision.can_prepare_proposal
