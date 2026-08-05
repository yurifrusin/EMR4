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
from datetime import datetime, timedelta, timezone
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
EXPECTED_ARTIFACT_SHA256 = "a45dd29f2b1bdd4fc70b5bce0a22d6893b295b4001cf22949cd2d2d2927dbd4b"
PLAN_SHA256 = "9f23396e8facadc5f8f1baa3294ebbcdcaeca0bf71b29f95a7743ac80220ac15"
POLICY_DIGEST = "3c876f12269878f3e36ad6a91c7c014f7dc31da593bc4fc1da34f49a22551450"
CATALOG_DIGEST = "610aa502251720dcc779efc5ceb5cbbf7e2e565970ae9dd811d5c0def64f348a"
TARGET_REFERENCE = "c5:recovery-target-0001"
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

_UUID36_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
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
        and 8 <= len(value) <= 128
        and _REF_RE.match(value) is not None
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

    def digest(self) -> str:
        return canonical_sha256(self.to_dict())


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
    port: int
    target_nonce: str
    generation: int
    artifact_sha256: str
    python_executable_sha256: str
    frame_digest: str
    candidate_digest: str
    proofreader_digest: str
    provider_admission_digest: str
    command_material_sha256: str
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
            "port": self.port,
            "target_nonce": self.target_nonce,
            "generation": self.generation,
            "artifact_sha256": self.artifact_sha256,
            "python_executable_sha256": self.python_executable_sha256,
            "frame_digest": self.frame_digest,
            "candidate_digest": self.candidate_digest,
            "proofreader_digest": self.proofreader_digest,
            "provider_admission_digest": self.provider_admission_digest,
            "command_material_sha256": self.command_material_sha256,
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
            port=data["port"],
            target_nonce=data["target_nonce"],
            generation=data["generation"],
            artifact_sha256=data["artifact_sha256"],
            python_executable_sha256=data["python_executable_sha256"],
            frame_digest=data["frame_digest"],
            candidate_digest=data["candidate_digest"],
            proofreader_digest=data["proofreader_digest"],
            provider_admission_digest=data["provider_admission_digest"],
            command_material_sha256=data["command_material_sha256"],
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


