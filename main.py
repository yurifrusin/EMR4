import json
import os
import datetime
import uuid
from fastapi import FastAPI, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from google.cloud import discoveryengine_v1 as discoveryengine
from sqlalchemy import or_, and_
from database import SessionLocal
from models import Patient, Encounter, MbsClaim, ClinicalDiagnosis, Prescription, MbsDirectory, SnomedDirectory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- VERTEX AI CONFIGURATION ---
# Temporarily using us-central1 for development to bypass the 5 RPM new-account quota.
# Switch back to australia-southeast1 (Sydney) for production APP compliance.
GCP_PROJECT = os.environ.get("GCP_PROJECT", "emr4-copilot")
DATA_STORE_ID = os.environ.get("DATA_STORE_ID", "mbs-search-app_1780903132373")
DATA_STORE_LOCATION = os.environ.get("DATA_STORE_LOCATION", "global")

vertexai.init(project=GCP_PROJECT, location="us-central1")

# We use the Flash model for high-speed, low-latency UI syncing
model = GenerativeModel("gemini-2.5-flash")

# --- DATA MODELS ---
class OverrideData(BaseModel):
    consultation_type: Optional[str] = None  # GP's edited consultation type
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

# --- LOCAL DATABASE FALLBACK SEARCH ---
def search_local_mbs(query: str) -> str:
    print(f"🔎 Querying local database for MBS rules fallback (Query: '{query}')")
    db = SessionLocal()
    try:
        # Split query into keywords to do an AND/OR search
        words = [w.strip() for w in query.split() if len(w.strip()) > 2]
        if not words:
            # Fallback words
            words = ["Level"]

        db_query = db.query(MbsDirectory)

        # Build keyword filter conditions (max first 3 keywords to avoid over-filtering)
        conditions = []
        for word in words[:3]:
            conditions.append(or_(
                MbsDirectory.description.ilike(f"%{word}%"),
                MbsDirectory.item_number.ilike(f"%{word}%")
            ))

        local_results = db_query.filter(and_(*conditions)).limit(5).all()

        # If no results match all keywords, relax condition to OR
        if not local_results:
            conditions = [or_(
                MbsDirectory.description.ilike(f"%{word}%"),
                MbsDirectory.item_number.ilike(f"%{word}%")
            ) for word in words[:3]]
            local_results = db_query.filter(or_(*conditions)).limit(5).all()

        # If still nothing, return standard Level B/C/D items
        if not local_results:
            local_results = db.query(MbsDirectory).filter(MbsDirectory.item_number.in_(["3", "23", "36", "44"])).all()

        formatted = []
        for item in local_results:
            formatted.append(f"MBS Item: {item.item_number} | Fee: {item.fee} | Description: {item.description}")

        return "\n\n".join([f"- {res}" for res in formatted])
    except Exception as e:
        print(f"⚠️ Local MBS Search Error: {e}")
        return "No matching MBS rules found (Local DB error)."
    finally:
        db.close()

