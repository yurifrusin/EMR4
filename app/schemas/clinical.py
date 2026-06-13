import uuid
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional, Any


class AllergyCreate(BaseModel):
    substance: str
    reaction: Optional[str] = None
    severity: Optional[str] = None
    snomed_code: Optional[str] = None
    recorded_date: Optional[date] = None


class AllergyOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    substance: str
    reaction: Optional[str] = None
    severity: Optional[str] = None
    snomed_code: Optional[str] = None
    recorded_date: Optional[date] = None

    model_config = {"from_attributes": True}


class HistoryCreate(BaseModel):
    category: str  # Medical | Surgical | Family | Social
    description: str
    date_recorded: Optional[date] = None


class HistoryOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    category: str
    description: str
    date_recorded: Optional[date] = None

    model_config = {"from_attributes": True}


class EncounterOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    practice_id: uuid.UUID
    consultation_date: Optional[datetime] = None
    consultation_type: Optional[str] = None
    status: Optional[str] = None
    template_type: Optional[str] = None
    raw_document_text: Optional[str] = None
    is_finalized: Optional[bool] = False

    model_config = {"from_attributes": True}


class CarePlanCreate(BaseModel):
    plan_type: str
    mbs_item: Optional[str] = None
    valid_until: Optional[date] = None
    review_date: Optional[date] = None
    plan_data: Optional[dict[str, Any]] = None


class CarePlanOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    plan_type: str
    mbs_item: Optional[str] = None
    status: Optional[str] = None
    valid_until: Optional[date] = None
    review_date: Optional[date] = None
    plan_data: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConsentFormCreate(BaseModel):
    form_type: str
    signature_data: Optional[str] = None
    document_path: Optional[str] = None


class ConsentFormOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    form_type: str
    signed_at: Optional[datetime] = None
    document_path: Optional[str] = None

    model_config = {"from_attributes": True}


class LetterDraftRequest(BaseModel):
    letter_type: str  # Referral | MedicalCertificate | SpecialistReply | ToWhomItMayConcern
    recipient_name: Optional[str] = None
    recipient_specialty: Optional[str] = None
    recipient_address: Optional[str] = None
    reason: str
    encounter_id: Optional[uuid.UUID] = None
    additional_context: Optional[str] = None


class LetterDraftResponse(BaseModel):
    letter_text: str
    subject_line: str
