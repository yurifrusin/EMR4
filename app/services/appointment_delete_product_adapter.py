"""Unmounted application-owned adapter for the delete-confirm composition."""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import uuid
from contextlib import closing, contextmanager
from typing import Any, Callable, Mapping

from app.models.appointments import (
    AppointmentAuditAction,
    AppointmentAuditLog,
    AppointmentStatus,
)
from app.models.tenancy import User, UserRole
from app.schemas.appointments import (
    AppointmentDeleteProposalConfirmationIn,
    AppointmentDeleteProposalOut,
)
from app.services.appointment_delete_composition import (
    DELETE_CONFIRM_AUDIT_LABELS,
    DELETE_CONFIRM_INTENT,
    DELETE_CONFIRM_PUBLIC_SCHEMA,
    DeleteConfirmCompositionResult,
    DeleteConfirmEffectResult,
    DeleteConfirmServerIngress,
    compose_delete_confirm,
)
from app.services.appointment_delete_physical import (
    DELETE_CONFIRM_CANCELLATION_REASON_MAX,
    DELETE_CONFIRM_REASON_CODES,
    DELETE_CONFIRM_RECEIPT_VERSION,
    DeleteConfirmPhysicalDecision,
    delete_confirm_locked_transaction,
)
from app.services.bernie_turn_evidence import (
    SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
    verify_signed_confirmation_evidence,
)


DELETE_CONFIRM_OPERATION_ID = "confirmAppointmentDeleteProposal"
DELETE_CONFIRM_ROUTE_FAMILY = "delete-confirm"
DELETE_CONFIRM_EVIDENCE_PURPOSE = SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE
DELETE_PROPOSAL_VERSION_BINDING_SCHEMA = "raisa.delete_proposal_version_binding.v1"
DELETE_CONFIRM_LOCK_PLAN = ["user", "appointment", "idempotency_record"]
DELETE_SESSION_REFERENCE_DOMAIN = b"appointment-delete-session-reference:v1"
MUTATING_ROLES = {
    UserRole.Receptionist,
    UserRole.GP,
    UserRole.Nurse,
    UserRole.Admin,
    UserRole.PracticeOwner,
}

UserLoader = Callable[[Any, Any], Any]
TransactionFactory = Callable[..., Any]


