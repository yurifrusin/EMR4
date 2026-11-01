"""Five minimal patient endpoints; mounted only by the explicit inert factory.

The dependency User is defense in depth, not the principal/expiry authority.
Each service call re-verifies the bearer and uses fresh locked SQL authority.
No request can supply actor, tenant, generation, expiry or a signing secret.
"""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from app.dependencies import get_current_user, oauth2_scheme
from app.schemas.patient_registration import (
    ConfirmRegistration, PatientDemographics, PrepareRegistration,
    PrepareRegistrationResult, RegistrationReceipt,
)
from app.services.patient_registration import PatientRegistrationError, PatientRegistrationService

router = APIRouter(prefix="/api/v1/patients", tags=["local synthetic patients"])


def _service(request: Request) -> PatientRegistrationService:
    service = getattr(request.app.state, "patient_registration_service", None)
    if type(service) is not PatientRegistrationService:
        raise HTTPException(503, detail="PATIENT_REGISTRATION_UNAVAILABLE")
    return service


def _invoke(response, operation):
    response.headers["Cache-Control"] = "no-store"
    try:
        return operation()
    except PatientRegistrationError as exc:
        headers = {"Cache-Control": "no-store"}
        if exc.status_code == 401:
            headers["WWW-Authenticate"] = "Bearer"
        raise HTTPException(exc.status_code, detail=exc.code, headers=headers) from None


# Static paths precede UUID paths. No legacy clinical/full-patient router mount.
@router.get("/search", response_model=list[PatientDemographics])
def search_patients(response: Response, q: str | None = Query(default=None, min_length=2, max_length=100),
                    date_of_birth: date | None = None, limit: int = Query(default=10, ge=1, le=20),
                    token: str = Depends(oauth2_scheme), _user=Depends(get_current_user),
                    service: PatientRegistrationService = Depends(_service)):
    return _invoke(response, lambda: service.search(token, q, date_of_birth, limit))


@router.post("/registrations/prepare", response_model=PrepareRegistrationResult)
def prepare_registration(body: PrepareRegistration, response: Response,
                         token: str = Depends(oauth2_scheme), _user=Depends(get_current_user),
                         service: PatientRegistrationService = Depends(_service)):
    return _invoke(response, lambda: service.prepare(token, body))


@router.post("/registrations/confirm", response_model=RegistrationReceipt)
def confirm_registration(body: ConfirmRegistration, response: Response,
                         token: str = Depends(oauth2_scheme), _user=Depends(get_current_user),
                         service: PatientRegistrationService = Depends(_service)):
    return _invoke(response, lambda: service.confirm(token, body))


@router.get("/registrations/{command_key}", response_model=RegistrationReceipt)
def registration_receipt(command_key: UUID, response: Response,
                         token: str = Depends(oauth2_scheme), _user=Depends(get_current_user),
                         service: PatientRegistrationService = Depends(_service)):
    return _invoke(response, lambda: service.receipt(token, command_key))


@router.get("/{patient_id}", response_model=PatientDemographics)
def read_patient(patient_id: UUID, response: Response,
                 token: str = Depends(oauth2_scheme), _user=Depends(get_current_user),
                 service: PatientRegistrationService = Depends(_service)):
    return _invoke(response, lambda: service.read(token, patient_id))