@dataclass
class ProviderAttemptState:
    correlation_id: str
    request_digest: str
    frame_digest: str
    call_count: int = 0
    state: str = "reserved"
    rejected_candidate_digest: Optional[str] = None
    correction_ticket_id: Optional[str] = None
    correction_ticket_digest: Optional[str] = None
    admitted_candidate_digest: Optional[str] = None
    admitted_proofreader_digest: Optional[str] = None
    admission_digest: Optional[str] = None


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
        self.provider_attempts: dict[str, ProviderAttemptState] = {}
        self.issued_effective_keys: set[tuple[str, str]] = set()
        self.evidence_sequence = 0
        self.operation_audit: list[dict[str, Any]] = []
        self.cleanup_complete = False
        self._attempt_sequence = 0

    def next_attempt_id(self) -> str:
        with self.transaction_lock:
            self._attempt_sequence += 1
            return "c5-attempt-%012d" % self._attempt_sequence

    def reserve_provider_attempt(
        self,
        *,
        correlation_id: str,
        request_metadata: ProviderRequestMetadata,
        frame_digest: str,
    ) -> ProviderAttemptState:
        if not _UUID36_RE.match(correlation_id) or not _SHA256_RE.match(frame_digest):
            raise ValueError("invalid provider reservation binding")
        if request_metadata != build_provider_request_metadata():
            raise ValueError("provider request metadata drift")
        request_digest = canonical_sha256(request_metadata.to_dict())
        with self.transaction_lock:
            if correlation_id in self.provider_attempts:
                raise ValueError("provider attempt already reserved")
            state = ProviderAttemptState(
                correlation_id=correlation_id,
                request_digest=request_digest,
                frame_digest=frame_digest,
            )
            self.provider_attempts[correlation_id] = state
            return state

    def record_provider_failure(
        self,
        correlation_id: str,
        failure_kind: str,
        *,
        correction_ticket: Optional[dict[str, Any]] = None,
    ) -> None:
        if failure_kind not in {"schema", "transport", "admission"}:
            raise ValueError("invalid provider failure kind")
        with self.transaction_lock:
            state = self.provider_attempts.get(correlation_id)
            if state is None:
                raise ValueError("provider failure is not eligible")
            if state.state == "reserved" and state.call_count == 0:
                if correction_ticket is not None:
                    raise ValueError("primary failure cannot consume a correction ticket")
                state.call_count = 1
            elif state.state == "correction_eligible" and state.call_count == 1:
                if (
                    not isinstance(correction_ticket, dict)
                    or correction_ticket.get("ticket_id")
                    != state.correction_ticket_id
                    or canonical_sha256(correction_ticket)
                    != state.correction_ticket_digest
                ):
                    raise ValueError("correction failure ticket mismatch")
                state.call_count = 2
            else:
                raise ValueError("provider failure is not eligible")
            state.state = "closed_failed"

    def record_provider_candidate(
        self,
        *,
        correlation_id: str,
        frame: SystemAnatomyFrameSet,
        candidate: RecoveryDiagnosisCandidate,
        disposition: ProofreaderDisposition,
        correction_ticket: Optional[dict[str, Any]] = None,
    ) -> str:
        with self.transaction_lock:
            state = self.provider_attempts.get(correlation_id)
            if state is None:
                raise ValueError("provider attempt missing")
            validate_frame_semantics(frame)
            if frame.frame_digest != state.frame_digest:
                raise ValueError("provider frame object drift")
            if candidate.frame_digest != state.frame_digest:
                raise ValueError("provider frame binding drift")
            candidate_digest = candidate.digest()
            disposition_digest = disposition.digest()
            if disposition.frame_digest != state.frame_digest:
                raise ValueError("proofreader frame binding drift")
            if disposition.candidate_digest != candidate_digest:
                raise ValueError("proofreader candidate binding drift")
            if disposition != proofread_candidate(candidate, frame):
                raise ValueError("proofreader disposition was not reproduced")

            if state.state == "reserved" and state.call_count == 0:
                if correction_ticket is not None:
                    raise ValueError("primary call cannot consume a correction ticket")
                state.call_count = 1
            elif state.state == "correction_eligible" and state.call_count == 1:
                if (
                    not isinstance(correction_ticket, dict)
                    or correction_ticket.get("ticket_id") != state.correction_ticket_id
                    or canonical_sha256(correction_ticket) != state.correction_ticket_digest
                ):
                    raise ValueError("correction ticket mismatch")
                if candidate_digest == state.rejected_candidate_digest:
                    raise ValueError("unchanged correction rejected")
                state.call_count = 2
            else:
                raise ValueError("provider call limit or terminal state reached")

            if disposition.admitted:
                state.state = "admitted"
                state.admitted_candidate_digest = candidate_digest
                state.admitted_proofreader_digest = disposition_digest
                state.admission_digest = canonical_sha256(
                    {
                        "correlation_id": correlation_id,
                        "request_digest": state.request_digest,
                        "frame_digest": state.frame_digest,
                        "candidate_digest": candidate_digest,
                        "proofreader_digest": disposition_digest,
                        "call_count": state.call_count,
                        "state": "admitted",
                    }
                )
                return state.admission_digest

            ticket = disposition.correction_ticket
            if state.call_count == 1 and ticket is not None:
                ticket_id = ticket.get("ticket_id")
                if not isinstance(ticket_id, str):
                    raise ValueError("invalid correction ticket")
                state.state = "correction_eligible"
                state.rejected_candidate_digest = candidate_digest
                state.correction_ticket_id = ticket_id
                state.correction_ticket_digest = canonical_sha256(ticket)
                return state.correction_ticket_digest

            state.state = "closed_denied"
            return disposition_digest

    def require_provider_admission(
        self,
        *,
        correlation_id: str,
        admission_digest: str,
        frame_digest: str,
        candidate_digest: str,
        proofreader_digest: str,
    ) -> ProviderAttemptState:
        with self.transaction_lock:
            state = self.provider_attempts.get(correlation_id)
            if (
                state is None
                or state.state != "admitted"
                or state.admission_digest != admission_digest
                or state.frame_digest != frame_digest
                or state.admitted_candidate_digest != candidate_digest
                or state.admitted_proofreader_digest != proofreader_digest
            ):
                raise ValueError("provider admission binding mismatch")
            return state

    def consume_provider_admission(self, correlation_id: str, admission_digest: str) -> None:
        with self.transaction_lock:
            current = self.provider_attempts.get(correlation_id)
            if current is None:
                raise ValueError("provider attempt missing")
            state = self.require_provider_admission(
                correlation_id=correlation_id,
                admission_digest=admission_digest,
                frame_digest=current.frame_digest,
                candidate_digest=current.admitted_candidate_digest or "",
                proofreader_digest=current.admitted_proofreader_digest or "",
            )
            state.state = "consumed"

    def close_provider_attempts(self) -> None:
        with self.transaction_lock:
            for state in self.provider_attempts.values():
                if state.state not in {"consumed", "closed_failed", "closed_denied"}:
                    state.state = "closed_denied"

    def provider_open_count(self) -> int:
        with self.transaction_lock:
            return sum(
                state.state not in {"consumed", "closed_failed", "closed_denied"}
                for state in self.provider_attempts.values()
            )


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
    if not all(
        isinstance(value, str) and _SHA256_RE.match(value)
        for value in (service_artifact_sha256, policy_digest, catalog_digest)
    ):
        raise ValueError("frame digest input is invalid")
    if not _is_opaque_reference(target_reference):
        raise ValueError("target reference is invalid")
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
    frame = replace(frame, frame_digest=frame.digest())
    validate_frame_semantics(frame)
    return frame


