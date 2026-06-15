import asyncio
import json
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
from google.cloud import discoveryengine_v1 as discoveryengine
from app.config import settings
from app.dependencies import get_db
from app.models.patients import Patient
from app.models.clinical import Encounter, EncounterStatus, ClinicalDiagnosis, Prescription
from app.models.billing import MbsClaim, MbsDirectory
import datetime

router = APIRouter(prefix="/api/v1", tags=["consultation"])

vertexai.init(project=settings.gcp_project, location=settings.gcp_location)
model = GenerativeModel("gemini-2.5-flash")


# --- Request schemas ---

class OverrideData(BaseModel):
    consultation_type: Optional[str] = None
    mbs_items: List[Dict[str, Any]] = []
    diagnoses: List[Dict[str, Any]] = []
    medications: List[Dict[str, Any]] = []


class ConsultationPayload(BaseModel):
    document_id: str
    text_delta: str
    is_finalized: bool
    clinician_overrides: Optional[OverrideData] = None


class FinalizePayload(BaseModel):
    document_id: str
    text_delta: str
    clinician_overrides: OverrideData
    audio_url: Optional[str] = None
    patient_id: Optional[str] = None


# --- Helpers ---

def _search_local_mbs(query: str, db: Session) -> str:
    words = [w.strip() for w in query.split() if len(w.strip()) > 2][:3] or ["Level"]
    conditions = [
        or_(MbsDirectory.description.ilike(f"%{w}%"), MbsDirectory.item_number.ilike(f"%{w}%"))
        for w in words
    ]
    results = db.query(MbsDirectory).filter(and_(*conditions)).limit(5).all()
    if not results:
        results = db.query(MbsDirectory).filter(or_(*conditions)).limit(5).all()
    if not results:
        results = db.query(MbsDirectory).filter(MbsDirectory.item_number.in_(["3", "23", "36", "44"])).all()
    return "\n\n".join(
        f"- MBS Item: {r.item_number} | Fee: {r.fee} | Description: {r.description[:200]}" for r in results
    )


def _search_mbs_rules(query: str, db: Session) -> str:
    try:
        endpoint = "discoveryengine.googleapis.com"
        if settings.data_store_location.lower() != "global":
            endpoint = f"{settings.data_store_location.lower()}-discoveryengine.googleapis.com"

        client = discoveryengine.SearchServiceClient(client_options={"api_endpoint": endpoint})
        serving_config = (
            f"projects/{settings.gcp_project}/locations/{settings.data_store_location}"
            f"/collections/default_collection/dataStores/{settings.data_store_id}"
            f"/servingConfigs/default_search"
        )
        response = client.search(
            discoveryengine.SearchRequest(serving_config=serving_config, query=query, page_size=5)
        )
        results = []
        for result in response.results:
            doc_dict = type(result.document).to_dict(result.document)
            struct_data = doc_dict.get("structData") or doc_dict.get("struct_data") or {}
            json_str = doc_dict.get("jsonData") or doc_dict.get("json_data") or ""
            if json_str and not struct_data:
                try:
                    struct_data = json.loads(json_str)
                except Exception:
                    pass
            if struct_data:
                results.append(
                    f"- MBS Item: {struct_data.get('item_number', '?')} "
                    f"| Fee: {struct_data.get('fee', '')} "
                    f"| Description: {struct_data.get('description', '')}"
                )
        return "\n\n".join(results) if results else _search_local_mbs(query, db)
    except Exception as e:
        print(f"Vertex AI Search error: {e}")
        return _search_local_mbs(query, db)


