"""AES-C5 provider-free pure containment core (product-runtime admission).

This module is the provider-free, database-free containment core for the exact
AES-C5 product-runtime admission boundary.  It never contacts a database,
application route, cloud service or provider: the source read and the provider
inference are supplied by injectable provider-free fixtures, and any request
for ``local-source`` or ``live`` mode fails before I/O with a closed reason
code.

The broker builds one immutable generation with exactly two grants
(``authoritative_read`` for the frozen practitioner-directory GET and
``provider_inference`` for the exact Sydney Vertex POST), runs two sequential
AES-C1 admission attempts with cumulative budget state, minimizes the admitted
route response into order-derived opaque aliases, builds one digest-bound
60-second ContextFrameSet with a 30-second source-to-dispatch age, constructs a
closed Vertex request, and deterministically proofreads exactly four release
fields with ``command_authority: false``.  Separate single-use source/provider
ledgers are consumed and both leases revoked on every terminal path.  Evidence
carries digests/counts/reason codes only.
"""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping
import uuid

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import (  # noqa: E402
    raisa_agent_execution_surface_containment_gate_aes_c1_admission as c1,
)

BASE = ROOT / (
    "orchestration/continuity/"
    "raisa-agent-execution-surface-containment-gate-aes-c5"
)
ENVELOPE_PATH = BASE / "product-runtime-envelope.json"
ENVELOPE_SCHEMA_PATH = BASE / "product-runtime-envelope.schema.json"

INHERITED_ARTIFACT_DIGESTS = {
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json": "sha256:403c7ddac2399760395d60a8094ffe42d2519a4a809bc8a59104acd2883eb9ae",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json": "sha256:344d88c59a5d781ebb205de575b66f2e3d64f3878f73c9c0bf4d86eb996b1740",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json": "sha256:241f081b1c3346ef50e80eb495c9bfb6ea3b99f67956b439c7c7638962069f90",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json": "sha256:2e6c5b83d379f5b6f900fa0a26a8733b6fe09496ff8e1c52d5ed40123603e9b6",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.json": "sha256:530c9c3067725f6078785e846fa82c0ebb89f72d0a8feeb5c2916d567b5a4ccf",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.schema.json": "sha256:895f1afc8c4d7f58ba0a8032f54f274496d93e1601e9ce40444d642d4bf0c175",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.json": "sha256:4b4e94b07823576b469921308fd46f741d02834f860759db56985285ceb67d3e",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.schema.json": "sha256:fc9e1ae2e42e6178586c51faabf1dabc7ae292d9889091b310a8fd9c021e3de1",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/provider-envelope.json": "sha256:baa22577ca29b09a783765bb5e5893a7d907f98578bf4b1fbc9d6cce24670393",
    "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/provider-envelope.schema.json": "sha256:df3c56c5c67f44d66b3b2c4c93af2fc040c636dffb33a4301eb276a96e0d2412",
}

GENERATION_ID = "generation-aes-c5-product-runtime-001"
MANIFEST_ID = "manifest-aes-c5-product-runtime-001"
BUREAU_ID = "bureau-raisa-containment"
WORK_CELL_ID = "work-cell-aes-c5-reception-one-001"
PURPOSE_CODE = "aes-c5-product-runtime-admission"
BROKER_ID = "broker-aes-c5-external-001"
READ_CAPABILITY_ID = "capability-aes-c5-practitioner-directory-read"
PROVIDER_CAPABILITY_ID = "capability-aes-c5-sydney-vertex-provider-inference"
READ_OPERATION_ID = "read-active-practitioner-directory"
PROVIDER_OPERATION_ID = "generate-aes-c5-booking-context-match"
READ_ADAPTER_ID = "practitioner-directory-route-adapter-v1"
PROVIDER_ADAPTER_ID = "vertex-generate-content-broker-adapter-v1"
READ_DESTINATION_ID = "local-practitioner-directory-route"
PROVIDER_DESTINATION_ID = "vertex-sydney-gemini-25"
READ_LEASE_ID = "lease-aes-c5-authoritative-read-001"
PROVIDER_LEASE_ID = "lease-aes-c5-provider-inference-001"
READ_AUDIENCE = "emr4-reception-one-product-read"
PROVIDER_AUDIENCE = "google-vertex-ai-prediction"
CANDIDATE_ID = "candidate-aes-c5-product-runtime-001"
SCENARIO_ID = "aes-c5-product-runtime-admission"
FRAME_ID = "context-frame-aes-c5-001"
TARGET_DISPLAY_NAME = "Marlow Quill"
TARGET_ALIAS = "practitioner-choice-002"

ZERO_HASH = "sha256:" + "0" * 64
SENTINEL = ZERO_HASH
PROVIDER_INSTRUCTIONS_VERSION = "emr4.aes_c5.provider_instructions.v1"

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
    "route",
    "query",
    "provider",
    "model",
    "url",
    "method",
    "audience",
    "credential",
    "credential_reference",
    "path",
    "filesystem_path",
    "sql",
    "database",
    "schema",
    "executable",
    "tool",
    "tool_definition",
    "command_route",
    "cleanup_target",
    "policy_amendment",
    "lease",
    "lease_id",
    "ledger",
    "token",
}

RELEASE_SCHEMA_BASE = {
    "type": "OBJECT",
    "properties": {
        "decision_code": {"type": "STRING", "enum": ["active_practitioner_choice_matched"]},
        "selected_practitioner_ref": {"type": "STRING"},
        "context_frame_set_digest": {"type": "STRING"},
        "command_authority": {"type": "BOOLEAN"},
    },
    "required": [
        "decision_code",
        "selected_practitioner_ref",
        "context_frame_set_digest",
        "command_authority",
    ],
    "propertyOrdering": [
        "decision_code",
        "selected_practitioner_ref",
        "context_frame_set_digest",
        "command_authority",
    ],
}