class _DeleteConfirmProposalBlocked(RuntimeError):
    """Proposal-level admission failure that must map to a typed 200 blocked result."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _canonical_digest(value: Mapping[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _uuid_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None


def _length_frame(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError("session binding fields must be non-empty strings")
    encoded = value.encode("utf-8")
    if len(encoded) > 0xFFFFFFFF:
        raise ValueError("session binding field is too long")
    return len(encoded).to_bytes(4, "big") + encoded


def authenticated_session_reference(
    authenticated_bearer_token: str,
    *,
    secret: bytes,
    actor_id: Any,
    practice_id: Any,
) -> str:
    """Minimise one already-authenticated bearer value to a keyed reference.

    The reference is a domain-separated HMAC bound to the authenticated bearer,
    actor and practice; it is never the raw bearer value.
    """
    if (
        not isinstance(authenticated_bearer_token, str)
        or not authenticated_bearer_token
        or not authenticated_bearer_token.strip()
    ):
        raise ValueError("authenticated bearer token is required")
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("authenticated session secret must contain at least 32 bytes")
    if not actor_id or not practice_id:
        raise ValueError("actor and practice identity are required for the session reference")
    message = b"\x00".join(
        (
            DELETE_SESSION_REFERENCE_DOMAIN,
            _length_frame(authenticated_bearer_token),
            _length_frame(str(actor_id)),
            _length_frame(str(practice_id)),
        )
    )
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _require_hmac_secret(secret: bytes, *, label: str) -> bytes:
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError(f"{label} must contain at least 32 bytes")
    return secret


def _require_evidence_secret(secret: str) -> str:
    if not isinstance(secret, str) or len(secret) < 32:
        raise ValueError("signed evidence secret must contain at least 32 characters")
    return secret


def _proposal_version_material(*, evidence_signature: str, source_version: int) -> dict[str, Any]:
    """Return exactly the two HMAC-covered proposal-version fields.

    ``schema_version`` is intentionally excluded from signature material; it is
    carried only in the returned envelope and the exact shape check.
    """
    if not isinstance(evidence_signature, str) or len(evidence_signature) != 64:
        raise ValueError("signed evidence signature is invalid")
    if isinstance(source_version, bool) or not isinstance(source_version, int) or source_version < 1:
        raise ValueError("proposal source version is invalid")
    return {
        "source_version": source_version,
        "evidence_signature": evidence_signature,
    }


def mint_delete_proposal_version_binding(
    signed_confirmation_evidence: Mapping[str, Any],
    *,
    source_version: int,
    secret: bytes,
) -> dict[str, Any]:
    """Mint an opaque binding between one signed proposal and its source version."""
    material = _proposal_version_material(
        evidence_signature=signed_confirmation_evidence.get("signature"),
        source_version=source_version,
    )
    digest = hmac.new(
        _require_hmac_secret(secret, label="proposal version secret"),
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "schema_version": DELETE_PROPOSAL_VERSION_BINDING_SCHEMA,
        **material,
        "signature": digest,
    }


def verify_delete_proposal_version_binding(
    value: Mapping[str, Any],
    *,
    signed_confirmation_evidence: Mapping[str, Any],
    secret: bytes,
) -> int:
    """Return the bound positive source version or fail closed."""
    if not isinstance(value, Mapping) or set(value) != {
        "schema_version",
        "source_version",
        "evidence_signature",
        "signature",
    }:
        raise ValueError("proposal version binding shape is invalid")
    if value.get("schema_version") != DELETE_PROPOSAL_VERSION_BINDING_SCHEMA:
        raise ValueError("proposal version binding schema is invalid")
    material = _proposal_version_material(
        evidence_signature=value.get("evidence_signature"),
        source_version=value.get("source_version"),
    )
    if material["evidence_signature"] != signed_confirmation_evidence.get("signature"):
        raise ValueError("proposal version binding evidence mismatch")
    signature = value.get("signature")
    if not isinstance(signature, str) or len(signature) != 64:
        raise ValueError("proposal version binding signature is invalid")
    expected = hmac.new(
        _require_hmac_secret(secret, label="proposal version secret"),
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("proposal version binding signature does not verify")
    return material["source_version"]


def delete_command_payload(command: Any) -> dict[str, Any]:
    if command.__class__.__name__ != "AppointmentDeleteCommand":
        raise ValueError("only AppointmentDeleteCommand is supported")
    return {
        "kind": "delete",
        "appointment_id": str(command.appointment_id),
        "clears_waiting_area": bool(command.clears_waiting_area),
        "cancellation_reason": command.cancellation_reason,
        "status_reason_code": command.status_reason_code,
    }


def appointment_delete_state(appointment: Any) -> dict[str, Any]:
    source_version = getattr(appointment, "appointment_state_version", None)
    if isinstance(source_version, bool) or not isinstance(source_version, int) or source_version < 1:
        raise ValueError("appointment state version is invalid")
    return {
        "appointment_id": str(appointment.id),
        "status": _enum_value(appointment.status),
        "status_reason_code": getattr(appointment, "status_reason_code", None),
        "waiting_area_id": _uuid_or_none(getattr(appointment, "waiting_area_id", None)),
        "cancellation_reason": getattr(appointment, "cancellation_reason", None),
        "source_version": source_version,
    }


def delete_proposal_freshness_id(command: Any, current_state: Mapping[str, Any]) -> str:
    payload = {
        "kind": "delete_proposal_v1",
        "current_state": {
            key: current_state[key]
            for key in ("appointment_id", "status", "waiting_area_id", "status_reason_code", "cancellation_reason")
        },
        "command": delete_command_payload(command),
    }
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def delete_signed_confirmation_payload(
    *,
    practice_id: Any,
    actor_id: Any,
    command: Any,
    current_state: Mapping[str, Any],
    freshness_id: str,
) -> dict[str, Any]:
    return {
        "practice_id": str(practice_id),
        "staff_user_id": str(actor_id),
        "current_state": {
            key: current_state[key]
            for key in ("appointment_id", "status", "waiting_area_id", "status_reason_code", "cancellation_reason")
        },
        "command": delete_command_payload(command),
        "delete_proposal_freshness_id": freshness_id,
    }


def required_warning_codes(
    current_state: Mapping[str, Any],
    command: Mapping[str, Any],
) -> list[str]:
    warnings: list[str] = []
    if current_state["waiting_area_id"] is not None:
        warnings.append("waiting_area_cleared")
    return sorted(warnings)


def _stop(reason: str, outcome: str = "validation_rejected") -> dict[str, Any]:
    return {
        "kind": "stopped",
        "outcome": outcome,
        "reason": reason,
        "kernel_request": None,
        "effect_authority": False,
    }


def delete_confirm_admission_adapter(value: Mapping[str, Any]) -> dict[str, Any]:
    """Admit an exact delete-only product request or return a typed stop."""
    try:
        if value.get("structure") != "valid":
            return _stop("structure_invalid")
        transport = value["transport"]
        server = value["server"]
        command = transport["command"]
        current = server["current_state"]
        if (
            transport["operation_id"] != DELETE_CONFIRM_OPERATION_ID
            or transport["route_family"] != DELETE_CONFIRM_ROUTE_FAMILY
        ):
            return _stop("operation_binding_mismatch")
        if transport["proposal_intent"] != "delete_appointment" or command["kind"] != "delete":
            return _stop("unsupported_delete_confirm_variant")
        if not isinstance(transport["idempotency_key"], str) or not transport["idempotency_key"].strip():
            return _stop("idempotency_key_required", "idempotency_conflict")
        if not server["authority_current"]:
            return _stop("current_authority_revoked", "authority_revoked")
        session_id = server["session_id"]
        if (
            not isinstance(session_id, str)
            or len(session_id) != 64
            or session_id != session_id.lower()
        ):
            return _stop("server_session_binding_required")
        try:
            bytes.fromhex(session_id)
        except ValueError:
            return _stop("server_session_binding_required")
        if transport["confirmed"] is not True:
            return _stop("explicit_confirmation_required", "confirmation_required")
        if (
            not transport["proposal_safe"]
            or not transport["requires_confirmation"]
            or transport["autonomy_tier"] not in {"proposal"}
        ):
            return _stop("delete_proposal_not_safe")
        if (
            not transport["signed_evidence_required"]
            or server["evidence_status"] != "verified"
            or server["evidence_purpose"] != DELETE_CONFIRM_EVIDENCE_PURPOSE
            or server["expected_evidence_purpose"] != DELETE_CONFIRM_EVIDENCE_PURPOSE
            or server["evidence_binding"] != "exact"
        ):
            return _stop("signed_confirmation_evidence_invalid", "confirmation_required")
        if transport["freshness_id"] != server["expected_freshness_id"]:
            return _stop("stale_delete_proposal_freshness_id", "stale_precondition")
        if command["appointment_id"] != current["appointment_id"]:
            return _stop("current_target_mismatch", "stale_precondition")
        if (
            isinstance(current["source_version"], bool)
            or not isinstance(current["source_version"], int)
            or current["source_version"] < 1
        ):
            return _stop("current_source_version_invalid", "stale_precondition")
        if current["status"] == "Cancelled":
            return _stop("already_cancelled", "stale_precondition")
        if command["status_reason_code"] not in DELETE_CONFIRM_REASON_CODES:
            return _stop("reason_code_not_dedicated")
        if (
            command["cancellation_reason"] is not None
            and (
                not isinstance(command["cancellation_reason"], str)
                or len(command["cancellation_reason"]) > DELETE_CONFIRM_CANCELLATION_REASON_MAX
            )
        ):
            return _stop("cancellation_reason_invalid")
        expected_clear = current["waiting_area_id"] is not None
        if bool(command["clears_waiting_area"]) != expected_clear:
            return _stop("waiting_area_clear_flag_mismatch", "stale_precondition")
        proposed = transport["proposal_warning_codes"]
        confirmed = transport["confirmed_warning_codes"]
        required = required_warning_codes(current, command)
        if (
            not isinstance(proposed, list)
            or not isinstance(confirmed, list)
            or len(proposed) != len(set(proposed))
            or len(confirmed) != len(set(confirmed))
            or sorted(proposed) != required
            or sorted(confirmed) != required
        ):
            return _stop("warning_acknowledgement_mismatch", "confirmation_required")
        authority_generation = server["authority_generation"]
        if (
            isinstance(authority_generation, bool)
            or not isinstance(authority_generation, int)
            or authority_generation < 1
        ):
            return _stop("server_authority_generation_invalid", "authority_revoked")
        request = {
            "schema_version": "raisa.delete_kernel_request.v1",
            "operation_id": transport["operation_id"],
            "route_family": transport["route_family"],
            "practice_id": server["practice_id"],
            "actor_id": server["actor_id"],
            "actor_role": server["actor_role"],
            "authority_generation": authority_generation,
            "session_id": server["session_id"],
            "idempotency_key": transport["idempotency_key"].strip(),
            "target_appointment_id": command["appointment_id"],
            "source_version": current["source_version"],
            "command": dict(command),
            "warning_codes": required,
            "lock_plan": list(DELETE_CONFIRM_LOCK_PLAN),
            "signed_evidence_binding_digest": _canonical_digest(
                {
                    "purpose": server["evidence_purpose"],
                    "binding": server["evidence_binding"],
                }
            ),
            "effect_authority": False,
        }
        request["request_digest"] = _canonical_digest(request)
        return {
            "kind": "kernel_request_ready",
            "outcome": None,
            "reason": None,
            "kernel_request": request,
            "effect_authority": False,
        }
    except (AttributeError, KeyError, TypeError, ValueError):
        return _stop("admission_input_invalid")


def _transport(
    body: AppointmentDeleteProposalConfirmationIn,
    *,
    idempotency_key: str,
) -> dict[str, Any]:
    proposal = body.delete_proposal
    if not isinstance(proposal, AppointmentDeleteProposalOut):
        raise _DeleteConfirmProposalBlocked("unsupported_delete_confirm_variant")
    if proposal.blocks:
        raise _DeleteConfirmProposalBlocked("delete_proposal_not_safe")
    if (
        proposal.signed_confirmation_evidence_required is not True
        or body.signed_confirmation_evidence_required is not True
    ):
        raise _DeleteConfirmProposalBlocked("signed_confirmation_evidence_invalid")
    return {
        "operation_id": DELETE_CONFIRM_OPERATION_ID,
        "route_family": DELETE_CONFIRM_ROUTE_FAMILY,
        "idempotency_key": idempotency_key,
        "confirmed": body.confirmed,
        "proposal_intent": proposal.intent,
        "proposal_safe": proposal.safe,
        "requires_confirmation": proposal.requires_confirmation,
        "autonomy_tier": proposal.autonomy_tier,
        "command": delete_command_payload(proposal.command),
        "proposal_warning_codes": [issue.code for issue in proposal.warnings],
        "confirmed_warning_codes": list(body.confirmed_warnings),
        "freshness_id": body.delete_proposal_freshness_id or proposal.delete_proposal_freshness_id,
        "signed_evidence_required": True,
    }


def _verified_proposal_state(
    *,
    body: AppointmentDeleteProposalConfirmationIn,
    authenticated_user: User,
    evidence_secret: str,
    proposal_version_binding: Mapping[str, Any],
    proposal_version_binding_secret: bytes,
) -> tuple[dict[str, Any], str, str, str]:
    """Return ``(current_state, freshness_id, evidence_status, evidence_binding)``.

    Structural proposal defects raise ``_DeleteConfirmProposalBlocked``. Evidence
    and proposal-generation binding failures are reflected in the returned
    status/binding fields so the pre-command admission adapter can issue the
    exact typed blocked stop before any command session is opened.
    """
    proposal = body.delete_proposal
    if not isinstance(proposal, AppointmentDeleteProposalOut):
        raise _DeleteConfirmProposalBlocked("unsupported_delete_confirm_variant")
    evidence = body.signed_confirmation_evidence
    if not isinstance(evidence, Mapping):
        raise _DeleteConfirmProposalBlocked("signed_confirmation_evidence_invalid")
    payload = evidence.get("payload")
    if not isinstance(payload, Mapping):
        raise _DeleteConfirmProposalBlocked("signed_confirmation_evidence_invalid")
    signed_state = payload.get("current_state")
    required_state_keys = {
        "appointment_id",
        "status",
        "waiting_area_id",
        "status_reason_code",
        "cancellation_reason",
    }
    if not isinstance(signed_state, Mapping) or set(signed_state) != required_state_keys:
        raise _DeleteConfirmProposalBlocked("signed_confirmation_evidence_invalid")
    try:
        source_version = verify_delete_proposal_version_binding(
            proposal_version_binding,
            signed_confirmation_evidence=evidence,
            secret=proposal_version_binding_secret,
        )
        binding_verified = True
    except ValueError:
        source_version = None
        binding_verified = False
    current_state = {key: signed_state[key] for key in sorted(required_state_keys)}
    current_state["source_version"] = source_version
    freshness_id = delete_proposal_freshness_id(proposal.command, current_state)
    expected_payload = delete_signed_confirmation_payload(
        practice_id=authenticated_user.practice_id,
        actor_id=authenticated_user.id,
        command=proposal.command,
        current_state=current_state,
        freshness_id=freshness_id,
    )
    result = verify_signed_confirmation_evidence(
        dict(evidence),
        expected_payload,
        expected_purpose=DELETE_CONFIRM_EVIDENCE_PURPOSE,
        secret=_require_evidence_secret(evidence_secret),
    )
    if proposal.signed_confirmation_evidence not in (None, dict(evidence)):
        raise _DeleteConfirmProposalBlocked("signed_confirmation_evidence_invalid")
    if result.verified and binding_verified:
        return current_state, freshness_id, "verified", "exact"
    if not result.verified:
        return current_state, freshness_id, result.code, "invalid"
    return current_state, freshness_id, "signed_evidence_binding_invalid", "invalid"


def _proposal_server_ingress(
    *,
    body: AppointmentDeleteProposalConfirmationIn,
    authenticated_user: User,
    session_reference: str,
    evidence_secret: str,
    proposal_version_binding: Mapping[str, Any],
    proposal_version_binding_secret: bytes,
) -> DeleteConfirmServerIngress:
    (
        current_state,
        freshness_id,
        evidence_status,
        evidence_binding,
    ) = _verified_proposal_state(
        body=body,
        authenticated_user=authenticated_user,
        evidence_secret=evidence_secret,
        proposal_version_binding=proposal_version_binding,
        proposal_version_binding_secret=proposal_version_binding_secret,
    )
    role = authenticated_user.role
    authority_generation = getattr(authenticated_user, "authority_generation", None)
    if (
        isinstance(authority_generation, bool)
        or not isinstance(authority_generation, int)
        or authority_generation < 1
    ):
        raise ValueError("authenticated authority generation is invalid")
    authority_current = bool(
        authenticated_user.is_active
        and role in MUTATING_ROLES
        and authority_generation >= 1
    )
    return DeleteConfirmServerIngress(
        practice_id=authenticated_user.practice_id,
        actor_id=authenticated_user.id,
        actor_role=_enum_value(role),
        authority_generation=authority_generation,
        session_id=session_reference,
        authority_current=authority_current,
        current_state=current_state,
        expected_freshness_id=freshness_id,
        evidence_status=evidence_status,
        evidence_purpose=DELETE_CONFIRM_EVIDENCE_PURPOSE,
        expected_evidence_purpose=DELETE_CONFIRM_EVIDENCE_PURPOSE,
        evidence_binding=evidence_binding,
    )


def _locked_server_ingress(
    *,
    body: AppointmentDeleteProposalConfirmationIn,
    authenticated_user: User,
    appointment: Any,
    session_reference: str,
    evidence_secret: str,
) -> DeleteConfirmServerIngress:
    proposal = body.delete_proposal
    if not isinstance(proposal, AppointmentDeleteProposalOut):
        raise ValueError("only AppointmentDeleteProposalOut is supported")
    current_state = appointment_delete_state(appointment)
    freshness_id = delete_proposal_freshness_id(proposal.command, current_state)
    expected_payload = delete_signed_confirmation_payload(
        practice_id=authenticated_user.practice_id,
        actor_id=authenticated_user.id,
        command=proposal.command,
        current_state=current_state,
        freshness_id=freshness_id,
    )
    evidence = verify_signed_confirmation_evidence(
        body.signed_confirmation_evidence,
        expected_payload,
        expected_purpose=DELETE_CONFIRM_EVIDENCE_PURPOSE,
        secret=_require_evidence_secret(evidence_secret),
    )
    role = authenticated_user.role
    authority_generation = getattr(authenticated_user, "authority_generation", None)
    if (
        isinstance(authority_generation, bool)
        or not isinstance(authority_generation, int)
        or authority_generation < 1
    ):
        raise ValueError("authenticated authority generation is invalid")
    authority_current = bool(
        authenticated_user.is_active
        and role in MUTATING_ROLES
        and authority_generation >= 1
        and authenticated_user.practice_id == appointment.practice_id
    )
    return DeleteConfirmServerIngress(
        practice_id=authenticated_user.practice_id,
        actor_id=authenticated_user.id,
        actor_role=_enum_value(role),
        authority_generation=authority_generation,
        session_id=session_reference,
        authority_current=authority_current,
        current_state=current_state,
        expected_freshness_id=freshness_id,
        evidence_status="verified" if evidence.verified else evidence.code,
        evidence_purpose=DELETE_CONFIRM_EVIDENCE_PURPOSE,
        expected_evidence_purpose=DELETE_CONFIRM_EVIDENCE_PURPOSE,
        evidence_binding="exact" if evidence.verified else "invalid",
    )


def _locked_server_factory(
    *,
    body: AppointmentDeleteProposalConfirmationIn,
    authenticated_user: User,
    evidence_secret: str,
) -> Callable[[Any, DeleteConfirmServerIngress], Mapping[str, Any]]:
    def build(appointment: Any, ingress: DeleteConfirmServerIngress) -> Mapping[str, Any]:
        return _locked_server_ingress(
            body=body,
            authenticated_user=authenticated_user,
            appointment=appointment,
            session_reference=ingress.session_id,
            evidence_secret=evidence_secret,
        ).as_adapter_mapping()

    return build


def _stage_effect(
    *,
    db: Any,
    body: AppointmentDeleteProposalConfirmationIn,
    authenticated_user: User,
    session_reference: str,
) -> Callable[[DeleteConfirmPhysicalDecision, Mapping[str, Any]], DeleteConfirmEffectResult]:
    def stage(
        decision: DeleteConfirmPhysicalDecision,
        request: Mapping[str, Any],
    ) -> DeleteConfirmEffectResult:
        appointment = decision.appointment
        command = request["command"]
        if (
            str(appointment.id) != request["target_appointment_id"]
            or appointment.practice_id != authenticated_user.practice_id
            or str(authenticated_user.id) != request["actor_id"]
            or str(authenticated_user.practice_id) != request["practice_id"]
            or request["session_id"] != session_reference
            or not isinstance(decision.record.id, uuid.UUID)
        ):
            raise ValueError("locked effect binding mismatch")
        status_before = appointment.status
        waiting_area_before_id = appointment.waiting_area_id
        appointment.status = AppointmentStatus.Cancelled
        appointment.waiting_area_id = None
        appointment.cancellation_reason = command["cancellation_reason"]
        appointment.status_reason_code = command["status_reason_code"]
        audit = AppointmentAuditLog(
            id=uuid.uuid4(),
            practice_id=authenticated_user.practice_id,
            appointment_id=appointment.id,
            confirmed_by_user_id=authenticated_user.id,
            action=AppointmentAuditAction.delete,
            status_before=status_before,
            status_after=AppointmentStatus.Cancelled,
            cancellation_reason=command["cancellation_reason"],
            status_reason_code=command["status_reason_code"],
            confirmed_warnings=list(request["warning_codes"]),
            command_id=decision.record.id,
            bernie_session_id=session_reference,
            audit_contract_version=DELETE_CONFIRM_RECEIPT_VERSION,
            authority_generation=request["authority_generation"],
            pre_state_version=decision.pre_state_version,
            post_state_version=decision.pre_state_version + 1,
            waiting_area_before_id=waiting_area_before_id,
            waiting_area_after_id=None,
            audit_evidence_codes=list(DELETE_CONFIRM_AUDIT_LABELS),
        )
        decision.record.bernie_session_id = session_reference
        db.add(audit)
        db.flush()
        db.refresh(appointment)
        if appointment.appointment_state_version != decision.pre_state_version + 1:
            raise ValueError("database-owned adjacent appointment version missing")
        return DeleteConfirmEffectResult(audit_log_id=audit.id)

    return stage


def _uuid_bound_transaction_factory(
    transaction_factory: TransactionFactory,
) -> TransactionFactory:
    @contextmanager
    def enter(db: Any, **arguments: Any):
        target = arguments.get("target_appointment_id")
        if isinstance(target, str):
            target = uuid.UUID(target)
        if not isinstance(target, uuid.UUID):
            raise ValueError("physical target appointment id is invalid")
        exact_arguments = {**arguments, "target_appointment_id": target}
        with transaction_factory(db, **exact_arguments) as decision:
            yield decision

    return enter


def _blocked(reason: str) -> DeleteConfirmCompositionResult:
    body = {
        "schema_version": DELETE_CONFIRM_PUBLIC_SCHEMA,
        "intent": DELETE_CONFIRM_INTENT,
        "safe": False,
        "requires_confirmation": True,
        "autonomy_tier": "blocked",
        "summary": "Cannot confirm delete proposal. See blocked issues.",
        "receipt": None,
        "warnings": [],
        "blocks": [
            {
                "code": reason,
                "severity": "blocked",
                "message": "Delete confirmation stopped.",
            }
        ],
        "audit_evidence": [],
    }
    return DeleteConfirmCompositionResult("blocked", 200, body)


def _error(status_code: int, code: str) -> DeleteConfirmCompositionResult:
    return DeleteConfirmCompositionResult(
        "error",
        status_code,
        {"detail": {"code": code, "message": "Delete confirmation is unavailable."}},
    )


def _map_admission_stop(admission: Mapping[str, Any]) -> DeleteConfirmCompositionResult:
    outcome = admission.get("outcome")
    reason = str(admission.get("reason") or "validation_rejected")
    if outcome == "authority_revoked":
        return _error(403, "current_authority_unavailable")
    if outcome == "idempotency_conflict":
        return _error(409, "idempotency_key_required")
    return _blocked(reason)


def compose_product_delete_confirm(
    body: AppointmentDeleteProposalConfirmationIn,
    *,
    authenticated_user: User,
    authenticated_bearer_token: str,
    idempotency_key: str,
    proposal_version_binding: Mapping[str, Any],
    command_session_factory: Callable[[], Any],
    authenticated_session_secret: bytes,
    proposal_version_binding_secret: bytes,
    idempotency_secret: bytes,
    session_binding_secret: bytes,
    evidence_secret: str,
    transaction_factory: TransactionFactory = delete_confirm_locked_transaction,
) -> DeleteConfirmCompositionResult:
    """Compose one delete-only product confirmation without mounting a route."""
    if not isinstance(body.delete_proposal, AppointmentDeleteProposalOut):
        return _blocked("unsupported_delete_confirm_variant")

    # ---- Stage A: server-owned secrets, bearer minimization and identity ----
    try:
        _require_hmac_secret(idempotency_secret, label="idempotency secret")
        _require_hmac_secret(session_binding_secret, label="session binding secret")
        _require_hmac_secret(
            proposal_version_binding_secret, label="proposal version binding secret"
        )
        _require_evidence_secret(evidence_secret)
        if authenticated_user is None:
            raise ValueError("authenticated user identity is missing")
        authority_generation = getattr(
            authenticated_user, "authority_generation", None
        )
        if (
            isinstance(authority_generation, bool)
            or not isinstance(authority_generation, int)
            or authority_generation < 1
        ):
            raise ValueError("authenticated authority generation is invalid")
        if not authenticated_user.is_active:
            raise ValueError("authenticated user is inactive")
        if authenticated_user.role not in MUTATING_ROLES:
            raise ValueError("authenticated role is not admitted")
        session_reference = authenticated_session_reference(
            authenticated_bearer_token,
            secret=authenticated_session_secret,
            actor_id=authenticated_user.id,
            practice_id=authenticated_user.practice_id,
        )
    except (AttributeError, TypeError, ValueError):
        return _error(403, "authenticated_delete_context_unavailable")

    # ---- Stage B: idempotency key presence ----
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        return _error(409, "idempotency_key_required")

    # ---- Stage C: transport and pre-command ingress ----
    try:
        transport = _transport(body, idempotency_key=idempotency_key)
        ingress = _proposal_server_ingress(
            body=body,
            authenticated_user=authenticated_user,
            session_reference=session_reference,
            evidence_secret=evidence_secret,
            proposal_version_binding=proposal_version_binding,
            proposal_version_binding_secret=proposal_version_binding_secret,
        )
    except _DeleteConfirmProposalBlocked as exc:
        return _blocked(exc.reason)
    except (AttributeError, TypeError, ValueError):
        return _blocked("unsupported_delete_confirm_variant")

    # ---- Stage D: pre-command admission gate ----
    adapter_input = {
        "structure": "valid",
        "transport": copy.deepcopy(dict(transport)),
        "server": ingress.as_adapter_mapping(),
    }
    try:
        admission = delete_confirm_admission_adapter(adapter_input)
    except (AttributeError, KeyError, TypeError, ValueError):
        return _blocked("admission_input_invalid")
    if admission.get("kind") != "kernel_request_ready":
        return _map_admission_stop(admission)

    # ---- Stage E: open the command session and compose ----
    try:
        command_db = command_session_factory()
    except Exception:
        return _error(503, "delete_confirm_transaction_unavailable")
    with closing(command_db):
        return compose_delete_confirm(
            transport,
            server_ingress=ingress,
            db=command_db,
            idempotency_secret=idempotency_secret,
            session_binding_secret=session_binding_secret,
            admission_adapter=delete_confirm_admission_adapter,
            locked_server_factory=_locked_server_factory(
                body=body,
                authenticated_user=authenticated_user,
                evidence_secret=evidence_secret,
            ),
            stage_effect=_stage_effect(
                db=command_db,
                body=body,
                authenticated_user=authenticated_user,
                session_reference=session_reference,
            ),
            transaction_factory=_uuid_bound_transaction_factory(transaction_factory),
        )


__all__ = [
    "DELETE_CONFIRM_EVIDENCE_PURPOSE",
    "DELETE_CONFIRM_OPERATION_ID",
    "DELETE_CONFIRM_ROUTE_FAMILY",
    "DELETE_PROPOSAL_VERSION_BINDING_SCHEMA",
    "appointment_delete_state",
    "authenticated_session_reference",
    "compose_product_delete_confirm",
    "delete_command_payload",
    "delete_confirm_admission_adapter",
    "delete_proposal_freshness_id",
    "delete_signed_confirmation_payload",
    "mint_delete_proposal_version_binding",
    "required_warning_codes",
    "verify_delete_proposal_version_binding",
]
