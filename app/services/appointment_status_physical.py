"""Unmounted physical helpers for a future status-confirm command kernel.

No route imports this module. The transaction seam deliberately cannot stage a
product mutation, audit or receipt completion; it only establishes the accepted
authority-first lock/classification boundary for a separately admitted kernel.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Iterator, Literal, Sequence
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.orm import Session

from app.models.appointments import Appointment, AppointmentCommandIdempotency
from app.models.tenancy import Practice


STATUS_CONFIRM_OPERATION_ID = "confirmAppointmentStatusProposal"
STATUS_CONFIRM_ROUTE_FAMILY = "status-confirm"
STATUS_CONFIRM_RECEIPT_VERSION = 1
STATUS_CONFIRM_SESSION_DOMAIN = b"appointment-status-session:v1"
STATUS_CONFIRM_RESPONSE_FIELDS = (
    "appointment_id",
    "status",
    "status_reason_code",
    "waiting_area_id",
    "warning_codes",
)

StatusConfirmDecisionKind = Literal[
    "new_command",
    "replay",
    "conflict",
    "legacy_receipt_not_replayable",
    "in_progress_not_replayable",
    "receipt_integrity_failure",
]


class StatusConfirmPhysicalError(RuntimeError):
    """Base fail-closed outcome for the unmounted physical seam."""


class StatusConfirmTargetUnavailable(StatusConfirmPhysicalError):
    """Practice or practice-scoped appointment is unavailable."""


class StatusConfirmAuthorityRevoked(StatusConfirmPhysicalError):
    """Current command authority did not survive both checks."""


class StatusConfirmScaffoldIncomplete(StatusConfirmPhysicalError):
    """The future kernel did not complete the atomic v1 write set."""


@dataclass(frozen=True)
class StatusConfirmPhysicalDecision:
    kind: StatusConfirmDecisionKind
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


def status_confirm_session_binding_digest(
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
            STATUS_CONFIRM_SESSION_DOMAIN,
            _length_frame(_identity_text(practice_id, "practice_id")),
            _length_frame(_identity_text(actor_user_id, "actor_user_id")),
            _length_frame(authenticated_session_id),
        )
    )
    return hmac.new(secret, message, hashlib.sha256).digest()


def canonical_status_confirm_response_bytes(
    *,
    appointment_id: UUID | str,
    status: str,
    status_reason_code: str | None,
    waiting_area_id: UUID | str | None,
    warning_codes: Sequence[str],
) -> bytes:
    """Serialize exactly the closed five-field public response contract."""
    if not isinstance(status, str) or not status:
        raise ValueError("status must be a non-empty string")
    if status_reason_code is not None and not isinstance(status_reason_code, str):
        raise ValueError("status_reason_code must be a string or null")
    if isinstance(warning_codes, (str, bytes)):
        raise ValueError("warning_codes must be a sequence of strings")
    warnings = list(warning_codes)
    if any(not isinstance(code, str) or not code for code in warnings):
        raise ValueError("warning codes must be non-empty strings")
    if len(warnings) != len(set(warnings)):
        raise ValueError("warning codes must already be unique")
    payload = {
        "appointment_id": _identity_text(appointment_id, "appointment_id"),
        "status": status,
        "status_reason_code": status_reason_code,
        "waiting_area_id": str(waiting_area_id) if waiting_area_id is not None else None,
        "warning_codes": warnings,
    }
    if tuple(payload) != STATUS_CONFIRM_RESPONSE_FIELDS:
        raise AssertionError("closed response field order changed")
    return json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def status_confirm_response_digest(response_bytes: bytes) -> str:
    if not isinstance(response_bytes, bytes) or not response_bytes:
        raise ValueError("non-empty canonical response bytes are required")
    return hashlib.sha256(response_bytes).hexdigest()


def status_confirm_response_integrity_valid(
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
        status_confirm_response_digest(response_bytes),
        stored_lowercase_sha256,
    )


def _receipt_v1_complete(record: AppointmentCommandIdempotency) -> bool:
    response_bytes = record.response_body_canonical_bytes
    return bool(
        record.completed_receipt_version == STATUS_CONFIRM_RECEIPT_VERSION
        and record.operation_id == STATUS_CONFIRM_OPERATION_ID
        and record.route_family == STATUS_CONFIRM_ROUTE_FAMILY
        and record.result_kind == "confirmed_write"
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


def _bindings_match(
    record: AppointmentCommandIdempotency,
    *,
    actor_role: str,
    target_appointment_id: UUID,
    request_body_hash: str,
    session_binding_digest: bytes,
) -> bool:
    return bool(
        record.operation_id == STATUS_CONFIRM_OPERATION_ID
        and record.route_family == STATUS_CONFIRM_ROUTE_FAMILY
        and record.actor_role == actor_role
        and record.target_appointment_id == target_appointment_id
        and record.request_body_hash == request_body_hash
        and isinstance(record.session_binding_digest, bytes)
        and hmac.compare_digest(record.session_binding_digest, session_binding_digest)
    )


@contextmanager
def status_confirm_locked_transaction(
    db: Session,
    *,
    practice_id: UUID,
    target_appointment_id: UUID,
    actor_user_id: str,
    actor_role: str,
    idempotency_key_hash: str,
    request_body_hash: str,
    session_binding_digest: bytes,
    practice_is_active: Callable[[Practice], bool],
    current_authority: Callable[[Practice, Appointment], bool],
    lock_timeout_ms: int,
) -> Iterator[StatusConfirmPhysicalDecision]:
    """Compose, but do not mount, the accepted ordered transaction boundary.

    A future admitted caller may stage the appointment mutation, audit and v1
    receipt while the `new_command` decision is yielded. On return, the seam
    verifies that the complete write set and database-owned adjacent version
    exist; otherwise it raises and the transaction rolls back.
    """
    if lock_timeout_ms <= 0:
        raise ValueError("lock_timeout_ms must be positive")
    if len(session_binding_digest) != 32:
        raise ValueError("session_binding_digest must contain 32 bytes")

    with db.begin():
        db.execute(text("SET TRANSACTION ISOLATION LEVEL READ COMMITTED"))
        db.execute(
            select(func.set_config("lock_timeout", f"{lock_timeout_ms}ms", True))
        )
        practice = (
            db.query(Practice)
            .filter(Practice.id == practice_id)
            .with_for_update(read=True)
            .one_or_none()
        )
        if practice is None:
            raise StatusConfirmTargetUnavailable("command target unavailable")
        if not practice_is_active(practice):
            raise StatusConfirmTargetUnavailable("command target unavailable")

        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.practice_id == practice_id,
                Appointment.id == target_appointment_id,
            )
            .with_for_update()
            .one_or_none()
        )
        if appointment is None:
            raise StatusConfirmTargetUnavailable("command target unavailable")
        if not current_authority(practice, appointment):
            raise StatusConfirmAuthorityRevoked("current authority unavailable")

        identity_filter = (
            AppointmentCommandIdempotency.practice_id == practice_id,
            AppointmentCommandIdempotency.actor_user_id == actor_user_id,
            AppointmentCommandIdempotency.operation_id == STATUS_CONFIRM_OPERATION_ID,
            AppointmentCommandIdempotency.idempotency_key_hash
            == idempotency_key_hash,
        )
        inserted_id = db.execute(
            postgresql_insert(AppointmentCommandIdempotency)
            .values(
                id=uuid.uuid4(),
                practice_id=practice_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                operation_id=STATUS_CONFIRM_OPERATION_ID,
                route_family=STATUS_CONFIRM_ROUTE_FAMILY,
                idempotency_key_hash=idempotency_key_hash,
                request_body_hash=request_body_hash,
                request_body_canonicalization_version=1,
                state="in_progress",
                target_appointment_id=target_appointment_id,
                session_binding_digest=session_binding_digest,
            )
            .on_conflict_do_nothing(
                constraint="uq_appt_cmd_idem_practice_actor_operation_key"
            )
            .returning(AppointmentCommandIdempotency.id)
        ).scalar_one_or_none()
        inserted = inserted_id is not None
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

        if not current_authority(practice, appointment):
            raise StatusConfirmAuthorityRevoked("current authority unavailable")

        pre_state_version = appointment.appointment_state_version
        if not isinstance(pre_state_version, int) or pre_state_version < 1:
            raise StatusConfirmPhysicalError("appointment state version is invalid")

        if inserted:
            decision = StatusConfirmPhysicalDecision(
                kind="new_command",
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        elif not _bindings_match(
            record,
            actor_role=actor_role,
            target_appointment_id=target_appointment_id,
            request_body_hash=request_body_hash,
            session_binding_digest=session_binding_digest,
        ):
            decision = StatusConfirmPhysicalDecision(
                kind="conflict",
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        elif record.state == "completed" and record.completed_receipt_version is None:
            decision = StatusConfirmPhysicalDecision(
                kind="legacy_receipt_not_replayable",
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        elif record.state != "completed":
            decision = StatusConfirmPhysicalDecision(
                kind="in_progress_not_replayable",
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        elif not _receipt_v1_complete(record) or not status_confirm_response_integrity_valid(
            record.response_body_canonical_bytes,
            record.response_body_hash,
        ):
            decision = StatusConfirmPhysicalDecision(
                kind="receipt_integrity_failure",
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
            )
        else:
            decision = StatusConfirmPhysicalDecision(
                kind="replay",
                appointment=appointment,
                record=record,
                pre_state_version=pre_state_version,
                response_body_canonical_bytes=record.response_body_canonical_bytes,
            )

        yield decision

        if decision.kind == "new_command":
            db.flush()
            if (
                not _receipt_v1_complete(record)
                or record.pre_state_version != pre_state_version
                or appointment.appointment_state_version != pre_state_version + 1
                or record.post_state_version != appointment.appointment_state_version
                or not status_confirm_response_integrity_valid(
                    record.response_body_canonical_bytes,
                    record.response_body_hash,
                )
            ):
                raise StatusConfirmScaffoldIncomplete(
                    "atomic status-confirm v1 write set is incomplete"
                )
