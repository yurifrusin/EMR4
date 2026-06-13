import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Date, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.models.base import Base


class RequestType(str, enum.Enum):
    Pathology = "Pathology"
    Radiology = "Radiology"
    Specialist = "Specialist"
    Other = "Other"


class RequestStatus(str, enum.Enum):
    Pending = "Pending"
    ResultReceived = "ResultReceived"
    Reviewed = "Reviewed"


class ResultSource(str, enum.Enum):
    PIT = "PIT"
    HL7 = "HL7"
    Manual = "Manual"
    Scan = "Scan"


class ResultStatus(str, enum.Enum):
    New = "New"
    Reviewed = "Reviewed"
    ActionRequired = "ActionRequired"
    Filed = "Filed"


class ResultFlag(str, enum.Enum):
    Normal = "Normal"
    Low = "Low"
    High = "High"
    Critical = "Critical"


class ReferralStatus(str, enum.Enum):
    Draft = "Draft"
    Sent = "Sent"
    Accepted = "Accepted"
    Completed = "Completed"


class ReminderType(str, enum.Enum):
    ResultFollowUp = "ResultFollowUp"
    Recall = "Recall"
    ReviewAppointment = "ReviewAppointment"
    CarePlanReview = "CarePlanReview"
    Custom = "Custom"


class DocumentType(str, enum.Enum):
    SpecialistLetter = "SpecialistLetter"
    Report = "Report"
    Correspondence = "Correspondence"
    Other = "Other"


class TriageStatus(str, enum.Enum):
    Pending = "Pending"
    Triaged = "Triaged"
    Reviewed = "Reviewed"


class TestRequest(Base):
    __tablename__ = "test_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    request_type = Column(Enum(RequestType), nullable=False)
    request_text = Column(Text)
    urgency = Column(String(50))
    status = Column(Enum(RequestStatus), default=RequestStatus.Pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_test_requests_patient_id", "patient_id"),)


class Result(Base):
    __tablename__ = "results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    test_request_id = Column(UUID(as_uuid=True), ForeignKey("test_requests.id"), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    result_source = Column(Enum(ResultSource), nullable=False)
    lab_name = Column(String(255))
    specimen_date = Column(Date)
    report_date = Column(Date)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(ResultStatus), default=ResultStatus.New)
    reviewed_at = Column(DateTime(timezone=True))
    raw_message = Column(Text)
    parsed_data = Column(JSONB)
    is_abnormal = Column(Boolean, default=False)
    ai_summary = Column(Text)
    display_pdf_url = Column(String(500))

    __table_args__ = (
        Index("ix_results_practice_id", "practice_id"),
        Index("ix_results_patient_id", "patient_id"),
        Index("ix_results_status", "status"),
    )


class ResultItem(Base):
    __tablename__ = "result_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("results.id"), nullable=False)
    test_name = Column(String(255), nullable=False)
    value = Column(String(100))
    units = Column(String(50))
    reference_range = Column(String(100))
    flag = Column(Enum(ResultFlag), default=ResultFlag.Normal)
    loinc_code = Column(String(20))

    __table_args__ = (Index("ix_result_items_result_id", "result_id"),)


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    referral_to = Column(String(255))
    specialty = Column(String(100))
    reason = Column(Text)
    urgency = Column(String(50))
    status = Column(Enum(ReferralStatus), default=ReferralStatus.Draft)
    letter_document_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_referrals_patient_id", "patient_id"),)


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    triggered_by_result_id = Column(UUID(as_uuid=True), ForeignKey("results.id"), nullable=True)
    reminder_type = Column(Enum(ReminderType), nullable=False)
    message = Column(Text)
    due_date = Column(Date)
    is_dismissed = Column(Boolean, default=False)

    __table_args__ = (
        Index("ix_reminders_practice_id", "practice_id"),
        Index("ix_reminders_patient_id", "patient_id"),
    )


class ScannedDocument(Base):
    __tablename__ = "scanned_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    triaged_to = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_url = Column(String(500), nullable=False)
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())
    triage_status = Column(Enum(TriageStatus), default=TriageStatus.Pending)
    notes = Column(Text)

    __table_args__ = (Index("ix_scanned_documents_patient_id", "patient_id"),)
