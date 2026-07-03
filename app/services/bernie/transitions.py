"""Bounded-domain facade for Bernie's deterministic transition tables.

Re-exports the booking-date resolution transition table from the legacy flat
module. The implementation stays in ``app.services.bernie_transition_table``
for this extraction slice. The session-level statechart contract lives in
``app.services.bernie.session``.
"""

from app.services.bernie_transition_table import (
    DateResolutionTransition,
    resolve_booking_date_transition,
)

__all__ = [
    "DateResolutionTransition",
    "resolve_booking_date_transition",
]
