"""Unmounted composition boundary for a future status-confirm route convergence.

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

from app.schemas.appointments import AppointmentConfirmStatusProposalOut
from app.services.appointment_idempotency import hash_idempotency_key
from app.services.appointment_status_physical import (
    STATUS_CONFIRM_RECEIPT_VERSION,
    StatusConfirmAuthorityRevoked,
    StatusConfirmPhysicalDecision,
    StatusConfirmPhysicalError,
    StatusConfirmScaffoldIncomplete,
    StatusConfirmTargetUnavailable,
    status_confirm_locked_transaction,
    status_confirm_response_digest,
    status_confirm_response_integrity_valid,
    status_confirm_session_binding_digest,
)


AdmissionAdapter = Callable[[dict[str, Any]], dict[str, Any]]
LockedServerFactory = Callable[[Any, "StatusConfirmServerIngress"], Mapping[str, Any]]
TransactionFactory = Callable[..., ContextManager[StatusConfirmPhysicalDecision]]


@dataclass(frozen=True)
class StatusConfirmServerIngress:
    """Facts owned by authenticated server/session and current-state services."""

    practice_id: UUID | str
    actor_id: UUID | str
    actor_role: str
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
class StatusConfirmEffectResult:
    """The staged atomic effect returned by the injected status-only kernel."""

    public_response: Mapping[str, Any]
    audit_log_id: UUID | str


@dataclass(frozen=True)
class StatusConfirmCompositionResult:
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


def canonical_status_confirm_envelope_bytes(
    response_body: Mapping[str, Any],
) -> bytes:
    """Validate and canonically serialize the complete current public envelope."""
    if not isinstance(response_body, Mapping):
        raise ValueError("status-confirm response must be a mapping")
    supplied = copy.deepcopy(dict(response_body))
    model = AppointmentConfirmStatusProposalOut.model_validate(supplied)
    normalized = model.model_dump(mode="json")
    if supplied != normalized:
        raise ValueError("status-confirm response must contain the exact complete envelope")
    if (
        normalized["safe"] is not True
        or normalized["requires_confirmation"] is not False
        or normalized["autonomy_tier"] != "confirmed_write"
        or normalized["appointment"] is None
        or normalized["blocks"]
    ):
        raise ValueError("stored status-confirm receipt must be a successful write")
    warning_codes = [item["code"] for item in normalized["warnings"]]
    if len(warning_codes) != len(set(warning_codes)):
        raise ValueError("stored status-confirm warning codes must be unique")
    if any(item["severity"] != "warning" for item in normalized["warnings"]):
        raise ValueError("stored status-confirm warnings must have warning severity")
    raw = json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if json.loads(raw) != normalized:
        raise AssertionError("canonical response does not round-trip")
    return raw


def status_confirm_envelope_projection(response_bytes: bytes) -> dict[str, Any]:
    """Return the five status fields as a validated projection, never a response."""
    try:
        payload = json.loads(response_bytes)
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("stored status-confirm response is not valid UTF-8 JSON") from exc
    canonical = canonical_status_confirm_envelope_bytes(payload)
    if canonical != response_bytes:
        raise ValueError("stored status-confirm response is not canonical")
    appointment = payload["appointment"]
    return {
        "appointment_id": appointment["id"],
        "status": appointment["status"],
        "status_reason_code": appointment["status_reason_code"],
        "waiting_area_id": appointment["waiting_area_id"],
        "warning_codes": [item["code"] for item in payload["warnings"]],
    }


def _blocked(reason: str) -> StatusConfirmCompositionResult:
    body = {
        "intent": "confirm_status_appointment",
        "safe": False,
        "requires_confirmation": True,
        "autonomy_tier": "blocked",
        "summary": "Status confirmation was blocked.",
        "appointment": None,
        "warnings": [],
        "blocks": [
            {
                "code": reason,
                "severity": "blocked",
                "message": "The status confirmation did not pass current checks.",
            }
        ],
        "audit_evidence": [],
    }
    AppointmentConfirmStatusProposalOut.model_validate(body)
    return StatusConfirmCompositionResult("blocked", 200, body)


def _error(status_code: int, code: str, message: str) -> StatusConfirmCompositionResult:
    return StatusConfirmCompositionResult(
        "error",
        status_code,
        {"detail": {"code": code, "message": message}},
    )


def _map_admission_stop(admission: Mapping[str, Any]) -> StatusConfirmCompositionResult:
    outcome = admission.get("outcome")
    reason = str(admission.get("reason") or "validation_rejected")
    if outcome == "authority_revoked":
        return _error(403, "current_authority_unavailable", "Current authority is unavailable.")
    if outcome == "idempotency_conflict":
        return _error(409, "idempotency_key_required", "A valid Idempotency-Key is required.")
    return _blocked(reason)


def _validate_ready_request(
    admission: Mapping[str, Any],
    ingress: StatusConfirmServerIngress,
) -> dict[str, Any]:
    if admission.get("kind") != "kernel_request_ready":
        raise ValueError("admission result is not kernel-request ready")
    request = admission.get("kernel_request")
    if not isinstance(request, dict) or admission.get("effect_authority") is not False:
        raise ValueError("admission result has an invalid effect boundary")
    expected = {
        "operation_id": "confirmAppointmentStatusProposal",
        "route_family": "status-confirm",
        "practice_id": str(ingress.practice_id),
        "actor_id": str(ingress.actor_id),
        "actor_role": ingress.actor_role,
        "session_id": ingress.session_id,
        "lock_plan": ["practice", "appointment", "idempotency_record"],
        "effect_authority": False,
    }
    for field, value in expected.items():
        if request.get(field) != value:
            raise ValueError(f"admitted request disagrees with server-owned {field}")
    if request.get("schema_version") != "raisa.status_kernel_request.v1":
        raise ValueError("admitted request schema version is invalid")
    command = request.get("command")
    if not isinstance(command, dict) or command.get("kind") != "status":
        raise ValueError("admitted request is not status-only")
    if set(command) != {
        "kind",
        "appointment_id",
        "status",
        "status_reason_code",
        "waiting_area_id",
        "waiting_area_id_supplied",
        "clears_waiting_area",
    }:
        raise ValueError("admitted status command fields are incomplete")
    if command.get("appointment_id") != request.get("target_appointment_id"):
        raise ValueError("admitted command target binding is invalid")
    if not isinstance(command.get("status"), str) or not command["status"]:
        raise ValueError("admitted status is invalid")
    if command["status_reason_code"] is not None and not isinstance(
        command["status_reason_code"], str
    ):
        raise ValueError("admitted status reason is invalid")
    if not isinstance(command["waiting_area_id_supplied"], bool) or not isinstance(
        command["clears_waiting_area"], bool
    ):
        raise ValueError("admitted waiting-area flags are invalid")
    source_version = request.get("source_version")
    if not isinstance(source_version, int) or isinstance(source_version, bool) or source_version < 1:
        raise ValueError("admitted source version is invalid")
    warnings = request.get("warning_codes")
    if (
        not isinstance(warnings, list)
        or any(not isinstance(code, str) or not code for code in warnings)
        or warnings != sorted(set(warnings))
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
    digest_payload = {key: value for key, value in request.items() if key != "request_digest"}
    expected_digest = hashlib.sha256(
        json.dumps(digest_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if digest != expected_digest:
        raise ValueError("admitted request digest does not bind the request")
    return request


def _stage_completed_receipt(
    decision: StatusConfirmPhysicalDecision,
    *,
    effect: StatusConfirmEffectResult,
    session_digest: bytes,
    request: Mapping[str, Any],
) -> bytes:
    try:
        response_bytes = canonical_status_confirm_envelope_bytes(effect.public_response)
        projection = status_confirm_envelope_projection(response_bytes)
    except (TypeError, ValueError) as exc:
        raise _ReceiptCompositionFailed("public response envelope is invalid") from exc
    if str(projection["appointment_id"]) != str(decision.appointment.id):
        raise _ReceiptCompositionFailed("public response target differs from locked target")
    appointment_status = (
        decision.appointment.status.value
        if hasattr(decision.appointment.status, "value")
        else decision.appointment.status
    )
    if str(projection["status"]) != str(appointment_status):
        raise _ReceiptCompositionFailed("public response status differs from staged status")
    appointment_reason = getattr(decision.appointment, "status_reason_code", None)
    if projection["status_reason_code"] != appointment_reason:
        raise _ReceiptCompositionFailed("public response reason differs from staged reason")
    appointment_waiting_area = getattr(decision.appointment, "waiting_area_id", None)
    if (
        str(projection["waiting_area_id"])
        if projection["waiting_area_id"] is not None
        else None
    ) != (
        str(appointment_waiting_area) if appointment_waiting_area is not None else None
    ):
        raise _ReceiptCompositionFailed(
            "public response waiting area differs from staged waiting area"
        )
    if projection["warning_codes"] != request["warning_codes"]:
        raise _ReceiptCompositionFailed(
            "public response warnings differ from locked admission"
        )
    appointment_practice_id = getattr(decision.appointment, "practice_id", None)
    if str(effect.public_response["appointment"]["practice_id"]) != str(
        appointment_practice_id
    ):
        raise _ReceiptCompositionFailed(
            "public response practice differs from locked appointment"
        )
    if not isinstance(effect.audit_log_id, (UUID, str)) or not str(effect.audit_log_id):
        raise _ReceiptCompositionFailed("status effect did not return an audit identity")
    record = decision.record
    record.state = "completed"
    record.response_status_code = 200
    record.response_body_json = json.loads(response_bytes)
    record.response_body_hash = status_confirm_response_digest(response_bytes)
    record.result_kind = "confirmed_write"
    record.target_appointment_id = decision.appointment.id
    record.audit_log_id = effect.audit_log_id
    record.completed_receipt_version = STATUS_CONFIRM_RECEIPT_VERSION
    record.session_binding_digest = session_digest
    record.pre_state_version = decision.pre_state_version
    record.post_state_version = decision.appointment.appointment_state_version
    record.response_body_canonical_bytes = response_bytes
    return response_bytes


def _validated_stored_response(decision: StatusConfirmPhysicalDecision) -> bytes:
    response_bytes = decision.response_body_canonical_bytes
    record = decision.record
    if not status_confirm_response_integrity_valid(response_bytes, record.response_body_hash):
        raise _ReceiptCompositionFailed("stored response integrity failed")
    if json.loads(response_bytes) != record.response_body_json:
        raise _ReceiptCompositionFailed("stored JSON and canonical bytes differ")
    status_confirm_envelope_projection(response_bytes)
    return response_bytes


def compose_status_confirm(
    transport: Mapping[str, Any],
    *,
    server_ingress: StatusConfirmServerIngress,
    db: Any,
    idempotency_secret: bytes,
    session_binding_secret: bytes,
    admission_adapter: AdmissionAdapter,
    locked_server_factory: LockedServerFactory,
    stage_effect: Callable[
        [StatusConfirmPhysicalDecision, Mapping[str, Any]], StatusConfirmEffectResult
    ],
    practice_is_active: Callable[[Any], bool],
    current_authority: Callable[[Any, Any], bool],
    lock_timeout_ms: int = 1000,
    transaction_factory: TransactionFactory = status_confirm_locked_transaction,
) -> StatusConfirmCompositionResult:
    """Compose the admitted status-only request without mounting the route."""
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
        session_digest = status_confirm_session_binding_digest(
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
            practice_is_active=practice_is_active,
            current_authority=current_authority,
            lock_timeout_ms=lock_timeout_ms,
        ) as decision:
            if decision.kind == "new_command":
                locked_input = {
                    "structure": "valid",
                    "transport": copy.deepcopy(dict(transport)),
                    "server": dict(locked_server_factory(decision.appointment, server_ingress)),
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
                if not isinstance(effect, StatusConfirmEffectResult):
                    raise _ReceiptCompositionFailed("status effect returned an invalid result")
                response_bytes = _stage_completed_receipt(
                    decision,
                    effect=effect,
                    session_digest=session_digest,
                    request=locked_request,
                )
            elif decision.kind == "replay":
                response_bytes = _validated_stored_response(decision)
            elif decision.kind == "conflict":
                return _error(409, "idempotency_key_conflict", "Idempotency-Key conflicts with a prior request.")
            elif decision.kind == "legacy_receipt_not_replayable":
                return _error(409, "legacy_receipt_not_replayable", "The prior receipt needs staff review.")
            elif decision.kind == "in_progress_not_replayable":
                return _error(409, "idempotency_key_in_progress", "The prior request is still in progress.")
            else:
                return _error(503, "receipt_integrity_failure", "The stored result is unavailable.")
        if response_bytes is None:
            raise _ReceiptCompositionFailed("transaction produced no stored response")
        return StatusConfirmCompositionResult(
            "replay" if decision.kind == "replay" else "committed",
            200,
            json.loads(response_bytes),
            response_bytes,
        )
    except _LockedAdmissionStopped as exc:
        return _map_admission_stop(exc.admission)
    except StatusConfirmAuthorityRevoked:
        return _error(403, "current_authority_unavailable", "Current authority is unavailable.")
    except StatusConfirmTargetUnavailable:
        return _error(404, "appointment_not_found", "The appointment is unavailable.")
    except (
        StatusConfirmScaffoldIncomplete,
        _ReceiptCompositionFailed,
        StatusConfirmPhysicalError,
        TypeError,
        ValueError,
        AttributeError,
        KeyError,
    ):
        return _error(503, "status_confirm_transaction_unavailable", "The status confirmation did not commit.")
