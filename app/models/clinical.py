import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Date, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.models.base import Base


class EncounterStatus(str, enum.Enum):
    Draft = "Draft"
    InProgress = "InProgress"
    Finalized = "Finalized"
    Amended = "Amended"


class TemplateType(str, enum.Enum):
    SOAP = "SOAP"
    Procedure = "Procedure"
    MentalHealth = "MentalHealth"
    CDM = "CDM"
    GPCCMP = "GPCCMP"
    HealthAssessment = "HealthAssessment"
    Antenatal = "Antenatal"
    WoundCare = "WoundCare"


class HistoryCategory(str, enum.Enum):
    Medical = "Medical"
    Surgical = "Surgical"
    Family = "Family"
    Social = "Social"


class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    status = Column(Enum(EncounterStatus), default=EncounterStatus.Draft)
    template_type = Column(Enum(TemplateType), default=TemplateType.SOAP)
    consultation_type = Column(String(255))
    consultation_date = Column(DateTime(timezone=True), server_default=func.now())
    raw_document_text = Column(Text)
    document_embedding = Column(Vector(768))
    is_shared_to_hive = Column(Boolean, default=False)
    google_doc_id = Column(String(255))
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    practice = relationship("Practice")
    patient = relationship("Patient")
    practitioner = relationship("Practitioner")

    __table_args__ = (
        Index("ix_encounters_practice_id", "practice_id"),
        Index("ix_encounters_patient_id", "patient_id"),
    )


class ClinicalDiagnosis(Base):
    __tablename__ = "clinical_diagnoses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    term = Column(String(255), nullable=False)
    snomed_ct_au_code = Column(String(50))
    is_active = Column(Boolean, default=True)
    onset_date = Column(Date)
    resolved_date = Column(Date)
    severity = Column(String(50))

    __table_args__ = (
        Index("ix_clinical_diagnoses_patient_id", "patient_id"),
        Index("ix_clinical_diagnoses_practice_id", "practice_id"),
    )


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    prescribed_by = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    drug_name = Column(String(255), nullable=False)
    dosage_text = Column(Text)
    pbs_code = Column(String(20))
    repeats = Column(String(10))
    quantity = Column(String(20))
    route = Column(String(50))
    frequency = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)
    erx_token = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_prescriptions_patient_id", "patient_id"),)


class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    substance = Column(String(255), nullable=False)
    reaction = Column(Text)
    severity = Column(String(50))
    snomed_code = Column(String(50))
    recorded_date = Column(Date)

    __table_args__ = (Index("ix_allergies_patient_id", "patient_id"),)


class Immunisation(Base):
    __tablename__ = "immunisations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    vaccine_name = Column(String(255), nullable=False)
    dose_number = Column(String(10))
    date_given = Column(Date)
    batch_number = Column(String(50))
    site = Column(String(50))
    route = Column(String(50))
    air_notification_sent = Column(Boolean, default=False)

    __table_args__ = (Index("ix_immunisations_patient_id", "patient_id"),)


class PatientHistory(Base):
    __tablename__ = "patient_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    category = Column(Enum(HistoryCategory), nullable=False)
    description = Column(Text, nullable=False)
    date_recorded = Column(Date)

    __table_args__ = (Index("ix_patient_history_patient_id", "patient_id"),)


class ConsentForm(Base):
    __tablename__ = "consent_forms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    form_type = Column(String(100), nullable=False)
    signed_at = Column(DateTime(timezone=True))
    signature_data = Column(Text)
    document_path = Column(String(500))

    __table_args__ = (Index("ix_consent_forms_patient_id", "patient_id"),)


class ClinicalImage(Base):
    __tablename__ = "clinical_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    image_url = Column(String(500), nullable=False)
    caption = Column(Text)
    body_site = Column(String(100))
    captured_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_clinical_images_patient_id", "patient_id"),)
