"""Native diary/reception domain services.

This package owns diary-domain contracts that may be authored or consumed by
Bernie, the ordinary diary UI, Rayleen, Davida, and future bounded agents.
N1a keeps the public Bernie symbol names stable while moving the implementation
home behind compatibility facades.
"""

from app.services.diary.action_grammar import (
    DIARY_ACTION_GRAMMAR,
    GRAMMAR_SCHEMA_VERSION,
    DiaryActionVerb,
    DiaryActionVerbDescriptor,
    action_verb_for_envelope,
    assert_grammar_consistency,
    get_verb_descriptor,
)
from app.services.diary.confirm_gate import (
    ConfirmAffordanceDecision,
    ConfirmAffordanceGate,
    evaluate_confirm_affordance,
)
from app.services.diary.confirm_actions import (
    DIARY_CONFIRM_ACTIONS,
    DiaryConfirmAction,
    DiaryConfirmActionDescriptor,
    get_diary_confirm_action,
)
from app.services.diary.capabilities import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapability,
    BernieCapabilityTier,
    get_bernie_capability,
)
from app.services.diary.envelope_capability_policy import (
    EnvelopeAuthorityDecision,
    validate_envelope_authority,
)
from app.services.diary.envelopes import (
    DiaryActionAuthor,
    DiaryActionChannel,
    DiaryActionConfirmation,
    DiaryActionIntent,
    DiaryActionProposal,
    DiaryActionSuggestion,
)
from app.services.diary.frames import (
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
from app.services.diary.policy import (
    BernieAvailabilityClassification,
    BernieReceptionPolicyDecision,
    evaluate_reception_context,
)
from app.services.diary.schedule_explanations import (
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
from app.services.diary.temporal import (
    DATE_RE,
    WEEK_RELATIVE_RE,
    SameDayWindowDecision,
    SameDayWindowKind,
    TemporalExtraction,
    TemporalRelationKind,
    adjust_search_window_for_relation,
    evaluate_same_day_window,
    extract_natural_date_constraint,
    extract_natural_time_constraints,
    infer_temporal_relation,
    parse_time_fragment,
    resolve_week_relative_date,
    should_classify_exact_booking,
)

__all__ = [
    # action grammar
    "GRAMMAR_SCHEMA_VERSION",
    "DiaryActionVerb",
    "DiaryActionVerbDescriptor",
    "DIARY_ACTION_GRAMMAR",
    "get_verb_descriptor",
    "action_verb_for_envelope",
    "assert_grammar_consistency",
    # confirm gate
    "ConfirmAffordanceDecision",
    "ConfirmAffordanceGate",
    "evaluate_confirm_affordance",
    "DIARY_CONFIRM_ACTIONS",
    "DiaryConfirmAction",
    "DiaryConfirmActionDescriptor",
    "get_diary_confirm_action",
    "EnvelopeAuthorityDecision",
    "validate_envelope_authority",
    "BERNIE_CAPABILITY_REGISTRY",
    "BernieCapability",
    "BernieCapabilityTier",
    "get_bernie_capability",
    "DiaryActionAuthor",
    "DiaryActionChannel",
    "DiaryActionConfirmation",
    "DiaryActionIntent",
    "DiaryActionProposal",
    "DiaryActionSuggestion",
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
    "DATE_RE",
    "WEEK_RELATIVE_RE",
    "SameDayWindowDecision",
    "SameDayWindowKind",
    "TemporalExtraction",
    "TemporalRelationKind",
    "adjust_search_window_for_relation",
    "evaluate_same_day_window",
    "extract_natural_date_constraint",
    "extract_natural_time_constraints",
    "infer_temporal_relation",
    "parse_time_fragment",
    "resolve_week_relative_date",
    "should_classify_exact_booking",
]
