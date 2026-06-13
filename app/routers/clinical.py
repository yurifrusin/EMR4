import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.tenancy import User
from app.models.patients import Patient
from app.models.clinical import (
    Allergy, PatientHistory, Encounter, Prescription, ClinicalDiagnosis,
    ConsentForm,
)
from app.models.care_plans import CarePlan
from app.schemas.clinical import (
    AllergyCreate, AllergyOut,
    HistoryCreate, HistoryOut,
    EncounterOut,
    CarePlanCreate, CarePlanOut,
    ConsentFormCreate, ConsentFormOut,
)

router = APIRouter(prefix="/api/v1/patients/{patient_id}", tags=["clinical"])


def _get_patient_or_404(patient_id: uuid.UUID, practice_id: uuid.UUID, db: Session) -> Patient:
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.practice_id == practice_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# --- Allergies ---

@router.get("/allergies", response_model=list[AllergyOut])
def list_allergies(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    return db.query(Allergy).filter(Allergy.patient_id == patient_id).all()


@router.post("/allergies", response_model=AllergyOut, status_code=status.HTTP_201_CREATED)
def add_allergy(
    patient_id: uuid.UUID,
    body: AllergyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    allergy = Allergy(
        practice_id=current_user.practice_id,
        patient_id=patient_id,
        **body.model_dump(),
    )
    db.add(allergy)
    db.commit()
    db.refresh(allergy)
    return allergy


@router.delete("/allergies/{allergy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_allergy(
    patient_id: uuid.UUID,
    allergy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    allergy = db.query(Allergy).filter(
        Allergy.id == allergy_id,
        Allergy.patient_id == patient_id,
    ).first()
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")
    db.delete(allergy)
    db.commit()


# --- Patient History ---

@router.get("/history", response_model=list[HistoryOut])
def list_history(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    return db.query(PatientHistory).filter(PatientHistory.patient_id == patient_id).all()


@router.post("/history", response_model=HistoryOut, status_code=status.HTTP_201_CREATED)
def add_history(
    patient_id: uuid.UUID,
    body: HistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    item = PatientHistory(
        practice_id=current_user.practice_id,
        patient_id=patient_id,
        **body.model_dump(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# --- Encounters ---

@router.get("/encounters", response_model=list[EncounterOut])
def list_encounters(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    return (
        db.query(Encounter)
        .filter(Encounter.patient_id == patient_id)
        .order_by(Encounter.consultation_date.desc())
        .limit(50)
        .all()
    )


@router.get("/encounters/{encounter_id}", response_model=EncounterOut)
def get_encounter(
    patient_id: uuid.UUID,
    encounter_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enc = db.query(Encounter).filter(
        Encounter.id == encounter_id,
        Encounter.patient_id == patient_id,
        Encounter.practice_id == current_user.practice_id,
    ).first()
    if not enc:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return enc


# --- Medications ---

@router.get("/medications", response_model=list)
def list_medications(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    meds = db.query(Prescription).filter(
        Prescription.patient_id == patient_id,
        Prescription.is_active == True,
    ).all()
    return [
        {
            "id": str(m.id),
            "drug_name": m.drug_name,
            "dosage_text": m.dosage_text,
            "frequency": m.frequency,
            "route": m.route,
            "start_date": str(m.start_date) if m.start_date else None,
        }
        for m in meds
    ]


# --- Care Plans ---

@router.get("/care-plans", response_model=list[CarePlanOut])
def list_care_plans(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    return db.query(CarePlan).filter(CarePlan.patient_id == patient_id).all()


@router.post("/care-plans", response_model=CarePlanOut, status_code=status.HTTP_201_CREATED)
def create_care_plan(
    patient_id: uuid.UUID,
    body: CarePlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    plan = CarePlan(
        practice_id=current_user.practice_id,
        patient_id=patient_id,
        **body.model_dump(),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


# --- Consent Forms ---

@router.post("/consent", response_model=ConsentFormOut, status_code=status.HTTP_201_CREATED)
def create_consent_form(
    patient_id: uuid.UUID,
    body: ConsentFormCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime, timezone
    _get_patient_or_404(patient_id, current_user.practice_id, db)
    form = ConsentForm(
        practice_id=current_user.practice_id,
        patient_id=patient_id,
        signed_at=datetime.now(timezone.utc),
        **body.model_dump(),
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    return form
