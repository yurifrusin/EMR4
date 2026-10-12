"""Inert Stage 1 appointment vocabulary and time-only move intent.

These pure functions neither authenticate an actor nor read or change an
appointment. A future server adapter must supply the trusted current context.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import re
import uuid
from typing import Any


MOVE_VERSION = "appointment.move_time_intent.v1"
DOMAIN_STATUSES = frozenset(
    ("Booked", "Confirmed", "Arrived", "InConsult", "Completed", "Cancelled", "NoShow", "DNA")
)
_BUREAU_STATUSES = {
    "Booked": "booked",
    "Arrived": "arrived",
    "Completed": "completed",
    "DNA": "dna",
}
_MOVABLE = frozenset(("Booked", "Confirmed"))
_TIMEZONES = frozenset(("Australia/Brisbane", "Australia/Sydney"))
_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
_LOCAL_TIME = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d\Z")
_CONTEXT_FIELDS = {
    "tenant_id", "actor_id", "role", "move_capability", "source_revision",
    "selected_appointment_id", "selected_state_version", "selected_status",
    "selected_date", "selected_start_local", "patient_id", "practitioner_id",
    "appointment_type_id", "location_id", "duration_minutes",
    "practice_timezone", "captured_at", "as_of",
}
_INTENT_FIELDS = {
    "schema_version", "tenant_id", "actor_id", "role", "source_appointment_id",
    "source_state_version", "source_revision", "target_date", "target_start_local",
    "authority",
}


class LifecycleRejected(ValueError):
    """A fixed rejection code that never contains caller-supplied values."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _reject(code: str) -> None:
    raise LifecycleRejected(code)


def domain_status(value: Any) -> str:
    """Keep the source lifecycle meaning exact; do not normalize unknowns."""
    if type(value) is not str or value not in DOMAIN_STATUSES:
        _reject("STATUS_UNSUPPORTED")
    return value


def bureau_status(value: Any) -> str:
    """Map only states expressible by the existing v1 Bureau input schema."""
    status = domain_status(value)
    if status not in _BUREAU_STATUSES:
        _reject("STATUS_UNSUPPORTED")
    return _BUREAU_STATUSES[status]


def _object(value: Any, fields: set[str]) -> dict[str, Any]:
    if type(value) is not dict or set(value) != fields:
        _reject("STRUCTURE_INVALID")
    return value