def search_mbs_rules(query: str, project_id: str, location: str, data_store_id: str) -> str:
    try:
        endpoint = "discoveryengine.googleapis.com"
        if location and location.lower() != "global":
            endpoint = f"{location.lower()}-discoveryengine.googleapis.com"

        client = discoveryengine.SearchServiceClient(
            client_options={"api_endpoint": endpoint}
        )
        serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}/servingConfigs/default_search"

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=5
        )

        print(f"📡 Querying Vertex AI Search (Engine: {data_store_id}) with: '{query}'")
        response = client.search(request)
        print(f"🔍 Search results count: {len(response.results)}")

        results = []
        for i, result in enumerate(response.results):
            doc = result.document

            # 1. THE FIX: Strip Google's Protocol Buffer wrappers into a standard Python Dictionary
            doc_dict = type(doc).to_dict(doc)

            # 2. THE DEBUGGER: Print the raw JSON of the first result so we can see exactly where the data is
            if i == 0:
                print("\n=== RAW DOC DICT DEBUG ===")
                print(json.dumps(doc_dict, indent=2)[:800])  # Print the first 800 chars safely
                print("==========================\n")

            # 3. Check the two places Vertex AI hides structured CSV data
            struct_data = doc_dict.get("structData", {}) or doc_dict.get("struct_data", {})
            json_data_str = doc_dict.get("jsonData", "") or doc_dict.get("json_data", "")

            # If Google passed it as a raw JSON string, parse it into a dictionary
            if json_data_str and not struct_data:
                try:
                    struct_data = json.loads(json_data_str)
                except Exception:
                    pass

            # 4. Extract the exact keys from your schema!
            if struct_data:
                item_number = struct_data.get("item_number", "Unknown Code")
                description = struct_data.get("description", "No description available in GCP")
                fee = struct_data.get("fee", "")
                mbs_entry = f"MBS Item: {item_number} | Fee: {fee} | Description: {description}"
                results.append(mbs_entry)
            else:
                # 5. Fallback to snippets if structured data completely fails
                snippets = doc_dict.get("derivedStructData", {}).get("snippets", [])
                if snippets:
                    results.append(snippets[0].get("snippet", ""))

        if not results:
            print("⚠️ Vertex AI Search returned 0 results. Falling back to local DB search.")
            return search_local_mbs(query)

        return "\n\n".join([f"- {res}" for res in results])

    except Exception as e:
        print(f"⚠️ Vertex AI Search Error: {e}. Falling back to local DB search.")
        return search_local_mbs(query)

