"""Native diary/reception domain services.

This package owns diary-domain contracts that may be authored or consumed by
Bernie, the ordinary diary UI, Rayleen, Davida, and future bounded agents.
N1a keeps the public Bernie symbol names stable while moving the implementation
home behind compatibility facades.
"""

from app.services.diary.capabilities import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapability,
    BernieCapabilityTier,
    get_bernie_capability,
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
from app.services.diary.temporal import (
    DATE_RE,
    WEEK_RELATIVE_RE,
    SameDayWindowDecision,
    SameDayWindowKind,
    evaluate_same_day_window,
    extract_natural_date_constraint,
    extract_natural_time_constraints,
    parse_time_fragment,
    resolve_week_relative_date,
)

__all__ = [
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
    "DATE_RE",
    "WEEK_RELATIVE_RE",
    "SameDayWindowDecision",
    "SameDayWindowKind",
    "evaluate_same_day_window",
    "extract_natural_date_constraint",
    "extract_natural_time_constraints",
    "parse_time_fragment",
    "resolve_week_relative_date",
]
