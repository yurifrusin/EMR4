"""Pure unmounted check-in admission-control rehearsal kernel.

The module deliberately has no application, persistence, environment, network,
provider, filesystem-write, or clockwork-control dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


SCHEMA_VERSION = "emr4.check-in-admission-kernel.v1"
DECISION_SCHEMA_VERSION = "emr4.check-in-admission-decision.v1"
FULL_GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ClosedTextEnum(str, Enum):
    """String enum with stable JSON-facing values."""


class AdmissionState(ClosedTextEnum):
    ABSENT = "absent"
    PREPARED = "prepared"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"


class KillSwitchState(ClosedTextEnum):
    CLEAR = "clear"
    ENGAGED = "engaged"


class AdmissionLane(ClosedTextEnum):
    NONE = "none"
    AUTHORED_SYNTHETIC = "authored_synthetic"
    ORDINARY_PRACTICE = "ordinary_practice"
    AMBIGUOUS = "ambiguous"


class DecisionValue(ClosedTextEnum):
    ADMITTED = "admitted"
    DENIED = "denied"


class DecisionReason(ClosedTextEnum):
    SNAPSHOT_MISSING = "snapshot_missing"
    SNAPSHOT_INVALID = "snapshot_invalid"
    SNAPSHOT_STALE = "snapshot_stale"
    SNAPSHOT_AMBIGUOUS = "snapshot_ambiguous"
    FEATURE_DISABLED = "feature_disabled"
    KILL_SWITCH_ENGAGED = "kill_switch_engaged"
    NO_MATCHING_LANE = "no_matching_lane"
    LANE_AMBIGUOUS = "lane_ambiguous"
    ADMITTED_SYNTHETIC = "admitted_synthetic"
    ORDINARY_ACTIVATION_CLOSED = "ordinary_activation_closed"
    ORDINARY_STATE_NOT_ACTIVE = "ordinary_state_not_active"
    ORDINARY_BINDING_MISMATCH = "ordinary_binding_mismatch"
    ORDINARY_EVIDENCE_MISSING = "ordinary_evidence_missing"


class ControlOperation(ClosedTextEnum):
    PREPARE = "prepareAppointmentCheckInAdmission"
    ACTIVATE = "activateAppointmentCheckInAdmission"
    SUSPEND = "suspendAppointmentCheckInAdmission"
    WITHDRAW = "withdrawAppointmentCheckInAdmission"
    ENGAGE_KILL_SWITCH = "engageAppointmentCheckInGlobalKillSwitch"


class TransitionReason(ClosedTextEnum):
    ACCEPTED_NON_ADMITTING = "accepted_non_admitting"
    ACTIVATION_AUTHORITY_CLOSED = "activation_authority_closed"
    INVALID_TRANSITION = "invalid_transition"
    KILL_SWITCH_ALREADY_ENGAGED = "kill_switch_already_engaged"


class CommandValidationReason(ClosedTextEnum):
    ACCEPTED = "accepted"
    UNKNOWN_OPERATION = "unknown_operation"
    HUMAN_AUTHORITY_REQUIRED = "human_authority_required"
    OPERATOR_ROLE_REQUIRED = "operator_role_required"
    PRACTICE_SCOPE_REQUIRED = "practice_scope_required"
    ENVIRONMENT_SCOPE_REQUIRED = "environment_scope_required"
    CORRELATION_REQUIRED = "correlation_required"
    IDEMPOTENCY_REQUIRED = "idempotency_required"
    REQUEST_DIGEST_INVALID = "request_digest_invalid"
    IDEMPOTENCY_DIGEST_BINDING_REQUIRED = "idempotency_digest_binding_required"
    EXPECTED_RECORD_VERSION_INVALID = "expected_record_version_invalid"
    EXPECTED_GENERATION_INVALID = "expected_generation_invalid"
    CLOSED_REASON_REQUIRED = "closed_reason_required"
    AUTHORITY_GIT_OBJECT_INVALID = "authority_git_object_invalid"
    AUTHORITY_GIT_OBJECT_UNRESOLVED = "authority_git_object_unresolved"
    FRESHNESS_REQUIRED = "freshness_required"
    AUDIT_REQUIRED = "audit_required"
    PATIENT_FREE_RECEIPT_REQUIRED = "patient_free_receipt_required"


@dataclass(frozen=True, slots=True)
class RehearsalProfile:
    schema_version: str = SCHEMA_VERSION
    ordinary_activation_authority_granted: bool = False
    canonical_active_ordinary_record_count: int = 0


REHEARSAL_PROFILE = RehearsalProfile()


@dataclass(frozen=True, slots=True)
class OrdinaryAdmissionRecord:
    state: AdmissionState
    practice_id: str
    environment: str
    operation_family: str
    record_version: int
    snapshot_generation: int
    operational_evidence_valid: bool


@dataclass(frozen=True, slots=True)
class AdmissionSnapshot:
    schema_version: str
    signature_valid: bool
    authority_git_object: str
    authority_git_object_resolved: bool
    fresh: bool
    environment: str
    snapshot_generation: int
    snapshot_digest: str
    current_record_count: int
    kill_switch: KillSwitchState
    ordinary_record: OrdinaryAdmissionRecord | None = None


@dataclass(frozen=True, slots=True)
class AdmissionRequest:
    feature_enabled: bool
    authored_synthetic_admitted: bool
    practice_id: str
    environment: str
    operation_family: str = "canonical_check_in"


@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    schema_version: str
    decision: DecisionValue
    lane: AdmissionLane
    reason_code: DecisionReason
    snapshot_generation: int | None
    snapshot_digest: str | None

    @property
    def admitted(self) -> bool:
        return self.decision is DecisionValue.ADMITTED


@dataclass(frozen=True, slots=True)
class TransitionResult:
    accepted: bool
    operation: ControlOperation
    from_state: AdmissionState
    to_state: AdmissionState
    reason_code: TransitionReason


@dataclass(frozen=True, slots=True)
class KillSwitchTransitionResult:
    accepted: bool
    operation: ControlOperation
    from_state: KillSwitchState
    to_state: KillSwitchState
    reason_code: TransitionReason


@dataclass(frozen=True, slots=True)
class ControlCommandEnvelope:
    operation_id: str
    authenticated_current_human: bool
    dedicated_operator_role: bool
    server_owned_practice_scope: bool
    server_owned_environment_scope: bool
    correlation_id: str
    idempotency_key: str
    complete_request_digest: str
    idempotency_bound_to_complete_request_digest: bool
    expected_record_version: int
    expected_snapshot_generation: int
    closed_reason_code: str
    authority_git_object: str
    authority_git_object_resolved: bool
    fresh: bool
    append_only_audit_available: bool
    bounded_patient_free_receipt: bool


@dataclass(frozen=True, slots=True)
class CommandValidationResult:
    accepted: bool
    reason_code: CommandValidationReason


@dataclass(frozen=True, slots=True)
class UnknownCommitResult:
    success_released: bool = False
    readback_required: bool = True
    retry_allowed: bool = False
    readback_identity: str = "server_command_id_and_idempotency_identity"


def _decision(
    *,
    snapshot: AdmissionSnapshot | None,
    decision: DecisionValue,
    lane: AdmissionLane,
    reason: DecisionReason,
) -> AdmissionDecision:
    return AdmissionDecision(
        schema_version=DECISION_SCHEMA_VERSION,
        decision=decision,
        lane=lane,
        reason_code=reason,
        snapshot_generation=None if snapshot is None else snapshot.snapshot_generation,
        snapshot_digest=None if snapshot is None else snapshot.snapshot_digest,
    )


def _snapshot_invalid(snapshot: AdmissionSnapshot, request: AdmissionRequest) -> bool:
    return any(
        (
            snapshot.schema_version != SCHEMA_VERSION,
            not snapshot.signature_valid,
            FULL_GIT_OBJECT.fullmatch(snapshot.authority_git_object) is None,
            not snapshot.authority_git_object_resolved,
            snapshot.environment != request.environment,
            snapshot.snapshot_generation < 1,
            SHA256.fullmatch(snapshot.snapshot_digest) is None,
            snapshot.current_record_count < 0,
            snapshot.current_record_count > 1,
            snapshot.current_record_count == 0 and snapshot.ordinary_record is not None,
            snapshot.current_record_count == 1 and snapshot.ordinary_record is None,
        )
    )


def _ordinary_matches(
    record: OrdinaryAdmissionRecord, request: AdmissionRequest, snapshot: AdmissionSnapshot
) -> bool:
    return all(
        (
            record.practice_id == request.practice_id,
            record.environment == request.environment,
            record.operation_family == request.operation_family,
            record.snapshot_generation == snapshot.snapshot_generation,
            record.record_version >= 1,
        )
    )


def evaluate_admission(
    snapshot: AdmissionSnapshot | None,
    request: AdmissionRequest,
    *,
    profile: RehearsalProfile = REHEARSAL_PROFILE,
) -> AdmissionDecision:
    """Evaluate one immutable snapshot without I/O, fallback, or side effect."""

    if snapshot is None:
        return _decision(
            snapshot=None,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.NONE,
            reason=DecisionReason.SNAPSHOT_MISSING,
        )
    if _snapshot_invalid(snapshot, request):
        reason = (
            DecisionReason.SNAPSHOT_AMBIGUOUS
            if snapshot.current_record_count > 1
            else DecisionReason.SNAPSHOT_INVALID
        )
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.NONE,
            reason=reason,
        )
    if not snapshot.fresh:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.NONE,
            reason=DecisionReason.SNAPSHOT_STALE,
        )
    if request.feature_enabled is not True:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.NONE,
            reason=DecisionReason.FEATURE_DISABLED,
        )
    if snapshot.kill_switch is KillSwitchState.ENGAGED:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.NONE,
            reason=DecisionReason.KILL_SWITCH_ENGAGED,
        )

    record = snapshot.ordinary_record
    synthetic_match = request.authored_synthetic_admitted is True
    ordinary_match = record is not None and _ordinary_matches(record, request, snapshot)
    if synthetic_match and ordinary_match:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.AMBIGUOUS,
            reason=DecisionReason.LANE_AMBIGUOUS,
        )
    if synthetic_match:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.ADMITTED,
            lane=AdmissionLane.AUTHORED_SYNTHETIC,
            reason=DecisionReason.ADMITTED_SYNTHETIC,
        )
    if record is None:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.NONE,
            reason=DecisionReason.NO_MATCHING_LANE,
        )
    if not ordinary_match:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.ORDINARY_PRACTICE,
            reason=DecisionReason.ORDINARY_BINDING_MISMATCH,
        )
    if record.state is not AdmissionState.ACTIVE:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.ORDINARY_PRACTICE,
            reason=DecisionReason.ORDINARY_STATE_NOT_ACTIVE,
        )
    if not record.operational_evidence_valid:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.ORDINARY_PRACTICE,
            reason=DecisionReason.ORDINARY_EVIDENCE_MISSING,
        )
    if not profile.ordinary_activation_authority_granted:
        return _decision(
            snapshot=snapshot,
            decision=DecisionValue.DENIED,
            lane=AdmissionLane.ORDINARY_PRACTICE,
            reason=DecisionReason.ORDINARY_ACTIVATION_CLOSED,
        )
    raise ValueError("ordinary activation is outside the admitted rehearsal profile")


def transition_record(
    state: AdmissionState, operation: ControlOperation
) -> TransitionResult:
    """Apply only the current disable-biased executable transition subset."""

    if operation is ControlOperation.PREPARE and state is AdmissionState.ABSENT:
        target = AdmissionState.PREPARED
        accepted = True
        reason = TransitionReason.ACCEPTED_NON_ADMITTING
    elif operation is ControlOperation.ACTIVATE and state is AdmissionState.PREPARED:
        target = state
        accepted = False
        reason = TransitionReason.ACTIVATION_AUTHORITY_CLOSED
    elif operation is ControlOperation.SUSPEND and state is AdmissionState.ACTIVE:
        target = AdmissionState.SUSPENDED
        accepted = True
        reason = TransitionReason.ACCEPTED_NON_ADMITTING
    elif operation is ControlOperation.WITHDRAW and state in {
        AdmissionState.PREPARED,
        AdmissionState.ACTIVE,
        AdmissionState.SUSPENDED,
    }:
        target = AdmissionState.WITHDRAWN
        accepted = True
        reason = TransitionReason.ACCEPTED_NON_ADMITTING
    else:
        target = state
        accepted = False
        reason = TransitionReason.INVALID_TRANSITION
    if accepted and target is AdmissionState.ACTIVE:
        raise AssertionError("rehearsal transition produced active state")
    return TransitionResult(
        accepted=accepted,
        operation=operation,
        from_state=state,
        to_state=target,
        reason_code=reason,
    )


def engage_kill_switch(state: KillSwitchState) -> KillSwitchTransitionResult:
    """Engage the monotonic switch; there is deliberately no clear operation."""

    if state is KillSwitchState.CLEAR:
        return KillSwitchTransitionResult(
            accepted=True,
            operation=ControlOperation.ENGAGE_KILL_SWITCH,
            from_state=state,
            to_state=KillSwitchState.ENGAGED,
            reason_code=TransitionReason.ACCEPTED_NON_ADMITTING,
        )
    return KillSwitchTransitionResult(
        accepted=False,
        operation=ControlOperation.ENGAGE_KILL_SWITCH,
        from_state=state,
        to_state=state,
        reason_code=TransitionReason.KILL_SWITCH_ALREADY_ENGAGED,
    )


def validate_command_envelope(
    command: ControlCommandEnvelope,
) -> CommandValidationResult:
    """Validate the frozen command shape without dispatching it."""

    checks = (
        (
            command.operation_id not in {item.value for item in ControlOperation},
            CommandValidationReason.UNKNOWN_OPERATION,
        ),
        (
            not command.authenticated_current_human,
            CommandValidationReason.HUMAN_AUTHORITY_REQUIRED,
        ),
        (
            not command.dedicated_operator_role,
            CommandValidationReason.OPERATOR_ROLE_REQUIRED,
        ),
        (
            not command.server_owned_practice_scope,
            CommandValidationReason.PRACTICE_SCOPE_REQUIRED,
        ),
        (
            not command.server_owned_environment_scope,
            CommandValidationReason.ENVIRONMENT_SCOPE_REQUIRED,
        ),
        (
            not command.correlation_id or len(command.correlation_id) > 128,
            CommandValidationReason.CORRELATION_REQUIRED,
        ),
        (
            not command.idempotency_key or len(command.idempotency_key) > 128,
            CommandValidationReason.IDEMPOTENCY_REQUIRED,
        ),
        (
            SHA256.fullmatch(command.complete_request_digest) is None,
            CommandValidationReason.REQUEST_DIGEST_INVALID,
        ),
        (
            not command.idempotency_bound_to_complete_request_digest,
            CommandValidationReason.IDEMPOTENCY_DIGEST_BINDING_REQUIRED,
        ),
        (
            command.expected_record_version < 0,
            CommandValidationReason.EXPECTED_RECORD_VERSION_INVALID,
        ),
        (
            command.expected_snapshot_generation < 1,
            CommandValidationReason.EXPECTED_GENERATION_INVALID,
        ),
        (
            not command.closed_reason_code or len(command.closed_reason_code) > 64,
            CommandValidationReason.CLOSED_REASON_REQUIRED,
        ),
        (
            FULL_GIT_OBJECT.fullmatch(command.authority_git_object) is None,
            CommandValidationReason.AUTHORITY_GIT_OBJECT_INVALID,
        ),
        (
            not command.authority_git_object_resolved,
            CommandValidationReason.AUTHORITY_GIT_OBJECT_UNRESOLVED,
        ),
        (not command.fresh, CommandValidationReason.FRESHNESS_REQUIRED),
        (
            not command.append_only_audit_available,
            CommandValidationReason.AUDIT_REQUIRED,
        ),
        (
            not command.bounded_patient_free_receipt,
            CommandValidationReason.PATIENT_FREE_RECEIPT_REQUIRED,
        ),
    )
    for failed, reason in checks:
        if failed:
            return CommandValidationResult(accepted=False, reason_code=reason)
    return CommandValidationResult(
        accepted=True, reason_code=CommandValidationReason.ACCEPTED
    )


def unknown_commit_result() -> UnknownCommitResult:
    """Return the only admitted uncertain-commit posture."""

    return UnknownCommitResult()
