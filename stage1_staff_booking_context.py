"""Uninstalled read-only selected-staff context; no booking or runtime authority."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import json
import re
import secrets
from typing import Awaitable, Callable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from stage1_seeded_login import COOKIE, SeededLoginController, _Denied, _Unavailable, _reply
from stage1_patient_browser import _patient, _uuid


@dataclass(frozen=True, repr=False)
class StaffBookingContextBinding:
    practice_id: str
    practitioner_id: str
    fixture_day: date
    duration_minutes: int
    max_slots: int
    practice_context: Callable[..., Awaitable]
    patient_read: Callable[..., Awaitable]
    practitioners: Callable[..., Awaitable]
    fixture_attestation: Callable[..., Awaitable]
    slots: Callable[..., Awaitable]
    enabled: bool = False


def _local_instant(value: datetime, zone: ZoneInfo) -> datetime:
    """Require a unique existent local wall time by two-fold UTC round trips."""
    if value.tzinfo is not None:
        raise _Denied()
    instants = set()
    for fold in (0, 1):
        candidate = value.replace(tzinfo=zone, fold=fold)
        instant = candidate.astimezone(timezone.utc)
        if instant.astimezone(zone).replace(tzinfo=None) == value:
            instants.add(instant)
    if len(instants) != 1:
        raise _Denied()
    return next(iter(instants))


def _local_datetime(value):
    if type(value) is not str or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}", value):
        raise _Denied()
    try:
        result = datetime.fromisoformat(value)
    except ValueError:
        raise _Denied() from None
    if result.tzinfo is not None or result.isoformat(timespec="seconds") != value:
        raise _Denied()
    return result


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


class StaffBookingContextBridge:
    def __init__(self, controller, binding):
        if (type(controller) is not SeededLoginController
                or type(binding) is not StaffBookingContextBinding or binding.enabled is not True
                or not _uuid(binding.practice_id) or not _uuid(binding.practitioner_id)
                or type(binding.fixture_day) is not date
                or type(binding.duration_minutes) is not int or not 1 <= binding.duration_minutes <= 180
                or type(binding.max_slots) is not int or not 1 <= binding.max_slots <= 32
                or any(not callable(getattr(binding, name)) for name in (
                    "practice_context", "patient_read", "practitioners", "fixture_attestation", "slots"))):
            raise ValueError("staff booking context disabled")
        self.controller, self.binding, self._closed = controller, binding, False
        self._diagnostic_first_refusal = None

    def refusal_diagnostic_snapshot(self):
        recorded = self._diagnostic_first_refusal
        if recorded is None:
            return {"sample":"BEFORE_SERVER_DRAIN","state":"NO_REFUSAL_RECORDED",
                "stage":"NONE","callback":"NONE","callback_status":"NOT_OBSERVED","refusal_class":None}
        stage,callback,callback_status,refusal_class = recorded
        return {"sample":"BEFORE_SERVER_DRAIN","state":"REFUSED","stage":stage,
            "callback":callback,"callback_status":callback_status,"refusal_class":refusal_class}

    async def handle(self, request):
        diagnostic_stage = "NONE"
        diagnostic_callback = "NONE"
        diagnostic_callback_status = "NOT_OBSERVED"
        key = request.cookies.get(COOKIE, "")
        value = self.controller.sessions.get(key)
        try:
            diagnostic_stage = "ENVELOPE"
            if (self._closed or value is None or request.method != "POST" or request.url.query
                    or request.headers.get("authorization") is not None
                    or request.headers.get("origin") != request.app.state.seeded_login_origin
                    or request.headers.get("content-type") != "application/json"
                    or not secrets.compare_digest(request.headers.get("x-csrf-token", ""), value.csrf)):
                raise _Denied()
            async with value.lock:
                diagnostic_stage = "SESSION_CURRENT"
                self.controller._require_current(key, value)
                diagnostic_stage = "BODY_READ"
                chunks, size = [], 0
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > 4096:
                        raise _Denied()
                    chunks.append(chunk)
                diagnostic_stage = "BODY_CURRENT"
                self.controller._require_current(key, value)
                diagnostic_stage = "BODY_DECODE"
                try:
                    body = json.loads(b"".join(chunks), object_pairs_hook=_pairs,
                                      parse_constant=lambda _v: (_ for _ in ()).throw(ValueError()))
                except (ValueError, UnicodeDecodeError):
                    raise _Denied() from None
                diagnostic_stage = "BODY_SHAPE"
                if (type(body) is not dict or set(body) != {"patient_id", "date", "duration_minutes"}
                        or not _uuid(body["patient_id"]) or type(body["date"]) is not str
                        or body["date"] != self.binding.fixture_day.isoformat()
                        or type(body["duration_minutes"]) is not int
                        or body["duration_minutes"] != self.binding.duration_minutes):
                    raise _Denied()
                diagnostic_stage = "SELECTION"
                tenant, selected, staff = value.tenant, value.selected, value.staff_session
                if not tenant or type(selected) is not dict:
                    raise _Denied()
                selected_copy = dict(selected)
                def same():
                    if self._closed:
                        raise _Denied()
                    self.controller._require_current(key, value)
                    if (value.tenant != tenant or value.selected is not selected
                            or value.selected != selected_copy or value.staff_session is not staff):
                        raise _Denied()
                diagnostic_stage = "INITIAL_SAME"
                same()
                diagnostic_stage = "INITIAL_CURRENT"
                role = await self.controller._current(value, key=key, expected=value)
                diagnostic_stage = "INITIAL_CURRENT_POST"
                same()
                diagnostic_stage = "AUTHORITY"
                authority = value.patient_current_authority
                if (role != "InvitedReceptionist" or type(authority) is not dict
                        or set(authority) != {"account_id", "membership_id", "user_id", "practice_id", "role", "authority_generation"}
                        or authority["practice_id"] != self.binding.practice_id
                        or selected_copy.get("practice_id") != self.binding.practice_id
                        or authority["role"] != "Receptionist"
                        or authority["user_id"] == self.binding.practitioner_id):
                    raise _Denied()
                authority = dict(authority)
                async def call(callback, callback_name, completion_stage, **kwargs):
                    nonlocal diagnostic_stage, diagnostic_callback, diagnostic_callback_status
                    diagnostic_callback = callback_name
                    diagnostic_callback_status = "NOT_OBSERVED"
                    diagnostic_stage = "READ_PRE_SAME"
                    same()
                    diagnostic_stage = "READ_EXCHANGE"
                    async def observed_callback(**callback_kwargs):
                        nonlocal diagnostic_callback_status
                        diagnostic_callback_status = "NOT_RETURNED"
                        response = await callback(**callback_kwargs)
                        try:
                            status = response.status_code
                            diagnostic_callback_status = {
                                200:"HTTP_200",400:"HTTP_400",401:"HTTP_401",403:"HTTP_403",
                                404:"HTTP_404",409:"HTTP_409",422:"HTTP_422",500:"HTTP_500",
                                503:"HTTP_503"}.get(status,"HTTP_OTHER") if type(status) is int else "HTTP_OTHER"
                        except BaseException:
                            diagnostic_callback_status = "UNAVAILABLE"
                        return response
                    result = await self.controller._call(observed_callback, tenant_bearer=tenant, **kwargs)
                    diagnostic_stage = "READ_POST_SAME"
                    same()
                    diagnostic_stage = "READ_ACCOUNT_CURRENT"
                    role_after = await self.controller._current(value, key=key, expected=value)
                    diagnostic_stage = "READ_ACCOUNT_POST"
                    same()
                    diagnostic_stage = "READ_AUTHORITY"
                    if role_after != role or value.patient_current_authority != authority:
                        raise _Denied()
                    diagnostic_stage = completion_stage
                    return result

                context = await call(self.binding.practice_context, "PRACTICE_CONTEXT", "PRACTICE_SHAPE")
                if (type(context) is not dict or set(context) != {"practice_id", "timezone"}
                        or context["practice_id"] != self.binding.practice_id
                        or type(context["timezone"]) is not str or not context["timezone"]
                        or context["timezone"] != context["timezone"].strip()):
                    raise _Denied()
                diagnostic_stage = "ZONE_LOAD"
                try:
                    zone = ZoneInfo(context["timezone"])
                except (ZoneInfoNotFoundError, ValueError):
                    raise _Denied() from None
                diagnostic_stage = "ZONE_ROUNDTRIP"
                midnight = datetime.combine(self.binding.fixture_day, time.min)
                midnight_utc = _local_instant(midnight, zone)
                aware_midnight = midnight_utc.astimezone(zone)
                if aware_midnight.date() != self.binding.fixture_day:
                    raise _Denied()
                query_date = aware_midnight.isoformat(timespec="seconds")
                patient = _patient(await call(self.binding.patient_read, "PATIENT_READ", "PATIENT_SHAPE", patient_id=body["patient_id"]), self.binding.practice_id)
                if patient["id"] != body["patient_id"]:
                    raise _Denied()
                rows = await call(self.binding.practitioners, "PRACTITIONERS", "PRACTITIONER_SHAPE", active_only=True, limit=2, offset=0)
                if type(rows) is not list or len(rows) != 1 or type(rows[0]) is not dict:
                    raise _Denied()
                practitioner = rows[0]
                if (set(practitioner) != {"id", "displayName", "roleLabel", "active", "defaultLocation"}
                        or practitioner["id"] != self.binding.practitioner_id
                        or type(practitioner["displayName"]) is not str
                        or not 1 <= len(practitioner["displayName"]) <= 201
                        or practitioner["displayName"] != practitioner["displayName"].strip()
                        or any(ord(c) < 32 or ord(c) == 127 for c in practitioner["displayName"])
                        or (practitioner["roleLabel"] is not None and (type(practitioner["roleLabel"]) is not str
                            or len(practitioner["roleLabel"]) > 100
                            or any(ord(c) < 32 or ord(c) == 127 for c in practitioner["roleLabel"])))
                        or practitioner["active"] is not True or practitioner["defaultLocation"] is not None):
                    raise _Denied()
                # Trusted read-only callback must attest the exact fixture and no override
                # before invoking the backend's otherwise uncapped schedule loop.
                attestation = await call(self.binding.fixture_attestation, "FIXTURE_ATTESTATION", "ATTESTATION_SHAPE",
                    practitioner_id=self.binding.practitioner_id, date=self.binding.fixture_day.isoformat())
                if (type(attestation) is not dict or set(attestation) != {"practice_id", "practitioner_id", "date",
                        "start_time", "end_time", "slot_minutes", "location_id", "override_absent"}
                        or attestation["practice_id"] != self.binding.practice_id
                        or attestation["practitioner_id"] != self.binding.practitioner_id
                        or attestation["date"] != self.binding.fixture_day.isoformat()
                        or attestation["location_id"] is not None or attestation["override_absent"] is not True
                        or type(attestation["slot_minutes"]) is not int
                        or attestation["slot_minutes"] != self.binding.duration_minutes):
                    raise _Denied()
                diagnostic_stage = "ATTESTATION_LOCAL_BOUNDS"
                start = _local_datetime(attestation["start_time"])
                end = _local_datetime(attestation["end_time"])
                if (start.date() != self.binding.fixture_day or end.date() != self.binding.fixture_day
                        or start >= end or (end - start) > timedelta(hours=12)):
                    raise _Denied()
                diagnostic_stage = "ATTESTATION_UTC"
                _local_instant(start, zone)
                _local_instant(end, zone)
                diagnostic_stage = "ATTESTATION_GRID"
                minutes = (end - start).total_seconds() / 60
                if minutes % self.binding.duration_minutes or not 1 <= minutes / self.binding.duration_minutes <= self.binding.max_slots:
                    raise _Denied()
                rows = await call(self.binding.slots, "SLOTS", "SLOTS_SHAPE", practitioner_id=self.binding.practitioner_id, date=query_date)
                if type(rows) is not list or len(rows) > self.binding.max_slots:
                    raise _Denied()
                # Require the complete exact attested grid, not an empty list or prefix.
                if len(rows) != int(minutes / self.binding.duration_minutes):
                    raise _Denied()
                result = []
                diagnostic_stage = "SLOT_ROW"
                for index, row in enumerate(rows):
                    diagnostic_stage = "SLOT_ROW"
                    if (type(row) is not dict or set(row) != {"start_time", "end_time", "available"}
                            or type(row["available"]) is not bool):
                        raise _Denied()
                    first, last = _local_datetime(row["start_time"]), _local_datetime(row["end_time"])
                    if (first != start + timedelta(minutes=index * self.binding.duration_minutes)
                            or last != first + timedelta(minutes=self.binding.duration_minutes)
                            or last > end or first.date() != self.binding.fixture_day
                            or last.date() != self.binding.fixture_day):
                        raise _Denied()
                    diagnostic_stage = "SLOT_UTC"
                    first_utc, last_utc = _local_instant(first, zone), _local_instant(last, zone)
                    if last_utc - first_utc != timedelta(minutes=self.binding.duration_minutes):
                        raise _Denied()
                    result.append({"start_time": row["start_time"], "end_time": row["end_time"],
                                   "available": row["available"]})
                diagnostic_stage = "FINAL_CURRENT"
                same()
                diagnostic_stage = "REPLY"
                return _reply({"state": "ready", "patient": patient,
                    "practitioner": dict(practitioner), "practice_id": self.binding.practice_id,
                    "timezone": context["timezone"], "date": body["date"],
                    "duration_minutes": self.binding.duration_minutes, "slots": result})
        except asyncio.CancelledError:
            raise
        except (_Denied, _Unavailable, KeyError, TypeError, ValueError, OverflowError) as error:
            if self._diagnostic_first_refusal is None:
                caught_type = type(error)
                refusal_class = ("_Denied" if caught_type is _Denied else
                    "_Unavailable" if caught_type is _Unavailable else
                    "KeyError" if caught_type is KeyError else
                    "TypeError" if caught_type is TypeError else
                    "ValueError" if caught_type is ValueError else
                    "OverflowError" if caught_type is OverflowError else "OTHER")
                self._diagnostic_first_refusal = (
                    diagnostic_stage,diagnostic_callback,diagnostic_callback_status,refusal_class)
            return _reply({"detail": "Booking context unavailable."}, 403)

    async def close(self):
        self._closed = True
