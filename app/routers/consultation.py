import hashlib
import json
import re
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy import or_, and_, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictStr,
    field_validator,
    model_validator,
)
from typing import Optional, List, Dict, Any, Literal
from google.cloud import discoveryengine_v1 as discoveryengine
from app.config import settings
from app.dependencies import get_command_session_factory, get_db, get_current_user
from app.models.ai_audit import AccessAiAuditLog
from app.models.patients import Patient
from app.models.tenancy import Practitioner, User, UserRole
from app.models.clinical import Encounter, EncounterStatus, ClinicalDiagnosis, Prescription
from app.models.billing import MbsClaim, MbsDirectory, ClaimStatus
from app.services.ai.service import AiService
from app.services.ai.audit_events import (
    AiAuditDecision,
    AiAuditEventType,
    AiAuditSourceSurface,
    build_access_ai_audit_event,
)
from app.services.ai.audit_store import persist_access_ai_audit_events
from app.services.ai.entitlements import actor_context_from_user

router = APIRouter(prefix="/api/v1", tags=["consultation"])

_ai_service = AiService()


# --- Request schemas ---

class OverrideData(BaseModel):
    consultation_type: Optional[str] = None
    mbs_items: List[Dict[str, Any]] = []
    diagnoses: List[Dict[str, Any]] = []
    medications: List[Dict[str, Any]] = []


class ConsultationPayload(BaseModel):
    document_id: str
    text_delta: str
    is_finalized: Literal[False] = False
    clinician_overrides: Optional[OverrideData] = None


