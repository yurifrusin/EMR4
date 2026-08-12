"""Validate the provider-free unmounted status-confirm physical design."""

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
    / "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "physical-design-architecture"
)
CONTRACT_PATH = BASE / "physical-design-contract.json"
SCHEMA_PATH = BASE / "physical-design-contract.schema.json"
EVIDENCE_PATH = BASE / "provider-free-unmounted-architecture-evidence.json"

EXPECTED_SOURCE_BINDINGS = {
    "docs/raisa-provider-free-read-only-status-confirm-physical-representability-review-closeout.md": "a587fe03ee8a4a0b51ae1f17308c31dc9660bb96c17e3f508bbb2692b5339189",
    "orchestration/agent_inbox/codex/raisa-status-confirm-physical-representability-review-sol-acceptance.md": "72997a4b0358b15201c36da976eff827fba49f4bd14de3b354dfa0eb4738d659",
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-physical-representability-review/physical-representability-review-contract.json": "c255e52d5b2c8a90ad2e975b8b55d87b8248aa571811eb1ad3b1049a326e786d",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.json": "6f2c970a4ab9234e72d6ffb08b2aa9b8738b779b94cee1885dbf262bfb5306ce",
    "orchestration/api_spine_adr.md": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
    "docs/api-spine/openapi/appointment-commands.yaml": "c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6",
    "app/models/appointments.py": "af00f7318da3f19732843c75b56721db89a3fa0c94b6e0feeb12a614850c4952",
    "app/services/appointment_idempotency.py": "c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410",
    "alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py": "a77be7e159614a579eb2dec2d3d8e5b401f1c1d1722f5f740367ae74e6a8a59a",
    "alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py": "da6493f60b8a8d39186c273db0b9615758b3927cc913d1117d12df0003f245fd",
    "alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py": "78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae",
}

EXPECTED_API_BOUNDARY = {
    "classification": "rest_openapi_status_confirm_command_security_audit_idempotency",
    "operation_id": "confirmAppointmentStatusProposal",
    "route_family": "status-confirm",
    "public_response_schema_changed": False,
    "private_receipt_fields_publicly_mapped": False,
    "graphql_mutation_authority": False,
    "event_command_authority": False,
}

EXPECTED_STATE_VERSION = {
    "table": "appointments",
    "column": "appointment_state_version",
    "postgresql_type": "BIGINT",
    "minimum": 1,
    "maximum": 9223372036854775807,
    "nullable_after_migration": False,
    "insert_value": 1,
    "increment_owner": "postgresql_before_update_trigger",
    "submitted_value_policy": "replace_with_old_plus_one",
    "increment_event": "every_committed_appointment_row_update_exactly_once",
    "timestamp_substitution": False,
    "overflow_outcome": "transaction_aborted",
    "trigger_is_watcher_or_event": False,
}

EXPECTED_MIGRATION = {
    "phases": [
        "add_nullable_bigint_without_default",
        "set_server_default_one_for_new_inserts",
        "backfill_existing_nulls_to_cutover_baseline_one",
        "add_not_valid_positive_range_check_validate_then_set_not_null",
        "install_database_owned_before_update_trigger",
        "prove_no_null_nonpositive_or_overrange_rows",
        "expose_version_only_after_all_prior_phases",
    ],
    "historical_backfill_claim": (
        "cutover_baseline_not_historical_revision_chronology"
    ),
    "server_default_retained": True,
    "runtime_before_completion": False,
    "automatic_downgrade_after_first_v1_receipt": False,
    "post_adoption_recovery": "forward_only",
}

EXPECTED_ADDITIVE_FIELDS = [
    {"name": "completed_receipt_version", "type": "SMALLINT", "nullable_for_legacy": True},
    {"name": "session_binding_digest", "type": "BYTEA", "nullable_for_legacy": True},
    {"name": "pre_state_version", "type": "BIGINT", "nullable_for_legacy": True},
    {"name": "post_state_version", "type": "BIGINT", "nullable_for_legacy": True},
    {"name": "response_body_canonical_bytes", "type": "BYTEA", "nullable_for_legacy": True},
]

EXPECTED_EXISTING_RECEIPT_FIELDS = [
    "practice_id",
    "actor_user_id",
    "actor_role",
    "operation_id",
    "route_family",
    "idempotency_key_hash",
    "request_body_hash",
    "state",
    "response_status_code",
    "response_body_hash",
    "response_body_json",
    "result_kind",
    "target_appointment_id",
    "audit_log_id",
]

