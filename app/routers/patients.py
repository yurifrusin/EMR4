import sys
import uuid
from datetime import date
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session
from app.config import settings
from app.dependencies import get_db, get_current_user
from app.models.tenancy import User
from app.models.patients import Patient
from app.models.clinical import ClinicalDiagnosis, Prescription, Encounter, Allergy
from app.schemas.patients import (
    PatientCreate, PatientUpdate, PatientOut, PatientWithFileOut,
    PatientSummary, AllergyOut, EncounterSummary, MedicationSummary, DiagnosisSummary,
    PatientDuplicateCandidate,
)

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


def _norm_identifier(value: str | None) -> str:
    if not value:
        return ""
    return "".join(ch.lower() for ch in value if ch.isalnum())


def _norm_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.lower().split())


def _normalized_column(column):
    return func.regexp_replace(func.lower(column), "[^a-z0-9]", "", "g")


def _same_identifier(left: str | None, right: str | None) -> bool:
    left_norm = _norm_identifier(left)
    right_norm = _norm_identifier(right)
    return bool(left_norm and right_norm and left_norm == right_norm)


def _raise_if_incomplete_medicare_identity(
    *,
    medicare_number: str | None,
    medicare_irn: str | None,
) -> None:
    has_medicare = bool(_norm_identifier(medicare_number))
    has_irn = bool(_norm_identifier(medicare_irn))
    if has_medicare != has_irn:
        raise HTTPException(
            status_code=422,
            detail="Medicare number and IRN must be entered together.",
        )


def _duplicate_match_reasons(
    patient: Patient,
    *,
    first_name: str | None,
    last_name: str | None,
    date_of_birth: date | None,
    medicare_number: str | None,
    medicare_irn: str | None,
    ihi_number: str | None,
    phone_mobile: str | None,
    phone_home: str | None,
) -> list[str]:
    reasons: list[str] = []

    if _same_identifier(patient.ihi_number, ihi_number):
        reasons.append("same_ihi")

    if _same_identifier(patient.medicare_number, medicare_number):
        if _same_identifier(patient.medicare_irn, medicare_irn):
            reasons.append("same_medicare_card_and_irn")
        else:
            reasons.append("same_medicare_card")

    if (
        date_of_birth
        and patient.date_of_birth == date_of_birth
        and _norm_text(patient.first_name) == _norm_text(first_name)
        and _norm_text(patient.last_name) == _norm_text(last_name)
    ):
        reasons.append("same_name_and_dob")

    requested_phones = {_norm_identifier(phone_mobile), _norm_identifier(phone_home)} - {""}
    patient_phones = {
        _norm_identifier(patient.phone_mobile),
        _norm_identifier(patient.phone_home),
    } - {""}
    if date_of_birth and patient.date_of_birth == date_of_birth and requested_phones & patient_phones:
        reasons.append("same_phone_and_dob")

    return reasons


def _raise_if_hard_duplicate(
    db: Session,
    current_user: User,
    *,
    first_name: str | None,
    last_name: str | None,
    date_of_birth: date | None,
    medicare_number: str | None,
    medicare_irn: str | None,
    ihi_number: str | None,
    phone_mobile: str | None,
    phone_home: str | None,
    exclude_patient_id: uuid.UUID | None = None,
) -> None:
    ihi_norm = _norm_identifier(ihi_number)
    medicare_norm = _norm_identifier(medicare_number)
    medicare_irn_norm = _norm_identifier(medicare_irn)

    conditions = []
    if ihi_norm:
        conditions.append(_normalized_column(Patient.ihi_number) == ihi_norm)
    if medicare_norm and medicare_irn_norm:
        conditions.append(and_(
            _normalized_column(Patient.medicare_number) == medicare_norm,
            _normalized_column(Patient.medicare_irn) == medicare_irn_norm,
        ))

    if not conditions:
        return

    query = db.query(Patient).filter(
        Patient.practice_id == current_user.practice_id,
        or_(*conditions),
    )
    if exclude_patient_id is not None:
        query = query.filter(Patient.id != exclude_patient_id)

    existing = query.order_by(Patient.last_name, Patient.first_name).first()

    if not existing:
        return

    reasons = _duplicate_match_reasons(
        existing,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        medicare_number=medicare_number,
        medicare_irn=medicare_irn,
        ihi_number=ihi_number,
        phone_mobile=phone_mobile,
        phone_home=phone_home,
    )
    hard_reasons = [
        reason
        for reason in reasons
        if reason in {"same_ihi", "same_medicare_card_and_irn"}
    ]
    if hard_reasons:
        name = " ".join(
            part for part in (existing.first_name, existing.last_name) if part
        ) or "another patient"
        if "same_ihi" in hard_reasons:
            message = f"This IHI is already used by {name}. Please check the IHI before saving."
        elif "same_medicare_card_and_irn" in hard_reasons:
            message = (
                f"This Medicare number and IRN are already used by {name}. "
                "Please check the card number and IRN before saving."
            )
        else:
            message = f"These details look like they already belong to {name}. Please check them before saving."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": message,
                "existing_patient_id": str(existing.id),
                "match_reasons": hard_reasons,
            },
        )


