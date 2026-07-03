"""Bounded-domain facade for the Bernie staff-pilot eligibility gate.

Re-exports the allowlist gate from the legacy flat module. The implementation
stays in ``app.services.bernie_pilot_gate`` for this extraction slice.
"""

from app.services.bernie_pilot_gate import (
    BERNIE_STAFF_REVIEW_SURFACE,
    BerniePilotEligibility,
    evaluate_bernie_pilot_eligibility,
)

__all__ = [
    "BERNIE_STAFF_REVIEW_SURFACE",
    "BerniePilotEligibility",
    "evaluate_bernie_pilot_eligibility",
]