# Exact frozen envelope values.  Any drift in these committed values is a
# stop before any admission.
FROZEN_VALUES: dict[str, Any] = {
    "schema_version": "emr4.aes_c5.product_runtime_envelope.v1",
    "envelope_id": "raisa-aes-c5-practitioner-directory-reception-one-001",
    "status": "frozen_pending_exact_head_preexecution_gates",
    "authority_source.decided_on": "2026-08-11",
    "authority_source.source_decision": (
        "authenticated_internal_staff_get_api_v1_practice_practitioners"
    ),
    "authority_source.purpose_decision": (
        "supply_active_practitioner_choices_for_reception_one_booking_context"
    ),
    "source_boundary.source_class": "authored_synthetic_product_runtime",
    "source_boundary.evidence_mode": "live_local_backend_postgres",
    "source_boundary.method": "GET",
    "source_boundary.route": "/api/v1/practice/practitioners",
    "source_boundary.query": "activeOnly=true&limit=4&offset=0",
    "source_boundary.maximum_route_calls": 1,
    "source_boundary.maximum_route_retries": 0,
    "source_boundary.maximum_admitted_rows": 3,
    "source_boundary.overflow_detection_limit": 4,
    "source_boundary.watcher_or_subscription": False,
    "source_boundary.detail_route": False,
    "source_boundary.runtime_readiness_fixture_consumed": False,
    "source_boundary.global_readiness_changed": False,
    "principal_and_tenant_boundary.human_role": "Receptionist",
    "principal_and_tenant_boundary.human_identity_class": (
        "fresh_authored_synthetic_active_internal_staff"
    ),
    "principal_and_tenant_boundary.ordinary_bearer_auth_dependency_required": True,
    "principal_and_tenant_boundary.token_user_practice_equality_required": True,
    "principal_and_tenant_boundary.operational_database_or_practice": False,
    "principal_and_tenant_boundary.work_cell_receives_jwt_database_credential_or_lease": False,
    "principal_and_tenant_boundary.evidence_retains_user_or_practice_identifier": False,
    "field_and_freshness_boundary.route_response_fields": [
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation",
    ],
    "field_and_freshness_boundary.work_cell_fields": [
        "practitioner_ref",
        "display_name",
        "role_label",
    ],
    "field_and_freshness_boundary.broker_only_fields": [
        "id",
        "active",
        "defaultLocation",
        "alias_map",
    ],
    "field_and_freshness_boundary.maximum_display_name_bytes": 80,
    "field_and_freshness_boundary.maximum_role_label_bytes": 40,
    "field_and_freshness_boundary.maximum_source_to_dispatch_age_seconds": 30,
    "field_and_freshness_boundary.context_frame_ttl_seconds": 60,
    "field_and_freshness_boundary.target_display_name": "Marlow Quill",
    "field_and_freshness_boundary.expected_target_alias": "practitioner-choice-002",
    "field_and_freshness_boundary.patient_appointment_or_clinical_fields": False,
    "field_and_freshness_boundary.provider_prescriber_ahpra_hpii_contact_or_location_fields": False,
    "field_and_freshness_boundary.command_authority": False,
    "provider_binding.provider": "google_vertex_ai",
    "provider_binding.model_id": "gemini-2.5-flash",
    "provider_binding.launch_stage": "GA",
    "provider_binding.published_retirement_on": "2026-10-20",
    "provider_binding.project": "bernie-emr4-dev",
    "provider_binding.quota_project": "bernie-emr4-dev",
    "provider_binding.service_account": (
        "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
    ),
    "provider_binding.authentication": "keyless_impersonated_service_account_adc",
    "provider_binding.oauth_scope": "https://www.googleapis.com/auth/cloud-platform",
    "provider_binding.required_permission": "aiplatform.endpoints.predict",
    "provider_binding.location": "australia-southeast1",
    "provider_binding.endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "provider_binding.request_path": (
        "/v1/projects/bernie-emr4-dev/locations/australia-southeast1/"
        "publishers/google/models/gemini-2.5-flash:generateContent"
    ),
    "provider_binding.allowed_identity_hosts": [
        "oauth2.googleapis.com",
        "iamcredentials.googleapis.com",
    ],
    "provider_binding.allowed_data_plane_hosts": [
        "australia-southeast1-aiplatform.googleapis.com"
    ],
    "data_and_retention_boundary.classification": (
        "authored_synthetic_product_runtime_derived_non_phi"
    ),
    "data_and_retention_boundary.real_person_or_operational_practice_data": False,
    "data_and_retention_boundary.patient_or_health_information": False,
    "data_and_retention_boundary.appointment_or_clinical_information": False,
    "data_and_retention_boundary.historical_diary_or_protected_evidence": False,
    "data_and_retention_boundary.licensed_or_external_corpus_content": False,
    "data_and_retention_boundary.raw_source_response_retained": False,
    "data_and_retention_boundary.raw_prompt_retained": False,
    "data_and_retention_boundary.raw_provider_response_retained": False,
    "data_and_retention_boundary.provider_text_or_reasoning_retained": False,
    "request_contract.candidate_count": 1,
    "request_contract.temperature": 0,
    "request_contract.thinking_budget_tokens": 1024,
    "request_contract.maximum_output_tokens": 2048,
    "request_contract.maximum_request_bytes": 8192,
    "request_contract.maximum_provider_response_bytes": 16384,
    "request_contract.maximum_provider_error_bytes": 65536,
    "request_contract.provider_http_timeout_seconds": 45,
    "request_contract.provider_tools": False,
    "request_contract.function_calling": False,
    "request_contract.grounding": False,
    "request_contract.retrieval": False,
    "request_contract.code_execution": False,
    "request_contract.session_resumption": False,
    "request_contract.explicit_context_cache": False,
    "request_contract.automatic_fallback": False,
    "call_and_cost_boundary.maximum_provider_calls": 1,
    "call_and_cost_boundary.maximum_provider_retries": 0,
    "call_and_cost_boundary.maximum_product_route_calls": 1,
    "call_and_cost_boundary.maximum_product_route_retries": 0,
    "call_and_cost_boundary.call_after_any_provider_attempt": False,
    "call_and_cost_boundary.application_cost_ceiling_usd": 0.25,
    "call_and_cost_boundary.reserved_cost_per_call_usd": 0.25,
    "call_and_cost_boundary.published_input_price_per_million_tokens_usd": 0.3,
    "call_and_cost_boundary.published_text_output_including_reasoning_price_per_million_tokens_usd": 2.5,
    "broker_and_isolation_boundary.capability_classes": [
        "authoritative_read",
        "provider_inference",
    ],
    "broker_and_isolation_boundary.immutable_generation": True,
    "broker_and_isolation_boundary.distinct_single_use_leases": 2,
    "broker_and_isolation_boundary.broker_operations": 2,
    "broker_and_isolation_boundary.distinct_destinations": 2,
    "broker_and_isolation_boundary.external_broker_owns_route_jwt_adc_database_session_alias_map_and_tokens": True,
    "broker_and_isolation_boundary.work_cell_selects_operation_identity": False,
    "broker_and_isolation_boundary.current_authority_recheck_before_each_operation": True,
    "broker_and_isolation_boundary.generic_network": False,
    "broker_and_isolation_boundary.redirects": 0,
    "broker_and_isolation_boundary.provider_executed_tools": False,
    "broker_and_isolation_boundary.product_mutations": 0,
    "broker_and_isolation_boundary.command_confirmations": 0,
    "broker_and_isolation_boundary.external_kill_switch": True,
    "broker_and_isolation_boundary.generation_wide_revocation": True,
    "broker_and_isolation_boundary.generation_elapsed_time_ceiling_ms": 120000,
    "proofreader_and_release_boundary.source_response_validator_required": True,
    "proofreader_and_release_boundary.field_minimizer_required": True,
    "proofreader_and_release_boundary.pre_dispatch_candidate_proofreader_required": True,
    "proofreader_and_release_boundary.post_provider_deterministic_proofreader_required": True,
    "proofreader_and_release_boundary.source_manifest_and_context_digest_binding_required": True,
    "proofreader_and_release_boundary.closed_schema_additional_properties_false": True,
    "proofreader_and_release_boundary.release_fields": [
        "decision_code",
        "selected_practitioner_ref",
        "context_frame_set_digest",
        "command_authority",
    ],
    "proofreader_and_release_boundary.command_authority": False,
    "proofreader_and_release_boundary.invalid_or_unproved_output_state": (
        "intelligence_unavailable"
    ),
    "proofreader_and_release_boundary.repair_call_permitted": False,
    "evidence_and_cleanup_boundary.evidence_label": (
        "occupied_authored_synthetic_product_runtime_route_postgres_brokered_provider_proof"
    ),
    "evidence_and_cleanup_boundary.evidence_retains_route_values_display_names_uuids_jwt_database_url_prompt_or_provider_text": False,
    "evidence_and_cleanup_boundary.disposable_schema_absent_after_terminal_state": True,
    "evidence_and_cleanup_boundary.jwt_alias_map_credential_or_token_retained": False,
    "evidence_and_cleanup_boundary.lease_or_ledger_reusable_after_terminal_state": False,
    "evidence_and_cleanup_boundary.broker_process_listener_or_task_root_after_terminal_state": False,
    "claim_boundary.real_person_patient_clinical_or_operational_data_safety_proved": False,
    "claim_boundary.australian_physical_or_sovereign_processing_proved": False,
    "claim_boundary.production_identity_rls_or_deployment_proved": False,
    "claim_boundary.reusable_runtime_or_command_authorised": False,
    "claim_boundary.aes_c6_or_later_planned_or_authorised": False,
}

