"""One synthetic patient's durable request, separate from an appointment."""

import uuid

from sqlalchemy import (
    BigInteger, CheckConstraint, Column, Date, DateTime, ForeignKey,
    ForeignKeyConstraint, Index, Integer, String, Time, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.models.base import Base


class PatientBookingRequest(Base):
    __tablename__ = "patient_booking_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    practitioner_id = Column(UUID(as_uuid=True), nullable=False)
    appointment_type_id = Column(UUID(as_uuid=True), nullable=False)
    location_id = Column(UUID(as_uuid=True), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    practice_timezone = Column(String(64), nullable=False)
    capability_digest = Column(String(64), nullable=False)
    capability_expires_at = Column(DateTime(timezone=True), nullable=False)
    state = Column(String(16), nullable=False, server_default="draft")
    request_version = Column(BigInteger, nullable=False, server_default="1")
    preference_date = Column(Date, nullable=True)
    earliest_local = Column(Time, nullable=True)
    latest_local = Column(Time, nullable=True)
    reason_code = Column(String(32), nullable=True)
    submission_key_digest = Column(String(64), nullable=True)
    submission_body_digest = Column(String(64), nullable=True)
    submission_receipt = Column(JSONB, nullable=True)
    booked_appointment_id = Column(UUID(as_uuid=True), nullable=True)
    booked_command_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    booked_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("practice_id", "id", name="uq_patient_request_practice_id_id"),
        UniqueConstraint("practice_id", "booked_appointment_id", name="uq_patient_request_booked_appointment"),
        UniqueConstraint("practice_id", "booked_command_id", name="uq_patient_request_booked_command"),
        ForeignKeyConstraint(["practice_id", "patient_id"], ["patients.practice_id", "patients.id"], name="fk_patient_request_patient"),
        ForeignKeyConstraint(["practice_id", "practitioner_id"], ["practitioners.practice_id", "practitioners.id"], name="fk_patient_request_practitioner"),
        ForeignKeyConstraint(["practice_id", "appointment_type_id"], ["appointment_types.practice_id", "appointment_types.id"], name="fk_patient_request_type"),
        ForeignKeyConstraint(["practice_id", "location_id"], ["practice_locations.practice_id", "practice_locations.id"], name="fk_patient_request_location"),
        ForeignKeyConstraint(["practice_id", "booked_appointment_id"], ["appointments.practice_id", "appointments.id"], name="fk_patient_request_appointment"),
        ForeignKeyConstraint(["practice_id", "booked_command_id", "booked_appointment_id"], ["appointment_command_idempotency.practice_id", "appointment_command_idempotency.id", "appointment_command_idempotency.target_appointment_id"], name="fk_patient_request_command_target", use_alter=True),
        CheckConstraint("state IN ('draft', 'submitted', 'booked', 'cancelled', 'expired')", name="ck_patient_request_state"),
        CheckConstraint("request_version >= 1 AND duration_minutes BETWEEN 1 AND 480", name="ck_patient_request_version_duration"),
        CheckConstraint("(state = 'booked' AND booked_appointment_id IS NOT NULL AND booked_command_id IS NOT NULL AND booked_at IS NOT NULL) OR (state != 'booked' AND booked_appointment_id IS NULL AND booked_command_id IS NULL AND booked_at IS NULL)", name="ck_patient_request_booked_links"),
        CheckConstraint("state NOT IN ('submitted', 'booked') OR (preference_date IS NOT NULL AND earliest_local IS NOT NULL AND latest_local IS NOT NULL AND earliest_local < latest_local AND reason_code = 'follow_up' AND submitted_at IS NOT NULL)", name="ck_patient_request_submitted_preference"),
        Index("ix_patient_request_practice_state", "practice_id", "state"),
    )
