"""Server-side singleton readback for the reviewed G3 appointment projection.

The selected appointment's state version is the revision of this singleton
source. It is not a revision for a diary list, audit stream, or event aggregate.
Authentication, tenant scoping, and current-row selection belong to the route.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.appointment_list_projection import (
    ProjectionRejected,
    V2_VERSION,
    render_fallback_v2,
    render_view_v2,
)


def _utc_text(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("READ_TIME_INVALID")
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_singleton_appointment_readback(
    appointment: Any,
    *,
    tenant_id: str,
    actor_id: str,
    practice_timezone: str,
    as_of: datetime,
    fallback: bool = False,
) -> dict[str, Any]:
    """Render one tenant-scoped row using the same G3 validation in both modes.

    The route must pass a freshly selected row and authenticated identity.
    Fallback revalidates the complete raw projection and never shows part of
    rejected input.
    """
    captured_at = _utc_text(as_of)
    version = appointment.appointment_state_version
    if type(version) is not int or version < 1:
        raise ValueError("READ_VERSION_INVALID")
    if str(appointment.practice_id) != tenant_id:
        raise ValueError("READ_SCOPE_INVALID")
    start = _utc_text(appointment.start_time)
    end = _utc_text(appointment.end_time)
    status = appointment.status.value
    label = "Appointment 1"
    raw = {
        "schema_version": V2_VERSION,
        "tenant_id": tenant_id,
        "actor_id": actor_id,
        "role": "reception",
        "source_id": str(appointment.id),
        "source_revision": version,
        "captured_at": captured_at,
        "practice_timezone": practice_timezone,
        "total_count": 1,
        "is_complete": True,
        "authority": "read_only",
        "heading": "Appointments",
        "columns": ["Start", "End", "Status", "Appointment"],
        "items": [{
            "id": str(appointment.id),
            "practice_id": tenant_id,
            "source_version": version,
            "start_time": start,
            "end_time": end,
            "status": status,
            "display_label": label,
            "accessibility_label": (
                f"{label}; starts {start}; ends {end}; status {status}; "
                f"timezone {practice_timezone}"
            ),
            "warnings": [],
        }],
        "warnings": [],
    }
    context = {
        "tenant_id": tenant_id,
        "actor_id": actor_id,
        "role": "reception",
        "read_capability": "appointments.read",
        "source_id": str(appointment.id),
        "source_revision": version,
        "as_of": captured_at,
        "practice_timezone": practice_timezone,
        "expected_total": 1,
    }
    if fallback:
        return render_fallback_v2(raw, context)
    try:
        return render_view_v2(raw, context)
    except ProjectionRejected:
        return render_fallback_v2(raw, context)
