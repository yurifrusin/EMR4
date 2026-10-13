"""Inert, pure Stage 1 synthetic patient-request boundary.

The future server route must supply current tenant-scoped request facts and
verify the bearer against its stored digest. This module cannot authenticate
the holder, query availability, reserve a slot, or create an appointment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import hashlib
import hmac
import re
import uuid
from typing import Any


VERSION = "patient.request_submission.v1"
RECOVERY_HOURS = 24
_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
_CLOCK = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d\Z")
_TOKEN = re.compile(r"[0-9a-f]{64}\Z")
_RAW_FIELDS = {
    "schema_version", "request_id", "request_version", "date",
    "earliest_local", "latest_local", "reason_code", "authority",
}
_CONTEXT_FIELDS = {
    "request_id", "request_version", "state", "allowed_dates",
    "minimum_local", "maximum_local", "expires_at", "as_of",
}


class RequestRejected(ValueError):
    """Fixed, non-disclosing rejection code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _reject(code: str) -> None:
    raise RequestRejected(code)


def _uuid(value: Any) -> str:
    if type(value) is not str:
        _reject("REQUEST_ID_INVALID")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        _reject("REQUEST_ID_INVALID")
    if str(parsed) != value:
        _reject("REQUEST_ID_INVALID")
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
        _reject("DATE_INVALID")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        _reject("DATE_INVALID")
    if parsed.isoformat() != value:
        _reject("DATE_INVALID")
    return value


def _clock(value: Any) -> str:
    if type(value) is not str or not _CLOCK.fullmatch(value):
        _reject("TIME_INVALID")
    return value


@dataclass(frozen=True)
class Submission:
    request_id: str
    request_version: int
    date: str
    earliest_local: str
    latest_local: str
    reason_code: str


def validate_submission(raw: Any, trusted_context: Any) -> Submission:
    """Validate only a request preference, never a create command."""
    if type(raw) is not dict or set(raw) != _RAW_FIELDS:
        _reject("STRUCTURE_INVALID")
    if type(trusted_context) is not dict or set(trusted_context) != _CONTEXT_FIELDS:
        _reject("CONTEXT_INVALID")
    if raw["schema_version"] != VERSION or raw["authority"] != "request_only":
        _reject("AUTHORITY_INVALID")
    request_id = _uuid(trusted_context["request_id"])
    if raw["request_id"] != request_id:
        _reject("REQUEST_SCOPE_MISMATCH")
    version = trusted_context["request_version"]
    if type(version) is not int or version < 1:
        _reject("REVISION_INVALID")
    if type(raw["request_version"]) is not int or raw["request_version"] != version:
        _reject("REVISION_MISMATCH")
    state = trusted_context["state"]
    if type(state) is not str or state != "draft":
        _reject("STATE_INVALID")
    now = _instant(trusted_context["as_of"])
    if now >= _instant(trusted_context["expires_at"]):
        _reject("CAPABILITY_EXPIRED")
    allowed = trusted_context["allowed_dates"]
    if (
        type(allowed) is not list or not 1 <= len(allowed) <= 7
        or any(_date(item) != item for item in allowed)
        or allowed != sorted(set(allowed))
    ):
        _reject("CONTEXT_INVALID")
    selected = _date(raw["date"])
    if selected not in allowed:
        _reject("DATE_NOT_ALLOWED")
    earliest = _clock(raw["earliest_local"])
    latest = _clock(raw["latest_local"])
    floor = _clock(trusted_context["minimum_local"])
    ceiling = _clock(trusted_context["maximum_local"])
    if not floor <= earliest < latest <= ceiling:
        _reject("WINDOW_INVALID")
    if raw["reason_code"] != "follow_up":
        _reject("REASON_UNSUPPORTED")
    return Submission(request_id, version, selected, earliest, latest, "follow_up")


def capability_digest(token: Any, secret: bytes) -> str:
    """Domain-separated digest for a server-generated 256-bit random bearer."""
    if type(token) is not str or not _TOKEN.fullmatch(token):
        _reject("CAPABILITY_INVALID")
    if type(secret) is not bytes or len(secret) < 32:
        _reject("CONTEXT_INVALID")
    return hmac.new(
        secret, b"emr4.stage1.patient-request.v1\x00" + bytes.fromhex(token),
        hashlib.sha256,
    ).hexdigest()


def capability_matches(token: Any, stored_digest: Any, secret: bytes) -> bool:
    if type(stored_digest) is not str or not _TOKEN.fullmatch(stored_digest):
        _reject("CONTEXT_INVALID")
    return hmac.compare_digest(capability_digest(token, secret), stored_digest)


def read_access_window(
    *,
    state: str,
    capability_expires_at: str,
    booked_at: str | None,
    as_of: str,
) -> str:
    """Return the permitted read window after separate bearer verification.

    An expired bearer never regains submit/cancel/options authority. Only a
    booked request may expose its own bounded result for 24 further hours.
    """
    if type(state) is not str or state not in {"draft", "submitted", "booked", "cancelled", "expired"}:
        _reject("STATE_INVALID")
    now = _instant(as_of)
    expires = _instant(capability_expires_at)
    if state == "booked":
        if booked_at is None:
            _reject("STATE_INVALID")
        booked = _instant(booked_at)
        if booked > now or booked > expires:
            _reject("STATE_INVALID")
        if now <= booked + timedelta(hours=RECOVERY_HOURS):
            return "booked_readback"
        _reject("CAPABILITY_EXPIRED")
    elif booked_at is not None:
        _reject("STATE_INVALID")
    if now < expires:
        return "request_read"
    _reject("CAPABILITY_EXPIRED")
