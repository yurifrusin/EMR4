"""Bounded-domain facade for Bernie's read-only patient booking context.

Re-exports the recognized-patient-only compact context service from the legacy
flat module. The implementation stays in ``app.services.bernie_patient_context``
for this extraction slice.
"""

from app.services.bernie_patient_context import (
    build_existing_future_follow_up_warning,
    build_patient_booking_context,
    has_existing_booking_on_requested_day,
)

__all__ = [
    "build_existing_future_follow_up_warning",
    "build_patient_booking_context",
    "has_existing_booking_on_requested_day",
]
