import uuid
import enum
from datetime import timedelta
from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Enum, ForeignKey, Date,
    Time, Index, CheckConstraint, UniqueConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class AppointmentStatus(str, enum.Enum):
    Booked = "Booked"
    Confirmed = "Confirmed"
    Arrived = "Arrived"
    InConsult = "InConsult"
    Completed = "Completed"
    Cancelled = "Cancelled"
    NoShow = "NoShow"
    DNA = "DNA"


class BookingChannel(str, enum.Enum):
    Receptionist = "Receptionist"
    Online = "Online"
    Phone = "Phone"
    Kiosk = "Kiosk"
    App = "App"


class AppointmentType(Base):
    __tablename__ = "appointment_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    name = Column(String(100), nullable=False)
    default_duration = Column(Integer, default=15)
    color_hex = Column(String(7))
    is_bookable_online = Column(Boolean, default=False)

    __table_args__ = (Index("ix_appointment_types_practice_id", "practice_id"),)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    patient_name_provisional = Column(String(200), nullable=True)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=False)
    appointment_type_id = Column(UUID(as_uuid=True), ForeignKey("appointment_types.id"), nullable=True)
    booked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    appointment_date = Column(Date, nullable=False)
    start_time_local = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=15)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.Booked)
    reason = Column(String(500))
    notes = Column(String(1000))
    cancellation_reason = Column(String(500), nullable=True)
    status_reason_code = Column(String(50), nullable=True)
    booked_via = Column(Enum(BookingChannel), default=BookingChannel.Receptionist)
    waiting_room = Column(String(50))
    waiting_area_id = Column(UUID(as_uuid=True), ForeignKey("waiting_areas.id"), nullable=True)
    queue_position = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient")
    practitioner = relationship("Practitioner")
    appointment_type = relationship("AppointmentType")

    @property
    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration_minutes or 0)

    __table_args__ = (
        UniqueConstraint(
            "practice_id",
            "id",
            name="uq_appointments_practice_id_id",
        ),
        Index("ix_appointments_practice_id", "practice_id"),
        Index("ix_appointments_patient_id", "patient_id"),
        Index("ix_appointments_practitioner_id", "practitioner_id"),
        Index("ix_appointments_start_time", "start_time"),
        Index("ix_appointments_practice_date", "practice_id", "appointment_date"),
        Index(
            "ix_appointments_practitioner_date_time",
            "practitioner_id",
            "appointment_date",
            "start_time_local",
        ),
    )


class PractitionerSchedule(Base):
    __tablename__ = "practitioner_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Mon, 6=Sun
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration_minutes = Column(Integer, default=15)

    __table_args__ = (Index("ix_practitioner_schedules_practitioner_id", "practitioner_id"),)


class AppointmentAuditAction(str, enum.Enum):
    create = "create"
    update = "update"
    status_change = "status_change"
    delete = "delete"


class AppointmentAuditLog(Base):
    __tablename__ = "appointment_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)
    confirmed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(Enum(AppointmentAuditAction), nullable=False)
    status_before = Column(Enum(AppointmentStatus), nullable=True)
    status_after = Column(Enum(AppointmentStatus), nullable=True)
    cancellation_reason = Column(String(500), nullable=True)
    status_reason_code = Column(String(50), nullable=True)
    confirmed_warnings = Column(JSONB, nullable=True)
    command_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "appointment_command_idempotency.id",
            name="fk_appt_audit_log_command_id",
            use_alter=True,
        ),
        nullable=True,
    )
    bernie_session_id = Column(
        String(64),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "practice_id",
            "id",
            name="uq_appt_audit_log_practice_id_id",
        ),
        ForeignKeyConstraint(
            ["practice_id", "appointment_id"],
            ["appointments.practice_id", "appointments.id"],
            name="fk_appt_audit_log_practice_appointment",
            use_alter=True,
        ),
        ForeignKeyConstraint(
            ["practice_id", "command_id"],
            [
                "appointment_command_idempotency.practice_id",
                "appointment_command_idempotency.id",
            ],
            name="fk_appt_audit_log_practice_command",
            use_alter=True,
        ),
        Index("ix_appt_audit_log_practice_appt", "practice_id", "appointment_id"),
        Index("ix_appt_audit_log_appointment_id", "appointment_id"),
        Index(
            "uq_appt_audit_log_command_id",
            "command_id",
            unique=True,
            postgresql_where=command_id.isnot(None),
        ),
        Index("ix_appt_audit_log_practice_session", "practice_id", "bernie_session_id"),
    )


