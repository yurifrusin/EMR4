"""Scoped, default-off synthetic patient request operations.

This is possession of one preseeded demo capability, never patient identity.
Staff booking uses the existing appointment command transaction separately.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import uuid
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models.appointments import Appointment
from app.models.patient_requests import PatientBookingRequest
from app.services.appointment_conflicts import set_appointment_practice_context
from app.services.patient_request_contract import (
    RequestRejected, capability_matches, validate_submission,
)


def _denied():
    raise HTTPException(status_code=404, detail={"code": "REQUEST_UNAVAILABLE"})


def _profile_ids():
    if settings.environment != "dev" or not settings.stage1_patient_request_enabled:
        _denied()
    try:
        practice_id = uuid.UUID(settings.stage1_patient_request_practice_id)
        patient_id = uuid.UUID(settings.stage1_patient_request_patient_id)
    except (ValueError, AttributeError):
        _denied()
    secret = settings.secret_key.encode("utf-8")
    if len(secret) < 32:
        _denied()
    return practice_id, patient_id, secret


def require_patient_request(
    db: Session, request_id: uuid.UUID, bearer: str | None,
    *, write: bool = False, options: bool = False, lock: bool = False,
) -> PatientBookingRequest:
    practice_id, patient_id, secret = _profile_ids()
    set_appointment_practice_context(db, practice_id)
    query = db.query(PatientBookingRequest).filter(
        PatientBookingRequest.id == request_id,
        PatientBookingRequest.practice_id == practice_id,
        PatientBookingRequest.patient_id == patient_id,
    )
    if lock:
        query = query.with_for_update()
    row = query.one_or_none()
    if row is None or bearer is None:
        _denied()
    try:
        valid = capability_matches(bearer, row.capability_digest, secret)
    except RequestRejected:
        _denied()
    if not valid:
        _denied()
    now = datetime.now(timezone.utc)
    if write or options:
        if now >= row.capability_expires_at or row.state in {"cancelled", "expired", "booked"}:
            _denied()
    else:
        if row.state == "booked":
            if (
                row.booked_at is None or row.booked_at > now
                or now > row.booked_at + timedelta(hours=24)
            ):
                _denied()
        elif now >= row.capability_expires_at:
            _denied()
    return row


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def allowed_dates(row: PatientBookingRequest, now: datetime) -> list[str]:
    zone = ZoneInfo(row.practice_timezone)
    tomorrow = now.astimezone(zone).date() + timedelta(days=1)
    return [(tomorrow + timedelta(days=i)).isoformat() for i in range(7)]


def request_options(row: PatientBookingRequest, now: datetime) -> list[dict]:
    """Small candidate times; staff create performs the authoritative check."""
    if row.preference_date is None:
        return [
            {"date": day, "local_time": "14:00", "zone": row.practice_timezone}
            for day in allowed_dates(row, now)
        ]
    days = [row.preference_date.isoformat()]
    clocks = ("14:00", "14:30", "15:00", "15:30", "16:00")
    return [
        {"date": day, "local_time": clock, "zone": row.practice_timezone}
        for day in days for clock in clocks
        if not row.earliest_local or row.earliest_local.strftime("%H:%M") <= clock
        if not row.latest_local or clock < row.latest_local.strftime("%H:%M")
    ][:7]


def submit_request(db: Session, row: PatientBookingRequest, raw: dict, key: str):
    if not key or len(key) > 128:
        raise HTTPException(status_code=400, detail={"code": "REQUEST_KEY_INVALID"})
    _, _, secret = _profile_ids()
    key_hash = hmac.new(secret, b"request-submit-key\x00" + key.encode(), hashlib.sha256).hexdigest()
    material = json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()
    body_hash = hashlib.sha256(material).hexdigest()
    if row.state == "submitted" and row.submission_key_digest == key_hash:
        if row.submission_body_digest != body_hash:
            raise HTTPException(status_code=409, detail={"code": "REQUEST_KEY_CONFLICT"})
        return row.submission_receipt
    context = {
        "request_id": str(row.id), "request_version": row.request_version,
        "state": row.state, "allowed_dates": allowed_dates(row, datetime.now(timezone.utc)),
        "minimum_local": "14:00", "maximum_local": "17:00",
        "expires_at": _utc_text(row.capability_expires_at),
        "as_of": _utc_text(datetime.now(timezone.utc)),
    }
    try:
        submission = validate_submission(raw, context)
    except RequestRejected as exc:
        raise HTTPException(status_code=409, detail={"code": exc.code}) from None
    row.preference_date = datetime.fromisoformat(submission.date).date()
    row.earliest_local = datetime.strptime(submission.earliest_local, "%H:%M").time()
    row.latest_local = datetime.strptime(submission.latest_local, "%H:%M").time()
    row.reason_code = submission.reason_code
    row.state = "submitted"
    row.request_version += 1
    row.submitted_at = datetime.now(timezone.utc)
    row.submission_key_digest = key_hash
    row.submission_body_digest = body_hash
    receipt = {
        "request_id": str(row.id), "state": "submitted",
        "request_version": row.request_version, "message": "Request received for staff review.",
    }
    row.submission_receipt = receipt
    db.commit()
    return receipt


def patient_readback(db: Session, row: PatientBookingRequest) -> dict:
    result = {
        "request_id": row.id, "state": row.state,
        "request_version": row.request_version,
        "preference_date": row.preference_date,
        "earliest_local": row.earliest_local,
        "latest_local": row.latest_local,
        "booked_appointment_id": None, "booked_start_time": None,
        "booked_status": None, "historical_request_result": row.state == "booked",
    }
    if row.state == "booked":
        set_appointment_practice_context(db, row.practice_id)
        appointment = db.query(Appointment).filter(
            Appointment.practice_id == row.practice_id,
            Appointment.id == row.booked_appointment_id,
            Appointment.patient_id == row.patient_id,
        ).one_or_none()
        if appointment is None:
            _denied()
        result.update(
            booked_appointment_id=appointment.id,
            booked_start_time=appointment.start_time,
            booked_status=appointment.status.value,
        )
    return result