def _same_exact_value(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (
            left.keys() == right.keys()
            and all(_same_exact_value(left[key], right[key]) for key in left)
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _same_exact_value(a, b) for a, b in zip(left, right)
        )
    return left == right


def _canonicalize_aliases(
    value: object,
    aliases: dict[str, str],
) -> object:
    if not isinstance(value, dict):
        return value
    result = dict(value)
    for canonical, alias in aliases.items():
        if canonical in result and alias in result:
            if not _same_exact_value(result[canonical], result[alias]):
                raise ValueError(f"conflicting values for {canonical} and {alias}")
            del result[alias]
        elif alias in result:
            result[canonical] = result.pop(alias)
    return result


def _require_meaningful(value: str) -> str:
    if not value.strip():
        raise ValueError("value must contain non-whitespace characters")
    return value


class FinalizeMbsItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_number: StrictStr = Field(min_length=1, max_length=10)
    description: StrictStr = Field(default="", max_length=2048)

    @model_validator(mode="before")
    @classmethod
    def accept_known_aliases(cls, value: object) -> object:
        return _canonicalize_aliases(value, {"item_number": "item"})

    @field_validator("item_number")
    @classmethod
    def require_item_number(cls, value: str) -> str:
        return _require_meaningful(value)


class FinalizeDiagnosis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    term: StrictStr = Field(min_length=1, max_length=255)
    snomed_ct_au_code: StrictStr = Field(min_length=1, max_length=50)

    @model_validator(mode="before")
    @classmethod
    def accept_known_aliases(cls, value: object) -> object:
        return _canonicalize_aliases(
            value,
            {
                "term": "concept_name",
                "snomed_ct_au_code": "concept_id",
            },
        )

    @field_validator("term", "snomed_ct_au_code")
    @classmethod
    def require_diagnosis_identity(cls, value: str) -> str:
        return _require_meaningful(value)


class FinalizeMedication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drug_name: StrictStr = Field(min_length=1, max_length=255)
    dosage_text: StrictStr = Field(default="", max_length=2048)

    @model_validator(mode="before")
    @classmethod
    def accept_known_aliases(cls, value: object) -> object:
        return _canonicalize_aliases(
            value,
            {
                "drug_name": "drug",
                "dosage_text": "dosage",
            },
        )

    @field_validator("drug_name")
    @classmethod
    def require_drug_name(cls, value: str) -> str:
        return _require_meaningful(value)


class FinalizeOverrideData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consultation_type: StrictStr | None = Field(default=None, max_length=255)
    mbs_items: list[FinalizeMbsItem] = Field(default_factory=list, max_length=100)
    diagnoses: list[FinalizeDiagnosis] = Field(default_factory=list, max_length=100)
    medications: list[FinalizeMedication] = Field(default_factory=list, max_length=100)

    @model_validator(mode="before")
    @classmethod
    def accept_known_aliases(cls, value: object) -> object:
        return _canonicalize_aliases(
            value,
            {
                "mbs_items": "mbs_item_candidates",
                "diagnoses": "clinical_diagnoses",
                "medications": "medications_and_prescriptions",
            },
        )

    @field_validator("consultation_type")
    @classmethod
    def reject_whitespace_consultation_type(cls, value: str | None) -> str | None:
        if value is not None and value and not value.strip():
            raise ValueError("consultation_type cannot be whitespace-only")
        return value


class FinalizePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: uuid.UUID
    document_context: StrictStr = Field(min_length=1, max_length=2048)
    text_delta: StrictStr = Field(min_length=1, max_length=100000)
    clinician_overrides: FinalizeOverrideData
    clinician_attested: StrictBool
    audio_url: StrictStr | None = Field(default=None, max_length=2048)
    patient_id: uuid.UUID

    @field_validator("document_context")
    @classmethod
    def require_exact_url(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("document_context must not contain boundary whitespace")
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("document_context must be an absolute HTTP(S) URL")
        return value

    @field_validator("text_delta")
    @classmethod
    def require_text_delta(cls, value: str) -> str:
        return _require_meaningful(value)


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
                except Exception as json_err:
                    print(f"[mbs-rules] skipped malformed JSON result: {type(json_err).__name__}")
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


CLINICAL_FINALIZATION_POLICY_ID = "emr4.clinical-finalization.gp-linked-practitioner.v1"
CLINICAL_FINALIZATION_NORMALIZATION_POLICY_ID = "emr4.clinical-finalization.saved-projection.v1"
# Synthetic-only schema-free proof: audit retention/immutability is not DB-enforced,
# so this is not production durable-idempotency acceptance.
CLINICAL_FINALIZATION_IDEMPOTENCY_NAME = "emr4.clinical-finalization.receipt.v1"
CLINICAL_FINALIZATION_IDEMPOTENCY_NAMESPACE = uuid.UUID(
    "7b56fb23-fdc5-5bd9-951f-80a7b9b94b2e"
)
_FINALIZATION_CONFLICT_CONTENT = {
    "_saved": False,
    "_save_error": "Finalization command conflict.",
}
_FINALIZATION_SAVE_FAILURE_CONTENT = {
    "_saved": False,
    "_save_error": "Encounter save failed. Please contact support.",
}


def _clinical_finalization_event_id(
    practice_id: uuid.UUID,
    document_id: uuid.UUID,
) -> uuid.UUID:
    canonical_name = (
        f"{CLINICAL_FINALIZATION_IDEMPOTENCY_NAME}:"
        f"{str(practice_id)}:{str(document_id)}"
    )
    return uuid.uuid5(CLINICAL_FINALIZATION_IDEMPOTENCY_NAMESPACE, canonical_name)


def _effective_finalization_projection(
    payload: FinalizePayload,
    *,
    patient_id: uuid.UUID,
) -> dict[str, object]:
    overrides = payload.clinician_overrides.model_dump(mode="json")
    consultation_type = overrides["consultation_type"]
    return {
        "consultation_type": (
            consultation_type
            if consultation_type not in {None, ""}
            else "Standard Consultation"
        ),
        # Technical debt: this command UUID occupies legacy google_doc_id storage.
        "document_id": str(payload.document_id),
        "document_context": payload.document_context,
        "normalization_policy_id": CLINICAL_FINALIZATION_NORMALIZATION_POLICY_ID,
        "overrides": {
            "diagnoses": overrides["diagnoses"],
            "mbs_items": overrides["mbs_items"],
            "medications": overrides["medications"],
        },
        "patient_id": str(patient_id),
        "text": payload.text_delta,
    }


def _reviewed_content_sha256(projection: dict[str, object]) -> str:
    """Hash the exact canonical clinical command projection."""
    canonical = json.dumps(
        projection,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _finalization_response(
    encounter_id: uuid.UUID,
    projection: dict[str, object],
) -> dict[str, object]:
    overrides = projection["overrides"]
    lines = [f"Consultation: {projection['consultation_type']}"]
    diagnoses = [item["term"] for item in overrides["diagnoses"]]
    if diagnoses:
        lines.append("Diagnoses: " + ", ".join(diagnoses))
    mbs_items = [f"MBS {item['item_number']}" for item in overrides["mbs_items"]]
    if mbs_items:
        lines.append("Billed: " + ", ".join(mbs_items))
    medications = [
        f"{item['drug_name']} {item['dosage_text']}".strip()
        for item in overrides["medications"]
    ]
    if medications:
        lines.append("Prescribed: " + "; ".join(medications))
    return {
        "_saved": True,
        "encounter_id": str(encounter_id),
        "generated_clinical_note": "\n".join(lines),
    }


def _save_encounter(
    db: Session,
    patient: Patient,
    practitioner_id: uuid.UUID,
    encounter_id: uuid.UUID,
    document_id: str,
    text: str,
    consult_type: str,
    mbs_items: list[dict[str, str]],
    diagnoses: list[dict[str, str]],
    medications: list[dict[str, str]],
) -> uuid.UUID:
    encounter = Encounter(
        id=encounter_id,
        practice_id=patient.practice_id,
        patient_id=patient.id,
        practitioner_id=practitioner_id,
        # Technical debt: command UUID, not a Word document identity.
        google_doc_id=document_id,
        consultation_type=consult_type,
        raw_document_text=text,
        is_finalized=True,
        status=EncounterStatus.Finalized,
    )
    db.add(encounter)
    db.flush()

    for item in mbs_items:
        db.add(MbsClaim(
            practice_id=patient.practice_id,
            patient_id=patient.id,
            practitioner_id=practitioner_id,
            encounter_id=encounter_id,
            item_number=item["item_number"],
            description=item["description"],
            # Existing synthetic DB semantics only; no provider dispatch occurs.
            claim_status=ClaimStatus.Submitted,
            submitted_at=datetime.now(timezone.utc),
        ))

    for diagnosis in diagnoses:
        db.add(ClinicalDiagnosis(
            practice_id=patient.practice_id,
            patient_id=patient.id,
            encounter_id=encounter_id,
            term=diagnosis["term"],
            snomed_ct_au_code=diagnosis["snomed_ct_au_code"],
        ))

    for medication in medications:
        db.add(Prescription(
            practice_id=patient.practice_id,
            patient_id=patient.id,
            encounter_id=encounter_id,
            prescribed_by=practitioner_id,
            drug_name=medication["drug_name"],
            dosage_text=medication["dosage_text"],
            is_active=True,
        ))

    db.flush()
    return encounter_id


def _validated_replay_target(
    db: Session,
    receipt: AccessAiAuditLog,
    *,
    event_id: uuid.UUID,
    actor_user_id: uuid.UUID,
    practice_id: uuid.UUID,
    practitioner_id: uuid.UUID,
    patient_id: uuid.UUID,
    projection: dict[str, object],
    reviewed_hash: str,
) -> Encounter | None:
    expected_metadata = {
        "attested": True,
        "normalization_policy_id": CLINICAL_FINALIZATION_NORMALIZATION_POLICY_ID,
        "patient_id": str(patient_id),
        "practitioner_id": str(practitioner_id),
        "reviewed_content_sha256": reviewed_hash,
        "server_policy_id": CLINICAL_FINALIZATION_POLICY_ID,
    }
    stored_metadata = receipt.metadata_json
    stored_hash = (
        stored_metadata.get("reviewed_content_sha256")
        if isinstance(stored_metadata, dict)
        else None
    )
    if (
        receipt.event_id != event_id
        or receipt.practice_id != practice_id
        or receipt.actor_user_id != actor_user_id
        or receipt.actor_roles != [UserRole.GP.value]
        or receipt.event_type != AiAuditEventType.CLINICAL_CONSULTATION_ATTESTED.value
        or receipt.decision != AiAuditDecision.RECORDED.value
        or receipt.source_surface != AiAuditSourceSurface.API.value
        or receipt.capability is not None
        or receipt.method is not None
        or receipt.reason_code is not None
        or receipt.target_resource_type != "encounter"
        or not isinstance(receipt.correlation_id, uuid.UUID)
        or not isinstance(receipt.event_timestamp, datetime)
        or receipt.event_timestamp.tzinfo is None
        or receipt.event_timestamp.utcoffset() is None
        or not isinstance(stored_hash, str)
        or re.fullmatch(r"[0-9a-f]{64}", stored_hash) is None
        or not isinstance(stored_metadata, dict)
        or stored_metadata.get("attested") is not True
        or not _same_exact_value(stored_metadata, expected_metadata)
    ):
        return None
    try:
        target_id = uuid.UUID(receipt.target_resource_id)
    except (AttributeError, TypeError, ValueError):
        return None
    if str(target_id) != receipt.target_resource_id:
        return None

    encounter = (
        db.query(Encounter)
        .filter(
            Encounter.id == target_id,
            Encounter.practice_id == practice_id,
            Encounter.patient_id == patient_id,
            Encounter.practitioner_id == practitioner_id,
        )
        .with_for_update()
        .first()
    )
    if (
        encounter is None
        or encounter.status != EncounterStatus.Finalized
        or encounter.is_finalized is not True
        or encounter.google_doc_id != projection["document_id"]
        or encounter.consultation_type != projection["consultation_type"]
        or encounter.raw_document_text != projection["text"]
    ):
        return None
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
async def analyze_consultation(
    payload: ConsultationPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(payload.text_delta.strip()) < 10:
        return {"encounter_metadata": {}, "clinical_diagnoses": [], "medications_and_prescriptions": []}

    mbs_context = _search_mbs_rules(payload.text_delta, db)
    prompt = ANALYSIS_PROMPT.format(mbs_context=mbs_context, text=payload.text_delta)

    extracted = {"encounter_metadata": {}, "clinical_diagnoses": [], "medications_and_prescriptions": []}
    try:
        ai_result = await _ai_service.analyze_consultation_text(
            prompt,
            actor_context_from_user(
                current_user,
                environment=settings.environment.lower(),
            ),
        )
        if ai_result.audit_events:
            persist_access_ai_audit_events(db, ai_result.audit_events)
            db.commit()
        extracted = ai_result.raw
        mbs  = [m.get("item_number") for m in extracted.get("encounter_metadata", {}).get("mbs_item_candidates", [])]
        dx   = extracted.get("clinical_diagnoses", [])
        rx   = extracted.get("medications_and_prescriptions", [])
        print(f"[analyze] type={extracted.get('encounter_metadata',{}).get('consultation_type','?')} | MBS={mbs} | dx_count={len(dx)} | rx_count={len(rx)}")
    except Exception as e:
        print(f"Vertex AI error: {e}")
        extracted["encounter_metadata"]["consultation_type"] = "AI Processing Error"

    # Analysis results cannot claim that a clinical record was persisted.
    extracted.pop("_saved", None)
    extracted.pop("_save_error", None)
    return extracted


@router.post("/scribe-consultation")
async def scribe_consultation(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    audio_bytes = await audio_file.read()

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
    "generated_clinical_note": "Full SOAP note as a SINGLE PLAIN-TEXT STRING (use \\n line breaks and S:/O:/A:/P: labels). Do NOT return a nested object.",
    "encounter_metadata": {
        "consultation_type": "Brief description e.g. Level B GP consultation",
        "mbs_item_candidates": [{"item_number": "23", "description": "Level B consultation", "justification": "Duration approx 10 min"}]
    },
    "clinical_diagnoses": [{"term": "Diagnosis name", "snomed_ct_au_code": "XXXXXXX"}],
    "medications_and_prescriptions": [{"drug_name": "DrugName", "dosage_text": "dose and frequency"}]
}
"""
    try:
        ai_result = await _ai_service.scribe_audio(
            audio_bytes,
            audio_file.content_type,
            prompt,
            actor_context_from_user(
                current_user,
                environment=settings.environment.lower(),
            ),
        )
        if ai_result.audit_events:
            persist_access_ai_audit_events(db, ai_result.audit_events)
            db.commit()
        result = ai_result.raw
        mbs  = [m.get("item_number") for m in result.get("encounter_metadata", {}).get("mbs_item_candidates", [])]
        dx   = result.get("clinical_diagnoses", [])
        rx   = result.get("medications_and_prescriptions", [])
        print(f"[scribe] type={result.get('encounter_metadata',{}).get('consultation_type','?')} | MBS={mbs} | dx_count={len(dx)} | rx_count={len(rx)}")
        result.pop("audio_url", None)
        return result
    except Exception as e:
        print(f"[scribe] Gemini error: {type(e).__name__}")
        return JSONResponse(status_code=502, content={"error": "Transcription failed. Please try again."})


@router.post("/finalize")
async def finalize_consultation(
    payload: FinalizePayload,
    command_session_factory: Callable[[], Session] = Depends(get_command_session_factory),
    current_user: User = Depends(get_current_user),
):
    if payload.clinician_attested is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinical finalization is not permitted.",
        )

    actor_user_id = current_user.id
    practice_id = current_user.practice_id
    event_id = _clinical_finalization_event_id(practice_id, payload.document_id)
    try:
        with command_session_factory() as command_db:
            with command_db.begin():
                command_db.execute(
                    text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
                    {"practice_id": str(practice_id)},
                )
                authority_user = (
                    command_db.query(User)
                    .filter(User.id == actor_user_id, User.practice_id == practice_id)
                    .with_for_update()
                    .first()
                )
                if (
                    authority_user is None
                    or not authority_user.is_active
                    or authority_user.role != UserRole.GP
                ):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Clinical finalization is not permitted.",
                    )

                practitioner = (
                    command_db.query(Practitioner)
                    .filter(
                        Practitioner.id == authority_user.practitioner_id,
                        Practitioner.practice_id == practice_id,
                    )
                    .with_for_update()
                    .first()
                )
                if practitioner is None or not practitioner.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Clinical finalization is not permitted.",
                    )

                patient = (
                    command_db.query(Patient)
                    .filter(
                        Patient.id == payload.patient_id,
                        Patient.practice_id == practice_id,
                    )
                    .with_for_update()
                    .first()
                )
                if patient is None:
                    return JSONResponse(
                        status_code=404,
                        content={"_saved": False, "_save_error": "Patient not found."},
                    )

                # Exact string equality only. This does not prove Office identity.
                if (
                    patient.document_url is None
                    or payload.document_context != patient.document_url
                ):
                    return JSONResponse(
                        status_code=status.HTTP_409_CONFLICT,
                        content=_FINALIZATION_CONFLICT_CONTENT,
                    )

                projection = _effective_finalization_projection(
                    payload,
                    patient_id=patient.id,
                )
                reviewed_hash = _reviewed_content_sha256(projection)
                receipt = (
                    command_db.query(AccessAiAuditLog)
                    .filter(
                        AccessAiAuditLog.event_id == event_id,
                        AccessAiAuditLog.practice_id == practice_id,
                        AccessAiAuditLog.event_type
                        == AiAuditEventType.CLINICAL_CONSULTATION_ATTESTED.value,
                    )
                    .with_for_update()
                    .first()
                )
                if receipt is not None:
                    replay_target = _validated_replay_target(
                        command_db,
                        receipt,
                        event_id=event_id,
                        actor_user_id=authority_user.id,
                        practice_id=practice_id,
                        practitioner_id=practitioner.id,
                        patient_id=patient.id,
                        projection=projection,
                        reviewed_hash=reviewed_hash,
                    )
                    if replay_target is None:
                        return JSONResponse(
                            status_code=status.HTTP_409_CONFLICT,
                            content=_FINALIZATION_CONFLICT_CONTENT,
                        )
                    return JSONResponse(
                        content=_finalization_response(replay_target.id, projection)
                    )

                encounter_id = uuid.uuid4()
                audit_event = build_access_ai_audit_event(
                    event_id=event_id,
                    event_type=AiAuditEventType.CLINICAL_CONSULTATION_ATTESTED,
                    source_surface=AiAuditSourceSurface.API,
                    decision=AiAuditDecision.RECORDED,
                    actor_user_id=authority_user.id,
                    actor_roles=(authority_user.role.value,),
                    practice_id=practice_id,
                    target_resource_type="encounter",
                    target_resource_id=encounter_id,
                    metadata={
                        "practitioner_id": str(practitioner.id),
                        "patient_id": str(patient.id),
                        "server_policy_id": CLINICAL_FINALIZATION_POLICY_ID,
                        "normalization_policy_id": (
                            CLINICAL_FINALIZATION_NORMALIZATION_POLICY_ID
                        ),
                        "attested": True,
                        "reviewed_content_sha256": reviewed_hash,
                    },
                )
                # Receipt is flushed before any clinical row is staged.
                persist_access_ai_audit_events(command_db, (audit_event,))

                overrides = projection["overrides"]
                _save_encounter(
                    command_db,
                    patient,
                    practitioner.id,
                    encounter_id,
                    projection["document_id"],
                    projection["text"],
                    projection["consultation_type"],
                    overrides["mbs_items"],
                    overrides["diagnoses"],
                    overrides["medications"],
                )
                response_content = _finalization_response(encounter_id, projection)

        return JSONResponse(content=response_content)
    except HTTPException:
        raise
    except IntegrityError:
        # The failed transaction is closed before this bounded collision check.
        try:
            with command_session_factory() as conflict_db:
                with conflict_db.begin():
                    conflict_db.execute(
                        text(
                            "SELECT set_config("
                            "'app.current_practice_id', :practice_id, true)"
                        ),
                        {"practice_id": str(practice_id)},
                    )
                    same_scope_receipt_exists = (
                        conflict_db.query(AccessAiAuditLog)
                        .filter(
                            AccessAiAuditLog.event_id == event_id,
                            AccessAiAuditLog.practice_id == practice_id,
                        )
                        .first()
                        is not None
                    )
            if same_scope_receipt_exists:
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content=_FINALIZATION_CONFLICT_CONTENT,
                )
        except Exception as check_error:
            print(f"[finalize] collision check: {type(check_error).__name__}")
        return JSONResponse(content=_FINALIZATION_SAVE_FAILURE_CONTENT)
    except Exception as error:
        print(f"[finalize] exception: {type(error).__name__}")
        return JSONResponse(content=_FINALIZATION_SAVE_FAILURE_CONTENT)