EXPECTED_RECEIPT_CONSTRAINTS = [
    "operation_and_route_are_exact_status_confirm",
    "all_five_additive_fields_are_non_null",
    "session_binding_digest_has_exactly_32_bytes",
    "pre_and_post_versions_are_positive",
    "post_state_version_equals_pre_state_version_plus_one",
    "canonical_response_bytes_are_nonempty",
    "existing_target_audit_status_hash_json_and_result_fields_are_non_null",
]

EXPECTED_CANONICAL_RESPONSE = {
    "authoritative_storage": "response_body_canonical_bytes",
    "jsonb_is_delivery_authority": False,
    "fields_in_order": [
        "appointment_id",
        "status",
        "status_reason_code",
        "waiting_area_id",
        "warning_codes",
    ],
    "encoding": "UTF-8",
    "byte_order_mark": False,
    "insignificant_whitespace": False,
    "string_escaping": "RFC8259",
    "nullable_encoding": "json_null",
    "warning_order": "already_validated_canonical_order",
    "extra_fields": False,
    "digest": "lowercase_hex_sha256_of_exact_stored_bytes",
    "digest_compare": "constant_time_before_replay",
    "initial_delivery": "exact_receipt_byte_buffer_without_reserialization",
    "replay_delivery": "exact_stored_bytes_without_reserialization",
    "integrity_failure": "release_no_body_and_fail_closed",
}

EXPECTED_LOCKS = [
    {"resource": "practice", "strength": "FOR SHARE", "predicate": "practice_id"},
    {
        "resource": "appointment",
        "strength": "FOR UPDATE",
        "predicate": "practice_id_and_appointment_id",
    },
    {
        "resource": "idempotency_record",
        "strength": "FOR UPDATE",
        "predicate": "practice_actor_operation_and_hashed_key",
    },
]

EXPECTED_TRACE = [
    "pretransaction_reject_invalid_or_non_status_ingress",
    "lock_practice_or_stop",
    "lock_practice_scoped_appointment_or_stop_before_idempotency_access",
    "check_current_authority_before_idempotency_insert",
    "lock_existing_idempotency_or_insert_target_bound_in_progress_row",
    "recheck_current_authority_while_all_locks_held",
    "classify_exact_operation_route_target_actor_role_request_and_session_bindings",
    "replay_only_complete_integrity_valid_v1_receipt",
    "for_new_command_recheck_locked_version_warnings_evidence_and_terminal_policy",
    "stage_appointment_mutation_audit_and_completed_v1_receipt",
    "require_post_version_equals_pre_version_plus_one",
    "commit_atomic_write_set",
    "deliver_exact_receipt_bytes",
]

