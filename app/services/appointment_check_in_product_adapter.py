"""Provider-free, unmounted adapter for one canonical check-in confirmation."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Literal, Mapping
from uuid import UUID

from app.models.appointments import AppointmentStatus
from app.models.tenancy import UserRole
from app.schemas.appointments import (
    AppointmentCheckInCommand,
    AppointmentCheckInProposalConfirmationIn,
    AppointmentCheckInProposalOut,
    AppointmentCheckInReceipt,
    AppointmentConfirmCheckInProposalOut,
    AppointmentProposalIssue,
)


CHECK_IN_OPERATION_ID = "confirmAppointmentCheckInProposal"
CHECK_IN_ROUTE_FAMILY = "check-in-confirm"
CHECK_IN_EVENT_TYPE = "diary.appointment_checked_in"
CHECK_IN_EVENT_SCHEMA_VERSION = "diary.appointment_checked_in.v1"
CHECK_IN_RECEIPT_SCHEMA_VERSION = "appointment.check_in_receipt.v1"
CHECK_IN_AUDIT_EVIDENCE = (
    "rayleen_check_in_confirmation",
    "source_check_in_proposal",
    "source_current_appointment_state",
    "check_in_signed_confirmation_evidence_verified",
)
CHECK_IN_SOURCE_STATUSES = {AppointmentStatus.Booked, AppointmentStatus.Confirmed}
CHECK_IN_EVIDENCE_FAILURE_CODES = {
    "signed_evidence_missing",
    "signed_evidence_tampered",
    "signed_evidence_malformed",
    "signed_evidence_wrong_version",
    "signed_evidence_wrong_purpose",
    "signed_evidence_expired",
    "signed_evidence_mismatch",
}

ResultKind = Literal["confirmed_write", "replay", "stopped"]


@dataclass(frozen=True)
class CheckInAuditPlan:
    practice_id: UUID
    appointment_id: UUID
    actor_user_id: UUID
    actor_role: str
    command_id: UUID
    action: Literal["status_change"]
    status_before: str
    status_after: Literal["Arrived"]
    waiting_area_id_before: UUID | None
    waiting_area_id_after: UUID | None
    confirmed_warnings: tuple[str, ...]
    audit_evidence: tuple[str, ...]


@dataclass(frozen=True)
class CheckInEventPlan:
    event_type: Literal["diary.appointment_checked_in"]
    schema_version: Literal["diary.appointment_checked_in.v1"]
    practice_id: UUID
    appointment_id: UUID
    actor_user_id: UUID
    actor_role: str
    command_id: UUID
    audit_log_id: UUID
    correlation_id: UUID
    occurred_at: datetime
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class CheckInEffectPlan:
    appointment_id: UUID
    status_after: Literal["Arrived"]
    waiting_area_id_after: UUID | None


@dataclass(frozen=True)
class CheckInAdapterResult:
    kind: ResultKind
    outcome: str
    reason: str | None
    response_status_code: int
    response_body: Mapping[str, Any] | None
    committed: bool | None


@dataclass(frozen=True)
class CheckInDependencies:
    claim: Callable[..., Any]
    load_locked_appointment: Callable[..., Any]
    load_current_actor: Callable[..., Any]
    load_waiting_area: Callable[..., Any]
    verify_evidence: Callable[..., tuple[bool, str, Mapping[str, Any] | None]]
    stage_effect: Callable[..., Any]
    write_audit: Callable[..., Any]
    write_event: Callable[..., Any]
    complete: Callable[..., Any]
    commit: Callable[[], Any]
    rollback: Callable[[], Any]
    readback: Callable[..., Any]


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _uuid_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None


def check_in_state_payload(appointment: Any) -> dict[str, object]:
    """Return the exact route-local A5.1 state material."""
    return {
        "appointment_id": str(appointment.id),
        "status": _enum_value(appointment.status),
        "waiting_area_id": _uuid_or_none(appointment.waiting_area_id),
    }


def check_in_command_payload(command: AppointmentCheckInCommand) -> dict[str, object]:
    """Return the exact route-local A5.1 command material."""
    if type(command) is not AppointmentCheckInCommand:
        raise ValueError("only AppointmentCheckInCommand is supported")
    return {
        "appointment_id": str(command.appointment_id),
        "waiting_area_id": _uuid_or_none(command.waiting_area_id),
        "waiting_area_id_supplied": command.waiting_area_id_supplied,
    }


def check_in_proposal_freshness_id(
    command: AppointmentCheckInCommand,
    current_state: Mapping[str, object],
) -> str:
    """Reproduce the current A5.1 32-character freshness calculation."""
    payload = {
        "kind": "check_in_proposal_v1",
        "current_state": dict(current_state),
        "command": check_in_command_payload(command),
    }
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def check_in_target_area_id(
    appointment: Any,
    command: AppointmentCheckInCommand,
) -> UUID | None:
    """Reproduce assignment-versus-preservation target selection."""
    if command.waiting_area_id_supplied and command.waiting_area_id is not None:
        return command.waiting_area_id
    return appointment.waiting_area_id


def _patient_free(value: Any) -> bool:
    forbidden = {
        "patient",
        "patient_id",
        "patient_name",
        "patient_name_provisional",
        "first_name",
        "last_name",
        "reason",
        "reason_for_visit",
        "note",
        "notes",
        "clinical_text",
        "signed_confirmation_evidence",
        "idempotency_key",
        "raw_idempotency_key",
    }
    if isinstance(value, Mapping):
        return not any(
            str(key).lower() in forbidden or not _patient_free(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return all(_patient_free(item) for item in value)
    return True


def _exact_replay_response(value: Any, *, appointment_id: UUID) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("stored replay response is not an object")
    expected = set(AppointmentConfirmCheckInProposalOut.model_fields)
    if set(value) != expected or not _patient_free(value):
        raise ValueError("stored replay response shape is invalid")
    receipt = value.get("receipt")
    if receipt is not None:
        if not isinstance(receipt, Mapping):
            raise ValueError("stored replay receipt is invalid")
        if set(receipt) != set(AppointmentCheckInReceipt.model_fields):
            raise ValueError("stored replay receipt shape is invalid")
    parsed = AppointmentConfirmCheckInProposalOut.model_validate(value)
    if (
        parsed.safe is not True
        or parsed.requires_confirmation is not False
        or parsed.autonomy_tier != "confirmed_write"
        or parsed.summary != "Confirmed check-in and moved the appointment to Arrived."
        or parsed.receipt is None
        or parsed.receipt.appointment_id != appointment_id
        or parsed.receipt.status != AppointmentStatus.Arrived
        or parsed.receipt.commit_time.tzinfo is None
        or parsed.receipt.commit_time.utcoffset() is None
        or parsed.receipt.commit_time.utcoffset().total_seconds() != 0
        or parsed.warnings
        or parsed.blocks
        or tuple(parsed.audit_evidence) != CHECK_IN_AUDIT_EVIDENCE
    ):
        raise ValueError("stored replay result is not a canonical check-in success")
    return copy.deepcopy(dict(value))


def _blocked_response(reason: str) -> dict[str, Any]:
    response = AppointmentConfirmCheckInProposalOut(
        safe=False,
        requires_confirmation=True,
        autonomy_tier="blocked",
        summary="Check-in confirmation stopped by the deterministic adapter.",
        receipt=None,
        warnings=[],
        blocks=[
            AppointmentProposalIssue(
                code=reason,
                severity="blocked",
                message="The check-in confirmation was rejected.",
            )
        ],
        audit_evidence=[],
    )
    return response.model_dump(mode="json")


def _stop(
    reason: str,
    *,
    outcome: str = "validation_rejected",
    status_code: int = 409,
    committed: bool | None = False,
) -> CheckInAdapterResult:
    return CheckInAdapterResult(
        kind="stopped",
        outcome=outcome,
        reason=reason,
        response_status_code=status_code,
        response_body=_blocked_response(reason),
        committed=committed,
    )


def _rollback(dependencies: CheckInDependencies) -> None:
    try:
        dependencies.rollback()
    except Exception:
        pass


def _valid_receptionist(actor: Any, practice_id: UUID, actor_id: UUID | None = None) -> bool:
    try:
        return bool(
            actor is not None
            and actor.is_active is True
            and actor.practice_id == practice_id
            and (actor_id is None or actor.id == actor_id)
            and _enum_value(actor.role) == UserRole.Receptionist.value
        )
    except AttributeError:
        return False


def _submitted_evidence(body: AppointmentCheckInProposalConfirmationIn) -> str:
    proposal_evidence = body.check_in_proposal.signed_confirmation_evidence
    body_evidence = body.signed_confirmation_evidence
    if body_evidence and proposal_evidence and body_evidence != proposal_evidence:
        raise ValueError("proposal and confirmation evidence differ")
    evidence = body_evidence or proposal_evidence
    if not isinstance(evidence, str) or not evidence.strip():
        raise ValueError("signed evidence is required")
    return evidence


def _validate_envelope(
    body: AppointmentCheckInProposalConfirmationIn,
    *,
    target_appointment_id: UUID,
) -> tuple[AppointmentCheckInProposalOut, AppointmentCheckInCommand, str, str]:
    if type(body) is not AppointmentCheckInProposalConfirmationIn:
        raise ValueError("only the dedicated check-in confirmation is supported")
    proposal = body.check_in_proposal
    if type(proposal) is not AppointmentCheckInProposalOut:
        raise ValueError("only the dedicated check-in proposal is supported")
    command = proposal.command
    if type(command) is not AppointmentCheckInCommand:
        raise ValueError("only the dedicated check-in command is supported")
    if proposal.intent != "check_in_appointment":
        raise ValueError("check-in proposal intent is invalid")
    if command.appointment_id != target_appointment_id:
        raise ValueError("command and server target differ")
    if type(command.waiting_area_id_supplied) is not bool:
        raise ValueError("waiting-area supplied marker is invalid")
    if body.confirmed is not True:
        raise ValueError("explicit confirmation is required")
    if (
        proposal.safe is not True
        or proposal.requires_confirmation is not True
        or proposal.autonomy_tier not in {"proposal", "execute_with_report"}
        or proposal.blocks
    ):
        raise ValueError("check-in proposal is not safe")
    if (
        proposal.signed_confirmation_evidence_required is not True
        or body.signed_confirmation_evidence_required is not True
    ):
        raise ValueError("signed evidence must remain required")
    # The frozen A5.1 proposer emits no warnings. Treat any additive warning
    # vocabulary as a later contract change rather than reflecting client text.
    if proposal.warnings or body.confirmed_warnings:
        raise ValueError("warning acknowledgement mismatch")
    evidence = _submitted_evidence(body)
    submitted_freshness = (
        body.check_in_proposal_freshness_id
        or proposal.check_in_proposal_freshness_id
    )
    if (
        not isinstance(submitted_freshness, str)
        or len(submitted_freshness) != 32
        or (
            body.check_in_proposal_freshness_id
            and proposal.check_in_proposal_freshness_id
            and body.check_in_proposal_freshness_id
            != proposal.check_in_proposal_freshness_id
        )
    ):
        raise ValueError("check-in freshness is invalid")
    return proposal, command, evidence, submitted_freshness


def _validate_locked_appointment(
    appointment: Any,
    *,
    practice_id: UUID,
    appointment_id: UUID,
) -> str | None:
    try:
        if appointment is None:
            return "appointment_not_found"
        if appointment.id != appointment_id or appointment.practice_id != practice_id:
            return "locked_appointment_scope_mismatch"
        status = AppointmentStatus(_enum_value(appointment.status))
        if status == AppointmentStatus.Arrived:
            return "already_arrived"
        if status not in CHECK_IN_SOURCE_STATUSES:
            return "invalid_source_status"
        return None
    except (AttributeError, TypeError, ValueError):
        return "locked_appointment_invalid"


def _validate_waiting_area(
    appointment: Any,
    command: AppointmentCheckInCommand,
    *,
    practice_id: UUID,
    dependencies: CheckInDependencies,
) -> tuple[str | None, UUID | None]:
    target = check_in_target_area_id(appointment, command)
    supplied = command.waiting_area_id_supplied and command.waiting_area_id is not None
    if supplied and appointment.waiting_area_id is not None:
        return "waiting_area_move_not_supported", None
    if target is None:
        return None, None
    if appointment.location_id is None:
        code = (
            "waiting_area_location_required"
            if supplied
            else "preserved_waiting_area_location_required"
        )
        return code, None
    area = dependencies.load_waiting_area(
        practice_id=practice_id,
        waiting_area_id=target,
    )
    if area is None:
        code = "waiting_area_not_active" if supplied else "preserved_waiting_area_not_active"
        return code, None
    try:
        if area.id != target or area.practice_id != practice_id or area.is_active is not True:
            code = (
                "waiting_area_not_active"
                if supplied
                else "preserved_waiting_area_not_active"
            )
            return code, None
        if area.location_id is None or area.location_id != appointment.location_id:
            code = (
                "waiting_area_location_mismatch"
                if supplied
                else "preserved_waiting_area_location_mismatch"
            )
            return code, None
    except AttributeError:
        return "waiting_area_invalid", None
    return None, target


def _idempotency_stop(kind: str) -> CheckInAdapterResult:
    mapping = {
        "conflict": ("idempotency_key_conflict", "idempotency_conflict", 409),
        "in_progress": ("command_in_progress", "in_progress", 409),
        "stale_in_progress": ("stale_command_in_progress", "in_progress", 409),
        "failed_transient": ("prior_command_failed", "retry_required", 503),
        "evidence_replay_rejected": (
            "confirmation_replay_rejected",
            "evidence_reuse_rejected",
            409,
        ),
    }
    reason, outcome, status_code = mapping.get(
        kind,
        ("idempotency_decision_invalid", "validation_rejected", 409),
    )
    return _stop(reason, outcome=outcome, status_code=status_code)


def compose_product_check_in(
    body: AppointmentCheckInProposalConfirmationIn,
    *,
    target_appointment_id: UUID,
    server_practice_id: UUID,
    authenticated_actor: Any,
    raw_idempotency_key: str,
    now: datetime,
    dependencies: CheckInDependencies,
) -> CheckInAdapterResult:
    """Compose one fail-closed check-in transaction through injected callbacks."""
    if not isinstance(raw_idempotency_key, str) or not raw_idempotency_key.strip():
        return _stop("idempotency_key_required", outcome="idempotency_conflict")
    if (
        not isinstance(now, datetime)
        or now.tzinfo is None
        or now.utcoffset() is None
        or now.utcoffset().total_seconds() != 0
    ):
        return _stop("aware_utc_time_required")
    if not _valid_receptionist(authenticated_actor, server_practice_id):
        return _stop("current_receptionist_authority_required", outcome="authority_revoked")
    try:
        proposal, command, evidence, submitted_freshness = _validate_envelope(
            body,
            target_appointment_id=target_appointment_id,
        )
    except (AttributeError, TypeError, ValueError):
        return _stop("confirmation_envelope_invalid", outcome="confirmation_required")

    evidence_hash = hashlib.sha256(evidence.encode("utf-8")).hexdigest()
    try:
        decision = dependencies.claim(
            practice_id=server_practice_id,
            actor_user_id=str(authenticated_actor.id),
            actor_role=UserRole.Receptionist.value,
            operation_id=CHECK_IN_OPERATION_ID,
            route_family=CHECK_IN_ROUTE_FAMILY,
            raw_idempotency_key=raw_idempotency_key.strip(),
            request_body=body.model_dump(mode="json"),
            confirmation_evidence_hash=evidence_hash,
            now=now,
        )
    except Exception:
        _rollback(dependencies)
        return _stop("idempotency_claim_failed", outcome="retry_required", status_code=503)

    kind = getattr(decision, "kind", None)
    if kind == "replay":
        try:
            if decision.response_status_code != 200:
                raise ValueError("stored replay status is invalid")
            replay = _exact_replay_response(
                decision.response_body_json,
                appointment_id=target_appointment_id,
            )
        except (AttributeError, TypeError, ValueError):
            _rollback(dependencies)
            return _stop("stored_replay_invalid", outcome="retry_required", status_code=503)
        return CheckInAdapterResult(
            kind="replay",
            outcome="replay",
            reason=None,
            response_status_code=200,
            response_body=replay,
            committed=True,
        )
    if kind != "started":
        _rollback(dependencies)
        return _idempotency_stop(str(kind))

    try:
        command_record_id = decision.record.id
        if not isinstance(command_record_id, UUID):
            raise ValueError("command record id is invalid")
        appointment = dependencies.load_locked_appointment(
            practice_id=server_practice_id,
            appointment_id=target_appointment_id,
        )
        appointment_error = _validate_locked_appointment(
            appointment,
            practice_id=server_practice_id,
            appointment_id=target_appointment_id,
        )
        if appointment_error:
            _rollback(dependencies)
            return _stop(appointment_error)

        current_actor = dependencies.load_current_actor(
            practice_id=server_practice_id,
            actor_user_id=authenticated_actor.id,
        )
        if not _valid_receptionist(
            current_actor,
            server_practice_id,
            authenticated_actor.id,
        ):
            _rollback(dependencies)
            return _stop("current_authority_revoked", outcome="authority_revoked")

        current_state = check_in_state_payload(appointment)
        expected_freshness = check_in_proposal_freshness_id(command, current_state)
        if submitted_freshness != expected_freshness:
            _rollback(dependencies)
            return _stop("stale_check_in_proposal_freshness_id", outcome="stale_precondition")

        target_area_id = check_in_target_area_id(appointment, command)
        verified, verify_code, _ = dependencies.verify_evidence(
            evidence,
            now=now,
            expected_practice_id=str(server_practice_id),
            expected_actor_user_id=str(current_actor.id),
            expected_appointment_id=str(command.appointment_id),
            expected_status_before=_enum_value(appointment.status),
            expected_waiting_area_id_before=_uuid_or_none(appointment.waiting_area_id),
            expected_waiting_area_id_target=_uuid_or_none(target_area_id),
            expected_check_in_proposal_freshness_id=expected_freshness,
        )
        if verified is not True or verify_code != "signed_evidence_verified":
            _rollback(dependencies)
            reason = (
                verify_code
                if verify_code in CHECK_IN_EVIDENCE_FAILURE_CODES
                else "signed_evidence_invalid"
            )
            return _stop(reason, outcome="confirmation_required")

        area_error, target_area_id = _validate_waiting_area(
            appointment,
            command,
            practice_id=server_practice_id,
            dependencies=dependencies,
        )
        if area_error:
            _rollback(dependencies)
            return _stop(area_error)

        status_before = _enum_value(appointment.status)
        waiting_area_before = appointment.waiting_area_id
        effect_plan = CheckInEffectPlan(
            appointment_id=target_appointment_id,
            status_after=AppointmentStatus.Arrived.value,
            waiting_area_id_after=target_area_id,
        )
        dependencies.stage_effect(appointment=appointment, plan=effect_plan)

        audit_plan = CheckInAuditPlan(
            practice_id=server_practice_id,
            appointment_id=target_appointment_id,
            actor_user_id=current_actor.id,
            actor_role=UserRole.Receptionist.value,
            command_id=command_record_id,
            action="status_change",
            status_before=status_before,
            status_after=AppointmentStatus.Arrived.value,
            waiting_area_id_before=waiting_area_before,
            waiting_area_id_after=target_area_id,
            confirmed_warnings=tuple(body.confirmed_warnings),
            audit_evidence=CHECK_IN_AUDIT_EVIDENCE,
        )
        audit = dependencies.write_audit(plan=audit_plan)
        audit_id = audit.id
        if not isinstance(audit_id, UUID):
            raise ValueError("audit id is invalid")

        event_plan = CheckInEventPlan(
            event_type=CHECK_IN_EVENT_TYPE,
            schema_version=CHECK_IN_EVENT_SCHEMA_VERSION,
            practice_id=server_practice_id,
            appointment_id=target_appointment_id,
            actor_user_id=current_actor.id,
            actor_role=UserRole.Receptionist.value,
            command_id=command_record_id,
            audit_log_id=audit_id,
            correlation_id=command_record_id,
            occurred_at=now,
            payload={
                "appointment_id": str(target_appointment_id),
                "status_before": status_before,
                "status_after": AppointmentStatus.Arrived.value,
                "waiting_area_id_before": _uuid_or_none(waiting_area_before),
                "waiting_area_id_after": _uuid_or_none(target_area_id),
                "reason_codes": ["appointment_checked_in"],
            },
        )
        event = dependencies.write_event(plan=event_plan)
        event_id = event.id
        if not isinstance(event_id, UUID):
            raise ValueError("event id is invalid")

        receipt = AppointmentCheckInReceipt(
            schema_version=CHECK_IN_RECEIPT_SCHEMA_VERSION,
            appointment_id=target_appointment_id,
            status=AppointmentStatus.Arrived,
            waiting_area_id=target_area_id,
            audit_log_id=audit_id,
            event_id=event_id,
            command_id=command_record_id,
            commit_time=now,
        )
        response = AppointmentConfirmCheckInProposalOut(
            safe=True,
            requires_confirmation=False,
            autonomy_tier="confirmed_write",
            summary="Confirmed check-in and moved the appointment to Arrived.",
            receipt=receipt,
            warnings=proposal.warnings,
            blocks=[],
            audit_evidence=list(CHECK_IN_AUDIT_EVIDENCE),
        )
        response_body = response.model_dump(mode="json")
        if not _patient_free(response_body):
            raise ValueError("successful response is not patient-free")
        dependencies.complete(
            record=decision.record,
            response_status_code=200,
            response_body=response_body,
            result_kind="confirmed_write",
            target_appointment_id=target_appointment_id,
            audit_log_id=audit_id,
            confirmation_evidence_consumed_at=now,
        )
    except Exception:
        _rollback(dependencies)
        return _stop("precommit_composition_failed", outcome="retry_required", status_code=503)

    try:
        dependencies.commit()
    except Exception:
        return _stop(
            "commit_outcome_unknown",
            outcome="outcome_unknown",
            status_code=503,
            committed=None,
        )

    try:
        fresh = dependencies.readback(
            practice_id=server_practice_id,
            appointment_id=target_appointment_id,
        )
        if (
            fresh is None
            or fresh.id != target_appointment_id
            or fresh.practice_id != server_practice_id
            or _enum_value(fresh.status) != AppointmentStatus.Arrived.value
            or fresh.waiting_area_id != target_area_id
        ):
            raise ValueError("fresh readback does not match committed result")
    except Exception:
        return _stop(
            "committed_readback_unavailable",
            outcome="outcome_unknown",
            status_code=503,
            committed=None,
        )

    return CheckInAdapterResult(
        kind="confirmed_write",
        outcome="confirmed_write",
        reason=None,
        response_status_code=200,
        response_body=response_body,
        committed=True,
    )