class AppointmentCommandIdempotency(Base):
    __tablename__ = "appointment_command_idempotency"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    actor_user_id = Column(String(64), nullable=False)
    actor_role = Column(String(64), nullable=False)
    operation_id = Column(String(100), nullable=False)
    route_family = Column(String(100), nullable=False)
    idempotency_key_hash = Column(String(128), nullable=False)
    request_body_hash = Column(String(128), nullable=False)
    request_body_canonicalization_version = Column(Integer, nullable=False, default=1)
    state = Column(String(32), nullable=False)
    response_status_code = Column(Integer, nullable=True)
    response_body_hash = Column(String(128), nullable=True)
    response_body_json = Column(JSONB, nullable=True)
    result_kind = Column(String(50), nullable=True)
    target_appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    audit_log_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "appointment_audit_log.id",
            name="fk_appt_cmd_idem_audit_log_id",
            use_alter=True,
        ),
        nullable=True,
    )
    bernie_session_id = Column(
        String(64),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "practice_id",
            "id",
            name="uq_appt_cmd_idem_practice_id_id",
        ),
        UniqueConstraint(
            "practice_id",
            "actor_user_id",
            "operation_id",
            "idempotency_key_hash",
            name="uq_appt_cmd_idem_practice_actor_operation_key",
        ),
        CheckConstraint(
            "state in ('in_progress', 'completed', 'failed_transient')",
            name="ck_appt_cmd_idem_state",
        ),
        CheckConstraint(
            "state != 'completed' OR "
            "(response_status_code IS NOT NULL AND "
            "response_body_hash IS NOT NULL AND response_body_json IS NOT NULL)",
            name="ck_appt_cmd_idem_completed_response",
        ),
        CheckConstraint(
            "NOT (state = 'completed' AND "
            "operation_id = 'confirmAppointmentCreateProposal' AND "
            "result_kind = 'confirmed_write') OR "
            "(target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL)",
            name="ck_appt_cmd_idem_completed_create_correlation",
        ),
        ForeignKeyConstraint(
            ["practice_id", "target_appointment_id"],
            ["appointments.practice_id", "appointments.id"],
            name="fk_appt_cmd_idem_practice_target",
            use_alter=True,
        ),
        ForeignKeyConstraint(
            ["practice_id", "audit_log_id"],
            ["appointment_audit_log.practice_id", "appointment_audit_log.id"],
            name="fk_appt_cmd_idem_practice_audit",
            use_alter=True,
        ),
        Index("ix_appt_cmd_idem_practice_target", "practice_id", "target_appointment_id"),
        Index("ix_appt_cmd_idem_practice_created", "practice_id", "created_at"),
        Index(
            "uq_appt_cmd_idem_audit_log_id",
            "audit_log_id",
            unique=True,
            postgresql_where=audit_log_id.isnot(None),
        ),
        Index("ix_appt_cmd_idem_practice_session", "practice_id", "bernie_session_id"),
    )


class ScheduleOverride(Base):
    __tablename__ = "schedule_overrides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=False)
    date = Column(Date, nullable=False)
    is_unavailable = Column(Boolean, default=False)
    override_start = Column(Time)
    override_end = Column(Time)
    reason = Column(String(255))

    __table_args__ = (Index("ix_schedule_overrides_practitioner_id_date", "practitioner_id", "date"),)
