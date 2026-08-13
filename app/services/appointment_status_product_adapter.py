"""Unmounted application-owned adapter for the status-confirm composition."""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from contextlib import closing
from typing import Any, Callable, Mapping

from sqlalchemy import text

from app.models.appointments import (
    AppointmentAuditAction,
    AppointmentAuditLog,
    AppointmentStatus,
)
from app.models.tenancy import User, UserRole
from app.schemas.appointments import (
    AppointmentConfirmStatusProposalOut,
    AppointmentOut,
    AppointmentStatusProposalConfirmationIn,
    AppointmentStatusProposalOut,
)
from app.services.appointment_status_composition import (
    StatusConfirmCompositionResult,
    StatusConfirmEffectResult,
    StatusConfirmServerIngress,
    compose_status_confirm,
)
from app.services.appointment_status_physical import (
    StatusConfirmPhysicalDecision,
    status_confirm_locked_transaction,
)
from app.services.bernie_turn_evidence import (
    SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
    verify_signed_confirmation_evidence,
)


STATUS_CONFIRM_OPERATION_ID = "confirmAppointmentStatusProposal"
STATUS_CONFIRM_ROUTE_FAMILY = "status-confirm"
STATUS_CONFIRM_EVIDENCE_PURPOSE = SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE
PROPOSAL_VERSION_BINDING_SCHEMA = "raisa.status_proposal_version_binding.v1"
LOCK_PLAN = ["practice", "appointment", "idempotency_record"]
TERMINAL_STATUSES = {"Completed", "Cancelled", "DNA", "NoShow"}
MUTATING_ROLES = {
    UserRole.Receptionist,
    UserRole.GP,
    UserRole.Nurse,
    UserRole.Admin,
    UserRole.PracticeOwner,
}

UserLoader = Callable[[Any, Any], Any]
TransactionFactory = Callable[..., Any]