def _raise_if_create_hard_duplicate(
    db: Session,
    current_user: User,
    body: PatientCreate,
) -> None:
    _raise_if_incomplete_medicare_identity(
        medicare_number=body.medicare_number,
        medicare_irn=body.medicare_irn,
    )
    _raise_if_hard_duplicate(
        db,
        current_user,
        first_name=body.first_name,
        last_name=body.last_name,
        date_of_birth=body.date_of_birth,
        medicare_number=body.medicare_number,
        medicare_irn=body.medicare_irn,
        ihi_number=body.ihi_number,
        phone_mobile=body.phone_mobile,
        phone_home=body.phone_home,
    )


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(
    body: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _raise_if_create_hard_duplicate(db, current_user, body)
    patient = Patient(practice_id=current_user.practice_id, **body.model_dump())
    db.add(patient)
    db.flush()
    response = PatientOut.model_validate(patient)
    db.commit()
    return response


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

    _raise_if_create_hard_duplicate(db, current_user, body)

    doc_path = None
    try:
        # 1. Create the DB row without committing yet. If file generation fails,
        #    rollback removes the patient row as well.
        patient_data = body.model_dump()
        patient_data["document_url"] = None
        patient = Patient(practice_id=current_user.practice_id, **patient_data)
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

        base = PatientOut.model_validate(patient)
        db.commit()
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
    first_last = func.concat(
        func.coalesce(Patient.first_name, ""),
        " ",
        func.coalesce(Patient.last_name, ""),
    )
    last_first = func.concat(
        func.coalesce(Patient.last_name, ""),
        " ",
        func.coalesce(Patient.first_name, ""),
    )
    results = base.filter(
        or_(
            Patient.first_name.ilike(f"%{q}%"),
            Patient.last_name.ilike(f"%{q}%"),
            first_last.ilike(f"%{q}%"),
            last_first.ilike(f"%{q}%"),
            Patient.medicare_number.ilike(f"%{q}%"),
            Patient.medicare_irn.ilike(f"%{q}%"),
            Patient.ihi_number.ilike(f"%{q}%"),
            Patient.phone_mobile.ilike(f"%{q}%"),
            Patient.phone_home.ilike(f"%{q}%"),
        )
    ).order_by(Patient.last_name, Patient.first_name).limit(limit).all()
    return results


@router.get("/duplicate-candidates", response_model=list[PatientDuplicateCandidate])
def duplicate_candidates(
    first_name: str | None = Query(None),
    last_name: str | None = Query(None),
    date_of_birth: date | None = Query(None),
    medicare_number: str | None = Query(None),
    medicare_irn: str | None = Query(None),
    ihi_number: str | None = Query(None),
    phone_mobile: str | None = Query(None),
    phone_home: str | None = Query(None),
    limit: int = Query(10, le=25),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    has_identifier = bool(_norm_identifier(ihi_number) or _norm_identifier(medicare_number))
    has_name_dob = bool(date_of_birth and _norm_text(first_name) and _norm_text(last_name))
    has_phone_dob = bool(
        date_of_birth and (_norm_identifier(phone_mobile) or _norm_identifier(phone_home))
    )
    if not (has_identifier or has_name_dob or has_phone_dob):
        raise HTTPException(
            status_code=422,
            detail="Provide an IHI, Medicare number, name+DOB, or phone+DOB to check duplicates",
        )

    conditions = []
    ihi_norm = _norm_identifier(ihi_number)
    medicare_norm = _norm_identifier(medicare_number)
    if ihi_norm:
        conditions.append(_normalized_column(Patient.ihi_number) == ihi_norm)
    if medicare_norm:
        conditions.append(_normalized_column(Patient.medicare_number) == medicare_norm)
    if has_name_dob:
        conditions.append(and_(
            Patient.date_of_birth == date_of_birth,
            func.lower(func.trim(Patient.first_name)) == _norm_text(first_name),
            func.lower(func.trim(Patient.last_name)) == _norm_text(last_name),
        ))
    if has_phone_dob:
        phone_conditions = []
        for phone in (phone_mobile, phone_home):
            phone_norm = _norm_identifier(phone)
            if phone_norm:
                phone_conditions.extend([
                    _normalized_column(Patient.phone_mobile) == phone_norm,
                    _normalized_column(Patient.phone_home) == phone_norm,
                ])
        if phone_conditions:
            conditions.append(and_(Patient.date_of_birth == date_of_birth, or_(*phone_conditions)))

    candidates = db.query(Patient).filter(
        Patient.practice_id == current_user.practice_id,
        or_(*conditions),
    ).order_by(Patient.last_name, Patient.first_name).limit(limit).all()

    response = []
    for patient in candidates:
        reasons = _duplicate_match_reasons(
            patient,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            medicare_number=medicare_number,
            medicare_irn=medicare_irn,
            ihi_number=ihi_number,
            phone_mobile=phone_mobile,
            phone_home=phone_home,
        )
        if reasons:
            response.append(PatientDuplicateCandidate(
                patient=PatientOut.model_validate(patient),
                match_reasons=reasons,
            ))
    return response


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

    updates = body.model_dump(exclude_unset=True)
    effective_identity = {
        field: updates[field] if field in updates else getattr(patient, field)
        for field in (
            "first_name", "last_name", "date_of_birth", "medicare_number",
            "medicare_irn", "ihi_number", "phone_mobile", "phone_home",
        )
    }
    _raise_if_incomplete_medicare_identity(
        medicare_number=effective_identity["medicare_number"],
        medicare_irn=effective_identity["medicare_irn"],
    )
    _raise_if_hard_duplicate(
        db,
        current_user,
        **effective_identity,
        exclude_patient_id=patient.id,
    )

    for field, value in updates.items():
        setattr(patient, field, value)
    db.flush()
    response = PatientOut.model_validate(patient)
    db.commit()
    return response


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