def _get_or_create_default_patient(db: Session) -> Patient:
    patient = db.query(Patient).filter_by(first_name="John", last_name="Citizen").first()
    if not patient:
        # Requires at least one practice to exist — use the first one found
        from app.models.tenancy import Practice
        practice = db.query(Practice).first()
        if not practice:
            raise RuntimeError("No practice found. Seed a practice first.")
        patient = Patient(
            practice_id=practice.id,
            first_name="John",
            last_name="Citizen",
            date_of_birth=datetime.date(1974, 4, 12),
            medicare_number="1234567890",
            ihi_number="8003608333333333",
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    return patient


def _save_encounter(db: Session, patient: Patient, document_id: str, text: str,
                    consult_type: str, mbs_items: list, diagnoses: list, medications: list):
    from app.models.tenancy import Practice
    practice = db.query(Practice).filter(Practice.id == patient.practice_id).first()
    encounter = Encounter(
        practice_id=patient.practice_id,
        patient_id=patient.id,
        google_doc_id=document_id,
        consultation_type=consult_type,
        raw_document_text=text,
        is_finalized=True,
        status=EncounterStatus.Finalized,
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)

    for item in mbs_items:
        item_num = item.get("item_number") or item.get("item")
        if item_num:
            db.add(MbsClaim(
                practice_id=patient.practice_id,
                patient_id=patient.id,
                encounter_id=encounter.id,
                item_number=str(item_num),
                description=item.get("description", ""),
                claim_status="Finalized",
            ))

    for diag in diagnoses:
        term = diag.get("term") or diag.get("concept_name") or ""
        if term:
            db.add(ClinicalDiagnosis(
                practice_id=patient.practice_id,
                patient_id=patient.id,
                encounter_id=encounter.id,
                term=term,
                snomed_ct_au_code=str(diag.get("snomed_ct_au_code") or diag.get("concept_id") or ""),
            ))

    for med in medications:
        drug_name = med.get("drug_name") or med.get("drug") or ""
        if drug_name:
            db.add(Prescription(
                practice_id=patient.practice_id,
                patient_id=patient.id,
                encounter_id=encounter.id,
                drug_name=drug_name,
                dosage_text=med.get("dosage_text") or med.get("dosage") or "",
                is_active=True,
            ))

    db.commit()
    return encounter


# --- Endpoints ---

ANALYSIS_PROMPT = """
You are an expert Australian Medical Billing and Clinical Coding assistant.
Read the following consultation notes and extract data into STRICT JSON format.
Do not include markdown blocks or conversational text. Return only raw JSON.

STEP 0 — EXTRACT DURATION FIRST:
Scan the notes for any explicit time statement. Duration rules:
   - < 5 min   → Item 3  (Level A)
   - 5-19 min  → Item 23 (Level B) ← DEFAULT
   - 20-39 min → Item 36 (Level C)
   - ≥ 40 min  → Item 44 (Level D)
If NO duration stated, default to Item 23.

CRITICAL RULES:
1. For ANY general consultation use ONLY items 3, 23, 36, or 44.
2. Only use other item numbers for explicitly described physical PROCEDURES.
3. For procedural items, verify body site matches MBS definition exactly.
4. Always extract the underlying diagnosis as a SNOMED CT AU code.

RETRIEVED MBS REFERENCE GUIDELINES:
{mbs_context}

Expected JSON (return ONLY this):
{{
    "encounter_metadata": {{
        "consultation_type": "Brief summary",
        "mbs_item_candidates": [{{"item_number": "XXX", "description": "Reasoning", "justification": "Quote"}}]
    }},
    "clinical_diagnoses": [{{"term": "Diagnosis Name", "snomed_ct_au_code": "XXXXXXX"}}],
    "medications_and_prescriptions": [{{"drug_name": "Drug", "dosage_text": "Dosage"}}]
}}

Consultation Notes:
{text}
"""


@router.post("/analyze-consultation")
async def analyze_consultation(payload: ConsultationPayload, db: Session = Depends(get_db)):
    if len(payload.text_delta.strip()) < 10:
        return {"encounter_metadata": {}, "clinical_diagnoses": [], "medications_and_prescriptions": []}

    mbs_context = _search_mbs_rules(payload.text_delta, db)
    prompt = ANALYSIS_PROMPT.format(mbs_context=mbs_context, text=payload.text_delta)

    extracted = {"encounter_metadata": {}, "clinical_diagnoses": [], "medications_and_prescriptions": []}
    try:
        response = await asyncio.to_thread(
            model.generate_content, prompt,
            generation_config=GenerationConfig(response_mime_type="application/json", temperature=0.1)
        )
        extracted = json.loads(response.text)
        mbs  = [m.get("item_number") for m in extracted.get("encounter_metadata", {}).get("mbs_item_candidates", [])]
        dx   = [d.get("term") for d in extracted.get("clinical_diagnoses", [])]
        rx   = [m.get("drug_name") for m in extracted.get("medications_and_prescriptions", [])]
        print(f"[analyze] type={extracted.get('encounter_metadata',{}).get('consultation_type','?')} | MBS={mbs} | Dx={dx} | Rx={rx}")
    except Exception as e:
        print(f"Vertex AI error: {e}")
        extracted["encounter_metadata"]["consultation_type"] = "AI Processing Error"

    save_error = None
    if payload.is_finalized:
        try:
            patient = _get_or_create_default_patient(db)
            overrides = payload.clinician_overrides
            consult_type = (
                (overrides.consultation_type if overrides else None)
                or extracted.get("encounter_metadata", {}).get("consultation_type", "Standard Consultation")
            )
            mbs_items = overrides.mbs_items if overrides else extracted.get("encounter_metadata", {}).get("mbs_item_candidates", [])
            diagnoses = overrides.diagnoses if overrides else extracted.get("clinical_diagnoses", [])
            medications = overrides.medications if overrides else extracted.get("medications_and_prescriptions", [])
            _save_encounter(db, patient, payload.document_id, payload.text_delta, consult_type, mbs_items, diagnoses, medications)
        except Exception as e:
            db.rollback()
            save_error = str(e)

    if payload.is_finalized:
        extracted["_saved"] = save_error is None
        if save_error:
            extracted["_save_error"] = save_error

    return extracted


@router.post("/scribe-consultation")
async def scribe_consultation(audio_file: UploadFile = File(...)):
    audio_bytes = await audio_file.read()

    audio_filename = f"{uuid.uuid4()}.webm"
    audio_filepath = os.path.join("static", "audio", audio_filename)
    os.makedirs(os.path.dirname(audio_filepath), exist_ok=True)
    with open(audio_filepath, "wb") as f:
        f.write(audio_bytes)

    prompt = """
You are an expert AI medical scribe for an Australian general practice.
Listen to the following audio recording of a doctor-patient consultation.

RULES:
1. Identify speakers (Doctor vs Patient).
2. Ignore small talk and non-clinical content.
3. Extract Subjective from patient statements; Objective/Assessment/Plan from doctor.
4. MBS billing: default Item 23 (Level B, 5-19 min) unless duration explicitly stated.
   < 5 min → Item 3 | 5-19 min → Item 23 | 20-39 min → Item 36 | ≥ 40 min → Item 44.

CRITICAL — medications_and_prescriptions:
- Include ONLY medications the doctor explicitly prescribes in THIS consultation.
- Do NOT include medications mentioned as allergies, adverse reactions, or contraindications.
- Do NOT include medications the patient already takes unless the doctor changes/reissues them.
- If a patient mentions "I'm allergic to Amoxil", do NOT add Amoxil to medications_and_prescriptions.

Return strict JSON only, no markdown:
{
    "raw_transcript": "Verbatim transcript of the full consultation.",
    "generated_clinical_note": "Full SOAP note suitable for insertion into a medical record.",
    "encounter_metadata": {
        "consultation_type": "Brief description e.g. Level B GP consultation",
        "mbs_item_candidates": [{"item_number": "23", "description": "Level B consultation", "justification": "Duration approx 10 min"}]
    },
    "clinical_diagnoses": [{"term": "Diagnosis name", "snomed_ct_au_code": "XXXXXXX"}],
    "medications_and_prescriptions": [{"drug_name": "DrugName", "dosage_text": "dose and frequency"}]
}
"""
    try:
        audio_part = Part.from_data(data=audio_bytes, mime_type=audio_file.content_type)
        response = await asyncio.to_thread(
            model.generate_content,
            [audio_part, prompt],
            generation_config=GenerationConfig(response_mime_type="application/json", temperature=0.1),
        )
        result = json.loads(response.text)
        mbs  = [m.get("item_number") for m in result.get("encounter_metadata", {}).get("mbs_item_candidates", [])]
        dx   = [d.get("term") for d in result.get("clinical_diagnoses", [])]
        rx   = [m.get("drug_name") for m in result.get("medications_and_prescriptions", [])]
        print(f"[scribe] type={result.get('encounter_metadata',{}).get('consultation_type','?')} | MBS={mbs} | Dx={dx} | Rx={rx}")
        result["audio_url"] = f"/static/audio/{audio_filename}"
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/finalize")
async def finalize_consultation(payload: FinalizePayload, db: Session = Depends(get_db)):
    try:
        # Use provided patient_id; fall back to default only if not supplied
        if payload.patient_id:
            patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
            if not patient:
                return {"_saved": False, "_save_error": f"Patient {payload.patient_id} not found"}
        else:
            patient = _get_or_create_default_patient(db)

        consult_type = payload.clinician_overrides.consultation_type or "Standard Consultation"
        encounter = _save_encounter(
            db, patient, payload.document_id, payload.text_delta, consult_type,
            payload.clinician_overrides.mbs_items,
            payload.clinician_overrides.diagnoses,
            payload.clinician_overrides.medications,
        )
        if payload.audio_url:
            path = payload.audio_url.lstrip("/")
            if os.path.exists(path):
                os.remove(path)

        # Build a brief clinical note from the saved data to insert into Word
        lines = [f"Consultation: {consult_type}"]
        if payload.clinician_overrides.diagnoses:
            dx = [d.get("term", "") for d in payload.clinician_overrides.diagnoses if d.get("term")]
            if dx:
                lines.append("Diagnoses: " + ", ".join(dx))
        if payload.clinician_overrides.mbs_items:
            mbs = [f"MBS {m.get('item_number','')}" for m in payload.clinician_overrides.mbs_items if m.get("item_number")]
            if mbs:
                lines.append("Billed: " + ", ".join(mbs))
        if payload.clinician_overrides.medications:
            rx = [f"{m.get('drug_name','')} {m.get('dosage_text','')}".strip()
                  for m in payload.clinician_overrides.medications if m.get("drug_name")]
            if rx:
                lines.append("Prescribed: " + "; ".join(rx))

        return {
            "_saved": True,
            "encounter_id": str(encounter.id),
            "generated_clinical_note": "\n".join(lines),
        }
    except Exception as e:
        db.rollback()
        return {"_saved": False, "_save_error": str(e)}
