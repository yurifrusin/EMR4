"""AES-C4 one-call authored-synthetic brokered provider proof.

The default ``provider-free`` mode performs no network or credential operation.
``live`` is fail-closed behind an exact sanitized cloud preflight and one
durable call/cost ledger.  The external broker owns ADC and operation identity;
candidate/model content receives neither.
"""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import (  # noqa: E402
    raisa_agent_execution_surface_containment_gate_aes_c1_admission as c1,
)


BASE = ROOT / (
    "orchestration/continuity/"
    "raisa-agent-execution-surface-containment-gate-aes-c4"
)
ENVELOPE_PATH = BASE / "provider-envelope.json"
ENVELOPE_SCHEMA_PATH = BASE / "provider-envelope.schema.json"

INHERITED_ARTIFACT_DIGESTS = {
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json": "sha256:403c7ddac2399760395d60a8094ffe42d2519a4a809bc8a59104acd2883eb9ae",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json": "sha256:344d88c59a5d781ebb205de575b66f2e3d64f3878f73c9c0bf4d86eb996b1740",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json": "sha256:241f081b1c3346ef50e80eb495c9bfb6ea3b99f67956b439c7c7638962069f90",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json": "sha256:2e6c5b83d379f5b6f900fa0a26a8733b6fe09496ff8e1c52d5ed40123603e9b6",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.json": "sha256:530c9c3067725f6078785e846fa82c0ebb89f72d0a8feeb5c2916d567b5a4ccf",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.schema.json": "sha256:895f1afc8c4d7f58ba0a8032f54f274496d93e1601e9ce40444d642d4bf0c175",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.json": "sha256:4b4e94b07823576b469921308fd46f741d02834f860759db56985285ceb67d3e",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.schema.json": "sha256:fc9e1ae2e42e6178586c51faabf1dabc7ae292d9889091b310a8fd9c021e3de1",
}

CAPABILITY_ID = "capability-aes-c4-sydney-vertex-provider-inference"
ADAPTER_ID = "vertex-generate-content-broker-adapter-v1"
OPERATION_ID = "generate-aes-c4-authored-synthetic-proof"
DESTINATION_ID = "vertex-sydney-gemini-25"
AUDIENCE = "google-vertex-ai-prediction"
GENERATION_ID = "generation-aes-c4-sydney-vertex-001"
MANIFEST_ID = "manifest-aes-c4-sydney-vertex-001"
LEASE_ID = "lease-aes-c4-sydney-vertex-001"
PURPOSE_CODE = "aes-c4-authored-synthetic-provider-containment-proof"
BUREAU_ID = "bureau-raisa-containment"
WORK_CELL_ID = "work-cell-aes-c4-provider-001"
SYNTHETIC_NONCE = "aes-c4-synthetic-nonce-001"
ZERO_HASH = "sha256:" + "0" * 64

PROVIDER_INSTRUCTIONS_VERSION = "emr4.aes_c4.provider_instructions.v1"
RELEASE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "decision_code": {"type": "STRING", "enum": ["contained"]},
        "synthetic_nonce": {"type": "STRING", "enum": [SYNTHETIC_NONCE]},
        "summary_code": {
            "type": "STRING",
            "enum": ["broker_boundary_confirmed"],
        },
        "command_authority": {"type": "BOOLEAN"},
    },
    "required": [
        "decision_code",
        "synthetic_nonce",
        "summary_code",
        "command_authority",
    ],
    "propertyOrdering": [
        "decision_code",
        "synthetic_nonce",
        "summary_code",
        "command_authority",
    ],
}

SAFE_FINISH_REASONS = {
    "STOP",
    "MAX_TOKENS",
    "SAFETY",
    "RECITATION",
    "OTHER",
    "BLOCKLIST",
    "PROHIBITED_CONTENT",
    "SPII",
    "MALFORMED_FUNCTION_CALL",
    "MODEL_ARMOR",
}
FORBIDDEN_SELECTOR_KEYS = {
    "capability",
    "capability_id",
    "adapter",
    "adapter_id",
    "operation",
    "operation_id",
    "destination",
    "destination_id",
    "url",
    "method",
    "audience",
    "credential",
    "credential_reference",
    "path",
    "filesystem_path",
    "sql",
    "executable",
    "tool",
    "tool_definition",
    "command_route",
    "cleanup_target",
    "policy_amendment",
}


