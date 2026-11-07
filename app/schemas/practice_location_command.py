"""STOPPED source candidate: typed owner scheduling-location CREATE contracts.

Adds only an active PracticeLocation. No login, membership, clinical privilege,
default-location assignment, working hours or appointment capacity is granted.
Source adoption and every runtime binding remain separate.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from pydantic import field_validator, model_validator

CANONICALIZATION_VERSION = "practice_location.create.body.v1"
CONFIRMATION_PURPOSE = "practice_location_confirm_create"
CONFIRMATION_SCHEMA = "practice_location.create.confirmation.v1"
EVIDENCE_VERSION = "bernie.confirmation_evidence.v1"
# Frozen W1; do not replace with str.strip()'s evolving default character set.
W1 = ("\u0009\u000a\u000b\u000c\u000d\u001c\u001d\u001e\u001f\u0020"
      "\u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006"
      "\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000")
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _uuid(value):
    if type(value) is UUID:
        return value
    if type(value) is not str:
        raise ValueError("canonical UUID required")
    parsed = UUID(value)
    if str(parsed) != value:
        raise ValueError("canonical UUID required")
    return parsed


def _name(value):
    if type(value) is not str:
        raise ValueError("text required")
    value.encode("utf-8", errors="strict")
    value = value.strip(W1)
    if not 1 <= len(value) <= 255 or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("bounded scalar text required")
    return value


class PracticeLocationCreateBody(ClosedModel):
    name: StrictStr

    @field_validator("name", mode="before")
    @classmethod
    def required_name(cls, value):
        return _name(value)


def canonical_practice_location_body(body: PracticeLocationCreateBody):
    if type(body) is not PracticeLocationCreateBody:
        raise ValueError("typed practice location body required")
    # Revalidate callers using model_construct rather than validation.
    value = {"name": _name(body.name)}
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False,
                           allow_nan=False, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8", errors="strict")).hexdigest()
    return value, canonical, digest


class PreparePracticeLocationCreate(ClosedModel):
    command_key: UUID
    body: PracticeLocationCreateBody
    new_intent: StrictBool = True
    create_intent_id: UUID | None = None
    supersedes_command_id: UUID | None = None
    supersedes_revision: StrictInt | None = Field(default=None, ge=1, le=9223372036854775806)

    @field_validator("command_key", "create_intent_id", "supersedes_command_id", mode="before")
    @classmethod
    def identifiers(cls, value):
        return None if value is None else _uuid(value)

    @model_validator(mode="after")
    def predecessor(self):
        linked = (self.create_intent_id, self.supersedes_command_id, self.supersedes_revision)
        if self.new_intent and any(v is not None for v in linked):
            raise ValueError("new intent cannot name a predecessor")
        if not self.new_intent and any(v is None for v in linked):
            raise ValueError("exact predecessor required")
        return self


class ConfirmPracticeLocationCreate(ClosedModel):
    command_key: UUID
    command_id: UUID
    create_intent_id: UUID
    draft_revision: StrictInt = Field(ge=1, le=9223372036854775807)
    body_digest: StrictStr
    signed_confirmation_evidence: dict[str, Any]
    confirmed: StrictBool

    @field_validator("command_key", "command_id", "create_intent_id", mode="before")
    @classmethod
    def identifiers(cls, value):
        return _uuid(value)

    @field_validator("body_digest")
    @classmethod
    def digest(cls, value):
        if not _DIGEST.fullmatch(value):
            raise ValueError("SHA-256 required")
        return value

    @field_validator("confirmed")
    @classmethod
    def separate_confirmation(cls, value):
        if value is not True:
            raise ValueError("separate confirmation required")
        return value


class PracticeLocationCreateDraft(ClosedModel):
    command_id: UUID
    command_key: UUID
    create_intent_id: UUID
    draft_revision: StrictInt
    canonicalization_version: Literal["practice_location.create.body.v1"]
    body: PracticeLocationCreateBody
    body_digest: StrictStr
    role: Literal["PracticeOwner"]
    authority_generation: StrictInt
    expires_at: StrictStr


class PracticeLocationCreateReceipt(ClosedModel):
    schema_version: Literal["practice_location.create.receipt.v1"]
    command_id: UUID
    command_key: UUID
    create_intent_id: UUID
    draft_revision: StrictInt
    practice_id: UUID
    location_id: UUID
    actor_account_id: UUID
    actor_membership_id: UUID
    actor_user_id: UUID
    role: Literal["PracticeOwner"]
    authority_generation: StrictInt
    body_digest: StrictStr
    audit_event_id: UUID
    outbox_event_id: UUID
    committed_at: StrictStr


class PreparePracticeLocationCreateResult(ClosedModel):
    state: Literal["prepared", "committed"]
    draft: PracticeLocationCreateDraft | None = None
    receipt: PracticeLocationCreateReceipt | None = None
    confirmation_evidence: dict[str, Any] | None = None

    @model_validator(mode="after")
    def terminal_shape(self):
        if self.state == "committed":
            if self.receipt is None or self.draft is not None or self.confirmation_evidence is not None:
                raise ValueError("committed receipt shape required")
        elif self.draft is None or self.receipt is not None:
            raise ValueError("prepared draft shape required")
        return self


class PracticeLocationCreatedFacts(ClosedModel):
    name: StrictStr
    is_active: StrictBool

    @field_validator("is_active")
    @classmethod
    def explicitly_active(cls, value):
        if value is not True:
            raise ValueError("created location active flag required")
        return value


class PracticeLocationCurrentFacts(ClosedModel):
    id: UUID
    practice_id: UUID
    name: StrictStr
    is_active: StrictBool | None


class PracticeLocationCreateReadback(ClosedModel):
    status: Literal["matches_created", "diverged", "missing"]
    expected: PracticeLocationCreatedFacts
    current: PracticeLocationCurrentFacts | None


class PracticeLocationCreateRecovery(ClosedModel):
    receipt: PracticeLocationCreateReceipt
    readback: PracticeLocationCreateReadback