def validate_frame_semantics(
    frame: SystemAnatomyFrameSet,
    *,
    now: Optional[datetime] = None,
) -> None:
    """Validate the exact two-observation C5 failure frame.

    Structural closure alone is insufficient: the model may see exactly one
    healthy generation-1 baseline followed by one absent/refused post-fault
    observation, with distinct observation and source identities.
    """
    if frame.schema_version != FRAME_SET_SCHEMA or frame.target != TargetRef.frozen():
        raise ValueError("frame target or schema drift")
    if frame.evidence_label != OCCUPIED_LABEL or frame.risk_tier != RISK_TIER:
        raise ValueError("frame authority drift")
    if frame.required_approval_class != REQUIRED_APPROVAL_CLASS:
        raise ValueError("frame approval class drift")
    if (
        frame.target_reference != TARGET_REFERENCE
        or frame.service_artifact_sha256 != EXPECTED_ARTIFACT_SHA256
        or frame.policy_digest != POLICY_DIGEST
        or frame.catalog_digest != CATALOG_DIGEST
    ):
        raise ValueError("frame source binding drift")
    expected_runbooks = {
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
    expected_absence = (
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
    if frame.runbooks != expected_runbooks or frame.context_absence != expected_absence:
        raise ValueError("frame runbook or context-absence drift")
    if frame.frame_digest != frame.digest():
        raise ValueError("frame digest drift")
    if len(frame.observations) != 2:
        raise ValueError("frame must contain exactly two observations")
    baseline, post_fault = frame.observations
    if (
        baseline.kind != "baseline"
        or baseline.process_disposition != "alive"
        or baseline.loopback_health_disposition != "reachable"
        or baseline.generation != 1
    ):
        raise ValueError("baseline observation semantics invalid")
    if (
        post_fault.kind != "post_fault"
        or post_fault.process_disposition != "absent"
        or post_fault.loopback_health_disposition != "connection_refused"
        or post_fault.generation is not None
    ):
        raise ValueError("post-fault observation semantics invalid")
    if baseline.observation_id == post_fault.observation_id:
        raise ValueError("observation ids must be distinct")
    if baseline.observation_source_id == post_fault.observation_source_id:
        raise ValueError("observation source ids must be distinct")
    if baseline.content_sha256 == post_fault.content_sha256:
        raise ValueError("observation content digests must be distinct")
    for observation in frame.observations:
        if not _OBS_ID_RE.match(observation.observation_id):
            raise ValueError("observation id invalid")
        if not observation.observation_source_id.startswith("obs-"):
            raise ValueError("observation source invalid")
        if observation.freshness_seconds != FRESHNESS_SECONDS:
            raise ValueError("observation freshness contract drift")
        if not _SHA256_RE.match(observation.content_sha256):
            raise ValueError("observation content digest invalid")
        observed_at = _parse_time(observation.observed_at)
        if observed_at.tzinfo is None:
            raise ValueError("observation timestamp must be timezone-aware")
        if now is not None:
            age = (now.astimezone(timezone.utc) - observed_at.astimezone(timezone.utc)).total_seconds()
            if age < 0 or age > observation.freshness_seconds:
                raise ValueError("observation is stale or future-dated")
    if _parse_time(post_fault.observed_at) < _parse_time(baseline.observed_at):
        raise ValueError("post-fault observation must follow baseline")


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
    if set(raw.keys()) != _ALLOWED_CANDIDATE_KEYS:
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
    if not isinstance(evidence_ids, list) or not 1 <= len(evidence_ids) <= 8:
        return deny("EVIDENCE_GROUNDING_REJECTED")
    if not all(isinstance(i, str) and _OBS_ID_RE.match(i) for i in evidence_ids):
        return deny("SCHEMA_REJECTED")
    if len(set(evidence_ids)) != len(evidence_ids):
        return deny("SCHEMA_REJECTED")
    if not isinstance(missing_evidence, list) or len(missing_evidence) > 8:
        return deny("SCHEMA_REJECTED")
    if not all(isinstance(i, str) and 1 <= len(i) <= 120 for i in missing_evidence):
        return deny("SCHEMA_REJECTED")
    if len(set(missing_evidence)) != len(missing_evidence):
        return deny("SCHEMA_REJECTED")

    expected_effect = raw.get("expected_effect")
    uncertainty = raw.get("uncertainty")
    explanation = raw.get("operator_explanation")
    if not _is_bounded_str(expected_effect, max_len=200):
        return deny("SCHEMA_REJECTED")
    if not _is_bounded_str(uncertainty, max_len=200):
        return deny("SCHEMA_REJECTED")
    if not _is_bounded_str(explanation, max_len=400):
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

    try:
        validate_frame_semantics(frame)
    except ValueError:
        reason_codes.append("FRAME_SEMANTICS_REJECTED")
        grounding["every_hypothesis_grounded"] = False
        grounding["exact_stopped_process_diagnosis"] = False

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

    post_fault_ids = {
        observation.observation_id
        for observation in frame.observations
        if observation.kind == "post_fault"
        and observation.process_disposition == "absent"
        and observation.loopback_health_disposition == "connection_refused"
    }
    if not post_fault_ids or not post_fault_ids.issubset(evidence_ids):
        reason_codes.append("POST_FAULT_EVIDENCE_REQUIRED")
        grounding["every_hypothesis_grounded"] = False
        grounding["exact_stopped_process_diagnosis"] = False

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
        ticket_digest = canonical_sha256(
            {
                "frame_digest": frame.frame_digest,
                "candidate_digest": candidate_digest,
                "reason_codes": reason_codes[:4],
            }
        )
        correction_ticket = {
            "ticket_id": "ticket-c5-" + ticket_digest[:16],
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


def validate_execution_approval(
    approval: ExecutionApproval,
    *,
    now: datetime,
) -> None:
    """Revalidate every frozen approval field against current time."""
    if approval.schema_version != APPROVAL_SCHEMA:
        raise ValueError("approval schema drift")
    if not _UUID36_RE.match(approval.approval_id):
        raise ValueError("approval id drift")
    if approval.approval_basis != APPROVAL_BASIS:
        raise ValueError("approval basis drift")
    if approval.plan_sha256 != PLAN_SHA256 or approval.plan_revision != 1:
        raise ValueError("approval plan drift")
    if approval.target != TargetRef.frozen():
        raise ValueError("approval target drift")
    if approval.fault != "controller_terminates_owned_child":
        raise ValueError("approval fault drift")
    if approval.runbook_id != FORWARD_RUNBOOK or approval.rollback_runbook_id != ROLLBACK_RUNBOOK:
        raise ValueError("approval runbook drift")
    expected_provider = {
        "model": PROVIDER_MODEL,
        "project": PROVIDER_PROJECT,
        "identity": PROVIDER_IDENTITY,
        "region": PROVIDER_REGION,
        "endpoint": PROVIDER_ENDPOINT,
    }
    if approval.provider != expected_provider:
        raise ValueError("approval provider drift")
    if approval.cost_ceiling_usd != COST_CEILING_USD or approval.call_limit != CALL_LIMIT:
        raise ValueError("approval cost or call drift")
    if approval.thinking_budget != THINKING_BUDGET or approval.max_output_tokens != MAX_OUTPUT_TOKENS:
        raise ValueError("approval reasoning envelope drift")
    if approval.rehearsal_count != 1:
        raise ValueError("approval rehearsal drift")
    if approval.evidence_label != OCCUPIED_LABEL:
        raise ValueError("approval evidence label drift")
    if approval.scope_expansion is not False or approval.non_transferable is not True:
        raise ValueError("approval scope or transfer drift")
    expires_at = _parse_time(approval.expires_at)
    now_utc = now.astimezone(timezone.utc)
    if expires_at <= now_utc or expires_at > now_utc + timedelta(seconds=EXPIRY_SECONDS):
        raise ValueError("approval expiry is stale or over-broad")


def build_command_material_digest(
    *,
    approval: ExecutionApproval,
    port: int,
    target_nonce: str,
    generation: int,
    artifact_sha256: str,
    python_executable_sha256: str,
    frame_digest: str,
    candidate_digest: str,
    proofreader_digest: str,
    provider_admission_digest: str,
    correlation_id: str,
) -> str:
    return canonical_sha256(
        {
            "schema_version": ENVELOPE_SCHEMA,
            "evidence_label": OCCUPIED_LABEL,
            "approval_sha256": approval.digest(),
            "runbook_id": FORWARD_RUNBOOK,
            "rollback_runbook_id": ROLLBACK_RUNBOOK,
            "target": TargetRef.frozen().to_dict(),
            "host": HOST,
            "port": port,
            "generation": generation,
            "target_nonce": target_nonce,
            "artifact_sha256": artifact_sha256,
            "python_executable_sha256": python_executable_sha256,
            "frame_digest": frame_digest,
            "candidate_digest": candidate_digest,
            "proofreader_digest": proofreader_digest,
            "provider_admission_digest": provider_admission_digest,
            "correlation_id": correlation_id,
            "parameters": {},
        }
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

    @property
    def store(self) -> C5SharedStore:
        return self._store

    def mint(
        self,
        *,
        approval: ExecutionApproval,
        frame: SystemAnatomyFrameSet,
        candidate: RecoveryDiagnosisCandidate,
        proofreader: ProofreaderDisposition,
        provider_admission_digest: str,
        port: int,
        target_nonce: str,
        generation: int,
        artifact_sha256: str,
        python_executable_sha256: str,
        correlation_id: str,
    ) -> IssuedEvidence:
        now = self._now()
        now_iso = _format_time(now)
        try:
            validate_execution_approval(approval, now=now)
        except ValueError as error:
            reason = "STALE_OR_SUPERSEDED" if "expiry" in str(error) else "AUTHORITY_MISMATCH"
            raise IssuanceDenied(reason) from error
        try:
            validate_frame_semantics(frame, now=now)
        except ValueError as error:
            raise IssuanceDenied("FRAME_INVALID") from error
        if candidate.frame_digest != frame.frame_digest:
            raise IssuanceDenied("FRAME_DIGEST_MISMATCH")
        if proofreader.admitted is not True or proofreader.reason_codes:
            raise IssuanceDenied("PROOFREADER_REJECTED")
        if proofreader.frame_digest != frame.frame_digest:
            raise IssuanceDenied("FRAME_DIGEST_MISMATCH")
        if proofreader.candidate_digest != candidate.digest():
            raise IssuanceDenied("CANDIDATE_DIGEST_MISMATCH")
        if proofreader.correction_ticket is not None or not all(proofreader.grounding.values()):
            raise IssuanceDenied("PROOFREADER_REJECTED")
        if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
            raise IssuanceDenied("PORT_MISMATCH")
        if not _SHA256_RE.match(python_executable_sha256):
            raise IssuanceDenied("EXECUTABLE_DIGEST_MISMATCH")
        if not _SHA256_RE.match(provider_admission_digest):
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

        candidate_digest = candidate.digest()
        proofreader_digest = proofreader.digest()
        command_material_sha256 = build_command_material_digest(
            approval=approval,
            port=port,
            target_nonce=target_nonce,
            generation=generation,
            artifact_sha256=artifact_sha256,
            python_executable_sha256=python_executable_sha256,
            frame_digest=frame.frame_digest,
            candidate_digest=candidate_digest,
            proofreader_digest=proofreader_digest,
            provider_admission_digest=provider_admission_digest,
            correlation_id=correlation_id,
        )

        effective_key = (approval.plan_sha256, SUPERSESSION_KEY)
        with self._lock:
            try:
                self._store.require_provider_admission(
                    correlation_id=correlation_id,
                    admission_digest=provider_admission_digest,
                    frame_digest=frame.frame_digest,
                    candidate_digest=candidate_digest,
                    proofreader_digest=proofreader_digest,
                )
            except ValueError as error:
                raise IssuanceDenied("PROVIDER_ADMISSION_MISMATCH") from error
            if effective_key in self._store.issued_effective_keys:
                raise IssuanceDenied("STALE_OR_SUPERSEDED")
            reference = _generate_reference()
            nonce = _generate_nonce()
            reference_sha256 = sha256_hex(reference.encode("utf-8"))
            self._store.evidence_sequence += 1
            evidence_id = "92000000-0000-4000-8000-%012d" % self._store.evidence_sequence
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
                port=port,
                target_nonce=target_nonce,
                generation=generation,
                artifact_sha256=artifact_sha256,
                python_executable_sha256=python_executable_sha256,
                frame_digest=frame.frame_digest,
                candidate_digest=candidate_digest,
                proofreader_digest=proofreader_digest,
                provider_admission_digest=provider_admission_digest,
                command_material_sha256=command_material_sha256,
                correlation_id=correlation_id,
                nonce=nonce,
                issued_at=now_iso,
                expires_at=approval.expires_at,
                supersession_key=SUPERSESSION_KEY,
            )
            self._store.evidence_records[reference_sha256] = record
            self._store.issued_effective_keys.add(effective_key)
            return IssuedEvidence(reference=reference, record=record)