def _uuid(value: Any, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    if type(value) is not str or len(value) != 36:
        _reject("IDENTITY_INVALID")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        _reject("IDENTITY_INVALID")
    if str(parsed) != value:
        _reject("IDENTITY_INVALID")
    return value


def _instant(value: Any) -> datetime:
    if type(value) is not str or not _UTC.fullmatch(value):
        _reject("TIME_INVALID")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        _reject("TIME_INVALID")
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        _reject("TIME_INVALID")
    return parsed


def _date(value: Any) -> str:
    if type(value) is not str or len(value) != 10:
        _reject("TIME_INVALID")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        _reject("TIME_INVALID")
    if parsed.isoformat() != value:
        _reject("TIME_INVALID")
    return value


def _clock(value: Any) -> str:
    if type(value) is not str or not _LOCAL_TIME.fullmatch(value):
        _reject("TIME_INVALID")
    return value


@dataclass(frozen=True)
class MoveIntent:
    tenant_id: str
    actor_id: str
    appointment_id: str
    source_state_version: int
    source_revision: int
    source_status: str
    source_date: str
    source_start_local: str
    target_date: str
    target_start_local: str
    practice_timezone: str
    patient_id: str | None
    practitioner_id: str
    appointment_type_id: str | None
    location_id: str | None
    duration_minutes: int


def validate_move_intent(raw: Any, trusted_context: Any) -> MoveIntent:
    """Bind a proposed time delta to current server-supplied facts.

    This is no appointment update command, availability decision, signed
    confirmation, or evidence that the actor has been authenticated.
    """
    context = _object(trusted_context, _CONTEXT_FIELDS)
    intent = _object(raw, _INTENT_FIELDS)
    if intent["schema_version"] != MOVE_VERSION:
        _reject("VERSION_UNSUPPORTED")
    if intent["authority"] != "proposal_only":
        _reject("AUTHORITY_INVALID")
    tenant_id = _uuid(context["tenant_id"])
    actor_id = _uuid(context["actor_id"])
    appointment_id = _uuid(context["selected_appointment_id"])
    if (
        context["role"] != "reception"
        or context["move_capability"] != "appointments.move.propose"
    ):
        _reject("CONTEXT_UNAUTHORIZED")
    if (
        intent["tenant_id"] != tenant_id
        or intent["actor_id"] != actor_id
        or intent["role"] != context["role"]
        or intent["source_appointment_id"] != appointment_id
    ):
        _reject("SCOPE_MISMATCH")
    for field in ("source_revision", "selected_state_version"):
        if type(context[field]) is not int or context[field] < 1:
            _reject("REVISION_INVALID")
    if (
        type(intent["source_revision"]) is not int
        or type(intent["source_state_version"]) is not int
        or intent["source_revision"] != context["source_revision"]
        or intent["source_state_version"] != context["selected_state_version"]
    ):
        _reject("REVISION_MISMATCH")
    captured = _instant(context["captured_at"])
    age = _instant(context["as_of"]) - captured
    if age < timedelta(0) or age > timedelta(seconds=300):
        _reject("SOURCE_STALE")
    source_status = domain_status(context["selected_status"])
    if source_status not in _MOVABLE:
        _reject("STATUS_NOT_MOVABLE")
    if type(context["practice_timezone"]) is not str or context["practice_timezone"] not in _TIMEZONES:
        _reject("TIMEZONE_UNSUPPORTED")
    source_date = _date(context["selected_date"])
    source_start = _clock(context["selected_start_local"])
    target_date = _date(intent["target_date"])
    target_start = _clock(intent["target_start_local"])
    if (source_date, source_start) == (target_date, target_start):
        _reject("NO_CHANGE")
    patient_id = _uuid(context["patient_id"], optional=True)
    practitioner_id = _uuid(context["practitioner_id"])
    appointment_type_id = _uuid(context["appointment_type_id"], optional=True)
    location_id = _uuid(context["location_id"], optional=True)
    duration = context["duration_minutes"]
    if type(duration) is not int or not 1 <= duration <= 480:
        _reject("STRUCTURE_INVALID")
    return MoveIntent(
        tenant_id=tenant_id, actor_id=actor_id, appointment_id=appointment_id,
        source_state_version=context["selected_state_version"],
        source_revision=context["source_revision"], source_status=source_status,
        source_date=source_date, source_start_local=source_start,
        target_date=target_date, target_start_local=target_start,
        practice_timezone=context["practice_timezone"], patient_id=patient_id,
        practitioner_id=practitioner_id, appointment_type_id=appointment_type_id,
        location_id=location_id, duration_minutes=duration,
    )


def move_review(raw: Any, trusted_context: Any) -> dict[str, Any]:
    """Revalidate raw input and render only the resulting immutable snapshot."""
    intent = validate_move_intent(raw, trusted_context)
    return {
        "schema_version": MOVE_VERSION,
        "appointment_id": intent.appointment_id,
        "source_state_version": intent.source_state_version,
        "source_revision": intent.source_revision,
        "before": {"date": intent.source_date, "start_local": intent.source_start_local},
        "after": {"date": intent.target_date, "start_local": intent.target_start_local},
        "practice_timezone": intent.practice_timezone,
        "unchanged": {
            "patient_id": intent.patient_id,
            "practitioner_id": intent.practitioner_id,
            "appointment_type_id": intent.appointment_type_id,
            "duration_minutes": intent.duration_minutes,
            "location_id": intent.location_id,
            "status": intent.source_status,
        },
        "risk": "availability_and_source_may_change",
        "confirmation": "staff_signed_update_required",
        "authority": "proposal_only",
        "write_performed": False,
        "affordances": {"confirm": False, "write": False},
    }
