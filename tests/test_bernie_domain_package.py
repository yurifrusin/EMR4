"""Tests for the bounded app/services/bernie domain package (extraction foundation).

Three concerns:
1. The package facades re-export the exact same objects as the legacy flat
   modules - the extraction changes import paths only, never behaviour.
2. The persistence-shaped session/event contract scaffolding upholds the core
   statechart invariants (confirmed is unreachable by client events; the
   confirmation path is confirm_submitted from proposal_preview only).
3. The capability registry skeleton is well-formed and encodes the
   staff-confirmation rule for propose/confirm tiers.
"""

import uuid
from datetime import date, datetime, timezone

import app.services.bernie as bernie_domain
import app.services.bernie.frames as bernie_frames
import app.services.bernie.policy as bernie_policy
import app.services.bernie_booking_interpreter as legacy_interpreter
import app.services.bernie_patient_context as legacy_context
import app.services.bernie_pilot_gate as legacy_pilot
import app.services.bernie_slot_normalizer as legacy_normalizer
import app.services.bernie_transition_table as legacy_transitions
import app.services.bernie_turn_evidence as legacy_evidence
from app.schemas.appointments import (
    BernieBookingInstructionInterpretOut,
    BernieSupervisedBookingOut,
)
from app.services.bernie import (
    BERNIE_CAPABILITY_REGISTRY,
    CLIENT_EVENT_TRANSITIONS,
    SERVER_ADVANCE_TARGETS,
    TERMINAL_STATES,
    TRANSIENT_STATES,
    BernieCapabilityTier,
    BernieSessionEvent,
    BernieSessionEventType,
    BernieSessionRecord,
    BernieSessionState,
    get_bernie_capability,
    validate_session_event,
)
from app.services.bernie import temporal


# 1. Facade identity: package == legacy implementation

def test_interpreter_facade_reexports_legacy_objects():
    assert bernie_domain.get_booking_instruction_interpreter is legacy_interpreter.get_booking_instruction_interpreter
    assert bernie_domain.interpreter_is_ready is legacy_interpreter.interpreter_is_ready
    assert bernie_domain.set_live_provider_factory is legacy_interpreter.set_live_provider_factory
    assert bernie_domain.actor_context_for_interpreter_user is legacy_interpreter.actor_context_for_interpreter_user
    assert bernie_domain.FakeBookingInstructionInterpreter is legacy_interpreter.FakeBookingInstructionInterpreter
    assert bernie_domain.DisabledBookingInstructionInterpreter is legacy_interpreter.DisabledBookingInstructionInterpreter
    assert bernie_domain.GeminiVertexBookingInstructionInterpreter is legacy_interpreter.GeminiVertexBookingInstructionInterpreter
    assert bernie_domain.InterpreterReadinessStatus is legacy_interpreter.InterpreterReadinessStatus


def test_context_facade_reexports_legacy_objects():
    assert bernie_domain.build_patient_booking_context is legacy_context.build_patient_booking_context
    assert bernie_domain.build_existing_future_follow_up_warning is legacy_context.build_existing_future_follow_up_warning
    assert bernie_domain.has_existing_booking_on_requested_day is legacy_context.has_existing_booking_on_requested_day


def test_normalizer_facade_reexports_legacy_objects():
    assert bernie_domain.normalize_slot_search_command is legacy_normalizer.normalize_slot_search_command


def test_transitions_facade_reexports_legacy_objects():
    assert bernie_domain.resolve_booking_date_transition is legacy_transitions.resolve_booking_date_transition
    assert bernie_domain.DateResolutionTransition is legacy_transitions.DateResolutionTransition


def test_evidence_facade_reexports_legacy_objects():
    assert bernie_domain.compute_candidate_freshness_id is legacy_evidence.compute_candidate_freshness_id
    assert bernie_domain.compute_proposal_freshness_id is legacy_evidence.compute_proposal_freshness_id
    assert bernie_domain.check_staleness is legacy_evidence.check_staleness
    assert bernie_domain.mint_session_id is legacy_evidence.mint_session_id
    assert bernie_domain.mint_turn_id is legacy_evidence.mint_turn_id
    assert bernie_domain.StalenessVerdict is legacy_evidence.StalenessVerdict


def test_pilot_facade_reexports_legacy_objects():
    assert bernie_domain.evaluate_bernie_pilot_eligibility is legacy_pilot.evaluate_bernie_pilot_eligibility
    assert bernie_domain.BerniePilotEligibility is legacy_pilot.BerniePilotEligibility
    assert bernie_domain.BERNIE_STAFF_REVIEW_SURFACE is legacy_pilot.BERNIE_STAFF_REVIEW_SURFACE


