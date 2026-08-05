"""Durable practice-administration command storage for the B4.1 runtime.

The four tables are practice-scoped, default-off, provider-free and storage-only.
Durable rows store hashes and bounded enum/code values only: no raw idempotency
keys, session credentials, provider output, patient data or free text. Audit and
outbox rows are append-only; the outbox is unpublished storage until a separate
descendant opens publication.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func, text

from app.models.base import Base


class PracticeAdministrationConfirmationEvidence(Base):
    __tablename__ = "practice_administration_confirmation_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    actor_role = Column(String(64), nullable=False)
    proposal_id = Column(String(4096), nullable=False)
    proposal_hash = Column(String(64), nullable=False)
    canonical_request_hash = Column(String(64), nullable=False)
    before_state_hash = Column(String(64), nullable=False)
    practitioner_id = Column(
        UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=False
    )
    requested_location_id = Column(
        UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=False
    )
    expected_aggregate_version = Column(Integer, nullable=False)
    correlation_id = Column(String(128), nullable=False)
    idempotency_key_hash = Column(String(64), nullable=False)
    nonce = Column(String(128), nullable=False)
    state = Column(String(32), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    consumed_by_command_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("state in ('live', 'consumed')", name="ck_b4_evidence_state"),
        CheckConstraint("expires_at > issued_at", name="ck_b4_evidence_expiry"),
        CheckConstraint(
            "expected_aggregate_version >= 0",
            name="ck_b4_evidence_expected_version",
        ),
        UniqueConstraint(
            "practice_id", "id", name="uq_b4_evidence_practice_id_id"
        ),
        UniqueConstraint(
            "practice_id",
            "actor_user_id",
            "proposal_hash",
            name="uq_b4_evidence_practice_actor_proposal",
        ),
        UniqueConstraint("nonce", name="uq_b4_evidence_nonce"),
        Index("ix_b4_evidence_practice_actor", "practice_id", "actor_user_id"),
        Index("ix_b4_evidence_practice_expiry", "practice_id", "expires_at"),
    )


class PracticeAdministrationCommandIdempotency(Base):
    __tablename__ = "practice_administration_command_idempotency"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    actor_role = Column(String(64), nullable=False)
    operation_id = Column(String(100), nullable=False)
    route_family = Column(String(100), nullable=False)
    idempotency_key_hash = Column(String(64), nullable=False)
    request_body_hash = Column(String(64), nullable=False)
    canonical_request_hash = Column(String(64), nullable=False)
    proposal_hash = Column(String(64), nullable=False)
    state = Column(String(32), nullable=False)
    response_status_code = Column(Integer, nullable=True)
    response_body_hash = Column(String(64), nullable=True)
    response_body_json = Column(JSONB, nullable=True)
    result_kind = Column(String(50), nullable=True)
    receipt_id = Column(String(128), nullable=True)
    practitioner_id = Column(
        UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True
    )
    confirmation_evidence_id = Column(UUID(as_uuid=True), nullable=True)
    audit_event_id = Column(UUID(as_uuid=True), nullable=True)
    outbox_event_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "practice_id", "id", name="uq_b4_cmd_idem_practice_id_id"
        ),
        UniqueConstraint(
            "practice_id",
            "actor_user_id",
            "operation_id",
            "idempotency_key_hash",
            name="uq_b4_cmd_idem_practice_actor_operation_key",
        ),
        CheckConstraint(
            "state in ('in_progress', 'completed', 'failed_transient')",
            name="ck_b4_cmd_idem_state",
        ),
        CheckConstraint(
            "state != 'completed' OR "
            "(response_status_code IS NOT NULL AND "
            "response_body_hash IS NOT NULL AND response_body_json IS NOT NULL)",
            name="ck_b4_cmd_idem_completed_response",
        ),
        Index("ix_b4_cmd_idem_practice_created", "practice_id", "created_at"),
        Index(
            "ix_b4_cmd_idem_practice_evidence",
            "practice_id",
            "confirmation_evidence_id",
        ),
    )


class PracticeAdministrationAuditEvent(Base):
    __tablename__ = "practice_administration_audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    actor_role = Column(String(64), nullable=False)
    action = Column(String(100), nullable=False)
    command_id = Column(UUID(as_uuid=True), nullable=False)
    practitioner_id = Column(
        UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=False
    )
    before_location_id = Column(
        UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=True
    )
    after_location_id = Column(
        UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=False
    )
    expected_aggregate_version = Column(Integer, nullable=False)
    resulting_aggregate_version = Column(Integer, nullable=False)
    proposal_hash = Column(String(64), nullable=False)
    correlation_id = Column(String(128), nullable=False)
    committed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "action = 'practitioner_default_location_changed'",
            name="ck_b4_audit_action",
        ),
        CheckConstraint(
            "resulting_aggregate_version = expected_aggregate_version + 1",
            name="ck_b4_audit_version_step",
        ),
        UniqueConstraint("practice_id", "id", name="uq_b4_audit_practice_id_id"),
        UniqueConstraint("command_id", name="uq_b4_audit_command"),
        Index("ix_b4_audit_practice_practitioner", "practice_id", "practitioner_id"),
    )


class PracticeAdministrationOutboxEvent(Base):
    __tablename__ = "practice_administration_outbox_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    event_type = Column(String(64), nullable=False)
    schema_version = Column(String(64), nullable=False)
    source_system = Column(String(64), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    actor_role = Column(String(64), nullable=False)
    command_id = Column(UUID(as_uuid=True), nullable=False)
    audit_event_id = Column(UUID(as_uuid=True), nullable=False)
    correlation_id = Column(String(128), nullable=False)
    published = Column(Boolean, nullable=False, server_default=text("false"))
    payload = Column(JSONB, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "event_type = 'practice.practitioner_default_location_changed'",
            name="ck_b4_outbox_type",
        ),
        CheckConstraint(
            "schema_version = 'practice.practitioner_default_location_changed.v1'",
            name="ck_b4_outbox_schema",
        ),
        CheckConstraint(
            "source_system = 'emr4-practice-administration'",
            name="ck_b4_outbox_source",
        ),
        CheckConstraint("published = false", name="ck_b4_outbox_unpublished"),
        CheckConstraint(
            "jsonb_typeof(payload) = 'object' AND "
            "payload ?& ARRAY['practitioner_id', 'before_location_id', "
            "'after_location_id', 'aggregate_version', 'reason_codes'] AND "
            "payload - ARRAY['practitioner_id', 'before_location_id', "
            "'after_location_id', 'aggregate_version', 'reason_codes'] = '{}'::jsonb AND "
            "payload->'reason_codes' = '[\"practitioner_default_location_changed\"]'::jsonb",
            name="ck_b4_outbox_payload_allowlist",
        ),
        UniqueConstraint("practice_id", "id", name="uq_b4_outbox_practice_id_id"),
        UniqueConstraint("command_id", name="uq_b4_outbox_command"),
        UniqueConstraint("audit_event_id", name="uq_b4_outbox_audit"),
        Index("ix_b4_outbox_practice_order", "practice_id", "created_at", "id"),
    )


__all__ = [
    "PracticeAdministrationAuditEvent",
    "PracticeAdministrationCommandIdempotency",
    "PracticeAdministrationConfirmationEvidence",
    "PracticeAdministrationOutboxEvent",
]
