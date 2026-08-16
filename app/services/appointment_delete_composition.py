"""Unmounted pure composition boundary for the delete-confirm command kernel.

No router imports this module. The callable accepts an admission adapter and a
transaction factory explicitly so its control flow can be rehearsed entirely
with authored-synthetic, in-memory doubles while retaining the exact physical
transaction seam as the default.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, ContextManager, Mapping
from uuid import UUID

from app.services.appointment_idempotency import hash_idempotency_key
from app.services.appointment_delete_physical import (
    DELETE_CONFIRM_CANCELLATION_REASON_MAX,
    DELETE_CONFIRM_RECEIPT_VERSION,
    DELETE_CONFIRM_REASON_CODES,
    DELETE_CONFIRM_STATUS,
    DeleteConfirmAuthorityRevoked,
    DeleteConfirmPhysicalDecision,
    DeleteConfirmPhysicalError,
    DeleteConfirmScaffoldIncomplete,
    DeleteConfirmTargetUnavailable,
    DeleteConfirmWaitBudgetExhausted,
    canonical_delete_confirm_response_bytes,
    delete_confirm_locked_transaction,
    delete_confirm_response_digest,
    delete_confirm_response_integrity_valid,
    delete_confirm_session_binding_digest,
)


DELETE_CONFIRM_OPERATION_ID = "confirmAppointmentDeleteProposal"
DELETE_CONFIRM_ROUTE_FAMILY = "delete-confirm"
DELETE_CONFIRM_KERNEL_SCHEMA = "raisa.delete_kernel_request.v1"
DELETE_CONFIRM_LOCK_PLAN = ("user", "appointment", "idempotency_record")
DELETE_CONFIRM_PUBLIC_SCHEMA = "raisa.delete_confirm_public_envelope.v1"
DELETE_CONFIRM_RECEIPT_SCHEMA = "appointment.delete_confirmation_receipt.v1"
DELETE_CONFIRM_INTENT = "confirm_delete_appointment"
DELETE_CONFIRM_SUMMARY = "Confirmed delete proposal and cancelled one appointment."
DELETE_CONFIRM_AUDIT_LABELS = (
    "delete_product_adapter_v1",
    "delete_signed_confirmation_evidence_verified",
    "delete_current_authority_rechecked",
)
DELETE_CONFIRM_WARNING_REGISTRY: Mapping[str, Mapping[str, str]] = {
    "waiting_area_cleared": {
        "code": "waiting_area_cleared",
        "severity": "warning",
        "message": "Deleting this appointment will remove the patient from the waiting area.",
    }
}
DELETE_CONFIRM_WARNING_CODES = frozenset(DELETE_CONFIRM_WARNING_REGISTRY)
DELETE_CONFIRM_PRIVATE_FIELDS = (
    "appointment_id",
    "status",
    "status_reason_code",
    "cancellation_reason",
    "waiting_area_id",
    "warning_codes",
)


AdmissionAdapter = Callable[[dict[str, Any]], dict[str, Any]]
LockedServerFactory = Callable[[Any, "DeleteConfirmServerIngress"], Mapping[str, Any]]
TransactionFactory = Callable[..., ContextManager[DeleteConfirmPhysicalDecision]]


@dataclass(frozen=True)
class DeleteConfirmServerIngress:
    """Facts owned by authenticated server/session and current-state services."""

    practice_id: UUID | str
    actor_id: UUID | str
    actor_role: str
    authority_generation: int
    session_id: str
    authority_current: bool
    current_state: Mapping[str, Any]
    expected_freshness_id: str
    evidence_status: str
    evidence_purpose: str
    expected_evidence_purpose: str
    evidence_binding: str

    def as_adapter_mapping(self) -> dict[str, Any]:
        return {
            "practice_id": str(self.practice_id),
            "actor_id": str(self.actor_id),
            "actor_role": self.actor_role,
            "authority_generation": self.authority_generation,
            "session_id": self.session_id,
            "authority_current": self.authority_current,
            "current_state": copy.deepcopy(dict(self.current_state)),
            "expected_freshness_id": self.expected_freshness_id,
            "evidence_status": self.evidence_status,
            "evidence_purpose": self.evidence_purpose,
            "expected_evidence_purpose": self.expected_evidence_purpose,
            "evidence_binding": self.evidence_binding,
        }


@dataclass(frozen=True)
class DeleteConfirmEffectResult:
    """The staged atomic effect returned by the injected delete-only kernel.

    Composition writes the complete six-field private receipt; the staged effect
    returns only the attributable delete-audit identity.
    """

    audit_log_id: UUID | str


@dataclass(frozen=True)
class DeleteConfirmCompositionResult:
    kind: str
    status_code: int
    body: Mapping[str, Any]
    stored_response_bytes: bytes | None = None


class _LockedAdmissionStopped(RuntimeError):
    def __init__(self, admission: Mapping[str, Any]):
        super().__init__(str(admission.get("reason") or "locked admission stopped"))
        self.admission = dict(admission)


class _ReceiptCompositionFailed(RuntimeError):
    pass


def validate_delete_confirm_private_receipt_bytes(response_bytes: bytes) -> dict[str, Any]:
    """Strictly validate the six-field private receipt and return its payload.

    Requires exact object key order, exact compact UTF-8 bytes, ``Cancelled``
    status, null waiting area, one dedicated reason code, nullable <=500-char
    cancellation text and sorted-unique canonical warning codes.
    """
    if not isinstance(response_bytes, bytes) or not response_bytes:
        raise ValueError("stored delete-confirm response must be non-empty bytes")
    try:
        payload = json.loads(response_bytes)
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("stored delete-confirm response is not valid UTF-8 JSON") from exc
    if not isinstance(payload, dict) or tuple(payload) != DELETE_CONFIRM_PRIVATE_FIELDS:
        raise ValueError("stored delete-confirm response field order is invalid")
    if payload.get("status") != DELETE_CONFIRM_STATUS:
        raise ValueError("stored delete-confirm status must be Cancelled")
    if payload.get("waiting_area_id") is not None:
        raise ValueError("stored delete-confirm waiting area must be null")
    if payload.get("status_reason_code") not in DELETE_CONFIRM_REASON_CODES:
        raise ValueError("stored delete-confirm reason code is not dedicated")
    cancellation_reason = payload.get("cancellation_reason")
    if cancellation_reason is not None:
        if not isinstance(cancellation_reason, str):
            raise ValueError(
                "stored delete-confirm cancellation text must be a string or null"
            )
        if len(cancellation_reason) > DELETE_CONFIRM_CANCELLATION_REASON_MAX:
            raise ValueError("stored delete-confirm cancellation text is too long")
    warnings = payload.get("warning_codes")
    if (
        not isinstance(warnings, list)
        or any(not isinstance(code, str) or not code for code in warnings)
        or warnings != sorted(warnings)
        or len(warnings) != len(set(warnings))
        or any(code not in DELETE_CONFIRM_WARNING_CODES for code in warnings)
    ):
        raise ValueError("stored delete-confirm warning codes are invalid")
    try:
        canonical = canonical_delete_confirm_response_bytes(
            appointment_id=payload["appointment_id"],
            status_reason_code=payload["status_reason_code"],
            cancellation_reason=payload["cancellation_reason"],
            warning_codes=payload["warning_codes"],
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("stored delete-confirm response is not canonical") from exc
    if canonical != response_bytes:
        raise ValueError("stored delete-confirm response is not canonical compact UTF-8")
    return payload


def delete_confirm_envelope_projection(response_bytes: bytes) -> dict[str, Any]:
    """Project the minimal public envelope strictly from validated private bytes.

    The projection never reads a current appointment, ``AppointmentOut`` or any
    live database state; it consumes only the validated private receipt bytes.
    """
    payload = validate_delete_confirm_private_receipt_bytes(response_bytes)
    return {
        "schema_version": DELETE_CONFIRM_PUBLIC_SCHEMA,
        "intent": DELETE_CONFIRM_INTENT,
        "safe": True,
        "requires_confirmation": False,
        "autonomy_tier": "confirmed_write",
        "summary": DELETE_CONFIRM_SUMMARY,
        "receipt": {
            "schema_version": DELETE_CONFIRM_RECEIPT_SCHEMA,
            "appointment_id": payload["appointment_id"],
            "status": payload["status"],
            "status_reason_code": payload["status_reason_code"],
            "cancellation_reason": payload["cancellation_reason"],
            "waiting_area_id": payload["waiting_area_id"],
            "warning_codes": list(payload["warning_codes"]),
        },
        "warnings": [
            dict(DELETE_CONFIRM_WARNING_REGISTRY[code]) for code in payload["warning_codes"]
        ],
        "blocks": [],
        "audit_evidence": list(DELETE_CONFIRM_AUDIT_LABELS),
    }


def canonical_delete_confirm_envelope_bytes(envelope: Mapping[str, Any]) -> bytes:
    """Validate and canonically serialize the complete public envelope.

    Serialization is sorted-key compact UTF-8 JSON without NaN. The envelope may
    not contain an ``appointment``, patient, practitioner, schedule, notes,
    reason, audit identity or live projection field.
    """
    if not isinstance(envelope, Mapping):
        raise ValueError("delete-confirm public envelope must be a mapping")
    supplied = copy.deepcopy(dict(envelope))
    expected_keys = {
        "schema_version",
        "intent",
        "safe",
        "requires_confirmation",
        "autonomy_tier",
        "summary",
        "receipt",
        "warnings",
        "blocks",
        "audit_evidence",
    }
    if set(supplied) != expected_keys:
        raise ValueError("delete-confirm public envelope fields are incomplete")
    if supplied["schema_version"] != DELETE_CONFIRM_PUBLIC_SCHEMA:
        raise ValueError("delete-confirm public schema version is invalid")
    if (
        supplied["intent"] != DELETE_CONFIRM_INTENT
        or supplied["safe"] is not True
        or supplied["requires_confirmation"] is not False
        or supplied["autonomy_tier"] != "confirmed_write"
        or supplied["summary"] != DELETE_CONFIRM_SUMMARY
        or supplied["blocks"] != []
        or supplied["audit_evidence"] != list(DELETE_CONFIRM_AUDIT_LABELS)
    ):
        raise ValueError("delete-confirm public constants are invalid")
    receipt = supplied["receipt"]
    if not isinstance(receipt, dict) or set(receipt) != {
        "schema_version",
        "appointment_id",
        "status",
        "status_reason_code",
        "cancellation_reason",
        "waiting_area_id",
        "warning_codes",
    }:
        raise ValueError("delete-confirm public receipt is invalid")
    if receipt["schema_version"] != DELETE_CONFIRM_RECEIPT_SCHEMA:
        raise ValueError("delete-confirm public receipt schema is invalid")
    warnings = supplied["warnings"]
    if not isinstance(warnings, list):
        raise ValueError("delete-confirm public warnings must be a list")
    receipt_warning_codes = receipt["warning_codes"]
    if (
        not isinstance(receipt_warning_codes, list)
        or any(code not in DELETE_CONFIRM_WARNING_CODES for code in receipt_warning_codes)
    ):
        raise ValueError("delete-confirm public receipt warnings are invalid")
    expected_warnings = [
        dict(DELETE_CONFIRM_WARNING_REGISTRY[code]) for code in receipt_warning_codes
    ]
    if warnings != expected_warnings:
        raise ValueError("delete-confirm public warnings are not the registry projection")
    raw = json.dumps(
        supplied,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if json.loads(raw) != supplied:
        raise AssertionError("canonical response does not round-trip")
    return raw


def _blocked(reason: str) -> DeleteConfirmCompositionResult:
    body = {
        "schema_version": DELETE_CONFIRM_PUBLIC_SCHEMA,
        "intent": DELETE_CONFIRM_INTENT,
        "safe": False,
        "requires_confirmation": True,
        "autonomy_tier": "blocked",
        "summary": "Delete confirmation was blocked.",
        "receipt": None,
        "warnings": [],
        "blocks": [
            {
                "code": reason,
                "severity": "blocked",
                "message": "The delete confirmation did not pass current checks.",
            }
        ],
        "audit_evidence": [],
    }
    return DeleteConfirmCompositionResult("blocked", 200, body)


def _error(status_code: int, code: str, message: str) -> DeleteConfirmCompositionResult:
    return DeleteConfirmCompositionResult(
        "error",
        status_code,
        {"detail": {"code": code, "message": message}},
    )


def _map_admission_stop(admission: Mapping[str, Any]) -> DeleteConfirmCompositionResult:
    outcome = admission.get("outcome")
    reason = str(admission.get("reason") or "validation_rejected")
    if outcome == "authority_revoked":
        return _error(403, "current_authority_unavailable", "Current authority is unavailable.")
    if outcome == "idempotency_conflict":
        return _error(409, "idempotency_key_required", "A valid Idempotency-Key is required.")
    return _blocked(reason)


def _validate_ready_request(
    admission: Mapping[str, Any],
    ingress: DeleteConfirmServerIngress,
) -> dict[str, Any]:
    if admission.get("kind") != "kernel_request_ready":
        raise ValueError("admission result is not kernel-request ready")
    request = admission.get("kernel_request")
    if not isinstance(request, dict) or admission.get("effect_authority") is not False:
        raise ValueError("admission result has an invalid effect boundary")
    expected = {
        "operation_id": DELETE_CONFIRM_OPERATION_ID,
        "route_family": DELETE_CONFIRM_ROUTE_FAMILY,
        "practice_id": str(ingress.practice_id),
        "actor_id": str(ingress.actor_id),
        "actor_role": ingress.actor_role,
        "authority_generation": ingress.authority_generation,
        "session_id": ingress.session_id,
        "lock_plan": list(DELETE_CONFIRM_LOCK_PLAN),
        "effect_authority": False,
    }
    for field, value in expected.items():
        if request.get(field) != value:
            raise ValueError(f"admitted request disagrees with server-owned {field}")
    if request.get("schema_version") != DELETE_CONFIRM_KERNEL_SCHEMA:
        raise ValueError("admitted request schema version is invalid")
    command = request.get("command")
    if not isinstance(command, dict) or command.get("kind") != "delete":
        raise ValueError("admitted request is not delete-only")
    if set(command) != {
        "kind",
        "appointment_id",
        "clears_waiting_area",
        "cancellation_reason",
        "status_reason_code",
    }:
        raise ValueError("admitted delete command fields are incomplete")
    if command.get("appointment_id") != request.get("target_appointment_id"):
        raise ValueError("admitted command target binding is invalid")
    if not isinstance(command.get("clears_waiting_area"), bool):
        raise ValueError("admitted clears-waiting-area flag is invalid")
    if command.get("status_reason_code") not in DELETE_CONFIRM_REASON_CODES:
        raise ValueError("admitted delete reason code is invalid")
    cancellation_reason = command.get("cancellation_reason")
    if cancellation_reason is not None:
        if not isinstance(cancellation_reason, str):
            raise ValueError("admitted cancellation text is invalid")
        if len(cancellation_reason) > DELETE_CONFIRM_CANCELLATION_REASON_MAX:
            raise ValueError("admitted cancellation text is too long")
    source_version = request.get("source_version")
    if (
        not isinstance(source_version, int)
        or isinstance(source_version, bool)
        or source_version < 1
    ):
        raise ValueError("admitted source version is invalid")
    warnings = request.get("warning_codes")
    if (
        not isinstance(warnings, list)
        or any(not isinstance(code, str) or not code for code in warnings)
        or warnings != sorted(set(warnings))
        or any(code not in DELETE_CONFIRM_WARNING_CODES for code in warnings)
    ):
        raise ValueError("admitted warning codes are invalid")
    idempotency_key = request.get("idempotency_key")
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        raise ValueError("admitted idempotency key is invalid")
    digest = request.get("request_digest")
    if not isinstance(digest, str) or len(digest) != 64 or digest != digest.lower():
        raise ValueError("admitted request digest is invalid")
    try:
        bytes.fromhex(digest)
    except ValueError as exc:
        raise ValueError("admitted request digest is invalid") from exc
    digest_payload = {
        key: value for key, value in request.items() if key != "request_digest"
    }
    expected_digest = hashlib.sha256(
        json.dumps(
            digest_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    if digest != expected_digest:
        raise ValueError("admitted request digest does not bind the request")
    return request


def _stage_completed_receipt(
    decision: DeleteConfirmPhysicalDecision,
    *,
    effect: DeleteConfirmEffectResult,
    session_digest: bytes,
    request: Mapping[str, Any],
) -> bytes:
    if not isinstance(effect, DeleteConfirmEffectResult):
        raise _ReceiptCompositionFailed("delete effect returned an invalid result")
    appointment = decision.appointment
    command = request["command"]
    appointment_status = (
        appointment.status.value
        if hasattr(appointment.status, "value")
        else appointment.status
    )
    if appointment_status != DELETE_CONFIRM_STATUS:
        raise _ReceiptCompositionFailed("staged appointment is not Cancelled")
    if getattr(appointment, "waiting_area_id", None) is not None:
        raise _ReceiptCompositionFailed("staged appointment still has a waiting area")
    if command["status_reason_code"] != getattr(appointment, "status_reason_code", None):
        raise _ReceiptCompositionFailed("staged reason differs from locked command")
    if command["cancellation_reason"] != getattr(appointment, "cancellation_reason", None):
        raise _ReceiptCompositionFailed("staged cancellation text differs from locked command")
    try:
        response_bytes = canonical_delete_confirm_response_bytes(
            appointment_id=decision.appointment.id,
            status_reason_code=command["status_reason_code"],
            cancellation_reason=command["cancellation_reason"],
            warning_codes=request["warning_codes"],
        )
    except (TypeError, ValueError) as exc:
        raise _ReceiptCompositionFailed("private delete-confirm receipt is invalid") from exc
    validate_delete_confirm_private_receipt_bytes(response_bytes)
    if str(decision.appointment.id) != str(request["target_appointment_id"]):
        raise _ReceiptCompositionFailed("private receipt target differs from locked target")
    if not isinstance(effect.audit_log_id, (UUID, str)) or not str(effect.audit_log_id):
        raise _ReceiptCompositionFailed("delete effect did not return an audit identity")
    record = decision.record
    record.state = "completed"
    record.response_status_code = 200
    record.response_body_json = json.loads(response_bytes)
    record.response_body_hash = delete_confirm_response_digest(response_bytes)
    record.result_kind = "confirmed_write"
    record.target_appointment_id = decision.appointment.id
    record.audit_log_id = effect.audit_log_id
    record.completed_receipt_version = DELETE_CONFIRM_RECEIPT_VERSION
    record.session_binding_digest = session_digest
    record.pre_state_version = decision.pre_state_version
    record.post_state_version = decision.appointment.appointment_state_version
    record.response_body_canonical_bytes = response_bytes
    record.authority_generation = request["authority_generation"]
    return response_bytes


def _validated_stored_response(decision: DeleteConfirmPhysicalDecision) -> bytes:
    response_bytes = decision.response_body_canonical_bytes
    record = decision.record
    if not isinstance(response_bytes, bytes) or not response_bytes:
        raise _ReceiptCompositionFailed("stored response bytes are missing")
    if not delete_confirm_response_integrity_valid(
        response_bytes, record.response_body_hash
    ):
        raise _ReceiptCompositionFailed("stored response integrity failed")
    if json.loads(response_bytes) != record.response_body_json:
        raise _ReceiptCompositionFailed("stored JSON and canonical bytes differ")
    validate_delete_confirm_private_receipt_bytes(response_bytes)
    return response_bytes


def compose_delete_confirm(
    transport: Mapping[str, Any],
    *,
    server_ingress: DeleteConfirmServerIngress,
    db: Any,
    idempotency_secret: bytes,
    session_binding_secret: bytes,
    admission_adapter: AdmissionAdapter,
    locked_server_factory: LockedServerFactory,
    stage_effect: Callable[
        [DeleteConfirmPhysicalDecision, Mapping[str, Any]], DeleteConfirmEffectResult
    ],
    transaction_factory: TransactionFactory = delete_confirm_locked_transaction,
) -> DeleteConfirmCompositionResult:
    """Compose the admitted delete-only request without mounting the route."""
    adapter_input = {
        "structure": "valid",
        "transport": copy.deepcopy(dict(transport)),
        "server": server_ingress.as_adapter_mapping(),
    }
    try:
        admission = admission_adapter(adapter_input)
    except (AttributeError, KeyError, TypeError, ValueError):
        return _blocked("admission_input_invalid")
    if admission.get("kind") != "kernel_request_ready":
        return _map_admission_stop(admission)
    try:
        request = _validate_ready_request(admission, server_ingress)
        idempotency_key_hash = hash_idempotency_key(
            request["idempotency_key"], idempotency_secret
        )
        session_digest = delete_confirm_session_binding_digest(
            secret=session_binding_secret,
            practice_id=server_ingress.practice_id,
            actor_user_id=server_ingress.actor_id,
            authenticated_session_id=server_ingress.session_id,
        )
        response_bytes: bytes | None = None
        with transaction_factory(
            db,
            practice_id=server_ingress.practice_id,
            target_appointment_id=request["target_appointment_id"],
            actor_user_id=str(server_ingress.actor_id),
            actor_role=server_ingress.actor_role,
            idempotency_key_hash=idempotency_key_hash,
            request_body_hash=request["request_digest"],
            session_binding_digest=session_digest,
            signed_authority_generation=request["authority_generation"],
        ) as decision:
            if decision.kind == "new_command":
                locked_input = {
                    "structure": "valid",
                    "transport": copy.deepcopy(dict(transport)),
                    "server": dict(
                        locked_server_factory(decision.appointment, server_ingress)
                    ),
                }
                try:
                    locked_admission = admission_adapter(locked_input)
                except (AttributeError, KeyError, TypeError, ValueError) as exc:
                    raise _LockedAdmissionStopped(
                        {
                            "outcome": "validation_rejected",
                            "reason": "locked_admission_input_invalid",
                        }
                    ) from exc
                if locked_admission.get("kind") != "kernel_request_ready":
                    raise _LockedAdmissionStopped(locked_admission)
                locked_request = _validate_ready_request(locked_admission, server_ingress)
                if locked_request["request_digest"] != request["request_digest"]:
                    raise _LockedAdmissionStopped(
                        {
                            "outcome": "stale_precondition",
                            "reason": "locked_request_digest_changed",
                        }
                    )
                effect = stage_effect(decision, locked_request)
                if not isinstance(effect, DeleteConfirmEffectResult):
                    raise _ReceiptCompositionFailed(
                        "delete effect returned an invalid result"
                    )
                response_bytes = _stage_completed_receipt(
                    decision,
                    effect=effect,
                    session_digest=session_digest,
                    request=locked_request,
                )
            elif decision.kind == "replay":
                response_bytes = _validated_stored_response(decision)
            elif decision.kind == "conflict":
                return _error(
                    409,
                    "idempotency_key_conflict",
                    "Idempotency-Key conflicts with a prior request.",
                )
            elif decision.kind == "legacy_receipt_not_replayable":
                return _error(
                    409,
                    "legacy_receipt_not_replayable",
                    "The prior receipt needs staff review.",
                )
            elif decision.kind == "in_progress_not_replayable":
                return _error(
                    409,
                    "idempotency_key_in_progress",
                    "The prior request is still in progress.",
                )
            else:
                return _error(
                    503,
                    "receipt_integrity_failure",
                    "The stored result is unavailable.",
                )
        if response_bytes is None:
            raise _ReceiptCompositionFailed("transaction produced no stored response")
        public_bytes = canonical_delete_confirm_envelope_bytes(
            delete_confirm_envelope_projection(response_bytes)
        )
        return DeleteConfirmCompositionResult(
            "replay" if decision.kind == "replay" else "committed",
            200,
            json.loads(public_bytes),
            response_bytes,
        )
    except _LockedAdmissionStopped as exc:
        return _map_admission_stop(exc.admission)
    except DeleteConfirmAuthorityRevoked:
        return _error(403, "current_authority_unavailable", "Current authority is unavailable.")
    except DeleteConfirmTargetUnavailable:
        return _error(404, "appointment_not_found", "The appointment is unavailable.")
    except (
        DeleteConfirmScaffoldIncomplete,
        DeleteConfirmWaitBudgetExhausted,
        _ReceiptCompositionFailed,
        DeleteConfirmPhysicalError,
        TypeError,
        ValueError,
        AttributeError,
        KeyError,
    ):
        return _error(
            503,
            "delete_confirm_transaction_unavailable",
            "The delete confirmation did not commit.",
        )


__all__ = [
    "DELETE_CONFIRM_AUDIT_LABELS",
    "DELETE_CONFIRM_INTENT",
    "DELETE_CONFIRM_KERNEL_SCHEMA",
    "DELETE_CONFIRM_LOCK_PLAN",
    "DELETE_CONFIRM_OPERATION_ID",
    "DELETE_CONFIRM_PUBLIC_SCHEMA",
    "DELETE_CONFIRM_RECEIPT_SCHEMA",
    "DELETE_CONFIRM_ROUTE_FAMILY",
    "DELETE_CONFIRM_SUMMARY",
    "DELETE_CONFIRM_WARNING_CODES",
    "DELETE_CONFIRM_WARNING_REGISTRY",
    "DeleteConfirmCompositionResult",
    "DeleteConfirmEffectResult",
    "DeleteConfirmServerIngress",
    "canonical_delete_confirm_envelope_bytes",
    "compose_delete_confirm",
    "delete_confirm_envelope_projection",
    "validate_delete_confirm_private_receipt_bytes",
]
