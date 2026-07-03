"""Bernie reception-agent package and compatibility facade.

This package is the domain boundary named by the Fable 5 architecture consult
(Sprint A of the Bernie extraction programme). Callers outside the Bernie
domain - routers, future session runtimes, voice lanes - should import from
``app.services.bernie`` (or its submodules), never from the legacy flat
``app.services.bernie_*`` modules directly.

Current shape (native diary/reception domain foundation, no behaviour change):

- Diary/reception implementation contracts live in ``app.services.diary``.
  Bernie submodules keep stable import paths by re-exporting those contracts.
- Bernie continues to own interpretation, session state, narration/pilot
  boundaries, and legacy flat-module facades that have not moved yet.

Later sprints add action envelopes and retire more flat-module implementations;
external import paths through this package stay stable.
"""

from app.services.bernie.confirm_gate import (
    ConfirmAffordanceDecision,
    ConfirmAffordanceGate,
    evaluate_confirm_affordance,
)
from app.services.bernie.capabilities import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapability,
    BernieCapabilityTier,
    get_bernie_capability,
)
from app.services.bernie.context import (
    build_existing_future_follow_up_warning,
    build_patient_booking_context,
    has_existing_booking_on_requested_day,
)
from app.services.bernie.evidence import (
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_CONFIRMATION_EVIDENCE_VERSION,
    SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SignedEvidenceResult,
    StalenessResult,
    StalenessVerdict,
    check_staleness,
    compute_candidate_freshness_id,
    compute_proposal_freshness_id,
    mint_signed_confirmation_evidence,
    mint_session_id,
    mint_turn_id,
    verify_signed_confirmation_evidence,
)
from app.services.bernie.frames import (
    BernieAdvisoryWarningFrame,
    BernieFrameSource,
    BernieFrameStatus,
    BernieFrameType,
    BernieGuardrailOutcomeFrame,
    BernieModelUncertaintyFrame,
    BerniePatientBookingContextFrame,
    BernieReceptionContextFrameSet,
    BernieReceptionFrame,
    BernieReceptionFrameBase,
    BernieRequestedAppointmentFrame,
    BernieRosterScheduleFrame,
    BernieSlotSearchFrame,
    BernieStaleEvidenceFrame,
)
from app.services.bernie.interpreter import (
    BookingInstructionInterpreter,
    DisabledBookingInstructionInterpreter,
    FakeBookingInstructionInterpreter,
    GeminiVertexBookingInstructionInterpreter,
    InterpreterReadinessStatus,
    actor_context_for_interpreter_user,
    get_booking_instruction_interpreter,
    interpreter_is_ready,
    set_live_provider_factory,
)
from app.services.bernie.normalizer import normalize_slot_search_command
from app.services.bernie.pilot import (
    BERNIE_STAFF_REVIEW_SURFACE,
    BerniePilotEligibility,
    evaluate_bernie_pilot_eligibility,
)
from app.services.bernie.policy import (
    BernieAvailabilityClassification,
    BernieReceptionPolicyDecision,
    evaluate_reception_context,
)
from app.services.bernie.schedule_explanations import (
    DIARY_SCHEDULE_COPY_CATALOG,
    DIARY_SCHEDULE_REASON_ALIASES,
    DiaryScheduleCopy,
    DiaryScheduleExplanation,
    DiaryScheduleExplanationEvidence,
    DiaryScheduleExplanationReason,
    explain_schedule,
    get_schedule_copy,
    parse_schedule_explanation_reason,
)
from app.services.bernie.session import (
    CLIENT_EVENT_TRANSITIONS,
    SERVER_ADVANCE_TARGETS,
    SERVER_OUTCOME_EVENT_TARGETS,
    TERMINAL_STATES,
    TRANSIENT_STATES,
    BernieSessionEvent,
    BernieSessionEventRejectionCode,
    BernieSessionEventResult,
    BernieSessionEventType,
    BernieSessionRecord,
    BernieSessionState,
    SessionTransitionValidation,
    validate_session_event,
)
from app.services.bernie.session_store import (
    InMemoryBernieSessionStore,
    build_session_confirmation_binding,
)
from app.services.bernie.temporal import (
    SameDayWindowDecision,
    evaluate_same_day_window,
    extract_natural_date_constraint,
    extract_natural_time_constraints,
    parse_time_fragment,
    resolve_week_relative_date,
)
from app.services.bernie.transitions import (
    DateResolutionTransition,
    resolve_booking_date_transition,
)

