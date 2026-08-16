"""Validate the provider-free unmounted delete-confirm response compatibility.

Read-only provider-free validator for the frozen delete-confirm
response-compatibility and product-adapter architecture. It uses only the
Python standard library plus ``jsonschema`` for schema admission. It never
writes files, opens a database, executes DDL/SQL, spawns subprocesses, touches
the shell, uses the network, holds credentials or controls runtime. All bound
text is handled as strict UTF-8 with CRLF canonicalized to LF and bare CR
rejected before SHA-256 comparison. The committed evidence file is
authored-synthetic and is admitted by ``verify_evidence`` which compares it to
the deterministic ``build_evidence`` output.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-"
    "response-compatibility-product-adapter-architecture"
)
CONTRACT_PATH = BASE / "architecture-contract.json"
CONTRACT_SCHEMA_PATH = BASE / "architecture-contract.schema.json"
EVIDENCE_PATH = BASE / "provider-free-architecture-evidence.json"
EVIDENCE_SCHEMA_PATH = BASE / "provider-free-architecture-evidence.schema.json"
PRECOMMIT_RECEIPT_PATH = (
    ROOT
    / "orchestration/agent_inbox/codex/"
    "raisa-delete-confirm-response-compatibility-product-adapter-architecture-"
    "plan-precommit-receipt.json"
)

EXPECTED_SOURCE_COMMIT = "5aaed2a859c64062d40dd2fe1b419d48dcc5d821"
EXPECTED_CONTRACT_SOURCE_HEAD = "f0c98682568784441991b080681f9beb3b9354c2"
INPUT_HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
MIN_HOSTILE_MUTATIONS = 100
MIN_HOSTILE_EVIDENCE_MUTATIONS = 20

# The frozen semantic-output digests recorded by the pre-commit receipt
# ``raisa-delete-confirm-response-compatibility-product-adapter-architecture-`
# ``plan-precommit-receipt.json`` (source_evidence.active_plan_and_acceptance).
EXPECTED_SEMANTIC_OUTPUT_HASHES = {
    "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-plan.md": (
        "c5d77c82362fd767574cbef33adcdeb1a601010a6ff129eca0ced907ed78670d"
    ),
    "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md": (
        "ad4b440bd8a6a01194a32bc27ec0872993630505f4026626a5ba186598813197"
    ),
    "docs/security/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-threat-model-delta.md": (
        "ffb8876efe954e399526bf5e1f41cfb7c2fb460e992428f4aeba7f3b91d2e0bb"
    ),
    "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture/architecture-contract.json": (
        "7a715d50dc7d997171c21ab0646923e82493b13571a3584bd3ef872f4c8e0c37"
    ),
}

# The frozen architecture contract, embedded verbatim. The validator compares
# the on-disk contract against this literal so any authority or response-surface
# expansion is rejected independently of the JSON Schema.
_FROZEN_CONTRACT_JSON = r"""{
  "schema_version": "raisa.delete_confirm_response_product_adapter_architecture.v1",
  "operation_id": "confirmAppointmentDeleteProposal",
  "route_family": "delete-confirm",
  "mode": "provider_free_unmounted_architecture_only",
  "source_head": "f0c98682568784441991b080681f9beb3b9354c2",
  "input_hash_mode": "strict_utf8_canonical_lf_reject_bare_cr_sha256",
  "input_bindings": [
    {"path": "docs/raisa-provider-free-read-only-delete-confirm-route-convergence-review.md", "sha256": "6b146f64a715738ff4729588bb77f9fb3c7edfcf04edba272888ad2972f50b6f"},
    {"path": "docs/raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution-closeout.md", "sha256": "2e2941e5bbe8574dd044067140d66bc8ded2b49215376763ed53716423ed6713"},
    {"path": "orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-git-object-resolution-sol-acceptance.md", "sha256": "fcd9e11be52b3c4bf261f944e196a4cb32f142be1c302b37e76b060381c8eab2"},
    {"path": "app/services/appointment_delete_physical.py", "sha256": "8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533"},
    {"path": "app/services/appointment_status_product_adapter.py", "sha256": "a067e05802a74461fb14571c26e02bb72f34fcdd4624ee2a5ebcadd0266cdf55"},
    {"path": "app/services/appointment_status_composition.py", "sha256": "42221f72df9290b663b81bd8925afc448d4857733a8029914e09e0b905e9774a"},
    {"path": "app/schemas/appointments.py", "sha256": "c35c271e9308f1f57eeeee53eefa6388087e126944ab5100c225f50066e3a0cf"},
    {"path": "app/models/appointments.py", "sha256": "4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794"},
    {"path": "app/routers/appointments.py", "sha256": "f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624"},
    {"path": "docs/api-spine/openapi/appointment-commands.yaml", "sha256": "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a"},
    {"path": "docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-plan.md", "sha256": "4988e5c694d6b9a4ad07b31d619088a1f7b216d4e6b91f63215a82a5a0dc0704"},
    {"path": "docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-closeout.md", "sha256": "ff975620aa9dc531b04389f89963759a5decc0e80ab853d6688e5501924e3366"},
    {"path": "docs/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-closeout.md", "sha256": "584405db5d49a56e18061f80fcd1faa72c278cf0d4975cf95febc86783609019"},
    {"path": "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md", "sha256": "8d8e3a388aeda71800f014535dccc63af8da6aaa945834add044dc2a49097a91"}
  ],
  "private_receipt": {
    "schema_version": "appointment.delete_confirmation_private_receipt.v1",
    "persistence_authority": "sole",
    "canonical_field_order": [
      "appointment_id",
      "status",
      "status_reason_code",
      "cancellation_reason",
      "waiting_area_id",
      "warning_codes"
    ],
    "status_constant": "Cancelled",
    "waiting_area_constant": null,
    "warning_code_order": "sorted_unique",
    "forbidden_fields": [
      "appointment",
      "patient",
      "practitioner",
      "appointment_date",
      "start_time",
      "notes",
      "reason",
      "audit_identity"
    ]
  },
  "public_projection": {
    "schema_version": "raisa.delete_confirm_public_envelope.v1",
    "receipt_schema_version": "appointment.delete_confirmation_receipt.v1",
    "source": "validated_private_receipt_bytes_only",
    "serialization": "utf8_json_sorted_keys_compact_no_nan",
    "initial_and_replay_use_same_projection": true,
    "current_appointment_read_for_response": false,
    "success_fields": [
      "schema_version",
      "intent",
      "safe",
      "requires_confirmation",
      "autonomy_tier",
      "summary",
      "receipt",
      "warnings",
      "blocks",
      "audit_evidence"
    ],
    "success_constants": {
      "intent": "confirm_delete_appointment",
      "safe": true,
      "requires_confirmation": false,
      "autonomy_tier": "confirmed_write",
      "summary": "Confirmed delete proposal and cancelled one appointment.",
      "blocks": [],
      "audit_evidence": [
        "delete_product_adapter_v1",
        "delete_signed_confirmation_evidence_verified",
        "delete_current_authority_rechecked"
      ]
    },
    "warning_registry": {
      "waiting_area_cleared": {
        "code": "waiting_area_cleared",
        "severity": "warning",
        "message": "Deleting this appointment will remove the patient from the waiting area."
      }
    },
    "forbidden_success_fields": ["appointment", "audit_event", "live_projection"]
  },
  "authority_ingress": {
    "server_owned_fields": [
      "practice_id",
      "actor_id",
      "actor_role",
      "authority_generation",
      "authenticated_session_reference"
    ],
    "client_authority_fields": [],
    "capability_constant": "appointment.cancel.confirm",
    "capability_check_owner": "delete_confirm_locked_transaction",
    "current_authority_check_count": 2,
    "command_session": "distinct_server_owned_close_after_use",
    "effect_authority_before_physical_seam": false
  },
  "proposal_binding": {
    "schema_version": "raisa.delete_proposal_version_binding.v1",
    "server_hmac_fields": ["source_version", "evidence_signature"],
    "client_posture": "opaque_return_unchanged",
    "positive_source_version_required": true
  },
  "admission": {
    "pre_command_checks": [
      "exact_delete_proposal_type",
      "operation_and_route_binding",
      "explicit_confirmation",
      "idempotency_key_present",
      "proposal_safe_and_requires_confirmation",
      "signed_evidence_exact_purpose_and_binding",
      "opaque_positive_source_version_binding",
      "freshness_binding",
      "unique_sorted_warning_acknowledgement"
    ],
    "locked_checks": [
      "practice_actor_target_binding",
      "same_positive_source_version",
      "status_not_cancelled",
      "waiting_area_and_clears_flag",
      "reason_and_cancellation_text_command",
      "freshness_and_signed_evidence",
      "warning_acknowledgement"
    ],
    "effect_authority": false
  },
  "composition": {
    "transaction_factory": "delete_confirm_locked_transaction",
    "new_command_write_set": ["appointment_cancellation", "attributable_delete_audit", "complete_private_receipt"],
    "replay_effect_count": 0,
    "route_local_fallback": false
  },
  "outcome_mapping": [
    {"outcomes": ["committed", "replay"], "http_status": 200, "body": "canonical_public_projection_bytes"},
    {"outcomes": ["proposal_stop", "admission_stop"], "http_status": 200, "body": "typed_blocked_envelope"},
    {"outcomes": ["idempotency_key_missing", "idempotency_conflict"], "http_status": 409, "body": "stable_non_sensitive_error"},
    {"outcomes": ["current_authority_unavailable"], "http_status": 403, "body": "stable_non_sensitive_error"},
    {"outcomes": ["target_unavailable", "cross_practice_target"], "http_status": 404, "body": "indistinguishable_unavailable"},
    {"outcomes": ["in_progress_not_replayable", "legacy_receipt_not_replayable"], "http_status": 409, "body": "no_partial_receipt"},
    {"outcomes": ["wait_budget_exhausted", "scaffold_incomplete", "receipt_integrity_failure", "projection_failure"], "http_status": 503, "body": "no_stored_or_current_appointment_disclosure"}
  ],
  "compatibility": {
    "future_canonical_path": "/appointments/proposals/delete/confirm",
    "future_hidden_alias": "/appointments/proposals/delete-confirm",
    "one_future_handler": true,
    "one_public_envelope_version": true,
    "raw_delete_path": "/appointments/{appointment_id}",
    "raw_delete_isolation": [
      "no_dedicated_adapter_import_or_call",
      "no_dedicated_capability_inheritance",
      "no_dedicated_receipt_or_replay_inheritance"
    ]
  },
  "claim_boundary": {
    "proves": [
      "coherent_provider_free_unmounted_response_and_product_adapter_architecture",
      "privacy_minimized_byte_deterministic_public_projection_design",
      "server_owned_authority_and_locked_readmission_design"
    ],
    "does_not_prove": [
      "adapter_or_schema_implementation",
      "route_or_http_behavior",
      "database_execution",
      "capability_provisioning",
      "client_compatibility",
      "deployment_or_production"
    ]
  },
  "forbidden_surfaces": [
    "product_source_edit",
    "route_edit_mount_or_call",
    "database_docker_sql_or_migration_execution",
    "capability_provisioning_or_product_command",
    "product_patient_clinical_historical_or_protected_data",
    "provider_adc_credentials_iam_browser_or_external_network",
    "ui_deployment_production_release_pages_or_protected_refs",
    "broad_staging_or_docs_branding"
  ]
}
"""

EXPECTED_CONTRACT = json.loads(_FROZEN_CONTRACT_JSON)
EXPECTED_SOURCE_BINDINGS = {
    item["path"]: item["sha256"] for item in EXPECTED_CONTRACT["input_bindings"]
}

HOSTILE_FAMILY_NAMES = {
    "dpa_001_client_authority",
    "dpa_002_stale_generation",
    "dpa_003_unlocked",
    "dpa_004_route_local_fallback",
    "dpa_005_appointment_out_leak",
    "dpa_006_full_data_persistence",
    "dpa_007_replay_drift",
    "dpa_008_version_drift",
    "dpa_009_warning_registry_drift",
    "dpa_010_cross_practice_disclosure",
    "dpa_011_partial_receipt_leak",
    "dpa_012_raw_delete_inheritance",
    "dpa_013_alias_divergence",
    "dpa_014_authority_expansion",
    "input_digest_mismatch",
    "array_reorder_or_expand",
    "unknown_or_missing_key",
}

PRIVATE_RECEIPT_FIELDS = [
    "appointment_id",
    "status",
    "status_reason_code",
    "cancellation_reason",
    "waiting_area_id",
    "warning_codes",
]
PRIVATE_RECEIPT_FIELD_SET = frozenset(PRIVATE_RECEIPT_FIELDS)

RECEIPT_SCHEMA_VERSION = "appointment.delete_confirmation_receipt.v1"
PUBLIC_ENVELOPE_SCHEMA_VERSION = "raisa.delete_confirm_public_envelope.v1"

WARNING_REGISTRY = {
    "waiting_area_cleared": {
        "code": "waiting_area_cleared",
        "severity": "warning",
        "message": "Deleting this appointment will remove the patient from the waiting area.",
    }
}

PUBLIC_SUCCESS_CONSTANTS = {
    "audit_evidence": [
        "delete_product_adapter_v1",
        "delete_signed_confirmation_evidence_verified",
        "delete_current_authority_rechecked",
    ],
    "autonomy_tier": "confirmed_write",
    "blocks": [],
    "intent": "confirm_delete_appointment",
    "requires_confirmation": False,
    "safe": True,
    "schema_version": PUBLIC_ENVELOPE_SCHEMA_VERSION,
    "summary": "Confirmed delete proposal and cancelled one appointment.",
}


def _read_strict_utf8(path: Path) -> str:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"non-UTF-8 bytes in {path}") from exc
    if "\r" in text.replace("\r\n", ""):
        raise ValueError(f"bare CR in {path}")
    return text


def _canonical_lf_sha256(path: Path) -> str:
    text = _read_strict_utf8(path)
    canonical = text.replace("\r\n", "\n")
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(_read_strict_utf8(path))


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant rejected: {value}")


def validate_schema(instance: Any, schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def verify_source_bindings(contract: dict[str, Any]) -> dict[str, str]:
    declared = {item["path"]: item["sha256"] for item in contract["input_bindings"]}
    if declared != EXPECTED_SOURCE_BINDINGS:
        raise ValueError("exact source binding set changed")
    observed: dict[str, str] = {}
    for relative_path, expected_hash in EXPECTED_SOURCE_BINDINGS.items():
        path = ROOT / relative_path
        if not path.is_file():
            raise ValueError(f"source missing: {relative_path}")
        digest = _canonical_lf_sha256(path)
        if digest != expected_hash:
            raise ValueError(f"source hash mismatch: {relative_path}")
        observed[relative_path] = digest
    return observed


def verify_semantic_output_hashes() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative_path, expected_hash in EXPECTED_SEMANTIC_OUTPUT_HASHES.items():
        path = ROOT / relative_path
        if not path.is_file():
            raise ValueError(f"semantic output missing: {relative_path}")
        digest = _canonical_lf_sha256(path)
        if digest != expected_hash:
            raise ValueError(f"semantic output hash mismatch: {relative_path}")
        observed[relative_path] = digest
    return observed


def verify_precommit_receipt_binding() -> dict[str, Any]:
    if not PRECOMMIT_RECEIPT_PATH.is_file():
        raise ValueError("pre-commit receipt missing")
    receipt_text = _read_strict_utf8(PRECOMMIT_RECEIPT_PATH)
    for relative_path, digest in EXPECTED_SEMANTIC_OUTPUT_HASHES.items():
        if digest not in receipt_text:
            raise ValueError(f"pre-commit receipt does not record {relative_path} digest")
    return {
        "path": str(PRECOMMIT_RECEIPT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "semantic_output_digests_recorded": True,
        "bound_digest_count": len(EXPECTED_SEMANTIC_OUTPUT_HASHES),
    }


def validate_contract_semantics(contract: dict[str, Any]) -> None:
    if contract != EXPECTED_CONTRACT:
        raise ValueError("frozen architecture contract drifted")


Mutation = Callable[[dict[str, Any]], None]


def _set(path: tuple[Any, ...], value: Any) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value

    return mutate


def _without(path: tuple[Any, ...], item: str) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = [value for value in cursor[path[-1]] if value != item]

    return mutate


def _append(path: tuple[Any, ...], value: Any) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = [*cursor[path[-1]], value]

    return mutate


def _delete(path: tuple[Any, ...]) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        del cursor[path[-1]]

    return mutate


def hostile_mutations() -> list[tuple[str, Mutation]]:
    mutations: list[tuple[str, Mutation]] = [
        # DPA-001 server-owned ingress; client authority is rejected.
        ("dpa_001_client_authority_role", _set(("authority_ingress", "client_authority_fields"), ["actor_role"])),
        ("dpa_001_client_authority_generation", _set(("authority_ingress", "client_authority_fields"), ["authority_generation"])),
        ("dpa_001_client_authority_capability", _set(("authority_ingress", "client_authority_fields"), ["capability"])),
        ("dpa_001_client_authority_session", _set(("authority_ingress", "client_authority_fields"), ["authenticated_session_reference"])),
        ("dpa_001_server_owned_expanded", _append(("authority_ingress", "server_owned_fields"), "client_role")),
        ("dpa_001_effect_authority_before_seam", _set(("authority_ingress", "effect_authority_before_physical_seam"), True)),
        ("dpa_001_admission_effect_authority", _set(("admission", "effect_authority"), True)),
        ("dpa_001_capability_owner_route_local", _set(("authority_ingress", "capability_check_owner"), "route_local")),
        ("dpa_001_capability_constant_change", _set(("authority_ingress", "capability_constant"), "appointment.delete")),
        ("dpa_001_capability_check_count_one", _set(("authority_ingress", "current_authority_check_count"), 1)),
        ("dpa_001_capability_check_count_zero", _set(("authority_ingress", "current_authority_check_count"), 0)),
        ("dpa_001_request_scoped_session", _set(("authority_ingress", "command_session"), "request_scoped")),
        # DPA-002 opaque proposal-generation binding and locked re-admission.
        ("dpa_002_stale_generation_hmac_remove_version", _set(("proposal_binding", "server_hmac_fields"), ["evidence_signature"])),
        ("dpa_002_stale_generation_hmac_expand", _append(("proposal_binding", "server_hmac_fields"), "client_nonce")),
        ("dpa_002_positive_source_version_not_required", _set(("proposal_binding", "positive_source_version_required"), False)),
        ("dpa_002_precheck_remove_generation_binding", _without(("admission", "pre_command_checks"), "opaque_positive_source_version_binding")),
        ("dpa_002_locked_remove_source_version", _without(("admission", "locked_checks"), "same_positive_source_version")),
        ("dpa_002_precheck_remove_freshness", _without(("admission", "pre_command_checks"), "freshness_binding")),
        ("dpa_002_locked_remove_freshness_evidence", _without(("admission", "locked_checks"), "freshness_and_signed_evidence")),
        ("dpa_002_precheck_remove_signed_evidence", _without(("admission", "pre_command_checks"), "signed_evidence_exact_purpose_and_binding")),
        # DPA-003 no unlocked state becomes effect authority.
        ("dpa_003_unlocked_practice_actor", _without(("admission", "locked_checks"), "practice_actor_target_binding")),
        ("dpa_003_unlocked_status", _without(("admission", "locked_checks"), "status_not_cancelled")),
        ("dpa_003_unlocked_waiting_area", _without(("admission", "locked_checks"), "waiting_area_and_clears_flag")),
        ("dpa_003_unlocked_reason", _without(("admission", "locked_checks"), "reason_and_cancellation_text_command")),
        ("dpa_003_unlocked_warning", _without(("admission", "locked_checks"), "warning_acknowledgement")),
        ("dpa_003_precheck_remove_confirmation", _without(("admission", "pre_command_checks"), "explicit_confirmation")),
        ("dpa_003_precheck_remove_idempotency", _without(("admission", "pre_command_checks"), "idempotency_key_present")),
        ("dpa_003_precheck_remove_proposal_safe", _without(("admission", "pre_command_checks"), "proposal_safe_and_requires_confirmation")),
        ("dpa_003_precheck_remove_warning_ack", _without(("admission", "pre_command_checks"), "unique_sorted_warning_acknowledgement")),
        # DPA-004 only the physical transaction factory; no route-local fallback.
        ("dpa_004_route_local_fallback", _set(("composition", "route_local_fallback"), True)),
        ("dpa_004_route_local_transaction", _set(("composition", "transaction_factory"), "route_local_transaction")),
        ("dpa_004_route_local_write_set", _append(("composition", "new_command_write_set"), "route_local_claim")),
        ("dpa_004_write_set_remove_receipt", _without(("composition", "new_command_write_set"), "complete_private_receipt")),
        ("dpa_004_replay_effect_count_one", _set(("composition", "replay_effect_count"), 1)),
        # DPA-005 the private receipt is never relabelled AppointmentOut.
        ("dpa_005_appointment_out_leak_success", _without(("public_projection", "forbidden_success_fields"), "appointment")),
        ("dpa_005_appointment_out_leak_all", _set(("public_projection", "forbidden_success_fields"), [])),
        ("dpa_005_receipt_schema_appointment_out", _set(("public_projection", "receipt_schema_version"), "appointment.AppointmentOut")),
        ("dpa_005_success_fields_expand_appointment", _append(("public_projection", "success_fields"), "appointment")),
        ("dpa_005_success_fields_remove_receipt", _without(("public_projection", "success_fields"), "receipt")),
        # DPA-006 only the six accepted fields are persisted.
        ("dpa_006_full_data_persistence_patient", _without(("private_receipt", "forbidden_fields"), "patient")),
        ("dpa_006_full_data_persistence_all", _set(("private_receipt", "forbidden_fields"), [])),
        ("dpa_006_field_order_expand_patient", _append(("private_receipt", "canonical_field_order"), "patient")),
        ("dpa_006_field_order_remove", _without(("private_receipt", "canonical_field_order"), "warning_codes")),
        ("dpa_006_persistence_shared", _set(("private_receipt", "persistence_authority"), "shared")),
        # DPA-007 replay is a pure projection of the stored bytes only.
        ("dpa_007_replay_drift_source_current_read", _set(("public_projection", "source"), "current_appointment_read")),
        ("dpa_007_replay_drift_current_read", _set(("public_projection", "current_appointment_read_for_response"), True)),
        ("dpa_007_replay_drift_different_projection", _set(("public_projection", "initial_and_replay_use_same_projection"), False)),
        ("dpa_007_replay_drift_orm_projection", _set(("public_projection", "serialization"), "live_orm_projection")),
        # DPA-008 immutable v1 version constants; no drift.
        ("dpa_008_version_drift_public_envelope", _set(("public_projection", "schema_version"), "raisa.delete_confirm_public_envelope.v2")),
        ("dpa_008_version_drift_private_receipt", _set(("private_receipt", "schema_version"), "appointment.delete_confirmation_private_receipt.v2")),
        ("dpa_008_version_drift_proposal_binding", _set(("proposal_binding", "schema_version"), "raisa.delete_proposal_version_binding.v2")),
        ("dpa_008_version_drift_contract", _set(("schema_version",), "raisa.delete_confirm_response_product_adapter_architecture.v2")),
        ("dpa_008_success_intent_change", _set(("public_projection", "success_constants", "intent"), "confirm_appointment_delete")),
        ("dpa_008_success_safe_false", _set(("public_projection", "success_constants", "safe"), False)),
        ("dpa_008_success_requires_confirmation", _set(("public_projection", "success_constants", "requires_confirmation"), True)),
        ("dpa_008_success_autonomy_change", _set(("public_projection", "success_constants", "autonomy_tier"), "client_authoritative")),
        ("dpa_008_success_summary_change", _set(("public_projection", "success_constants", "summary"), "Cancelled.")),
        ("dpa_008_success_blocks_nonempty", _set(("public_projection", "success_constants", "blocks"), ["block"])),
        ("dpa_008_success_audit_evidence_expand", _append(("public_projection", "success_constants", "audit_evidence"), "delete_client_authority")),
        ("dpa_008_success_audit_evidence_remove", _without(("public_projection", "success_constants", "audit_evidence"), "delete_current_authority_rechecked")),
        # DPA-009 exact one-entry warning registry; sorted unique codes only.
        ("dpa_009_warning_registry_drift_expand", _set(
            ("public_projection", "warning_registry"),
            {**EXPECTED_CONTRACT["public_projection"]["warning_registry"], "new_warning": {"code": "new_warning", "severity": "warning", "message": "x"}},
        )),
        ("dpa_009_warning_registry_drift_empty", _set(("public_projection", "warning_registry"), {})),
        ("dpa_009_warning_registry_drift_message", _set(("public_projection", "warning_registry", "waiting_area_cleared", "message"), "changed")),
        ("dpa_009_warning_registry_drift_severity", _set(("public_projection", "warning_registry", "waiting_area_cleared", "severity"), "error")),
        ("dpa_009_warning_registry_drift_code", _set(("public_projection", "warning_registry", "waiting_area_cleared", "code"), "waiting_area_changed")),
        ("dpa_009_warning_code_order_insertion", _set(("private_receipt", "warning_code_order"), "insertion_order")),
        # DPA-010 cross-practice absence is non-disclosing.
        ("dpa_010_cross_practice_disclosure_body", _set(("outcome_mapping", 4, "body"), "cross_practice_row_exists")),
        ("dpa_010_cross_practice_disclosure_status", _set(("outcome_mapping", 4, "http_status"), 200)),
        ("dpa_010_cross_practice_disclosure_outcomes", _set(("outcome_mapping", 4, "outcomes"), ["target_unavailable"])),
        # DPA-011 partial/legacy receipts never leak or retry.
        ("dpa_011_partial_receipt_leak_body", _set(("outcome_mapping", 5, "body"), "partial_receipt")),
        ("dpa_011_partial_receipt_leak_status", _set(("outcome_mapping", 5, "http_status"), 200)),
        ("dpa_011_partial_receipt_leak_outcomes", _set(("outcome_mapping", 5, "outcomes"), ["legacy_receipt_not_replayable"])),
        ("dpa_011_partial_receipt_503_body", _set(("outcome_mapping", 6, "body"), "receipt_integrity_detail")),
        # DPA-012 raw DELETE isolation.
        ("dpa_012_raw_delete_inheritance_import", _without(("compatibility", "raw_delete_isolation"), "no_dedicated_adapter_import_or_call")),
        ("dpa_012_raw_delete_inheritance_capability", _without(("compatibility", "raw_delete_isolation"), "no_dedicated_capability_inheritance")),
        ("dpa_012_raw_delete_inheritance_receipt", _without(("compatibility", "raw_delete_isolation"), "no_dedicated_receipt_or_replay_inheritance")),
        ("dpa_012_raw_delete_inheritance_all", _set(("compatibility", "raw_delete_isolation"), [])),
        ("dpa_012_raw_delete_path_reuse", _set(("compatibility", "raw_delete_path"), "/appointments/proposals/delete/confirm")),
        # DPA-013 canonical and compatibility aliases converge on one envelope.
        ("dpa_013_alias_divergence_handler", _set(("compatibility", "one_future_handler"), False)),
        ("dpa_013_alias_divergence_envelope", _set(("compatibility", "one_public_envelope_version"), False)),
        ("dpa_013_alias_divergence_path", _set(("compatibility", "future_hidden_alias"), "/appointments/proposals/delete-alias")),
        ("dpa_013_alias_divergence_canonical", _set(("compatibility", "future_canonical_path"), "/appointments/proposals/delete")),
        # DPA-014 architecture-only claim boundary.
        ("dpa_014_authority_expansion_mode", _set(("mode",), "mounted_runtime")),
        ("dpa_014_authority_expansion_claim", _append(("claim_boundary", "proves"), "mounted_route_authority")),
        ("dpa_014_authority_expansion_does_not_prove", _without(("claim_boundary", "does_not_prove"), "adapter_or_schema_implementation")),
        ("dpa_014_forbidden_route_opened", _without(("forbidden_surfaces",), "route_edit_mount_or_call")),
        ("dpa_014_forbidden_database_opened", _without(("forbidden_surfaces",), "database_docker_sql_or_migration_execution")),
        ("dpa_014_forbidden_surfaces_expanded", _append(("forbidden_surfaces",), "client_authority")),
        # Input digest mismatch.
        ("input_digest_mismatch_mode", _set(("input_hash_mode",), "plain_sha256")),
        ("array_reorder_or_expand_input_bindings_reversed", _set(("input_bindings",), list(reversed(EXPECTED_CONTRACT["input_bindings"])))),
        ("array_reorder_or_expand_input_bindings_expanded", _append(("input_bindings",), {"path": "extra/input.md", "sha256": "0" * 64})),
        ("array_reorder_or_expand_input_bindings_removed", _set(("input_bindings",), EXPECTED_CONTRACT["input_bindings"][1:])),
        ("array_reorder_or_expand_outcome_mapping_reversed", _set(("outcome_mapping",), list(reversed(EXPECTED_CONTRACT["outcome_mapping"])))),
        # Unknown / missing key rejection.
        ("unknown_or_missing_key_top", _set(("extra_top_key",), True)),
        ("unknown_or_missing_key_private", _set(("private_receipt", "extra"), True)),
        ("unknown_or_missing_key_authority", _set(("authority_ingress", "extra"), True)),
        ("unknown_or_missing_key_composition_missing", _delete(("composition",))),
        ("unknown_or_missing_key_private_missing", _delete(("private_receipt", "status_constant"))),
        ("unknown_or_missing_key_binding_missing_path", _delete(("input_bindings", 0, "path"))),
        ("unknown_or_missing_key_projection_missing", _delete(("public_projection", "serialization"))),
    ]
    for index in range(14):
        mutations.append(
            (
                f"input_digest_mismatch_binding_{index}",
                _set(("input_bindings", index, "sha256"), "0" * 64),
            )
        )
    for index in range(6):
        mutations.append(
            (
                f"array_reorder_or_expand_private_field_{index}",
                _set(("private_receipt", "canonical_field_order", index), "patient"),
            )
        )
    for index in range(9):
        mutations.append(
            (
                f"array_reorder_or_expand_precheck_{index}",
                _set(("admission", "pre_command_checks", index), "weakened"),
            )
        )
    for index in range(7):
        mutations.append(
            (
                f"array_reorder_or_expand_locked_{index}",
                _set(("admission", "locked_checks", index), "weakened"),
            )
        )
    return mutations


def reject_hostile_mutations(
    contract: dict[str, Any], schema: dict[str, Any]
) -> dict[str, int]:
    mutations = hostile_mutations()
    names = {name for name, _ in mutations}
    missing_families = sorted(
        family for family in HOSTILE_FAMILY_NAMES
        if not any(family in name for name in names)
    )
    if missing_families:
        raise ValueError(f"hostile family not covered: {missing_families}")
    rejected = 0
    for mutation_id, mutation in mutations:
        candidate = copy.deepcopy(contract)
        mutation(candidate)
        try:
            validate_schema(candidate, schema)
            validate_contract_semantics(candidate)
            verify_source_bindings(candidate)
        except (AssertionError, KeyError, TypeError, ValidationError, ValueError):
            rejected += 1
            continue
        raise ValueError(f"hostile mutation admitted: {mutation_id}")
    if rejected < MIN_HOSTILE_MUTATIONS:
        raise ValueError("fewer than 100 hostile mutations were rejected")
    return {
        "attempted": len(mutations),
        "rejected": rejected,
        "minimum_required": MIN_HOSTILE_MUTATIONS,
    }


def hostile_evidence_mutations() -> list[tuple[str, Mutation]]:
    mutations: list[tuple[str, Mutation]] = [
        ("unknown_or_missing_key_evidence_top", _set(("extra_key",), True)),
        ("unknown_or_missing_key_evidence_facts", _set(("architecture_facts", "extra"), True)),
        ("unknown_or_missing_key_evidence_side_effects", _set(("side_effects", "extra"), True)),
        ("unknown_or_missing_key_evidence_missing", _delete(("hostile_mutations",))),
        ("input_digest_mismatch_evidence_source_hash", _set(("source_hashes", "app/routers/appointments.py"), "0" * 64)),
        ("input_digest_mismatch_evidence_semantic_hash", _set(("semantic_output_hashes", "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-plan.md"), "0" * 64)),
        ("output_digest_mismatch_evidence_fingerprint", _set(("contract_fingerprint",), "sha256:" + "0" * 64)),
        ("output_digest_mismatch_evidence_source_head", _set(("source_head",), "0" * 40)),
        ("array_reorder_or_expand_evidence_field_order", _set(("architecture_facts", "private_receipt", "canonical_field_order"), list(reversed(EXPECTED_CONTRACT["private_receipt"]["canonical_field_order"])))),
        ("array_reorder_or_expand_evidence_success_fields", _set(("architecture_facts", "public_projection", "success_fields"), ["audit_evidence", "blocks"])),
        ("array_reorder_or_expand_evidence_prechecks", _set(("architecture_facts", "admission", "pre_command_checks"), list(reversed(EXPECTED_CONTRACT["admission"]["pre_command_checks"])))),
        ("array_reorder_or_expand_evidence_locked", _set(("architecture_facts", "admission", "locked_checks"), list(reversed(EXPECTED_CONTRACT["admission"]["locked_checks"])))),
        ("array_reorder_or_expand_evidence_write_set", _set(("architecture_facts", "composition", "new_command_write_set"), list(reversed(EXPECTED_CONTRACT["composition"]["new_command_write_set"])))),
        ("array_reorder_or_expand_evidence_outcomes", _set(("architecture_facts", "outcome_mapping", "entries"), list(reversed(EXPECTED_CONTRACT["outcome_mapping"])))),
        ("array_reorder_or_expand_evidence_isolation", _set(("architecture_facts", "compatibility", "raw_delete_isolation"), list(reversed(EXPECTED_CONTRACT["compatibility"]["raw_delete_isolation"])))),
        ("dpa_005_appointment_out_leak_evidence", _set(("architecture_facts", "public_projection", "forbidden_success_fields"), [])),
        ("dpa_001_client_authority_evidence", _set(("architecture_facts", "authority_ingress", "client_authority_field_count"), 1)),
        ("dpa_004_route_local_evidence", _set(("architecture_facts", "composition", "route_local_fallback"), True)),
        ("dpa_007_replay_drift_evidence", _set(("architecture_facts", "public_projection", "current_appointment_read_for_response"), True)),
        ("dpa_012_raw_delete_evidence", _set(("architecture_facts", "compatibility", "raw_delete_isolation"), [])),
    ]
    return mutations


def reject_hostile_evidence_mutations(
    committed: dict[str, Any],
    built: dict[str, Any],
    evidence_schema: dict[str, Any],
) -> dict[str, int]:
    mutations = hostile_evidence_mutations()
    rejected = 0
    for mutation_id, mutation in mutations:
        candidate = copy.deepcopy(committed)
        mutation(candidate)
        schema_rejected = False
        try:
            validate_schema(candidate, evidence_schema)
        except (AssertionError, KeyError, TypeError, ValidationError, ValueError):
            schema_rejected = True
        if not schema_rejected and candidate == built:
            raise ValueError(f"hostile evidence mutation admitted: {mutation_id}")
        rejected += 1
    if rejected < MIN_HOSTILE_EVIDENCE_MUTATIONS:
        raise ValueError("fewer than 20 hostile evidence mutations were rejected")
    return {"attempted": len(mutations), "rejected": rejected}


def _canonical_private_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    """Serialize the six-field receipt in the frozen canonical physical order.

    The exact accepted private-receipt byte contract is compact, follows the
    frozen six-field insertion order, never sorts or reorders keys, adds no
    whitespace, emits literal UTF-8 (``ensure_ascii=False``) and rejects
    non-finite JSON constants (``allow_nan=False``). Any other physical
    representation (sorted/reordered keys, whitespace, CRLF, duplicate keys,
    alternate Unicode escaping) is noncanonical and must fail closed.
    """
    ordered = {field: receipt[field] for field in PRIVATE_RECEIPT_FIELDS}
    return json.dumps(
        ordered,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def project_public_envelope(receipt_bytes: bytes) -> bytes:
    """Project the v1 public envelope purely from validated six-field bytes.

    The supplied bytes must be the exact canonical physical private-receipt
    sequence: strict UTF-8, the frozen six-field insertion order, compact
    separators ``(',', ':')``, literal non-escaped Unicode and no reordered
    keys, added whitespace, CRLF, duplicate keys or alternate escaping.
    """
    try:
        text = receipt_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("receipt bytes are not strict UTF-8") from exc
    if "\r" in text.replace("\r\n", ""):
        raise ValueError("bare CR in receipt bytes")
    try:
        receipt = json.loads(text, parse_constant=_reject_constant)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("receipt bytes are not canonical JSON") from exc
    if not isinstance(receipt, dict):
        raise ValueError("private receipt is not a JSON object")
    if set(receipt.keys()) != PRIVATE_RECEIPT_FIELD_SET:
        raise ValueError("private receipt field set changed")
    if not isinstance(receipt["appointment_id"], str) or not receipt["appointment_id"]:
        raise ValueError("appointment_id invalid")
    if receipt["status"] != "Cancelled":
        raise ValueError("status is not the cancelled constant")
    if not isinstance(receipt["status_reason_code"], str) or not receipt["status_reason_code"]:
        raise ValueError("status_reason_code invalid")
    if receipt["cancellation_reason"] is not None and not isinstance(receipt["cancellation_reason"], str):
        raise ValueError("cancellation_reason invalid")
    if receipt["waiting_area_id"] is not None:
        raise ValueError("waiting_area_id must be null")
    warning_codes = receipt["warning_codes"]
    if not isinstance(warning_codes, list) or not all(
        isinstance(code, str) for code in warning_codes
    ):
        raise ValueError("warning_codes invalid")
    if warning_codes != sorted(warning_codes) or len(set(warning_codes)) != len(warning_codes):
        raise ValueError("warning codes are not sorted and unique")
    for code in warning_codes:
        if code not in WARNING_REGISTRY:
            raise ValueError(f"unknown warning code: {code}")
    if receipt_bytes != _canonical_private_receipt_bytes(receipt):
        raise ValueError(
            "private receipt bytes are not the canonical six-field physical sequence"
        )
    receipt_projection = {
        "appointment_id": receipt["appointment_id"],
        "cancellation_reason": receipt["cancellation_reason"],
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "status": "Cancelled",
        "status_reason_code": receipt["status_reason_code"],
        "waiting_area_id": None,
        "warning_codes": warning_codes,
    }
    envelope: dict[str, Any] = dict(PUBLIC_SUCCESS_CONSTANTS)
    envelope["receipt"] = receipt_projection
    envelope["warnings"] = [WARNING_REGISTRY[code] for code in warning_codes]
    return json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_evidence() -> dict[str, Any]:
    contract = _load_json(CONTRACT_PATH)
    contract_schema = _load_json(CONTRACT_SCHEMA_PATH)
    validate_schema(contract, contract_schema)
    validate_contract_semantics(contract)
    source_hashes = verify_source_bindings(contract)
    semantic_hashes = verify_semantic_output_hashes()
    receipt_binding = verify_precommit_receipt_binding()
    hostile = reject_hostile_mutations(contract, contract_schema)
    fingerprint = hashlib.sha256(
        json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    contract_public = contract["public_projection"]
    contract_authority = contract["authority_ingress"]
    contract_admission = contract["admission"]
    contract_composition = contract["composition"]
    contract_compat = contract["compatibility"]
    contract_claim = contract["claim_boundary"]
    contract_private = contract["private_receipt"]
    contract_proposal = contract["proposal_binding"]

    evidence = {
        "schema_version": "raisa.delete_confirm_response_product_adapter_architecture_evidence.v1",
        "result": "raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture_pass",
        "source_head": EXPECTED_SOURCE_COMMIT,
        "evidence_label": "authored_synthetic_provider_free_unmounted_architecture",
        "input_hash_mode": INPUT_HASH_MODE,
        "contract_source_head": contract["source_head"],
        "contract_fingerprint": f"sha256:{fingerprint}",
        "source_hashes": source_hashes,
        "semantic_output_hashes": semantic_hashes,
        "precommit_receipt": receipt_binding,
        "architecture_facts": {
            "private_receipt": {
                "schema_version": contract_private["schema_version"],
                "persistence_authority": contract_private["persistence_authority"],
                "canonical_field_count": len(contract_private["canonical_field_order"]),
                "canonical_field_order": contract_private["canonical_field_order"],
                "status_constant": contract_private["status_constant"],
                "waiting_area_constant": contract_private["waiting_area_constant"],
                "warning_code_order": contract_private["warning_code_order"],
                "forbidden_fields": contract_private["forbidden_fields"],
            },
            "public_projection": {
                "schema_version": contract_public["schema_version"],
                "receipt_schema_version": contract_public["receipt_schema_version"],
                "source": contract_public["source"],
                "serialization": contract_public["serialization"],
                "initial_and_replay_use_same_projection": contract_public["initial_and_replay_use_same_projection"],
                "current_appointment_read_for_response": contract_public["current_appointment_read_for_response"],
                "success_field_count": len(contract_public["success_fields"]),
                "success_fields": contract_public["success_fields"],
                "success_constants": contract_public["success_constants"],
                "warning_registry_entry_count": len(contract_public["warning_registry"]),
                "warning_registry_codes": sorted(contract_public["warning_registry"].keys()),
                "forbidden_success_fields": contract_public["forbidden_success_fields"],
            },
            "authority_ingress": {
                "server_owned_fields": contract_authority["server_owned_fields"],
                "client_authority_field_count": len(contract_authority["client_authority_fields"]),
                "capability_constant": contract_authority["capability_constant"],
                "capability_check_owner": contract_authority["capability_check_owner"],
                "current_authority_check_count": contract_authority["current_authority_check_count"],
                "command_session": contract_authority["command_session"],
                "effect_authority_before_physical_seam": contract_authority["effect_authority_before_physical_seam"],
            },
            "proposal_binding": {
                "schema_version": contract_proposal["schema_version"],
                "server_hmac_fields": contract_proposal["server_hmac_fields"],
                "client_posture": contract_proposal["client_posture"],
                "positive_source_version_required": contract_proposal["positive_source_version_required"],
            },
            "admission": {
                "pre_command_check_count": len(contract_admission["pre_command_checks"]),
                "pre_command_checks": contract_admission["pre_command_checks"],
                "locked_check_count": len(contract_admission["locked_checks"]),
                "locked_checks": contract_admission["locked_checks"],
                "effect_authority": contract_admission["effect_authority"],
            },
            "composition": {
                "transaction_factory": contract_composition["transaction_factory"],
                "new_command_write_set": contract_composition["new_command_write_set"],
                "replay_effect_count": contract_composition["replay_effect_count"],
                "route_local_fallback": contract_composition["route_local_fallback"],
            },
            "outcome_mapping": {
                "mapping_count": len(contract["outcome_mapping"]),
                "entries": contract["outcome_mapping"],
            },
            "compatibility": {
                "future_canonical_path": contract_compat["future_canonical_path"],
                "future_hidden_alias": contract_compat["future_hidden_alias"],
                "one_future_handler": contract_compat["one_future_handler"],
                "one_public_envelope_version": contract_compat["one_public_envelope_version"],
                "raw_delete_path": contract_compat["raw_delete_path"],
                "raw_delete_isolation": contract_compat["raw_delete_isolation"],
            },
            "claim_boundary": {
                "proves": contract_claim["proves"],
                "does_not_prove": contract_claim["does_not_prove"],
            },
        },
        "hostile_mutations": hostile,
        "side_effects": {
            "route_calls": 0,
            "database_connections": 0,
            "provider_calls": 0,
            "network_calls": 0,
            "subprocess_calls": 0,
            "product_patient_records": 0,
        },
        "claim_boundary": "authored_synthetic_provider_free_unmounted_architecture_only",
    }

    evidence_schema = _load_json(EVIDENCE_SCHEMA_PATH)
    validate_schema(evidence, evidence_schema)
    return evidence


def verify_evidence() -> dict[str, Any]:
    committed = _load_json(EVIDENCE_PATH)
    built = build_evidence()
    evidence_schema = _load_json(EVIDENCE_SCHEMA_PATH)
    validate_schema(committed, evidence_schema)
    if committed != built:
        raise ValueError("committed evidence does not match fresh builder output")
    return committed


def main() -> int:
    evidence = build_evidence()
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
