import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.models.base import Base


class DiaryCommittedEvent(Base):
    __tablename__ = "diary_committed_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    event_type = Column(String(64), nullable=False)
    schema_version = Column(String(64), nullable=False)
    source_system = Column(String(64), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), nullable=False)
    aggregate_revision = Column(Integer, nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    actor_role = Column(String(64), nullable=False)
    command_id = Column(UUID(as_uuid=True), nullable=False)
    audit_log_id = Column(UUID(as_uuid=True), nullable=False)
    correlation_id = Column(UUID(as_uuid=True), nullable=False)
    evidence_mode = Column(String(64), nullable=False)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "event_type = 'diary.appointment_rescheduled'",
            name="ck_diary_committed_events_type",
        ),
        CheckConstraint(
            "schema_version = 'diary.appointment_rescheduled.v1'",
            name="ck_diary_committed_events_schema",
        ),
        CheckConstraint(
            "source_system = 'emr4-diary'",
            name="ck_diary_committed_events_source",
        ),
        CheckConstraint(
            "evidence_mode = 'authored_synthetic_local'",
            name="ck_diary_committed_events_evidence",
        ),
        CheckConstraint(
            "aggregate_revision > 0",
            name="ck_diary_committed_events_revision",
        ),
        CheckConstraint(
            "expires_at > occurred_at",
            name="ck_diary_committed_events_expiry",
        ),
        CheckConstraint(
            "correlation_id = command_id",
            name="ck_diary_committed_events_correlation",
        ),
        CheckConstraint(
            "jsonb_typeof(payload) = 'object' AND "
            "payload ?& ARRAY['appointment_id', 'practitioner_id', 'location_id', "
            "'start_time', 'end_time', 'reason_codes'] AND "
            "payload - ARRAY['appointment_id', 'practitioner_id', 'location_id', "
            "'start_time', 'end_time', 'reason_codes'] = '{}'::jsonb AND "
            "payload->'reason_codes' = '[\"appointment_time_changed\"]'::jsonb",
            name="ck_diary_committed_events_payload_allowlist",
        ),
        UniqueConstraint(
            "practice_id", "id", name="uq_diary_committed_events_practice_id_id"
        ),
        UniqueConstraint(
            "practice_id",
            "appointment_id",
            "aggregate_revision",
            name="uq_diary_committed_events_aggregate_revision",
        ),
        UniqueConstraint("command_id", name="uq_diary_committed_events_command"),
        UniqueConstraint("audit_log_id", name="uq_diary_committed_events_audit"),
        ForeignKeyConstraint(
            ["practice_id", "appointment_id"],
            ["appointments.practice_id", "appointments.id"],
            name="fk_diary_committed_events_practice_appointment",
        ),
        ForeignKeyConstraint(
            ["practice_id", "command_id"],
            [
                "appointment_command_idempotency.practice_id",
                "appointment_command_idempotency.id",
            ],
            name="fk_diary_committed_events_practice_command",
        ),
        ForeignKeyConstraint(
            ["practice_id", "audit_log_id"],
            ["appointment_audit_log.practice_id", "appointment_audit_log.id"],
            name="fk_diary_committed_events_practice_audit",
        ),
        Index(
            "ix_diary_committed_events_practice_order",
            "practice_id",
            "occurred_at",
            "id",
        ),
        Index(
            "ix_diary_committed_events_practice_expiry",
            "practice_id",
            "expires_at",
        ),
    )
