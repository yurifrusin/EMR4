"""Bureau C4 provider-free authored-synthetic allowlisted-actuator simulator.

Pure in-memory.  This module has **no** filesystem, process, shell, SQL,
socket, network, database, container, cloud, IAM, secret-store, product-route,
provider or external-event capability.  It never imports production actuator
code and never imports ``app.main``.

The only allowlisted forward runbook is ``restart-api-synthetic.v1`` targeting
exactly ``isolated_authored_synthetic / service / synthetic:api-service`` with
an exact empty parameter object.  Its effect is a pure in-memory
``SyntheticServiceState`` transition ``degraded -> healthy``.  The only rollback
runbook is ``restore-api-synthetic-lkg.v1``.  Success is never released until a
distinct fresh read of the in-memory state proves the exact expected health and
revision; otherwise the exact rollback runs and a second fresh read must prove
restoration before a verified-rollback denial is released.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import threading
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional

EVIDENCE_LABEL = "provider_free_authored_synthetic_allowlisted_actuator_simulation"

PLAN_ENVIRONMENT = "isolated_authored_synthetic"
TARGET_KIND = "service"
TARGET_ID = "synthetic:api-service"
EXPECTED_REVISION = "api-synthetic-1.2.3"
FORWARD_RUNBOOK = "restart-api-synthetic.v1"
ROLLBACK_RUNBOOK = "restore-api-synthetic-lkg.v1"
FORWARD_RUNBOOK_FAMILY = "restart-api-synthetic"
OPERATION_CLASS = "scoped_service_recovery"
RISK_TIER = "reversible_scoped_service_recovery"
REQUIRED_AUTHORITY = "ordinary_confirmation"
REQUIRED_ROLE = "authorized_technical_operator"
POLICY_VERSION = "emr4.recovery_risk_policy.v1"
CATALOG_VERSION = "emr4.synthetic_runbook_catalog.v1"
SUPERSESSION_KEY = "synthetic.api-service.recovery"
HEALTH_DEGRADED = "degraded"
HEALTH_HEALTHY = "healthy"
FRESHNESS_SECONDS = 300

RUNBOOK_CATALOG_ENTRY_SCHEMA = "emr4.runbook_catalog_entry.v1"
EXECUTION_EVIDENCE_SCHEMA = "emr4.execution_evidence.v1"
COMMAND_ENVELOPE_SCHEMA = "emr4.simulator_command_envelope.v1"
EXECUTION_RECEIPT_SCHEMA = "emr4.simulator_execution_receipt.v1"
DENIAL_RECEIPT_SCHEMA = "emr4.simulator_denial_receipt.v1"

RECOVERY_PLAN_SCHEMA = "emr4.recovery_plan_candidate.v1"
RECOVERY_AUTHORITY_DECISION_SCHEMA = "emr4.recovery_authority_decision.v1"


# --------------------------------------------------------------------------- #
# Small pure helpers (no ambient capability)
# --------------------------------------------------------------------------- #

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _sha256_hex(encoded)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _runbook_family(runbook_id: str) -> str:
    return runbook_id.rsplit(".", 1)[0]


# --------------------------------------------------------------------------- #
# Enums (closed value sets)
# --------------------------------------------------------------------------- #

class RunbookId(Enum):
    RESTART_API_SYNTHETIC_V1 = FORWARD_RUNBOOK
    RESTORE_API_SYNTHETIC_LKG_V1 = ROLLBACK_RUNBOOK


class DenialReason(Enum):
    SCHEMA_REJECTED = "SCHEMA_REJECTED"
    EXECUTABLE_CONTENT_REJECTED = "EXECUTABLE_CONTENT_REJECTED"
    UNKNOWN_RUNBOOK = "UNKNOWN_RUNBOOK"
    UNKNOWN_PARAMETER = "UNKNOWN_PARAMETER"
    SCOPE_EXPANSION_REJECTED = "SCOPE_EXPANSION_REJECTED"
    STALE_OR_SUPERSEDED = "STALE_OR_SUPERSEDED"
    TARGET_REVISION_CONFLICT = "TARGET_REVISION_CONFLICT"
    OBSERVATION_MISMATCH = "OBSERVATION_MISMATCH"
    AUTHORITY_MISMATCH = "AUTHORITY_MISMATCH"
    REVIEWER_INVALID = "REVIEWER_INVALID"
    EXECUTION_EVIDENCE_INVALID = "EXECUTION_EVIDENCE_INVALID"
    EXECUTION_EVIDENCE_REPLAY = "EXECUTION_EVIDENCE_REPLAY"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    IDEMPOTENCY_IN_PROGRESS = "IDEMPOTENCY_IN_PROGRESS"
    SIMULATED_TRANSITION_FAILED = "SIMULATED_TRANSITION_FAILED"
    SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED = (
        "SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED"
    )
    SIMULATED_ROLLBACK_UNVERIFIED = "SIMULATED_ROLLBACK_UNVERIFIED"


class EvidenceState(Enum):
    ISSUED = "issued"
    CONSUMED = "consumed"


class FaultInjection(Enum):
    """Explicit test-only fault injection.  Never an arbitrary callable."""

    NONE = "none"
    TRANSITION_FAILED = "transition_failed"
    EFFECT_AUDIT_APPEND_FAILED = "effect_audit_append_failed"
    HANDLER_RETURN_FALSE = "handler_return_false"
    FIRST_READBACK_FAILED = "first_readback_failed"
    ROLLBACK_FAILED = "rollback_failed"
    ROLLBACK_READBACK_UNVERIFIED = "rollback_readback_unverified"


class SimulatedTransitionError(RuntimeError):
    pass


class SimulatedAuditAppendError(RuntimeError):
    pass


class SimulatedRollbackError(RuntimeError):
    pass


class IssuanceDenied(RuntimeError):
    """The issuer refuses to mint evidence.  Carries a stable denial reason."""

    def __init__(self, reason: DenialReason) -> None:
        super().__init__(reason.value)
        self.reason = reason


# --------------------------------------------------------------------------- #
# Closed typed objects
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ForbiddenOperationCounters:
    """Deterministic counters proving zero forbidden operations."""

    filesystem_operations: int = 0
    process_operations: int = 0
    shell_operations: int = 0
    sql_operations: int = 0
    socket_operations: int = 0
    network_operations: int = 0
    database_operations: int = 0
    container_operations: int = 0
    cloud_operations: int = 0
    iam_operations: int = 0
    secret_store_operations: int = 0
    product_route_operations: int = 0
    provider_operations: int = 0
    external_event_operations: int = 0
    dynamic_import_operations: int = 0
    eval_exec_operations: int = 0
    reflection_operations: int = 0
    template_url_path_operations: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "filesystem_operations": self.filesystem_operations,
            "process_operations": self.process_operations,
            "shell_operations": self.shell_operations,
            "sql_operations": self.sql_operations,
            "socket_operations": self.socket_operations,
            "network_operations": self.network_operations,
            "database_operations": self.database_operations,
            "container_operations": self.container_operations,
            "cloud_operations": self.cloud_operations,
            "iam_operations": self.iam_operations,
            "secret_store_operations": self.secret_store_operations,
            "product_route_operations": self.product_route_operations,
            "provider_operations": self.provider_operations,
            "external_event_operations": self.external_event_operations,
            "dynamic_import_operations": self.dynamic_import_operations,
            "eval_exec_operations": self.eval_exec_operations,
            "reflection_operations": self.reflection_operations,
            "template_url_path_operations": self.template_url_path_operations,
        }


@dataclass(frozen=True)
class SyntheticServiceState:
    environment: str = PLAN_ENVIRONMENT
    target_kind: str = TARGET_KIND
    target_id: str = TARGET_ID
    revision: str = EXPECTED_REVISION
    health: str = HEALTH_DEGRADED

    def to_dict(self) -> dict[str, str]:
        return {
            "environment": self.environment,
            "kind": self.target_kind,
            "target_id": self.target_id,
            "revision": self.revision,
            "health": self.health,
        }


@dataclass(frozen=True)
class TargetRef:
    environment: str
    kind: str
    target_id: str
    expected_revision: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TargetRef":
        return cls(
            environment=data["environment"],
            kind=data["kind"],
            target_id=data["target_id"],
            expected_revision=data["expected_revision"],
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "environment": self.environment,
            "kind": self.kind,
            "target_id": self.target_id,
            "expected_revision": self.expected_revision,
        }


@dataclass(frozen=True)
class Actor:
    actor_id: str
    role: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Actor":
        return cls(actor_id=data["actor_id"], role=data["role"])

    def to_dict(self) -> dict[str, str]:
        return {"actor_id": self.actor_id, "role": self.role}


@dataclass(frozen=True)
class ReadbackContract:
    health: str
    revision: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReadbackContract":
        return cls(health=data["health"], revision=data["revision"])

    def to_dict(self) -> dict[str, str]:
        return {"health": self.health, "revision": self.revision}


@dataclass(frozen=True)
class PlanBinding:
    plan_id: str
    plan_revision: int
    plan_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "plan_revision": self.plan_revision,
            "plan_sha256": self.plan_sha256,
        }


@dataclass(frozen=True)
class DecisionBinding:
    decision_id: str
    decision_sha256: str
    policy_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_sha256": self.decision_sha256,
            "policy_version": self.policy_version,
        }


@dataclass(frozen=True)
class CatalogBinding:
    catalog_version: str
    catalog_digest: str

    def to_dict(self) -> dict[str, str]:
        return {
            "catalog_version": self.catalog_version,
            "catalog_digest": self.catalog_digest,
        }


@dataclass(frozen=True)
class EvidenceBinding:
    evidence_id: str
    reference_sha256: str

    def to_dict(self) -> dict[str, str]:
        return {"evidence_id": self.evidence_id, "reference_sha256": self.reference_sha256}


@dataclass(frozen=True)
class Observation:
    observation_id: str
    expected_sha256: str
    must_be_fresh: bool
    observed_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Observation":
        return cls(
            observation_id=data["observation_id"],
            expected_sha256=data["expected_sha256"],
            must_be_fresh=data["must_be_fresh"],
            observed_at=data["observed_at"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "expected_sha256": self.expected_sha256,
            "must_be_fresh": self.must_be_fresh,
            "observed_at": self.observed_at,
        }


@dataclass(frozen=True)
class SimulatorRequest:
    idempotency_key: str
    correlation_id: str
    actor: Actor
    evidence_reference: str
    runbook_id: RunbookId
    target: TargetRef
    parameters: dict
    plan_binding: PlanBinding
    decision_binding: DecisionBinding
    catalog_binding: CatalogBinding
    supersession_key: str
    readback_contract: ReadbackContract

    @property
    def evidence_reference_sha256(self) -> str:
        return _sha256_hex(self.evidence_reference.encode("utf-8"))

    def fingerprint(self) -> str:
        payload = {
            "idempotency_key": self.idempotency_key,
            "correlation_id": self.correlation_id,
            "actor_id": self.actor.actor_id,
            "actor_role": self.actor.role,
            "evidence_reference_sha256": self.evidence_reference_sha256,
            "runbook_id": self.runbook_id.value,
            "target": self.target.to_dict(),
            "parameters_sha256": canonical_sha256(self.parameters),
            "plan_id": self.plan_binding.plan_id,
            "plan_revision": self.plan_binding.plan_revision,
            "plan_sha256": self.plan_binding.plan_sha256,
            "decision_id": self.decision_binding.decision_id,
            "decision_sha256": self.decision_binding.decision_sha256,
            "policy_version": self.decision_binding.policy_version,
            "catalog_version": self.catalog_binding.catalog_version,
            "catalog_digest": self.catalog_binding.catalog_digest,
            "supersession_key": self.supersession_key,
            "readback_contract": self.readback_contract.to_dict(),
        }
        return canonical_sha256(payload)


@dataclass(frozen=True)
class RunbookCatalogEntry:
    schema_version: str
    catalog_version: str
    entry_id: str
    runbook_id: str
    rollback_runbook_id: str
    operation_class: str
    risk_tier: str
    required_authority: str
    target: TargetRef
    parameter_schema: dict
    expected_transition: dict
    readback_contract: ReadbackContract
    expires_at: str
    catalog_digest: str
    immutable: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunbookCatalogEntry":
        return cls(
            schema_version=data["schema_version"],
            catalog_version=data["catalog_version"],
            entry_id=data["entry_id"],
            runbook_id=data["runbook_id"],
            rollback_runbook_id=data["rollback_runbook_id"],
            operation_class=data["operation_class"],
            risk_tier=data["risk_tier"],
            required_authority=data["required_authority"],
            target=TargetRef.from_dict(data["target"]),
            parameter_schema=data["parameter_schema"],
            expected_transition=data["expected_transition"],
            readback_contract=ReadbackContract.from_dict(data["readback_contract"]),
            expires_at=data["expires_at"],
            catalog_digest=data["catalog_digest"],
            immutable=data["immutable"],
        )

    def to_dict_core(self) -> dict[str, Any]:
        """The canonical catalog entry bytes without the self digest."""
        return {
            "schema_version": self.schema_version,
            "catalog_version": self.catalog_version,
            "entry_id": self.entry_id,
            "runbook_id": self.runbook_id,
            "rollback_runbook_id": self.rollback_runbook_id,
            "operation_class": self.operation_class,
            "risk_tier": self.risk_tier,
            "required_authority": self.required_authority,
            "target": self.target.to_dict(),
            "parameter_schema": self.parameter_schema,
            "expected_transition": self.expected_transition,
            "readback_contract": self.readback_contract.to_dict(),
            "expires_at": self.expires_at,
            "immutable": self.immutable,
        }

    def to_dict(self) -> dict[str, Any]:
        core = self.to_dict_core()
        core["catalog_digest"] = self.catalog_digest
        return core


@dataclass(frozen=True)
class ExecutionEvidenceRecord:
    evidence_id: str
    reference_sha256: str
    state: EvidenceState
    plan_id: str
    plan_revision: int
    plan_sha256: str
    decision_id: str
    decision_sha256: str
    policy_version: str
    catalog_version: str
    catalog_digest: str
    runbook_id: str
    rollback_runbook_id: str
    target: TargetRef
    actor: Actor
    candidate_generator_id: str
    reviewer_id: str
    observations: tuple[Observation, ...]
    parameters_sha256: str
    correlation_id: str
    nonce: str
    issued_at: str
    expires_at: str
    supersession_key: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionEvidenceRecord":
        return cls(
            evidence_id=data["evidence_id"],
            reference_sha256=data["reference_sha256"],
            state=EvidenceState(data["state"]),
            plan_id=data["plan_id"],
            plan_revision=data["plan_revision"],
            plan_sha256=data["plan_sha256"],
            decision_id=data["decision_id"],
            decision_sha256=data["decision_sha256"],
            policy_version=data["policy_version"],
            catalog_version=data["catalog_version"],
            catalog_digest=data["catalog_digest"],
            runbook_id=data["runbook_id"],
            rollback_runbook_id=data["rollback_runbook_id"],
            target=TargetRef.from_dict(data["target"]),
            actor=Actor.from_dict(data["actor"]),
            candidate_generator_id=data["candidate_generator_id"],
            reviewer_id=data["reviewer_id"],
            observations=tuple(Observation.from_dict(o) for o in data["observations"]),
            parameters_sha256=data["parameters_sha256"],
            correlation_id=data["correlation_id"],
            nonce=data["nonce"],
            issued_at=data["issued_at"],
            expires_at=data["expires_at"],
            supersession_key=data["supersession_key"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EXECUTION_EVIDENCE_SCHEMA,
            "evidence_id": self.evidence_id,
            "reference_sha256": self.reference_sha256,
            "state": self.state.value,
            "plan_id": self.plan_id,
            "plan_revision": self.plan_revision,
            "plan_sha256": self.plan_sha256,
            "decision_id": self.decision_id,
            "decision_sha256": self.decision_sha256,
            "policy_version": self.policy_version,
            "catalog_version": self.catalog_version,
            "catalog_digest": self.catalog_digest,
            "runbook_id": self.runbook_id,
            "rollback_runbook_id": self.rollback_runbook_id,
            "target": self.target.to_dict(),
            "actor": self.actor.to_dict(),
            "candidate_generator_id": self.candidate_generator_id,
            "reviewer_id": self.reviewer_id,
            "observations": [o.to_dict() for o in self.observations],
            "parameters_sha256": self.parameters_sha256,
            "correlation_id": self.correlation_id,
            "nonce": self.nonce,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "supersession_key": self.supersession_key,
        }


@dataclass(frozen=True)
class CommandEnvelope:
    runbook_id: str
    rollback_runbook_id: str
    target: TargetRef
    expected_revision: str
    parameters: dict
    plan_binding: PlanBinding
    decision_binding: DecisionBinding
    catalog_binding: CatalogBinding
    evidence_binding: EvidenceBinding
    actor: Actor
    correlation_id: str
    idempotency_key: str
    request_fingerprint: str
    readback_contract: ReadbackContract
    issued_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": COMMAND_ENVELOPE_SCHEMA,
            "evidence_label": EVIDENCE_LABEL,
            "runbook_id": self.runbook_id,
            "rollback_runbook_id": self.rollback_runbook_id,
            "target": self.target.to_dict(),
            "expected_revision": self.expected_revision,
            "parameters": self.parameters,
            "plan_binding": self.plan_binding.to_dict(),
            "decision_binding": self.decision_binding.to_dict(),
            "catalog_binding": self.catalog_binding.to_dict(),
            "evidence_binding": self.evidence_binding.to_dict(),
            "actor": self.actor.to_dict(),
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "request_fingerprint": self.request_fingerprint,
            "readback_contract": self.readback_contract.to_dict(),
            "issued_at": self.issued_at,
        }


@dataclass(frozen=True)
class ExecutionReceipt:
    correlation_id: str
    idempotency_key_sha256: str
    before_health: str
    after_health: str
    readback_health: str
    readback_revision: str
    attempt_evidence_sha256: str
    effect_audit_sha256: str
    rollback_invoked: bool
    rollback_verified: Optional[bool]
    operation_counters: dict
    issued_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EXECUTION_RECEIPT_SCHEMA,
            "evidence_label": EVIDENCE_LABEL,
            "result": "simulated_effect_verified",
            "simulated_effect": "health_transition_degraded_to_healthy",
            "runbook_id": FORWARD_RUNBOOK,
            "target": {
                "environment": PLAN_ENVIRONMENT,
                "kind": TARGET_KIND,
                "target_id": TARGET_ID,
                "expected_revision": EXPECTED_REVISION,
            },
            "expected_revision": EXPECTED_REVISION,
            "correlation_id": self.correlation_id,
            "idempotency_key_sha256": self.idempotency_key_sha256,
            "before_health": self.before_health,
            "after_health": self.after_health,
            "readback_health": self.readback_health,
            "readback_revision": self.readback_revision,
            "readback_fresh": True,
            "evidence_consumed": True,
            "attempt_evidence_sha256": self.attempt_evidence_sha256,
            "effect_audit_sha256": self.effect_audit_sha256,
            "rollback": {
                "invoked": self.rollback_invoked,
                "verified": self.rollback_verified,
            },
            "operation_counters": self.operation_counters,
            "issued_at": self.issued_at,
        }


@dataclass(frozen=True)
class DenialReceipt:
    reason_code: DenialReason
    correlation_digest: str
    simulated_effect: str
    rollback_invoked: bool
    rollback_verified: Optional[bool]
    operation_counters: dict
    issued_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": DENIAL_RECEIPT_SCHEMA,
            "evidence_label": EVIDENCE_LABEL,
            "result": "denied",
            "reason_code": self.reason_code.value,
            "correlation_digest": self.correlation_digest,
            "simulated_effect": self.simulated_effect,
            "rollback": {
                "invoked": self.rollback_invoked,
                "verified": self.rollback_verified,
            },
            "operation_counters": self.operation_counters,
            "issued_at": self.issued_at,
        }


@dataclass(frozen=True)
class SimulatorResult:
    execution_receipt: Optional[ExecutionReceipt] = None
    denial_receipt: Optional[DenialReceipt] = None

    @property
    def is_success(self) -> bool:
        return self.execution_receipt is not None

    @property
    def is_denial(self) -> bool:
        return self.denial_receipt is not None

    def to_dict(self) -> dict[str, Any]:
        if self.execution_receipt is not None:
            return self.execution_receipt.to_dict()
        if self.denial_receipt is not None:
            return self.denial_receipt.to_dict()
        raise ValueError("SimulatorResult must carry exactly one receipt")


@dataclass
class IdempotencyRecord:
    key: str
    fingerprint: str
    terminal_receipt: Optional[SimulatorResult] = None


@dataclass(frozen=True)
class IssuedEvidence:
    reference: str
    record: ExecutionEvidenceRecord


@dataclass
class InMemoryStateStore:
    """In-memory synthetic service state.  No persistence, no process, no IO."""

    _state: SyntheticServiceState = field(default_factory=SyntheticServiceState)

    def read(self) -> SyntheticServiceState:
        return self._state

    def write(self, state: SyntheticServiceState) -> None:
        self._state = state


@dataclass
class InMemoryAuditLog:
    """In-memory append-only immutable audit.  No persistence."""

    _records: list = field(default_factory=list)

    def append(self, record: dict[str, Any]) -> None:
        self._records.append(record)

    def snapshot(self) -> list:
        return list(self._records)

    def restore(self, snapshot: list) -> None:
        self._records = list(snapshot)

    def read(self) -> list:
        return list(self._records)


# --------------------------------------------------------------------------- #
# Fixed code-level enum-to-callable map (never string interpretation)
# --------------------------------------------------------------------------- #

def _transition_restart_api_synthetic(
    state: SyntheticServiceState,
) -> SyntheticServiceState:
    """Pure in-memory transition for restart-api-synthetic.v1."""
    if state.health != HEALTH_DEGRADED:
        raise SimulatedTransitionError("unexpected pre-transition health")
    return SyntheticServiceState(
        environment=state.environment,
        target_kind=state.target_kind,
        target_id=state.target_id,
        revision=state.revision,
        health=HEALTH_HEALTHY,
    )


def _transition_restore_lkg(snapshot: SyntheticServiceState) -> SyntheticServiceState:
    """Pure rollback for restore-api-synthetic-lkg.v1 (identity on the LKG)."""
    return snapshot


_RUNBOOK_CALLABLES: dict[
    RunbookId, Callable[[SyntheticServiceState], SyntheticServiceState]
] = {
    RunbookId.RESTART_API_SYNTHETIC_V1: _transition_restart_api_synthetic,
    RunbookId.RESTORE_API_SYNTHETIC_LKG_V1: _transition_restore_lkg,
}


# --------------------------------------------------------------------------- #
# Executable-content / callable-name screening (fail closed before lookup)
# --------------------------------------------------------------------------- #

_FORBIDDEN_TOKENS = (
    "subprocess",
    "os.system",
    "os.popen",
    "start-process",
    "cmd.exe",
    "powershell",
    "sh -c",
    "bash -c",
    "exec(",
    "eval(",
    "system(",
    "popen(",
    "__import__",
    "importlib",
    "pickle",
    "yaml.load",
    "jinja2",
    "sql",
    "drop table",
    "truncate",
    "delete from",
    "insert into",
    "http://",
    "https://",
    "ftp://",
    "file://",
    "kubectl",
    "docker",
    "aws ",
    "gcloud",
    "az ",
    "lambda",
    "getattr",
    "globals()",
    "locals()",
    "open(",
    "socket",
    "connect(",
    "urllib",
    "requests.",
    "pathlib",
    "os.path",
    "curl ",
    "wget ",
    "invoke-expression",
    "template",
    "render_template",
)


def _scan_for_executable(value: Any) -> bool:
    """Recursively reject executable content / command text in a raw payload."""
    if isinstance(value, str):
        lowered = value.lower()
        return any(token in lowered for token in _FORBIDDEN_TOKENS)
    if isinstance(value, dict):
        return any(_scan_for_executable(k) or _scan_for_executable(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(_scan_for_executable(item) for item in value)
    return False


# --------------------------------------------------------------------------- #
# Closed request boundary (rejects before authority/state lookup)
# --------------------------------------------------------------------------- #

_ALLOWED_REQUEST_KEYS = frozenset(
    {
        "idempotency_key",
        "correlation_id",
        "actor",
        "evidence_reference",
        "runbook_id",
        "target",
        "parameters",
        "plan_binding",
        "decision_binding",
        "catalog_binding",
        "supersession_key",
        "readback_contract",
    }
)


def _correlation_digest(hint: Any) -> str:
    if isinstance(hint, str) and hint:
        return _sha256_hex(hint.encode("utf-8"))
    return _sha256_hex(b"no-correlation")


def _nested_keys_ok(value: Any, expected: set[str]) -> bool:
    return isinstance(value, dict) and set(value.keys()) == expected


def parse_request(
    raw: Any, now: str
) -> tuple[Optional[SimulatorRequest], Optional[DenialReceipt]]:
    """Convert a raw dict into a closed ``SimulatorRequest`` or a denial.

    Unknown properties, executable content/command text, arbitrary callable
    names, unknown runbook ids, non-empty/unknown parameters and scope or
    revision drift all fail closed here, before any authority or state lookup.
    """
    counters = ForbiddenOperationCounters().to_dict()

    def deny(
        reason: DenialReason,
        hint: Any = "",
    ) -> tuple[Optional[SimulatorRequest], Optional[DenialReceipt]]:
        return None, DenialReceipt(
            reason_code=reason,
            correlation_digest=_correlation_digest(hint),
            simulated_effect="none",
            rollback_invoked=False,
            rollback_verified=None,
            operation_counters=counters,
            issued_at=now,
        )

    if not isinstance(raw, dict):
        return deny(DenialReason.SCHEMA_REJECTED)

    hint = raw.get("correlation_id", "")

    unknown = set(raw.keys()) - _ALLOWED_REQUEST_KEYS
    if unknown:
        return deny(DenialReason.SCHEMA_REJECTED, hint)

    if _scan_for_executable(raw):
        return deny(DenialReason.EXECUTABLE_CONTENT_REJECTED, hint)

    try:
        runbook_id = RunbookId(raw.get("runbook_id"))
    except (TypeError, ValueError):
        return deny(DenialReason.UNKNOWN_RUNBOOK, hint)

    parameters = raw.get("parameters")
    if not isinstance(parameters, dict) or parameters:
        return deny(DenialReason.UNKNOWN_PARAMETER, hint)

    # Strict nested closedness: unknown nested properties reject too.
    if not _nested_keys_ok(raw.get("target"), {"environment", "kind", "target_id", "expected_revision"}):
        return deny(DenialReason.SCHEMA_REJECTED, hint)
    if not _nested_keys_ok(raw.get("actor"), {"actor_id", "role"}):
        return deny(DenialReason.SCHEMA_REJECTED, hint)
    if not _nested_keys_ok(raw.get("readback_contract"), {"health", "revision"}):
        return deny(DenialReason.SCHEMA_REJECTED, hint)
    if not _nested_keys_ok(raw.get("plan_binding"), {"plan_id", "plan_revision", "plan_sha256"}):
        return deny(DenialReason.SCHEMA_REJECTED, hint)
    if not _nested_keys_ok(raw.get("decision_binding"), {"decision_id", "decision_sha256", "policy_version"}):
        return deny(DenialReason.SCHEMA_REJECTED, hint)
    if not _nested_keys_ok(raw.get("catalog_binding"), {"catalog_version", "catalog_digest"}):
        return deny(DenialReason.SCHEMA_REJECTED, hint)

    target_data = raw.get("target")
    if not isinstance(target_data, dict):
        return deny(DenialReason.SCOPE_EXPANSION_REJECTED, hint)
    if (
        target_data.get("environment") != PLAN_ENVIRONMENT
        or target_data.get("kind") != TARGET_KIND
        or target_data.get("target_id") != TARGET_ID
    ):
        return deny(DenialReason.SCOPE_EXPANSION_REJECTED, hint)
    if target_data.get("expected_revision") != EXPECTED_REVISION:
        return deny(DenialReason.TARGET_REVISION_CONFLICT, hint)

    actor_data = raw.get("actor")
    if not isinstance(actor_data, dict) or actor_data.get("role") != REQUIRED_ROLE:
        return deny(DenialReason.AUTHORITY_MISMATCH, hint)
    actor = Actor(actor_id=actor_data.get("actor_id"), role=actor_data.get("role"))

    if raw.get("supersession_key") != SUPERSESSION_KEY:
        return deny(DenialReason.SCOPE_EXPANSION_REJECTED, hint)

    readback_data = raw.get("readback_contract")
    if not isinstance(readback_data, dict):
        return deny(DenialReason.TARGET_REVISION_CONFLICT, hint)
    if (
        readback_data.get("health") != HEALTH_HEALTHY
        or readback_data.get("revision") != EXPECTED_REVISION
    ):
        return deny(DenialReason.TARGET_REVISION_CONFLICT, hint)

    plan_data = raw.get("plan_binding")
    decision_data = raw.get("decision_binding")
    catalog_data = raw.get("catalog_binding")
    if not all(isinstance(v, dict) for v in (plan_data, decision_data, catalog_data)):
        return deny(DenialReason.SCHEMA_REJECTED, hint)

    plan_binding = PlanBinding(
        plan_id=plan_data.get("plan_id"),
        plan_revision=plan_data.get("plan_revision"),
        plan_sha256=plan_data.get("plan_sha256"),
    )
    decision_binding = DecisionBinding(
        decision_id=decision_data.get("decision_id"),
        decision_sha256=decision_data.get("decision_sha256"),
        policy_version=decision_data.get("policy_version"),
    )
    catalog_binding = CatalogBinding(
        catalog_version=catalog_data.get("catalog_version"),
        catalog_digest=catalog_data.get("catalog_digest"),
    )

    request = SimulatorRequest(
        idempotency_key=raw["idempotency_key"],
        correlation_id=raw["correlation_id"],
        actor=actor,
        evidence_reference=raw["evidence_reference"],
        runbook_id=runbook_id,
        target=TargetRef.from_dict(target_data),
        parameters={},
        plan_binding=plan_binding,
        decision_binding=decision_binding,
        catalog_binding=catalog_binding,
        supersession_key=raw["supersession_key"],
        readback_contract=ReadbackContract.from_dict(readback_data),
    )
    return request, None


# --------------------------------------------------------------------------- #
# Evidence issuer (separate backend authority function)
# --------------------------------------------------------------------------- #

class EvidenceIssuer:
    """Mints one opaque one-use execution reference after every binding passes.

    The raw opaque reference is returned once and only its one-way SHA-256
    digest is stored in the server-held record.
    """

    def __init__(
        self,
        catalog: dict[str, RunbookCatalogEntry],
        now: Callable[[], datetime],
    ) -> None:
        self._catalog = catalog
        self._now = now
        self._records: dict[str, ExecutionEvidenceRecord] = {}
        self._issued_keys: set[tuple[int, str]] = set()
        self._sequence = 0

    @property
    def records(self) -> dict[str, ExecutionEvidenceRecord]:
        # The live store is shared with the runtime so evidence consumption is
        # observed by the issuer (one-use monotone semantics).
        return self._records

    def mint(
        self,
        *,
        plan: dict[str, Any],
        decision: dict[str, Any],
        candidate_generator_id: str,
        reviewer_id: str,
        actor: Actor,
        observations: list[dict[str, Any]],
        correlation_id: str,
        reference: Optional[str] = None,
        nonce: Optional[str] = None,
        actor_expires_at: Optional[str] = None,
        reviewer_expires_at: Optional[str] = None,
    ) -> IssuedEvidence:
        now = self._now()
        now_iso = _format_time(now)

        if plan.get("schema_version") != RECOVERY_PLAN_SCHEMA:
            raise IssuanceDenied(DenialReason.SCHEMA_REJECTED)
        if decision.get("schema_version") != RECOVERY_AUTHORITY_DECISION_SCHEMA:
            raise IssuanceDenied(DenialReason.SCHEMA_REJECTED)

        plan_sha256 = canonical_sha256(plan)
        if decision.get("plan_sha256") != plan_sha256:
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)
        if decision.get("plan_id") != plan.get("plan_id"):
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)
        if decision.get("plan_revision") != plan.get("plan_revision", 1):
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)

        if plan.get("environment") != PLAN_ENVIRONMENT:
            raise IssuanceDenied(DenialReason.SCOPE_EXPANSION_REJECTED)
        plan_target = plan.get("target", {})
        if (
            plan_target.get("kind") != TARGET_KIND
            or plan_target.get("target_id") != TARGET_ID
        ):
            raise IssuanceDenied(DenialReason.SCOPE_EXPANSION_REJECTED)
        if plan.get("operation_class") != OPERATION_CLASS:
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)

        if decision.get("computed_risk_tier") != RISK_TIER:
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)
        if decision.get("required_authority") != REQUIRED_AUTHORITY:
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)
        if decision.get("execution_authorized") is not False:
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)
        if decision.get("command_envelope_issued") is not False:
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)
        if decision.get("actuator_gate") != "closed":
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)
        if decision.get("current_state") != "review_required":
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)

        entry = self._catalog.get(FORWARD_RUNBOOK)
        if entry is None:
            raise IssuanceDenied(DenialReason.UNKNOWN_RUNBOOK)
        if _runbook_family(entry.runbook_id) != plan.get("runbook_id"):
            raise IssuanceDenied(DenialReason.UNKNOWN_RUNBOOK)
        if entry.rollback_runbook_id != ROLLBACK_RUNBOOK:
            raise IssuanceDenied(DenialReason.UNKNOWN_RUNBOOK)
        if canonical_sha256(entry.to_dict_core()) != entry.catalog_digest:
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)

        if decision.get("minimum_reviewer_count", 0) < 1:
            raise IssuanceDenied(DenialReason.REVIEWER_INVALID)
        if REQUIRED_ROLE not in decision.get("required_roles", []):
            raise IssuanceDenied(DenialReason.REVIEWER_INVALID)
        if reviewer_id == candidate_generator_id:
            raise IssuanceDenied(DenialReason.REVIEWER_INVALID)
        if actor.actor_id == candidate_generator_id:
            raise IssuanceDenied(DenialReason.REVIEWER_INVALID)
        if actor.role != REQUIRED_ROLE:
            raise IssuanceDenied(DenialReason.AUTHORITY_MISMATCH)

        observation_by_id = {o["observation_id"]: o for o in observations}
        evidence_observations: list[Observation] = []
        for precondition in plan.get("preconditions", []):
            obs_id = precondition.get("observation_id")
            source = observation_by_id.get(obs_id)
            if source is None:
                raise IssuanceDenied(DenialReason.OBSERVATION_MISMATCH)
            if source.get("content_sha256") != precondition.get("expected_sha256"):
                raise IssuanceDenied(DenialReason.OBSERVATION_MISMATCH)
            observed_at = source.get("observed_at")
            if not observed_at:
                raise IssuanceDenied(DenialReason.OBSERVATION_MISMATCH)
            evidence_observations.append(
                Observation(
                    observation_id=obs_id,
                    expected_sha256=precondition.get("expected_sha256"),
                    must_be_fresh=bool(precondition.get("must_be_fresh", True)),
                    observed_at=observed_at,
                )
            )
        if not evidence_observations:
            raise IssuanceDenied(DenialReason.OBSERVATION_MISMATCH)

        expiries = [
            _parse_time(plan.get("expires_at", "")),
            _parse_time(decision.get("effective_expiry", "")),
            _parse_time(entry.expires_at),
        ]
        for obs in evidence_observations:
            expiries.append(_parse_time(observation_by_id[obs.observation_id]["expires_at"]))
        if actor_expires_at:
            expiries.append(_parse_time(actor_expires_at))
        if reviewer_expires_at:
            expiries.append(_parse_time(reviewer_expires_at))
        earliest = min(expiries)
        if now >= earliest:
            raise IssuanceDenied(DenialReason.STALE_OR_SUPERSEDED)
        evidence_expires_at = _format_time(earliest)

        plan_revision = plan.get("plan_revision", 1)
        issued_key = (plan_revision, SUPERSESSION_KEY)
        if issued_key in self._issued_keys:
            raise IssuanceDenied(DenialReason.STALE_OR_SUPERSEDED)

        if reference is None:
            reference = secrets.token_hex(32)
        if nonce is None:
            nonce = secrets.token_hex(16)
        reference_sha256 = _sha256_hex(reference.encode("utf-8"))
        self._sequence += 1
        evidence_id = "72000000-0000-4000-8000-%012d" % self._sequence

        record = ExecutionEvidenceRecord(
            evidence_id=evidence_id,
            reference_sha256=reference_sha256,
            state=EvidenceState.ISSUED,
            plan_id=plan["plan_id"],
            plan_revision=plan_revision,
            plan_sha256=plan_sha256,
            decision_id=decision["decision_id"],
            decision_sha256=canonical_sha256(decision),
            policy_version=decision.get("policy_version", POLICY_VERSION),
            catalog_version=entry.catalog_version,
            catalog_digest=entry.catalog_digest,
            runbook_id=entry.runbook_id,
            rollback_runbook_id=entry.rollback_runbook_id,
            target=TargetRef(
                PLAN_ENVIRONMENT,
                TARGET_KIND,
                TARGET_ID,
                plan_target.get("expected_revision", EXPECTED_REVISION),
            ),
            actor=actor,
            candidate_generator_id=candidate_generator_id,
            reviewer_id=reviewer_id,
            observations=tuple(evidence_observations),
            parameters_sha256=canonical_sha256({}),
            correlation_id=correlation_id,
            nonce=nonce,
            issued_at=now_iso,
            expires_at=evidence_expires_at,
            supersession_key=SUPERSESSION_KEY,
        )
        self._records[reference_sha256] = record
        self._issued_keys.add(issued_key)
        return IssuedEvidence(reference=reference, record=record)


# --------------------------------------------------------------------------- #
# Single-purpose simulator handler
# --------------------------------------------------------------------------- #

class SimulatorRuntime:
    """In-memory single-purpose handler with one explicit critical section.

    Steps 1-12 of the frozen plan run inside one ``RLock`` critical section.
    The only dispatch is the fixed code-level ``_RUNBOOK_CALLABLES`` map.
    """

    def __init__(
        self,
        *,
        catalog: dict[str, RunbookCatalogEntry],
        state_store: InMemoryStateStore,
        attempt_audit: InMemoryAuditLog,
        effect_audit: InMemoryAuditLog,
        evidence_records: dict[str, ExecutionEvidenceRecord],
        now: Callable[[], datetime],
    ) -> None:
        self._lock = threading.RLock()
        self._catalog = catalog
        self._state_store = state_store
        self._attempt_audit = attempt_audit
        self._effect_audit = effect_audit
        self._evidence_records = evidence_records
        self._now = now
        self._idempotency: dict[str, IdempotencyRecord] = {}
        self._superseded_keys: set[str] = set()
        self._counters = ForbiddenOperationCounters()
        self._attempt_counter = 0
        self._last_envelope: Optional[CommandEnvelope] = None

    @property
    def operation_counters(self) -> dict[str, int]:
        return self._counters.to_dict()

    @property
    def idempotency_records(self) -> dict[str, IdempotencyRecord]:
        return dict(self._idempotency)

    @property
    def last_envelope(self) -> Optional[CommandEnvelope]:
        return self._last_envelope

    @property
    def attempt_audit_records(self) -> list:
        return self._attempt_audit.read()

    @property
    def effect_audit_records(self) -> list:
        return self._effect_audit.read()

    def mark_superseded(self, supersession_key: str) -> None:
        """Test-only explicit state: record that a key is superseded."""
        self._superseded_keys.add(supersession_key)

    def seed_in_progress_idempotency(self, key: str, fingerprint: str) -> None:
        """Test-only explicit state: simulate a crashed in-progress attempt."""
        self._idempotency[key] = IdempotencyRecord(key=key, fingerprint=fingerprint)

    def handle(
        self,
        request: SimulatorRequest,
        fault: FaultInjection = FaultInjection.NONE,
    ) -> SimulatorResult:
        with self._lock:
            return self._handle_locked(request, fault)

    # -- helpers ------------------------------------------------------------ #

    def _denial(
        self,
        reason: DenialReason,
        request: SimulatorRequest,
        now_iso: str,
        counters: dict,
        simulated_effect: str = "none",
        rollback_invoked: bool = False,
        rollback_verified: Optional[bool] = None,
    ) -> SimulatorResult:
        return SimulatorResult(
            denial_receipt=DenialReceipt(
                reason_code=reason,
                correlation_digest=_correlation_digest(request.correlation_id),
                simulated_effect=simulated_effect,
                rollback_invoked=rollback_invoked,
                rollback_verified=rollback_verified,
                operation_counters=counters,
                issued_at=now_iso,
            )
        )

    def _execution_receipt(
        self,
        request: SimulatorRequest,
        now_iso: str,
        counters: dict,
        before: SyntheticServiceState,
        after: SyntheticServiceState,
        readback: SyntheticServiceState,
        attempt_evidence_sha256: str,
        effect_audit_sha256: str,
    ) -> ExecutionReceipt:
        return ExecutionReceipt(
            correlation_id=request.correlation_id,
            idempotency_key_sha256=_sha256_hex(request.idempotency_key.encode("utf-8")),
            before_health=before.health,
            after_health=after.health,
            readback_health=readback.health,
            readback_revision=readback.revision,
            attempt_evidence_sha256=attempt_evidence_sha256,
            effect_audit_sha256=effect_audit_sha256,
            rollback_invoked=False,
            rollback_verified=None,
            operation_counters=counters,
            issued_at=now_iso,
        )

    def _revalidate(
        self,
        request: SimulatorRequest,
        record: ExecutionEvidenceRecord,
        now_iso: str,
    ) -> Optional[SimulatorResult]:
        """Step 4: reauthorize actor/role and revalidate every binding."""
        counters = self._counters.to_dict()

        if request.actor.role != REQUIRED_ROLE:
            return self._denial(DenialReason.AUTHORITY_MISMATCH, request, now_iso, counters)
        if request.actor.actor_id != record.actor.actor_id:
            return self._denial(DenialReason.AUTHORITY_MISMATCH, request, now_iso, counters)
        if request.runbook_id.value != record.runbook_id:
            return self._denial(DenialReason.UNKNOWN_RUNBOOK, request, now_iso, counters)
        if request.target != record.target:
            if request.target.expected_revision != record.target.expected_revision:
                return self._denial(DenialReason.TARGET_REVISION_CONFLICT, request, now_iso, counters)
            return self._denial(DenialReason.SCOPE_EXPANSION_REJECTED, request, now_iso, counters)
        if request.parameters != {} or canonical_sha256(request.parameters) != record.parameters_sha256:
            return self._denial(DenialReason.UNKNOWN_PARAMETER, request, now_iso, counters)
        if (
            request.plan_binding.plan_id != record.plan_id
            or request.plan_binding.plan_revision != record.plan_revision
            or request.plan_binding.plan_sha256 != record.plan_sha256
        ):
            return self._denial(DenialReason.AUTHORITY_MISMATCH, request, now_iso, counters)
        if (
            request.decision_binding.decision_id != record.decision_id
            or request.decision_binding.decision_sha256 != record.decision_sha256
            or request.decision_binding.policy_version != record.policy_version
        ):
            return self._denial(DenialReason.AUTHORITY_MISMATCH, request, now_iso, counters)
        if (
            request.catalog_binding.catalog_version != record.catalog_version
            or request.catalog_binding.catalog_digest != record.catalog_digest
        ):
            return self._denial(DenialReason.AUTHORITY_MISMATCH, request, now_iso, counters)
        if request.supersession_key != record.supersession_key:
            return self._denial(DenialReason.STALE_OR_SUPERSEDED, request, now_iso, counters)
        if request.correlation_id != record.correlation_id:
            return self._denial(DenialReason.AUTHORITY_MISMATCH, request, now_iso, counters)
        if request.evidence_reference_sha256 != record.reference_sha256:
            return self._denial(DenialReason.EXECUTION_EVIDENCE_INVALID, request, now_iso, counters)

        now = _parse_time(now_iso)
        if now >= _parse_time(record.expires_at):
            return self._denial(DenialReason.STALE_OR_SUPERSEDED, request, now_iso, counters)
        if record.supersession_key in self._superseded_keys:
            return self._denial(DenialReason.STALE_OR_SUPERSEDED, request, now_iso, counters)
        if record.reviewer_id == record.candidate_generator_id:
            return self._denial(DenialReason.REVIEWER_INVALID, request, now_iso, counters)
        if record.actor.actor_id == record.candidate_generator_id:
            return self._denial(DenialReason.REVIEWER_INVALID, request, now_iso, counters)

        for obs in record.observations:
            if obs.must_be_fresh:
                observed = _parse_time(obs.observed_at)
                if observed > now or (now - observed) > timedelta(seconds=FRESHNESS_SECONDS):
                    return self._denial(DenialReason.OBSERVATION_MISMATCH, request, now_iso, counters)
        return None

    def _build_envelope(
        self,
        request: SimulatorRequest,
        record: ExecutionEvidenceRecord,
        fingerprint: str,
        now_iso: str,
    ) -> CommandEnvelope:
        envelope = CommandEnvelope(
            runbook_id=request.runbook_id.value,
            rollback_runbook_id=ROLLBACK_RUNBOOK,
            target=request.target,
            expected_revision=EXPECTED_REVISION,
            parameters={},
            plan_binding=request.plan_binding,
            decision_binding=request.decision_binding,
            catalog_binding=request.catalog_binding,
            evidence_binding=EvidenceBinding(record.evidence_id, record.reference_sha256),
            actor=request.actor,
            correlation_id=request.correlation_id,
            idempotency_key=request.idempotency_key,
            request_fingerprint=fingerprint,
            readback_contract=request.readback_contract,
            issued_at=now_iso,
        )
        self._last_envelope = envelope
        return envelope

    # -- the fixed 12-step sequence ----------------------------------------- #

    def _handle_locked(
        self,
        request: SimulatorRequest,
        fault: FaultInjection,
    ) -> SimulatorResult:
        counters = self._counters.to_dict()
        now_iso = _format_time(self._now())
        fingerprint = request.fingerprint()

        # Step 1: same-key/same-fingerprint stored replay.
        # Step 2: same-key changed fingerprint or in-progress denial.
        existing = self._idempotency.get(request.idempotency_key)
        if existing is not None:
            if existing.fingerprint != fingerprint:
                return self._denial(
                    DenialReason.IDEMPOTENCY_CONFLICT, request, now_iso, counters
                )
            if existing.terminal_receipt is None:
                return self._denial(
                    DenialReason.IDEMPOTENCY_IN_PROGRESS, request, now_iso, counters
                )
            return existing.terminal_receipt

        # Step 3: resolve and lock the hashed opaque evidence.
        reference_sha256 = request.evidence_reference_sha256
        record = self._evidence_records.get(reference_sha256)
        if record is None:
            return self._denial(
                DenialReason.EXECUTION_EVIDENCE_INVALID, request, now_iso, counters
            )

        # Step 4: reauthorize actor/role and revalidate every binding.
        revalidation = self._revalidate(request, record, now_iso)
        if revalidation is not None:
            return revalidation

        # Step 5: reject consumed evidence, including under a different key.
        if record.state != EvidenceState.ISSUED:
            return self._denial(
                DenialReason.EXECUTION_EVIDENCE_REPLAY, request, now_iso, counters
            )

        # Step 6: build the closed backend-owned command envelope.
        envelope = self._build_envelope(request, record, fingerprint, now_iso)
        del envelope

        # Step 7: atomically seal idempotency, consume evidence and append the
        # immutable attempt evidence that can never be rolled back.
        self._idempotency[request.idempotency_key] = IdempotencyRecord(
            key=request.idempotency_key, fingerprint=fingerprint
        )
        self._evidence_records[reference_sha256] = replace(
            record, state=EvidenceState.CONSUMED
        )
        self._attempt_counter += 1
        attempt_id = "c4-attempt-%012d" % self._attempt_counter
        attempt_record = {
            "kind": "attempt",
            "attempt_id": attempt_id,
            "correlation_id": request.correlation_id,
            "idempotency_key_sha256": _sha256_hex(
                request.idempotency_key.encode("utf-8")
            ),
            "evidence_reference_sha256": reference_sha256,
            "runbook_id": request.runbook_id.value,
            "request_fingerprint": fingerprint,
            "sealed_at": now_iso,
            "immutable": True,
        }
        self._attempt_audit.append(attempt_record)
        attempt_evidence_sha256 = canonical_sha256(attempt_record)

        # Step 8: snapshot only simulated state/effect audit and invoke the
        # fixed transition.
        state_snapshot = self._state_store.read()
        effect_audit_snapshot = self._effect_audit.snapshot()
        try:
            if fault == FaultInjection.TRANSITION_FAILED:
                raise SimulatedTransitionError("fault: transition failed")
            transition_fn = _RUNBOOK_CALLABLES[request.runbook_id]
            transitioned = transition_fn(state_snapshot)
        except SimulatedTransitionError:
            self._state_store.write(state_snapshot)
            self._effect_audit.restore(effect_audit_snapshot)
            denial = self._denial(
                DenialReason.SIMULATED_TRANSITION_FAILED, request, now_iso, counters
            )
            self._idempotency[request.idempotency_key] = IdempotencyRecord(
                key=request.idempotency_key,
                fingerprint=fingerprint,
                terminal_receipt=denial,
            )
            return denial

        if fault == FaultInjection.HANDLER_RETURN_FALSE:
            # The transition return is non-authoritative: simulate a handler
            # that claims success while the state-store commit is skipped.
            committed = state_snapshot
        else:
            committed = transitioned
            self._state_store.write(committed)

        # Step 9: append the effect audit.
        try:
            if fault == FaultInjection.EFFECT_AUDIT_APPEND_FAILED:
                raise SimulatedAuditAppendError("fault: effect audit append failed")
            effect_record = {
                "kind": "effect",
                "attempt_id": attempt_id,
                "correlation_id": request.correlation_id,
                "runbook_id": request.runbook_id.value,
                "before": state_snapshot.to_dict(),
                "after": committed.to_dict(),
                "readback_contract": request.readback_contract.to_dict(),
                "appended_at": now_iso,
                "immutable": True,
            }
            self._effect_audit.append(effect_record)
            effect_audit_sha256 = canonical_sha256(effect_record)
        except SimulatedAuditAppendError:
            self._state_store.write(state_snapshot)
            self._effect_audit.restore(effect_audit_snapshot)
            denial = self._denial(
                DenialReason.SIMULATED_TRANSITION_FAILED, request, now_iso, counters
            )
            self._idempotency[request.idempotency_key] = IdempotencyRecord(
                key=request.idempotency_key,
                fingerprint=fingerprint,
                terminal_receipt=denial,
            )
            return denial

        # Step 10: perform a separately invoked fresh state-store read.
        readback = self._fresh_read(fault, first=True)

        # Step 11: release success only on exact expected health/revision
        # readback; otherwise invoke only the exact rollback, freshly read
        # again and distinguish verified rollback from inconclusive rollback.
        expected_health = request.readback_contract.health
        expected_revision = request.readback_contract.revision
        if (
            readback.health == expected_health
            and readback.revision == expected_revision
        ):
            receipt = self._execution_receipt(
                request,
                now_iso,
                counters,
                before=state_snapshot,
                after=committed,
                readback=readback,
                attempt_evidence_sha256=attempt_evidence_sha256,
                effect_audit_sha256=effect_audit_sha256,
            )
            result = SimulatorResult(execution_receipt=receipt)
            self._idempotency[request.idempotency_key] = IdempotencyRecord(
                key=request.idempotency_key,
                fingerprint=fingerprint,
                terminal_receipt=result,
            )
            return result

        return self._rollback_path(
            request,
            fault,
            now_iso,
            counters,
            fingerprint,
            state_snapshot,
            effect_audit_snapshot,
        )

    def _fresh_read(
        self,
        fault: FaultInjection,
        *,
        first: bool,
    ) -> SyntheticServiceState:
        """Separately invoked fresh state-store read (never the handler return)."""
        if first and fault in (
            FaultInjection.FIRST_READBACK_FAILED,
            FaultInjection.ROLLBACK_FAILED,
            FaultInjection.ROLLBACK_READBACK_UNVERIFIED,
        ):
            # A rollback can only be reached after a failed first readback, so
            # rollback-scoped faults also force the first read to fail.
            return SyntheticServiceState(
                environment=PLAN_ENVIRONMENT,
                target_kind=TARGET_KIND,
                target_id=TARGET_ID,
                revision=EXPECTED_REVISION,
                health=HEALTH_DEGRADED,
            )
        if not first and fault == FaultInjection.ROLLBACK_READBACK_UNVERIFIED:
            return SyntheticServiceState(
                environment=PLAN_ENVIRONMENT,
                target_kind=TARGET_KIND,
                target_id=TARGET_ID,
                revision=EXPECTED_REVISION,
                health=HEALTH_HEALTHY,
            )
        return self._state_store.read()

    def _rollback_path(
        self,
        request: SimulatorRequest,
        fault: FaultInjection,
        now_iso: str,
        counters: dict,
        fingerprint: str,
        state_snapshot: SyntheticServiceState,
        effect_audit_snapshot: list,
    ) -> SimulatorResult:
        # Step 11 continued: invoke only the exact rollback runbook.
        try:
            if fault == FaultInjection.ROLLBACK_FAILED:
                raise SimulatedRollbackError("fault: rollback failed")
            rollback_fn = _RUNBOOK_CALLABLES[RunbookId.RESTORE_API_SYNTHETIC_LKG_V1]
            restored = rollback_fn(state_snapshot)
            self._state_store.write(restored)
        except SimulatedRollbackError:
            # The state store is not restored; the second read will prove it.
            pass

        readback_after_rollback = self._fresh_read(fault, first=False)
        if (
            readback_after_rollback.health == state_snapshot.health
            and readback_after_rollback.revision == state_snapshot.revision
        ):
            denial = self._denial(
                DenialReason.SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED,
                request,
                now_iso,
                counters,
                simulated_effect="state_restored_to_last_known_good",
                rollback_invoked=True,
                rollback_verified=True,
            )
        else:
            denial = self._denial(
                DenialReason.SIMULATED_ROLLBACK_UNVERIFIED,
                request,
                now_iso,
                counters,
                simulated_effect="none",
                rollback_invoked=True,
                rollback_verified=False,
            )
        self._idempotency[request.idempotency_key] = IdempotencyRecord(
            key=request.idempotency_key,
            fingerprint=fingerprint,
            terminal_receipt=denial,
        )
        return denial
