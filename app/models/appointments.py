import uuid
import enum
from datetime import timedelta
from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Enum, ForeignKey, Date,
    Time, Index, Text,
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
    confirmed_warnings = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_appt_audit_log_practice_appt", "practice_id", "appointment_id"),
        Index("ix_appt_audit_log_appointment_id", "appointment_id"),
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
