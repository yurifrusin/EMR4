import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from app.config import settings
from app.dependencies import get_db, get_current_user
from app.models.tenancy import User, Practitioner
from app.models.patients import Patient
from app.models.clinical import Encounter, Prescription, ClinicalDiagnosis, Allergy
from app.schemas.clinical import LetterDraftRequest, LetterDraftResponse

router = APIRouter(prefix="/api/v1/patients/{patient_id}/letters", tags=["letters"])

ai_client = genai.Client(
    vertexai=True,
    project=settings.gcp_project,
    location=settings.gcp_location
)

LETTER_TYPES = {
    "Referral": "a specialist referral letter",
    "MedicalCertificate": "a medical certificate",
    "SpecialistReply": "a reply to a specialist",
    "ToWhomItMayConcern": "a to-whom-it-may-concern letter",
    "WorkCover": "a WorkCover medical report",
}


@router.post("/draft", response_model=LetterDraftResponse)
async def draft_letter(
    patient_id: uuid.UUID,
    body: LetterDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.practice_id == current_user.practice_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Build context from the patient record
    allergy_list = ", ".join(
        a.substance for a in db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
    ) or "None known"

    active_meds = db.query(Prescription).filter(
        Prescription.patient_id == patient_id, Prescription.is_active == True
    ).all()
    med_list = "; ".join(f"{m.drug_name} {m.dosage_text or ''}" for m in active_meds) or "Nil"

    active_dx = db.query(ClinicalDiagnosis).filter(
        ClinicalDiagnosis.patient_id == patient_id, ClinicalDiagnosis.is_active == True
    ).all()
    dx_list = ", ".join(d.term for d in active_dx) or "Nil"

    encounter_context = ""
    if body.encounter_id:
        enc = db.query(Encounter).filter(Encounter.id == body.encounter_id).first()
        if enc and enc.raw_document_text:
            encounter_context = f"\n\nEncounter notes:\n{enc.raw_document_text[:2000]}"

    practitioner = None
    if current_user.practitioner_id:
        practitioner = db.query(Practitioner).filter(
            Practitioner.id == current_user.practitioner_id
        ).first()

    dr_name = f"Dr {practitioner.first_name} {practitioner.last_name}" if practitioner else "The treating doctor"
    provider_num = practitioner.provider_number if practitioner else ""

    letter_description = LETTER_TYPES.get(body.letter_type, "a clinical letter")

    prompt = f"""You are an expert Australian GP writing {letter_description}.
Write a professional, concise letter in Australian medical style.

PATIENT: {patient.first_name} {patient.last_name}
DOB: {patient.date_of_birth}
Medicare: {patient.medicare_number or 'N/A'}

ACTIVE PROBLEMS: {dx_list}
MEDICATIONS: {med_list}
ALLERGIES: {allergy_list}

REASON: {body.reason}
{f"RECIPIENT: {body.recipient_name} ({body.recipient_specialty})" if body.recipient_name else ""}
{f"ADDITIONAL CONTEXT: {body.additional_context}" if body.additional_context else ""}
{encounter_context}

Return ONLY a JSON object with two fields:
- "subject_line": a concise subject line (e.g. "Re: John Citizen DOB 12/04/1974 — Referral for Cardiology Review")
- "letter_text": the full letter body text (no letterhead — that is pre-printed). Use \\n for line breaks. Begin with "Dear {body.recipient_name or 'Colleague'},"

Australian conventions:
- Formal but warm tone
- Use generic drug names (not brand names) unless brand is clinically significant
- Reference relevant MBS item numbers where appropriate
- Sign off: "Yours sincerely,\\n\\n{dr_name}\\nMBBS, FRACGP\\nProvider No: {provider_num}"
"""

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.3)
        )
        data = json.loads(response.text)
        return LetterDraftResponse(
            letter_text=data.get("letter_text", ""),
            subject_line=data.get("subject_line", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI letter drafting failed: {e}")
