import sys
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.config import settings
from app.dependencies import get_db, get_current_user
from app.models.tenancy import User
from app.models.patients import Patient
from app.models.clinical import ClinicalDiagnosis, Prescription, Encounter, Allergy
from app.schemas.patients import (
    PatientCreate, PatientUpdate, PatientOut, PatientWithFileOut,
    PatientSummary, AllergyOut, EncounterSummary, MedicationSummary, DiagnosisSummary,
)

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(
    body: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = Patient(practice_id=current_user.practice_id, **body.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.post("/with-file", response_model=PatientWithFileOut, status_code=status.HTTP_201_CREATED)
def create_patient_with_file(
    body: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a patient DB record AND generate their .docx file atomically.
    The file is written to settings.patient_files_dir (configured via PATIENT_FILES_DIR
    in .env; point it at a OneDrive-synced folder for Word Online access).
    document_url is left null here and backfilled by the taskpane autoDetectPatient()
    the first time the file is opened in Word Online.
    """
    # Lazy-import to avoid adding the repo root to the module search path globally;
    # uvicorn is launched from the repo root so the import resolves correctly.
    if "" not in sys.path:
        sys.path.insert(0, "")
    from create_patient_file import create_patient_docx, PatientData  # noqa: E402

    doc_path = None
    try:
        # 1. Create the DB row without committing yet. If file generation fails,
        #    rollback removes the patient row as well.
        patient = Patient(practice_id=current_user.practice_id, **body.model_dump())
        db.add(patient)
        db.flush()

        # 2. Build the PatientData — map the richer PatientCreate fields to the
        #    simpler PatientData dataclass that the generator expects.
        address_parts = filter(None, [
            patient.address_line1,
            patient.address_suburb,
            patient.address_state,
            patient.address_postcode,
        ])
        address_str = " ".join(address_parts)
        phone_str = patient.phone_mobile or patient.phone_home or ""

        pd = PatientData(
            first_name=patient.first_name,
            last_name=patient.last_name,
            date_of_birth=patient.date_of_birth,
            sex=patient.sex or "Other",
            address=address_str,
            phone=phone_str,
            medicare_number=patient.medicare_number or "",
        )

        # 3. Generate the .docx, creating the output directory if needed.
        output_dir = Path(settings.patient_files_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        doc_path = create_patient_docx(pd, output_dir=output_dir)

        db.commit()
        db.refresh(patient)
        base = PatientOut.model_validate(patient)
        return PatientWithFileOut(**base.model_dump(), generated_filename=doc_path.name)
    except Exception:
        db.rollback()
        if doc_path and doc_path.exists():
            doc_path.unlink()
        raise


@router.get("/search", response_model=list[PatientOut])
def search_patients(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base = db.query(Patient).filter(Patient.practice_id == current_user.practice_id)
    results = base.filter(
        or_(
            Patient.first_name.ilike(f"%{q}%"),
            Patient.last_name.ilike(f"%{q}%"),
            Patient.medicare_number.ilike(f"%{q}%"),
            Patient.phone_mobile.ilike(f"%{q}%"),
            Patient.phone_home.ilike(f"%{q}%"),
        )
    ).order_by(Patient.last_name, Patient.first_name).limit(limit).all()
    return results


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.practice_id == current_user.practice_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: uuid.UUID,
    body: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.practice_id == current_user.practice_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}/summary", response_model=PatientSummary)
def get_patient_summary(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.practice_id == current_user.practice_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    active_diagnoses = db.query(ClinicalDiagnosis).filter(
        ClinicalDiagnosis.patient_id == patient_id,
        ClinicalDiagnosis.is_active == True,
    ).all()

    active_medications = db.query(Prescription).filter(
        Prescription.patient_id == patient_id,
        Prescription.is_active == True,
    ).all()

    allergies = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()

    recent_encounters = db.query(Encounter).filter(
        Encounter.patient_id == patient_id,
    ).order_by(Encounter.consultation_date.desc()).limit(10).all()

    return PatientSummary(
        patient=PatientOut.model_validate(patient),
        active_diagnoses=[DiagnosisSummary.model_validate(d) for d in active_diagnoses],
        active_medications=[MedicationSummary.model_validate(m) for m in active_medications],
        allergies=[AllergyOut.model_validate(a) for a in allergies],
        recent_encounters=[EncounterSummary.model_validate(e) for e in recent_encounters],
    )
