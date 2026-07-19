import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Literal
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

from app.models.appointments import AppointmentCommandIdempotency


DecisionKind = Literal[
    "started",
    "replay",
    "conflict",
    "in_progress",
    "stale_in_progress",
    "failed_transient",
]


@dataclass(frozen=True)
class AppointmentIdempotencyDecision:
    kind: DecisionKind
    record: AppointmentCommandIdempotency
    response_status_code: int | None = None
    response_body_json: dict[str, Any] | None = None
    audit_log_id: UUID | None = None


def _json_default(value: Any) -> str:
    if isinstance(value, (UUID, datetime, date, time)):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    )


def sha256_canonical_json(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def hash_idempotency_key(raw_key: str, secret: bytes) -> str:
    return hmac.new(secret, raw_key.encode("utf-8"), hashlib.sha256).hexdigest()


def _as_aware_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def claim_appointment_command(
    db: Session,
    *,
    practice_id: UUID,
    actor_user_id: str,
    actor_role: str,
    operation_id: str,
    route_family: str,
    raw_idempotency_key: str,
    request_body: dict[str, Any],
    secret: bytes,
    stale_after: timedelta | None = None,
    now: datetime | None = None,
) -> AppointmentIdempotencyDecision:
    idempotency_key_hash = hash_idempotency_key(raw_idempotency_key, secret)
    request_body_hash = sha256_canonical_json(request_body)

    identity_filter = (
        AppointmentCommandIdempotency.practice_id == practice_id,
        AppointmentCommandIdempotency.actor_user_id == actor_user_id,
        AppointmentCommandIdempotency.operation_id == operation_id,
        AppointmentCommandIdempotency.idempotency_key_hash == idempotency_key_hash,
    )
    inserted_id = db.execute(
        postgresql_insert(AppointmentCommandIdempotency)
        .values(
            id=uuid.uuid4(),
            practice_id=practice_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            operation_id=operation_id,
            route_family=route_family,
            idempotency_key_hash=idempotency_key_hash,
            request_body_hash=request_body_hash,
            request_body_canonicalization_version=1,
            state="in_progress",
        )
        .on_conflict_do_nothing(
            constraint="uq_appt_cmd_idem_practice_actor_operation_key"
        )
        .returning(AppointmentCommandIdempotency.id)
    ).scalar_one_or_none()
    record = (
        db.query(AppointmentCommandIdempotency)
        .filter(
            AppointmentCommandIdempotency.id == inserted_id
            if inserted_id is not None
            else identity_filter[0],
            *(() if inserted_id is not None else identity_filter[1:]),
        )
        .with_for_update()
        .one()
    )

    if inserted_id is not None:
        return AppointmentIdempotencyDecision(kind="started", record=record)

    if record.request_body_hash != request_body_hash:
        return AppointmentIdempotencyDecision(kind="conflict", record=record)

    if record.state == "completed":
        return AppointmentIdempotencyDecision(
            kind="replay",
            record=record,
            response_status_code=record.response_status_code,
            response_body_json=record.response_body_json,
            audit_log_id=record.audit_log_id,
        )

    if record.state == "in_progress":
        updated_at = _as_aware_utc(record.updated_at)
        current_time = now or datetime.now(timezone.utc)
        if stale_after is not None and updated_at is not None:
            if current_time - updated_at >= stale_after:
                return AppointmentIdempotencyDecision(
                    kind="stale_in_progress",
                    record=record,
                    audit_log_id=record.audit_log_id,
                )
        return AppointmentIdempotencyDecision(kind="in_progress", record=record)

    return AppointmentIdempotencyDecision(kind="failed_transient", record=record)


def complete_appointment_command(
    db: Session,
    record: AppointmentCommandIdempotency,
    *,
    response_status_code: int,
    response_body: dict[str, Any],
    result_kind: str,
    target_appointment_id: UUID | None = None,
    audit_log_id: UUID | None = None,
    bernie_session_id: str | None = None,
) -> AppointmentCommandIdempotency:
    record.state = "completed"
    record.response_status_code = response_status_code
    record.response_body_json = response_body
    record.response_body_hash = sha256_canonical_json(response_body)
    record.result_kind = result_kind
    record.target_appointment_id = target_appointment_id
    record.audit_log_id = audit_log_id
    record.bernie_session_id = bernie_session_id
    db.flush()
    return record
