import base64
import binascii
import hashlib
import hmac
import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Literal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
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
    "evidence_replay_rejected",
]


CHECK_IN_EVIDENCE_SCHEMA_VERSION = "rayleen.check_in_evidence.v1"
CHECK_IN_EVIDENCE_PURPOSE = "rayleen_confirm_check_in_proposal"
CHECK_IN_EVIDENCE_TTL = timedelta(seconds=120)


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
    confirmation_evidence_consumed_at: datetime | None = None,
) -> AppointmentCommandIdempotency:
    record.state = "completed"
    record.response_status_code = response_status_code
    record.response_body_json = response_body
    record.response_body_hash = sha256_canonical_json(response_body)
    record.result_kind = result_kind
    record.target_appointment_id = target_appointment_id
    record.audit_log_id = audit_log_id
    record.bernie_session_id = bernie_session_id
    if confirmation_evidence_consumed_at is not None:
        record.confirmation_evidence_consumed_at = confirmation_evidence_consumed_at
    db.flush()
    return record


def _uuid_str_or_none(value: UUID | None) -> str | None:
    return str(value) if value is not None else None


def mint_check_in_evidence_token(
    *,
    practice_id: UUID,
    actor_user_id: UUID,
    appointment_id: UUID,
    status_before: str,
    waiting_area_id_before: UUID | None,
    waiting_area_id_target: UUID | None,
    check_in_proposal_freshness_id: str,
    secret: bytes,
    nonce: str | None = None,
    issued_at: datetime | None = None,
    ttl_seconds: int | None = None,
    purpose: str | None = None,
) -> str:
    """Mint the one opaque patient-free base64url A5.1 check-in evidence token.

    The token is a random-nonce, purpose-bound, actor/practice/appointment/state/
    waiting-area/freshness-bound HMAC-signed value with a maximum 120-second
    lifetime. Client-visible structured claims cannot be submitted as a
    substitute for this opaque value.
    """
    issued = issued_at or datetime.now(timezone.utc)
    if issued.tzinfo is None:
        issued = issued.replace(tzinfo=timezone.utc)
    expires = issued + timedelta(seconds=ttl_seconds or int(CHECK_IN_EVIDENCE_TTL.total_seconds()))
    payload = {
        "schema_version": CHECK_IN_EVIDENCE_SCHEMA_VERSION,
        "purpose": purpose or CHECK_IN_EVIDENCE_PURPOSE,
        "nonce": nonce or secrets.token_hex(16),
        "issued_at": issued.isoformat(),
        "expires_at": expires.isoformat(),
        "practice_id": str(practice_id),
        "actor_user_id": str(actor_user_id),
        "appointment_id": str(appointment_id),
        "status_before": status_before,
        "waiting_area_id_before": _uuid_str_or_none(waiting_area_id_before),
        "waiting_area_id_target": _uuid_str_or_none(waiting_area_id_target),
        "check_in_proposal_freshness_id": check_in_proposal_freshness_id,
    }
    body = canonical_json(payload).encode("utf-8")
    encoded = base64.urlsafe_b64encode(body).decode("ascii").rstrip("=")
    signature = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def verify_check_in_evidence_token(
    token: str,
    *,
    secret: bytes,
    now: datetime,
    expected_practice_id: str,
    expected_actor_user_id: str,
    expected_appointment_id: str,
    expected_status_before: str,
    expected_waiting_area_id_before: str | None,
    expected_waiting_area_id_target: str | None,
    expected_check_in_proposal_freshness_id: str,
) -> tuple[bool, str, dict[str, Any] | None]:
    """Verify an opaque A5.1 evidence token and its exact current-state binding.

    Returns (verified, code, payload). Fail-closed on malformed, tampered,
    wrong-version, wrong-purpose, expired, wrong-actor, wrong-practice,
    wrong-appointment, wrong-state, wrong-area or wrong-freshness.
    """
    if not isinstance(token, str) or not token:
        return False, "signed_evidence_missing", None
    try:
        encoded, signature = token.split(".", 1)
        expected_signature = hmac.new(
            secret, encoded.encode("ascii"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return False, "signed_evidence_tampered", None
        padded = encoded + "=" * (-len(encoded) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        payload = json.loads(raw.decode("utf-8"))
    except (
        ValueError,
        TypeError,
        binascii.Error,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return False, "signed_evidence_malformed", None

    if not isinstance(payload, dict):
        return False, "signed_evidence_malformed", None
    if payload.get("schema_version") != CHECK_IN_EVIDENCE_SCHEMA_VERSION:
        return False, "signed_evidence_wrong_version", None
    if payload.get("purpose") != CHECK_IN_EVIDENCE_PURPOSE:
        return False, "signed_evidence_wrong_purpose", None

    expires_raw = payload.get("expires_at")
    if not isinstance(expires_raw, str):
        return False, "signed_evidence_malformed", None
    try:
        expires_at = datetime.fromisoformat(expires_raw)
    except ValueError:
        return False, "signed_evidence_malformed", None
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if now is None:
        now = datetime.now(timezone.utc)
    if now > expires_at:
        return False, "signed_evidence_expired", None

    expected = {
        "practice_id": expected_practice_id,
        "actor_user_id": expected_actor_user_id,
        "appointment_id": expected_appointment_id,
        "status_before": expected_status_before,
        "waiting_area_id_before": expected_waiting_area_id_before,
        "waiting_area_id_target": expected_waiting_area_id_target,
        "check_in_proposal_freshness_id": expected_check_in_proposal_freshness_id,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            return False, "signed_evidence_mismatch", None
    return True, "signed_evidence_verified", payload


def claim_appointment_check_in_command(
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
    confirmation_evidence_hash: str | None,
    stale_after: timedelta | None = None,
    now: datetime | None = None,
) -> AppointmentIdempotencyDecision:
    """Claim an A5.1 check-in command with its unique signed-evidence hash.

    Same-key replay/conflict/in-progress semantics are inherited from the shared
    claim. A first-use claim attaches the evidence hash under the unique partial
    constraint on (practice_id, operation_id, confirmation_evidence_hash) using a
    conflict-aware savepoint so a concurrent or prior different-key reuse is
    deterministically classified as evidence_replay_rejected rather than leaking
    a database integrity error.
    """
    decision = claim_appointment_command(
        db,
        practice_id=practice_id,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        operation_id=operation_id,
        route_family=route_family,
        raw_idempotency_key=raw_idempotency_key,
        request_body=request_body,
        secret=secret,
        stale_after=stale_after,
        now=now,
    )
    if decision.kind != "started" or confirmation_evidence_hash is None:
        return decision

    record = decision.record
    try:
        with db.begin_nested():
            record.confirmation_evidence_hash = confirmation_evidence_hash
            db.flush()
    except IntegrityError:
        # A different command row already consumed (or is consuming) this exact
        # evidence hash. Abort the whole attempt and classify it as replay.
        db.rollback()
        return AppointmentIdempotencyDecision(
            kind="evidence_replay_rejected",
            record=record,
        )
    return decision