def get_or_create_default_patient(db):
    patient = db.query(Patient).filter_by(first_name="John", last_name="Citizen").first()
    if not patient:
        patient = Patient(
            first_name="John",
            last_name="Citizen",
            date_of_birth=datetime.date(1974, 4, 12),
            medicare_number="1234567890",
            ihi_number="8003608333333333"
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
    return patient

# --- THE LIVE AI ENDPOINT ---
@app.post("/api/v1/analyze-consultation")
async def analyze_consultation(payload: ConsultationPayload):
    print("=========================================")
    print(f"📡 Sending {len(payload.text_delta)} chars to Vertex AI (Sydney)...")

    # If the document is basically empty, return empty boxes
    if len(payload.text_delta.strip()) < 10:
        return {
            "encounter_metadata": {},
            "clinical_diagnoses": [],
            "medications_and_prescriptions": []
        }

    # Query the existing Vertex AI Data Store for MBS candidates
    mbs_context = search_mbs_rules(
        query=payload.text_delta,
        project_id=GCP_PROJECT,
        location=DATA_STORE_LOCATION,
        data_store_id=DATA_STORE_ID
    )
    print(f"🔍 Retrieved MBS context ({len(mbs_context)} chars)")

    # The Prompt: Forcing the AI to act as a structured data extractor
    prompt = f"""
    You are an expert Australian Medical Billing and Clinical Coding assistant for an Australian medical practice.
    Read the following consultation notes and extract the data into STRICT JSON format.
    Do not include markdown blocks or any conversational text. Just the raw JSON.

    STEP 0 — EXTRACT DURATION FIRST (do this before anything else):
    Scan the notes for any explicit time statement (e.g. "12 minutes", "total time: 25 min", "45-minute review").
    If found, use that duration to determine the attendance item BEFORE reading the MBS context.
    Duration rules are absolute and override all other considerations for GP attendance items:
       - Stated duration < 5 min   → Item 3  (Level A)
       - Stated duration 5-19 min  → Item 23 (Level B)  ← DEFAULT for any standard consultation
       - Stated duration 20-39 min → Item 36 (Level C)
       - Stated duration ≥ 40 min  → Item 44 (Level D)
    If NO duration is stated, default to Item 23 unless the note describes only a trivial single-task visit.

    CRITICAL RULES:
    1. STRICT ATTENDANCE WHITELIST: For ANY general consultation, review, assessment, or standard attendance, you MUST ONLY use items 3, 23, 36, or 44. You must IGNORE any other attendance items (like 17645, 701, 703, etc.) that might appear in the retrieved guidelines.
    2. PROCEDURES EXCEPTION: The ONLY time you may use an item other than 3, 23, 36, or 44 is if the notes explicitly describe a specific physical PROCEDURE (e.g., skin excision, wound suturing, joint injection). Only for physical procedures should you use the item numbers from the RETRIEVED MBS REFERENCE GUIDELINES.
    3. ANATOMY MATCHING: For procedural items, verify the body site in the notes matches the MBS definition exactly.
    4. MANDATORY SNOMED: Always extract the underlying diagnosis as a SNOMED CT AU code.

    RETRIEVED MBS REFERENCE GUIDELINES:
    {mbs_context}

    Expected JSON Structure (return ONLY this, no markdown):
    {{
        "encounter_metadata": {{
            "consultation_type": "Brief summary of visit type",
            "mbs_item_candidates": [{{
                "item_number": "XXX",
                "description": "Reasoning including the stated duration or procedure matched",
                "justification": "Quote the exact time found in notes OR the procedural rule applied"
            }}]
        }},
        "clinical_diagnoses": [{{"term": "Diagnosis Name", "snomed_ct_au_code": "XXXXXXX"}}],
        "medications_and_prescriptions": [{{"drug_name": "Drug", "dosage_text": "Dosage"}}]
    }}

    Consultation Notes:
    {payload.text_delta}
    """

    # Temperature 0.1 for balanced factual extraction without hallucinated item codes
    generation_config = GenerationConfig(
        response_mime_type="application/json",
        temperature=0.1
    )

    extracted_data = {
        "encounter_metadata": {},
        "clinical_diagnoses": [],
        "medications_and_prescriptions": []
    }

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        # Parse the AI's string response back into a Python dictionary
        extracted_data = json.loads(response.text)
        print("✅ Vertex AI Extraction Successful!")
        print(f"DEBUG EXTRACTED: {json.dumps(extracted_data)[:200]}")
    except Exception as e:
        print(f"❌ Vertex AI Error: {e}")
        extracted_data = {
            "encounter_metadata": {"consultation_type": "AI Processing Error"},
            "clinical_diagnoses": [],
            "medications_and_prescriptions": []
        }

    # Save to database if finalized
    save_error = None
    if payload.is_finalized:
        db = SessionLocal()
        try:
            patient = get_or_create_default_patient(db)

            # Determine the consultation type: prefer GP's override, then AI extraction
            consult_type = (
                (payload.clinician_overrides.consultation_type if payload.clinician_overrides else None)
                or extracted_data.get("encounter_metadata", {}).get("consultation_type", "Standard Consultation")
            )

            # Create Encounter record
            encounter = Encounter(
                patient_id=patient.id,
                google_doc_id=payload.document_id,
                consultation_type=consult_type,
                raw_document_text=payload.text_delta,
                is_finalized=True
            )
            db.add(encounter)
            db.commit()
            db.refresh(encounter)

            # Determine source of items (either clinician_overrides or extracted_data)
            mbs_items = []
            diagnoses = []
            medications = []

            if payload.clinician_overrides:
                mbs_items = payload.clinician_overrides.mbs_items
                diagnoses = payload.clinician_overrides.diagnoses
                medications = payload.clinician_overrides.medications
            else:
                mbs_items = extracted_data.get("encounter_metadata", {}).get("mbs_item_candidates", [])
                diagnoses = extracted_data.get("clinical_diagnoses", [])
                medications = extracted_data.get("medications_and_prescriptions", [])

            # Insert MBS Claims
            for item in mbs_items:
                item_num = item.get("item_number") or item.get("item")
                if item_num:
                    claim = MbsClaim(
                        encounter_id=encounter.id,
                        item_number=str(item_num),
                        description=item.get("description", ""),
                        status="Finalized"
                    )
                    db.add(claim)

            # Insert Clinical Diagnoses
            for diag in diagnoses:
                snomed_code = diag.get("snomed_ct_au_code") or diag.get("concept_id") or ""
                term = diag.get("term") or diag.get("concept_name") or ""
                if term:
                    cd = ClinicalDiagnosis(
                        patient_id=patient.id,
                        encounter_id=encounter.id,
                        term=term,
                        snomed_ct_au_code=str(snomed_code)
                    )
                    db.add(cd)

            # Insert Prescriptions
            for med in medications:
                drug_name = med.get("drug_name") or med.get("drug") or ""
                if drug_name:
                    rx = Prescription(
                        patient_id=patient.id,
                        encounter_id=encounter.id,
                        drug_name=drug_name,
                        dosage_text=med.get("dosage_text") or med.get("dosage") or "",
                        is_active=True
                    )
                    db.add(rx)

            db.commit()
            print(f"💾 Saved finalized encounter {encounter.id} to local DB.")
        except Exception as db_err:
            db.rollback()
            save_error = str(db_err)
            print(f"⚠️ Failed to save finalized encounter to DB: {db_err}")
        finally:
            db.close()

    # Include save status in response so the frontend can show real errors
    if payload.is_finalized:
        extracted_data["_saved"] = save_error is None
        if save_error:
            extracted_data["_save_error"] = save_error

    return extracted_data

import base64
from vertexai.generative_models import Part

# --- THE AUDIO SCRIBE ENDPOINT ---
@app.post("/api/v1/scribe-consultation")
async def scribe_consultation(audio_file: UploadFile = File(...)):
    print("=========================================")
    print(f"🎤 Received audio file: {audio_file.filename} ({audio_file.content_type})")

    try:
        # 1. Read the raw binary bytes directly from the uploaded file
        audio_bytes = await audio_file.read()

        # Save audio to static folder temporarily
        audio_filename = f"{uuid.uuid4()}.webm"
        audio_filepath = os.path.join("static", "audio", audio_filename)
        with open(audio_filepath, "wb") as f:
            f.write(audio_bytes)
        audio_url = f"/static/audio/{audio_filename}"

        # 2. Package it securely for Vertex AI's multimodal engine
        audio_part = Part.from_data(data=audio_bytes, mime_type=audio_file.content_type)

        # 3. The Master Ambient Prompt (Supercharged for Diarization)
        prompt = """
        You are an expert AI medical scribe and clinical coder for an Australian general practice.
        Listen to the following audio recording of a consultation between a doctor and a patient.

        DIARIZATION & AMBIENT RULES:
        1. Identify the speakers (Doctor vs. Patient).
        2. IGNORE all small talk, pleasantries, or non-clinical banter (e.g. talking about the weather or holidays).
        3. Extract the 'Subjective' history *only* from the patient's statements and complaints.
        4. Extract the 'Objective', 'Assessment', and 'Plan' primarily from the doctor's summary, physical exam dictation, or instructions to the patient.

        TASK: Write a highly professional, concise clinical SOAP note summarizing the medical facts, and extract structured billing/clinical data based on the conversation.

        Return a strict JSON object with this EXACT structure:
        {
            "raw_transcript": "The verbatim transcript of the audio recording.",
            "generated_clinical_note": "The full text of the SOAP note here. Use standard medical abbreviations.",
            "encounter_metadata": {
                "consultation_type": "Brief summary",
                "mbs_item_candidates": [
                    {
                        "item_number": "XXX",
                        "description": "Standard attendance or procedure code",
                        "justification": "Why this code applies based on the audio"
                    }
                ]
            },
            "clinical_diagnoses": [{"term": "Diagnosis Name", "snomed_ct_au_code": "XXXXXXX"}],
            "medications_and_prescriptions": [{"drug_name": "Drug Name", "dosage_text": "Dosage instructions"}]
        }
        """

        # Force the model to return our JSON structure
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1
        )

        # Pass BOTH the audio part and the text prompt to Gemini
        response = model.generate_content([audio_part, prompt], generation_config=generation_config)

        extracted_data = json.loads(response.text)
        extracted_data["audio_url"] = audio_url
        print("✅ Vertex AI Audio Transcription & Extraction Successful!")
        return extracted_data

    except Exception as e:
        print(f"❌ Vertex AI Audio Error: {e}")
        return {"error": str(e)}