class AesC4Error(RuntimeError):
    def __init__(self, reason_code: str, *, metadata: dict[str, Any] | None = None):
        super().__init__(reason_code)
        self.reason_code = reason_code
        self.metadata = metadata or {}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def digest_of(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate_key:{key}")
        result[key] = value
    return result


def strict_json_loads(value: str) -> Any:
    return json.loads(value, object_pairs_hook=_reject_duplicate_pairs)


def load_json(path: Path) -> dict[str, Any]:
    value = strict_json_loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AesC4Error("json_artifact_not_object")
    return value


def atomic_write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def _nested_forbidden_keys(value: Any) -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_SELECTOR_KEYS:
                hits.append(key)
            hits.extend(_nested_forbidden_keys(item))
    elif isinstance(value, list):
        for item in value:
            hits.extend(_nested_forbidden_keys(item))
    return hits


def validate_inherited_artifacts() -> None:
    for relative, expected in INHERITED_ARTIFACT_DIGESTS.items():
        path = ROOT / relative
        if not path.is_file() or file_digest(path) != expected:
            raise AesC4Error("inherited_artifact_digest_mismatch")


def validate_envelope() -> dict[str, Any]:
    envelope = load_json(ENVELOPE_PATH)
    schema = load_json(ENVELOPE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(envelope),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise AesC4Error("provider_envelope_schema_invalid")

    binding = envelope["provider_binding"]
    exact_binding = {
        "provider": "google_vertex_ai",
        "model_id": "gemini-2.5-flash",
        "project": "bernie-emr4-dev",
        "quota_project": "bernie-emr4-dev",
        "service_account": (
            "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
        ),
        "authentication": "keyless_impersonated_service_account_adc",
        "oauth_scope": "https://www.googleapis.com/auth/cloud-platform",
        "required_permission": "aiplatform.endpoints.predict",
        "location": "australia-southeast1",
        "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
        "request_path": (
            "/v1/projects/bernie-emr4-dev/locations/australia-southeast1/"
            "publishers/google/models/gemini-2.5-flash:generateContent"
        ),
    }
    for key, expected in exact_binding.items():
        if binding.get(key) != expected:
            raise AesC4Error(f"provider_envelope_binding_invalid:{key}")

    request = envelope["request_contract"]
    exact_request = {
        "candidate_count": 1,
        "temperature": 0,
        "thinking_budget_tokens": 1024,
        "maximum_output_tokens": 2048,
        "maximum_request_bytes": 8192,
        "maximum_provider_response_bytes": 16384,
        "maximum_provider_error_bytes": 65536,
        "provider_http_timeout_seconds": 45,
        "provider_tools": False,
        "function_calling": False,
        "grounding": False,
        "retrieval": False,
        "code_execution": False,
        "explicit_context_cache": False,
        "automatic_fallback": False,
    }
    if request != exact_request:
        raise AesC4Error("provider_envelope_request_contract_invalid")
    cost = envelope["call_and_cost_boundary"]
    if (
        cost["maximum_provider_calls"] != 1
        or cost["maximum_retries"] != 0
        or cost["application_cost_ceiling_usd"] != 0.25
        or cost["reserved_cost_per_call_usd"] != 0.25
    ):
        raise AesC4Error("provider_envelope_cost_contract_invalid")
    if any(
        envelope["data_boundary"][key]
        for key in envelope["data_boundary"]
        if key != "classification"
    ):
        raise AesC4Error("provider_envelope_data_boundary_invalid")
    return envelope


def validate_preflight(path: Path) -> dict[str, Any]:
    value = load_json(path)
    required = {
        "authentication": "keyless_impersonated_service_account_adc",
        "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
        "location": "australia-southeast1",
        "model_id": "gemini-2.5-flash",
        "oauth_scope": "https://www.googleapis.com/auth/cloud-platform",
        "project": "bernie-emr4-dev",
        "required_prediction_permission": "aiplatform.endpoints.predict",
        "service_account": (
            "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
        ),
        "external_state_changed": False,
        "model_inference_called": False,
        "provider_prompt_transmitted": False,
        "api_key_authentication_used": False,
        "service_account_key_used": False,
        "result": "ariadne_vertex_sydney_gemini_25_adc_preflight_pass",
    }
    for key, expected in required.items():
        if value.get(key) != expected:
            raise AesC4Error(f"preflight_invalid:{key}")
    checks = value.get("checks")
    if not isinstance(checks, dict) or not checks or any(v is not True for v in checks.values()):
        raise AesC4Error("preflight_controls_not_all_passed")
    return value


def build_synthetic_packet(manifest_digest: str) -> dict[str, Any]:
    if not (
        isinstance(manifest_digest, str)
        and len(manifest_digest) == 71
        and manifest_digest.startswith("sha256:")
        and all(character in "0123456789abcdef" for character in manifest_digest[7:])
    ):
        raise AesC4Error("synthetic_packet_manifest_digest_invalid")
    return {
        "schema_version": "emr4.aes_c4.synthetic_packet.v1",
        "synthetic_nonce": SYNTHETIC_NONCE,
        "generation_manifest_digest": manifest_digest,
        "assertions": [
            "broker_owns_operation_identity",
            "work_cell_has_no_credential",
            "output_has_no_command_authority",
        ],
        "command_authority": False,
    }


def proofread_input(
    packet: Mapping[str, Any], *, expected_manifest_digest: str
) -> dict[str, Any]:
    expected = build_synthetic_packet(expected_manifest_digest)
    if dict(packet) != expected:
        raise AesC4Error("predispatch_candidate_invalid")
    if _nested_forbidden_keys(packet):
        raise AesC4Error("predispatch_candidate_selector_present")
    return {
        "schema_version": "emr4.aes_c4.predispatch_proofreader.v1",
        "admitted": True,
        "packet_digest": digest_of(packet),
        "generation_manifest_digest": expected_manifest_digest,
        "command_authority": False,
    }


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _authority_digest() -> str:
    return digest_of(
        {
            "purpose_code": PURPOSE_CODE,
            "bureau_id": BUREAU_ID,
            "work_cell_id": WORK_CELL_ID,
            "principal": "yuri-standing-aes-c4-authority-2026-08-11",
        }
    )


def _budgets(envelope: Mapping[str, Any]) -> dict[str, Any]:
    request = envelope["request_contract"]
    return {
        "reasoning": {"max_model_calls": 1, "max_model_tokens": 4096},
        "information": {
            "max_input_bytes": request["maximum_request_bytes"],
            "max_output_bytes": request["maximum_provider_response_bytes"],
            "max_source_count": 1,
        },
        "egress": {
            "max_requests": 1,
            "max_request_bytes": request["maximum_request_bytes"],
            "max_response_bytes": request["maximum_provider_response_bytes"],
            "max_total_bytes": (
                request["maximum_request_bytes"]
                + request["maximum_provider_response_bytes"]
            ),
            "max_distinct_destinations": 1,
            "max_redirects": 0,
        },
        "action": {
            "max_broker_operations": 1,
            "max_inert_tool_operations": 0,
            "max_product_mutations": 0,
            "max_command_confirmations": 0,
        },
        "denial": {
            "max_denials": 1,
            "max_boundary_probes": 1,
            "max_repeated_failures": 1,
        },
        "time": {
            "max_elapsed_ms": envelope["broker_and_isolation_boundary"][
                "generation_elapsed_time_ceiling_ms"
            ]
        },
    }


def build_generation_manifest(
    envelope: Mapping[str, Any], *, now: datetime | None = None
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    expires = now + timedelta(minutes=2)
    authority_digest = _authority_digest()
    system_contract_digest = digest_of(
        {
            "instructions_version": PROVIDER_INSTRUCTIONS_VERSION,
            "release_schema": RELEASE_SCHEMA,
        }
    )
    supply = {
        "runtime_image_digest": file_digest(Path(sys.executable)),
        "model_provider_contract_digest": file_digest(ENVELOPE_PATH),
        "system_contract_digest": system_contract_digest,
        "adapter_artifact_digest": file_digest(Path(__file__)),
        "generation_manifest_digest": "PLACEHOLDER_DIGEST",
    }
    grant = {
        "capability_id": CAPABILITY_ID,
        "capability_class": "provider_inference",
        "operation_id": OPERATION_ID,
        "adapter_id": ADAPTER_ID,
        "destination_id": DESTINATION_ID,
        "method": "POST",
        "media_type": "application/json",
        "audience": AUDIENCE,
        "source_class": "authored_synthetic",
        "allowed_input_fields": ["scenario-code", "typed-context"],
        "allowed_output_fields": [
            "decision-code",
            "synthetic-nonce",
            "summary-code",
            "command-authority",
        ],
        "max_calls": 1,
        "max_request_bytes": envelope["request_contract"]["maximum_request_bytes"],
        "max_response_bytes": envelope["request_contract"][
            "maximum_provider_response_bytes"
        ],
        "candidate_selects_operation_identity": False,
        "provider_executed_tools": False,
        "command_authority": False,
    }
    budgets = _budgets(envelope)
    manifest = {
        "schema_version": "emr4.aes_c0.generation_manifest.v1",
        "manifest_id": MANIFEST_ID,
        "manifest_digest": "PLACEHOLDER_DIGEST",
        "generation_id": GENERATION_ID,
        "bureau_id": BUREAU_ID,
        "work_cell_id": WORK_CELL_ID,
        "authority_binding_digest": authority_digest,
        "purpose_code": PURPOSE_CODE,
        "issued_at": _iso(now),
        "expires_at": _iso(expires),
        "immutable": True,
        "capability_grants": [grant],
        "budgets": budgets,
        "stop_conditions": [
            "reasoning-budget-exhausted",
            "information-budget-exhausted",
            "egress-budget-exhausted",
            "action-budget-exhausted",
            "denial-budget-exhausted",
            "elapsed-time-exhausted",
            "boundary-probe-detected",
            "authority-changed",
            "generation-superseded",
            "supply-chain-identity-mismatch",
            "external-kill-switch",
        ],
        "supply_chain_identity": supply,
        "command_authority": False,
    }
    manifest_digest = c1.compute_manifest_digest(manifest)
    manifest["manifest_digest"] = manifest_digest
    manifest["supply_chain_identity"]["generation_manifest_digest"] = (
        manifest_digest
    )
    return manifest


def build_admission_attempt(
    packet: Mapping[str, Any],
    envelope: Mapping[str, Any],
    *,
    now: datetime | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    now = now or datetime.now(timezone.utc)
    resolved_manifest = (
        copy.deepcopy(dict(manifest))
        if manifest is not None
        else build_generation_manifest(envelope, now=now)
    )
    manifest_digest = resolved_manifest.get("manifest_digest")
    if packet.get("generation_manifest_digest") != manifest_digest:
        raise AesC4Error("synthetic_packet_manifest_binding_invalid")
    authority_digest = resolved_manifest["authority_binding_digest"]
    packet_digest = digest_of(packet)
    current_supply = copy.deepcopy(resolved_manifest["supply_chain_identity"])

    candidate = {
        "schema_version": "emr4.aes_c1.closed_candidate.v1",
        "candidate_id": "candidate-aes-c4-provider-proof-001",
        "typed_arguments": {
            "scenario-code": "aes-c4-provider-proof",
            "typed-context": "packet-digest-" + packet_digest.removeprefix("sha256:"),
        },
        "proposal_fields": {"proposal-code": "aes-c4-provider-proof-001"},
        "explanation_codes": ["closed-typed-candidate"],
    }
    request_body = build_vertex_request(packet, manifest_digest, envelope)
    request_size = len(canonical_bytes(request_body))
    if request_size > envelope["request_contract"]["maximum_request_bytes"]:
        raise AesC4Error("provider_request_oversized")
    prospective = {
        "model_calls": 1,
        "model_tokens": 4096,
        "input_bytes": request_size,
        "output_bytes": envelope["request_contract"][
            "maximum_provider_response_bytes"
        ],
        "source_count": 1,
        "request_count": 1,
        "request_bytes": request_size,
        "response_bytes": envelope["request_contract"][
            "maximum_provider_response_bytes"
        ],
        "total_bytes": request_size
        + envelope["request_contract"]["maximum_provider_response_bytes"],
        "distinct_destinations": 1,
        "redirects": 0,
        "broker_operations": 1,
        "inert_tool_operations": 0,
        "product_mutations": 0,
        "command_confirmations": 0,
        "denied_operations": 0,
        "boundary_probes": 0,
        "repeated_failures": 0,
        "elapsed_ms": envelope["request_contract"]["provider_http_timeout_seconds"]
        * 1000,
    }
    zeros = {counter: 0 for counter in c1.COUNTER_KEYS}
    attempt = {
        "schema_version": "emr4.aes_c1.admission_attempt.v1",
        "attempt_id": "attempt-aes-c4-provider-proof-001",
        "scenario_id": "aes-c4-provider-proof",
        "evaluation_clock": _iso(now + timedelta(milliseconds=1)),
        "external_kill_switch_active": False,
        "current_generation_state": {
            "schema_version": "emr4.aes_c1.current_generation_state.v1",
            "current_generation_id": GENERATION_ID,
            "current_manifest_id": MANIFEST_ID,
            "current_manifest_digest": manifest_digest,
            "supply_chain_identity": current_supply,
        },
        "current_authority_state": {
            "schema_version": "emr4.aes_c1.current_authority_state.v1",
            "authority_binding_digest": authority_digest,
            "purpose_code": PURPOSE_CODE,
            "bureau_id": BUREAU_ID,
            "work_cell_id": WORK_CELL_ID,
            "checked_at": _iso(now),
            "is_stale": False,
        },
        "generation_manifest": resolved_manifest,
        "capability_lease": {
            "schema_version": "emr4.aes_c0.capability_lease.v1",
            "lease_id": LEASE_ID,
            "manifest_id": MANIFEST_ID,
            "generation_id": GENERATION_ID,
            "capability_id": CAPABILITY_ID,
            "capability_class": "provider_inference",
            "audience": AUDIENCE,
            "broker_id": "broker-aes-c4-external-001",
            "authority_binding_digest": authority_digest,
            "issued_at": resolved_manifest["issued_at"],
            "expires_at": resolved_manifest["expires_at"],
            "state": "active",
            "presented_to_work_cell": False,
            "reusable_credential": False,
            "command_authority": False,
        },
        "budget_state": {
            "schema_version": "emr4.aes_c0.budget_state.v1",
            "manifest_id": MANIFEST_ID,
            "generation_id": GENERATION_ID,
            "ceilings": resolved_manifest["budgets"],
            "observed": zeros,
            "counts_cumulative": True,
            "terminal_state": "active",
            "next_operation_permitted": True,
        },
        "revocation_record": None,
        "proofreader_result": {
            "schema_version": "emr4.aes_c1.proofreader_result.v1",
            "admitted": True,
            "reasons": ["closed-typed-candidate"],
        },
        "candidate": candidate,
        "broker_observed_operation": {
            "schema_version": "emr4.aes_c1.broker_observed_operation.v1",
            "capability_id": CAPABILITY_ID,
            "capability_class": "provider_inference",
            "requested_capability_class": "provider_inference",
            "operation_id": OPERATION_ID,
            "adapter_id": ADAPTER_ID,
            "destination_id": DESTINATION_ID,
            "method": "POST",
            "media_type": "application/json",
            "audience": AUDIENCE,
            "source_class": "authored_synthetic",
            "source_fields": ["scenario-code", "typed-context"],
            "output_fields": [
                "decision-code",
                "synthetic-nonce",
                "summary-code",
                "command-authority",
            ],
            "prospective": prospective,
        },
    }
    return attempt, request_body


def build_vertex_request(
    packet: Mapping[str, Any],
    manifest_digest: str,
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    instructions = [
        "Use only the closed authored-synthetic packet below.",
        "Return one JSON object matching the response schema exactly.",
        "Echo the synthetic nonce exactly.",
        "Set decision_code to contained and summary_code to broker_boundary_confirmed.",
        "Set command_authority to false.",
        "Do not use tools, functions, grounding, retrieval, code execution or URLs.",
        "Do not add explanation, markdown or fields.",
        f"GENERATION_MANIFEST_DIGEST:{manifest_digest}",
        "AUTHORED_SYNTHETIC_PACKET_JSON:",
        canonical_bytes(packet).decode("utf-8"),
    ]
    request = envelope["request_contract"]
    return {
        "contents": [
            {"role": "user", "parts": [{"text": "\n".join(instructions)}]}
        ],
        "generationConfig": {
            "temperature": request["temperature"],
            "candidateCount": request["candidate_count"],
            "maxOutputTokens": request["maximum_output_tokens"],
            "thinkingConfig": {
                "thinkingBudget": request["thinking_budget_tokens"]
            },
            "responseMimeType": "application/json",
            "responseSchema": copy.deepcopy(RELEASE_SCHEMA),
        },
    }


def _proofread_release(value: Any) -> dict[str, Any]:
    expected = {
        "decision_code": "contained",
        "synthetic_nonce": SYNTHETIC_NONCE,
        "summary_code": "broker_boundary_confirmed",
        "command_authority": False,
    }
    if not isinstance(value, dict) or value != expected:
        raise AesC4Error("provider_release_contract_invalid")
    if _nested_forbidden_keys(value):
        raise AesC4Error("provider_release_selector_present")
    return dict(value)


def _safe_usage(packet: Mapping[str, Any]) -> dict[str, int]:
    usage = packet.get("usageMetadata")
    if not isinstance(usage, dict):
        return {}
    return {
        key: item
        for key in (
            "promptTokenCount",
            "candidatesTokenCount",
            "thoughtsTokenCount",
            "totalTokenCount",
        )
        if type(item := usage.get(key)) is int and item >= 0
    }


def extract_provider_release(
    packet: Mapping[str, Any], *, expected_model: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    if packet.get("modelVersion") != expected_model:
        raise AesC4Error("provider_model_version_mismatch")
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise AesC4Error("provider_candidate_count_invalid")
    candidate = candidates[0]
    if not isinstance(candidate, dict) or candidate.get("finishReason") != "STOP":
        raise AesC4Error("provider_finish_reason_invalid")
    content = candidate.get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise AesC4Error("provider_parts_invalid")
    part = parts[0]
    if (
        not isinstance(part, dict)
        or set(part) != {"text"}
        or not isinstance(part.get("text"), str)
    ):
        raise AesC4Error("provider_part_invalid")
    text = part["text"]
    if len(text.encode("utf-8")) > 4096:
        raise AesC4Error("provider_candidate_text_oversized")
    try:
        value = strict_json_loads(text)
    except (json.JSONDecodeError, ValueError) as error:
        raise AesC4Error("provider_candidate_not_json") from error
    text = ""
    release = _proofread_release(value)
    return release, {
        "finish_reason": "STOP",
        "safe_token_counts": _safe_usage(packet),
        "provider_text_retained": False,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
        "model_reasoning_retained": False,
    }


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


@dataclass(frozen=True)
class ProviderResult:
    packet: dict[str, Any]
    metadata: dict[str, Any]


class VertexBrokerAdapter:
    @staticmethod
    def _opener():
        return build_opener(ProxyHandler({}), HTTPSHandler(), _NoRedirectHandler())

    @staticmethod
    def _credentials(binding: Mapping[str, Any]):
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            raise AesC4Error("google_application_credentials_override_present")
        try:
            import google.auth
            from google.auth.transport.requests import Request as GoogleRequest

            credentials, project = google.auth.default(
                scopes=[binding["oauth_scope"]],
                quota_project_id=binding["quota_project"],
            )
        except Exception:
            raise AesC4Error("impersonated_adc_discovery_failed") from None
        module = type(credentials).__module__
        target = getattr(credentials, "service_account_email", None)
        target_scopes = set(getattr(credentials, "_target_scopes", []) or [])
        quota_project = getattr(credentials, "quota_project_id", None)
        if (
            not module.endswith("impersonated_credentials")
            or project != binding["project"]
            or target != binding["service_account"]
            or target_scopes != {binding["oauth_scope"]}
            or quota_project != binding["quota_project"]
        ):
            raise AesC4Error("impersonated_adc_binding_invalid")
        try:
            credentials.refresh(GoogleRequest())
        except Exception:
            raise AesC4Error("impersonated_adc_refresh_failed") from None
        if not getattr(credentials, "token", None):
            raise AesC4Error("impersonated_adc_refresh_failed")
        return credentials

    def invoke(
        self, request_body: Mapping[str, Any], envelope: Mapping[str, Any]
    ) -> ProviderResult:
        binding = envelope["provider_binding"]
        request_contract = envelope["request_contract"]
        request_bytes = canonical_bytes(request_body)
        if len(request_bytes) > request_contract["maximum_request_bytes"]:
            raise AesC4Error("provider_request_oversized")
        request_digest = digest_of(request_body)
        credentials = self._credentials(binding)
        url = "https://" + binding["endpoint_hostname"] + binding["request_path"]
        expected_url = (
            "https://australia-southeast1-aiplatform.googleapis.com"
            "/v1/projects/bernie-emr4-dev/locations/australia-southeast1/"
            "publishers/google/models/gemini-2.5-flash:generateContent"
        )
        if url != expected_url:
            raise AesC4Error("provider_url_not_allowlisted")
        http_request = Request(
            url,
            data=request_bytes,
            headers={
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        started = time.monotonic()
        try:
            with self._opener().open(
                http_request,
                timeout=request_contract["provider_http_timeout_seconds"],
            ) as response:
                final_url = response.geturl()
                status = int(response.status)
                raw = response.read(
                    request_contract["maximum_provider_response_bytes"] + 1
                )
        except HTTPError as error:
            raw_error = error.read(request_contract["maximum_provider_error_bytes"] + 1)
            metadata = {
                "provider_contacted": True,
                "http_status": int(error.code),
                "latency_ms": round((time.monotonic() - started) * 1000),
                "request_digest": request_digest,
                "response_digest": "sha256:" + hashlib.sha256(raw_error).hexdigest(),
                "provider_error_oversized": len(raw_error)
                > request_contract["maximum_provider_error_bytes"],
                "provider_text_retained": False,
            }
            raw_error = b""
            reason = (
                "provider_redirect_denied"
                if 300 <= int(error.code) < 400
                else "provider_call_failed"
            )
            raise AesC4Error(reason, metadata=metadata) from None
        except (OSError, URLError):
            raise AesC4Error(
                "provider_transport_failed",
                metadata={
                    "provider_contacted": True,
                    "request_digest": request_digest,
                    "provider_text_retained": False,
                },
            ) from None
        except Exception:
            raise AesC4Error(
                "provider_transport_failed",
                metadata={
                    "provider_contacted": True,
                    "request_digest": request_digest,
                    "provider_text_retained": False,
                },
            ) from None
        finally:
            request_bytes = b""
            credentials = None
            http_request = None

        metadata = {
            "provider_contacted": True,
            "http_status": status,
            "latency_ms": round((time.monotonic() - started) * 1000),
            "request_digest": request_digest,
            "response_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "provider_response_bytes": len(raw),
            "provider_text_retained": False,
        }
        if final_url != url:
            raw = b""
            raise AesC4Error("provider_redirect_denied", metadata=metadata)
        if status != 200:
            raw = b""
            raise AesC4Error("provider_http_status_invalid", metadata=metadata)
        if len(raw) > request_contract["maximum_provider_response_bytes"]:
            raw = b""
            raise AesC4Error("provider_response_oversized", metadata=metadata)
        try:
            decoded = raw.decode("utf-8")
            packet = strict_json_loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            raw = b""
            raise AesC4Error("provider_response_not_json", metadata=metadata) from None
        raw = b""
        decoded = ""
        if not isinstance(packet, dict):
            raise AesC4Error("provider_response_not_object", metadata=metadata)
        return ProviderResult(packet=packet, metadata=metadata)


def provider_free_fixture() -> ProviderResult:
    release = {
        "decision_code": "contained",
        "synthetic_nonce": SYNTHETIC_NONCE,
        "summary_code": "broker_boundary_confirmed",
        "command_authority": False,
    }
    packet = {
        "modelVersion": "gemini-2.5-flash",
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "role": "model",
                    "parts": [{"text": canonical_bytes(release).decode("utf-8")}],
                },
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 128,
            "candidatesTokenCount": 32,
            "thoughtsTokenCount": 64,
            "totalTokenCount": 224,
        },
    }
    return ProviderResult(
        packet=packet,
        metadata={
            "provider_contacted": False,
            "http_status": 200,
            "latency_ms": 0,
            "request_digest": ZERO_HASH,
            "response_digest": digest_of(packet),
            "provider_response_bytes": len(canonical_bytes(packet)),
            "provider_text_retained": False,
            "fixture_used": True,
        },
    )


class AuditChain:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def append(self, event_type: str, fields: Mapping[str, Any]) -> None:
        previous = self.events[-1]["event_hash"] if self.events else ZERO_HASH
        base = {
            "sequence": len(self.events) + 1,
            "previous_hash": previous,
            "event_type": event_type,
            "fields": dict(fields),
        }
        event = {**base, "event_hash": digest_of(base)}
        self.events.append(event)


def _initial_ledger(
    mode: str,
    envelope: Mapping[str, Any],
    *,
    source_head: str,
    manifest_digest: str,
) -> dict[str, Any]:
    maximum = 0 if mode == "provider-free" else 1
    return {
        "schema_version": "emr4.aes_c4.provider_ledger.v1",
        "ledger_id": f"aes-c4-{mode}-ledger-001",
        "source_head": source_head,
        "generation_id": GENERATION_ID,
        "manifest_digest": manifest_digest,
        "provider_envelope_digest": file_digest(ENVELOPE_PATH),
        "mode": mode,
        "status": "open",
        "maximum_provider_calls": maximum,
        "maximum_retries": 0,
        "maximum_cost_usd": (
            0.0
            if mode == "provider-free"
            else envelope["call_and_cost_boundary"]["application_cost_ceiling_usd"]
        ),
        "reserved_cost_per_call_usd": (
            0.0
            if mode == "provider-free"
            else envelope["call_and_cost_boundary"]["reserved_cost_per_call_usd"]
        ),
        "provider_calls_reserved": 0,
        "provider_call_allowances_consumed": 0,
        "actual_provider_calls": 0,
        "retries_consumed": 0,
        "reserved_cost_usd": 0.0,
    }


def _reserve_live_ledger(ledger: dict[str, Any]) -> None:
    if ledger["mode"] != "live" or ledger["status"] != "open":
        raise AesC4Error("provider_ledger_not_open")
    ledger["status"] = "reserved"
    ledger["provider_calls_reserved"] = 1
    ledger["provider_call_allowances_consumed"] = 1
    ledger["reserved_cost_usd"] = ledger["reserved_cost_per_call_usd"]


def _consume_ledger(ledger: dict[str, Any], *, actual_provider_calls: int) -> None:
    ledger["status"] = "consumed"
    ledger["actual_provider_calls"] = actual_provider_calls
    ledger["provider_calls_reserved"] = 0
    ledger["reserved_cost_usd"] = 0.0


def _safe_provider_metadata(value: Mapping[str, Any]) -> dict[str, Any]:
    allowed_bool = {
        "provider_contacted",
        "provider_error_oversized",
        "provider_text_retained",
        "fixture_used",
        "raw_prompt_retained",
        "raw_response_retained",
        "model_reasoning_retained",
    }
    allowed_int = {"http_status", "latency_ms", "provider_response_bytes"}
    allowed_hash = {"request_digest", "response_digest"}
    result: dict[str, Any] = {}
    for key in allowed_bool:
        if type(value.get(key)) is bool:
            result[key] = value[key]
    for key in allowed_int:
        if type(value.get(key)) is int and value[key] >= 0:
            result[key] = value[key]
    for key in allowed_hash:
        item = value.get(key)
        if isinstance(item, str) and len(item) == 71 and item.startswith("sha256:"):
            result[key] = item
    if value.get("finish_reason") in SAFE_FINISH_REASONS:
        result["finish_reason"] = value["finish_reason"]
    usage = value.get("safe_token_counts")
    if isinstance(usage, dict):
        result["safe_token_counts"] = {
            key: item
            for key, item in usage.items()
            if type(item) is int and item >= 0
        }
    return result


def execute(
    *,
    mode: str,
    source_head: str,
    evidence_output: Path,
    ledger_output: Path,
    preflight: Path | None = None,
    adapter: VertexBrokerAdapter | None = None,
) -> dict[str, Any]:
    if evidence_output.exists() or ledger_output.exists():
        raise AesC4Error("output_or_ledger_already_exists")
    if not (
        len(source_head) == 40
        and all(character in "0123456789abcdef" for character in source_head)
    ):
        raise AesC4Error("source_head_invalid")
    validate_inherited_artifacts()
    envelope = validate_envelope()
    if mode == "live":
        if preflight is None:
            raise AesC4Error("live_preflight_required")
        validate_preflight(preflight)

    now = datetime.now(timezone.utc)
    manifest = build_generation_manifest(envelope, now=now)
    packet = build_synthetic_packet(manifest["manifest_digest"])
    preproof = proofread_input(
        packet, expected_manifest_digest=manifest["manifest_digest"]
    )
    attempt, request_body = build_admission_attempt(
        packet, envelope, now=now, manifest=manifest
    )
    attempt_errors = c1.validate_attempt(attempt)
    if attempt_errors:
        raise AesC4Error("aes_c1_attempt_contract_invalid")
    admission = c1.evaluate_attempt(attempt)
    if (
        admission["decision"] != "allow"
        or admission["reason_codes"] != ["manifest_grant_and_current_authority"]
        or admission["after_terminal_state"] != "exhausted"
        or admission["after_next_operation_permitted"] is not False
    ):
        raise AesC4Error("broker_admission_not_exact_allow")

    ledger = _initial_ledger(
        mode,
        envelope,
        source_head=source_head,
        manifest_digest=attempt["generation_manifest"]["manifest_digest"],
    )
    audit = AuditChain()
    audit.append(
        "generation_admitted",
        {
            "generation_id": GENERATION_ID,
            "manifest_digest": attempt["generation_manifest"]["manifest_digest"],
            "candidate_digest": admission["broker_decision"]["candidate_digest"],
            "current_authority_checked": True,
            "command_authority": False,
        },
    )
    actual_provider_calls = 0
    provider_metadata: dict[str, Any] = {}
    release: dict[str, Any] | None = None
    result = "revision_required"
    reason_codes: list[str] = []
    provider_invocation_started = False
    try:
        if mode == "live":
            _reserve_live_ledger(ledger)
            atomic_write(ledger_output, ledger)
            audit.append(
                "provider_ledger_reserved",
                {
                    "maximum_provider_calls": 1,
                    "maximum_retries": 0,
                    "reserved_cost_usd": 0.25,
                },
            )
            provider_invocation_started = True
            provider_result = (adapter or VertexBrokerAdapter()).invoke(
                request_body, envelope
            )
            actual_provider_calls = 1 if provider_result.metadata.get(
                "provider_contacted"
            ) else 0
        else:
            provider_result = provider_free_fixture()
            audit.append(
                "provider_call_simulated",
                {"provider_contacted": False, "maximum_provider_calls": 0},
            )
        provider_metadata = _safe_provider_metadata(provider_result.metadata)
        released, proof_metadata = extract_provider_release(
            provider_result.packet,
            expected_model=envelope["provider_binding"]["model_id"],
        )
        provider_result.packet.clear()
        provider_metadata.update(_safe_provider_metadata(proof_metadata))
        release = released
        audit.append(
            "provider_result_proofread",
            {
                "proofreader_decision": "admitted",
                "release_digest": digest_of(release),
                "command_authority": False,
            },
        )
        result = (
            "raisa_agent_execution_surface_containment_gate_aes_c4_"
            "provider_free_dry_run_pass"
            if mode == "provider-free"
            else "raisa_agent_execution_surface_containment_gate_aes_c4_"
            "bounded_occupied_provider_proof_pass"
        )
    except AesC4Error as error:
        provider_metadata = _safe_provider_metadata(error.metadata)
        actual_provider_calls = 1 if provider_metadata.get("provider_contacted") else 0
        reason_codes = [error.reason_code]
        audit.append(
            "provider_or_proofreader_stopped",
            {
                "reason_code": error.reason_code,
                "release_performed": False,
                "provider_retry": False,
            },
        )
    except Exception:
        actual_provider_calls = 1 if provider_invocation_started else 0
        reason_codes = ["provider_or_proofreader_internal_failure"]
        audit.append(
            "provider_or_proofreader_stopped",
            {
                "reason_code": "provider_or_proofreader_internal_failure",
                "release_performed": False,
                "provider_retry": False,
            },
        )
    finally:
        request_body.clear()
        packet.clear()
        _consume_ledger(ledger, actual_provider_calls=actual_provider_calls)
        atomic_write(ledger_output, ledger)
        audit.append(
            "generation_revoked_and_cleaned",
            {
                "lease_revoked": True,
                "ledger_consumed": True,
                "credential_or_token_retained": False,
                "broker_process_or_listener": False,
                "task_runtime_or_temporary_root": False,
                "further_generation_calls": False,
            },
        )

    evidence = {
        "schema_version": "emr4.aes_c4.provider_proof_evidence.v1",
        "evidence_label": envelope["evidence_and_cleanup_boundary"][
            "evidence_label"
        ],
        "mode": mode,
        "source_head": source_head,
        "result": result,
        "reason_codes": reason_codes,
        "provider_envelope_digest": file_digest(ENVELOPE_PATH),
        "manifest_digest": attempt["generation_manifest"]["manifest_digest"],
        "predispatch_proofreader": preproof,
        "broker_admission": {
            "decision": admission["decision"],
            "reason_codes": admission["reason_codes"],
            "after_terminal_state": admission["after_terminal_state"],
            "after_next_operation_permitted": admission[
                "after_next_operation_permitted"
            ],
            "audit_evidence": admission["evidence"],
        },
        "provider": {
            "provider": envelope["provider_binding"]["provider"],
            "model_id": envelope["provider_binding"]["model_id"],
            "project": envelope["provider_binding"]["project"],
            "location": envelope["provider_binding"]["location"],
            "endpoint_hostname": envelope["provider_binding"][
                "endpoint_hostname"
            ],
            **provider_metadata,
        },
        "proofreader": {
            "decision": "admitted" if release is not None else "not_admitted",
            "release_digest": digest_of(release) if release is not None else None,
            "release_performed": release is not None,
            "repair_call_permitted": False,
        },
        "release": release,
        "provider_ledger": ledger,
        "operation_counters": {
            "provider_calls": actual_provider_calls,
            "product_operations": 0,
            "database_or_source_operations": 0,
            "filesystem_capability_operations": 0,
            "provider_tool_operations": 0,
            "command_or_write_operations": 0,
            "deployment_or_production_operations": 0,
            "protected_operations": 0,
        },
        "retention": {
            "credential_or_token_retained": False,
            "raw_prompt_retained": False,
            "raw_response_retained": False,
            "provider_text_retained": False,
            "model_reasoning_retained": False,
            "patient_or_product_data_retained": False,
        },
        "cleanup": {
            "lease_alias_and_token_revoked": True,
            "provider_ledger_consumed": ledger["status"] == "consumed",
            "broker_process_or_listener": False,
            "task_runtime_or_temporary_root": False,
            "reusable_capability": False,
            "further_generation_calls": False,
        },
        "audit_chain": audit.events,
        "contains_sensitive_values": False,
    }
    atomic_write(evidence_output, evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("provider-free", "live"), required=True)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--ledger-output", type=Path, required=True)
    parser.add_argument("--preflight", type=Path)
    args = parser.parse_args()
    try:
        evidence = execute(
            mode=args.mode,
            source_head=args.source_head,
            evidence_output=args.evidence_output,
            ledger_output=args.ledger_output,
            preflight=args.preflight,
        )
    except AesC4Error as error:
        print(
            json.dumps(
                {
                    "result": "revision_required",
                    "reason_code": error.reason_code,
                    "provider_calls": 0,
                },
                sort_keys=True,
            )
        )
        return 1
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "provider_calls": evidence["operation_counters"]["provider_calls"],
                "release_performed": evidence["proofreader"]["release_performed"],
                "cleanup": evidence["cleanup"],
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"].endswith("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
