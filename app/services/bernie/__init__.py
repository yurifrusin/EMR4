"""Bounded reception-domain package for Bernie, EMR4's receptionist copilot.

This package is the domain boundary named by the Fable 5 architecture consult
(Sprint A of the Bernie extraction programme). Callers outside the Bernie
domain - routers, future session runtimes, voice lanes - should import from
``app.services.bernie`` (or its submodules), never from the legacy flat
``app.services.bernie_*`` modules directly.

Current shape (extraction foundation, no behaviour change):

- The legacy flat modules remain the implementation; each submodule here is a
  facade that re-exports the domain's public contract under its bounded home:
  ``interpreter``, ``context``, ``normalizer``, ``transitions``, ``evidence``,
  ``pilot``, ``temporal``.
- ``session`` and ``capabilities`` are new contract scaffolding: the
  persistence-shaped booking-session/event contract (no DB table yet) and the
  typed capability/tool registry skeleton.

Later sprints move implementations into this package and retire the flat
modules; external import paths through this package stay stable.
"""

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
    StalenessResult,
    StalenessVerdict,
    check_staleness,
    compute_candidate_freshness_id,
    compute_proposal_freshness_id,
    mint_session_id,
    mint_turn_id,
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
from app.services.bernie.session import (
    CLIENT_EVENT_TRANSITIONS,
    SERVER_ADVANCE_TARGETS,
    TERMINAL_STATES,
    TRANSIENT_STATES,
    BernieSessionEvent,
    BernieSessionEventType,
    BernieSessionRecord,
    BernieSessionState,
    SessionTransitionValidation,
    validate_session_event,
)
from app.services.bernie.transitions import (
    DateResolutionTransition,
    resolve_booking_date_transition,
)

__all__ = [
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
    "StalenessResult",
    "StalenessVerdict",
    "check_staleness",
    "compute_candidate_freshness_id",
    "compute_proposal_freshness_id",
    "mint_session_id",
    "mint_turn_id",
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
    # session
    "CLIENT_EVENT_TRANSITIONS",
    "SERVER_ADVANCE_TARGETS",
    "TERMINAL_STATES",
    "TRANSIENT_STATES",
    "BernieSessionEvent",
    "BernieSessionEventType",
    "BernieSessionRecord",
    "BernieSessionState",
    "SessionTransitionValidation",
    "validate_session_event",
    # transitions
    "DateResolutionTransition",
    "resolve_booking_date_transition",
]