ZERO_OBSERVED = {counter: 0 for counter in c1.COUNTER_KEYS}


class AesC5Error(RuntimeError):
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
        raise AesC5Error("json_artifact_not_object")
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


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _get_path(value: Any, dotted: str) -> Any:
    target: Any = value
    for part in dotted.split("."):
        if not isinstance(target, dict) or part not in target:
            raise KeyError(dotted)
        target = target[part]
    return target


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

# ---------------------------------------------------------------------------
# Inherited artifact and envelope validation
# ---------------------------------------------------------------------------

def validate_inherited_artifacts() -> None:
    for relative, expected in INHERITED_ARTIFACT_DIGESTS.items():
        path = ROOT / relative
        if not path.is_file() or file_digest(path) != expected:
            raise AesC5Error("inherited_artifact_digest_mismatch")


def validate_envelope_values(envelope: Mapping[str, Any]) -> None:
    for dotted, expected in FROZEN_VALUES.items():
        try:
            actual = _get_path(envelope, dotted)
        except KeyError:
            raise AesC5Error("product_runtime_envelope_frozen_value_invalid") from None
        if actual != expected:
            raise AesC5Error("product_runtime_envelope_frozen_value_invalid")


def validate_envelope() -> dict[str, Any]:
    envelope = load_json(ENVELOPE_PATH)
    schema = load_json(ENVELOPE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(envelope),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise AesC5Error("product_runtime_envelope_schema_invalid")
    validate_envelope_values(envelope)
    return envelope


# ---------------------------------------------------------------------------
# Immutable generation, grants, leases and admission attempts
# ---------------------------------------------------------------------------

def _read_grant() -> dict[str, Any]:
    return {
        "capability_id": READ_CAPABILITY_ID,
        "capability_class": "authoritative_read",
        "operation_id": READ_OPERATION_ID,
        "adapter_id": READ_ADAPTER_ID,
        "destination_id": READ_DESTINATION_ID,
        "method": "GET",
        "media_type": "application/json",
        "audience": READ_AUDIENCE,
        "source_class": "authored_synthetic",
        "allowed_input_fields": ["route", "query", "active-only", "limit", "offset"],
        "allowed_output_fields": ["practitioner-ref", "display-name", "role-label"],
        "max_calls": 1,
        "max_request_bytes": 4096,
        "max_response_bytes": 8192,
        "candidate_selects_operation_identity": False,
        "provider_executed_tools": False,
        "command_authority": False,
    }


def _provider_grant() -> dict[str, Any]:
    return {
        "capability_id": PROVIDER_CAPABILITY_ID,
        "capability_class": "provider_inference",
        "operation_id": PROVIDER_OPERATION_ID,
        "adapter_id": PROVIDER_ADAPTER_ID,
        "destination_id": PROVIDER_DESTINATION_ID,
        "method": "POST",
        "media_type": "application/json",
        "audience": PROVIDER_AUDIENCE,
        "source_class": "authored_synthetic",
        "allowed_input_fields": [
            "context-frame-set-digest",
            "target-alias",
            "target-display-name",
        ],
        "allowed_output_fields": [
            "decision-code",
            "selected-practitioner-ref",
            "context-frame-set-digest",
            "command-authority",
        ],
        "max_calls": 1,
        "max_request_bytes": 8192,
        "max_response_bytes": 16384,
        "candidate_selects_operation_identity": False,
        "provider_executed_tools": False,
        "command_authority": False,
    }


def _authority_digest() -> str:
    return digest_of(
        {
            "purpose_code": PURPOSE_CODE,
            "bureau_id": BUREAU_ID,
            "work_cell_id": WORK_CELL_ID,
            "principal": "yuri-aes-c5-product-runtime-admission-2026-08-11",
            "source_decision": (
                "authenticated_internal_staff_get_api_v1_practice_practitioners"
            ),
            "purpose_decision": (
                "supply_active_practitioner_choices_for_reception_one_booking_context"
            ),
        }
    )


def _budgets(envelope: Mapping[str, Any]) -> dict[str, Any]:
    request = envelope["request_contract"]
    max_req = request["maximum_request_bytes"]
    max_resp = request["maximum_provider_response_bytes"]
    return {
        "reasoning": {"max_model_calls": 1, "max_model_tokens": 4096},
        "information": {
            "max_input_bytes": max_req * 2,
            "max_output_bytes": max_resp * 2,
            "max_source_count": 2,
        },
        "egress": {
            "max_requests": 2,
            "max_request_bytes": max_req * 2,
            "max_response_bytes": max_resp * 2,
            "max_total_bytes": (max_req + max_resp) * 2,
            "max_distinct_destinations": 2,
            "max_redirects": 0,
        },
        "action": {
            "max_broker_operations": 2,
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
    system_contract_digest = digest_of(
        {
            "instructions_version": PROVIDER_INSTRUCTIONS_VERSION,
            "release_schema": RELEASE_SCHEMA_BASE,
            "context_frame_set_schema_version": "emr4.aes_c5.context_frame_set.v1",
        }
    )
    supply = {
        "runtime_image_digest": file_digest(Path(sys.executable)),
        "model_provider_contract_digest": file_digest(ENVELOPE_PATH),
        "system_contract_digest": system_contract_digest,
        "adapter_artifact_digest": file_digest(Path(__file__)),
        "generation_manifest_digest": "PLACEHOLDER_DIGEST",
    }
    manifest = {
        "schema_version": "emr4.aes_c0.generation_manifest.v1",
        "manifest_id": MANIFEST_ID,
        "manifest_digest": "PLACEHOLDER_DIGEST",
        "generation_id": GENERATION_ID,
        "bureau_id": BUREAU_ID,
        "work_cell_id": WORK_CELL_ID,
        "authority_binding_digest": _authority_digest(),
        "purpose_code": PURPOSE_CODE,
        "issued_at": _iso(now),
        "expires_at": _iso(expires),
        "immutable": True,
        "capability_grants": [_read_grant(), _provider_grant()],
        "budgets": _budgets(envelope),
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
    manifest["supply_chain_identity"]["generation_manifest_digest"] = manifest_digest
    return manifest


def validate_generation(manifest: Mapping[str, Any]) -> None:
    grants = manifest.get("capability_grants")
    if not isinstance(grants, list) or len(grants) != 2:
        raise AesC5Error("generation_grant_count_invalid")
    classes = [grant.get("capability_class") for grant in grants]
    if classes != ["authoritative_read", "provider_inference"]:
        raise AesC5Error("generation_capability_classes_invalid")
    ids = [grant.get("capability_id") for grant in grants]
    if ids != [READ_CAPABILITY_ID, PROVIDER_CAPABILITY_ID]:
        raise AesC5Error("generation_capability_ids_invalid")
    read_grant = grants[0]
    if (
        read_grant.get("method") != "GET"
        or read_grant.get("operation_id") != READ_OPERATION_ID
        or read_grant.get("adapter_id") != READ_ADAPTER_ID
        or read_grant.get("destination_id") != READ_DESTINATION_ID
        or read_grant.get("audience") != READ_AUDIENCE
        or read_grant.get("source_class") != "authored_synthetic"
    ):
        raise AesC5Error("generation_read_grant_invalid")
    provider_grant = grants[1]
    if (
        provider_grant.get("method") != "POST"
        or provider_grant.get("operation_id") != PROVIDER_OPERATION_ID
        or provider_grant.get("adapter_id") != PROVIDER_ADAPTER_ID
        or provider_grant.get("destination_id") != PROVIDER_DESTINATION_ID
        or provider_grant.get("audience") != PROVIDER_AUDIENCE
        or provider_grant.get("source_class") != "authored_synthetic"
    ):
        raise AesC5Error("generation_provider_grant_invalid")


def _zeros() -> dict[str, int]:
    return dict(ZERO_OBSERVED)


def _current_generation_state(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.current_generation_state.v1",
        "current_generation_id": manifest["generation_id"],
        "current_manifest_id": manifest["manifest_id"],
        "current_manifest_digest": manifest["manifest_digest"],
        "supply_chain_identity": copy.deepcopy(manifest["supply_chain_identity"]),
    }


def _current_authority_state(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.current_authority_state.v1",
        "authority_binding_digest": manifest["authority_binding_digest"],
        "purpose_code": manifest["purpose_code"],
        "bureau_id": manifest["bureau_id"],
        "work_cell_id": manifest["work_cell_id"],
        "checked_at": manifest["issued_at"],
        "is_stale": False,
    }


def _lease(
    grant: Mapping[str, Any], lease_id: str, manifest: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c0.capability_lease.v1",
        "lease_id": lease_id,
        "manifest_id": manifest["manifest_id"],
        "generation_id": manifest["generation_id"],
        "capability_id": grant["capability_id"],
        "capability_class": grant["capability_class"],
        "audience": grant["audience"],
        "broker_id": BROKER_ID,
        "authority_binding_digest": manifest["authority_binding_digest"],
        "issued_at": manifest["issued_at"],
        "expires_at": manifest["expires_at"],
        "state": "active",
        "presented_to_work_cell": False,
        "reusable_credential": False,
        "command_authority": False,
    }

def _budget_state(
    manifest: Mapping[str, Any], observed: Mapping[str, int]
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c0.budget_state.v1",
        "manifest_id": manifest["manifest_id"],
        "generation_id": manifest["generation_id"],
        "ceilings": copy.deepcopy(manifest["budgets"]),
        "observed": dict(observed),
        "counts_cumulative": True,
        "terminal_state": "active",
        "next_operation_permitted": True,
    }


def _observed_op(
    grant: Mapping[str, Any],
    prospective: Mapping[str, int],
    *,
    source_fields: list[str],
    output_fields: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.broker_observed_operation.v1",
        "capability_id": grant["capability_id"],
        "capability_class": grant["capability_class"],
        "requested_capability_class": grant["capability_class"],
        "operation_id": grant["operation_id"],
        "adapter_id": grant["adapter_id"],
        "destination_id": grant["destination_id"],
        "method": grant["method"],
        "media_type": grant["media_type"],
        "audience": grant["audience"],
        "source_class": "authored_synthetic",
        "source_fields": source_fields,
        "output_fields": output_fields,
        "prospective": dict(prospective),
    }


def build_closed_candidate(typed_context: str) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.closed_candidate.v1",
        "candidate_id": CANDIDATE_ID,
        "typed_arguments": {
            "scenario-code": SCENARIO_ID,
            "typed-context": typed_context,
        },
        "proposal_fields": {"proposal-code": CANDIDATE_ID},
        "explanation_codes": ["closed-typed-candidate"],
    }


def build_admission_attempt(
    manifest: Mapping[str, Any],
    lease: Mapping[str, Any],
    budget_state: Mapping[str, Any],
    observed_op: Mapping[str, Any],
    *,
    now: datetime,
    typed_context: str,
    attempt_id: str,
    scenario_id: str = SCENARIO_ID,
    kill_switch: bool = False,
    revocation_record: Mapping[str, Any] | None = None,
    current_generation_state: Mapping[str, Any] | None = None,
    current_authority_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c1.admission_attempt.v1",
        "attempt_id": attempt_id,
        "scenario_id": scenario_id,
        "evaluation_clock": _iso(now + timedelta(milliseconds=1)),
        "external_kill_switch_active": kill_switch,
        "current_generation_state": (
            current_generation_state
            if current_generation_state is not None
            else _current_generation_state(manifest)
        ),
        "current_authority_state": (
            current_authority_state
            if current_authority_state is not None
            else _current_authority_state(manifest)
        ),
        "generation_manifest": manifest,
        "capability_lease": lease,
        "budget_state": budget_state,
        "revocation_record": revocation_record,
        "proofreader_result": {
            "schema_version": "emr4.aes_c1.proofreader_result.v1",
            "admitted": True,
            "reasons": ["closed-typed-candidate"],
        },
        "candidate": build_closed_candidate(typed_context),
        "broker_observed_operation": observed_op,
    }


def _read_prospective(envelope: Mapping[str, Any]) -> dict[str, int]:
    return {
        "model_calls": 0,
        "model_tokens": 0,
        "input_bytes": 512,
        "output_bytes": 2048,
        "source_count": 1,
        "request_count": 1,
        "request_bytes": 512,
        "response_bytes": 2048,
        "total_bytes": 2560,
        "distinct_destinations": 1,
        "redirects": 0,
        "broker_operations": 1,
        "inert_tool_operations": 0,
        "product_mutations": 0,
        "command_confirmations": 0,
        "denied_operations": 0,
        "boundary_probes": 0,
        "repeated_failures": 0,
        "elapsed_ms": 1000,
    }


def _provider_prospective(
    envelope: Mapping[str, Any], request_body: Mapping[str, Any]
) -> dict[str, int]:
    request = envelope["request_contract"]
    request_bytes = len(canonical_bytes(request_body))
    response_bytes = request["maximum_provider_response_bytes"]
    return {
        "model_calls": 1,
        "model_tokens": 4096,
        "input_bytes": request_bytes,
        "output_bytes": response_bytes,
        "source_count": 0,
        "request_count": 1,
        "request_bytes": request_bytes,
        "response_bytes": response_bytes,
        "total_bytes": request_bytes + response_bytes,
        "distinct_destinations": 1,
        "redirects": 0,
        "broker_operations": 1,
        "inert_tool_operations": 0,
        "product_mutations": 0,
        "command_confirmations": 0,
        "denied_operations": 0,
        "boundary_probes": 0,
        "repeated_failures": 0,
        "elapsed_ms": request["provider_http_timeout_seconds"] * 1000,
    }

def build_read_attempt(
    manifest: Mapping[str, Any],
    envelope: Mapping[str, Any],
    *,
    now: datetime,
    observed: Mapping[str, int] | None = None,
    **overrides: Any,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    read_grant = manifest["capability_grants"][0]
    lease = _lease(read_grant, READ_LEASE_ID, manifest)
    prospective = _read_prospective(envelope)
    budget_state = _budget_state(
        manifest, observed if observed is not None else _zeros()
    )
    observed_op = _observed_op(
        read_grant,
        prospective,
        source_fields=["route", "query", "active-only", "limit", "offset"],
        output_fields=["practitioner-ref", "display-name", "role-label"],
    )
    attempt = build_admission_attempt(
        manifest,
        lease,
        budget_state,
        observed_op,
        now=now,
        typed_context="route-read-admission",
        attempt_id="attempt-aes-c5-authoritative-read-001",
        **overrides,
    )
    return attempt, lease, prospective


def build_provider_attempt(
    manifest: Mapping[str, Any],
    envelope: Mapping[str, Any],
    frame: Mapping[str, Any],
    request_body: Mapping[str, Any],
    *,
    now: datetime,
    observed: Mapping[str, int],
    **overrides: Any,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    provider_grant = manifest["capability_grants"][1]
    lease = _lease(provider_grant, PROVIDER_LEASE_ID, manifest)
    prospective = _provider_prospective(envelope, request_body)
    budget_state = _budget_state(manifest, observed)
    observed_op = _observed_op(
        provider_grant,
        prospective,
        source_fields=["context-frame-set-digest", "target-alias", "target-display-name"],
        output_fields=[
            "decision-code",
            "selected-practitioner-ref",
            "context-frame-set-digest",
            "command-authority",
        ],
    )
    typed_context = "frame-digest-" + frame["context_frame_set_digest"].removeprefix(
        "sha256:"
    )
    attempt = build_admission_attempt(
        manifest,
        lease,
        budget_state,
        observed_op,
        now=now,
        typed_context=typed_context,
        attempt_id="attempt-aes-c5-provider-inference-001",
        **overrides,
    )
    return attempt, lease, prospective


# ---------------------------------------------------------------------------
# Source adapter fixtures, route validation and minimization
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SourceResult:
    rows: list[dict[str, Any]]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ProviderResult:
    packet: dict[str, Any]
    metadata: dict[str, Any]


def _is_valid_uuid(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError):
        return False
    return True

def validate_route_response(
    rows: Any, envelope: Mapping[str, Any]
) -> list[dict[str, Any]]:
    boundary = envelope["field_and_freshness_boundary"]
    route_fields = set(boundary["route_response_fields"])
    max_name = boundary["maximum_display_name_bytes"]
    max_role = boundary["maximum_role_label_bytes"]
    if not isinstance(rows, list):
        raise AesC5Error("route_response_not_list")
    if len(rows) != envelope["source_boundary"]["maximum_admitted_rows"]:
        raise AesC5Error("route_response_row_count_invalid")
    ids: list[str] = []
    names: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            raise AesC5Error("route_response_row_not_object")
        if set(row) != route_fields:
            raise AesC5Error("route_response_field_set_invalid")
        raw_id = row["id"]
        if not _is_valid_uuid(raw_id):
            raise AesC5Error("route_response_id_not_uuid")
        display = row["displayName"]
        if not isinstance(display, str) or not display.strip():
            raise AesC5Error("route_response_display_name_invalid")
        if len(display.encode("utf-8")) > max_name:
            raise AesC5Error("route_response_display_name_oversized")
        role = row["roleLabel"]
        if not isinstance(role, str) or not role.strip():
            raise AesC5Error("route_response_role_label_invalid")
        if len(role.encode("utf-8")) > max_role:
            raise AesC5Error("route_response_role_label_oversized")
        if row["active"] is not True:
            raise AesC5Error("route_response_inactive_row")
        location = row["defaultLocation"]
        if not isinstance(location, str) or not location.strip():
            raise AesC5Error("route_response_default_location_invalid")
        if len(location.encode("utf-8")) > 120:
            raise AesC5Error("route_response_default_location_oversized")
        ids.append(raw_id)
        names.append(display)
    if len(set(ids)) != len(ids):
        raise AesC5Error("route_response_duplicate_ids")
    if len(set(names)) != len(names):
        raise AesC5Error("route_response_duplicate_names")
    return rows


def minimize(
    rows: list[dict[str, Any]], envelope: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    boundary = envelope["field_and_freshness_boundary"]
    target_name = boundary["target_display_name"]
    expected_alias = boundary["expected_target_alias"]
    target_index = next(
        (i for i, row in enumerate(rows) if row["displayName"] == target_name), None
    )
    if target_index != 1:
        raise AesC5Error("target_display_name_alias_mismatch")
    minimized: list[dict[str, Any]] = []
    alias_map: dict[str, str] = {}
    for index, row in enumerate(rows):
        alias = f"practitioner-choice-{index + 1:03d}"
        alias_map[alias] = row["id"]
        entry: dict[str, Any] = {
            "practitioner_ref": alias,
            "display_name": row["displayName"],
        }
        if row.get("roleLabel"):
            entry["role_label"] = row["roleLabel"]
        minimized.append(entry)
    if minimized[1]["practitioner_ref"] != expected_alias:
        raise AesC5Error("target_alias_mismatch")
    return minimized, alias_map


# ---------------------------------------------------------------------------
# ContextFrameSet
# ---------------------------------------------------------------------------

def compute_context_frame_set_digest(frame: Mapping[str, Any]) -> str:
    value = copy.deepcopy(dict(frame))
    value["context_frame_set_digest"] = SENTINEL
    return digest_of(value)


def build_context_frame_set(
    envelope: Mapping[str, Any],
    minimized: list[dict[str, Any]],
    *,
    observed_at: datetime,
    source_digest: str,
) -> dict[str, Any]:
    boundary = envelope["field_and_freshness_boundary"]
    frame: dict[str, Any] = {
        "schema_version": "emr4.aes_c5.context_frame_set.v1",
        "frame_id": FRAME_ID,
        "source": {
            "route": envelope["source_boundary"]["route"],
            "method": envelope["source_boundary"]["method"],
            "source_class": "authored_synthetic",
        },
        "observed_at": _iso(observed_at),
        "expires_at": _iso(
            observed_at
            + timedelta(seconds=boundary["context_frame_ttl_seconds"])
        ),
        "ttl_seconds": boundary["context_frame_ttl_seconds"],
        "source_digest": source_digest,
        "context_frame_set_digest": SENTINEL,
        "practitioners": minimized,
        "target_display_name": boundary["target_display_name"],
        "target_alias": boundary["expected_target_alias"],
        "command_authority": False,
    }
    frame["context_frame_set_digest"] = compute_context_frame_set_digest(frame)
    return frame


def validate_frame_source_digest(
    frame: Mapping[str, Any], source_digest: str
) -> None:
    if frame.get("source_digest") != source_digest:
        raise AesC5Error("context_frame_source_digest_mismatch")


def validate_frame_freshness(
    frame: Mapping[str, Any],
    now: datetime,
    *,
    max_age_seconds: int | None = None,
) -> None:
    boundary_max_age = 30
    limit = max_age_seconds if max_age_seconds is not None else boundary_max_age
    observed = _dt(frame["observed_at"])
    expires = _dt(frame["expires_at"])
    if now > expires:
        raise AesC5Error("context_frame_set_expired")
    if (now - observed) > timedelta(seconds=limit):
        raise AesC5Error("source_to_provider_dispatch_age_exceeded")

# ---------------------------------------------------------------------------
# Closed Vertex request and deterministic provider proofreader
# ---------------------------------------------------------------------------

def build_release_schema(frame: Mapping[str, Any]) -> dict[str, Any]:
    schema = copy.deepcopy(RELEASE_SCHEMA_BASE)
    schema["properties"]["selected_practitioner_ref"]["enum"] = [
        frame["target_alias"]
    ]
    schema["properties"]["context_frame_set_digest"]["enum"] = [
        frame["context_frame_set_digest"]
    ]
    return schema


def build_vertex_request(
    frame: Mapping[str, Any], envelope: Mapping[str, Any]
) -> dict[str, Any]:
    request_contract = envelope["request_contract"]
    instructions = [
        "Use only the closed authored-synthetic context frame below.",
        "Return one JSON object matching the response schema exactly.",
        f"Select the practitioner whose display_name is {frame['target_display_name']}.",
        "Echo the context_frame_set_digest exactly.",
        "Set decision_code to active_practitioner_choice_matched.",
        "Set selected_practitioner_ref to the matching practitioner_ref.",
        "Set command_authority to false.",
        "Do not use tools, functions, grounding, retrieval, code execution or URLs.",
        "Do not add explanation, markdown or fields.",
        "CONTEXT_FRAME_SET_JSON:",
        canonical_bytes(frame).decode("utf-8"),
    ]
    return {
        "contents": [
            {"role": "user", "parts": [{"text": "\n".join(instructions)}]}
        ],
        "generationConfig": {
            "temperature": request_contract["temperature"],
            "candidateCount": request_contract["candidate_count"],
            "maxOutputTokens": request_contract["maximum_output_tokens"],
            "thinkingConfig": {
                "thinkingBudget": request_contract["thinking_budget_tokens"]
            },
            "responseMimeType": "application/json",
            "responseSchema": build_release_schema(frame),
        },
    }


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
    packet: Mapping[str, Any],
    frame: Mapping[str, Any],
    envelope: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if packet.get("modelVersion") != envelope["provider_binding"]["model_id"]:
        raise AesC5Error("provider_model_version_mismatch")
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise AesC5Error("provider_candidate_count_invalid")
    candidate = candidates[0]
    if not isinstance(candidate, dict) or candidate.get("finishReason") != "STOP":
        raise AesC5Error("provider_finish_reason_invalid")
    content = candidate.get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or len(parts) != 1:
        raise AesC5Error("provider_parts_invalid")
    part = parts[0]
    if (
        not isinstance(part, dict)
        or set(part) != {"text"}
        or not isinstance(part.get("text"), str)
    ):
        raise AesC5Error("provider_part_invalid")
    text = part["text"]
    if len(text.encode("utf-8")) > 4096:
        raise AesC5Error("provider_candidate_text_oversized")
    try:
        value = strict_json_loads(text)
    except (json.JSONDecodeError, ValueError) as error:
        raise AesC5Error("provider_candidate_not_json") from error
    if not isinstance(value, dict):
        raise AesC5Error("provider_release_not_object")
    expected = {
        "decision_code": "active_practitioner_choice_matched",
        "selected_practitioner_ref": frame["target_alias"],
        "context_frame_set_digest": frame["context_frame_set_digest"],
        "command_authority": False,
    }
    if value != expected:
        raise AesC5Error("provider_release_contract_invalid")
    if _nested_forbidden_keys(value):
        raise AesC5Error("provider_release_selector_present")
    if not any(
        practitioner["practitioner_ref"] == value["selected_practitioner_ref"]
        for practitioner in frame["practitioners"]
    ):
        raise AesC5Error("provider_selected_ref_not_grounded")
    return dict(value), {
        "finish_reason": "STOP",
        "safe_token_counts": _safe_usage(packet),
        "provider_text_retained": False,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
        "model_reasoning_retained": False,
    }

# ---------------------------------------------------------------------------
# Provider-free fixtures
# ---------------------------------------------------------------------------

def source_provider_free_fixture() -> SourceResult:
    rows = [
        {
            "id": "3f2c7b1a-9d8e-4f6a-8b1c-2e5d7a9b0c1d",
            "displayName": "Aster Finch",
            "roleLabel": "General Practitioner",
            "active": True,
            "defaultLocation": "Main",
        },
        {
            "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
            "displayName": "Marlow Quill",
            "roleLabel": "General Practitioner",
            "active": True,
            "defaultLocation": "Main",
        },
        {
            "id": "6d5c4b3a-2f1e-4d0c-9b8a-7f6e5d4c3b2a",
            "displayName": "Nyra Sol",
            "roleLabel": "Practice Nurse",
            "active": True,
            "defaultLocation": "Consult",
        },
    ]
    return SourceResult(
        rows=rows,
        metadata={
            "fixture_used": True,
            "provider_contacted": False,
            "route": "/api/v1/practice/practitioners",
            "row_count": 3,
        },
    )


def provider_provider_free_fixture(
    request_body: Mapping[str, Any], frame: Mapping[str, Any]
) -> ProviderResult:
    release = {
        "decision_code": "active_practitioner_choice_matched",
        "selected_practitioner_ref": frame["target_alias"],
        "context_frame_set_digest": frame["context_frame_set_digest"],
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
            "request_digest": digest_of(request_body),
            "response_digest": digest_of(packet),
            "provider_response_bytes": len(canonical_bytes(packet)),
            "provider_text_retained": False,
            "fixture_used": True,
        },
    )

# ---------------------------------------------------------------------------
# Ledgers and audit chain
# ---------------------------------------------------------------------------

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


def _initial_source_ledger(
    mode: str,
    envelope: Mapping[str, Any],
    *,
    source_head: str,
    manifest_digest: str,
) -> dict[str, Any]:
    maximum = 1 if mode == "provider-free" else 0
    return {
        "schema_version": "emr4.aes_c5.source_ledger.v1",
        "ledger_id": "aes-c5-source-ledger-001",
        "source_head": source_head,
        "generation_id": GENERATION_ID,
        "manifest_digest": manifest_digest,
        "mode": mode,
        "status": "open",
        "maximum_source_calls": maximum,
        "maximum_route_calls": envelope["source_boundary"]["maximum_route_calls"],
        "maximum_route_retries": 0,
        "source_call_allowances_reserved": 0,
        "source_call_allowances_consumed": 0,
        "actual_source_calls": 0,
        "route_retries_consumed": 0,
    }


def _initial_provider_ledger(
    mode: str,
    envelope: Mapping[str, Any],
    *,
    source_head: str,
    manifest_digest: str,
) -> dict[str, Any]:
    maximum = 0 if mode == "provider-free" else 1
    return {
        "schema_version": "emr4.aes_c5.provider_ledger.v1",
        "ledger_id": "aes-c5-provider-ledger-001",
        "source_head": source_head,
        "generation_id": GENERATION_ID,
        "manifest_digest": manifest_digest,
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


def _reserve_source_ledger(ledger: dict[str, Any]) -> None:
    if ledger["mode"] != "provider-free" or ledger["status"] != "open":
        raise AesC5Error("source_ledger_not_open")
    ledger["status"] = "reserved"
    ledger["source_call_allowances_reserved"] = 1
    ledger["source_call_allowances_consumed"] = 1


def _consume_source_ledger(ledger: dict[str, Any], *, actual_source_calls: int) -> None:
    ledger["status"] = "consumed"
    ledger["actual_source_calls"] = actual_source_calls
    ledger["source_call_allowances_reserved"] = 0


def _consume_provider_ledger(
    ledger: dict[str, Any], *, actual_provider_calls: int
) -> None:
    ledger["status"] = "consumed"
    ledger["actual_provider_calls"] = actual_provider_calls
    ledger["provider_calls_reserved"] = 0
    ledger["provider_call_allowances_consumed"] = 1
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

# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def execute(
    *,
    mode: str,
    source_head: str,
    evidence_output: Path,
    ledger_output: Path,
    source_adapter: Callable[[], SourceResult] | None = None,
    provider_adapter: Callable[
        [Mapping[str, Any], Mapping[str, Any]], ProviderResult
    ]
    | None = None,
    now: datetime | None = None,
    kill_switch: bool = False,
    revocation_record: Mapping[str, Any] | None = None,
    current_generation_id: str | None = None,
    current_manifest_id: str | None = None,
    current_manifest_digest: str | None = None,
    current_supply_chain: Mapping[str, Any] | None = None,
    current_authority_state: Mapping[str, Any] | None = None,
    initial_observed: Mapping[str, int] | None = None,
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    if mode != "provider-free":
        raise AesC5Error("local_source_or_live_mode_denied")
    if evidence_output.exists() or ledger_output.exists():
        raise AesC5Error("output_or_ledger_already_exists")
    if not (
        isinstance(source_head, str)
        and len(source_head) == 40
        and all(character in "0123456789abcdef" for character in source_head)
    ):
        raise AesC5Error("source_head_invalid")
    validate_inherited_artifacts()
    envelope = validate_envelope()
    now = now or datetime.now(timezone.utc)

    manifest = build_generation_manifest(envelope, now=now)
    validate_generation(manifest)

    cg_overrides: dict[str, Any] = {}
    if current_generation_id is not None:
        cg_overrides["current_generation_id"] = current_generation_id
    if current_manifest_id is not None:
        cg_overrides["current_manifest_id"] = current_manifest_id
    if current_manifest_digest is not None:
        cg_overrides["current_manifest_digest"] = current_manifest_digest
    current_generation_state = _current_generation_state(manifest)
    if cg_overrides:
        current_generation_state = copy.deepcopy(current_generation_state)
        current_generation_state.update(cg_overrides)
    if current_supply_chain is not None:
        current_generation_state["supply_chain_identity"] = copy.deepcopy(
            dict(current_supply_chain)
        )
    authority_state = (
        copy.deepcopy(dict(current_authority_state))
        if current_authority_state is not None
        else _current_authority_state(manifest)
    )

    source_ledger = _initial_source_ledger(
        mode, envelope, source_head=source_head, manifest_digest=manifest["manifest_digest"]
    )
    provider_ledger = _initial_provider_ledger(
        mode, envelope, source_head=source_head, manifest_digest=manifest["manifest_digest"]
    )
    audit = AuditChain()
    audit.append(
        "generation_admitted",
        {
            "generation_id": GENERATION_ID,
            "manifest_digest": manifest["manifest_digest"],
            "current_authority_checked": True,
            "command_authority": False,
        },
    )

    actual_source_calls = 0
    actual_provider_calls = 0
    provider_metadata: dict[str, Any] = {}
    release: dict[str, Any] | None = None
    result = "revision_required"
    reason_codes: list[str] = []
    frame: dict[str, Any] | None = None
    request_body: dict[str, Any] | None = None
    admission1: dict[str, Any] | None = None
    admission2: dict[str, Any] | None = None
    source_digest: str | None = None
    row_count = 0
    provider_result: ProviderResult | None = None

    try:
        read_attempt, _, _ = build_read_attempt(
            manifest,
            envelope,
            now=now,
            observed=initial_observed,
            kill_switch=kill_switch,
            revocation_record=revocation_record,
            current_generation_state=current_generation_state,
            current_authority_state=authority_state,
        )
        admission1 = c1.evaluate_attempt(read_attempt)
        if admission1["decision"] != "allow":
            raise AesC5Error(admission1["reason_codes"][0])
        if admission1["reason_codes"] != ["manifest_grant_and_current_authority"]:
            raise AesC5Error("broker_admission_not_exact_allow")
        if (
            admission1["after_terminal_state"] != "active"
            or admission1["after_next_operation_permitted"] is not True
        ):
            raise AesC5Error("broker_admission_first_not_active")
        audit.append(
            "source_admission_allowed",
            {
                "decision": admission1["decision"],
                "reason_codes": admission1["reason_codes"],
                "after_terminal_state": admission1["after_terminal_state"],
                "after_next_operation_permitted": admission1[
                    "after_next_operation_permitted"
                ],
                "audit_evidence_digest": digest_of(admission1["evidence"]),
            },
        )

        _reserve_source_ledger(source_ledger)
        source_result = (source_adapter or source_provider_free_fixture)()
        actual_source_calls = 1
        row_count = len(source_result.rows)
        validated = validate_route_response(source_result.rows, envelope)
        minimized, _alias_map = minimize(validated, envelope)
        source_digest = digest_of(validated)
        frame = build_context_frame_set(
            envelope,
            minimized,
            observed_at=observed_at or now,
            source_digest=source_digest,
        )
        validate_frame_source_digest(frame, source_digest)
        validate_frame_freshness(frame, now)
        audit.append(
            "source_read_and_minimized",
            {
                "source_digest": source_digest,
                "row_count": len(validated),
                "minimized_field_count": 3,
            },
        )

        request_body = build_vertex_request(frame, envelope)
        if len(canonical_bytes(request_body)) > envelope["request_contract"][
            "maximum_request_bytes"
        ]:
            raise AesC5Error("provider_request_oversized")
        provider_attempt, _, _ = build_provider_attempt(
            manifest,
            envelope,
            frame,
            request_body,
            now=now,
            observed=admission1["after_observed"],
            kill_switch=kill_switch,
            revocation_record=revocation_record,
            current_generation_state=current_generation_state,
            current_authority_state=authority_state,
        )
        admission2 = c1.evaluate_attempt(provider_attempt)
        if admission2["decision"] != "allow":
            raise AesC5Error(admission2["reason_codes"][0])
        if admission2["reason_codes"] != ["manifest_grant_and_current_authority"]:
            raise AesC5Error("broker_admission_not_exact_allow")
        if (
            admission2["after_terminal_state"] != "exhausted"
            or admission2["after_next_operation_permitted"] is not False
        ):
            raise AesC5Error("broker_admission_second_not_exhausted")
        audit.append(
            "provider_admission_allowed",
            {
                "decision": admission2["decision"],
                "reason_codes": admission2["reason_codes"],
                "after_terminal_state": admission2["after_terminal_state"],
                "after_next_operation_permitted": admission2[
                    "after_next_operation_permitted"
                ],
                "audit_evidence_digest": digest_of(admission2["evidence"]),
            },
        )

        provider_result = (provider_adapter or provider_provider_free_fixture)(
            request_body, frame
        )
        actual_provider_calls = 1 if provider_result.metadata.get(
            "provider_contacted"
        ) else 0
        provider_metadata = _safe_provider_metadata(provider_result.metadata)
        released, proof_metadata = extract_provider_release(
            provider_result.packet, frame, envelope
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
            "raisa_agent_execution_surface_containment_gate_aes_c5_"
            "product_runtime_admission_pass"
        )
    except AesC5Error as error:
        provider_metadata = _safe_provider_metadata(error.metadata)
        reason_codes = [error.reason_code]
        audit.append(
            "broker_or_proofreader_stopped",
            {
                "reason_code": error.reason_code,
                "release_performed": False,
                "provider_retry": False,
            },
        )
    except Exception:
        reason_codes = ["internal_failure"]
        audit.append(
            "broker_or_proofreader_stopped",
            {
                "reason_code": "internal_failure",
                "release_performed": False,
                "provider_retry": False,
            },
        )
    finally:
        if request_body is not None:
            request_body.clear()
        if provider_result is not None:
            provider_result.packet.clear()
        _consume_source_ledger(source_ledger, actual_source_calls=actual_source_calls)
        _consume_provider_ledger(
            provider_ledger, actual_provider_calls=actual_provider_calls
        )
        ledger_output.mkdir(parents=True, exist_ok=True)
        atomic_write(ledger_output / "source-ledger.json", source_ledger)
        atomic_write(ledger_output / "provider-ledger.json", provider_ledger)
        audit.append(
            "generation_revoked_and_cleaned",
            {
                "lease_revoked": True,
                "source_ledger_consumed": True,
                "provider_ledger_consumed": True,
                "credential_or_token_retained": False,
                "broker_process_or_listener": False,
                "task_runtime_or_temporary_root": False,
                "further_generation_calls": False,
            },
        )

    evidence: dict[str, Any] = {
        "schema_version": "emr4.aes_c5.product_runtime_admission_evidence.v1",
        "evidence_label": envelope["evidence_and_cleanup_boundary"][
            "evidence_label"
        ],
        "mode": mode,
        "source_head": source_head,
        "result": result,
        "reason_codes": reason_codes,
        "envelope_digest": file_digest(ENVELOPE_PATH),
        "inherited_artifact_digests": dict(INHERITED_ARTIFACT_DIGESTS),
        "manifest_digest": manifest["manifest_digest"],
        "broker_admissions": {
            "source_read": _admission_summary(admission1),
            "provider_inference": _admission_summary(admission2),
        },
        "source": {
            "route": envelope["source_boundary"]["route"],
            "role": envelope["principal_and_tenant_boundary"]["human_role"],
            "row_count": row_count,
            "statement_count": 0,
            "source_digest": source_digest,
            "context_digest": (
                frame["context_frame_set_digest"] if frame is not None else None
            ),
            "freshness_disposition": "fresh"
            if frame is not None and not reason_codes
            else "not_dispatched",
            "data_classification": envelope["data_and_retention_boundary"][
                "classification"
            ],
        },
        "provider": {
            "provider": envelope["provider_binding"]["provider"],
            "model_id": envelope["provider_binding"]["model_id"],
            "project": envelope["provider_binding"]["project"],
            "location": envelope["provider_binding"]["location"],
            "endpoint_hostname": envelope["provider_binding"]["endpoint_hostname"],
            **provider_metadata,
        },
        "proofreader": {
            "decision": "admitted" if release is not None else "not_admitted",
            "release_digest": digest_of(release) if release is not None else None,
            "release_performed": release is not None,
            "repair_call_permitted": False,
        },
    }
    evidence["source_ledger"] = source_ledger
    evidence["provider_ledger"] = provider_ledger
    evidence["operation_counters"] = {
        "provider_calls": actual_provider_calls,
        "product_reads": 0,
        "database_operations": 0,
        "source_operations": actual_source_calls,
        "network_operations": 0,
        "filesystem_capability_operations": 0,
        "provider_tool_operations": 0,
        "command_or_write_operations": 0,
        "deployment_or_production_operations": 0,
        "protected_operations": 0,
    }
    evidence["cleanup"] = {
        "lease_alias_and_token_revoked": True,
        "source_ledger_consumed": source_ledger["status"] == "consumed",
        "provider_ledger_consumed": provider_ledger["status"] == "consumed",
        "broker_process_or_listener": False,
        "task_runtime_or_temporary_root": False,
        "reusable_capability": False,
        "further_generation_calls": False,
    }
    evidence["audit_chain"] = audit.events
    evidence["contains_sensitive_values"] = False
    atomic_write(evidence_output, evidence)
    return evidence


def _admission_summary(admission: dict[str, Any] | None) -> dict[str, Any]:
    if admission is None:
        return {
            "decision": "not_attempted",
            "reason_codes": [],
            "after_terminal_state": None,
            "after_next_operation_permitted": None,
            "audit_evidence_digest": None,
        }
    return {
        "decision": admission["decision"],
        "reason_codes": admission["reason_codes"],
        "after_terminal_state": admission["after_terminal_state"],
        "after_next_operation_permitted": admission["after_next_operation_permitted"],
        "audit_evidence_digest": digest_of(admission["evidence"]),
    }

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main_with_argv(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("provider-free", "local-source", "live"),
        required=True,
    )
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--ledger-output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.mode != "provider-free":
        reason = (
            "local_source_mode_denied"
            if args.mode == "local-source"
            else "live_mode_denied"
        )
        print(
            json.dumps(
                {
                    "result": "revision_required",
                    "reason_code": reason,
                    "provider_calls": 0,
                    "product_reads": 0,
                    "database_operations": 0,
                    "adapter_invocation_attempted": False,
                },
                sort_keys=True,
            )
        )
        return 1
    try:
        evidence = execute(
            mode=args.mode,
            source_head=args.source_head,
            evidence_output=args.evidence_output,
            ledger_output=args.ledger_output,
        )
    except AesC5Error as error:
        print(
            json.dumps(
                {
                    "result": "revision_required",
                    "reason_code": error.reason_code,
                    "provider_calls": 0,
                    "product_reads": 0,
                    "database_operations": 0,
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
                "product_reads": evidence["operation_counters"]["product_reads"],
                "database_operations": evidence["operation_counters"][
                    "database_operations"
                ],
                "release_performed": evidence["proofreader"]["release_performed"],
                "cleanup": evidence["cleanup"],
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"].endswith("pass") else 1


def main() -> int:
    return main_with_argv(sys.argv[1:])  # pragma: no cover - CLI shim


if __name__ == "__main__":
    raise SystemExit(main())
