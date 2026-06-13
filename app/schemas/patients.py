import uuid
from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    medicare_number: Optional[str] = None
    ihi_number: Optional[str] = None
    dva_number: Optional[str] = None
    sex: Optional[str] = None
    gender_identity: Optional[str] = None
    indigenous_status: Optional[str] = None
    preferred_language: Optional[str] = None
    email: Optional[str] = None
    phone_mobile: Optional[str] = None
    phone_home: Optional[str] = None
    address_line1: Optional[str] = None
    address_suburb: Optional[str] = None
    address_state: Optional[str] = None
    address_postcode: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    concession_type: Optional[str] = None


class PatientUpdate(PatientCreate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None


class PatientOut(BaseModel):
    id: uuid.UUID
    practice_id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    medicare_number: Optional[str] = None
    ihi_number: Optional[str] = None
    dva_number: Optional[str] = None
    sex: Optional[str] = None
    gender_identity: Optional[str] = None
    indigenous_status: Optional[str] = None
    preferred_language: Optional[str] = None
    email: Optional[str] = None
    phone_mobile: Optional[str] = None
    phone_home: Optional[str] = None
    address_line1: Optional[str] = None
    address_suburb: Optional[str] = None
    address_state: Optional[str] = None
    address_postcode: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    concession_type: Optional[str] = None
    sms_consent: Optional[bool] = False
    consent_facial_recognition: Optional[bool] = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AllergyOut(BaseModel):
    id: uuid.UUID
    substance: str
    reaction: Optional[str] = None
    severity: Optional[str] = None
    snomed_code: Optional[str] = None
    recorded_date: Optional[date] = None

    model_config = {"from_attributes": True}


class EncounterSummary(BaseModel):
    id: uuid.UUID
    consultation_date: Optional[datetime] = None
    consultation_type: Optional[str] = None
    status: Optional[str] = None
    template_type: Optional[str] = None

    model_config = {"from_attributes": True}


class MedicationSummary(BaseModel):
    id: uuid.UUID
    drug_name: str
    dosage_text: Optional[str] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = True

    model_config = {"from_attributes": True}


class DiagnosisSummary(BaseModel):
    id: uuid.UUID
    term: str
    snomed_ct_au_code: Optional[str] = None
    is_active: Optional[bool] = True

    model_config = {"from_attributes": True}


class PatientSummary(BaseModel):
    patient: PatientOut
    active_diagnoses: list[DiagnosisSummary] = []
    active_medications: list[MedicationSummary] = []
    allergies: list[AllergyOut] = []
    recent_encounters: list[EncounterSummary] = []