def test_frame_and_policy_facades_reexport_domain_objects():
    assert bernie_domain.BernieReceptionContextFrameSet is bernie_frames.BernieReceptionContextFrameSet
    assert bernie_domain.BernieRequestedAppointmentFrame is bernie_frames.BernieRequestedAppointmentFrame
    assert bernie_domain.BerniePatientBookingContextFrame is bernie_frames.BerniePatientBookingContextFrame
    assert bernie_domain.BernieRosterScheduleFrame is bernie_frames.BernieRosterScheduleFrame
    assert bernie_domain.BernieSlotSearchFrame is bernie_frames.BernieSlotSearchFrame
    assert bernie_domain.BernieAdvisoryWarningFrame is bernie_frames.BernieAdvisoryWarningFrame
    assert bernie_domain.BernieStaleEvidenceFrame is bernie_frames.BernieStaleEvidenceFrame
    assert bernie_domain.BernieModelUncertaintyFrame is bernie_frames.BernieModelUncertaintyFrame
    assert bernie_domain.BernieGuardrailOutcomeFrame is bernie_frames.BernieGuardrailOutcomeFrame
    assert bernie_domain.BernieReceptionPolicyDecision is bernie_policy.BernieReceptionPolicyDecision
    assert bernie_domain.evaluate_reception_context is bernie_policy.evaluate_reception_context


def test_temporal_facade_reexports_legacy_pure_helpers():
    assert temporal.parse_time_fragment is legacy_interpreter._parse_time_fragment
    assert temporal.extract_natural_time_constraints is legacy_interpreter._extract_natural_time_constraints
    assert temporal.extract_natural_date_constraint is legacy_interpreter._extract_natural_date_constraint


def test_temporal_facade_behaviour_matches_legacy():
    assert temporal.parse_time_fragment("3") == "15:00"
    assert temporal.parse_time_fragment("3:45 pm") == "15:45"
    assert temporal.extract_natural_time_constraints("after 3 pm") == ("15:00", None)
    assert temporal.extract_natural_time_constraints("between 2 pm and 3:45") == ("14:00", "15:45")
    assert temporal.extract_natural_date_constraint(
        "next week please", date(2026, 7, 3)
    ) == "2026-07-10"


def test_router_imports_bernie_services_through_domain_package():
    import app.routers.appointments as appointments_router

    assert appointments_router.normalize_slot_search_command is bernie_domain.normalize_slot_search_command
    assert appointments_router.build_patient_booking_context is bernie_domain.build_patient_booking_context
    assert appointments_router.check_staleness is bernie_domain.check_staleness
    assert appointments_router.evaluate_bernie_pilot_eligibility is bernie_domain.evaluate_bernie_pilot_eligibility
    assert appointments_router.resolve_booking_date_transition is bernie_domain.resolve_booking_date_transition
    assert appointments_router.get_booking_instruction_interpreter is bernie_domain.get_booking_instruction_interpreter


def test_reception_context_schema_version_is_stable():
    frame_set = bernie_domain.BernieReceptionContextFrameSet(
        reference_date=date(2026, 7, 3),
        frames=[],
    )

    dumped = frame_set.model_dump(mode="json")

    assert frame_set.schema_version == "bernie.reception_context.v1"
    assert dumped["schema_version"] == "bernie.reception_context.v1"


def test_bernie_response_models_keep_reception_policy_field():
    for response_model in (
        BernieBookingInstructionInterpretOut,
        BernieSupervisedBookingOut,
    ):
        assert "reception_context" in response_model.model_fields
        assert "reception_policy" in response_model.model_fields
        assert response_model.model_fields["reception_policy"].default is None


# 2. Session/event contract scaffolding invariants

def test_session_states_match_consulted_statechart():
    expected = {
        "instruction_entry", "recognition", "clarification",
        "context_enrichment", "slot_search", "candidate_selection",
        "proposal_preview", "confirmation", "confirmed", "no_slot",
        "clinic_day_exhausted", "handed_off",
    }
    assert {s.value for s in BernieSessionState} == expected


def test_transition_table_covers_every_state():
    assert set(CLIENT_EVENT_TRANSITIONS) == set(BernieSessionState)


def test_no_client_event_targets_confirmed():
    for state, events in CLIENT_EVENT_TRANSITIONS.items():
        for event_type, target in events.items():
            assert target is not BernieSessionState.confirmed, (
                f"{event_type} from {state} must not reach confirmed directly"
            )


