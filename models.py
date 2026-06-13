import uuid
from sqlalchemy import Column, String, Date, Boolean, Integer, ForeignKey, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    medicare_number = Column(String(20))
    ihi_number = Column(String(20))

class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    google_doc_id = Column(String(255), nullable=False)
    consultation_date = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    is_finalized = Column(Boolean, default=False)
    consultation_type = Column(String(255))
    raw_document_text = Column(Text)
    document_embedding = Column(Vector(768)) # For Gemini text embeddings later

class MbsClaim(Base):
    __tablename__ = "mbs_claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"))
    item_number = Column(String(10), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="Draft")

class ClinicalDiagnosis(Base):
    __tablename__ = "clinical_diagnoses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"))
    term = Column(String(255), nullable=False)
    snomed_ct_au_code = Column(String(50))

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"))
    drug_name = Column(String(255), nullable=False)
    dosage_text = Column(Text)
    is_active = Column(Boolean, default=True)

# --- DIRECTORY TABLES FOR TYPEAHEAD SEARCH ---

class MbsDirectory(Base):
    __tablename__ = "mbs_directory"

    item_number = Column(String(10), primary_key=True)
    description = Column(Text, nullable=False)
    fee = Column(String(20))

class SnomedDirectory(Base):
    __tablename__ = "snomed_directory"

    concept_id = Column(String(50), primary_key=True)
    term = Column(String(255), nullable=False)