import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.models.base import Base


class MessagePriority(str, enum.Enum):
    Normal = "Normal"
    Urgent = "Urgent"
    Critical = "Critical"


class SmsDirection(str, enum.Enum):
    Outbound = "Outbound"
    Inbound = "Inbound"


class SmsType(str, enum.Enum):
    AppointmentReminder = "AppointmentReminder"
    Confirmation = "Confirmation"
    ResultNotification = "ResultNotification"
    Recall = "Recall"
    Bulk = "Bulk"
    Custom = "Custom"


class SmsStatus(str, enum.Enum):
    Queued = "Queued"
    Sent = "Sent"
    Delivered = "Delivered"
    Failed = "Failed"
    Replied = "Replied"


class InternalMessage(Base):
    __tablename__ = "internal_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    recipient_role = Column(String(50))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    subject = Column(String(255))
    body = Column(Text, nullable=False)
    priority = Column(Enum(MessagePriority), default=MessagePriority.Normal)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_internal_messages_practice_id", "practice_id"),
        Index("ix_internal_messages_recipient_id", "recipient_id"),
    )


class SmsLog(Base):
    __tablename__ = "sms_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    direction = Column(Enum(SmsDirection), nullable=False)
    phone_number = Column(String(20), nullable=False)
    message_body = Column(Text, nullable=False)
    sms_type = Column(Enum(SmsType), default=SmsType.Custom)
    status = Column(Enum(SmsStatus), default=SmsStatus.Queued)
    clicksend_message_id = Column(String(100))
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_sms_log_practice_id", "practice_id"),
        Index("ix_sms_log_patient_id", "patient_id"),
    )
