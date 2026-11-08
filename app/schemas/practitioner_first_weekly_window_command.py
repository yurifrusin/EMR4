"""STOPPED/default-off first weekly window contracts; no bookability claim.

Only an exact committed practitioner-CREATE receipt and explicit selected-practice
location/calendar values are eligible. Storage remains PractitionerSchedule.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from pydantic import field_validator, model_validator

CANONICALIZATION_VERSION = "practitioner.first_weekly_window.body.v1"
CONFIRMATION_PURPOSE = "practitioner_first_weekly_window_confirm"
CONFIRMATION_SCHEMA = "practitioner.first_weekly_window.confirmation.v1"
EVIDENCE_VERSION = "bernie.confirmation_evidence.v1"
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_CLOCK = re.compile(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]\Z")
_ZONE = re.compile(r"[A-Za-z0-9._+/-]{1,50}\Z")


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _uuid(value):
    if type(value) is UUID:
        return value
    if type(value) is not str:
        raise ValueError("canonical UUID required")
    result = UUID(value)
    if str(result) != value:
        raise ValueError("canonical UUID required")
    return result


def _clock(value):
    if type(value) is not str or not _CLOCK.fullmatch(value):
        raise ValueError("HH:MM clock required; overnight windows are not supported")
    return value


def _zone(value):
    if type(value) is not str or not _ZONE.fullmatch(value):
        raise ValueError("explicit practice zone required")
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("valid practice zone required") from None
    return value


def _minutes(value):
    return int(value[:2]) * 60 + int(value[3:])


class FirstWeeklyWindowBody(ClosedModel):
    practitioner_id: UUID
    practitioner_create_command_id: UUID
    practitioner_create_command_key: UUID
    location_id: UUID
    weekday: StrictInt = Field(ge=0, le=6)
    start_time: StrictStr
    end_time: StrictStr
    slot_duration_minutes: StrictInt = Field(ge=1, le=1440)
    practice_timezone: StrictStr

    @field_validator("practitioner_id", "practitioner_create_command_id",
                     "practitioner_create_command_key", "location_id", mode="before")
    @classmethod
    def identifiers(cls, value):
        return _uuid(value)

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def clocks(cls, value):
        return _clock(value)

    @field_validator("practice_timezone", mode="before")
    @classmethod
    def explicit_zone(cls, value):
        return _zone(value)

    @model_validator(mode="after")
    def positive_grid(self):
        width = _minutes(self.end_time) - _minutes(self.start_time)
        if width <= 0 or self.slot_duration_minutes > width:
            raise ValueError("positive same-day window containing a full grid slot required")
        return self


def canonical_first_weekly_window_body(body: FirstWeeklyWindowBody):
    if type(body) is not FirstWeeklyWindowBody:
        raise ValueError("typed first weekly window required")
    # A fresh dict revalidates even a caller using model_construct.
    checked = FirstWeeklyWindowBody.model_validate({
        "practitioner_id": body.practitioner_id,
        "practitioner_create_command_id": body.practitioner_create_command_id,
        "practitioner_create_command_key": body.practitioner_create_command_key,
        "location_id": body.location_id, "weekday": body.weekday,
        "start_time": body.start_time, "end_time": body.end_time,
        "slot_duration_minutes": body.slot_duration_minutes,
        "practice_timezone": body.practice_timezone,
    })
    value = checked.model_dump(mode="json")
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False,
                           allow_nan=False, separators=(",", ":"))
    return value, canonical, hashlib.sha256(canonical.encode("utf-8", errors="strict")).hexdigest()


class PrepareFirstWeeklyWindow(ClosedModel):
    command_key: UUID
    body: FirstWeeklyWindowBody

    @field_validator("command_key", mode="before")
    @classmethod
    def identifier(cls, value):
        return _uuid(value)


class ConfirmFirstWeeklyWindow(ClosedModel):
    command_key: UUID
    command_id: UUID
    body_digest: StrictStr
    context_digest: StrictStr
    signed_confirmation_evidence: dict[str, Any]
    confirmed: StrictBool

    @field_validator("command_key", "command_id", mode="before")
    @classmethod
    def identifiers(cls, value):
        return _uuid(value)

    @field_validator("body_digest", "context_digest")
    @classmethod
    def digests(cls, value):
        if not _DIGEST.fullmatch(value):
            raise ValueError("SHA-256 required")
        return value

    @field_validator("confirmed")
    @classmethod
    def separate_confirmation(cls, value):
        if value is not True:
            raise ValueError("separate confirmation required")
        return value


class FirstWeeklyWindowDraft(ClosedModel):
    command_id: UUID
    command_key: UUID
    canonicalization_version: Literal["practitioner.first_weekly_window.body.v1"]
    body: FirstWeeklyWindowBody
    body_digest: StrictStr
    context_digest: StrictStr
    role: Literal["PracticeOwner"]
    authority_generation: StrictInt
    expires_at: StrictStr


class FirstWeeklyWindowReceipt(ClosedModel):
    schema_version: Literal["practitioner.first_weekly_window.receipt.v1"]
    command_id: UUID
    command_key: UUID
    practice_id: UUID
    practitioner_id: UUID
    location_id: UUID
    schedule_id: UUID
    body: FirstWeeklyWindowBody
    body_digest: StrictStr
    context_digest: StrictStr
    actor_account_id: UUID
    actor_membership_id: UUID
    actor_user_id: UUID
    role: Literal["PracticeOwner"]
    authority_generation: StrictInt
    audit_event_id: UUID
    outbox_event_id: UUID
    committed_at: StrictStr


class PrepareFirstWeeklyWindowResult(ClosedModel):
    state: Literal["prepared", "committed"]
    draft: FirstWeeklyWindowDraft | None = None
    receipt: FirstWeeklyWindowReceipt | None = None
    confirmation_evidence: dict[str, Any] | None = None

    @model_validator(mode="after")
    def terminal_shape(self):
        if self.state == "committed":
            if self.receipt is None or self.draft is not None or self.confirmation_evidence is not None:
                raise ValueError("committed receipt shape required")
        elif self.draft is None or self.receipt is not None:
            raise ValueError("prepared draft shape required")
        return self


class FirstWeeklyWindowCurrent(ClosedModel):
    schedule_id: UUID
    practitioner_id: UUID
    location_id: UUID | None
    weekday: StrictInt
    start_time: StrictStr
    end_time: StrictStr
    slot_duration_minutes: StrictInt | None
    practice_timezone: StrictStr | None
    practitioner_active: StrictBool | None
    location_active: StrictBool | None


class FirstWeeklyWindowReadback(ClosedModel):
    status: Literal["matches_created", "diverged", "missing"]
    expected: FirstWeeklyWindowBody
    current: FirstWeeklyWindowCurrent | None


class FirstWeeklyWindowRecovery(ClosedModel):
    receipt: FirstWeeklyWindowReceipt
    readback: FirstWeeklyWindowReadback


class FirstWeeklyWindowContextRequest(ClosedModel):
    practitioner_create_command_key: UUID
    location_create_command_key: UUID

    @field_validator("practitioner_create_command_key", "location_create_command_key", mode="before")
    @classmethod
    def identifiers(cls, value):
        return _uuid(value)


class FirstWeeklyWindowContext(ClosedModel):
    schema_version: Literal["practitioner.first_weekly_window.context.v1"]
    practice_id: UUID
    practitioner_id: UUID
    practitioner_create_command_id: UUID
    practitioner_create_command_key: UUID
    location_id: UUID
    location_create_command_id: UUID
    location_create_command_key: UUID
    practice_timezone: StrictStr
    practitioner_active: StrictBool
    location_active: StrictBool
    role: Literal["PracticeOwner"]
    authority_generation: StrictInt = Field(ge=1)

    @field_validator("practice_id", "practitioner_id", "practitioner_create_command_id",
                     "practitioner_create_command_key", "location_id", "location_create_command_id",
                     "location_create_command_key", mode="before")
    @classmethod
    def identifiers(cls, value):
        return _uuid(value)

    @field_validator("practice_timezone", mode="before")
    @classmethod
    def practice_zone(cls, value):
        return _zone(value)

    @field_validator("practitioner_active", "location_active")
    @classmethod
    def active_resources(cls, value):
        if value is not True:
            raise ValueError("active same-practice resources required")
        return value