__all__ = [
    # confirm gate
    "ConfirmAffordanceDecision",
    "ConfirmAffordanceGate",
    "evaluate_confirm_affordance",
    # capabilities
    "BERNIE_CAPABILITY_REGISTRY",
    "BernieCapability",
    "BernieCapabilityTier",
    "get_bernie_capability",
    # context
    "build_existing_future_follow_up_warning",
    "build_patient_booking_context",
    "has_existing_booking_on_requested_day",
    # evidence
    "SIGNED_CONFIRMATION_EVIDENCE_PURPOSE",
    "SIGNED_CONFIRMATION_EVIDENCE_VERSION",
    "SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE",
    "SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE",
    "SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE",
    "SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE",
    "SignedEvidenceResult",
    "StalenessResult",
    "StalenessVerdict",
    "check_staleness",
    "compute_candidate_freshness_id",
    "compute_proposal_freshness_id",
    "mint_signed_confirmation_evidence",
    "mint_session_id",
    "mint_turn_id",
    "verify_signed_confirmation_evidence",
    # frames
    "BernieAdvisoryWarningFrame",
    "BernieFrameSource",
    "BernieFrameStatus",
    "BernieFrameType",
    "BernieGuardrailOutcomeFrame",
    "BernieModelUncertaintyFrame",
    "BerniePatientBookingContextFrame",
    "BernieReceptionContextFrameSet",
    "BernieReceptionFrame",
    "BernieReceptionFrameBase",
    "BernieRequestedAppointmentFrame",
    "BernieRosterScheduleFrame",
    "BernieSlotSearchFrame",
    "BernieStaleEvidenceFrame",
    # interpreter
    "BookingInstructionInterpreter",
    "DisabledBookingInstructionInterpreter",
    "FakeBookingInstructionInterpreter",
    "GeminiVertexBookingInstructionInterpreter",
    "InterpreterReadinessStatus",
    "actor_context_for_interpreter_user",
    "get_booking_instruction_interpreter",
    "interpreter_is_ready",
    "set_live_provider_factory",
    # normalizer
    "normalize_slot_search_command",
    # pilot
    "BERNIE_STAFF_REVIEW_SURFACE",
    "BerniePilotEligibility",
    "evaluate_bernie_pilot_eligibility",
    # policy
    "BernieAvailabilityClassification",
    "BernieReceptionPolicyDecision",
    "evaluate_reception_context",
    "DIARY_SCHEDULE_COPY_CATALOG",
    "DIARY_SCHEDULE_REASON_ALIASES",
    "DiaryScheduleCopy",
    "DiaryScheduleExplanation",
    "DiaryScheduleExplanationEvidence",
    "DiaryScheduleExplanationReason",
    "explain_schedule",
    "get_schedule_copy",
    "parse_schedule_explanation_reason",
    # session
    "CLIENT_EVENT_TRANSITIONS",
    "SERVER_ADVANCE_TARGETS",
    "SERVER_OUTCOME_EVENT_TARGETS",
    "TERMINAL_STATES",
    "TRANSIENT_STATES",
    "BernieSessionEvent",
    "BernieSessionEventRejectionCode",
    "BernieSessionEventResult",
    "BernieSessionEventType",
    "BernieSessionRecord",
    "BernieSessionState",
    "InMemoryBernieSessionStore",
    "SessionTransitionValidation",
    "build_session_confirmation_binding",
    "validate_session_event",
    # temporal
    "SameDayWindowDecision",
    "evaluate_same_day_window",
    "extract_natural_date_constraint",
    "extract_natural_time_constraints",
    "parse_time_fragment",
    "resolve_week_relative_date",
    # transitions
    "DateResolutionTransition",
    "resolve_booking_date_transition",
]
