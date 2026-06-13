import uuid
from sqlalchemy import (
    Column, String, Date, Boolean, DateTime, ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    medicare_number = Column(String(20))
    ihi_number = Column(String(20))
    dva_number = Column(String(20))
    sex = Column(String(10))
    gender_identity = Column(String(50))
    indigenous_status = Column(String(50))
    preferred_language = Column(String(50))
    email = Column(String(255))
    phone_mobile = Column(String(20))
    phone_home = Column(String(20))
    address_line1 = Column(String(255))
    address_suburb = Column(String(100))
    address_state = Column(String(10))
    address_postcode = Column(String(10))
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(50))
    concession_type = Column(String(50))
    consent_facial_recognition = Column(Boolean, default=False)
    face_embedding_id = Column(String(255))
    sms_consent = Column(Boolean, default=False)
    sms_consent_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    practice = relationship("Practice")

    __table_args__ = (
        Index("ix_patients_practice_id", "practice_id"),
        Index("ix_patients_last_name", "last_name"),
        Index("ix_patients_medicare_number", "medicare_number"),
    )