EXPECTED_FORBIDDEN_KEYS = {
    "protected_path_content_or_metadata_used",
    "application_model_migration_service_or_route_edited",
    "application_or_database_module_imported",
    "executable_ddl_or_sql_emitted",
    "route_or_database_executed",
    "real_transaction_or_lock_opened",
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
    if contract["source_head"] != "fad85e038b7168c3323075024dba7f9d5709eff5":
        raise ValueError("source head changed")
    if contract["implementation_authorized"] is not False:
        raise ValueError("implementation authority opened")
    if contract["api_boundary"] != EXPECTED_API_BOUNDARY:
        raise ValueError("API boundary changed")
    if contract["appointment_state_version"] != EXPECTED_STATE_VERSION:
        raise ValueError("state-version contract changed")
    if contract["migration_contract"] != EXPECTED_MIGRATION:
        raise ValueError("migration contract changed")

    receipt = contract["private_completed_receipt"]
    if receipt["table"] != "appointment_command_idempotency":
        raise ValueError("receipt table changed")
    if receipt["contract_version_column"] != "completed_receipt_version":
        raise ValueError("receipt version column changed")
    if receipt["contract_version"] != 1:
        raise ValueError("receipt version changed")
    if receipt["additive_fields"] != EXPECTED_ADDITIVE_FIELDS:
        raise ValueError("additive receipt fields changed")
    if receipt["legacy_backfill"] != "none":
        raise ValueError("legacy receipt backfill opened")
    if receipt["legacy_replay_outcome"] != "legacy_receipt_not_replayable":
        raise ValueError("legacy receipt outcome changed")
    expected_session = {
        "algorithm": "HMAC-SHA-256",
        "stored_form": "32_raw_digest_bytes",
        "domain_separator": "appointment-status-session:v1",
        "message_fields": [
            "practice_id",
            "actor_user_id",
            "authenticated_session_id",
        ],
        "raw_session_stored": False,
        "secret_stored": False,
    }
    if receipt["session_binding"] != expected_session:
        raise ValueError("session binding changed")
    if receipt["completed_v1_required_existing_fields"] != EXPECTED_EXISTING_RECEIPT_FIELDS:
        raise ValueError("existing receipt correlation changed")
    if receipt["completed_v1_constraints"] != EXPECTED_RECEIPT_CONSTRAINTS:
        raise ValueError("completed receipt constraints changed")

    if contract["canonical_response"] != EXPECTED_CANONICAL_RESPONSE:
        raise ValueError("canonical response contract changed")

    transaction = contract["transaction_contract"]
    if transaction["owner"] != "backend_status_confirm_kernel":
        raise ValueError("transaction owner changed")
    if transaction["isolation"] != "READ COMMITTED":
        raise ValueError("transaction isolation changed")
    if transaction["single_transaction"] is not True:
        raise ValueError("single transaction weakened")
    if transaction["locks"] != EXPECTED_LOCKS:
        raise ValueError("ordered lock contract changed")
    expected_wait = {
        "policy": "positive_bounded_blocking",
        "nowait": False,
        "skip_locked": False,
        "same_budget_for_all_locks": True,
        "hidden_effect_retry": False,
    }
    if transaction["lock_wait"] != expected_wait:
        raise ValueError("lock wait contract changed")
    if transaction["decision_trace"] != EXPECTED_TRACE:
        raise ValueError("decision trace changed")
    if transaction["idempotency_identity"] != [
        "practice_id",
        "actor_user_id",
        "operation_id",
        "idempotency_key_hash",
    ]:
        raise ValueError("idempotency identity changed")
    if transaction["same_digest_replay_requires"] != [
        "target_match",
        "actor_role_match",
        "request_digest_match",
        "session_binding_digest_match",
        "completed_receipt_version_one",
        "stored_byte_digest_valid",
        "current_authority",
    ]:
        raise ValueError("replay binding changed")
    if transaction["non_disclosing_outcomes"] != [
        "target_not_found",
        "authority_revoked",
        "idempotency_conflict",
        "legacy_receipt_not_replayable",
        "in_progress_not_replayable",
        "receipt_integrity_failure",
        "transaction_rolled_back",
    ]:
        raise ValueError("non-disclosure outcomes changed")

    if contract["failure_policy"] != {
        "lock_timeout": "rollback_generic_transient_no_receipt_disclosure",
        "deadlock": "rollback_generic_transient_no_receipt_disclosure",
        "serialization_failure": "rollback_generic_transient_no_receipt_disclosure",
        "connection_loss_before_commit": "outcome_unknown_client_retries_same_key",
        "connection_loss_after_commit": "delivery_unknown_client_retries_same_key",
        "server_effect_retry": False,
        "atomic_write_set": [
            "appointment_mutation",
            "attributable_audit",
            "completed_v1_receipt",
        ],
    }:
        raise ValueError("failure policy changed")
    if set(contract["forbidden"]) != EXPECTED_FORBIDDEN_KEYS:
        raise ValueError("forbidden surface set changed")
    if set(contract["forbidden"].values()) != {False}:
        raise ValueError("forbidden surface opened")
    if contract["next_candidate"] != (
        "provider_free_unmounted_status_confirm_physical_schema_and_"
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
        ("public_schema", _set(("api_boundary", "public_response_schema_changed"), True)),
        ("graphql_write", _set(("api_boundary", "graphql_mutation_authority"), True)),
        ("event_command", _set(("api_boundary", "event_command_authority"), True)),
        ("timestamp_version", _set(("appointment_state_version", "timestamp_substitution"), True)),
        ("integer_type", _set(("appointment_state_version", "postgresql_type"), "INTEGER")),
        ("zero_version", _set(("appointment_state_version", "minimum"), 0)),
        ("client_increment", _set(("appointment_state_version", "increment_owner"), "application")),
        ("no_trigger_override", _set(("appointment_state_version", "submitted_value_policy"), "accept")),
        ("trigger_event", _set(("appointment_state_version", "trigger_is_watcher_or_event"), True)),
        ("runtime_early", _set(("migration_contract", "runtime_before_completion"), True)),
        ("fake_history", _set(("migration_contract", "historical_backfill_claim"), "historical_versions")),
        ("unsafe_downgrade", _set(("migration_contract", "automatic_downgrade_after_first_v1_receipt"), True)),
        ("legacy_backfill", _set(("private_completed_receipt", "legacy_backfill"), "infer")),
        ("legacy_replay", _set(("private_completed_receipt", "legacy_replay_outcome"), "replay")),
        ("raw_session", _set(("private_completed_receipt", "session_binding", "raw_session_stored"), True)),
        ("stored_secret", _set(("private_completed_receipt", "session_binding", "secret_stored"), True)),
        ("weak_session_hash", _set(("private_completed_receipt", "session_binding", "algorithm"), "SHA-1")),
        ("jsonb_delivery", _set(("canonical_response", "jsonb_is_delivery_authority"), True)),
        ("bom", _set(("canonical_response", "byte_order_mark"), True)),
        ("whitespace", _set(("canonical_response", "insignificant_whitespace"), True)),
        ("extra_public_field", _set(("canonical_response", "extra_fields"), True)),
        ("non_constant_compare", _set(("canonical_response", "digest_compare"), "ordinary_equality")),
        ("reserialize_initial", _set(("canonical_response", "initial_delivery"), "reserialize_jsonb")),
        ("reserialize_replay", _set(("canonical_response", "replay_delivery"), "reserialize_jsonb")),
        ("integrity_release", _set(("canonical_response", "integrity_failure"), "release_anyway")),
        ("isolation", _set(("transaction_contract", "isolation"), "READ UNCOMMITTED")),
        ("multi_transaction", _set(("transaction_contract", "single_transaction"), False)),
        ("nowait", _set(("transaction_contract", "lock_wait", "nowait"), True)),
        ("skip_locked", _set(("transaction_contract", "lock_wait", "skip_locked"), True)),
        ("unbounded_wait", _set(("transaction_contract", "lock_wait", "policy"), "unbounded")),
        ("hidden_retry", _set(("transaction_contract", "lock_wait", "hidden_effect_retry"), True)),
        ("server_retry", _set(("failure_policy", "server_effect_retry"), True)),
        ("next_runtime", _set(("next_candidate",), "mounted_runtime")),
    ]
    for index in range(11):
        mutations.append(
            (f"source_hash_{index}", _set(("source_bindings", index, "sha256"), "0" * 64))
        )
    for index in range(7):
        mutations.append(
            (f"migration_phase_{index}", _set(("migration_contract", "phases", index), "weakened"))
        )
    for index in range(5):
        mutations.append(
            (
                f"receipt_field_{index}",
                _set(("private_completed_receipt", "additive_fields", index, "name"), "weakened"),
            )
        )
    for index in range(5):
        mutations.append(
            (f"public_field_{index}", _set(("canonical_response", "fields_in_order", index), "private_field"))
        )
    for index in range(3):
        mutations.extend(
            [
                (f"lock_resource_{index}", _set(("transaction_contract", "locks", index, "resource"), "weakened")),
                (f"lock_strength_{index}", _set(("transaction_contract", "locks", index, "strength"), "FOR KEY SHARE")),
            ]
        )
    for index in (2, 3, 5, 6, 7, 10, 11, 12):
        mutations.append(
            (f"decision_trace_{index}", _set(("transaction_contract", "decision_trace", index), "reordered"))
        )
    for key in sorted(EXPECTED_FORBIDDEN_KEYS):
        mutations.append((f"forbidden_{key}", _set(("forbidden", key), True)))
    return mutations


def reject_hostile_mutations(
    contract: dict[str, Any], schema: dict[str, Any]
) -> dict[str, int]:
    mutations = hostile_mutations()
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
    if rejected < 50:
        raise ValueError("fewer than 50 hostile mutations were rejected")
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
        "schema_version": "raisa.status_confirm_physical_design_architecture_evidence.v1",
        "result": contract["result"],
        "source_head": contract["source_head"],
        "evidence_label": contract["evidence_label"],
        "implementation_authorized": contract["implementation_authorized"],
        "source_hashes": source_hashes,
        "contract_fingerprint": f"sha256:{fingerprint}",
        "architecture_facts": {
            "appointment_state_version": "postgresql_bigint_trigger_owned",
            "migration_phase_count": len(contract["migration_contract"]["phases"]),
            "receipt_additive_field_count": len(
                contract["private_completed_receipt"]["additive_fields"]
            ),
            "legacy_receipts_replayable": False,
            "session_binding_storage": "32_raw_hmac_sha256_bytes",
            "response_delivery_authority": "stored_canonical_bytes",
            "lock_order": [
                item["resource"] for item in contract["transaction_contract"]["locks"]
            ],
            "authority_check_count": sum(
                "authority" in item
                for item in contract["transaction_contract"]["decision_trace"]
            ),
            "public_response_schema_changed": False,
        },
        "hostile_mutations": hostile,
        "forbidden": contract["forbidden"],
        "next_candidate": contract["next_candidate"],
    }


def main() -> int:
    evidence = build_evidence()
    EVIDENCE_PATH.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
