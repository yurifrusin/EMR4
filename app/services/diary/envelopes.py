"""Internal diary action envelope contracts.

These models describe intent/proposal/confirmation/suggestion messages inside
the diary domain. They are deliberately pure contracts: no DB, no network, no
wall-clock reads, and no route or UI behaviour.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DiaryActionAuthor(str, Enum):
    """Actor family that authored an internal diary action envelope."""

    staff_ui = "staff_ui"
    bernie = "bernie"
    rayleen = "rayleen"
    davida = "davida"
    system = "system"


class DiaryActionChannel(str, Enum):
    """Surface or internal lane that produced an action envelope."""

    nl_text = "nl_text"
    ui_gesture = "ui_gesture"
    agent_policy = "agent_policy"
    system_rule = "system_rule"
    taskpane = "taskpane"
    command_centre = "command_centre"
    diary_panel = "diary_panel"
    api = "api"
    internal = "internal"


class DiaryActionEnvelopeBase(BaseModel):
    """Shared validation posture for diary action envelopes."""

    model_config = ConfigDict(extra="forbid")

    author: DiaryActionAuthor
    channel: DiaryActionChannel
    action_name: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    turn_ref: str | None = None


class DiaryActionIntent(DiaryActionEnvelopeBase):
    """A parsed desire to do diary work; it does not propose or write."""

    schema_version: Literal["diary.action.intent.v1"] = "diary.action.intent.v1"
    envelope_type: Literal["intent"] = "intent"
    intent_id: str = Field(min_length=1)
    summary: str | None = None
    writes_authorized: Literal[False] = False


class DiaryActionProposal(DiaryActionEnvelopeBase):
    """A staff-reviewable, non-mutating proposal for diary work."""

    schema_version: Literal["diary.action.proposal.v1"] = "diary.action.proposal.v1"
    envelope_type: Literal["proposal"] = "proposal"
    proposal_id: str = Field(min_length=1)
    intent_id: str | None = None
    requires_staff_confirmation: Literal[True] = True
    writes_authorized: Literal[False] = False
    evidence_refs: list[str] = Field(default_factory=list)
    review_reasons: list[str] = Field(default_factory=list)


class DiaryActionConfirmation(DiaryActionEnvelopeBase):
    """A staff-confirmed envelope that can be consumed by a write path later."""

    schema_version: Literal["diary.action.confirmation.v1"] = "diary.action.confirmation.v1"
    envelope_type: Literal["confirmation"] = "confirmation"
    confirmation_id: str = Field(min_length=1)
    proposal_id: str = Field(min_length=1)
    confirmed_by_user_id: str = Field(min_length=1)
    confirmed_at: datetime
    staff_confirmed: Literal[True] = True
    writes_authorized: Literal[True] = True
    confirmation_evidence: dict[str, Any] = Field(default_factory=dict)
    audit_evidence: list[str] = Field(default_factory=list)


_SUGGESTION_CONFIRM_GRADE_KEYS = frozenset(
    {
        "audit_evidence",
        "candidate_freshness_ids",
        "confirmation_evidence",
        "confirmed_at",
        "confirmed_by_user_id",
        "fresh_for_turn_ref",
        "proposal_freshness_id",
        "staff_confirmed",
    }
)


def _payload_contains_forbidden_key(value: Any) -> str | None:
    """Return the first forbidden evidence key found in a nested payload."""
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in _SUGGESTION_CONFIRM_GRADE_KEYS:
                return key
            found = _payload_contains_forbidden_key(nested)
            if found is not None:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _payload_contains_forbidden_key(nested)
            if found is not None:
                return found
    return None


class DiaryActionSuggestion(DiaryActionEnvelopeBase):
    """A read-only next-step suggestion; it must never authorize a write."""

    schema_version: Literal["diary.action.suggestion.v1"] = "diary.action.suggestion.v1"
    envelope_type: Literal["suggestion"] = "suggestion"
    suggestion_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    reason_code: str = Field(min_length=1)
    writes_authorized: Literal[False] = False
    requires_staff_confirmation: Literal[False] = False

    @model_validator(mode="after")
    def reject_confirm_grade_evidence(self) -> "DiaryActionSuggestion":
        forbidden_key = _payload_contains_forbidden_key(self.payload)
        if forbidden_key is not None:
            raise ValueError(
                f"DiaryActionSuggestion payload cannot carry confirm-grade evidence key: {forbidden_key}"
            )
        return self


__all__ = [
    "DiaryActionAuthor",
    "DiaryActionChannel",
    "DiaryActionConfirmation",
    "DiaryActionIntent",
    "DiaryActionProposal",
    "DiaryActionSuggestion",
]
