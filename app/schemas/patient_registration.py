"""Pure minimal fictional registration contracts; no config, engine or I/O."""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
import re
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, field_validator, model_validator

CANONICALIZATION_VERSION = "patient.registration.body.v1"
CONFIRMATION_PURPOSE = "patient_registration.confirm.v1"


class _Closed(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RegistrationBody(_Closed):
    first_name: str
    last_name: str
    date_of_birth: date
    distinct_person: StrictBool = False

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def names(cls, value):
        if type(value) is not str:
            raise ValueError("name must be text")
        if any(ord(c) < 32 or ord(c) == 127 for c in value):
            raise ValueError("control characters are not names")
        value = value.strip()
        if not 1 <= len(value) <= 100:
            raise ValueError("bounded nonempty name required")
        return value

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def dob(cls, value):
        if type(value) is str:
            if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
                raise ValueError("ISO date required")
            value = date.fromisoformat(value)
        if type(value) is not date or value > datetime.now(timezone.utc).date():
            raise ValueError("nonfuture date required")
        return value


def canonical_registration_body(body: RegistrationBody) -> tuple[dict[str, Any], str, str]:
    if type(body) is not RegistrationBody:
        raise ValueError("exact registration body required")
    primitive = {"canonicalization_version": CANONICALIZATION_VERSION,
                 **body.model_dump(mode="json")}
    raw = json.dumps(primitive, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False)
    return primitive, raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


class PrepareRegistration(_Closed):
    command_key: UUID
    body: RegistrationBody
    new_registration: StrictBool
    registration_intent_id: UUID | None = None
    supersedes_command_id: UUID | None = None
    supersedes_revision: StrictInt | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def context(self):
        links = (self.registration_intent_id, self.supersedes_command_id, self.supersedes_revision)
        if self.new_registration:
            if any(x is not None for x in links):
                raise ValueError("a new intent has no predecessor")
        elif any(x is None for x in links):
            raise ValueError("correction requires current intent, predecessor and revision")
        return self


class ConfirmRegistration(_Closed):
    command_key: UUID
    command_id: UUID
    registration_intent_id: UUID
    draft_revision: StrictInt = Field(ge=1)
    body_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    confirmed: StrictBool
    signed_confirmation_evidence: dict[str, Any]

    @field_validator("confirmed")
    @classmethod
    def explicit_confirmation(cls, value):
        if value is not True:
            raise ValueError("separate explicit confirmation required")
        return value


class PatientDemographics(_Closed):
    id: UUID
    practice_id: UUID
    first_name: str
    last_name: str
    date_of_birth: date


class RegistrationReceipt(_Closed):
    schema_version: Literal["patient.registration.receipt.v1"]
    command_id: UUID
    command_key: UUID
    registration_intent_id: UUID
    draft_revision: int
    practice_id: UUID
    patient_id: UUID
    actor_account_id: UUID
    actor_membership_id: UUID
    actor_user_id: UUID
    role: str
    authority_generation: int
    body_digest: str
    audit_event_id: UUID
    created_at: str


class RegistrationDraft(_Closed):
    command_id: UUID
    command_key: UUID
    registration_intent_id: UUID
    draft_revision: int
    body: dict[str, Any]
    body_digest: str
    role: str
    authority_generation: int
    expires_at: str
    advisory_matches: list[PatientDemographics]
    requires_distinct_person_decision: bool


class PrepareRegistrationResult(_Closed):
    state: Literal["prepared", "committed"]
    draft: RegistrationDraft | None = None
    receipt: RegistrationReceipt | None = None
    confirmation_evidence: dict[str, Any] | None = None
