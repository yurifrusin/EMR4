"""Proposed read-only Stage 1 staff Diary adapter; not wired into the active app.

The caller must obtain the body from the authenticated, tenant-filtered,
unpaginated GET /api/v1/appointments route pinned in the handoff. This module
does not authenticate the actor. A changed route/transport requires review.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import json
from typing import Any
from urllib.parse import urlencode
import uuid

from app.services.appointment_list_projection import (
    ProjectionRejected, V2_VERSION, render_fallback_v2, render_view_v2,
)

MAX_ROWS = 32
MAX_DAYS = 7
MAX_REPLY_BYTES = 262144  # Existing child transport cap; do not raise here.
# The admitted synthetic practice and server clock are fixed to Brisbane UTC+10.
# Python zoneinfo data is not part of the pinned isolated Windows runtime.
ZONE = "Australia/Brisbane"
PRACTICE_TZ = timezone(timedelta(hours=10))
STATUSES = frozenset((
    "Booked", "Confirmed", "Arrived", "InConsult", "Completed",
    "Cancelled", "NoShow", "DNA",
))


class DiaryReadRejected(ValueError):
    pass


def _reject() -> None:
    raise DiaryReadRejected("DIARY_READ_UNAVAILABLE")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _reject()
        result[key] = value
    return result


def _constant(_: str) -> None:
    _reject()


def _uuid(value: Any) -> str:
    if type(value) is not str:
        _reject()
    try:
        result = str(uuid.UUID(value))
    except (ValueError, AttributeError):
        _reject()
    if result != value:
        _reject()
    return result


def _instant(value: Any) -> datetime:
    if type(value) is not str:
        _reject()
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _reject()
    if result.tzinfo is None or result.utcoffset() is None or result.microsecond:
        _reject()
    return result.astimezone(timezone.utc)


def _utc(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _day(value: Any) -> date:
    if type(value) is not str or len(value) != 10:
        _reject()
    try:
        result = date.fromisoformat(value)
    except ValueError:
        _reject()
    if result.isoformat() != value:
        _reject()
    return result


def _window(start: Any, end: Any, zone_name: Any) -> tuple[date, date, timezone]:
    first, last = _day(start), _day(end)
    if not 1 <= (last - first).days <= MAX_DAYS:
        _reject()
    if zone_name != ZONE:
        _reject()
    return first, last, PRACTICE_TZ


def list_path(date_from: str, date_to: str, practice_timezone: str) -> str:
    """Build the exact reviewed exclusive-end query for at most seven local days."""
    first, last, zone = _window(date_from, date_to, practice_timezone)
    begin = datetime.combine(first, time.min, zone)
    finish = datetime.combine(last, time.min, zone)
    return "/api/v1/appointments?" + urlencode({
        "date_from": begin.isoformat(timespec="seconds"),
        "date_to": finish.isoformat(timespec="seconds"),
    })


def _name(value: Any) -> str:
    if (type(value) is not str or not value or len(value) > 120
            or value != value.strip() or any(ord(ch) < 32 for ch in value)):
        _reject()
    return value


def _person(value: Any, expected_id: str) -> str:
    if type(value) is not dict or _uuid(value.get("id")) != expected_id:
        _reject()
    return _name(value.get("first_name")) + " " + _name(value.get("last_name"))


def _row(value: Any, tenant_id: str, first: date, last: date,
         zone: timezone) -> tuple[dict[str, Any], dict[str, Any]]:
    if type(value) is not dict or _uuid(value.get("practice_id")) != tenant_id:
        _reject()
    item_id = _uuid(value.get("id"))
    practitioner_id = _uuid(value.get("practitioner_id"))
    practitioner_name = _person(value.get("practitioner"), practitioner_id)
    patient_id = value.get("patient_id")
    patient = value.get("patient")
    provisional = value.get("patient_name_provisional")
    if patient_id is None:
        if patient is not None:
            _reject()
        patient_name = _name(provisional) if provisional is not None else None
    else:
        patient_id = _uuid(patient_id)
        patient_name = _person(patient, patient_id)
        if provisional is not None:
            _reject()
    appointment_type = value.get("appointment_type")
    appointment_type_id = value.get("appointment_type_id")
    if appointment_type_id is None:
        if appointment_type is not None:
            _reject()
        appointment_type_name = None
    else:
        appointment_type_id = _uuid(appointment_type_id)
        if (type(appointment_type) is not dict
                or _uuid(appointment_type.get("id")) != appointment_type_id):
            _reject()
        appointment_type_name = _name(appointment_type.get("name"))
    start, end = _instant(value.get("start_time")), _instant(value.get("end_time"))
    if not (first <= start.astimezone(zone).date() < last):
        _reject()
    if value.get("appointment_date") != start.astimezone(zone).date().isoformat():
        _reject()
    if value.get("start_time_local") != start.astimezone(zone).time().isoformat(timespec="seconds"):
        _reject()
    duration = value.get("duration_minutes")
    if (type(duration) is not int or not 1 <= duration <= 480
            or end - start != timedelta(minutes=duration)):
        _reject()
    version = value.get("appointment_state_version")
    if type(version) is not int or version < 1:
        _reject()
    status = value.get("status")
    if type(status) is not str or status not in STATUSES:
        _reject()
    start_text, end_text = _utc(start), _utc(end)
    detail = {
        "id": item_id, "practice_id": tenant_id, "source_version": version,
        "practitioner_id": practitioner_id, "practitioner_name": practitioner_name,
        "patient_id": patient_id, "patient_name": patient_name,
        "appointment_type_id": appointment_type_id,
        "appointment_type_name": appointment_type_name,
        "start_time": start_text, "end_time": end_text,
        "duration_minutes": duration, "status": status,
    }
    return detail, {"id": item_id, "practice_id": tenant_id,
                    "source_version": version, "start_time": start_text,
                    "end_time": end_text, "status": status}


def unavailable() -> dict[str, Any]:
    """A rejected response contributes no raw fields or appointment facts."""
    return {"schema_version": "staff_diary_read.v1", "state": "unavailable",
            "items": (), "source": None, "window": None,
            "qualification": "appointments_only_no_availability",
            "read_only": True, "availability_authority": False}


def render_staff_diary_read(
    body: bytes, *, status_code: int, content_type: str,
    tenant_id: str, actor_id: str, authenticated_role: str,
    date_from: str, date_to: str, practice_timezone: str,
    captured_at: str, as_of: str, fallback: bool = False,
) -> dict[str, Any]:
    """Validate a whole authenticated GET result, then render normal/fallback.

    ``authenticated_role`` and identity must come from server-owned session
    context. ``captured_at`` is when the full response was received, not when
    this function happened to be called. Caller must not refresh that timestamp
    for an old response. This view never grants create/confirm/availability.
    """
    try:
        if authenticated_role != "Receptionist":
            _reject()
        tenant_id, actor_id = _uuid(tenant_id), _uuid(actor_id)
        first, last, zone = _window(date_from, date_to, practice_timezone)
        if (type(body) is not bytes or len(body) > MAX_REPLY_BYTES
                or status_code != 200 or type(content_type) is not str
                or not content_type.lower().startswith("application/json")):
            _reject()
        received = _instant(captured_at)
        now = _instant(as_of)
        if not timedelta(0) <= now - received <= timedelta(seconds=300):
            _reject()
        rows = json.loads(body.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=_constant)
        if type(rows) is not list or len(rows) > MAX_ROWS:
            _reject()
        details, v2_rows = [], []
        seen: set[str] = set()
        for value in rows:
            detail, basic = _row(value, tenant_id, first, last, zone)
            if detail["id"] in seen:
                _reject()
            seen.add(detail["id"])
            details.append(detail)
            v2_rows.append(basic)
        paired = sorted(zip(details, v2_rows), key=lambda pair: (
            pair[1]["start_time"], pair[1]["id"]))
        capture_id = str(uuid.uuid4())
        raw_items = []
        for index, (_, basic) in enumerate(paired, 1):
            label = f"Appointment {index}"
            raw_items.append({**basic, "display_label": label,
                "accessibility_label": (
                    f"{label}; starts {basic['start_time']}; ends {basic['end_time']}; "
                    f"status {basic['status']}; timezone {practice_timezone}"),
                "warnings": []})
        raw = {"schema_version": V2_VERSION, "tenant_id": tenant_id,
               "actor_id": actor_id, "role": "reception", "source_id": capture_id,
               "source_revision": 1, "captured_at": _utc(received),
               "practice_timezone": practice_timezone, "total_count": len(raw_items),
               "is_complete": True, "authority": "read_only",
               "heading": "Appointments", "columns": ["Start", "End", "Status", "Appointment"],
               "items": raw_items, "warnings": []}
        context = {"tenant_id": tenant_id, "actor_id": actor_id,
                   "role": "reception", "read_capability": "appointments.read",
                   "source_id": capture_id, "source_revision": 1,
                   "as_of": _utc(now), "practice_timezone": practice_timezone,
                   "expected_total": len(raw_items)}
        view = render_fallback_v2(raw, context) if fallback else render_view_v2(raw, context)
        if view.get("unavailable_reason") or len(view["items"]) != len(paired):
            _reject()
        return {"schema_version": "staff_diary_read.v1", "state": "complete",
                "window": {"date_from": date_from, "date_to": date_to,
                           "practice_timezone": practice_timezone},
                "captured_at": _utc(received),
                "source": {"id": capture_id, "revision": 1,
                           "kind": "immutable_capture", "total_count": len(paired)},
                "items": tuple(pair[0] for pair in paired), "read_only": True,
                "qualification": "appointments_only_no_availability",
                "availability_authority": False}
    except (DiaryReadRejected, ProjectionRejected, ValueError, UnicodeError, TypeError,
            KeyError, OverflowError, json.JSONDecodeError):
        return unavailable()
