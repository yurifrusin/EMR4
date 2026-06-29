"""
Typed Access AI audit events.

These contracts are storage-agnostic for now. The invocation service can emit
them to a database table, structured logs, or a compliance export later without
changing event shape.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.ai.contracts import AiCapability, AiMethod


class AiAuditEventType(str, Enum):
    INVOCATION_ALLOWED = "ai.invocation.allowed"
    INVOCATION_BLOCKED = "ai.invocation.blocked"
    INVOCATION_FAILED = "ai.invocation.failed"
    CAPABILITY_ENABLED = "ai.capability.enabled"
    CAPABILITY_DISABLED = "ai.capability.disabled"
    ENTITLEMENT_GRANTED = "ai.entitlement.granted"
    ENTITLEMENT_REVOKED = "ai.entitlement.revoked"
    BERNIE_PROPOSAL_CREATED = "bernie.proposal.created"
    BERNIE_PROPOSAL_CONFIRMED = "bernie.proposal.confirmed"
    BERNIE_PROPOSAL_CANCELLED = "bernie.proposal.cancelled"
    IDENTITY_CALLER_CANDIDATE_MATCHED = "identity.caller_candidate_matched"
    IDENTITY_PATIENT_VERIFIED_BY_STAFF = "identity.patient_verified_by_staff"
    KNOWLEDGE_QUERY_ALLOWED = "knowledge.query.allowed"
    KNOWLEDGE_QUERY_BLOCKED = "knowledge.query.blocked"


class AiAuditDecision(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    FAILED = "failed"
    RECORDED = "recorded"


class AiAuditSourceSurface(str, Enum):
    TASKPANE = "taskpane"
    COMMAND_CENTRE = "command_centre"
    DIARY = "diary"
    API = "api"
    DEV_TOOL = "dev_tool"
    SYSTEM = "system"


_FORBIDDEN_METADATA_KEY_FRAGMENTS = (
    "raw",
    "prompt",
    "transcript",
    "note_text",
    "letter_text",
    "patient_name",
    "medicare",
    "ihi",
    "dob",
    "date_of_birth",
    "phone",
    "address",
)


class AccessAiAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    event_type: AiAuditEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_user_id: UUID | None = None
    actor_roles: tuple[str, ...] = ()
    practice_id: UUID | None = None
    target_resource_type: str | None = None
    target_resource_id: UUID | str | None = None
    capability: AiCapability | None = None
    method: AiMethod | None = None
    decision: AiAuditDecision
    reason_code: str | None = None
    correlation_id: UUID = Field(default_factory=uuid4)
    source_surface: AiAuditSourceSurface
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value

    @field_validator("reason_code")
    @classmethod
    def require_reason_code_slug(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value or any(char.isspace() for char in value):
            raise ValueError("reason_code must be a compact slug")
        return value

    @field_validator("metadata")
    @classmethod
    def reject_raw_or_phi_metadata_keys(
        cls,
        value: dict[str, str | int | float | bool | None],
    ) -> dict[str, str | int | float | bool | None]:
        for key in value:
            normalized = key.lower()
            if any(fragment in normalized for fragment in _FORBIDDEN_METADATA_KEY_FRAGMENTS):
                raise ValueError(f"metadata key is not audit-safe: {key}")
        return value

    @model_validator(mode="after")
    def require_ai_fields_for_ai_events(self) -> "AccessAiAuditEvent":
        if self.event_type.value.startswith("ai.") and (
            self.capability is None or self.method is None
        ):
            raise ValueError("ai audit events require capability and method")
        if self.decision in {AiAuditDecision.BLOCKED, AiAuditDecision.FAILED} and not self.reason_code:
            raise ValueError("blocked and failed audit events require reason_code")
        return self


def build_access_ai_audit_event(
    *,
    event_type: AiAuditEventType,
    source_surface: AiAuditSourceSurface,
    decision: AiAuditDecision,
    actor_user_id: UUID | None = None,
    actor_roles: tuple[str, ...] = (),
    practice_id: UUID | None = None,
    capability: AiCapability | None = None,
    method: AiMethod | None = None,
    reason_code: str | None = None,
    target_resource_type: str | None = None,
    target_resource_id: UUID | str | None = None,
    correlation_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> AccessAiAuditEvent:
    bounded_metadata: dict[str, str | int | float | bool | None] = {}
    for key, value in (metadata or {}).items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            bounded_metadata[key] = value
        else:
            bounded_metadata[key] = str(value)

    return AccessAiAuditEvent(
        event_type=event_type,
        actor_user_id=actor_user_id,
        actor_roles=actor_roles,
        practice_id=practice_id,
        target_resource_type=target_resource_type,
        target_resource_id=target_resource_id,
        capability=capability,
        method=method,
        decision=decision,
        reason_code=reason_code,
        correlation_id=correlation_id or uuid4(),
        source_surface=source_surface,
        metadata=bounded_metadata,
    )
