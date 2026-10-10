"""Unactivated, offline appointment-list projection contract.

Pure standard-library validation and view construction. A future server adapter
must supply authenticated context and map authoritative appointment data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import re
import uuid
from typing import Any


VERSION = "appointment.list_projection.v1"
MAX_ITEMS = 32
MAX_AGE_SECONDS = 300
_COLUMNS = ("Start", "End", "Status", "Appointment")
_STATUSES = frozenset(("scheduled", "cancelled"))
_WARNINGS = frozenset(("TIME_UNCONFIRMED",))
_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")


@dataclass(frozen=True)
class ValidatedRow:
    id: str
    practice_id: str
    start_time: str
    end_time: str
    status: str
    display_label: str
    accessibility_label: str
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class ValidatedProjection:
    rows: tuple[ValidatedRow, ...]
    warnings: tuple[str, ...]


class ProjectionRejected(ValueError):
    """A constant, non-disclosing rejection code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _reject(code: str) -> None:
    raise ProjectionRejected(code)


def _object(value: Any, fields: set[str]) -> dict[str, Any]:
    if type(value) is not dict or set(value) != fields:
        _reject("STRUCTURE_INVALID")
    return value


def _uuid(value: Any) -> str:
    if type(value) is not str or len(value) != 36:
        _reject("IDENTITY_INVALID")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        _reject("IDENTITY_INVALID")
    if str(parsed) != value:
        _reject("IDENTITY_INVALID")
    return value


def _time(value: Any) -> datetime:
    if type(value) is not str or not _UTC.fullmatch(value):
        _reject("TIME_INVALID")
    try:
        result = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        _reject("TIME_INVALID")
    if result.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        _reject("TIME_INVALID")
    return result


def _context(context: Any) -> dict[str, Any]:
    c = _object(context, {"tenant_id", "actor_id", "role", "read_capability", "source_revision", "as_of"})
    _uuid(c["tenant_id"])
    _uuid(c["actor_id"])
    if c["role"] != "reception" or c["read_capability"] != "appointments.read":
        _reject("CONTEXT_UNAUTHORIZED")
    if type(c["source_revision"]) is not int or c["source_revision"] < 1:
        _reject("REVISION_INVALID")
    _time(c["as_of"])
    return c


def validate_projection(raw: Any, context: Any) -> ValidatedProjection:
    """Return an immutable validated snapshot or raise a fixed rejection code.

    Context is trusted only by the caller's contract; this function cannot
    authenticate it. Raw projection data never grants read or write authority.
    """
    c = _context(context)
    p = _object(raw, {
        "schema_version", "tenant_id", "actor_id", "role", "source_revision",
        "captured_at", "authority", "heading", "columns", "items", "warnings",
    })
    if p["schema_version"] != VERSION:
        _reject("VERSION_UNSUPPORTED")
    if p["authority"] != "read_only":
        _reject("AUTHORITY_INVALID")
    if p["tenant_id"] != c["tenant_id"] or p["actor_id"] != c["actor_id"] or p["role"] != c["role"]:
        _reject("SCOPE_MISMATCH")
    if type(p["source_revision"]) is not int or p["source_revision"] != c["source_revision"]:
        _reject("REVISION_MISMATCH")
    captured = _time(p["captured_at"])
    age = _time(c["as_of"]) - captured
    if age < timedelta(0):
        _reject("FUTURE_PROJECTION")
    if age > timedelta(seconds=MAX_AGE_SECONDS):
        _reject("STALE_PROJECTION")
    if p["heading"] != "Appointments" or type(p["columns"]) is not list or tuple(p["columns"]) != _COLUMNS:
        _reject("ACCESSIBILITY_INVALID")
    raw_warnings = p["warnings"]
    if type(raw_warnings) is not list:
        _reject("WARNINGS_INVALID")
    validated_warnings = tuple(raw_warnings)
    if len(validated_warnings) > 4 or any(type(w) is not str or w not in _WARNINGS for w in validated_warnings):
        _reject("WARNINGS_INVALID")
    if len(set(validated_warnings)) != len(validated_warnings) or validated_warnings != tuple(sorted(validated_warnings)):
        _reject("WARNINGS_INVALID")
    if type(p["items"]) is not list or len(p["items"]) > MAX_ITEMS:
        _reject("SIZE_INVALID")
    rows: list[ValidatedRow] = []
    seen: set[str] = set()
    last_key: tuple[str, str] | None = None
    for value in p["items"]:
        item = _object(value, {"id", "practice_id", "start_time", "end_time", "status", "display_label", "accessibility_label", "warnings"})
        item_id = _uuid(item["id"])
        if item_id in seen:
            _reject("DUPLICATE_ID")
        seen.add(item_id)
        practice_id = _uuid(item["practice_id"])
        if practice_id != c["tenant_id"]:
            _reject("SCOPE_MISMATCH")
        start_time = item["start_time"]
        end_time = item["end_time"]
        start = _time(start_time)
        end = _time(end_time)
        if end <= start or end - start > timedelta(hours=8):
            _reject("TIME_INVALID")
        status = item["status"]
        if type(status) is not str or status not in _STATUSES:
            _reject("STATUS_INVALID")
        label = f"Appointment {len(rows) + 1}"
        if type(item["display_label"]) is not str or item["display_label"] != label:
            _reject("LABEL_INVALID")
        expected_accessibility = f"{label}; starts {start_time}; ends {end_time}; status {status}"
        if item["accessibility_label"] != expected_accessibility:
            _reject("ACCESSIBILITY_INVALID")
        raw_row_warnings = item["warnings"]
        if type(raw_row_warnings) is not list:
            _reject("WARNINGS_INVALID")
        warnings = tuple(raw_row_warnings)
        if len(warnings) > 1 or any(type(w) is not str or w not in _WARNINGS for w in warnings):
            _reject("WARNINGS_INVALID")
        key = (start_time, item_id)
        if last_key is not None and key <= last_key:
            _reject("ORDER_INVALID")
        last_key = key
        rows.append(ValidatedRow(
            id=item_id, practice_id=practice_id,
            start_time=start_time, end_time=end_time,
            status=status, display_label=label,
            accessibility_label=expected_accessibility, warnings=warnings,
        ))
    return ValidatedProjection(rows=tuple(rows), warnings=validated_warnings)


def render_view(raw: Any, context: Any) -> dict[str, Any]:
    """Construct inert view data from the sole validation path."""
    snapshot = validate_projection(raw, context)
    rows = tuple({
        "id": row.id, "practice_id": row.practice_id,
        "start_time": row.start_time, "end_time": row.end_time,
        "status": row.status, "display_label": row.display_label,
        "accessibility_label": row.accessibility_label, "warnings": row.warnings,
    } for row in snapshot.rows)
    return {
        "schema_version": VERSION,
        "heading": "Appointments",
        "columns": _COLUMNS,
        "items": rows,
        "warnings": snapshot.warnings,
        "affordances": {"create": False, "update": False, "cancel": False, "confirm": False},
        "read_only": True,
    }


def render_fallback(raw: Any, context: Any) -> dict[str, Any]:
    """Revalidate raw data; invalid input yields a generic empty inert view."""
    try:
        return render_view(raw, context)
    except ProjectionRejected:
        return {
            "schema_version": VERSION,
            "heading": "Appointments",
            "columns": _COLUMNS,
            "items": (),
            "warnings": (),
            "affordances": {"create": False, "update": False, "cancel": False, "confirm": False},
            "read_only": True,
            "unavailable_reason": "PROJECTION_UNAVAILABLE",
        }