def test_confirmed_only_reachable_via_server_advance_from_confirmation():
    reachable_from = [
        state
        for state, targets in SERVER_ADVANCE_TARGETS.items()
        if BernieSessionState.confirmed in targets
    ]
    assert reachable_from == [BernieSessionState.confirmation]


def test_confirmation_only_reachable_via_confirm_submitted_from_proposal_preview():
    sources = [
        (state, event_type)
        for state, events in CLIENT_EVENT_TRANSITIONS.items()
        for event_type, target in events.items()
        if target is BernieSessionState.confirmation
    ]
    assert sources == [
        (BernieSessionState.proposal_preview, BernieSessionEventType.confirm_submitted)
    ]
    for targets in SERVER_ADVANCE_TARGETS.values():
        assert BernieSessionState.confirmation not in targets


def test_transient_states_accept_no_direct_client_events():
    for state in TRANSIENT_STATES:
        assert CLIENT_EVENT_TRANSITIONS[state] == {}


def test_terminal_states_accept_no_direct_client_events():
    for state in TERMINAL_STATES:
        assert CLIENT_EVENT_TRANSITIONS[state] == {}


def test_new_session_allowed_from_every_state():
    for state in BernieSessionState:
        verdict = validate_session_event(state, BernieSessionEventType.new_session)
        assert verdict.allowed
        assert verdict.target_state is BernieSessionState.instruction_entry


def test_diary_navigated_is_memory_only_in_non_transient_states():
    for state in BernieSessionState:
        verdict = validate_session_event(state, BernieSessionEventType.diary_navigated)
        if state in TRANSIENT_STATES:
            assert not verdict.allowed
            assert verdict.reason_code == "event_not_allowed_in_transient_state"
        else:
            assert verdict.allowed
            assert verdict.target_state is state


def test_illegal_event_returns_typed_rejection():
    verdict = validate_session_event(
        BernieSessionState.instruction_entry,
        BernieSessionEventType.confirm_submitted,
    )
    assert not verdict.allowed
    assert verdict.target_state is None
    assert verdict.reason_code == "event_not_allowed_in_state"
    assert "confirm_submitted" in (verdict.detail or "")


def test_legal_event_returns_target_state():
    verdict = validate_session_event(
        BernieSessionState.instruction_entry,
        BernieSessionEventType.staff_instruction,
    )
    assert verdict.allowed
    assert verdict.target_state is BernieSessionState.recognition


def test_session_record_round_trips_through_json():
    now = datetime(2026, 7, 3, 9, 0, tzinfo=timezone.utc)
    event = BernieSessionEvent(
        event_id="evt-1",
        session_id="bernie-session-abc123def456",
        event_type=BernieSessionEventType.staff_instruction,
        turn_index=0,
        occurred_at=now,
        payload={"instruction_present": True},
    )
    record = BernieSessionRecord(
        session_id="bernie-session-abc123def456",
        practice_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        state=BernieSessionState.recognition,
        request_reference_date=date(2026, 7, 3),
        patient_id=uuid.uuid4(),
        patient_band="assume",
        candidate_freshness_ids=["a" * 32],
        turn_count=1,
        events=[event],
        created_at=now,
        updated_at=now,
    )
    restored = BernieSessionRecord.model_validate_json(record.model_dump_json())
    assert restored == record
    assert restored.events[0].event_type is BernieSessionEventType.staff_instruction


# 3. Capability registry skeleton

def test_capability_names_are_unique():
    names = [c.name for c in BERNIE_CAPABILITY_REGISTRY]
    assert len(names) == len(set(names))


def test_expected_capabilities_registered():
    names = {c.name for c in BERNIE_CAPABILITY_REGISTRY}
    assert {
        "interpret_instruction", "resolve_patient", "resolve_practitioner",
        "get_patient_booking_context", "find_slots", "explain_schedule",
        "suggest_next_actions", "propose_booking", "propose_edit",
        "propose_cancel", "propose_status", "confirm_booking",
        "handoff_to_receptionist",
    } <= names


def test_propose_and_confirm_tiers_require_staff_confirmation():
    for capability in BERNIE_CAPABILITY_REGISTRY:
        if capability.tier in (BernieCapabilityTier.propose, BernieCapabilityTier.confirm):
            assert capability.requires_staff_confirmation, capability.name
        if capability.tier is BernieCapabilityTier.read_only:
            assert not capability.requires_staff_confirmation, capability.name


def test_get_bernie_capability_lookup():
    confirm_booking = get_bernie_capability("confirm_booking")
    assert confirm_booking is not None
    assert confirm_booking.tier is BernieCapabilityTier.confirm
    assert get_bernie_capability("book_autonomously") is None
