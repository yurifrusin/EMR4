"""Bureau C5 provider-free authored-synthetic implementation-readiness contracts.

This module owns the closed typed contracts, source-bound policy/catalog/
examples, deterministic parser and proofreader, authority/evidence/idempotency
state machine and the pure provider-request builder for the frozen C5
disposable live-development-recovery foundation.

It is deliberately pure and has **no** filesystem, process, shell, SQL,
socket, network, database, container, cloud, IAM, secret-store, product-route,
provider or external-event capability.  It never imports ``app`` and never
invokes a provider SDK or any process/socket capability.  The fixed target
module, process adapter and controller live in separate modules and are never
invoked in this worker tranche.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import threading
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Callable, Optional

# --------------------------------------------------------------------------- #
# Frozen constants (exact plan values)
# --------------------------------------------------------------------------- #

EVIDENCE_LABEL = "provider_free_authored_synthetic_c5_implementation_readiness"
OCCUPIED_LABEL = "occupied_authored_synthetic_disposable_live_development_recovery"

PLAN_ENVIRONMENT = "c5_disposable_authored_synthetic"
TARGET_KIND = "task_owned_loopback_http_service"
TARGET_ID = "synthetic:c5-recovery-target"
HOST = "127.0.0.1"
FORWARD_RUNBOOK = "start-c5-disposable-service.v1"
ROLLBACK_RUNBOOK = "stop-c5-disposable-service.v1"
FORWARD_ENTRY_ID = "start-c5-disposable-service-v1-entry"
ROLLBACK_ENTRY_ID = "stop-c5-disposable-service-v1-entry"
RISK_TIER = "reversible_scoped_service_recovery"
REQUIRED_APPROVAL_CLASS = "ordinary_confirmation"
APPROVAL_BASIS = "yuri_standing_programme_authority_2026-08-04"
POLICY_VERSION = "emr4.c5_recovery_policy.v1"
CATALOG_VERSION = "emr4.c5_runbook_catalog.v1"
SUPERSESSION_KEY = "synthetic.c5-recovery-target.recovery"
FRESHNESS_SECONDS = 300
EXPIRY_SECONDS = 300
EXPECTED_ARTIFACT_SHA256 = "76373e9dc3e1f1d7acb47c47f6aa6fe8509870d63d1d73fa4d23f44a77284228"
PLAN_SHA256 = "9f23396e8facadc5f8f1baa3294ebbcdcaeca0bf71b29f95a7743ac80220ac15"
TARGET_MODULE_RELATIVE_PATH = "scripts/model_required_bureau_c5_target.py"
SCHEMA_ROOT = (
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery"
)

# Exact Sydney development provider envelope (pure metadata; no SDK/network).
PROVIDER_MODEL = "gemini-2.5-flash"
PROVIDER_PROJECT = "bernie-emr4-dev"
PROVIDER_IDENTITY = "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
PROVIDER_REGION = "australia-southeast1"
PROVIDER_ENDPOINT = "australia-southeast1-aiplatform.googleapis.com"
THINKING_BUDGET = 1024
MAX_OUTPUT_TOKENS = 2048
CANDIDATE_COUNT = 1
TEMPERATURE = 0
CALL_LIMIT = 2
COST_CEILING_USD = 0.50
FALLBACK_ENABLED = False

# Schema versions
FRAME_SET_SCHEMA = "emr4.system_anatomy_frame_set.v1"
CANDIDATE_SCHEMA = "emr4.recovery_diagnosis_candidate.v1"
PROOFREADER_SCHEMA = "emr4.proofreader_disposition.v1"
APPROVAL_SCHEMA = "emr4.execution_approval.v1"
EVIDENCE_SCHEMA = "emr4.execution_evidence.v1"
ENVELOPE_SCHEMA = "emr4.live_recovery_command_envelope.v1"
ATTEMPT_RECEIPT_SCHEMA = "emr4.live_recovery_attempt_receipt.v1"
CLEANUP_SCHEMA = "emr4.cleanup_receipt.v1"
POLICY_SCHEMA = "emr4.c5_policy.v1"

# --------------------------------------------------------------------------- #
# Scalar admission bounds / formats (fail-closed before any lookup)
# --------------------------------------------------------------------------- #

_UUID36_RE = re.compile(r"^[0-9a-f-]{36}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_HEX32_64_RE = re.compile(r"^[0-9a-f]{32,64}$")
_OBS_ID_RE = re.compile(r"^[a-z0-9_-]+$")
_REF_RE = re.compile(r"^c5:[a-z0-9-]+$")
_MAX_FIELD_LENGTH = 400


def _is_bounded_str(value: Any, *, min_len: int = 1, max_len: int = _MAX_FIELD_LENGTH) -> bool:
    return isinstance(value, str) and min_len <= len(value) <= max_len


def _is_opaque_reference(value: Any) -> bool:
    return (
        isinstance(value, str)
        and 8 <= len(value) <= 256
        and not any(ch.isspace() for ch in value)
    )


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def strict_json_loads(text: str) -> dict[str, Any]:
    """Reject duplicate keys and non-object payloads before any lookup."""

    def object_pairs_hook(pairs):
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate key: " + key)
            out[key] = value
        return out

    value = json.loads(text, object_pairs_hook=object_pairs_hook)
    if not isinstance(value, dict):
        raise ValueError("payload must be an object")
    return value


# --------------------------------------------------------------------------- #
# Forbidden operation counters (zero during worker acceptance)
# --------------------------------------------------------------------------- #

_COUNTER_NAMES = (
    "process_starts",
    "process_stops",
    "socket_binds",
    "socket_connects",
    "port_allocations",
    "directory_creates",
    "directory_removals",
    "provider_calls",
    "database_operations",
    "product_operations",
    "cloud_iam_operations",
    "deployment_operations",
    "external_event_operations",
    "protected_operations",
    "shell_operations",
    "sql_operations",
    "network_operations",
    "dynamic_import_operations",
    "eval_exec_operations",
    "reflection_operations",
)


@dataclass(frozen=True)
class ForbiddenOperationCounters:
    process_starts: int = 0
    process_stops: int = 0
    socket_binds: int = 0
    socket_connects: int = 0
    port_allocations: int = 0
    directory_creates: int = 0
    directory_removals: int = 0
    provider_calls: int = 0
    database_operations: int = 0
    product_operations: int = 0
    cloud_iam_operations: int = 0
    deployment_operations: int = 0
    external_event_operations: int = 0
    protected_operations: int = 0
    shell_operations: int = 0
    sql_operations: int = 0
    network_operations: int = 0
    dynamic_import_operations: int = 0
    eval_exec_operations: int = 0
    reflection_operations: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "process_starts": self.process_starts,
            "process_stops": self.process_stops,
            "socket_binds": self.socket_binds,
            "socket_connects": self.socket_connects,
            "port_allocations": self.port_allocations,
            "directory_creates": self.directory_creates,
            "directory_removals": self.directory_removals,
            "provider_calls": self.provider_calls,
            "database_operations": self.database_operations,
            "product_operations": self.product_operations,
            "cloud_iam_operations": self.cloud_iam_operations,
            "deployment_operations": self.deployment_operations,
            "external_event_operations": self.external_event_operations,
            "protected_operations": self.protected_operations,
            "shell_operations": self.shell_operations,
            "sql_operations": self.sql_operations,
            "network_operations": self.network_operations,
            "dynamic_import_operations": self.dynamic_import_operations,
            "eval_exec_operations": self.eval_exec_operations,
            "reflection_operations": self.reflection_operations,
        }

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return _COUNTER_NAMES

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

_PRODUCT_REFERENCE_TOKENS = (
    "appointment",
    "patient",
    "clinical",
    "diary",
    "emr4",
    "practice",
    "medicare",
    "billing",
    "patient_file",
)

_CREDENTIAL_REQUEST_TOKENS = (
    "api_key",
    "apikey",
    "token",
    "secret",
    "password",
    "credential",
    "adc",
    "service_account",
    "iam",
    "bearer",
)

_SOVEREIGNTY_CLAIM_TOKENS = (
    "australian sovereign",
    "sovereign processing",
    "australia processes",
    "physically processes",
)


def _scan_text(value: str, tokens: tuple[str, ...]) -> bool:
    lowered = value.lower()
    return any(token in lowered for token in tokens)


def _scan_for_executable(value: Any) -> bool:
    if isinstance(value, str):
        return _scan_text(value, _FORBIDDEN_TOKENS)
    if isinstance(value, dict):
        return any(_scan_for_executable(k) or _scan_for_executable(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(_scan_for_executable(item) for item in value)
    return False


def _scan_for_product_reference(value: Any) -> bool:
    if isinstance(value, str):
        return _scan_text(value, _PRODUCT_REFERENCE_TOKENS)
    if isinstance(value, dict):
        return any(_scan_for_product_reference(k) or _scan_for_product_reference(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(_scan_for_product_reference(item) for item in value)
    return False


def _scan_for_credential_request(value: Any) -> bool:
    if isinstance(value, str):
        return _scan_text(value, _CREDENTIAL_REQUEST_TOKENS)
    if isinstance(value, dict):
        return any(_scan_for_credential_request(k) or _scan_for_credential_request(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(_scan_for_credential_request(item) for item in value)
    return False


def _scan_for_sovereignty_claim(value: Any) -> bool:
    if isinstance(value, str):
        return _scan_text(value, _SOVEREIGNTY_CLAIM_TOKENS)
    if isinstance(value, dict):
        return any(_scan_for_sovereignty_claim(k) or _scan_for_sovereignty_claim(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return any(_scan_for_sovereignty_claim(item) for item in value)
    return False

# --------------------------------------------------------------------------- #
# Closed typed objects
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class TargetRef:
    environment: str
    kind: str
    target_id: str

    @classmethod
    def frozen(cls) -> "TargetRef":
        return cls(PLAN_ENVIRONMENT, TARGET_KIND, TARGET_ID)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TargetRef":
        return cls(data["environment"], data["kind"], data["target_id"])

    def to_dict(self) -> dict[str, str]:
        return {"environment": self.environment, "kind": self.kind, "target_id": self.target_id}


@dataclass(frozen=True)
class InternalObservation:
    """An observation that may carry internal-only values (port/PID/nonce/path).

    The provider-visible frame never serializes the internal-only fields.
    """

    observation_id: str
    observation_source_id: str
    kind: str
    observed_at: str
    process_disposition: str
    loopback_health_disposition: str
    generation: Optional[int]
    content_sha256: str
    # internal-only (excluded from provider-visible frames)
    port: Optional[int] = None
    pid: Optional[int] = None
    nonce: Optional[str] = None
    process_path: Optional[str] = None
    environment_names: tuple[str, ...] = ()
    log_excerpt: Optional[str] = None


@dataclass(frozen=True)
class FrameObservation:
    observation_id: str
    observation_source_id: str
    kind: str
    observed_at: str
    freshness_seconds: int
    process_disposition: str
    loopback_health_disposition: str
    generation: Optional[int]
    content_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "observation_source_id": self.observation_source_id,
            "kind": self.kind,
            "observed_at": self.observed_at,
            "freshness_seconds": self.freshness_seconds,
            "process_disposition": self.process_disposition,
            "loopback_health_disposition": self.loopback_health_disposition,
            "generation": self.generation,
            "content_sha256": self.content_sha256,
        }


@dataclass(frozen=True)
class SystemAnatomyFrameSet:
    schema_version: str
    evidence_label: str
    target: TargetRef
    target_reference: str
    service_artifact_sha256: str
    policy_digest: str
    catalog_digest: str
    observations: tuple[FrameObservation, ...]
    runbooks: dict[str, dict[str, Any]]
    risk_tier: str
    required_approval_class: str
    context_absence: tuple[str, ...]
    frame_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "evidence_label": self.evidence_label,
            "target": self.target.to_dict(),
            "target_reference": self.target_reference,
            "service_artifact_sha256": self.service_artifact_sha256,
            "policy_digest": self.policy_digest,
            "catalog_digest": self.catalog_digest,
            "observations": [o.to_dict() for o in self.observations],
            "runbooks": self.runbooks,
            "risk_tier": self.risk_tier,
            "required_approval_class": self.required_approval_class,
            "context_absence": list(self.context_absence),
            "frame_digest": self.frame_digest,
        }

    def digest(self) -> str:
        core = {k: v for k, v in self.to_dict().items() if k != "frame_digest"}
        return canonical_sha256(core)


@dataclass(frozen=True)
class Diagnosis:
    hypothesis: str
    evidence_observation_ids: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    impact: str
    cause: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis": self.hypothesis,
            "evidence_observation_ids": list(self.evidence_observation_ids),
            "missing_evidence": list(self.missing_evidence),
            "impact": self.impact,
            "cause": self.cause,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Diagnosis":
        return cls(
            hypothesis=data["hypothesis"],
            evidence_observation_ids=tuple(data["evidence_observation_ids"]),
            missing_evidence=tuple(data["missing_evidence"]),
            impact=data["impact"],
            cause=data["cause"],
        )


@dataclass(frozen=True)
class RecoveryDiagnosisCandidate:
    schema_version: str
    frame_digest: str
    diagnosis: Diagnosis
    selected_runbook: str
    expected_effect: str
    rollback_runbook_id: str
    risk_tier: str
    target: TargetRef
    parameters: dict
    uncertainty: str
    operator_explanation: str
    success_claim: bool
    executable_content: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "frame_digest": self.frame_digest,
            "diagnosis": self.diagnosis.to_dict(),
            "selected_runbook": self.selected_runbook,
            "expected_effect": self.expected_effect,
            "rollback_runbook_id": self.rollback_runbook_id,
            "risk_tier": self.risk_tier,
            "target": self.target.to_dict(),
            "parameters": self.parameters,
            "uncertainty": self.uncertainty,
            "operator_explanation": self.operator_explanation,
            "success_claim": self.success_claim,
            "executable_content": self.executable_content,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecoveryDiagnosisCandidate":
        return cls(
            schema_version=data["schema_version"],
            frame_digest=data["frame_digest"],
            diagnosis=Diagnosis.from_dict(data["diagnosis"]),
            selected_runbook=data["selected_runbook"],
            expected_effect=data["expected_effect"],
            rollback_runbook_id=data["rollback_runbook_id"],
            risk_tier=data["risk_tier"],
            target=TargetRef.from_dict(data["target"]),
            parameters=data["parameters"],
            uncertainty=data["uncertainty"],
            operator_explanation=data["operator_explanation"],
            success_claim=data["success_claim"],
            executable_content=data["executable_content"],
        )

    def digest(self) -> str:
        return canonical_sha256(self.to_dict())


@dataclass(frozen=True)
class ProofreaderDisposition:
    schema_version: str
    frame_digest: str
    candidate_digest: str
    admitted: bool
    reason_codes: tuple[str, ...]
    grounding: dict[str, bool]
    correction_ticket: Optional[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "frame_digest": self.frame_digest,
            "candidate_digest": self.candidate_digest,
            "admitted": self.admitted,
            "reason_codes": list(self.reason_codes),
            "grounding": dict(self.grounding),
            "correction_ticket": self.correction_ticket,
        }


@dataclass(frozen=True)
class ExecutionApproval:
    schema_version: str
    approval_id: str
    approval_basis: str
    plan_sha256: str
    plan_revision: int
    target: TargetRef
    fault: str
    runbook_id: str
    rollback_runbook_id: str
    provider: dict[str, str]
    cost_ceiling_usd: float
    call_limit: int
    thinking_budget: int
    max_output_tokens: int
    expires_at: str
    rehearsal_count: int
    evidence_label: str
    scope_expansion: bool
    non_transferable: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "approval_id": self.approval_id,
            "approval_basis": self.approval_basis,
            "plan_sha256": self.plan_sha256,
            "plan_revision": self.plan_revision,
            "target": self.target.to_dict(),
            "fault": self.fault,
            "runbook_id": self.runbook_id,
            "rollback_runbook_id": self.rollback_runbook_id,
            "provider": dict(self.provider),
            "cost_ceiling_usd": self.cost_ceiling_usd,
            "call_limit": self.call_limit,
            "thinking_budget": self.thinking_budget,
            "max_output_tokens": self.max_output_tokens,
            "expires_at": self.expires_at,
            "rehearsal_count": self.rehearsal_count,
            "evidence_label": self.evidence_label,
            "scope_expansion": self.scope_expansion,
            "non_transferable": self.non_transferable,
        }

    def digest(self) -> str:
        return canonical_sha256(self.to_dict())


@dataclass(frozen=True)
class ExecutionEvidenceRecord:
    schema_version: str
    evidence_id: str
    reference_sha256: str
    state: str
    approval_id: str
    approval_sha256: str
    plan_sha256: str
    plan_revision: int
    target: TargetRef
    runbook_id: str
    rollback_runbook_id: str
    target_nonce: str
    generation: int
    artifact_sha256: str
    correlation_id: str
    nonce: str
    issued_at: str
    expires_at: str
    supersession_key: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "evidence_id": self.evidence_id,
            "reference_sha256": self.reference_sha256,
            "state": self.state,
            "approval_id": self.approval_id,
            "approval_sha256": self.approval_sha256,
            "plan_sha256": self.plan_sha256,
            "plan_revision": self.plan_revision,
            "target": self.target.to_dict(),
            "runbook_id": self.runbook_id,
            "rollback_runbook_id": self.rollback_runbook_id,
            "target_nonce": self.target_nonce,
            "generation": self.generation,
            "artifact_sha256": self.artifact_sha256,
            "correlation_id": self.correlation_id,
            "nonce": self.nonce,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "supersession_key": self.supersession_key,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionEvidenceRecord":
        return cls(
            schema_version=data["schema_version"],
            evidence_id=data["evidence_id"],
            reference_sha256=data["reference_sha256"],
            state=data["state"],
            approval_id=data["approval_id"],
            approval_sha256=data["approval_sha256"],
            plan_sha256=data["plan_sha256"],
            plan_revision=data["plan_revision"],
            target=TargetRef.from_dict(data["target"]),
            runbook_id=data["runbook_id"],
            rollback_runbook_id=data["rollback_runbook_id"],
            target_nonce=data["target_nonce"],
            generation=data["generation"],
            artifact_sha256=data["artifact_sha256"],
            correlation_id=data["correlation_id"],
            nonce=data["nonce"],
            issued_at=data["issued_at"],
            expires_at=data["expires_at"],
            supersession_key=data["supersession_key"],
        )


@dataclass(frozen=True)
class IssuedEvidence:
    reference: str
    record: ExecutionEvidenceRecord


@dataclass(frozen=True)
class ProviderRequestMetadata:
    model: str
    project: str
    identity: str
    region: str
    endpoint: str
    thinking_budget: int
    max_output_tokens: int
    candidate_count: int
    temperature: int
    call_limit: int
    cost_ceiling_usd: float
    fallback_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": "google_vertex_ai",
            "model": self.model,
            "project": self.project,
            "identity": self.identity,
            "region": self.region,
            "endpoint": self.endpoint,
            "thinking_budget": self.thinking_budget,
            "max_output_tokens": self.max_output_tokens,
            "candidate_count": self.candidate_count,
            "temperature": self.temperature,
            "call_limit": self.call_limit,
            "cost_ceiling_usd": self.cost_ceiling_usd,
            "fallback_enabled": self.fallback_enabled,
        }


@dataclass(frozen=True)
class RunbookCatalogEntry:
    entry_id: str
    runbook_id: str
    rollback_runbook_id: Optional[str]
    operation_class: str
    risk_tier: str
    required_approval_class: str
    target: TargetRef
    parameter_schema: dict
    expected_effect: str
    executable: bool
    immutable: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "runbook_id": self.runbook_id,
            "rollback_runbook_id": self.rollback_runbook_id,
            "operation_class": self.operation_class,
            "risk_tier": self.risk_tier,
            "required_approval_class": self.required_approval_class,
            "target": self.target.to_dict(),
            "parameter_schema": self.parameter_schema,
            "expected_effect": self.expected_effect,
            "executable": self.executable,
            "immutable": self.immutable,
        }


@dataclass(frozen=True)
class RunbookCatalog:
    catalog_version: str
    catalog_digest: str
    entries: tuple[RunbookCatalogEntry, ...]
    immutable: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "catalog_version": self.catalog_version,
            "catalog_digest": self.catalog_digest,
            "entries": [e.to_dict() for e in self.entries],
            "immutable": self.immutable,
        }

    def core_dict(self) -> dict[str, Any]:
        return {
            "catalog_version": self.catalog_version,
            "entries": [e.to_dict() for e in self.entries],
            "immutable": self.immutable,
        }

    def digest(self) -> str:
        return canonical_sha256(self.core_dict())

    @classmethod
    def frozen_catalog(cls) -> "RunbookCatalog":
        entries = (
            RunbookCatalogEntry(
                entry_id=FORWARD_ENTRY_ID,
                runbook_id=FORWARD_RUNBOOK,
                rollback_runbook_id=ROLLBACK_RUNBOOK,
                operation_class="task_owned_loopback_http_service_recovery",
                risk_tier=RISK_TIER,
                required_approval_class=REQUIRED_APPROVAL_CLASS,
                target=TargetRef.frozen(),
                parameter_schema={"type": "object", "properties": {}, "additionalProperties": False},
                expected_effect="fresh_generation_healthy_readback",
                executable=False,
                immutable=True,
            ),
            RunbookCatalogEntry(
                entry_id=ROLLBACK_ENTRY_ID,
                runbook_id=ROLLBACK_RUNBOOK,
                rollback_runbook_id=None,
                operation_class="task_owned_loopback_http_service_recovery",
                risk_tier=RISK_TIER,
                required_approval_class=REQUIRED_APPROVAL_CLASS,
                target=TargetRef.frozen(),
                parameter_schema={"type": "object", "properties": {}, "additionalProperties": False},
                expected_effect="owned_process_absent_connection_refused",
                executable=False,
                immutable=True,
            ),
        )
        catalog = cls(
            catalog_version=CATALOG_VERSION,
            catalog_digest="",
            entries=entries,
            immutable=True,
        )
        return replace(catalog, catalog_digest=catalog.digest())


@dataclass
class IdempotencyRecord:
    key: str
    fingerprint: str
    terminal_receipt: Optional[dict[str, Any]] = None


class C5SharedStore:
    """One shared store/critical section for authority, evidence, idempotency,
    attempt sequence and launch state across every runtime sharing the store.
    """

    def __init__(self) -> None:
        self.transaction_lock = threading.RLock()
        self.evidence_records: dict[str, ExecutionEvidenceRecord] = {}
        self.idempotency_records: dict[str, IdempotencyRecord] = {}
        self.superseded_keys: set[str] = set()
        self.launch_state: str = "not_started"
        self.attempt_audit: list[dict[str, Any]] = []
        self._attempt_sequence = 0

    def next_attempt_id(self) -> str:
        with self.transaction_lock:
            self._attempt_sequence += 1
            return "c5-attempt-%012d" % self._attempt_sequence


# --------------------------------------------------------------------------- #
# Provider request builder (pure; no SDK/network)
# --------------------------------------------------------------------------- #

def build_provider_request_metadata() -> ProviderRequestMetadata:
    return ProviderRequestMetadata(
        model=PROVIDER_MODEL,
        project=PROVIDER_PROJECT,
        identity=PROVIDER_IDENTITY,
        region=PROVIDER_REGION,
        endpoint=PROVIDER_ENDPOINT,
        thinking_budget=THINKING_BUDGET,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        candidate_count=CANDIDATE_COUNT,
        temperature=TEMPERATURE,
        call_limit=CALL_LIMIT,
        cost_ceiling_usd=COST_CEILING_USD,
        fallback_enabled=FALLBACK_ENABLED,
    )


# --------------------------------------------------------------------------- #
# Frame minimisation (exclude port/PID/nonce/path/environment/credential/log/product)
# --------------------------------------------------------------------------- #

def _frame_observation(internal: InternalObservation) -> FrameObservation:
    return FrameObservation(
        observation_id=internal.observation_id,
        observation_source_id=internal.observation_source_id,
        kind=internal.kind,
        observed_at=internal.observed_at,
        freshness_seconds=FRESHNESS_SECONDS,
        process_disposition=internal.process_disposition,
        loopback_health_disposition=internal.loopback_health_disposition,
        generation=internal.generation,
        content_sha256=internal.content_sha256,
    )


def build_system_anatomy_frame_set(
    *,
    target_reference: str,
    service_artifact_sha256: str,
    policy_digest: str,
    catalog_digest: str,
    baseline: InternalObservation,
    post_fault: InternalObservation,
) -> SystemAnatomyFrameSet:
    observations = (_frame_observation(baseline), _frame_observation(post_fault))
    context_absence = (
        "patient",
        "product",
        "database",
        "credential",
        "ordinary_service",
        "port",
        "pid",
        "nonce",
        "path",
        "environment",
        "log",
    )
    runbooks = {
        "forward": {
            "runbook_id": FORWARD_RUNBOOK,
            "description": "Start the pinned C5 disposable loopback service at generation 2.",
            "executable": False,
        },
        "rollback": {
            "runbook_id": ROLLBACK_RUNBOOK,
            "description": "Stop the controller-owned C5 disposable loopback process and prove absence.",
            "executable": False,
        },
    }
    frame = SystemAnatomyFrameSet(
        schema_version=FRAME_SET_SCHEMA,
        evidence_label=OCCUPIED_LABEL,
        target=TargetRef.frozen(),
        target_reference=target_reference,
        service_artifact_sha256=service_artifact_sha256,
        policy_digest=policy_digest,
        catalog_digest=catalog_digest,
        observations=observations,
        runbooks=runbooks,
        risk_tier=RISK_TIER,
        required_approval_class=REQUIRED_APPROVAL_CLASS,
        context_absence=context_absence,
        frame_digest="",
    )
    return replace(frame, frame_digest=frame.digest())


# --------------------------------------------------------------------------- #
# Candidate parser (strict, fail-closed before authority/capability lookup)
# --------------------------------------------------------------------------- #

_ALLOWED_CANDIDATE_KEYS = frozenset(
    {
        "schema_version",
        "frame_digest",
        "diagnosis",
        "selected_runbook",
        "expected_effect",
        "rollback_runbook_id",
        "risk_tier",
        "target",
        "parameters",
        "uncertainty",
        "operator_explanation",
        "success_claim",
        "executable_content",
    }
)
_ALLOWED_DIAGNOSIS_KEYS = frozenset(
    {"hypothesis", "evidence_observation_ids", "missing_evidence", "impact", "cause"}
)
_ALLOWED_TARGET_KEYS = frozenset({"environment", "kind", "target_id"})


def parse_recovery_candidate(
    raw: Any, now: str
) -> tuple[Optional[RecoveryDiagnosisCandidate], Optional[ProofreaderDisposition]]:
    def deny(reason: str) -> tuple[Optional[RecoveryDiagnosisCandidate], Optional[ProofreaderDisposition]]:
        disposition = ProofreaderDisposition(
            schema_version=PROOFREADER_SCHEMA,
            frame_digest="0" * 64,
            candidate_digest="0" * 64,
            admitted=False,
            reason_codes=(reason,),
            grounding={
                "every_hypothesis_grounded": False,
                "exact_stopped_process_diagnosis": False,
                "exact_target_bound": False,
                "exact_runbook_bound": False,
                "exact_rollback_bound": False,
                "risk_tier_bound": False,
                "parameters_empty": False,
                "no_executable_content": False,
                "no_success_claim": False,
                "no_scope_expansion": False,
                "no_product_reference": False,
                "no_credential_request": False,
                "no_new_observation": False,
                "no_hidden_authority": False,
                "no_sovereignty_claim": False,
            },
            correction_ticket=None,
        )
        return None, disposition

    if not isinstance(raw, dict):
        return deny("SCHEMA_REJECTED")
    unknown = set(raw.keys()) - _ALLOWED_CANDIDATE_KEYS
    if unknown:
        return deny("SCHEMA_REJECTED")
    # The whole raw object is scanned for executable content (keys and values).
    if _scan_for_executable(raw):
        return deny("EXECUTABLE_CONTENT_REJECTED")

    # Free-text fields only are screened for product/credential/sovereignty
    # prose.  Constant schema identifiers legitimately contain the repository
    # namespace (``emr4.*``) and must not be treated as product references.
    text_fields = [
        raw.get("hypothesis"),
        raw.get("impact"),
        raw.get("expected_effect"),
        raw.get("uncertainty"),
        raw.get("operator_explanation"),
    ]
    diagnosis_data = raw.get("diagnosis")
    if isinstance(diagnosis_data, dict):
        text_fields.append(diagnosis_data.get("hypothesis"))
        text_fields.append(diagnosis_data.get("impact"))
        text_fields.append(diagnosis_data.get("expected_effect"))
        text_fields.append(diagnosis_data.get("uncertainty"))
        text_fields.append(diagnosis_data.get("operator_explanation"))
        missing = diagnosis_data.get("missing_evidence")
        if isinstance(missing, list):
            text_fields.extend(missing)
    text_fields = [v for v in text_fields if isinstance(v, str)]
    if _scan_for_product_reference(text_fields):
        return deny("PRODUCT_REFERENCE_REJECTED")
    if _scan_for_credential_request(text_fields):
        return deny("CREDENTIAL_REQUEST_REJECTED")
    if _scan_for_sovereignty_claim(text_fields):
        return deny("SOVEREIGNTY_CLAIM_REJECTED")

    if raw.get("schema_version") != CANDIDATE_SCHEMA:
        return deny("SCHEMA_REJECTED")
    frame_digest = raw.get("frame_digest")
    if not isinstance(frame_digest, str) or not _SHA256_RE.match(frame_digest):
        return deny("SCHEMA_REJECTED")
    if raw.get("selected_runbook") != FORWARD_RUNBOOK:
        return deny("UNKNOWN_RUNBOOK")
    if raw.get("rollback_runbook_id") != ROLLBACK_RUNBOOK:
        return deny("UNKNOWN_RUNBOOK")
    if raw.get("risk_tier") != RISK_TIER:
        return deny("RISK_TIER_MISMATCH")
    if raw.get("success_claim") is not False:
        return deny("SUCCESS_CLAIM_REJECTED")
    if raw.get("executable_content") is not False:
        return deny("EXECUTABLE_CONTENT_REJECTED")

    params = raw.get("parameters")
    if not isinstance(params, dict) or params:
        return deny("UNKNOWN_PARAMETER")

    target_data = raw.get("target")
    if not isinstance(target_data, dict) or set(target_data.keys()) != _ALLOWED_TARGET_KEYS:
        return deny("SCHEMA_REJECTED")
    if (
        target_data.get("environment") != PLAN_ENVIRONMENT
        or target_data.get("kind") != TARGET_KIND
        or target_data.get("target_id") != TARGET_ID
    ):
        return deny("SCOPE_EXPANSION_REJECTED")

    diagnosis_data = raw.get("diagnosis")
    if not isinstance(diagnosis_data, dict) or set(diagnosis_data.keys()) != _ALLOWED_DIAGNOSIS_KEYS:
        return deny("SCHEMA_REJECTED")
    if diagnosis_data.get("cause") != "stopped_process":
        return deny("UNSUPPORTED_DIAGNOSIS")
    hypothesis = diagnosis_data.get("hypothesis")
    if not _is_bounded_str(hypothesis, max_len=400):
        return deny("SCHEMA_REJECTED")
    impact = diagnosis_data.get("impact")
    if not _is_bounded_str(impact, max_len=200):
        return deny("SCHEMA_REJECTED")
    evidence_ids = diagnosis_data.get("evidence_observation_ids")
    missing_evidence = diagnosis_data.get("missing_evidence")
    if not isinstance(evidence_ids, list) or not evidence_ids:
        return deny("EVIDENCE_GROUNDING_REJECTED")
    if not all(isinstance(i, str) and _OBS_ID_RE.match(i) for i in evidence_ids):
        return deny("SCHEMA_REJECTED")
    if not isinstance(missing_evidence, list):
        return deny("SCHEMA_REJECTED")
    if not all(isinstance(i, str) and 1 <= len(i) <= 120 for i in missing_evidence):
        return deny("SCHEMA_REJECTED")

    expected_effect = raw.get("expected_effect")
    uncertainty = raw.get("uncertainty")
    explanation = raw.get("operator_explanation")
    for value in (expected_effect, uncertainty, explanation):
        if not _is_bounded_str(value, max_len=400):
            return deny("SCHEMA_REJECTED")

    candidate = RecoveryDiagnosisCandidate(
        schema_version=CANDIDATE_SCHEMA,
        frame_digest=frame_digest,
        diagnosis=Diagnosis(
            hypothesis=hypothesis,
            evidence_observation_ids=tuple(evidence_ids),
            missing_evidence=tuple(missing_evidence),
            impact=impact,
            cause="stopped_process",
        ),
        selected_runbook=FORWARD_RUNBOOK,
        expected_effect=expected_effect,
        rollback_runbook_id=ROLLBACK_RUNBOOK,
        risk_tier=RISK_TIER,
        target=TargetRef.from_dict(target_data),
        parameters={},
        uncertainty=uncertainty,
        operator_explanation=explanation,
        success_claim=False,
        executable_content=False,
    )
    return candidate, None


# --------------------------------------------------------------------------- #
# Deterministic proofreader
# --------------------------------------------------------------------------- #

_GROUNDING_KEYS = (
    "every_hypothesis_grounded",
    "exact_stopped_process_diagnosis",
    "exact_target_bound",
    "exact_runbook_bound",
    "exact_rollback_bound",
    "risk_tier_bound",
    "parameters_empty",
    "no_executable_content",
    "no_success_claim",
    "no_scope_expansion",
    "no_product_reference",
    "no_credential_request",
    "no_new_observation",
    "no_hidden_authority",
    "no_sovereignty_claim",
)


def _grounding(all_true: bool = True) -> dict[str, bool]:
    return {key: all_true for key in _GROUNDING_KEYS}


def proofread_candidate(
    candidate: RecoveryDiagnosisCandidate,
    frame: SystemAnatomyFrameSet,
) -> ProofreaderDisposition:
    candidate_digest = candidate.digest()
    reason_codes: list[str] = []
    grounding = _grounding(True)

    if candidate.frame_digest != frame.frame_digest:
        reason_codes.append("FRAME_DIGEST_MISMATCH")
        grounding["every_hypothesis_grounded"] = False

    frame_observation_ids = {o.observation_id for o in frame.observations}
    evidence_ids = set(candidate.diagnosis.evidence_observation_ids)
    if not evidence_ids:
        reason_codes.append("EVIDENCE_GROUNDING_REJECTED")
        grounding["every_hypothesis_grounded"] = False
    elif not evidence_ids.issubset(frame_observation_ids):
        reason_codes.append("NEW_OBSERVATION_REJECTED")
        grounding["every_hypothesis_grounded"] = False
        grounding["no_new_observation"] = False

    # Only the exact stopped-process diagnosis is eligible.
    if candidate.diagnosis.cause != "stopped_process":
        reason_codes.append("UNSUPPORTED_DIAGNOSIS")
        grounding["exact_stopped_process_diagnosis"] = False

    if candidate.target != frame.target or candidate.target != TargetRef.frozen():
        reason_codes.append("TARGET_MISMATCH")
        grounding["exact_target_bound"] = False
        grounding["no_scope_expansion"] = False

    if candidate.selected_runbook != FORWARD_RUNBOOK:
        reason_codes.append("UNKNOWN_RUNBOOK")
        grounding["exact_runbook_bound"] = False
    if candidate.rollback_runbook_id != ROLLBACK_RUNBOOK:
        reason_codes.append("UNKNOWN_ROLLBACK")
        grounding["exact_rollback_bound"] = False
    if candidate.risk_tier != RISK_TIER:
        reason_codes.append("RISK_TIER_MISMATCH")
        grounding["risk_tier_bound"] = False

    if candidate.parameters != {}:
        reason_codes.append("UNKNOWN_PARAMETER")
        grounding["parameters_empty"] = False

    if candidate.success_claim is not False:
        reason_codes.append("SUCCESS_CLAIM_REJECTED")
        grounding["no_success_claim"] = False

    candidate_texts = [
        candidate.diagnosis.hypothesis,
        candidate.diagnosis.impact,
        candidate.expected_effect,
        candidate.uncertainty,
        candidate.operator_explanation,
        *candidate.diagnosis.missing_evidence,
    ]

    if _scan_for_executable(candidate_texts):
        reason_codes.append("EXECUTABLE_CONTENT_REJECTED")
        grounding["no_executable_content"] = False

    if _scan_for_product_reference(candidate_texts):
        reason_codes.append("PRODUCT_REFERENCE_REJECTED")
        grounding["no_product_reference"] = False

    if _scan_for_credential_request(candidate_texts):
        reason_codes.append("CREDENTIAL_REQUEST_REJECTED")
        grounding["no_credential_request"] = False

    if _scan_for_sovereignty_claim(candidate_texts):
        reason_codes.append("SOVEREIGNTY_CLAIM_REJECTED")
        grounding["no_sovereignty_claim"] = False

    # Explanation must be present and must not itself be a success claim.
    if not candidate.operator_explanation:
        reason_codes.append("EXPLANATION_MISSING")
        grounding["no_hidden_authority"] = False

    admitted = not reason_codes
    correction_ticket: Optional[dict[str, Any]] = None
    if not admitted:
        # At most one closed correction ticket; never reveals preferred prose.
        correction_ticket = {
            "ticket_id": "ticket-c5-0001",
            "field_paths": ["diagnosis", "selected_runbook", "operator_explanation"],
            "reason_codes": reason_codes[:4],
            "frame_digest": frame.frame_digest,
            "open": True,
        }

    return ProofreaderDisposition(
        schema_version=PROOFREADER_SCHEMA,
        frame_digest=frame.frame_digest,
        candidate_digest=candidate_digest,
        admitted=admitted,
        reason_codes=tuple(reason_codes),
        grounding=grounding,
        correction_ticket=correction_ticket,
    )


# --------------------------------------------------------------------------- #
# Approval materialisation (from the fixed Yuri standing-authority basis)
# --------------------------------------------------------------------------- #

def materialise_execution_approval(
    *,
    approval_id: str,
    plan_sha256: str,
    plan_revision: int,
    expires_at: str,
) -> ExecutionApproval:
    if not isinstance(approval_id, str) or not _UUID36_RE.match(approval_id):
        raise ValueError("invalid approval_id")
    if plan_sha256 != PLAN_SHA256:
        raise ValueError("plan hash drift")
    if plan_revision != 1:
        raise ValueError("plan revision drift")
    return ExecutionApproval(
        schema_version=APPROVAL_SCHEMA,
        approval_id=approval_id,
        approval_basis=APPROVAL_BASIS,
        plan_sha256=plan_sha256,
        plan_revision=plan_revision,
        target=TargetRef.frozen(),
        fault="controller_terminates_owned_child",
        runbook_id=FORWARD_RUNBOOK,
        rollback_runbook_id=ROLLBACK_RUNBOOK,
        provider={
            "model": PROVIDER_MODEL,
            "project": PROVIDER_PROJECT,
            "identity": PROVIDER_IDENTITY,
            "region": PROVIDER_REGION,
            "endpoint": PROVIDER_ENDPOINT,
        },
        cost_ceiling_usd=COST_CEILING_USD,
        call_limit=CALL_LIMIT,
        thinking_budget=THINKING_BUDGET,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        expires_at=expires_at,
        rehearsal_count=1,
        evidence_label=OCCUPIED_LABEL,
        scope_expansion=False,
        non_transferable=True,
    )


# --------------------------------------------------------------------------- #
# Evidence issuer (non-caller-selectable cryptographic reference/nonce)
# --------------------------------------------------------------------------- #

def _generate_reference() -> str:
    return secrets.token_hex(32)


def _generate_nonce() -> str:
    return secrets.token_hex(32)


class IssuanceDenied(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class C5EvidenceIssuer:
    """Mints one opaque expiring one-use execution-evidence reference.

    Production issuance always draws the reference and nonce from
    ``secrets.token_hex``; no caller-supplied reference/nonce is accepted.
    The complete check-and-insert for the one effective ``(plan_sha256,
    supersession_key)`` record is protected by the shared-store lock so exactly
    one concurrent mint wins.
    """

    def __init__(self, now: Callable[[], datetime], store: Optional[C5SharedStore] = None) -> None:
        self._now = now
        self._store = store if store is not None else C5SharedStore()
        self._lock = self._store.transaction_lock
        self._issued_keys: set[tuple[str, str]] = set()
        self._sequence = 0

    @property
    def store(self) -> C5SharedStore:
        return self._store

    def mint(
        self,
        *,
        approval: ExecutionApproval,
        target_nonce: str,
        generation: int,
        artifact_sha256: str,
        correlation_id: str,
    ) -> IssuedEvidence:
        now = self._now()
        now_iso = _format_time(now)
        if approval.schema_version != APPROVAL_SCHEMA:
            raise IssuanceDenied("SCHEMA_REJECTED")
        if approval.plan_sha256 != PLAN_SHA256 or approval.plan_revision != 1:
            raise IssuanceDenied("AUTHORITY_MISMATCH")
        if approval.target != TargetRef.frozen():
            raise IssuanceDenied("SCOPE_EXPANSION_REJECTED")
        if approval.runbook_id != FORWARD_RUNBOOK or approval.rollback_runbook_id != ROLLBACK_RUNBOOK:
            raise IssuanceDenied("UNKNOWN_RUNBOOK")
        if approval.cost_ceiling_usd != COST_CEILING_USD or approval.call_limit != CALL_LIMIT:
            raise IssuanceDenied("AUTHORITY_MISMATCH")
        if approval.rehearsal_count != 1 or approval.scope_expansion is not False:
            raise IssuanceDenied("AUTHORITY_MISMATCH")
        if approval.non_transferable is not True:
            raise IssuanceDenied("AUTHORITY_MISMATCH")
        if not isinstance(target_nonce, str) or not _HEX32_64_RE.match(target_nonce):
            raise IssuanceDenied("SCHEMA_REJECTED")
        if generation != 2:
            raise IssuanceDenied("GENERATION_MISMATCH")
        if artifact_sha256 != EXPECTED_ARTIFACT_SHA256:
            raise IssuanceDenied("ARTIFACT_DIGEST_MISMATCH")
        if not isinstance(correlation_id, str) or not _UUID36_RE.match(correlation_id):
            raise IssuanceDenied("SCHEMA_REJECTED")
        if now >= _parse_time(approval.expires_at):
            raise IssuanceDenied("STALE_OR_SUPERSEDED")

        effective_key = (approval.plan_sha256, SUPERSESSION_KEY)
        with self._lock:
            if effective_key in self._issued_keys:
                raise IssuanceDenied("STALE_OR_SUPERSEDED")
            reference = _generate_reference()
            nonce = _generate_nonce()
            reference_sha256 = sha256_hex(reference.encode("utf-8"))
            self._sequence += 1
            evidence_id = "92000000-0000-4000-8000-%012d" % self._sequence
            record = ExecutionEvidenceRecord(
                schema_version=EVIDENCE_SCHEMA,
                evidence_id=evidence_id,
                reference_sha256=reference_sha256,
                state="issued",
                approval_id=approval.approval_id,
                approval_sha256=approval.digest(),
                plan_sha256=approval.plan_sha256,
                plan_revision=approval.plan_revision,
                target=approval.target,
                runbook_id=approval.runbook_id,
                rollback_runbook_id=approval.rollback_runbook_id,
                target_nonce=target_nonce,
                generation=generation,
                artifact_sha256=artifact_sha256,
                correlation_id=correlation_id,
                nonce=nonce,
                issued_at=now_iso,
                expires_at=approval.expires_at,
                supersession_key=SUPERSESSION_KEY,
            )
            self._store.evidence_records[reference_sha256] = record
            self._issued_keys.add(effective_key)
            return IssuedEvidence(reference=reference, record=record)
