import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.tenancy import User
from app.models.patients import Patient
from app.models.clinical import ClinicalDiagnosis, Prescription, Encounter, Allergy
from app.schemas.patients import (
    PatientCreate, PatientUpdate, PatientOut,
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