# --- AUTOCOMPLETE ENDPOINTS ---
@app.get("/api/v1/search-mbs")
def search_mbs_endpoint(q: str = Query(..., min_length=2)):
    db = SessionLocal()
    try:
        results = db.query(MbsDirectory).filter(
            or_(
                MbsDirectory.item_number.ilike(f"%{q}%"),
                MbsDirectory.description.ilike(f"%{q}%")
            )
        ).limit(10).all()
        return [{"item_number": r.item_number, "description": r.description, "fee": r.fee} for r in results]
    finally:
        db.close()

@app.get("/api/v1/search-snomed")
def search_snomed_endpoint(q: str = Query(..., min_length=2)):
    db = SessionLocal()
    try:
        results = db.query(SnomedDirectory).filter(
            or_(
                SnomedDirectory.concept_id.ilike(f"%{q}%"),
                SnomedDirectory.term.ilike(f"%{q}%")
            )
        ).limit(10).all()
        return [{"concept_id": r.concept_id, "term": r.term} for r in results]
    finally:
        db.close()

# --- FINALIZE ENDPOINT (no AI call — saves directly from clinician overrides) ---
@app.post("/api/v1/finalize")
async def finalize_consultation(payload: FinalizePayload):
    print("=========================================")
    print(f"💾 Finalize request received for doc '{payload.document_id}'")

    db = SessionLocal()
    try:
        patient = get_or_create_default_patient(db)

        consult_type = payload.clinician_overrides.consultation_type or "Standard Consultation"

        encounter = Encounter(
            patient_id=patient.id,
            google_doc_id=payload.document_id,
            consultation_type=consult_type,
            raw_document_text=payload.text_delta,
            is_finalized=True
        )
        db.add(encounter)
        db.commit()
        db.refresh(encounter)

        # MBS Claims
        for item in payload.clinician_overrides.mbs_items:
            item_num = item.get("item_number") or item.get("item")
            if item_num:
                db.add(MbsClaim(
                    encounter_id=encounter.id,
                    item_number=str(item_num),
                    description=item.get("description", ""),
                    status="Finalized"
                ))

        # Clinical Diagnoses
        for diag in payload.clinician_overrides.diagnoses:
            term = diag.get("term") or diag.get("concept_name") or ""
            if term:
                db.add(ClinicalDiagnosis(
                    patient_id=patient.id,
                    encounter_id=encounter.id,
                    term=term,
                    snomed_ct_au_code=str(diag.get("snomed_ct_au_code") or diag.get("concept_id") or "")
                ))

        # Prescriptions
        for med in payload.clinician_overrides.medications:
            drug_name = med.get("drug_name") or med.get("drug") or ""
            if drug_name:
                db.add(Prescription(
                    patient_id=patient.id,
                    encounter_id=encounter.id,
                    drug_name=drug_name,
                    dosage_text=med.get("dosage_text") or med.get("dosage") or "",
                    is_active=True
                ))

        db.commit()
        print(f"✅ Finalized encounter {encounter.id} saved successfully.")

        if payload.audio_url:
            audio_path = payload.audio_url.lstrip("/")
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"🗑️ Deleted temporary audio file: {audio_path}")

        return {"_saved": True, "encounter_id": str(encounter.id)}

    except Exception as e:
        db.rollback()
        err = str(e)
        print(f"⚠️ Finalize DB error: {err}")
        return {"_saved": False, "_save_error": err}
    finally:
        db.close()