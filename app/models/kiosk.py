import uuid
import enum
from sqlalchemy import (
    Column, String, DateTime, Integer, Enum, ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.models.base import Base


class CheckinMethod(str, enum.Enum):
    Details = "Details"
    QR = "QR"
    NFC = "NFC"
    FacialRecognition = "FacialRecognition"


class CallType(str, enum.Enum):
    Inbound = "Inbound"
    Outbound = "Outbound"
    Telehealth = "Telehealth"
    Missed = "Missed"


class CheckinEvent(Base):
    __tablename__ = "checkin_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    checkin_method = Column(Enum(CheckinMethod), nullable=False)
    checkin_time = Column(DateTime(timezone=True), server_default=func.now())
    waiting_room_assigned = Column(String(50))
    kiosk_id = Column(String(50))

    __table_args__ = (Index("ix_checkin_events_patient_id", "patient_id"),)


class PatientQrToken(Base):
    __tablename__ = "patient_qr_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("ix_patient_qr_tokens_patient_id", "patient_id"),)


class CallLog(Base):
    __tablename__ = "call_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    caller_number = Column(String(20))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    answered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    call_time = Column(DateTime(timezone=True), server_default=func.now())
    duration_seconds = Column(Integer, default=0)
    call_type = Column(Enum(CallType), nullable=False)
    notes = Column(String(1000))

    __table_args__ = (Index("ix_call_log_practice_id", "practice_id"),)