def _canonical_digest(value: Mapping[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _uuid_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None


def authenticated_session_reference(
    authenticated_bearer_token: str,
    *,
    secret: bytes,
) -> str:
    """Minimise one already-authenticated bearer value to a keyed reference."""
    if (
        not isinstance(authenticated_bearer_token, str)
        or not authenticated_bearer_token
        or not authenticated_bearer_token.strip()
    ):
        raise ValueError("authenticated bearer token is required")
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("authenticated session secret must contain at least 32 bytes")
    return hmac.new(secret, authenticated_bearer_token.encode("utf-8"), hashlib.sha256).hexdigest()


def _require_hmac_secret(secret: bytes, *, label: str) -> bytes:
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError(f"{label} must contain at least 32 bytes")
    return secret


def _require_evidence_secret(secret: str) -> str:
    if not isinstance(secret, str) or len(secret) < 32:
        raise ValueError("signed evidence secret must contain at least 32 characters")
    return secret


def _proposal_version_material(*, evidence_signature: str, source_version: int) -> dict[str, Any]:
    if not isinstance(evidence_signature, str) or len(evidence_signature) != 64:
        raise ValueError("signed evidence signature is invalid")
    if isinstance(source_version, bool) or not isinstance(source_version, int) or source_version < 1:
        raise ValueError("proposal source version is invalid")
    return {
        "schema_version": PROPOSAL_VERSION_BINDING_SCHEMA,
        "source_version": source_version,
        "evidence_signature": evidence_signature,
    }


def mint_status_proposal_version_binding(
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
    return {**material, "signature": digest}


def verify_status_proposal_version_binding(
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


def status_command_payload(command: Any) -> dict[str, Any]:
    if command.__class__.__name__ != "AppointmentStatusCommand":
        raise ValueError("only AppointmentStatusCommand is supported")
    return {
        "kind": "status",
        "appointment_id": str(command.appointment_id),
        "status": _enum_value(command.status),
        "status_reason_code": command.status_reason_code,
        "waiting_area_id": _uuid_or_none(command.waiting_area_id),
        "waiting_area_id_supplied": command.waiting_area_id_supplied,
        "clears_waiting_area": command.clears_waiting_area,
    }


def appointment_status_state(appointment: Any) -> dict[str, Any]:
    source_version = getattr(appointment, "appointment_state_version", None)
    if isinstance(source_version, bool) or not isinstance(source_version, int) or source_version < 1:
        raise ValueError("appointment state version is invalid")
    return {
        "appointment_id": str(appointment.id),
        "status": _enum_value(appointment.status),
        "status_reason_code": getattr(appointment, "status_reason_code", None),
        "waiting_area_id": _uuid_or_none(getattr(appointment, "waiting_area_id", None)),
        "source_version": source_version,
    }


def status_proposal_freshness_id(command: Any, current_state: Mapping[str, Any]) -> str:
    payload = {
        "kind": "status_proposal_v1",
        "current_state": {
            key: current_state[key]
            for key in ("appointment_id", "status", "waiting_area_id", "status_reason_code")
        },
        "command": status_command_payload(command),
    }
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def status_signed_confirmation_payload(
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
            for key in ("appointment_id", "status", "waiting_area_id", "status_reason_code")
        },
        "command": status_command_payload(command),
        "status_proposal_freshness_id": freshness_id,
    }


def required_warning_codes(
    current_state: Mapping[str, Any],
    command: Mapping[str, Any],
) -> list[str]:
    warnings: list[str] = []
    if (
        command["status"] in TERMINAL_STATUSES
        and current_state["waiting_area_id"] is not None
        and command["waiting_area_id"] is None
    ):
        warnings.append("waiting_area_cleared")
    if command["status"] in TERMINAL_STATUSES and command["waiting_area_id"] is not None:
        warnings.append("waiting_area_assigned_on_terminal")
    return sorted(warnings)


def _stop(reason: str, outcome: str = "validation_rejected") -> dict[str, Any]:
    return {
        "kind": "stopped",
        "outcome": outcome,
        "reason": reason,
        "kernel_request": None,
        "effect_authority": False,
    }


def status_confirm_admission_adapter(value: Mapping[str, Any]) -> dict[str, Any]:
    """Admit an exact status-only product request or return a typed stop."""
    try:
        if value.get("structure") != "valid":
            return _stop("structure_invalid")
        transport = value["transport"]
        server = value["server"]
        command = transport["command"]
        current = server["current_state"]
        if (
            transport["operation_id"] != STATUS_CONFIRM_OPERATION_ID
            or transport["route_family"] != STATUS_CONFIRM_ROUTE_FAMILY
        ):
            return _stop("operation_binding_mismatch")
        if transport["proposal_intent"] != "update_appointment_status" or command["kind"] != "status":
            return _stop("unsupported_status_confirm_variant")
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
            or transport["autonomy_tier"] not in {"proposal", "execute_with_report"}
        ):
            return _stop("status_proposal_not_safe")
        if (
            not transport["signed_evidence_required"]
            or server["evidence_status"] != "verified"
            or server["evidence_purpose"] != STATUS_CONFIRM_EVIDENCE_PURPOSE
            or server["expected_evidence_purpose"] != STATUS_CONFIRM_EVIDENCE_PURPOSE
            or server["evidence_binding"] != "exact"
        ):
            return _stop("signed_confirmation_evidence_invalid", "confirmation_required")
        if transport["freshness_id"] != server["expected_freshness_id"]:
            return _stop("stale_status_proposal_freshness_id", "stale_precondition")
        if command["appointment_id"] != current["appointment_id"]:
            return _stop("current_target_mismatch", "stale_precondition")
        if (
            isinstance(current["source_version"], bool)
            or not isinstance(current["source_version"], int)
            or current["source_version"] < 1
        ):
            return _stop("current_source_version_invalid", "stale_precondition")
        if command["status"] == current["status"]:
            return _stop("already_in_status", "stale_precondition")
        if current["status"] in TERMINAL_STATUSES:
            return _stop("transition_policy_deferred")
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
        request = {
            "schema_version": "raisa.status_kernel_request.v1",
            "operation_id": transport["operation_id"],
            "route_family": transport["route_family"],
            "practice_id": server["practice_id"],
            "actor_id": server["actor_id"],
            "actor_role": server["actor_role"],
            "session_id": server["session_id"],
            "idempotency_key": transport["idempotency_key"].strip(),
            "target_appointment_id": command["appointment_id"],
            "source_version": current["source_version"],
            "command": dict(command),
            "warning_codes": required,
            "lock_plan": list(LOCK_PLAN),
            "signed_evidence_binding_digest": _canonical_digest(
                {"purpose": server["evidence_purpose"], "binding": server["evidence_binding"]}
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
    body: AppointmentStatusProposalConfirmationIn,
    *,
    idempotency_key: str,
) -> dict[str, Any]:
    proposal = body.status_proposal
    if not isinstance(proposal, AppointmentStatusProposalOut):
        raise ValueError("waiting-area proposals are outside the status-only seam")
    if proposal.blocks:
        raise ValueError("blocked status proposals cannot enter confirmation")
    if (
        proposal.signed_confirmation_evidence_required is not True
        or body.signed_confirmation_evidence_required is not True
    ):
        raise ValueError("signed confirmation evidence must remain mandatory")
    return {
        "operation_id": STATUS_CONFIRM_OPERATION_ID,
        "route_family": STATUS_CONFIRM_ROUTE_FAMILY,
        "idempotency_key": idempotency_key,
        "confirmed": body.confirmed,
        "proposal_intent": proposal.intent,
        "proposal_safe": proposal.safe,
        "requires_confirmation": proposal.requires_confirmation,
        "autonomy_tier": proposal.autonomy_tier,
        "command": status_command_payload(proposal.command),
        "proposal_warning_codes": [issue.code for issue in proposal.warnings],
        "confirmed_warning_codes": list(body.confirmed_warnings),
        "freshness_id": body.status_proposal_freshness_id or proposal.status_proposal_freshness_id,
        "signed_evidence_required": True,
    }


def _verified_proposal_state(
    *,
    body: AppointmentStatusProposalConfirmationIn,
    authenticated_user: User,
    evidence_secret: str,
    proposal_version_binding: Mapping[str, Any],
    proposal_version_binding_secret: bytes,
) -> tuple[dict[str, Any], str]:
    proposal = body.status_proposal
    if not isinstance(proposal, AppointmentStatusProposalOut):
        raise ValueError("waiting-area proposals are outside the status-only seam")
    evidence = body.signed_confirmation_evidence
    if not isinstance(evidence, Mapping):
        raise ValueError("signed confirmation evidence is required")
    payload = evidence.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("signed confirmation evidence payload is invalid")
    signed_state = payload.get("current_state")
    required_state_keys = {
        "appointment_id",
        "status",
        "waiting_area_id",
        "status_reason_code",
    }
    if not isinstance(signed_state, Mapping) or set(signed_state) != required_state_keys:
        raise ValueError("signed proposal state shape is invalid")
    source_version = verify_status_proposal_version_binding(
        proposal_version_binding,
        signed_confirmation_evidence=evidence,
        secret=proposal_version_binding_secret,
    )
    current_state = {key: signed_state[key] for key in sorted(required_state_keys)}
    current_state["source_version"] = source_version
    freshness_id = status_proposal_freshness_id(proposal.command, current_state)
    if (
        proposal.status_proposal_freshness_id != freshness_id
        or body.status_proposal_freshness_id != freshness_id
    ):
        raise ValueError("proposal freshness fields do not match signed state")
    expected_payload = status_signed_confirmation_payload(
        practice_id=authenticated_user.practice_id,
        actor_id=authenticated_user.id,
        command=proposal.command,
        current_state=current_state,
        freshness_id=freshness_id,
    )
    result = verify_signed_confirmation_evidence(
        dict(evidence),
        expected_payload,
        expected_purpose=STATUS_CONFIRM_EVIDENCE_PURPOSE,
        secret=_require_evidence_secret(evidence_secret),
    )
    if not result.verified:
        raise ValueError(result.code)
    if proposal.signed_confirmation_evidence not in (None, dict(evidence)):
        raise ValueError("proposal and confirmation evidence differ")
    return current_state, freshness_id


def _proposal_server_ingress(
    *,
    body: AppointmentStatusProposalConfirmationIn,
    authenticated_user: User,
    session_reference: str,
    evidence_secret: str,
    proposal_version_binding: Mapping[str, Any],
    proposal_version_binding_secret: bytes,
) -> StatusConfirmServerIngress:
    current_state, freshness_id = _verified_proposal_state(
        body=body,
        authenticated_user=authenticated_user,
        evidence_secret=evidence_secret,
        proposal_version_binding=proposal_version_binding,
        proposal_version_binding_secret=proposal_version_binding_secret,
    )
    role = authenticated_user.role
    authority_current = bool(authenticated_user.is_active and role in MUTATING_ROLES)
    return StatusConfirmServerIngress(
        practice_id=authenticated_user.practice_id,
        actor_id=authenticated_user.id,
        actor_role=_enum_value(role),
        session_id=session_reference,
        authority_current=authority_current,
        current_state=current_state,
        expected_freshness_id=freshness_id,
        evidence_status="verified",
        evidence_purpose=STATUS_CONFIRM_EVIDENCE_PURPOSE,
        expected_evidence_purpose=STATUS_CONFIRM_EVIDENCE_PURPOSE,
        evidence_binding="exact",
    )


def _locked_server_ingress(
    *,
    body: AppointmentStatusProposalConfirmationIn,
    authenticated_user: User,
    appointment: Any,
    session_reference: str,
    evidence_secret: str,
) -> StatusConfirmServerIngress:
    proposal = body.status_proposal
    if not isinstance(proposal, AppointmentStatusProposalOut):
        raise ValueError("waiting-area proposals are outside the status-only seam")
    current_state = appointment_status_state(appointment)
    freshness_id = status_proposal_freshness_id(proposal.command, current_state)
    expected_payload = status_signed_confirmation_payload(
        practice_id=authenticated_user.practice_id,
        actor_id=authenticated_user.id,
        command=proposal.command,
        current_state=current_state,
        freshness_id=freshness_id,
    )
    evidence = verify_signed_confirmation_evidence(
        body.signed_confirmation_evidence,
        expected_payload,
        expected_purpose=STATUS_CONFIRM_EVIDENCE_PURPOSE,
        secret=_require_evidence_secret(evidence_secret),
    )
    role = authenticated_user.role
    authority_current = bool(
        authenticated_user.is_active
        and role in MUTATING_ROLES
        and authenticated_user.practice_id == appointment.practice_id
    )
    return StatusConfirmServerIngress(
        practice_id=authenticated_user.practice_id,
        actor_id=authenticated_user.id,
        actor_role=_enum_value(role),
        session_id=session_reference,
        authority_current=authority_current,
        current_state=current_state,
        expected_freshness_id=freshness_id,
        evidence_status="verified" if evidence.verified else evidence.code,
        evidence_purpose=STATUS_CONFIRM_EVIDENCE_PURPOSE,
        expected_evidence_purpose=STATUS_CONFIRM_EVIDENCE_PURPOSE,
        evidence_binding="exact" if evidence.verified else "invalid",
    )


def _blocked(reason: str) -> StatusConfirmCompositionResult:
    body = AppointmentConfirmStatusProposalOut(
        safe=False,
        requires_confirmation=True,
        autonomy_tier="blocked",
        summary="Cannot confirm status proposal. See blocked issues.",
        appointment=None,
        warnings=[],
        blocks=[{"code": reason, "severity": "blocked", "message": "Status confirmation stopped."}],
        audit_evidence=[],
    ).model_dump(mode="json")
    return StatusConfirmCompositionResult("blocked", 200, body)


def _error(status_code: int, code: str) -> StatusConfirmCompositionResult:
    return StatusConfirmCompositionResult(
        "error",
        status_code,
        {"detail": {"code": code, "message": "Status confirmation is unavailable."}},
    )


def _default_user_loader(db: Any, actor_id: Any) -> Any:
    return db.query(User).populate_existing().filter(User.id == actor_id).one_or_none()


def _set_practice_context(db: Any, practice_id: Any) -> None:
    db.execute(
        text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
        {"practice_id": str(practice_id)},
    )


def _current_authority(
    *,
    db: Any,
    actor_id: Any,
    practice_id: Any,
    actor_role: Any,
    user_loader: UserLoader,
) -> Callable[[Any, Any], bool]:
    expected_role = _enum_value(actor_role)

    def check(practice: Any, appointment: Any) -> bool:
        _set_practice_context(db, practice_id)
        actor = user_loader(db, actor_id)
        return bool(
            actor is not None
            and actor.is_active
            and actor.id == actor_id
            and actor.practice_id == practice_id
            and _enum_value(actor.role) == expected_role
            and practice.id == practice_id
            and appointment.practice_id == practice_id
        )

    return check


def _locked_server_factory(
    *,
    body: AppointmentStatusProposalConfirmationIn,
    authenticated_user: User,
    evidence_secret: str,
) -> Callable[[Any, StatusConfirmServerIngress], Mapping[str, Any]]:
    def build(appointment: Any, ingress: StatusConfirmServerIngress) -> Mapping[str, Any]:
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
    body: AppointmentStatusProposalConfirmationIn,
    authenticated_user: User,
    session_reference: str,
) -> Callable[[StatusConfirmPhysicalDecision, Mapping[str, Any]], StatusConfirmEffectResult]:
    def stage(
        decision: StatusConfirmPhysicalDecision,
        request: Mapping[str, Any],
    ) -> StatusConfirmEffectResult:
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
        status_after = AppointmentStatus(command["status"])
        appointment.status = status_after
        appointment.status_reason_code = command["status_reason_code"]
        if command["waiting_area_id_supplied"]:
            appointment.waiting_area_id = (
                uuid.UUID(command["waiting_area_id"])
                if command["waiting_area_id"] is not None
                else None
            )
        elif command["status"] in TERMINAL_STATUSES:
            appointment.waiting_area_id = None
        audit = AppointmentAuditLog(
            id=uuid.uuid4(),
            practice_id=authenticated_user.practice_id,
            appointment_id=appointment.id,
            confirmed_by_user_id=authenticated_user.id,
            action=AppointmentAuditAction.status_change,
            status_before=status_before,
            status_after=status_after,
            status_reason_code=command["status_reason_code"],
            confirmed_warnings=list(request["warning_codes"]),
            command_id=decision.record.id,
            bernie_session_id=session_reference,
        )
        decision.record.bernie_session_id = session_reference
        db.add(audit)
        db.flush()
        db.refresh(appointment)
        if appointment.appointment_state_version != decision.pre_state_version + 1:
            raise ValueError("database-owned adjacent appointment version missing")
        public = AppointmentConfirmStatusProposalOut(
            safe=True,
            requires_confirmation=False,
            autonomy_tier="confirmed_write",
            summary="Confirmed status proposal and updated one appointment.",
            appointment=AppointmentOut.model_validate(appointment),
            warnings=body.status_proposal.warnings,
            blocks=[],
            audit_evidence=[
                "status_product_adapter_v1",
                "status_signed_confirmation_evidence_verified",
                "status_current_authority_rechecked",
            ],
        ).model_dump(mode="json")
        return StatusConfirmEffectResult(public_response=public, audit_log_id=audit.id)

    return stage


def compose_product_status_confirm(
    body: AppointmentStatusProposalConfirmationIn,
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
    user_loader: UserLoader = _default_user_loader,
    transaction_factory: TransactionFactory = status_confirm_locked_transaction,
) -> StatusConfirmCompositionResult:
    """Compose one status-only product confirmation without mounting a route."""
    if not isinstance(body.status_proposal, AppointmentStatusProposalOut):
        return _blocked("unsupported_status_confirm_variant")
    try:
        _require_hmac_secret(idempotency_secret, label="idempotency secret")
        _require_hmac_secret(session_binding_secret, label="session binding secret")
        session_reference = authenticated_session_reference(
            authenticated_bearer_token,
            secret=authenticated_session_secret,
        )
        transport = _transport(body, idempotency_key=idempotency_key)
        ingress = _proposal_server_ingress(
            body=body,
            authenticated_user=authenticated_user,
            session_reference=session_reference,
            evidence_secret=evidence_secret,
            proposal_version_binding=proposal_version_binding,
            proposal_version_binding_secret=proposal_version_binding_secret,
        )
    except (AttributeError, TypeError, ValueError):
        return _error(403, "authenticated_status_context_unavailable")

    command_db = command_session_factory()
    with closing(command_db):
        authority = _current_authority(
            db=command_db,
            actor_id=authenticated_user.id,
            practice_id=authenticated_user.practice_id,
            actor_role=authenticated_user.role,
            user_loader=user_loader,
        )
        return compose_status_confirm(
            transport,
            server_ingress=ingress,
            db=command_db,
            idempotency_secret=idempotency_secret,
            session_binding_secret=session_binding_secret,
            admission_adapter=status_confirm_admission_adapter,
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
            practice_is_active=lambda practice: practice.id == authenticated_user.practice_id,
            current_authority=authority,
            transaction_factory=transaction_factory,
        )


__all__ = [
    "STATUS_CONFIRM_EVIDENCE_PURPOSE",
    "STATUS_CONFIRM_OPERATION_ID",
    "STATUS_CONFIRM_ROUTE_FAMILY",
    "PROPOSAL_VERSION_BINDING_SCHEMA",
    "appointment_status_state",
    "authenticated_session_reference",
    "compose_product_status_confirm",
    "mint_status_proposal_version_binding",
    "required_warning_codes",
    "status_command_payload",
    "status_confirm_admission_adapter",
    "status_proposal_freshness_id",
    "status_signed_confirmation_payload",
    "verify_status_proposal_version_binding",
]
