"""Unmounted physical helpers for a future delete-confirm command kernel.

No route imports this module. The transaction seam deliberately cannot stage a
product mutation, audit or receipt completion; it only establishes the accepted
authority-first lock/classification boundary for a separately admitted kernel.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Literal, Sequence
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.orm import Session

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.models.tenancy import User, UserCapabilityGrant


DELETE_CONFIRM_OPERATION_ID = "confirmAppointmentDeleteProposal"
DELETE_CONFIRM_ROUTE_FAMILY = "delete-confirm"
DELETE_CONFIRM_RECEIPT_VERSION = 1
DELETE_CONFIRM_SESSION_DOMAIN = b"appointment-delete-session:v1"
DELETE_CONFIRM_CAPABILITY = "appointment.cancel.confirm"
DELETE_CONFIRM_GENERATION_MAX = 9223372036854775807
DELETE_CONFIRM_LOCK_WAIT_DEADLINE_MS = 2000
DELETE_CONFIRM_CANCELLATION_REASON_MAX = 500
DELETE_CONFIRM_STATUS = "Cancelled"
DELETE_CONFIRM_RESPONSE_FIELDS = (
    "appointment_id",
    "status",
    "status_reason_code",
    "cancellation_reason",
    "waiting_area_id",
    "warning_codes",
)
DELETE_CONFIRM_REASON_CODES = frozenset(
    {
        "PATIENT_CANCELLED",
        "PATIENT_RESCHEDULED",
        "PATIENT_UNWELL",
        "PATIENT_TRANSPORT",
        "PRACTITIONER_UNAVAILABLE",
        "CLINIC_OPERATIONAL",
        "CLINIC_RESCHEDULED",
        "ADMIN_ERROR",
        "DUPLICATE_BOOKING",
        "OTHER",
    }
)
DELETE_CONFIRM_ADMITTED_ROLES = frozenset(
    {"Receptionist", "GP", "Nurse", "Admin", "PracticeOwner"}
)

DeleteConfirmDecisionKind = Literal[
    "new_command",
    "replay",
    "conflict",
    "legacy_receipt_not_replayable",
    "in_progress_not_replayable",
    "receipt_integrity_failure",
]


class DeleteConfirmPhysicalError(RuntimeError):
    """Base fail-closed outcome for the unmounted physical seam."""


class DeleteConfirmTargetUnavailable(DeleteConfirmPhysicalError):
    """Practice-scoped user or appointment is unavailable."""


class DeleteConfirmAuthorityRevoked(DeleteConfirmPhysicalError):
    """Current command authority did not survive both checks."""


class DeleteConfirmScaffoldIncomplete(DeleteConfirmPhysicalError):
    """The future kernel did not complete the atomic v1 write set."""


class DeleteConfirmWaitBudgetExhausted(DeleteConfirmPhysicalError):
    """The monotonic cumulative lock wait budget was exhausted."""


@dataclass(frozen=True)
class DeleteConfirmPhysicalDecision:
    kind: DeleteConfirmDecisionKind
    user: User
    appointment: Appointment
    record: AppointmentCommandIdempotency
    pre_state_version: int
    response_body_canonical_bytes: bytes | None = None


def _length_frame(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError("session binding fields must be non-empty strings")
    encoded = value.encode("utf-8")
    if len(encoded) > 0xFFFFFFFF:
        raise ValueError("session binding field is too long")
    return len(encoded).to_bytes(4, "big") + encoded


def _identity_text(value: UUID | str, field_name: str) -> str:
    if not isinstance(value, (UUID, str)) or not str(value):
        raise ValueError(f"{field_name} must be a UUID or non-empty string")
    return str(value)


def _as_uuid(value: UUID | str, field_name: str) -> UUID:
    if isinstance(value, UUID):
        return value
    if isinstance(value, str) and value:
        try:
            return uuid.UUID(value)
        except ValueError:
            pass
    raise ValueError(f"{field_name} must be a UUID or non-empty UUID string")


def _lowercase_sha256(value: str, field_name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{field_name} must be lowercase hexadecimal SHA-256")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be lowercase hexadecimal SHA-256") from exc
    return value


def delete_confirm_session_binding_digest(
    *,
    secret: bytes,
    practice_id: UUID | str,
    actor_user_id: UUID | str,
    authenticated_session_id: str,
) -> bytes:
    """Return the raw 32-byte, domain-separated session-binding HMAC."""
    if not isinstance(secret, bytes) or not secret:
        raise ValueError("a non-empty byte secret is required")
    message = b"\x00".join(
        (
            DELETE_CONFIRM_SESSION_DOMAIN,
            _length_frame(_identity_text(practice_id, "practice_id")),
            _length_frame(_identity_text(actor_user_id, "actor_user_id")),
            _length_frame(authenticated_session_id),
        )
    )
    return hmac.new(secret, message, hashlib.sha256).digest()


def canonical_delete_confirm_response_bytes(
    *,
    appointment_id: UUID | str,
    status_reason_code: str | None,
    cancellation_reason: str | None,
    warning_codes: Sequence[str],
) -> bytes:
    """Serialize exactly the closed six-field patient-free response contract.

    Status is always constructed as ``Cancelled`` and waiting area as JSON null;
    only the dedicated reason, nullable text and already-validated warnings are
    caller supplied. UTF-8 compact JSON is the sole byte representation.
    """
    if status_reason_code not in DELETE_CONFIRM_REASON_CODES:
        raise ValueError("status_reason_code must be one of the ten dedicated codes")
    if cancellation_reason is not None:
        if not isinstance(cancellation_reason, str):
            raise ValueError("cancellation_reason must be a string or null")
        if len(cancellation_reason) > DELETE_CONFIRM_CANCELLATION_REASON_MAX:
            raise ValueError("cancellation_reason exceeds 500 characters")
    if isinstance(warning_codes, (str, bytes)):
        raise ValueError("warning_codes must be a sequence of strings")
    warnings = list(warning_codes)
    if any(not isinstance(code, str) or not code for code in warnings):
        raise ValueError("warning codes must be non-empty strings")
    if len(warnings) != len(set(warnings)):
        raise ValueError("warning codes must already be unique")
    payload = {
        "appointment_id": _identity_text(appointment_id, "appointment_id"),
        "status": DELETE_CONFIRM_STATUS,
        "status_reason_code": status_reason_code,
        "cancellation_reason": cancellation_reason,
        "waiting_area_id": None,
        "warning_codes": warnings,
    }
    if tuple(payload) != DELETE_CONFIRM_RESPONSE_FIELDS:
        raise AssertionError("closed response field order changed")
    return json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def delete_confirm_response_digest(response_bytes: bytes) -> str:
    if not isinstance(response_bytes, bytes) or not response_bytes:
        raise ValueError("non-empty canonical response bytes are required")
    return hashlib.sha256(response_bytes).hexdigest()


def delete_confirm_response_integrity_valid(
    response_bytes: bytes,
    stored_lowercase_sha256: str,
) -> bool:
    if not isinstance(response_bytes, bytes) or not response_bytes:
        return False
    if (
        not isinstance(stored_lowercase_sha256, str)
        or len(stored_lowercase_sha256) != 64
        or stored_lowercase_sha256 != stored_lowercase_sha256.lower()
    ):
        return False
    try:
        bytes.fromhex(stored_lowercase_sha256)
    except ValueError:
        return False
    return hmac.compare_digest(
        delete_confirm_response_digest(response_bytes),
        stored_lowercase_sha256,
    )


def _delete_receipt_v1_complete(record: AppointmentCommandIdempotency) -> bool:
    response_bytes = record.response_body_canonical_bytes
    return bool(
        record.state == "completed"
        and record.completed_receipt_version == DELETE_CONFIRM_RECEIPT_VERSION
        and record.operation_id == DELETE_CONFIRM_OPERATION_ID
        and record.route_family == DELETE_CONFIRM_ROUTE_FAMILY
        and record.result_kind == "confirmed_write"
        and isinstance(record.authority_generation, int)
        and record.authority_generation >= 1
        and isinstance(record.session_binding_digest, bytes)
        and len(record.session_binding_digest) == 32
        and isinstance(record.pre_state_version, int)
        and record.pre_state_version >= 1
        and record.post_state_version == record.pre_state_version + 1
        and isinstance(response_bytes, bytes)
        and response_bytes
        and record.target_appointment_id is not None
        and record.audit_log_id is not None
        and record.response_status_code is not None
        and record.response_body_hash is not None
        and record.response_body_json is not None
    )


def _enum_value(value: object) -> object:
    return getattr(value, "value", value)


def _delete_write_set_complete(
    *,
    record: AppointmentCommandIdempotency,
    audit: AppointmentAuditLog | None,
    appointment: Appointment,
    practice_id: UUID,
    target_appointment_id: UUID,
    actor_user_id: UUID,
    actor_role: str,
    signed_authority_generation: int,
    request_body_hash: str,
    idempotency_key_hash: str,
    session_binding_digest: bytes,
    pre_state_version: int,
    pre_status: object,
    waiting_area_before_id: UUID | None,
) -> bool:
    """Require the exact three-artifact delete write set before commit."""
    if audit is None or not _delete_receipt_v1_complete(record):
        return False
    warning_codes = audit.confirmed_warnings
    if (
        not isinstance(warning_codes, list)
        or any(not isinstance(code, str) or not code for code in warning_codes)
        or len(warning_codes) != len(set(warning_codes))
        or not isinstance(audit.audit_evidence_codes, list)
    ):
        return False
    try:
        expected_response = canonical_delete_confirm_response_bytes(
            appointment_id=target_appointment_id,
            status_reason_code=appointment.status_reason_code,
            cancellation_reason=appointment.cancellation_reason,
            warning_codes=warning_codes,
        )
        expected_json = json.loads(expected_response.decode("utf-8"))
    except (TypeError, ValueError, UnicodeError):
        return False
    post_state_version = pre_state_version + 1
    return bool(
        record.practice_id == practice_id
        and record.actor_user_id == str(actor_user_id)
        and record.actor_role == actor_role
        and record.target_appointment_id == target_appointment_id
        and record.authority_generation == signed_authority_generation
        and record.request_body_hash == request_body_hash
        and record.idempotency_key_hash == idempotency_key_hash
        and record.request_body_canonicalization_version == 1
        and isinstance(record.session_binding_digest, bytes)
        and hmac.compare_digest(record.session_binding_digest, session_binding_digest)
        and record.pre_state_version == pre_state_version
        and record.post_state_version == post_state_version
        and appointment.practice_id == practice_id
        and appointment.id == target_appointment_id
        and appointment.appointment_state_version == post_state_version
        and _enum_value(appointment.status) == DELETE_CONFIRM_STATUS
        and appointment.waiting_area_id is None
        and audit.id == record.audit_log_id
        and audit.command_id == record.id
        and audit.practice_id == practice_id
        and audit.appointment_id == target_appointment_id
        and audit.confirmed_by_user_id == actor_user_id
        and _enum_value(audit.action) == "delete"
        and audit.audit_contract_version == DELETE_CONFIRM_RECEIPT_VERSION
        and audit.authority_generation == signed_authority_generation
        and audit.pre_state_version == pre_state_version
        and audit.post_state_version == post_state_version
        and _enum_value(audit.status_before) == pre_status
        and _enum_value(audit.status_after) == DELETE_CONFIRM_STATUS
        and audit.status_reason_code == appointment.status_reason_code
        and audit.cancellation_reason == appointment.cancellation_reason
        and audit.waiting_area_before_id == waiting_area_before_id
        and audit.waiting_area_after_id is None
        and record.response_body_canonical_bytes == expected_response
        and record.response_body_json == expected_json
        and delete_confirm_response_integrity_valid(
            expected_response, record.response_body_hash
        )
    )


def _bindings_match(
    record: AppointmentCommandIdempotency,
    *,
    actor_role: str,
    target_appointment_id: UUID,
    request_body_hash: str,
    session_binding_digest: bytes,
    signed_authority_generation: int,
) -> bool:
    return bool(
        record.operation_id == DELETE_CONFIRM_OPERATION_ID
        and record.route_family == DELETE_CONFIRM_ROUTE_FAMILY
        and record.actor_role == actor_role
        and record.target_appointment_id == target_appointment_id
        and record.request_body_hash == request_body_hash
        and record.authority_generation == signed_authority_generation
        and isinstance(record.session_binding_digest, bytes)
        and hmac.compare_digest(record.session_binding_digest, session_binding_digest)
    )


def _authority_valid(
    db: Session,
    user: User,
    *,
    actor_role: str,
    signed_authority_generation: int,
) -> bool:
    """Internal complete authority check; no caller callback can weaken it."""
    if user is None or not user.is_active:
        return False
    role_value = getattr(user.role, "value", user.role)
    if role_value != actor_role or actor_role not in DELETE_CONFIRM_ADMITTED_ROLES:
        return False
    if (
        not isinstance(user.authority_generation, int)
        or user.authority_generation < 1
        or user.authority_generation > DELETE_CONFIRM_GENERATION_MAX
    ):
        return False
    if user.authority_generation != signed_authority_generation:
        return False
    grant_exists = db.query(
        db.query(UserCapabilityGrant)
        .filter(
            UserCapabilityGrant.practice_id == user.practice_id,
            UserCapabilityGrant.user_id == user.id,
            UserCapabilityGrant.capability_code == DELETE_CONFIRM_CAPABILITY,
        )
        .exists()
    ).scalar()
    return bool(grant_exists)


@contextmanager
def delete_confirm_locked_transaction(
    db: Session,
    *,
    practice_id: UUID | str,
    target_appointment_id: UUID | str,
    actor_user_id: UUID | str,
    actor_role: str,
    idempotency_key_hash: str,
    request_body_hash: str,
    session_binding_digest: bytes,
    signed_authority_generation: int,
) -> Iterator[DeleteConfirmPhysicalDecision]:
    """Compose, but do not mount, the accepted ordered transaction boundary.

    One monotonic cumulative 2000 ms deadline is created once; only positive
    remaining budget is applied before every potentially blocking authority,
    appointment or idempotency access. The exact order is: User FOR SHARE,
    Appointment FOR UPDATE, first full authority check, select existing
    idempotency FOR UPDATE, only-if-absent target-bound conflict-do-nothing
    insert, winning row FOR UPDATE, second full authority check, then
    classification.

    A future admitted caller may stage the appointment soft-cancel, delete audit
    and v1 receipt while the ``new_command`` decision is yielded. On return, the
    seam verifies that the complete write set and database-owned adjacent version
    exist; otherwise it raises and the transaction rolls back.
    """
    practice_uuid = _as_uuid(practice_id, "practice_id")
    target_uuid = _as_uuid(target_appointment_id, "target_appointment_id")
    actor_uuid = _as_uuid(actor_user_id, "actor_user_id")
    if (
        not isinstance(actor_role, str)
        or actor_role not in DELETE_CONFIRM_ADMITTED_ROLES
    ):
        raise ValueError("actor_role is not admitted")
    if (
        isinstance(signed_authority_generation, bool)
        or not isinstance(signed_authority_generation, int)
        or signed_authority_generation < 1
        or signed_authority_generation > DELETE_CONFIRM_GENERATION_MAX
    ):
        raise ValueError(
            "signed_authority_generation is outside the positive BIGINT range"
        )
    _lowercase_sha256(idempotency_key_hash, "idempotency_key_hash")
    _lowercase_sha256(request_body_hash, "request_body_hash")
    if (
        not isinstance(session_binding_digest, bytes)
        or len(session_binding_digest) != 32
    ):
        raise ValueError("session_binding_digest must contain 32 bytes")

    with db.begin():
        db.execute(text("SET TRANSACTION ISOLATION LEVEL READ COMMITTED"))
        deadline = time.monotonic() + DELETE_CONFIRM_LOCK_WAIT_DEADLINE_MS / 1000.0

        def _apply_lock_budget() -> None:
            remaining_ms = int((deadline - time.monotonic()) * 1000)
            if remaining_ms <= 0:
                raise DeleteConfirmWaitBudgetExhausted(
                    "cumulative lock wait budget exhausted"
                )
            db.execute(
                select(func.set_config("lock_timeout", f"{remaining_ms}ms", True))
            ).scalar_one()

        _apply_lock_budget()
        user = (
            db.query(User)
            .filter(
                User.practice_id == practice_uuid,
                User.id == actor_uuid,
            )
            .with_for_update(read=True)
            .one_or_none()
        )
        if user is None or not user.is_active:
            raise DeleteConfirmTargetUnavailable("command target unavailable")

        _apply_lock_budget()
        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.practice_id == practice_uuid,
                Appointment.id == target_uuid,
            )
            .with_for_update()
            .one_or_none()
        )
        if appointment is None:
            raise DeleteConfirmTargetUnavailable("command target unavailable")

        _apply_lock_budget()
        if not _authority_valid(
            db,
            user,
            actor_role=actor_role,
            signed_authority_generation=signed_authority_generation,
        ):
            raise DeleteConfirmAuthorityRevoked("current authority unavailable")

        identity_filter = (
            AppointmentCommandIdempotency.practice_id == practice_uuid,
            AppointmentCommandIdempotency.actor_user_id == str(actor_uuid),
            AppointmentCommandIdempotency.operation_id == DELETE_CONFIRM_OPERATION_ID,
            AppointmentCommandIdempotency.idempotency_key_hash == idempotency_key_hash,
        )
        _apply_lock_budget()
        record = (
            db.query(AppointmentCommandIdempotency)
            .filter(*identity_filter)
            .with_for_update()
            .one_or_none()
        )
        inserted = False
        if record is None:
            _apply_lock_budget()
            inserted_id = db.execute(
                postgresql_insert(AppointmentCommandIdempotency)
                .values(
                    id=uuid.uuid4(),
                    practice_id=practice_uuid,
                    actor_user_id=str(actor_uuid),
                    actor_role=actor_role,
                    operation_id=DELETE_CONFIRM_OPERATION_ID,
                    route_family=DELETE_CONFIRM_ROUTE_FAMILY,
                    idempotency_key_hash=idempotency_key_hash,
                    request_body_hash=request_body_hash,
                    request_body_canonicalization_version=1,
                    state="in_progress",
                    target_appointment_id=target_uuid,
                    session_binding_digest=session_binding_digest,
                    authority_generation=signed_authority_generation,
                )
                .on_conflict_do_nothing(
                    constraint="uq_appt_cmd_idem_practice_actor_operation_key"
                )
                .returning(AppointmentCommandIdempotency.id)
            ).scalar_one_or_none()
            inserted = inserted_id is not None
            _apply_lock_budget()
            record = (
                db.query(AppointmentCommandIdempotency)
                .filter(
                    AppointmentCommandIdempotency.id == inserted_id
                    if inserted
                    else identity_filter[0],
                    *(() if inserted else identity_filter[1:]),
                )
                .with_for_update()
                .one()
            )

        _apply_lock_budget()
        if not _authority_valid(
            db,
            user,
            actor_role=actor_role,
            signed_authority_generation=signed_authority_generation,
        ):
            raise DeleteConfirmAuthorityRevoked("current authority unavailable")

        pre_state_version = appointment.appointment_state_version
        if not isinstance(pre_state_version, int) or pre_state_version < 1:
            raise DeleteConfirmPhysicalError("appointment state version is invalid")
        pre_status = _enum_value(appointment.status)
        waiting_area_before_id = appointment.waiting_area_id

        if inserted:
            decision = DeleteConfirmPhysicalDecision(
                kind="new_command",
                user=user,
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        elif not _bindings_match(
            record,
            actor_role=actor_role,
            target_appointment_id=target_uuid,
            request_body_hash=request_body_hash,
            session_binding_digest=session_binding_digest,
            signed_authority_generation=signed_authority_generation,
        ):
            decision = DeleteConfirmPhysicalDecision(
                kind="conflict",
                user=user,
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        elif record.state == "completed" and record.completed_receipt_version is None:
            decision = DeleteConfirmPhysicalDecision(
                kind="legacy_receipt_not_replayable",
                user=user,
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        elif record.state != "completed":
            decision = DeleteConfirmPhysicalDecision(
                kind="in_progress_not_replayable",
                user=user,
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        elif not _delete_receipt_v1_complete(
            record
        ) or not delete_confirm_response_integrity_valid(
            record.response_body_canonical_bytes,
            record.response_body_hash,
        ):
            decision = DeleteConfirmPhysicalDecision(
                kind="receipt_integrity_failure",
                user=user,
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        else:
            decision = DeleteConfirmPhysicalDecision(
                kind="replay",
                user=user,
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
                response_body_canonical_bytes=record.response_body_canonical_bytes,
            )

        yield decision

        if decision.kind == "new_command":
            db.flush()
            audit = (
                db.query(AppointmentAuditLog)
                .filter(
                    AppointmentAuditLog.practice_id == practice_uuid,
                    AppointmentAuditLog.id == record.audit_log_id,
                )
                .one_or_none()
            )
            if not _delete_write_set_complete(
                record=record,
                audit=audit,
                appointment=appointment,
                practice_id=practice_uuid,
                target_appointment_id=target_uuid,
                actor_user_id=actor_uuid,
                actor_role=actor_role,
                signed_authority_generation=signed_authority_generation,
                request_body_hash=request_body_hash,
                idempotency_key_hash=idempotency_key_hash,
                session_binding_digest=session_binding_digest,
                pre_state_version=pre_state_version,
                pre_status=pre_status,
                waiting_area_before_id=waiting_area_before_id,
            ):
                raise DeleteConfirmScaffoldIncomplete(
                    "atomic delete-confirm v1 write set is incomplete"
                )
