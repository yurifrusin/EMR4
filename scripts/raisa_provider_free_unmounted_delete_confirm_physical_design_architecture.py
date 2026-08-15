"""Validate the provider-free unmounted delete-confirm physical design.

Read-only provider-free validator for the frozen delete-confirm physical-design
architecture. It uses only the Python standard library plus ``jsonschema`` for
schema admission. It never writes files, opens a database, executes DDL/SQL,
spawns subprocesses, touches the shell, uses the network, holds credentials or
controls runtime. The committed evidence file is authored-synthetic and is
admitted by ``verify_evidence`` which compares it to the deterministic
``build_evidence`` output.
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
    "physical-design-architecture"
)
CONTRACT_PATH = BASE / "physical-design-contract.json"
SCHEMA_PATH = BASE / "physical-design-contract.schema.json"
EVIDENCE_PATH = BASE / "provider-free-physical-design-evidence.json"

MIN_HOSTILE_MUTATIONS = 60

HOSTILE_FAMILY_NAMES = {
    "synthetic_auth_reuse",
    "ambient_or_wildcard_grant",
    "automatic_capability_backfill",
    "timestamp_authority",
    "client_generation_claim",
    "grant_change_without_generation_advance",
    "missing_reason",
    "legacy_reason_promotion",
    "merged_audit_codes",
    "jsonb_replay",
    "raw_session_storage",
    "weakened_or_reordered_lock",
    "reset_wait_budget",
    "authority_after_disclosure",
    "hidden_retry",
    "full_appointment_response",
    "readback_as_commit",
}

EXPECTED_SOURCE_BINDINGS = {
    "docs/raisa-provider-free-read-only-unmounted-delete-confirm-physical-representability-review-closeout.md": "4122b7b2fbe9d712ef3cea47a2ee4f67ec7d2b55e38d594c85b89fd9d375af38",
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-representability-review-sol-acceptance.md": "3895da022f977bba9259a327bbccf7068c2b281c7a42e4ce36978f1367036975",
    "orchestration/continuity/raisa-provider-free-read-only-unmounted-delete-confirm-physical-representability-review/review-contract.json": "418c4239f7e5a85bcb76d056322ab32a50e46bda00b4b17bbac0ec79be948a2e",
    "orchestration/continuity/raisa-provider-free-read-only-unmounted-delete-confirm-physical-representability-review/provider-free-review-evidence.json": "6a5eb85b532a73169432788f59205e55e0b423056484680bb13938acb100dd6c",
    "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md": "8d8e3a388aeda71800f014535dccc63af8da6aaa945834add044dc2a49097a91",
    "docs/raisa-provider-free-unmounted-status-confirm-physical-design-architecture-plan.md": "0c7a02078aa360ecc14a6af1af8a12047bad39c68c38862d9e4360c9577556c0",
    "docs/security/raisa-provider-free-unmounted-status-confirm-physical-design-architecture-threat-model-delta.md": "3ca874ef0215fb57c74bb8e886c9bc48a912666830c9530e4165a21186dfcfc5",
    "orchestration/api_spine_adr.md": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
    "docs/api-spine/openapi/appointment-commands.yaml": "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a",
    "app/models/tenancy.py": "6be0d9ab4fc33a8709268d2f2a4550b6063e3f3e4188349c5fe3b0b6acd14431",
    "app/models/appointments.py": "d1f7960e13efb5f87d0f53334cb365bf49c24f3b6d8574ae3fe4c18a9ae22915",
    "app/schemas/appointments.py": "c35c271e9308f1f57eeeee53eefa6388087e126944ab5100c225f50066e3a0cf",
    "app/services/appointment_idempotency.py": "c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410",
    "app/routers/appointments.py": "f81fc3acc96f21efa64e1d694331792feebadf08f6384c8ac79542bb196d6624",
    "app/models/application_auth.py": "b4671fc5fd82ed06ce4af18b026ab70964a18a48e56157f719be19ce0989107b",
    "app/services/application_auth_persistence.py": "1dbfa4474178490b19c2332ebac29875641c3ea17742afe77f40aa56189f064b",
    "app/services/application_auth_role_runtime.py": "cac8a5623a838238cc68ded0c93570581391bf08226d2a312149bfe1cca87cfa",
    "alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py": "a77be7e159614a579eb2dec2d3d8e5b401f1c1d1722f5f740367ae74e6a8a59a",
    "alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py": "da6493f60b8a8d39186c273db0b9615758b3927cc913d1117d12df0003f245fd",
    "alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py": "78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae",
}

EXPECTED_API_BOUNDARY = {
    "classification": "rest_openapi_delete_confirm_command_security_audit_idempotency",
    "operation_id": "confirmAppointmentDeleteProposal",
    "route_family": "delete-confirm",
    "dedicated_ingress_only": True,
    "graphql_read_only": True,
    "events_non_authoritative_acceleration_hints": True,
    "model_context_fabric_channel_inert_proposals": True,
    "raw_compatibility_delete_ingress_authority": False,
    "status_family_cancellation_ingress_authority": False,
    "public_response_schema_changed": False,
    "private_receipt_fields_publicly_mapped": False,
}

EXPECTED_PRODUCT_AUTHORITY_FENCE = {
    "table": "users",
    "generation_column": "authority_generation",
    "postgresql_type": "BIGINT",
    "domain_minimum": 1,
    "domain_maximum": 9223372036854775807,
    "null_zero_negative_overflow_outcome": "fail_closed",
    "composite_uniqueness": ["practice_id", "id"],
    "generation_owner": "postgresql",
    "insert_policy": "force_generation_one",
    "update_policy": "preserve_old_generation_unless_practice_role_or_is_active_changes",
    "advance_event": "exactly_once_per_qualifying_update",
    "grant_change_advance": "same_transaction_before_grant_change_commits",
    "capability_identity_immutable": True,
    "capability_reassignment": "delete_then_insert_advances_generation_for_each_change",
    "overflow_outcome": "reject_whole_transaction",
    "submitted_generation_policy": "ignored_by_database",
    "synthetic_application_auth_relations_ineligible": True,
}

EXPECTED_USER_CAPABILITY_GRANTS = {
    "relation": "user_capability_grants",
    "columns": [
        {"name": "practice_id", "type": "UUID", "nullable": False},
        {"name": "user_id", "type": "UUID", "nullable": False},
        {"name": "capability_code", "type": "VARCHAR(100)", "nullable": False},
    ],
    "primary_key": ["practice_id", "user_id", "capability_code"],
    "composite_foreign_key": ["practice_id", "user_id"],
    "references": "users(practice_id, id)",
    "admitted_capabilities": ["appointment.cancel.confirm", "appointment.read"],
    "grant_semantics": "row_presence_is_grant_absence_is_denial",
    "wildcard_representable": False,
    "json_claim_capable": False,
    "client_role_claim_capable": False,
    "model_output_capable": False,
    "automatic_grant_to_existing_users": False,
    "later_explicit_provisioning_gate_required": True,
    "cancel_does_not_imply_read": True,
    "read_requires_separate_grant": True,
}

EXPECTED_AUTHORITY_CHECK = {
    "fence_lock_resource": "users",
    "fence_lock_predicate": "practice_id_and_actor_user_id",
    "fence_lock_strength": "FOR SHARE",
    "lock_prevents_generation_mutation_commit": True,
    "admitted_roles": ["Receptionist", "GP", "Nurse", "Admin", "PracticeOwner"],
    "required_conditions": [
        "locked_row_exists_at_authenticated_practice_and_actor_identity",
        "is_active_true",
        "locked_role_equals_authenticated_server_role",
        "locked_role_admitted",
        "signed_authority_generation_equals_locked_current_generation",
        "exact_grant_appointment_cancel_confirm_exists",
    ],
    "check_count": 2,
}

EXPECTED_AUTHORITY_MIGRATION = {
    "phases": [
        "add_users_authority_generation_nullable_without_table_rewriting_default",
        "set_server_default_one_for_subsequent_inserts",
        "backfill_existing_user_generations_to_baseline_one_without_claiming_prior_chronology",
        "add_and_validate_positive_range_check_then_set_not_null",
        "add_and_validate_unique_practice_id_id",
        "create_closed_capability_relation_with_no_rows",
        "install_generation_owner_and_grant_change_triggers_before_any_consumer",
        "prove_no_null_or_nonpositive_generation_and_no_orphan_or_unknown_grant",
        "grant_no_capability_and_mount_no_consumer",
        "retain_generation_server_default_for_new_users",
    ],
    "historical_backfill_claim": "baseline_one_not_authority_chronology",
    "runtime_before_completion": False,
    "capability_rows_after_migration": 0,
    "automatic_capability_grant": False,
}

EXPECTED_ROLLBACK_CONTRACT = {
    "schema_only_before_first_use": True,
    "permitted_before_first_use": ["any_capability_grant", "any_command_receipt"],
    "after_first_use": "forward_only",
    "automatic_downgrade_after_first_use": "fail_closed",
}

EXPECTED_APPOINTMENT_TRUTH = {
    "table": "appointments",
    "state_version_column": "appointment_state_version",
    "postgresql_type": "BIGINT",
    "minimum": 1,
    "maximum": 9223372036854775807,
    "insert_value": 1,
    "state_version_owner": "postgresql_database_owned_positive",
    "new_version_identity_added": False,
    "new_timestamp_identity_added": False,
    "effect_locked_at_version": "n",
    "effect_publishes_version": "n_plus_one",
    "status": "Cancelled",
    "waiting_area_id": "json_null",
    "mandatory_structured_reason": True,
    "nullable_free_text": True,
}

EXPECTED_STATUS_REASON_CODES = {
    "accepted_codes": [
        "PATIENT_CANCELLED",
        "PATIENT_RESCHEDULED",
        "PATIENT_UNWELL",
        "PATIENT_TRANSPORT",
        "PRACTITIONER_UNAVAILABLE",
        "CLINIC_OPERATIONAL",
        "CLINIC_RESCHEDULED",
        "ADMIN_ERROR",
        "DUPLICATE_BOOKING",
        "OTHER",
    ],
    "rejected_codes": ["LEGACY_UNCLASSIFIED", "missing_code", "status_family_only_codes"],
    "cancellation_reason_encoding": "json_null_or_unicode_string",
    "cancellation_reason_max_length": 500,
    "signature_and_request_bound": True,
    "byte_for_value_copy_targets": ["appointment_truth", "audit_state", "canonical_response"],
    "confirmed_warnings": "human_acknowledgement_set_not_reason",
}

EXPECTED_PRIVATE_COMPLETED_RECEIPT = {
    "table": "appointment_command_idempotency",
    "contract_version_column": "completed_receipt_version",
    "contract_version": 1,
    "family_qualified": True,
    "existing_reused_fields": [
        "completed_receipt_version",
        "session_binding_digest",
        "pre_state_version",
        "post_state_version",
        "response_body_canonical_bytes",
    ],
    "single_additive_field": {
        "name": "authority_generation",
        "type": "BIGINT",
        "nullable_for_legacy": True,
    },
    "family_qualified_v1_disjunction": [
        "unchanged_status_confirm_branch",
        "delete_confirm_branch_with_positive_authority_generation",
        "delete_confirm_branch_with_32_byte_session_binding_digest",
        "delete_confirm_branch_with_positive_pre_post_and_post_equals_pre_plus_one",
        "delete_confirm_branch_with_nonempty_canonical_bytes",
        "delete_confirm_branch_with_target_and_audit_identities",
        "delete_confirm_branch_with_response_status_hash_json_and_completed_state",
    ],
    "no_other_operation_may_set_version": True,
    "legacy_rows": "remain_null_not_inferred_or_backfilled",
    "legacy_replay_outcome": "legacy_receipt_not_replayable",
    "session_binding": {
        "algorithm": "HMAC-SHA-256",
        "stored_form": "32_raw_digest_bytes",
        "domain_separator": "appointment-delete-session:v1",
        "message_fields": ["practice_id", "actor_user_id", "authenticated_session_id"],
        "raw_session_stored": False,
        "secret_stored": False,
    },
    "same_digest_replay_outcome": "stored_receipt_only",
    "legacy_exact_match_outcome": "legacy_receipt_not_replayable",
    "replay_requires": [
        "actor_match",
        "role_match",
        "operation_match",
        "route_match",
        "target_match",
        "request_digest_match",
        "authority_generation_match",
        "session_digest_match",
        "completed_receipt_version_one",
        "stored_byte_digest_valid",
        "current_authority",
    ],
}

EXPECTED_CANONICAL_RESPONSE = {
    "authoritative_storage": "response_body_canonical_bytes",
    "jsonb_is_delivery_authority": False,
    "fields_in_order": [
        "appointment_id",
        "status",
        "status_reason_code",
        "cancellation_reason",
        "waiting_area_id",
        "warning_codes",
    ],
    "status_constant": "Cancelled",
    "encoding": "UTF-8",
    "byte_order_mark": False,
    "insignificant_whitespace": False,
    "string_escaping": "RFC8259",
    "nullable_encoding": "json_null",
    "warning_order": "already_validated_canonical_order",
    "duplicate_keys_rejected": True,
    "extra_fields_rejected": True,
    "non_finite_values_rejected": True,
    "digest": "lowercase_hex_sha256_of_exact_stored_bytes",
    "digest_compare": "constant_time_before_replay",
    "initial_delivery": "exact_stored_byte_buffer_without_reserialization",
    "replay_delivery": "exact_stored_bytes_without_reserialization",
    "integrity_failure": "release_no_body_and_fail_closed",
    "current_full_response_not_accepted": True,
    "compatibility_or_version_transition": "later_explicit_gate",
}

EXPECTED_ATTRIBUTABLE_AUDIT = {
    "table": "appointment_audit_log",
    "audit_contract_version": 1,
    "additive_fields": [
        {"name": "audit_contract_version", "type": "SMALLINT", "nullable": True},
        {"name": "authority_generation", "type": "BIGINT", "nullable": True},
        {"name": "pre_state_version", "type": "BIGINT", "nullable": True},
        {"name": "post_state_version", "type": "BIGINT", "nullable": True},
        {"name": "waiting_area_before_id", "type": "UUID", "nullable": True},
        {"name": "waiting_area_after_id", "type": "UUID", "nullable": True},
        {"name": "audit_evidence_codes", "type": "JSONB", "nullable": True},
    ],
    "v1_required": [
        "action_delete",
        "command_id_non_null",
        "positive_authority_generation",
        "positive_pre_state_version",
        "positive_post_state_version",
        "post_equals_pre_plus_one",
        "status_after_cancelled",
        "structured_reason_non_null",
        "waiting_area_after_id_null",
    ],
    "confirmed_warnings": "stores_only_exact_human_warning_acknowledgements",
    "audit_evidence_codes": "stores_only_bounded_internal_evidence_codes_as_json_array",
    "legacy_merged_array_not_reinterpreted": True,
    "command_fk_binds": ["session_binding_digest", "request_digest", "operation_identity"],
    "raw_authenticated_session_id_in_audit": False,
    "precommit_cross_artifact_equality": [
        "practice",
        "target",
        "actor",
        "authority_generation",
        "pre_state_version",
        "post_state_version",
        "statuses",
        "waiting_area_transition",
        "structured_reason",
        "nullable_cancellation_text",
        "warning_codes",
    ],
}

EXPECTED_TRANSACTION_CONTRACT = {
    "owner": "backend_delete_confirm_kernel",
    "isolation": "READ COMMITTED",
    "single_transaction": True,
    "cumulative_lock_wait_budget_ms": 2000,
    "budget_policy": "apply_only_positive_remaining_budget_before_each_lock_budget_never_resets",
    "nowait": False,
    "skip_locked": False,
    "advisory_locks": False,
    "hidden_effect_retries": False,
    "locks": [
        {
            "resource": "users_authority_fence",
            "strength": "FOR SHARE",
            "predicate": "practice_id_and_actor_user_id",
            "position": 1,
        },
        {
            "resource": "appointment",
            "strength": "FOR UPDATE",
            "predicate": "practice_id_and_appointment_id",
            "position": 2,
        },
        {
            "resource": "idempotency_record",
            "strength": "FOR UPDATE",
            "predicate": "practice_actor_operation_and_hashed_key",
            "position": 3,
        },
    ],
    "idempotency_insert": "target_bound_insert_on_conflict_do_nothing_returning_then_lock_winning_row_without_releasing_appointment_lock",
    "idempotency_identity": ["practice_id", "actor_user_id", "operation_id", "idempotency_key_hash"],
    "authority_check_positions": [5, 7],
    "replay_only": "complete_integrity_valid_family_qualified_v1_receipt",
    "new_command_verification": [
        "explicit_confirmation",
        "exact_warning_acknowledgement",
        "signed_evidence",
        "expiry",
        "locked_source_state",
        "exact_reasons",
    ],
    "decision_trace": [
        "reject_malformed_or_non_dedicated_ingress_and_missing_idempotency_identity",
        "begin_command_owned_transaction_and_cumulative_lock_deadline",
        "lock_server_selected_product_authority_fence_for_share",
        "lock_appointment_for_update_or_stop_non_disclosing_before_idempotency_access",
        "first_complete_current_authority_and_signed_generation_check",
        "select_exact_idempotency_row_for_update_or_insert_target_bound_conflict_do_nothing_returning_then_lock_winning_row_without_releasing_appointment_lock",
        "repeat_complete_current_authority_check_while_every_lock_held",
        "classify_exact_actor_role_generation_session_operation_route_target_key_and_request_bindings",
        "replay_only_complete_integrity_valid_family_qualified_v1_receipt",
        "for_new_command_verify_explicit_confirmation_exact_warning_acknowledgement_signed_evidence_expiry_locked_source_state_and_exact_reasons",
        "stage_one_appointment_soft_cancel_one_versioned_delete_audit_and_one_complete_private_receipt",
        "flush_once_and_require_database_owned_post_version_equals_pre_plus_one",
        "require_every_cross_artifact_identity_state_reason_and_warning_equality",
        "commit_appointment_audit_and_receipt_atomically",
        "deliver_only_stored_canonical_response_bytes",
    ],
    "flush_count": "once",
    "post_version_requirement": "database_owned_post_version_equals_pre_plus_one",
    "atomic_write_set": ["appointment_soft_cancel", "versioned_delete_audit", "complete_private_receipt"],
    "same_digest_replay_requires": [
        "actor_match",
        "role_match",
        "operation_match",
        "route_match",
        "target_match",
        "request_digest_match",
        "authority_generation_match",
        "session_digest_match",
        "completed_receipt_version_one",
        "stored_byte_digest_valid",
        "current_authority",
    ],
    "non_disclosing_outcomes": [
        "target_not_found",
        "authority_revoked",
        "idempotency_conflict",
        "legacy_receipt_not_replayable",
        "in_progress_not_replayable",
        "receipt_integrity_failure",
        "transaction_rolled_back",
    ],
}

EXPECTED_FAILURE_POLICY = {
    "lock_timeout": "rollback_generic_transient_no_receipt_disclosure",
    "deadlock": "rollback_generic_transient_no_receipt_disclosure",
    "serialization_failure": "rollback_generic_transient_no_receipt_disclosure",
    "connection_loss_before_commit": "rollback_generic_transient_no_receipt_disclosure",
    "connection_loss_after_commit": "delivery_unknown_client_retries_same_key",
    "server_effect_retry": False,
    "atomic_write_set": ["appointment_soft_cancel", "versioned_delete_audit", "complete_private_receipt"],
}

EXPECTED_FRESH_READBACK = {
    "begins_after_commit_only": True,
    "new_transaction": True,
    "re_resolves": "server_authenticated_practice_id_and_actor_user_id",
    "requires": ["current_active_membership", "current_role", "exact_appointment_read_grant"],
    "resource_authorization": "practice_id_and_appointment_id",
    "returns": "current_appointment_truth",
    "denial_outcome": "cannot_undo_committed_command_or_change_stored_receipt_or_imply_failure",
    "evidence_role": "reconciliation_only",
    "never_proves_commit": True,
    "command_response_contains_no_display_data": True,
    "excluded_display_data": ["patient", "practitioner", "free_form_appointment_reason", "notes", "contact"],
}

EXPECTED_NON_AUTHORITY_SURFACES = {
    "raw_compatibility_delete": "separate_ingress_inherits_no_authority",
    "status_family_cancellation_path": "separate_ingress_inherits_no_authority",
    "model_output": "inert_proposal_no_command_authority",
    "context_fabric": "inert_proposal_no_command_authority",
    "channel_output": "inert_proposal_no_command_authority",
    "events": "non_authoritative_acceleration_hints",
    "graphql": "read_only",
    "client_role_claims": "cannot_synthesize_grant",
    "json_claims": "cannot_synthesize_grant",
    "wildcard": "not_representable",
}

EXPECTED_WORKER_ALLOCATION = {
    "sol_owns": ["material_architecture", "source_binding", "acceptance", "git"],
    "deepseek_role": "bounded_mechanical_implementation_only",
    "deepseek_authority": {
        "closed_contract": True,
        "schema": True,
        "provider_free_validator": True,
        "evidence": True,
        "focused_tests": True,
        "semantic_choice": False,
        "acceptance": False,
        "integration": False,
        "protected_ref": False,
    },
    "gemini_verifier": "gemini_3_6_flash_high",
    "gemini_role": "fresh_independent_veto_exact_candidate",
    "gemini_authority": {
        "semantic_choice": False,
        "acceptance": False,
        "integration": False,
        "protected_ref": False,
    },
    "gemini_3_7_flash_high": "not_yet_admitted_no_silent_substitution",
    "native_subagents": "not_useful_for_same_closed_mechanical_artifact_set",
}

EXPECTED_FORBIDDEN_KEYS = {
    "protected_path_content_or_metadata_used",
    "application_model_migration_service_or_route_edited",
    "application_or_database_module_imported",
    "executable_ddl_or_sql_emitted",
    "route_or_database_executed",
    "real_transaction_or_lock_opened",
    "capability_provisioned",
    "provider_or_adc_used",
    "credential_iam_or_browser_authorization_used",
    "product_or_patient_data_used",
    "watcher_or_event_authority_added",
    "product_command_executed",
    "deployment_release_or_pages_opened",
    "protected_ref_moved",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_schema(contract: dict[str, Any], schema: dict[str, Any]) -> None:
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)


def verify_source_bindings(contract: dict[str, Any]) -> dict[str, str]:
    declared = {item["path"]: item["sha256"] for item in contract["source_bindings"]}
    if declared != EXPECTED_SOURCE_BINDINGS:
        raise ValueError("exact source binding set changed")
    observed: dict[str, str] = {}
    for relative_path, expected_hash in EXPECTED_SOURCE_BINDINGS.items():
        path = ROOT / relative_path
        if not path.is_file():
            raise ValueError(f"source missing: {relative_path}")
        digest = _sha256(path)
        if digest != expected_hash:
            raise ValueError(f"source hash mismatch: {relative_path}")
        observed[relative_path] = digest
    return observed


def validate_contract_semantics(contract: dict[str, Any]) -> None:
    if contract["source_head"] != "6514d35c465e304a421218890264f61c33ba51bb":
        raise ValueError("source head changed")
    if contract["implementation_authorized"] is not False:
        raise ValueError("implementation authority opened")
    if contract["api_boundary"] != EXPECTED_API_BOUNDARY:
        raise ValueError("API boundary changed")
    if contract["product_authority_fence"] != EXPECTED_PRODUCT_AUTHORITY_FENCE:
        raise ValueError("product authority fence changed")
    if contract["user_capability_grants"] != EXPECTED_USER_CAPABILITY_GRANTS:
        raise ValueError("capability relation changed")
    if contract["authority_check"] != EXPECTED_AUTHORITY_CHECK:
        raise ValueError("authority check contract changed")
    if contract["authority_migration"] != EXPECTED_AUTHORITY_MIGRATION:
        raise ValueError("authority migration contract changed")
    if contract["rollback_contract"] != EXPECTED_ROLLBACK_CONTRACT:
        raise ValueError("rollback contract changed")
    if contract["appointment_truth"] != EXPECTED_APPOINTMENT_TRUTH:
        raise ValueError("appointment truth contract changed")
    if contract["status_reason_codes"] != EXPECTED_STATUS_REASON_CODES:
        raise ValueError("status reason contract changed")
    if contract["private_completed_receipt"] != EXPECTED_PRIVATE_COMPLETED_RECEIPT:
        raise ValueError("private completed receipt contract changed")
    if contract["canonical_response"] != EXPECTED_CANONICAL_RESPONSE:
        raise ValueError("canonical response contract changed")
    if contract["attributable_audit"] != EXPECTED_ATTRIBUTABLE_AUDIT:
        raise ValueError("attributable audit contract changed")
    if contract["transaction_contract"] != EXPECTED_TRANSACTION_CONTRACT:
        raise ValueError("transaction contract changed")
    if contract["failure_policy"] != EXPECTED_FAILURE_POLICY:
        raise ValueError("failure policy changed")
    if contract["fresh_readback"] != EXPECTED_FRESH_READBACK:
        raise ValueError("fresh readback contract changed")
    if contract["non_authority_surfaces"] != EXPECTED_NON_AUTHORITY_SURFACES:
        raise ValueError("non-authority surface contract changed")
    if contract["worker_allocation"] != EXPECTED_WORKER_ALLOCATION:
        raise ValueError("worker allocation changed")
    if set(contract["forbidden"]) != EXPECTED_FORBIDDEN_KEYS:
        raise ValueError("forbidden surface set changed")
    if set(contract["forbidden"].values()) != {False}:
        raise ValueError("forbidden surface opened")
    if contract["next_candidate"] != (
        "provider_free_unmounted_delete_confirm_physical_schema_and_"
        "transaction_scaffold_implementation"
    ):
        raise ValueError("next candidate changed")


Mutation = Callable[[dict[str, Any]], None]


def _set(path: tuple[Any, ...], value: Any) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value

    return mutate


def hostile_mutations() -> list[tuple[str, Mutation]]:
    mutations: list[tuple[str, Mutation]] = [
        ("source_head", _set(("source_head",), "0" * 40)),
        ("implementation", _set(("implementation_authorized",), True)),
        ("evidence_label", _set(("evidence_label",), "runtime")),
        ("dedicated_ingress", _set(("api_boundary", "dedicated_ingress_only"), False)),
        ("graphql_write", _set(("api_boundary", "graphql_read_only"), False)),
        ("event_authority", _set(("api_boundary", "events_non_authoritative_acceleration_hints"), False)),
        ("model_authority", _set(("api_boundary", "model_context_fabric_channel_inert_proposals"), False)),
        ("raw_compat_authority", _set(("api_boundary", "raw_compatibility_delete_ingress_authority"), True)),
        ("status_family_authority", _set(("api_boundary", "status_family_cancellation_ingress_authority"), True)),
        ("public_schema", _set(("api_boundary", "public_response_schema_changed"), True)),
        ("private_mapped", _set(("api_boundary", "private_receipt_fields_publicly_mapped"), True)),
        ("synthetic_auth_reuse", _set(("product_authority_fence", "synthetic_application_auth_relations_ineligible"), False)),
        ("client_generation_claim", _set(("product_authority_fence", "submitted_generation_policy"), "accepted")),
        ("grant_change_without_generation_advance", _set(("product_authority_fence", "grant_change_advance"), "after_grant_change_commits")),
        ("generation_owner_app", _set(("product_authority_fence", "generation_owner"), "application")),
        ("domain_zero", _set(("product_authority_fence", "domain_minimum"), 0)),
        ("overflow_accept", _set(("product_authority_fence", "overflow_outcome"), "accept")),
        ("ambient_or_wildcard_grant", _set(("user_capability_grants", "wildcard_representable"), True)),
        ("json_claim_grant", _set(("user_capability_grants", "json_claim_capable"), True)),
        ("client_role_grant", _set(("user_capability_grants", "client_role_claim_capable"), True)),
        ("model_output_grant", _set(("user_capability_grants", "model_output_capable"), True)),
        ("automatic_capability_backfill", _set(("authority_migration", "automatic_capability_grant"), True)),
        ("capability_rows", _set(("authority_migration", "capability_rows_after_migration"), 1)),
        ("runtime_early", _set(("authority_migration", "runtime_before_completion"), True)),
        ("fake_history", _set(("authority_migration", "historical_backfill_claim"), "historical_chronology")),
        ("rollback_after_use", _set(("rollback_contract", "after_first_use"), "both_directions")),
        ("unsafe_downgrade", _set(("rollback_contract", "automatic_downgrade_after_first_use"), "permitted")),
        ("timestamp_authority", _set(("appointment_truth", "new_timestamp_identity_added"), True)),
        ("new_version_id", _set(("appointment_truth", "new_version_identity_added"), True)),
        ("version_owner_app", _set(("appointment_truth", "state_version_owner"), "application")),
        ("missing_reason", _set(("appointment_truth", "mandatory_structured_reason"), False)),
        ("legacy_reason_promotion", _set(("status_reason_codes", "rejected_codes", 0), "PATIENT_CANCELLED")),
        ("free_text_bound", _set(("status_reason_codes", "cancellation_reason_max_length"), 1000)),
        ("text_signature_bound", _set(("status_reason_codes", "signature_and_request_bound"), False)),
        ("jsonb_replay", _set(("canonical_response", "jsonb_is_delivery_authority"), True)),
        ("bom", _set(("canonical_response", "byte_order_mark"), True)),
        ("whitespace", _set(("canonical_response", "insignificant_whitespace"), True)),
        ("full_appointment_response", _set(("canonical_response", "current_full_response_not_accepted"), False)),
        ("reserialize_initial", _set(("canonical_response", "initial_delivery"), "reserialize_jsonb")),
        ("reserialize_replay", _set(("canonical_response", "replay_delivery"), "reserialize_jsonb")),
        ("integrity_release", _set(("canonical_response", "integrity_failure"), "release_anyway")),
        ("raw_session_storage", _set(("private_completed_receipt", "session_binding", "raw_session_stored"), True)),
        ("stored_secret", _set(("private_completed_receipt", "session_binding", "secret_stored"), True)),
        ("weak_session_hash", _set(("private_completed_receipt", "session_binding", "algorithm"), "SHA-1")),
        ("legacy_backfill", _set(("private_completed_receipt", "legacy_rows"), "inferred_and_backfilled")),
        ("legacy_replay", _set(("private_completed_receipt", "legacy_replay_outcome"), "replayable")),
        ("receipt_version_change", _set(("private_completed_receipt", "contract_version"), 2)),
        ("merged_audit_codes", _set(("attributable_audit", "legacy_merged_array_not_reinterpreted"), False)),
        ("raw_audit_session", _set(("attributable_audit", "raw_authenticated_session_id_in_audit"), True)),
        ("audit_version_change", _set(("attributable_audit", "audit_contract_version"), 2)),
        ("warnings_as_reason", _set(("attributable_audit", "confirmed_warnings"), "merged_reason_storage")),
        ("isolation", _set(("transaction_contract", "isolation"), "READ UNCOMMITTED")),
        ("multi_transaction", _set(("transaction_contract", "single_transaction"), False)),
        ("reset_wait_budget", _set(("transaction_contract", "budget_policy"), "reset_budget_per_lock")),
        ("budget_zero", _set(("transaction_contract", "cumulative_lock_wait_budget_ms"), 0)),
        ("nowait", _set(("transaction_contract", "nowait"), True)),
        ("skip_locked", _set(("transaction_contract", "skip_locked"), True)),
        ("advisory_locks", _set(("transaction_contract", "advisory_locks"), True)),
        ("hidden_retry", _set(("transaction_contract", "hidden_effect_retries"), True)),
        ("idempotency_insert_claim_first", _set(("transaction_contract", "idempotency_insert"), "claim_before_lock")),
        ("server_retry", _set(("failure_policy", "server_effect_retry"), True)),
        ("connection_loss_reveal", _set(("failure_policy", "connection_loss_before_commit"), "reveal_receipt")),
        ("readback_as_commit", _set(("fresh_readback", "never_proves_commit"), False)),
        ("readback_before_commit", _set(("fresh_readback", "begins_after_commit_only"), False)),
        ("readback_wrong_capability", _set(("fresh_readback", "requires", 2), "appointment.cancel.confirm")),
        ("readback_returns_full", _set(("fresh_readback", "returns"), "full_appointment_display")),
        ("display_data_leak", _set(("fresh_readback", "command_response_contains_no_display_data"), False)),
        ("non_authority_model", _set(("non_authority_surfaces", "model_output"), "command_authority")),
        ("non_authority_channel", _set(("non_authority_surfaces", "channel_output"), "command_authority")),
        ("non_authority_event", _set(("non_authority_surfaces", "events"), "command_authority")),
        ("non_authority_graphql", _set(("non_authority_surfaces", "graphql"), "mutation")),
        ("gemini_substitution", _set(("worker_allocation", "gemini_verifier"), "gemini_3_7_flash_high")),
        ("deepseek_acceptance", _set(("worker_allocation", "deepseek_authority", "acceptance"), True)),
        ("next_runtime", _set(("next_candidate",), "mounted_runtime")),
    ]
    for index in range(20):
        mutations.append(
            (f"source_hash_{index}", _set(("source_bindings", index, "sha256"), "0" * 64))
        )
    for index in range(10):
        mutations.append(
            (f"migration_phase_{index}", _set(("authority_migration", "phases", index), "weakened"))
        )
    for index in range(10):
        mutations.append(
            (f"accepted_code_{index}", _set(("status_reason_codes", "accepted_codes", index), "LEGACY_UNCLASSIFIED"))
        )
    for index in range(6):
        mutations.append(
            (f"public_field_{index}", _set(("canonical_response", "fields_in_order", index), "private_field"))
        )
    for index in range(3):
        mutations.extend(
            [
                (f"weakened_or_reordered_lock_resource_{index}", _set(("transaction_contract", "locks", index, "resource"), "weakened")),
                (f"weakened_or_reordered_lock_strength_{index}", _set(("transaction_contract", "locks", index, "strength"), "FOR KEY SHARE")),
            ]
        )
    for index in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
        mutations.append(
            (f"decision_trace_{index}", _set(("transaction_contract", "decision_trace", index), "reordered"))
        )
    for index in range(7):
        mutations.append(
            (f"audit_field_{index}", _set(("attributable_audit", "additive_fields", index, "name"), "weakened"))
        )
    for index in range(2):
        mutations.append(
            (f"capability_code_{index}", _set(("user_capability_grants", "admitted_capabilities", index), "appointment.delete"))
        )
    for index in range(3):
        mutations.append(
            (f"capability_column_{index}", _set(("user_capability_grants", "columns", index, "name"), "weakened"))
        )
    for key in sorted(EXPECTED_FORBIDDEN_KEYS):
        mutations.append((f"forbidden_{key}", _set(("forbidden", key), True)))
    # authority-after-disclosure is encoded by moving the second authority check
    # to after the classification and replay steps.
    mutations.append(
        (
            "authority_after_disclosure",
            _set(
                ("transaction_contract", "decision_trace", 7),
                "first_complete_current_authority_and_signed_generation_check",
            ),
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
        raise ValueError("fewer than 60 hostile mutations were rejected")
    return {"attempted": len(mutations), "rejected": rejected}


def build_evidence() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    validate_schema(contract, schema)
    validate_contract_semantics(contract)
    source_hashes = verify_source_bindings(contract)
    hostile = reject_hostile_mutations(contract, schema)
    fingerprint = hashlib.sha256(
        json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema_version": "raisa.delete_confirm_physical_design_architecture_evidence.v1",
        "result": contract["result"],
        "source_head": contract["source_head"],
        "evidence_label": contract["evidence_label"],
        "implementation_authorized": contract["implementation_authorized"],
        "source_hashes": source_hashes,
        "contract_fingerprint": f"sha256:{fingerprint}",
        "architecture_facts": {
            "authority_fence_table": contract["product_authority_fence"]["table"],
            "generation_owner": contract["product_authority_fence"]["generation_owner"],
            "capability_count": len(contract["user_capability_grants"]["admitted_capabilities"]),
            "admitted_roles": contract["authority_check"]["admitted_roles"],
            "migration_phase_count": len(contract["authority_migration"]["phases"]),
            "reason_code_count": len(contract["status_reason_codes"]["accepted_codes"]),
            "receipt_single_additive_field": contract["private_completed_receipt"]["single_additive_field"]["name"],
            "canonical_field_count": len(contract["canonical_response"]["fields_in_order"]),
            "audit_additive_field_count": len(contract["attributable_audit"]["additive_fields"]),
            "lock_order": [item["resource"] for item in contract["transaction_contract"]["locks"]],
            "cumulative_lock_wait_budget_ms": contract["transaction_contract"]["cumulative_lock_wait_budget_ms"],
            "authority_check_count": contract["authority_check"]["check_count"],
            "readback_never_proves_commit": contract["fresh_readback"]["never_proves_commit"],
            "implementation_authorized": False,
        },
        "hostile_mutations": hostile,
        "forbidden": contract["forbidden"],
        "next_candidate": contract["next_candidate"],
    }


def verify_evidence() -> dict[str, Any]:
    committed = _load(EVIDENCE_PATH)
    built = build_evidence()
    if committed != built:
        raise ValueError("committed evidence does not match fresh builder output")
    return committed


def main() -> int:
    evidence = build_evidence()
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
