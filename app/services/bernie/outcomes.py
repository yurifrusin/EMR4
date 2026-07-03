"""Compatibility facade for diary-domain booking outcome classification.

Follows the diary/frames → bernie/frames pattern: implementation lives in
app.services.diary.outcomes; this module keeps stable import paths for callers
that address the bernie package.
"""

from app.services.diary.outcomes import (
    BernieBookingOutcome,
    BernieBookingOutcomeKind,
    OutcomeFamily,
    OUTCOME_SESSION_STATE,
    assert_outcome_matches_state,
    classify_booking_outcome,
)

__all__ = [
    "BernieBookingOutcome",
    "BernieBookingOutcomeKind",
    "OutcomeFamily",
    "OUTCOME_SESSION_STATE",
    "assert_outcome_matches_state",
    "classify_booking_outcome",
]
