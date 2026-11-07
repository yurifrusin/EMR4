from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.tenancy import Practice, User
from app.schemas.practice import PracticeContextOut, PractitionerOut
from app.services.practice.practitioner_directory_read import (
    list_practitioner_directory,
)

router = APIRouter(prefix="/api/v1/practice", tags=["practice"])


@router.get("/practitioners", response_model=list[PractitionerOut])
def get_practitioners(
    active_only: bool = Query(True, alias="activeOnly"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_practitioner_directory(
        db=db,
        current_user=current_user,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )

@router.get("/context", response_model=PracticeContextOut)
def get_practice_context(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    response.headers["Cache-Control"] = "no-store"
    if request.url.query:
        raise HTTPException(status_code=400, detail="Practice context unavailable", headers={"Cache-Control": "no-store"})
    row = db.query(Practice.id, Practice.timezone).filter(
        Practice.id == current_user.practice_id
    ).one_or_none()
    if row is None or type(row.timezone) is not str or not row.timezone or row.timezone != row.timezone.strip():
        raise HTTPException(status_code=503, detail="Practice context unavailable", headers={"Cache-Control": "no-store"})
    try:
        ZoneInfo(row.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=503, detail="Practice context unavailable", headers={"Cache-Control": "no-store"}) from None
    return PracticeContextOut(practice_id=row.id, timezone=row.timezone)

# STOPPED source candidate. The trusted tenant service factory and existing
# installation/session/CSRF host join are separate admission dependencies.
from uuid import UUID

from app.dependencies import oauth2_scheme
from app.schemas.practitioner_create_command import (
    ConfirmPractitionerCreate, PreparePractitionerCreate,
    PractitionerCreateReceipt, PractitionerCreateRecovery,
    PreparePractitionerCreateResult,
)
from app.services.practice.practitioner_create_command import (
    PractitionerCreateError, PractitionerCreateService,
)


def _practitioner_create_service(request: Request):
    service = getattr(request.app.state, "practitioner_create_service", None)
    if type(service) is not PractitionerCreateService:
        raise HTTPException(status_code=503, detail="PRACTITIONER_CREATE_UNAVAILABLE",
                            headers={"Cache-Control": "no-store"})
    return service


def _create_request(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    if request.url.query:
        raise HTTPException(status_code=400, detail="PRACTITIONER_CREATE_INVALID",
                            headers={"Cache-Control": "no-store"})


def _create_error(error: PractitionerCreateError):
    return HTTPException(status_code=error.status_code, detail=error.code,
                         headers={"Cache-Control": "no-store"})


@router.post("/practitioners/create/proposals", response_model=PreparePractitionerCreateResult,
             operation_id="preparePractitionerCreate")
def prepare_practitioner_create(
    body: PreparePractitionerCreate,
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
    service: PractitionerCreateService = Depends(_practitioner_create_service),
):
    _create_request(request, response)
    try:
        return service.prepare(token, body)
    except PractitionerCreateError as error:
        raise _create_error(error) from None


@router.post("/practitioners/create/confirm", response_model=PractitionerCreateReceipt,
             operation_id="confirmPractitionerCreate")
def confirm_practitioner_create(
    body: ConfirmPractitionerCreate,
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
    service: PractitionerCreateService = Depends(_practitioner_create_service),
):
    _create_request(request, response)
    try:
        return service.confirm(token, body)
    except PractitionerCreateError as error:
        raise _create_error(error) from None


@router.get("/practitioners/create/receipts/{command_key}", response_model=PractitionerCreateRecovery,
            operation_id="readPractitionerCreateReceipt")
def read_practitioner_create_receipt(
    command_key: UUID,
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
    service: PractitionerCreateService = Depends(_practitioner_create_service),
):
    _create_request(request, response)
    try:
        return service.receipt(token, command_key)
    except PractitionerCreateError as error:
        raise _create_error(error) from None

# STOPPED location-only source extension; no service factory is installed here.
from app.schemas.practice_location_command import (
    ConfirmPracticeLocationCreate, PreparePracticeLocationCreate,
    PracticeLocationCreateReceipt, PracticeLocationCreateRecovery,
    PreparePracticeLocationCreateResult,
)
from app.services.practice.practice_location_command import (
    PracticeLocationCreateError, PracticeLocationCreateService,
)


def _practice_location_create_service(request: Request):
    service = getattr(request.app.state, "practice_location_create_service", None)
    if type(service) is not PracticeLocationCreateService:
        raise HTTPException(status_code=503, detail="PRACTICE_LOCATION_CREATE_UNAVAILABLE",
                            headers={"Cache-Control": "no-store"})
    return service


def _location_create_request(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    if request.url.query:
        raise HTTPException(status_code=400, detail="PRACTICE_LOCATION_CREATE_INVALID",
                            headers={"Cache-Control": "no-store"})


def _location_create_error(error: PracticeLocationCreateError):
    return HTTPException(status_code=error.status_code, detail=error.code,
                         headers={"Cache-Control": "no-store"})


@router.post("/locations/create/proposals", response_model=PreparePracticeLocationCreateResult,
             operation_id="preparePracticeLocationCreate")
def prepare_practice_location_create(
    body: PreparePracticeLocationCreate,
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
    service: PracticeLocationCreateService = Depends(_practice_location_create_service),
):
    _location_create_request(request, response)
    try:
        return service.prepare(token, body)
    except PracticeLocationCreateError as error:
        raise _location_create_error(error) from None


@router.post("/locations/create/confirm", response_model=PracticeLocationCreateReceipt,
             operation_id="confirmPracticeLocationCreate")
def confirm_practice_location_create(
    body: ConfirmPracticeLocationCreate,
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
    service: PracticeLocationCreateService = Depends(_practice_location_create_service),
):
    _location_create_request(request, response)
    try:
        return service.confirm(token, body)
    except PracticeLocationCreateError as error:
        raise _location_create_error(error) from None


@router.get("/locations/create/receipts/{command_key}", response_model=PracticeLocationCreateRecovery,
            operation_id="readPracticeLocationCreateReceipt")
def read_practice_location_create_receipt(
    command_key: UUID,
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
    service: PracticeLocationCreateService = Depends(_practice_location_create_service),
):
    _location_create_request(request, response)
    try:
        return service.receipt(token, command_key)
    except PracticeLocationCreateError as error:
        raise _location_create_error(error) from None
