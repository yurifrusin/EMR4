import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.models.base import Base


class UserRole(str, enum.Enum):
    GP = "GP"
    Receptionist = "Receptionist"
    Nurse = "Nurse"
    Admin = "Admin"
    PracticeOwner = "PracticeOwner"


class Practice(Base):
    __tablename__ = "practices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    abn = Column(String(20))
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    address_suburb = Column(String(100))
    address_state = Column(String(10))
    address_postcode = Column(String(10))
    phone = Column(String(20))
    email = Column(String(255))
    logo_url = Column(String(500))
    timezone = Column(String(50), default="Australia/Sydney")
    hive_mind_opt_in = Column(Boolean, default=False)
    practice_embedding = Column(Vector(768))
    specialty_tags = Column(JSONB)
    asgc_ra_code = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    proda_device_cert_path = Column(String(500))
    proda_cert_expiry = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    locations = relationship("PracticeLocation", back_populates="practice")
    users = relationship("User", back_populates="practice")
    practitioners = relationship("Practitioner", back_populates="practice")


class PracticeLocation(Base):
    __tablename__ = "practice_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address_line1 = Column(String(255))
    address_suburb = Column(String(100))
    address_state = Column(String(10))
    address_postcode = Column(String(10))
    phone = Column(String(20))
    waiting_rooms = Column(JSONB)
    is_active = Column(Boolean, default=True)

    practice = relationship("Practice", back_populates="locations")

    __table_args__ = (Index("ix_practice_locations_practice_id", "practice_id"),)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    practice = relationship("Practice", back_populates="users")
    practitioner = relationship("Practitioner", foreign_keys=[practitioner_id])

    __table_args__ = (
        Index("ix_users_practice_id", "practice_id"),
        Index("ix_users_email", "email"),
    )


class Practitioner(Base):
    __tablename__ = "practitioners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    provider_number = Column(String(20))
    prescriber_number = Column(String(20))
    ahpra_number = Column(String(20))
    hpi_i = Column(String(20))
    specialty = Column(String(100))
    default_location_id = Column(UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    practice = relationship("Practice", back_populates="practitioners")
    default_location = relationship("PracticeLocation", foreign_keys=[default_location_id])

    __table_args__ = (Index("ix_practitioners_practice_id", "practice_id"),)
