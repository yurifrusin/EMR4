import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Numeric, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.models.base import Base


class ClaimType(str, enum.Enum):
    BulkBill = "BulkBill"
    PatientClaim = "PatientClaim"
    DVA = "DVA"
    WorkCover = "WorkCover"
    TAC = "TAC"
    ECLIPSE = "ECLIPSE"


class ClaimStatus(str, enum.Enum):
    Draft = "Draft"
    Submitted = "Submitted"
    Accepted = "Accepted"
    Rejected = "Rejected"
    Paid = "Paid"


class InvoiceStatus(str, enum.Enum):
    Draft = "Draft"
    Issued = "Issued"
    Paid = "Paid"
    Overdue = "Overdue"
    Cancelled = "Cancelled"


class MbsClaim(Base):
    __tablename__ = "mbs_claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    item_number = Column(String(10), nullable=False)
    description = Column(Text)
    claim_type = Column(Enum(ClaimType), default=ClaimType.BulkBill)
    amount = Column(Numeric(10, 2))
    gateway_claim_id = Column(String(100))
    claim_status = Column(Enum(ClaimStatus), default=ClaimStatus.Draft)
    submitted_at = Column(DateTime(timezone=True))
    response_data = Column(JSONB)

    __table_args__ = (
        Index("ix_mbs_claims_practice_id", "practice_id"),
        Index("ix_mbs_claims_patient_id", "patient_id"),
        Index("ix_mbs_claims_claim_status", "claim_status"),
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    total_amount = Column(Numeric(10, 2))
    paid_amount = Column(Numeric(10, 2), default=0)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.Draft)
    issued_at = Column(DateTime(timezone=True))

    __table_args__ = (Index("ix_invoices_patient_id", "patient_id"),)


class MbsDirectory(Base):
    __tablename__ = "mbs_directory"

    item_number = Column(String(10), primary_key=True)
    description = Column(Text, nullable=False)
    fee = Column(String(20))


class SnomedDirectory(Base):
    __tablename__ = "snomed_directory"

    concept_id = Column(String(50), primary_key=True)
    term = Column(String(255), nullable=False)
