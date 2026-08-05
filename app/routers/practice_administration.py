"""B4.1 Davida default-location command REST router.

Mounts exactly three default-off, provider-free, authored-synthetic-practice-only
routes under ``/api/v1/practice-administration``. Every route requires bounded
``Idempotency-Key`` and ``X-Correlation-Id`` headers, reauthorizes from the
authenticated application session and returns closed-vocabulary rejections.
"""

from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, Header, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.tenancy import User
from app.schemas.practice_administration_default_location_command import (
    HEADER_VALUE_PATTERN,
    ConfirmationEvidenceEnvelope,
    DefaultLocationConfirmationCommand,
    DefaultLocationConfirmationResult,
    DefaultLocationEvidenceRequest,
    DefaultLocationProposalEnvelope,
    DefaultLocationProposalRequest,
    REJECTION_SCHEMA_VERSION,
    Rejection,
)
from app.services.practice.practice_administration_default_location_command import (
    B4CommandError,
    confirm_default_location_change,
    generate_default_location_proposal,
    issue_confirmation_evidence,
)

router = APIRouter(
    prefix="/api/v1/practice-administration",
    tags=["practice-administration"],
)

_HEADER_RE = re.compile(HEADER_VALUE_PATTERN)

PROPOSAL_PATH = (
    "/practitioners/default-location/proposals"
)
EVIDENCE_PATH = (
    "/practitioners/default-location/proposals/{proposal_id}/confirmation-evidence"
)
CONFIRM_PATH = "/practitioners/default-location/proposals/{proposal_id}/confirm"

_REJECTION_RESPONSES = {
    401: {"model": Rejection, "description": "Application session missing or invalid."},
    403: {"model": Rejection, "description": "Uniform anti-enumerating authorization rejection."},
    409: {"model": Rejection, "description": "State, evidence or idempotency conflict."},
    410: {"model": Rejection, "description": "Proposal or confirmation evidence expired."},
    422: {"model": Rejection, "description": "Canonical closed-envelope admission failed."},
    500: {"model": Rejection, "description": "Atomic transaction failed; all members rolled back."},
}


def _validated_headers(
    idempotency_key: Optional[str],
    correlation_id: Optional[str],
) -> tuple[str, str]:
    if not idempotency_key or not _HEADER_RE.fullmatch(idempotency_key):
        raise B4CommandError("invalid_envelope", status_code=422)
    if not correlation_id or not _HEADER_RE.fullmatch(correlation_id):
        raise B4CommandError("invalid_envelope", status_code=422)
    return idempotency_key, correlation_id


def _rejection(exc: B4CommandError, correlation_id: str) -> JSONResponse:
    payload = Rejection(
        schema_version=REJECTION_SCHEMA_VERSION,
        status="rejected",
        reason_code=exc.reason_code,  # type: ignore[arg-type]
        correlation_id=correlation_id,
        retryable=exc.retryable,
    ).model_dump(mode="json")
    return JSONResponse(status_code=exc.status_code, content=payload)


def _safe_correlation(value: Optional[str]) -> str:
    if value and _HEADER_RE.fullmatch(value):
        return value
    return "correlation-rejected"


@router.post(
    PROPOSAL_PATH,
    response_model=DefaultLocationProposalEnvelope,
    responses=_REJECTION_RESPONSES,
    operation_id="proposePractitionerDefaultLocationChange",
    summary="Recompute one non-mutating default-location proposal.",
)
def propose_default_location_change(
    body: DefaultLocationProposalRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        _idem_key, corr_id = _validated_headers(idempotency_key, correlation_id)
        return generate_default_location_proposal(
            db=db,
            current_user=current_user,
            request=body,
            correlation_id=corr_id,
        )
    except B4CommandError as exc:
        db.rollback()
        return _rejection(exc, _safe_correlation(correlation_id))
    except Exception:
        db.rollback()
        return _rejection(
            B4CommandError("atomic_transaction_failed", status_code=500),
            _safe_correlation(correlation_id),
        )


@router.post(
    EVIDENCE_PATH,
    response_model=ConfirmationEvidenceEnvelope,
    responses=_REJECTION_RESPONSES,
    operation_id="issuePractitionerDefaultLocationConfirmationEvidence",
    summary="Record one current human attestation and return one server-held ref.",
)
def issue_default_location_confirmation_evidence(
    proposal_id: str,
    body: DefaultLocationEvidenceRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        _idem_key, corr_id = _validated_headers(idempotency_key, correlation_id)
        return issue_confirmation_evidence(
            db=db,
            current_user=current_user,
            proposal_id=proposal_id,
            request=body,
            idempotency_key=_idem_key,
            correlation_id=corr_id,
        )
    except B4CommandError as exc:
        db.rollback()
        return _rejection(exc, _safe_correlation(correlation_id))
    except Exception:
        db.rollback()
        return _rejection(
            B4CommandError("atomic_transaction_failed", status_code=500),
            _safe_correlation(correlation_id),
        )


@router.post(
    CONFIRM_PATH,
    response_model=DefaultLocationConfirmationResult,
    responses=_REJECTION_RESPONSES,
    operation_id="confirmPractitionerDefaultLocationChange",
    summary="Consume evidence and commit the single default-location command.",
)
def confirm_default_location_change_route(
    proposal_id: str,
    body: DefaultLocationConfirmationCommand,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id"),
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        _idem_key, corr_id = _validated_headers(idempotency_key, correlation_id)
        result, replayed = confirm_default_location_change(
            db=db,
            current_user=current_user,
            proposal_id=proposal_id,
            request=body,
            idempotency_key=_idem_key,
            correlation_id=corr_id,
        )
    except B4CommandError as exc:
        db.rollback()
        return _rejection(exc, _safe_correlation(correlation_id))
    except Exception:
        db.rollback()
        return _rejection(
            B4CommandError("atomic_transaction_failed", status_code=500),
            _safe_correlation(correlation_id),
        )
    if replayed and response is not None:
        response.headers["Idempotent-Replayed"] = "true"
    return result
