#!/usr/bin/env python3
"""Source-gated serial C5 disposable live-development-recovery runner.

This module is never imported by EMR4 product runtime.  It owns one bounded
development-only Vertex diagnosis cell and coordinates the already accepted
C5 controller.  Ordinary tests inject provider-free fakes; the ``run`` command
is admitted only by a fresh exact-HEAD source veto and pre-execution receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess  # nosec B404
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_vertex_sydney_gemini_25_preflight as sydney_preflight
from scripts.model_required_bureau_c5_contract import (
    CALL_LIMIT,
    CANDIDATE_COUNT,
    CATALOG_DIGEST,
    COST_CEILING_USD,
    C5EvidenceIssuer,
    C5SharedStore,
    EXPECTED_ARTIFACT_SHA256,
    FALLBACK_ENABLED,
    FORWARD_RUNBOOK,
    HOST,
    InternalObservation,
    MAX_OUTPUT_TOKENS,
    OCCUPIED_LABEL,
    PLAN_ENVIRONMENT,
    PLAN_SHA256,
    POLICY_DIGEST,
    PROVIDER_ENDPOINT,
    PROVIDER_IDENTITY,
    PROVIDER_MODEL,
    PROVIDER_PROJECT,
    PROVIDER_REGION,
    RISK_TIER,
    ROLLBACK_RUNBOOK,
    TARGET_ID,
    TARGET_KIND,
    TARGET_REFERENCE,
    TEMPERATURE,
    THINKING_BUDGET,
    RecoveryDiagnosisCandidate,
    ProofreaderDisposition,
    build_system_anatomy_frame_set,
    canonical_sha256,
    parse_recovery_candidate,
    proofread_candidate,
    strict_json_loads,
)
from scripts.model_required_bureau_c5_rehearsal import (
    GENERATION_RECOVERED,
    HttpReadbackProbe,
    LiveRecoveryController,
    LoopbackPortAllocator,
    ProcessAdapter,
    TaskDirectoryOps,
    resolve_python_executable,
    resolve_target_module,
)


ARTIFACT_ROOT = ROOT / (
    "orchestration/continuity/"
    "model-required-bureau-c5-disposable-live-development-recovery"
)
PREEXECUTION_SCHEMA = ARTIFACT_ROOT / "live-preexecution-receipt.schema.json"
OCCUPIED_EVIDENCE_SCHEMA = ARTIFACT_ROOT / "occupied-rehearsal-evidence.schema.json"
TARGET_BRANCH = "codex/ariadne-bernie-davida-parallel-seam"
PROTECTED_HEAD = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
SCOPE = "https://www.googleapis.com/auth/cloud-platform"
PROVIDER_PATH = (
    f"/v1/projects/{PROVIDER_PROJECT}/locations/{PROVIDER_REGION}/"
    f"publishers/google/models/{PROVIDER_MODEL}:generateContent"
)
PROVIDER_URL = f"https://{PROVIDER_ENDPOINT}{PROVIDER_PATH}"
MAX_PROVIDER_REQUEST_BYTES = 65536
MAX_PROVIDER_RESPONSE_BYTES = 65536
RESERVED_COST_PER_CALL_USD = 0.25
PREEXECUTION_EXPIRY_SECONDS = 1800
SAFE_CREDENTIAL_RETENTION_FIELD = "credential_or_token_retained"  # nosec B105

PREEXECUTION_ARTIFACTS = (
    "docs/emr4-model-required-bureau-c5-disposable-live-development-recovery-plan.md",
    "docs/emr4-model-required-bureau-c5-live-preexecution-orchestration-boundary.md",
    "docs/security/emr4-model-required-bureau-c5-disposable-live-development-recovery-threat-model-delta.md",
    "docs/security/emr4-model-required-bureau-c5-live-preexecution-orchestration-threat-model-delta.md",
    "docs/api-spine/openapi/technical-control-live-development-recovery-commands.yaml",
    "scripts/model_required_bureau_c5_contract.py",
    "scripts/model_required_bureau_c5_rehearsal.py",
    "scripts/model_required_bureau_c5_target.py",
    "scripts/model_required_bureau_c5_live.py",
    "scripts/model_required_bureau_c5_acceptance.py",
    "scripts/ariadne_vertex_sydney_gemini_25_preflight.py",
    "scripts/ariadne_vertex_sydney_gemini_25_contracts.py",
    "tests/test_model_required_bureau_c5_live.py",
    "tests/test_model_required_bureau_c5_contract.py",
    "tests/test_model_required_bureau_c5_rehearsal.py",
    "orchestration/continuity/ariadne-vertex-sydney-gemini-25/broker-policy.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/c5-policy.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/c5-policy.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/system-anatomy-frame-set.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/system-anatomy-frame-set.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/recovery-diagnosis-candidate.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/recovery-diagnosis-candidate.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/proofreader-disposition.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/proofreader-disposition.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/execution-approval.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/execution-approval.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/execution-evidence.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/execution-evidence.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/live-recovery-command-envelope.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/live-recovery-command-envelope.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/live-recovery-attempt-receipt.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/live-recovery-attempt-receipt.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/cleanup-receipt.example.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/cleanup-receipt.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/live-preexecution-receipt.schema.json",
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery/occupied-rehearsal-evidence.schema.json",
)

REHYDRATION_SOURCES = [
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
]


class C5LiveError(RuntimeError):
    def __init__(self, reason_code: str, *, metadata: Mapping[str, Any] | None = None):
        super().__init__(reason_code)
        self.reason_code = reason_code
        self.metadata = dict(metadata or {})


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _validate(schema_path: Path, value: Mapping[str, Any]) -> None:
    schema = strict_json_loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(dict(value))


def _load_object(path: Path) -> dict[str, Any]:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def _atomic_write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(dict(value), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _git(*arguments: str) -> str:
    git_path = shutil.which("git")
    if git_path is None or not Path(git_path).resolve().is_file():
        raise C5LiveError("git_executable_missing")
    try:
        result = subprocess.run(  # nosec B603
            [str(Path(git_path).resolve()), *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
            shell=False,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise C5LiveError("git_source_gate_failed") from error
    return result.stdout.strip()


def _repository_relative(path: Path, prefix: str) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError as error:
        raise C5LiveError("receipt_path_outside_repository") from error
    if not relative.startswith(prefix):
        raise C5LiveError("receipt_path_scope_invalid")
    return "repository://" + relative


def _current_source_state() -> tuple[str, str, dict[str, str]]:
    head = _git("rev-parse", "HEAD")
    branch = _git("branch", "--show-current")
    tracked_status = _git("status", "--porcelain", "--untracked-files=no")
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise C5LiveError("source_head_invalid")
    if branch != TARGET_BRANCH:
        raise C5LiveError("task_branch_invalid")
    if tracked_status:
        raise C5LiveError("tracked_worktree_not_clean")
    refs = {
        "master": _git("rev-parse", "master"),
        "handoff_current": _git("rev-parse", "handoff/current"),
        "origin_master": _git("rev-parse", "origin/master"),
        "origin_handoff_current": _git("rev-parse", "origin/handoff/current"),
    }
    if set(refs.values()) != {PROTECTED_HEAD}:
        raise C5LiveError("protected_refs_drift")
    return head, branch, refs


def _artifact_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in PREEXECUTION_ARTIFACTS:
        path = (ROOT / relative).resolve()
        if not path.is_file() or ROOT.resolve() not in path.parents:
            raise C5LiveError("preexecution_artifact_missing")
        hashes[relative] = _sha256_file(path)
    return hashes


def _validate_ariadne_authority_binding(
    *,
    ariadne: Mapping[str, Any],
    runtime_state: Mapping[str, Any],
    head: str,
    branch: str,
    refs: Mapping[str, str],
    current: datetime,
) -> dict[str, Any]:
    """Require one fresh five-source state bound to the current Git authority."""
    source_evidence = runtime_state.get("source_evidence")
    binding = runtime_state.get("authority_binding")
    contexts = (runtime_state.get("context_health") or {}).get("agent_contexts")
    orchestrator_context = next(
        (
            item
            for item in contexts or []
            if isinstance(item, dict) and item.get("agent_id") == "orchestrator"
        ),
        None,
    )
    if (
        runtime_state.get("continuation_event") != "pre_sprint_planning"
        or runtime_state.get("planned_action")
        != "execute_frozen_serial_c5_live_rehearsal"
        or not isinstance(source_evidence, dict)
        or set(source_evidence) != set(REHYDRATION_SOURCES)
        or not isinstance(binding, dict)
        or set(binding)
        != {"source_head", "branch", "protected_refs", "recorded_at", "expires_at"}
        or binding.get("source_head") != head
        or binding.get("branch") != branch
        or binding.get("protected_refs") != dict(refs)
        or not isinstance(orchestrator_context, dict)
        or orchestrator_context.get("rehydrated_from_receipt") is not True
        or orchestrator_context.get("rehydration_sources") != REHYDRATION_SOURCES
        or ariadne.get("status") != "passed"
        or ariadne.get("continuation_event") != runtime_state.get("continuation_event")
        or ariadne.get("planned_action") != runtime_state.get("planned_action")
        or ariadne.get("rehydration_sources") != REHYDRATION_SOURCES
        or ariadne.get("source_evidence") != source_evidence
    ):
        raise C5LiveError("ariadne_authority_binding_invalid")
    try:
        recorded_at = _parse_time(binding["recorded_at"])
        expires_at = _parse_time(binding["expires_at"])
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        raise C5LiveError("ariadne_authority_binding_invalid") from error
    current_utc = current.astimezone(timezone.utc)
    if not (
        recorded_at <= current_utc < expires_at
        and expires_at - recorded_at
        <= timedelta(seconds=PREEXECUTION_EXPIRY_SECONDS)
    ):
        raise C5LiveError("ariadne_authority_receipt_expired")
    return dict(binding)


def build_preexecution_receipt(
    *,
    source_review_path: Path,
    ariadne_receipt_path: Path,
    ariadne_runtime_state_path: Path,
    now: Callable[[], datetime] = _now,
) -> dict[str, Any]:
    head, branch, refs = _current_source_state()
    source_review = _load_object(source_review_path)
    if (
        source_review.get("status") != "completed"
        or source_review.get("transport")
        != "antigravity_new_project_bound_readonly_worktree"
        or source_review.get("decision") != "pass"
        or source_review.get("head_before") != head
        or source_review.get("head_after") != head
        or source_review.get("dirty_after") is not False
        or source_review.get("model") != "gemini-3.6-flash-high"
        or source_review.get("reasoning_effort") != "high"
    ):
        raise C5LiveError("source_review_binding_invalid")
    ariadne = _load_object(ariadne_receipt_path)
    ariadne_runtime_state = _load_object(ariadne_runtime_state_path)
    hashes = _artifact_hashes()
    created = now()
    authority_binding = _validate_ariadne_authority_binding(
        ariadne=ariadne,
        runtime_state=ariadne_runtime_state,
        head=head,
        branch=branch,
        refs=refs,
        current=created,
    )
    receipt = {
        "schema_version": "emr4.c5_live_preexecution_receipt.v2",
        "status": "passed",
        "source_head": head,
        "branch": branch,
        "tracked_clean": True,
        "protected_refs": refs,
        "plan_sha256": PLAN_SHA256,
        "policy_digest": POLICY_DIGEST,
        "catalog_digest": CATALOG_DIGEST,
        "source_review": {
            "receipt_path": _repository_relative(
                source_review_path,
                "orchestration/agent_inbox/antigravity/",
            ),
            "receipt_sha256": _sha256_file(source_review_path),
            "status": "completed",
            "transport": "antigravity_new_project_bound_readonly_worktree",
            "decision": "pass",
            "head_before": head,
            "head_after": head,
            "dirty_after": False,
            "model": "gemini-3.6-flash-high",
            "reasoning_effort": "high",
        },
        "ariadne_receipt": {
            "receipt_path": _repository_relative(
                ariadne_receipt_path,
                "orchestration/agent_inbox/codex/",
            ),
            "receipt_sha256": _sha256_file(ariadne_receipt_path),
            "runtime_state_path": _repository_relative(
                ariadne_runtime_state_path,
                "orchestration/agent_inbox/codex/",
            ),
            "runtime_state_sha256": _sha256_file(ariadne_runtime_state_path),
            "status": "passed",
            "continuation_event": "pre_sprint_planning",
            "planned_action": "execute_frozen_serial_c5_live_rehearsal",
            "rehydration_sources": REHYDRATION_SOURCES,
            **authority_binding,
        },
        "provider": {
            "provider": "google_vertex_ai",
            "model": PROVIDER_MODEL,
            "project": PROVIDER_PROJECT,
            "identity": PROVIDER_IDENTITY,
            "region": PROVIDER_REGION,
            "endpoint": PROVIDER_ENDPOINT,
            "thinking_budget": THINKING_BUDGET,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "candidate_count": CANDIDATE_COUNT,
            "temperature": TEMPERATURE,
            "call_limit": CALL_LIMIT,
            "cost_ceiling_usd": COST_CEILING_USD,
            "reserved_cost_per_call_usd": RESERVED_COST_PER_CALL_USD,
            "fallback_enabled": FALLBACK_ENABLED,
            "tools_enabled": False,
            "retrieval_enabled": False,
            "data_class": "newly_authored_patient_free_c5_technical_frames",
        },
        "target": {
            "environment": PLAN_ENVIRONMENT,
            "kind": TARGET_KIND,
            "target_id": TARGET_ID,
            "host": HOST,
            "fault": "controller_terminates_owned_child",
            "forward_runbook": FORWARD_RUNBOOK,
            "rollback_runbook": ROLLBACK_RUNBOOK,
        },
        "artifact_hashes": hashes,
        "artifact_set_sha256": canonical_sha256(hashes),
        "created_at": _format_time(created),
        "expires_at": _format_time(
            created + timedelta(seconds=PREEXECUTION_EXPIRY_SECONDS)
        ),
    }
    _validate(PREEXECUTION_SCHEMA, receipt)
    return receipt


def validate_preexecution_receipt(
    receipt_path: Path,
    *,
    now: Callable[[], datetime] = _now,
) -> dict[str, Any]:
    receipt = _load_object(receipt_path)
    _validate(PREEXECUTION_SCHEMA, receipt)
    head, branch, refs = _current_source_state()
    if (
        receipt["source_head"] != head
        or receipt["branch"] != branch
        or receipt["protected_refs"] != refs
        or receipt["ariadne_receipt"]["source_head"] != head
        or receipt["ariadne_receipt"]["branch"] != branch
        or receipt["ariadne_receipt"]["protected_refs"] != refs
        or receipt["artifact_hashes"] != _artifact_hashes()
        or receipt["artifact_set_sha256"]
        != canonical_sha256(receipt["artifact_hashes"])
    ):
        raise C5LiveError("preexecution_source_binding_invalid")
    current = now().astimezone(timezone.utc)
    if not (_parse_time(receipt["created_at"]) <= current < _parse_time(receipt["expires_at"])):
        raise C5LiveError("preexecution_receipt_expired")
    evidence_files = (
        (
            receipt["source_review"]["receipt_path"],
            receipt["source_review"]["receipt_sha256"],
        ),
        (
            receipt["ariadne_receipt"]["receipt_path"],
            receipt["ariadne_receipt"]["receipt_sha256"],
        ),
        (
            receipt["ariadne_receipt"]["runtime_state_path"],
            receipt["ariadne_receipt"]["runtime_state_sha256"],
        ),
    )
    for relative, expected_sha256 in evidence_files:
        prefix = "repository://"
        if not relative.startswith(prefix):
            raise C5LiveError("preexecution_evidence_path_invalid")
        source = (ROOT / relative[len(prefix):]).resolve()
        if ROOT.resolve() not in source.parents or not source.is_file():
            raise C5LiveError("preexecution_evidence_missing")
        if _sha256_file(source) != expected_sha256:
            raise C5LiveError("preexecution_evidence_digest_drift")
    ariadne_path = (
        ROOT
        / receipt["ariadne_receipt"]["receipt_path"][len("repository://") :]
    ).resolve()
    runtime_state_path = (
        ROOT
        / receipt["ariadne_receipt"]["runtime_state_path"][len("repository://") :]
    ).resolve()
    authority_binding = _validate_ariadne_authority_binding(
        ariadne=_load_object(ariadne_path),
        runtime_state=_load_object(runtime_state_path),
        head=head,
        branch=branch,
        refs=refs,
        current=current,
    )
    if any(
        receipt["ariadne_receipt"].get(key) != value
        for key, value in authority_binding.items()
    ):
        raise C5LiveError("ariadne_authority_summary_drift")
    return receipt


def _provider_response_schema(frame_digest: str, observation_ids: list[str]) -> dict[str, Any]:
    ordered = [
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
    ]
    return {
        "type": "OBJECT",
        "properties": {
            "schema_version": {"type": "STRING", "enum": ["emr4.recovery_diagnosis_candidate.v1"]},
            "frame_digest": {"type": "STRING", "enum": [frame_digest]},
            "diagnosis": {
                "type": "OBJECT",
                "properties": {
                    "hypothesis": {"type": "STRING"},
                    "evidence_observation_ids": {
                        "type": "ARRAY",
                        "items": {"type": "STRING", "enum": observation_ids},
                        "minItems": 1,
                        "maxItems": 2,
                    },
                    "missing_evidence": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                        "maxItems": 8,
                    },
                    "impact": {"type": "STRING"},
                    "cause": {"type": "STRING", "enum": ["stopped_process"]},
                },
                "required": ["hypothesis", "evidence_observation_ids", "missing_evidence", "impact", "cause"],
                "propertyOrdering": ["hypothesis", "evidence_observation_ids", "missing_evidence", "impact", "cause"],
            },
            "selected_runbook": {"type": "STRING", "enum": [FORWARD_RUNBOOK]},
            "expected_effect": {"type": "STRING"},
            "rollback_runbook_id": {"type": "STRING", "enum": [ROLLBACK_RUNBOOK]},
            "risk_tier": {"type": "STRING", "enum": [RISK_TIER]},
            "target": {
                "type": "OBJECT",
                "properties": {
                    "environment": {"type": "STRING", "enum": [PLAN_ENVIRONMENT]},
                    "kind": {"type": "STRING", "enum": [TARGET_KIND]},
                    "target_id": {"type": "STRING", "enum": [TARGET_ID]},
                },
                "required": ["environment", "kind", "target_id"],
                "propertyOrdering": ["environment", "kind", "target_id"],
            },
            "parameters": {"type": "OBJECT", "properties": {}},
            "uncertainty": {"type": "STRING"},
            "operator_explanation": {"type": "STRING"},
            "success_claim": {"type": "BOOLEAN"},
            "executable_content": {"type": "BOOLEAN"},
        },
        "required": ordered,
        "propertyOrdering": ordered,
    }


def build_vertex_request(
    frame: Mapping[str, Any],
    *,
    correction_ticket: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    frame_digest = frame.get("frame_digest")
    observations = frame.get("observations")
    if not isinstance(frame_digest, str) or not isinstance(observations, list):
        raise C5LiveError("provider_frame_invalid")
    observation_ids = [
        item.get("observation_id")
        for item in observations
        if isinstance(item, dict) and isinstance(item.get("observation_id"), str)
    ]
    if len(observation_ids) != 2:
        raise C5LiveError("provider_frame_invalid")
    instructions = [
        "Diagnose only the closed authored-synthetic stopped-process evidence.",
        "Select only the eligible recovery runbook represented in the frame.",
        "Return one complete JSON object matching the response schema.",
        "Cite admitted observation ids. Do not claim recovery success.",
        "Do not include commands, paths, URLs, ports, PIDs, credentials, product references, tools or sovereign-processing claims.",
    ]
    if correction_ticket is not None:
        allowed = {"ticket_id", "field_paths", "reason_codes", "frame_digest", "open"}
        if set(correction_ticket) != allowed or correction_ticket.get("frame_digest") != frame_digest:
            raise C5LiveError("correction_ticket_invalid")
        instructions.extend(
            [
                "The deterministic proofreader issued this closed correction ticket.",
                "Return a complete replacement using the unchanged frame and authority.",
                "CORRECTION_TICKET_JSON:",
                _canonical_bytes(dict(correction_ticket)).decode("utf-8"),
            ]
        )
    instructions.extend(
        [
            "SYSTEM_ANATOMY_FRAME_SET_JSON:",
            _canonical_bytes(dict(frame)).decode("utf-8"),
        ]
    )
    request = {
        "contents": [
            {"role": "user", "parts": [{"text": "\n".join(instructions)}]}
        ],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "candidateCount": CANDIDATE_COUNT,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "thinkingConfig": {"thinkingBudget": THINKING_BUDGET},
            "responseMimeType": "application/json",
            "responseSchema": _provider_response_schema(
                frame_digest, observation_ids
            ),
        },
    }
    if len(_canonical_bytes(request)) > MAX_PROVIDER_REQUEST_BYTES:
        raise C5LiveError("provider_request_oversized")
    return request


def _bounded_provider_metadata(packet: Mapping[str, Any]) -> dict[str, Any]:
    usage = packet.get("usageMetadata")
    safe_usage: dict[str, int] = {}
    if isinstance(usage, dict):
        for key in (
            "promptTokenCount",
            "candidatesTokenCount",
            "thoughtsTokenCount",
            "totalTokenCount",
        ):
            value = usage.get(key)
            if type(value) is int and value >= 0:
                safe_usage[key] = value
    candidates = packet.get("candidates")
    first = candidates[0] if isinstance(candidates, list) and candidates else {}
    finish_reason = first.get("finishReason") if isinstance(first, dict) else None
    allowed_finish = {
        "STOP", "MAX_TOKENS", "SAFETY", "RECITATION", "OTHER", "BLOCKLIST",
        "PROHIBITED_CONTENT", "SPII", "MALFORMED_FUNCTION_CALL", "MODEL_ARMOR",
    }
    if finish_reason not in allowed_finish:
        finish_reason = "UNRECOGNIZED"
    content = first.get("content") if isinstance(first, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    part_kinds: list[str] = []
    if isinstance(parts, list):
        for part in parts[:16]:
            if not isinstance(part, dict):
                part_kinds.append("non_object")
            elif part.get("thought") is True:
                part_kinds.append("thought")
            elif isinstance(part.get("text"), str):
                part_kinds.append("text")
            else:
                part_kinds.append("non_text")
    model_version = packet.get("modelVersion")
    if not (
        isinstance(model_version, str)
        and 1 <= len(model_version) <= 160
        and all(ch.isalnum() or ch in "._:/-" for ch in model_version)
    ):
        model_version = None
    return {
        "candidate_count": len(candidates) if isinstance(candidates, list) else 0,
        "finish_reason": finish_reason,
        "part_kinds": part_kinds,
        "usage": safe_usage,
        "model_version": model_version,
        "provider_text_retained": False,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
        "thought_content_retained": False,
    }


def _safe_provider_attempt_metadata(value: Mapping[str, Any]) -> dict[str, Any]:
    """Project provider evidence to a closed metadata-only allowlist."""
    safe: dict[str, Any] = {}
    boolean_keys = {
        "provider_contacted",
        "raw_provider_response_retained",
        "provider_text_retained",
        "raw_prompt_retained",
        "raw_response_retained",
        "thought_content_retained",
        "error_stream_oversized",
        "provider_error_text_retained",
        "fixture_used",
    }
    integer_keys = {
        "http_status",
        "latency_ms",
        "provider_response_bytes",
        "observed_error_bytes",
        "candidate_count",
    }
    hash_keys = {
        "request_sha256",
        "discarded_provider_response_sha256",
        "discarded_error_sha256",
    }
    for key in boolean_keys:
        if type(value.get(key)) is bool:
            safe[key] = value[key]
    for key in integer_keys:
        item = value.get(key)
        if type(item) is int and item >= 0:
            safe[key] = item
    for key in hash_keys:
        item = value.get(key)
        if (
            isinstance(item, str)
            and len(item) == 64
            and all(character in "0123456789abcdef" for character in item)
        ):
            safe[key] = item
    finish_reason = value.get("finish_reason")
    if finish_reason in {
        "STOP", "MAX_TOKENS", "SAFETY", "RECITATION", "OTHER", "BLOCKLIST",
        "PROHIBITED_CONTENT", "SPII", "MALFORMED_FUNCTION_CALL", "MODEL_ARMOR",
        "UNRECOGNIZED",
    }:
        safe["finish_reason"] = finish_reason
    part_kinds = value.get("part_kinds")
    if (
        isinstance(part_kinds, list)
        and len(part_kinds) <= 16
        and all(
            item in {"text", "thought", "non_text", "non_object"}
            for item in part_kinds
        )
    ):
        safe["part_kinds"] = list(part_kinds)
    usage = value.get("usage")
    if isinstance(usage, dict):
        safe["usage"] = {
            key: item
            for key in (
                "promptTokenCount",
                "candidatesTokenCount",
                "thoughtsTokenCount",
                "totalTokenCount",
            )
            if type(item := usage.get(key)) is int and item >= 0
        }
    model_version = value.get("model_version")
    if model_version == PROVIDER_MODEL:
        safe["model_version"] = model_version
    return safe


def _extract_candidate(packet: dict[str, Any]) -> dict[str, Any]:
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise C5LiveError("provider_candidate_count_invalid")
    candidate = candidates[0]
    content = candidate.get("content") if isinstance(candidate, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise C5LiveError("provider_parts_invalid")
    part = parts[0]
    if not isinstance(part, dict) or part.get("thought") is True:
        raise C5LiveError("provider_part_invalid")
    text = part.get("text")
    if not isinstance(text, str) or len(text.encode("utf-8")) > 32768:
        raise C5LiveError("provider_text_invalid")
    try:
        value = strict_json_loads(text)
    except (json.JSONDecodeError, ValueError) as error:
        raise C5LiveError("provider_candidate_not_json") from error
    text = ""
    return value


@dataclass(frozen=True)
class ProviderCallResult:
    candidate: dict[str, Any]
    metadata: dict[str, Any]


class C5VertexProviderCell:
    is_live_capability = True

    @staticmethod
    def _opener():
        return build_opener(ProxyHandler({}), HTTPSHandler(), _NoRedirectHandler())

    @staticmethod
    def _credentials():
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            raise C5LiveError("google_application_credentials_override_present")
        import google.auth
        from google.auth.transport.requests import Request as GoogleRequest

        try:
            credentials, project = google.auth.default(scopes=[SCOPE])
        except Exception:
            raise C5LiveError("impersonated_adc_discovery_failed") from None
        module = type(credentials).__module__
        target = getattr(credentials, "service_account_email", None)
        target_scopes = set(getattr(credentials, "_target_scopes", []) or [])
        if (
            not module.endswith("impersonated_credentials")
            or project != PROVIDER_PROJECT
            or target != PROVIDER_IDENTITY
            or target_scopes != {SCOPE}
        ):
            raise C5LiveError("impersonated_adc_binding_invalid")
        try:
            credentials.refresh(GoogleRequest())
        except Exception:
            raise C5LiveError("impersonated_adc_refresh_failed") from None
        if not getattr(credentials, "token", None):
            raise C5LiveError("impersonated_adc_refresh_failed")
        return credentials

    def invoke(
        self,
        frame: Mapping[str, Any],
        *,
        correction_ticket: Mapping[str, Any] | None = None,
    ) -> ProviderCallResult:
        request_body = build_vertex_request(
            frame, correction_ticket=correction_ticket
        )
        request_bytes = _canonical_bytes(request_body)
        request_sha256 = hashlib.sha256(request_bytes).hexdigest()
        credentials = self._credentials()
        request = Request(
            PROVIDER_URL,
            data=request_bytes,
            headers={
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        started = time.monotonic()
        contacted = True
        try:
            with self._opener().open(request, timeout=45) as response:
                final_url = response.geturl()
                status = int(response.status)
                raw = response.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
        except HTTPError as error:
            raw_error = error.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
            metadata = {
                "provider_contacted": contacted,
                "http_status": int(error.code),
                "latency_ms": round((time.monotonic() - started) * 1000),
                "discarded_error_sha256": hashlib.sha256(raw_error).hexdigest(),
                "observed_error_bytes": len(raw_error),
                "error_stream_oversized": len(raw_error) > MAX_PROVIDER_RESPONSE_BYTES,
                "provider_error_text_retained": False,
                "request_sha256": request_sha256,
            }
            raw_error = b""
            reason = (
                "provider_redirect_denied"
                if 300 <= int(error.code) < 400
                else "provider_call_failed"
            )
            raise C5LiveError(reason, metadata=metadata) from None
        except (OSError, URLError):
            raise C5LiveError(
                "provider_transport_failed",
                metadata={
                    "provider_contacted": contacted,
                    "request_sha256": request_sha256,
                },
            ) from None
        finally:
            request_body.clear()
            request_bytes = b""
            credentials = None
        metadata = {
            "provider_contacted": True,
            "http_status": status,
            "latency_ms": round((time.monotonic() - started) * 1000),
            "discarded_provider_response_sha256": hashlib.sha256(raw).hexdigest(),
            "provider_response_bytes": len(raw),
            "request_sha256": request_sha256,
            "raw_provider_response_retained": False,
        }
        if final_url != PROVIDER_URL:
            raw = b""
            raise C5LiveError("provider_redirect_denied", metadata=metadata)
        if status != 200:
            raw = b""
            raise C5LiveError("provider_http_status_invalid", metadata=metadata)
        if len(raw) > MAX_PROVIDER_RESPONSE_BYTES:
            raw = b""
            raise C5LiveError("provider_response_oversized", metadata=metadata)
        try:
            packet = strict_json_loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raw = b""
            raise C5LiveError("provider_response_not_json", metadata=metadata) from error
        raw = b""
        safe = {**metadata, **_bounded_provider_metadata(packet)}
        if safe.get("model_version") != PROVIDER_MODEL:
            packet.clear()
            raise C5LiveError("provider_model_version_mismatch", metadata=safe)
        try:
            candidate = _extract_candidate(packet)
        except C5LiveError as error:
            packet.clear()
            raise C5LiveError(error.reason_code, metadata=safe) from None
        packet.clear()
        return ProviderCallResult(candidate=candidate, metadata=safe)


@dataclass
class C5LiveCostLedger:
    maximum_provider_calls: int = CALL_LIMIT
    maximum_cost_usd: float = COST_CEILING_USD
    reserved_cost_per_call_usd: float = RESERVED_COST_PER_CALL_USD
    status: str = "open"
    provider_calls_reserved: int = 0
    provider_calls_consumed: int = 0
    reserved_cost_usd: float = 0.0
    attempts: list[dict[str, Any]] = field(default_factory=list)

    def reserve(self, attempt_kind: str) -> str:
        if self.status != "open" or attempt_kind not in {"primary", "correction"}:
            raise C5LiveError("cost_reservation_invalid")
        if self.provider_calls_consumed + self.provider_calls_reserved >= self.maximum_provider_calls:
            raise C5LiveError("provider_call_limit_exhausted")
        projected = self.reserved_cost_usd + self.reserved_cost_per_call_usd
        if projected > self.maximum_cost_usd:
            raise C5LiveError("provider_cost_ceiling_exhausted")
        self.provider_calls_reserved += 1
        self.reserved_cost_usd = round(projected, 2)
        return f"c5-{attempt_kind}-{len(self.attempts) + 1:03d}"

    def complete(
        self,
        *,
        reservation_id: str,
        attempt_kind: str,
        contacted: bool,
        admitted: bool,
        reason_code: str,
        metadata: Mapping[str, Any],
    ) -> None:
        if self.status != "open" or self.provider_calls_reserved != 1:
            raise C5LiveError("cost_ledger_completion_invalid")
        self.provider_calls_reserved -= 1
        self.reserved_cost_usd = round(
            self.reserved_cost_usd - self.reserved_cost_per_call_usd, 2
        )
        if contacted:
            self.provider_calls_consumed += 1
        self.attempts.append(
            {
                "reservation_id": reservation_id,
                "attempt_kind": attempt_kind,
                "provider_contacted": contacted,
                "admitted": admitted,
                "reason_code": reason_code,
                "metadata": _safe_provider_attempt_metadata(metadata),
            }
        )

    def close(self) -> None:
        self.provider_calls_reserved = 0
        self.reserved_cost_usd = 0.0
        self.status = "closed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "emr4.c5_live_cost_ledger.v1",
            "status": self.status,
            "maximum_provider_calls": self.maximum_provider_calls,
            "maximum_cost_usd": self.maximum_cost_usd,
            "reserved_cost_per_call_usd": self.reserved_cost_per_call_usd,
            "provider_calls_reserved": self.provider_calls_reserved,
            "provider_calls_consumed": self.provider_calls_consumed,
            "reserved_cost_usd": self.reserved_cost_usd,
            "maximum_reserved_cost_consumed_usd": round(
                self.provider_calls_consumed * self.reserved_cost_per_call_usd, 2
            ),
            "fallback_used": False,
            "attempts": list(self.attempts),
        }


class C5CloudPreflight:
    is_live_capability = True

    def verify(self) -> dict[str, Any]:
        try:
            evidence = sydney_preflight.verify_cloud_controls()
        except sydney_preflight.PreflightError as error:
            reason = str(error).split(":", 1)[0]
            raise C5LiveError(reason) from None
        if (
            evidence.get("project") != PROVIDER_PROJECT
            or evidence.get("service_account") != PROVIDER_IDENTITY
            or evidence.get("location") != PROVIDER_REGION
            or evidence.get("endpoint_hostname") != PROVIDER_ENDPOINT
            or evidence.get("model_id") != PROVIDER_MODEL
            or evidence.get("provider_prompt_transmitted") is not False
            or evidence.get("model_inference_called") is not False
            or evidence.get("external_state_changed") is not False
            or not all((evidence.get("checks") or {}).values())
        ):
            raise C5LiveError("provider_preflight_binding_invalid")
        return {
            "result": "c5_exact_sydney_provider_preflight_pass",
            "project": PROVIDER_PROJECT,
            "identity": PROVIDER_IDENTITY,
            "region": PROVIDER_REGION,
            "endpoint": PROVIDER_ENDPOINT,
            "model": PROVIDER_MODEL,
            "authentication": "keyless_impersonated_service_account_adc",
            "provider_prompt_transmitted": False,
            "model_inference_called": False,
            "external_state_changed": False,
            "checks": dict(evidence["checks"]),
        }


def _record_provider_effect(store: C5SharedStore, *, now: Callable[[], datetime]) -> None:
    with store.transaction_lock:
        store.operation_audit.append(
            {
                "counter": "provider_calls",
                "outcome": "contacted",
                "recorded_at": _format_time(now()),
            }
        )


def _call_and_admit(
    *,
    provider: Any,
    ledger: C5LiveCostLedger,
    store: C5SharedStore,
    frame: Any,
    now: Callable[[], datetime],
    correlation_id: str,
    attempt_kind: str,
    correction_ticket: Mapping[str, Any] | None,
) -> tuple[RecoveryDiagnosisCandidate | None, ProofreaderDisposition | None, str | None]:
    reservation_id = ledger.reserve(attempt_kind)
    result: ProviderCallResult | None = None
    try:
        result = provider.invoke(frame.to_dict(), correction_ticket=correction_ticket)
    except C5LiveError as error:
        contacted = (
            getattr(provider, "is_live_capability", False) is True
            and error.metadata.get("provider_contacted") is True
        )
        if contacted:
            _record_provider_effect(store, now=now)
            store.record_provider_failure(
                correlation_id,
                "transport",
                correction_ticket=(
                    dict(correction_ticket) if correction_ticket is not None else None
                ),
            )
        ledger.complete(
            reservation_id=reservation_id,
            attempt_kind=attempt_kind,
            contacted=contacted,
            admitted=False,
            reason_code=error.reason_code,
            metadata=error.metadata,
        )
        raise
    contacted = (
        getattr(provider, "is_live_capability", False) is True
        and result.metadata.get("provider_contacted") is True
    )
    if contacted:
        _record_provider_effect(store, now=now)
    candidate, parse_denial = parse_recovery_candidate(
        result.candidate, _format_time(now())
    )
    result.candidate.clear()
    if candidate is None or parse_denial is not None:
        store.record_provider_failure(
            correlation_id,
            "schema",
            correction_ticket=(
                dict(correction_ticket) if correction_ticket is not None else None
            ),
        )
        reason = (
            parse_denial.reason_codes[0]
            if parse_denial is not None and parse_denial.reason_codes
            else "SCHEMA_REJECTED"
        )
        ledger.complete(
            reservation_id=reservation_id,
            attempt_kind=attempt_kind,
            contacted=contacted,
            admitted=False,
            reason_code=reason.lower(),
            metadata=result.metadata,
        )
        raise C5LiveError("provider_candidate_schema_rejected")
    proofreader = proofread_candidate(candidate, frame)
    admission_or_ticket = store.record_provider_candidate(
        correlation_id=correlation_id,
        frame=frame,
        candidate=candidate,
        disposition=proofreader,
        correction_ticket=(
            dict(correction_ticket) if correction_ticket is not None else None
        ),
    )
    ledger.complete(
        reservation_id=reservation_id,
        attempt_kind=attempt_kind,
        contacted=contacted,
        admitted=proofreader.admitted,
        reason_code=(
            "proofreader_admitted"
            if proofreader.admitted
            else "proofreader_rejected"
        ),
        metadata=result.metadata,
    )
    return candidate, proofreader, admission_or_ticket


def _sanitized_cleanup(receipt: Mapping[str, Any]) -> dict[str, Any]:
    cleaned = dict(receipt)
    removed = cleaned.get("removed_paths")
    cleaned["removed_paths"] = (
        ["task://owned-c5-directory"]
        if isinstance(removed, list) and removed
        else []
    )
    return cleaned


def run_serial_rehearsal(
    *,
    source_head: str,
    preexecution_receipt_sha256: str,
    preflight: Any,
    provider: Any,
    process: Any,
    http: Any,
    port_allocator: Any,
    directory: Any,
    now: Callable[[], datetime] = _now,
) -> tuple[dict[str, Any], dict[str, Any]]:
    store = C5SharedStore()
    python_sha256 = _sha256_file(resolve_python_executable())
    artifact_sha256 = _sha256_file(resolve_target_module())
    if artifact_sha256 != EXPECTED_ARTIFACT_SHA256:
        raise C5LiveError("target_artifact_digest_drift")
    controller = LiveRecoveryController(
        store=store,
        process=process,
        http=http,
        port_allocator=port_allocator,
        directory=directory,
        now=now,
        python_executable_sha256=python_sha256,
    )
    ledger = C5LiveCostLedger()
    provider_preflight: dict[str, Any] = {}
    frame = None
    candidate = None
    proofreader = None
    approval = None
    issued = None
    attempt_receipt = None
    terminal_reason_code: str | None = None
    correction_ticket_used = False
    correlation_id = str(uuid.uuid4())
    cleanup_receipt: dict[str, Any]
    try:
        provider_preflight = preflight.verify()
        target_nonce = os.urandom(32).hex()
        prepared = controller.prepare_runtime(
            target_nonce=target_nonce,
            artifact_sha256=artifact_sha256,
        )
        port = prepared["port"]
        baseline_handle, baseline_healthy = controller.run_baseline(
            port=port,
            nonce=target_nonce,
            artifact_sha256=artifact_sha256,
        )
        if not baseline_healthy:
            raise C5LiveError("baseline_health_not_verified")
        baseline_at = now()
        if not controller.inject_fault(baseline_handle):
            raise C5LiveError("fault_injection_not_verified")
        if not controller.post_fault_verify(baseline_handle, port=port):
            raise C5LiveError("post_fault_absence_not_verified")
        post_fault_at = now()
        controller.reserve_recovery_port()
        baseline = InternalObservation(
            observation_id="baseline-" + os.urandom(8).hex(),
            observation_source_id="obs-source-baseline-" + os.urandom(8).hex(),
            kind="baseline",
            observed_at=_format_time(baseline_at),
            process_disposition="alive",
            loopback_endpoint_disposition="reachable",
            generation=1,
            content_sha256=canonical_sha256(
                {
                    "target_id": TARGET_ID,
                    "artifact_sha256": artifact_sha256,
                    "process": "alive",
                    "health": "reachable",
                    "generation": 1,
                }
            ),
        )
        post_fault = InternalObservation(
            observation_id="post-fault-" + os.urandom(8).hex(),
            observation_source_id="obs-source-post-fault-" + os.urandom(8).hex(),
            kind="post_fault",
            observed_at=_format_time(post_fault_at),
            process_disposition="absent",
            loopback_endpoint_disposition="exact_port_reacquired",
            generation=None,
            content_sha256=canonical_sha256(
                {
                    "target_id": TARGET_ID,
                    "artifact_sha256": artifact_sha256,
                    "process": "absent",
                    "endpoint": "exact_port_reacquired",
                    "generation": None,
                }
            ),
        )
        frame = build_system_anatomy_frame_set(
            target_reference=TARGET_REFERENCE,
            service_artifact_sha256=artifact_sha256,
            policy_digest=POLICY_DIGEST,
            catalog_digest=CATALOG_DIGEST,
            baseline=baseline,
            post_fault=post_fault,
        )
        controller.reserve_provider_ledger(
            correlation_id=correlation_id,
            frame_digest=frame.frame_digest,
        )
        candidate, proofreader, admission = _call_and_admit(
            provider=provider,
            ledger=ledger,
            store=store,
            frame=frame,
            now=now,
            correlation_id=correlation_id,
            attempt_kind="primary",
            correction_ticket=None,
        )
        if proofreader is not None and not proofreader.admitted:
            ticket = proofreader.correction_ticket
            if not isinstance(ticket, dict):
                raise C5LiveError("proofreader_terminal_rejection")
            correction_ticket_used = True
            candidate, proofreader, admission = _call_and_admit(
                provider=provider,
                ledger=ledger,
                store=store,
                frame=frame,
                now=now,
                correlation_id=correlation_id,
                attempt_kind="correction",
                correction_ticket=ticket,
            )
        if (
            candidate is None
            or proofreader is None
            or proofreader.admitted is not True
            or admission is None
        ):
            raise C5LiveError("provider_candidate_not_admitted")
        approval = controller.materialise_approval(
            approval_id=str(uuid.uuid4()),
            expires_at=_format_time(now() + timedelta(seconds=240)),
        )
        issuer = C5EvidenceIssuer(now, store)
        issued = issuer.mint(
            approval=approval,
            frame=frame,
            candidate=candidate,
            proofreader=proofreader,
            provider_admission_digest=admission,
            port=port,
            target_nonce=target_nonce,
            generation=GENERATION_RECOVERED,
            artifact_sha256=artifact_sha256,
            python_executable_sha256=python_sha256,
            correlation_id=correlation_id,
        )
        reference_sha256 = hashlib.sha256(issued.reference.encode("utf-8")).hexdigest()
        if reference_sha256 != issued.record.reference_sha256:
            raise C5LiveError("execution_reference_digest_mismatch")
        attempt_receipt = controller.execute_recovery(
            approval=approval,
            evidence_reference_sha256=reference_sha256,
            candidate=candidate,
            frame=frame,
            proofreader=proofreader,
            provider_admission_digest=admission,
            target_nonce=target_nonce,
            port=port,
            artifact_sha256=artifact_sha256,
            correlation_id=correlation_id,
            idempotency_key=str(uuid.uuid4()),
        )
        if attempt_receipt.get("result") != "live_development_recovery_verified":
            raise C5LiveError("live_readback_not_verified")
    except C5LiveError as error:
        terminal_reason_code = error.reason_code
    except Exception:
        terminal_reason_code = "unexpected_fail_closed"
    finally:
        ledger.close()
        cleanup_receipt = _sanitized_cleanup(
            controller.cleanup(correlation_id=correlation_id)
        )
    passed = (
        terminal_reason_code is None
        and isinstance(attempt_receipt, dict)
        and attempt_receipt.get("result") == "live_development_recovery_verified"
        and cleanup_receipt.get("result") == "cleanup_verified"
        and ledger.provider_calls_consumed in {1, 2}
    )
    if not passed and terminal_reason_code is None:
        terminal_reason_code = "cleanup_or_accounting_not_verified"
    evidence = {
        "schema_version": "emr4.c5_occupied_rehearsal_evidence.v1",
        "result": (
            "model_required_bureau_c5_disposable_live_development_recovery_pass"
            if passed
            else "model_required_bureau_c5_disposable_live_development_recovery_terminal_failure"
        ),
        "terminal_reason_code": terminal_reason_code,
        "evidence_label": OCCUPIED_LABEL,
        "source_head": source_head,
        "preexecution_receipt_sha256": preexecution_receipt_sha256,
        "provider_preflight": provider_preflight,
        "provider_ledger": ledger.to_dict(),
        "frame_digest": frame.frame_digest if frame is not None else None,
        "candidate_digest": candidate.digest() if candidate is not None else None,
        "proofreader": {
            "admitted": proofreader.admitted if proofreader is not None else False,
            "reason_codes": (
                list(proofreader.reason_codes) if proofreader is not None else []
            ),
            "correction_ticket_used": correction_ticket_used,
        },
        "approval_sha256": approval.digest() if approval is not None else None,
        "execution_evidence_sha256": (
            canonical_sha256(issued.record.to_dict()) if issued is not None else None
        ),
        "attempt_receipt": attempt_receipt,
        "cleanup_receipt": cleanup_receipt,
        "operation_counters": cleanup_receipt["operation_counters"],
        "retention": {
            "raw_prompt_retained": False,
            "raw_response_retained": False,
            "provider_text_retained": False,
            "thought_content_retained": False,
            SAFE_CREDENTIAL_RETENTION_FIELD: False,
            "patient_or_product_data_retained": False,
        },
        "claim_boundary": "disposable_authored_synthetic_live_development_recovery_only_not_product_database_deployment_production_release_or_sovereignty_evidence",
        "completed_at": _format_time(now()),
    }
    _validate(OCCUPIED_EVIDENCE_SCHEMA, evidence)
    return evidence, ledger.to_dict()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare-receipt")
    prepare.add_argument("--source-review", type=Path, required=True)
    prepare.add_argument("--ariadne-receipt", type=Path, required=True)
    prepare.add_argument("--ariadne-runtime-state", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--preexecution-receipt", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--cost-ledger", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "prepare-receipt":
            receipt = build_preexecution_receipt(
                source_review_path=args.source_review,
                ariadne_receipt_path=args.ariadne_receipt,
                ariadne_runtime_state_path=args.ariadne_runtime_state,
            )
            _atomic_write(args.output, receipt)
            summary = {
                "result": "c5_live_preexecution_receipt_pass",
                "source_head": receipt["source_head"],
                "output": str(args.output),
            }
            print(json.dumps(summary, sort_keys=True), flush=True)
            return 0
        receipt = validate_preexecution_receipt(args.preexecution_receipt)
        evidence, ledger = run_serial_rehearsal(
            source_head=receipt["source_head"],
            preexecution_receipt_sha256=_sha256_file(args.preexecution_receipt),
            preflight=C5CloudPreflight(),
            provider=C5VertexProviderCell(),
            process=ProcessAdapter(),
            http=HttpReadbackProbe(),
            port_allocator=LoopbackPortAllocator(),
            directory=TaskDirectoryOps(),
        )
        _atomic_write(args.cost_ledger, ledger)
        _atomic_write(args.output, evidence)
        print(
            json.dumps(
                {
                    "result": evidence["result"],
                    "terminal_reason_code": evidence["terminal_reason_code"],
                    "provider_call_count": ledger["provider_calls_consumed"],
                    "cleanup": evidence["cleanup_receipt"]["result"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 0 if evidence["result"].endswith("_pass") else 2
    except (C5LiveError, OSError, ValueError) as error:
        reason = error.reason_code if isinstance(error, C5LiveError) else "preexecution_failed"
        print(
            json.dumps(
                {
                    "result": "model_required_bureau_c5_live_preexecution_blocked",
                    "reason_code": reason,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
