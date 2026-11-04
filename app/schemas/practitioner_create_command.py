"""STOPPED source candidate: typed scheduling-resource CREATE contracts.

These types grant no login, membership, clinical privilege, Diary column or
availability. Source adoption and every runtime binding require separate review.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from pydantic import field_validator, model_validator

CANONICALIZATION_VERSION = "practitioner.create.body.v1"
MATCHING_CONTEXT_VERSION = "practitioner.create.matches.v1"
CONFIRMATION_PURPOSE = "practitioner_confirm_create_resource"
CONFIRMATION_SCHEMA = "practitioner.create.confirmation.v1"
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


def _name(value, *, optional=False):
    if optional and value is None:
        return None
    if type(value) is not str:
        raise ValueError("text required")
    # Strict UTF-8 rejects isolated surrogates before retaining canonical data.
    value.encode("utf-8", errors="strict")
    value = value.strip(W1)
    if optional and not value:
        return None
    if not 1 <= len(value) <= 100 or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("bounded scalar text required")
    return value


class PractitionerCreateBody(ClosedModel):
    first_name: StrictStr
    last_name: StrictStr
    specialty: StrictStr | None = None
    distinct_resource: StrictBool = False

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def required_name(cls, value):
        return _name(value)

    @field_validator("specialty", mode="before")
    @classmethod
    def display_label(cls, value):
        return _name(value, optional=True)


def canonical_practitioner_body(body: PractitionerCreateBody):
    if type(body) is not PractitionerCreateBody:
        raise ValueError("typed practitioner body required")
    # Revalidate to protect callers using model_construct rather than validation.
    first, last = _name(body.first_name), _name(body.last_name)
    specialty = _name(body.specialty, optional=True)
    if type(body.distinct_resource) is not bool:
        raise ValueError("Boolean decision required")
    value = {"distinct_resource": body.distinct_resource, "first_name": first,
             "last_name": last, "specialty": specialty}
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False,
                           allow_nan=False, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8", errors="strict")).hexdigest()
    return value, canonical, digest


class PreparePractitionerCreate(ClosedModel):
    command_key: UUID
    body: PractitionerCreateBody
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


class ConfirmPractitionerCreate(ClosedModel):
    command_key: UUID
    command_id: UUID
    create_intent_id: UUID
    draft_revision: StrictInt = Field(ge=1, le=9223372036854775807)
    body_digest: StrictStr
    matching_context_digest: StrictStr
    signed_confirmation_evidence: dict[str, Any]
    confirmed: StrictBool

    @field_validator("command_key", "command_id", "create_intent_id", mode="before")
    @classmethod
    def identifiers(cls, value):
        return _uuid(value)

    @field_validator("body_digest", "matching_context_digest")
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


class PractitionerMatch(ClosedModel):
    id: UUID
    first_name: StrictStr
    last_name: StrictStr
    specialty: StrictStr | None
    is_active: StrictBool | None
    aggregate_version: StrictInt


class PractitionerCreateDraft(ClosedModel):
    command_id: UUID
    command_key: UUID
    create_intent_id: UUID
    draft_revision: StrictInt
    canonicalization_version: Literal["practitioner.create.body.v1"]
    matching_context_version: Literal["practitioner.create.matches.v1"]
    body: PractitionerCreateBody
    body_digest: StrictStr
    matching_context_digest: StrictStr
    role: Literal["PracticeOwner"]
    authority_generation: StrictInt
    expires_at: StrictStr
    match_total: StrictInt = Field(ge=0)
    sample_count: StrictInt = Field(ge=0, le=10)
    sample_label: StrictStr
    advisory_matches: list[PractitionerMatch]
    requires_distinct_resource_decision: StrictBool


class PractitionerCreateReceipt(ClosedModel):
    schema_version: Literal["practitioner.create.receipt.v1"]
    command_id: UUID
    command_key: UUID
    create_intent_id: UUID
    draft_revision: StrictInt
    practice_id: UUID
    practitioner_id: UUID
    actor_account_id: UUID
    actor_membership_id: UUID
    actor_user_id: UUID
    role: Literal["PracticeOwner"]
    authority_generation: StrictInt
    body_digest: StrictStr
    matching_context_digest: StrictStr
    initial_aggregate_version: Literal[0]
    audit_event_id: UUID
    outbox_event_id: UUID
    committed_at: StrictStr


class PreparePractitionerCreateResult(ClosedModel):
    state: Literal["prepared", "committed"]
    draft: PractitionerCreateDraft | None = None
    receipt: PractitionerCreateReceipt | None = None
    confirmation_evidence: dict[str, Any] | None = None

    @model_validator(mode="after")
    def terminal_shape(self):
        if self.state == "committed":
            if self.receipt is None or self.draft is not None or self.confirmation_evidence is not None:
                raise ValueError("committed receipt shape required")
        elif self.draft is None or self.receipt is not None:
            raise ValueError("prepared draft shape required")
        return self


class PractitionerCreatedFacts(ClosedModel):
    first_name: StrictStr
    last_name: StrictStr
    specialty: StrictStr | None
    is_active: StrictBool | None
    default_location_id: UUID | None
    aggregate_version: StrictInt


class PractitionerCurrentFacts(PractitionerCreatedFacts):
    id: UUID
    practice_id: UUID


class PractitionerCreateReadback(ClosedModel):
    status: Literal["matches_created", "diverged", "missing"]
    expected: PractitionerCreatedFacts
    current: PractitionerCurrentFacts | None


class PractitionerCreateRecovery(ClosedModel):
    receipt: PractitionerCreateReceipt
    readback: PractitionerCreateReadback
