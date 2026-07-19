import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    ForeignKeyConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.models.base import Base


class BernieBookingSession(Base):
    __tablename__ = "bernie_booking_sessions"

    session_id = Column(String(64), primary_key=True)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    staff_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    surface_id = Column(String(100), nullable=False)
    state = Column(String(64), nullable=False)
    revision = Column(Integer, nullable=False, default=0)
    request_reference_date = Column(Date, nullable=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    patient_band = Column(String(64), nullable=True)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    practitioner_band = Column(String(64), nullable=True)
    candidate_freshness_ids = Column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    staged_proposal_freshness_id = Column(String(128), nullable=True)
    turn_count = Column(Integer, nullable=False, default=0)
    last_event_id = Column(String(100), nullable=True)
    stale_reason_code = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("revision >= 0", name="ck_bernie_booking_sessions_revision"),
        CheckConstraint("turn_count >= 0", name="ck_bernie_booking_sessions_turn_count"),
        CheckConstraint(
            "state in ("
            "'instruction_entry', 'recognition', 'clarification', "
            "'context_enrichment', 'slot_search', 'candidate_selection', "
            "'proposal_preview', 'confirmation', 'confirmed', 'no_slot', "
            "'clinic_day_exhausted', 'handed_off'"
            ")",
            name="ck_bernie_booking_sessions_state",
        ),
        UniqueConstraint(
            "practice_id",
            "session_id",
            name="uq_bernie_booking_sessions_practice_session",
        ),
        Index(
            "uq_bernie_booking_sessions_active_surface",
            "practice_id",
            "staff_user_id",
            "surface_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
        Index(
            "ix_bernie_booking_sessions_owner_surface",
            "practice_id",
            "staff_user_id",
            "surface_id",
        ),
        Index("ix_bernie_booking_sessions_practice_expiry", "practice_id", "expires_at"),
        Index("ix_bernie_booking_sessions_patient_id", "patient_id"),
        Index("ix_bernie_booking_sessions_practitioner_id", "practitioner_id"),
    )


class BernieSessionEventRow(Base):
    __tablename__ = "bernie_session_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    session_id = Column(
        String(64),
        nullable=False,
    )
    event_id = Column(String(100), nullable=False)
    event_type = Column(String(64), nullable=False)
    session_revision = Column(Integer, nullable=False)
    turn_index = Column(Integer, nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    expected_revision = Column(Integer, nullable=True)
    idempotency_key_hash = Column(String(64), nullable=True)
    payload_hash = Column(String(64), nullable=False)
    payload = Column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("session_revision > 0", name="ck_bernie_session_events_revision"),
        CheckConstraint("turn_index >= 0", name="ck_bernie_session_events_turn_index"),
        UniqueConstraint("session_id", "event_id", name="uq_bernie_session_events_event_id"),
        UniqueConstraint(
            "session_id",
            "session_revision",
            name="uq_bernie_session_events_revision",
        ),
        UniqueConstraint(
            "session_id",
            "idempotency_key_hash",
            name="uq_bernie_session_events_idempotency_hash",
        ),
        ForeignKeyConstraint(
            ["practice_id", "session_id"],
            [
                "bernie_booking_sessions.practice_id",
                "bernie_booking_sessions.session_id",
            ],
            name="fk_bernie_session_events_practice_session",
            ondelete="CASCADE",
        ),
        Index("ix_bernie_session_events_practice_session", "practice_id", "session_id"),
        Index("ix_bernie_session_events_session_created", "session_id", "created_at"),
    )


__all__ = ["BernieBookingSession", "BernieSessionEventRow"]
