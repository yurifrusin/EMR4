import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Float, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.models.base import Base


class GpTier(str, enum.Enum):
    Tier1_Gold = "Tier1_Gold"
    Tier2 = "Tier2"
    Tier3 = "Tier3"


class IhiSource(str, enum.Enum):
    Manual = "Manual"
    HI_Service = "HI_Service"


class MhrDocumentType(str, enum.Enum):
    SharedHealthSummary = "SharedHealthSummary"
    EventSummary = "EventSummary"
    DischargeSummary = "DischargeSummary"
    Other = "Other"


class CommunityEncounter(Base):
    __tablename__ = "community_encounters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=True)
    deidentified_text = Column(Text, nullable=False)
    encounter_embedding = Column(Vector(768))
    mbs_item = Column(String(20))
    snomed_codes = Column(JSONB)
    gp_tier = Column(Enum(GpTier), default=GpTier.Tier3)
    practice_specialty_tags = Column(JSONB)
    practice_asgc_ra_code = Column(String(10))
    practice_latitude = Column(Float)
    practice_longitude = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RagFeedback(Base):
    __tablename__ = "rag_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    query_embedding = Column(Vector(768))
    retrieved_community_ids = Column(JSONB)
    was_accepted = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_rag_feedback_practice_id", "practice_id"),)


class IhiRecord(Base):
    __tablename__ = "ihi_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    ihi_number = Column(String(20), nullable=False)
    ihi_status = Column(String(50))
    verified_at = Column(DateTime(timezone=True))
    source = Column(Enum(IhiSource), default=IhiSource.Manual)

    __table_args__ = (Index("ix_ihi_records_patient_id", "patient_id"),)


class MhrUpload(Base):
    __tablename__ = "mhr_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    document_type = Column(Enum(MhrDocumentType), nullable=False)
    upload_status = Column(String(50))
    uploaded_at = Column(DateTime(timezone=True))
    mhr_document_id = Column(String(100))

    __table_args__ = (Index("ix_mhr_uploads_patient_id", "patient_id"),)
