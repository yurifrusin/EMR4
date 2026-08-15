"""Validate the provider-free unmounted delete-confirm physical scaffold.

The validator reads exact bound artifacts plus the open maintained Alembic
source inventory needed to prove the closed-world generation-writer boundary.
It imports no application, migration, database-driver or provider module and
executes no SQL.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/"
    "scaffold-contract.json"
)
SCHEMA_PATH = CONTRACT_PATH.with_name("scaffold-contract.schema.json")
EXPECTED_CONTRACT_SHA256 = (
    "bc7c83800d9280656d295d85ed2b72d28edd0f11baa1a41a86587d784fe2e4b7"
)
HOSTILE_MUTATION_TARGET = 90


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _contract_errors(candidate: Any, schema: dict[str, Any]) -> list[str]:
    errors = [
        error.message for error in Draft202012Validator(schema).iter_errors(candidate)
    ]
    if _canonical_digest(candidate) != EXPECTED_CONTRACT_SHA256:
        errors.append("contract_digest_mismatch")
    return errors


def _mutated_leaf(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return f"{value}-hostile"
    if value is None:
        return "hostile-non-null"
    raise TypeError(f"unsupported contract leaf: {type(value).__name__}")


def _mutate_at(candidate: Any, path: tuple[Any, ...]) -> None:
    parent = candidate
    for component in path[:-1]:
        parent = parent[component]
    final = path[-1]
    parent[final] = _mutated_leaf(parent[final])


CONTRACT_SEMANTIC_REQUIREMENTS: tuple[tuple[str, tuple[str, ...], Any], ...] = (
    (
        "result",
        ("result",),
        "raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold_pass",
    ),
    ("implementation_unmounted", ("implementation_status",), "unmounted_scaffold_only"),
    ("authority_not_nullable", ("mapping", "authority_fence", "nullable"), False),
    ("authority_minimum", ("mapping", "authority_fence", "minimum"), 1),
    (
        "authority_maximum",
        ("mapping", "authority_fence", "maximum"),
        9223372036854775807,
    ),
    (
        "generation_owner",
        ("mapping", "authority_fence", "generation_owner"),
        "postgresql",
    ),
    (
        "insert_forces_one",
        ("mapping", "authority_fence", "insert_policy"),
        "force_generation_one",
    ),
    (
        "submitted_generation_ignored",
        ("mapping", "authority_fence", "submitted_generation_policy"),
        "ignored_by_database",
    ),
    (
        "nested_grant_admitted",
        ("mapping", "authority_fence", "nested_grant_advance_admitted"),
        True,
    ),
    (
        "nested_depth_signal",
        ("mapping", "authority_fence", "nested_advance_signal"),
        "postgresql_pg_trigger_depth_equals_two",
    ),
    (
        "sole_nested_writer",
        (
            "mapping",
            "authority_fence",
            "closed_world_nested_writer_proof",
            "sole_nested_writer_function",
        ),
        "public.emr4_user_capability_grant_generation_guard",
    ),
    (
        "runtime_ddl_closed",
        (
            "mapping",
            "authority_fence",
            "closed_world_nested_writer_proof",
            "runtime_ddl_trigger_function_mutation_authorized",
        ),
        False,
    ),
    (
        "public_object_identity",
        (
            "mapping",
            "authority_fence",
            "closed_world_nested_writer_proof",
            "public_schema_object_identity_required",
        ),
        True,
    ),
    (
        "later_writer_denied",
        (
            "mapping",
            "authority_fence",
            "closed_world_nested_writer_proof",
            "later_writer_regression_denied",
        ),
        True,
    ),
    (
        "synthetic_auth_ineligible",
        (
            "mapping",
            "authority_fence",
            "synthetic_application_auth_relations_ineligible",
        ),
        True,
    ),
    (
        "grant_presence_semantics",
        ("mapping", "user_capability_grants", "grant_semantics"),
        "row_presence_is_grant_absence_is_denial",
    ),
    (
        "grant_wildcard_denied",
        ("mapping", "user_capability_grants", "wildcard_representable"),
        False,
    ),
    (
        "grant_json_denied",
        ("mapping", "user_capability_grants", "json_claim_capable"),
        False,
    ),
    (
        "grant_role_claim_denied",
        ("mapping", "user_capability_grants", "client_role_claim_capable"),
        False,
    ),
    (
        "grant_update_rejected",
        ("mapping", "user_capability_grants", "update_rejected"),
        True,
    ),
    (
        "duplicate_insert_no_advance",
        ("mapping", "user_capability_grants", "duplicate_insert_advances_generation"),
        False,
    ),
    (
        "no_automatic_grants",
        ("mapping", "user_capability_grants", "automatic_grant_to_existing_users"),
        False,
    ),
    (
        "empty_grant_cutover",
        ("mapping", "user_capability_grants", "capability_rows_after_migration"),
        0,
    ),
    (
        "receipt_generation_required",
        (
            "mapping",
            "family_qualified_v1_constraint",
            "delete_confirm_requires_positive_authority_generation",
        ),
        True,
    ),
    (
        "third_receipt_family_denied",
        (
            "mapping",
            "family_qualified_v1_constraint",
            "third_family_may_set_version_one",
        ),
        False,
    ),
    ("migration_unexecuted", ("migration", "executed"), False),
    ("database_uncontacted", ("migration", "database_contacted"), False),
    (
        "user_direct_generation_ignored",
        ("migration", "user_trigger", "direct_submitted_generation"),
        "ignored",
    ),
    (
        "user_nested_depth_exact",
        ("migration", "user_trigger", "nested_grant_advance"),
        "admitted_only_at_trigger_depth_two_and_old_plus_one",
    ),
    ("user_overflow_aborts", ("migration", "user_trigger", "overflow_aborts"), True),
    (
        "user_trigger_not_watcher",
        ("migration", "user_trigger", "event_or_watcher"),
        False,
    ),
    (
        "grant_parent_lock",
        ("migration", "capability_trigger", "parent_lock"),
        "users_for_update",
    ),
    (
        "grant_parent_advance",
        ("migration", "capability_trigger", "parent_advance"),
        "nested_update_old_plus_one",
    ),
    (
        "grant_duplicate_noop",
        ("migration", "capability_trigger", "duplicate_insert_policy"),
        "locked_exact_row_exists_returns_without_generation_advance",
    ),
    (
        "grant_missing_parent_aborts",
        ("migration", "capability_trigger", "missing_parent_aborts"),
        True,
    ),
    (
        "grant_update_trigger",
        ("migration", "capability_trigger", "update_rejected_trigger"),
        True,
    ),
    (
        "downgrade_grant_guard",
        ("migration", "downgrade", "fails_closed_when_grant_exists"),
        True,
    ),
    (
        "downgrade_receipt_guard",
        ("migration", "downgrade", "fails_closed_when_delete_receipt_v1_exists"),
        True,
    ),
    (
        "downgrade_audit_guard",
        ("migration", "downgrade", "fails_closed_when_delete_audit_v1_exists"),
        True,
    ),
    (
        "downgrade_forward_only",
        ("migration", "downgrade", "post_adoption_recovery"),
        "forward_only",
    ),
    ("session_hmac", ("helpers", "session_binding", "algorithm"), "HMAC-SHA-256"),
    (
        "raw_session_not_stored",
        ("helpers", "session_binding", "raw_session_stored"),
        False,
    ),
    ("secret_not_stored", ("helpers", "session_binding", "secret_stored"), False),
    (
        "response_digest",
        ("helpers", "response_integrity", "digest"),
        "lowercase_hex_sha256",
    ),
    (
        "response_constant_time",
        ("helpers", "response_integrity", "comparison"),
        "constant_time",
    ),
    (
        "json_not_delivery_authority",
        ("helpers", "response_integrity", "jsonb_is_delivery_authority"),
        False,
    ),
    ("transaction_unmounted", ("transaction_seam", "mounted"), False),
    ("transaction_not_called", ("transaction_seam", "called_by_route"), False),
    ("transaction_isolation", ("transaction_seam", "isolation"), "READ COMMITTED"),
    ("transaction_count", ("transaction_seam", "transaction_count"), 1),
    ("cumulative_budget", ("transaction_seam", "cumulative_lock_wait_budget_ms"), 2000),
    ("no_nowait", ("transaction_seam", "nowait"), False),
    ("no_skip_locked", ("transaction_seam", "skip_locked"), False),
    ("no_hidden_retry", ("transaction_seam", "hidden_effect_retry"), False),
    ("no_advisory_lock", ("transaction_seam", "advisory_locks"), False),
    (
        "select_before_insert",
        ("transaction_seam", "select_first_then_insert_if_absent"),
        True,
    ),
    ("two_authority_checks", ("transaction_seam", "authority_check_count"), 2),
    (
        "internal_authority_owner",
        ("transaction_seam", "authority_check_owner"),
        "internal_not_caller_callback",
    ),
    (
        "classification_after_authority",
        ("transaction_seam", "classification_after_second_authority_check"),
        True,
    ),
    (
        "claim_generation_bound",
        ("transaction_seam", "new_claim_binds_exact_signed_authority_generation"),
        True,
    ),
    (
        "actor_uuid_canonical",
        ("transaction_seam", "actor_identity_canonicalized_to_uuid"),
        True,
    ),
    (
        "lock_timeout_safe",
        ("transaction_seam", "lock_timeout_parameterization"),
        "select_set_config_transaction_local",
    ),
    (
        "replay_complete_only",
        (
            "transaction_seam",
            "replay_requires_complete_integrity_valid_family_qualified_v1",
        ),
        True,
    ),
    ("legacy_not_replayed", ("transaction_seam", "legacy_replay"), False),
    ("in_progress_not_replayed", ("transaction_seam", "in_progress_replay"), False),
    (
        "product_mutation_not_staged",
        ("transaction_seam", "product_mutation_staged"),
        False,
    ),
    ("audit_not_staged", ("transaction_seam", "audit_staged"), False),
    ("receipt_not_completed", ("transaction_seam", "receipt_completion_staged"), False),
    (
        "future_write_set_required",
        ("transaction_seam", "future_atomic_write_set_required_before_commit"),
        True,
    ),
    (
        "authority_lock_strength",
        ("authority_check", "fence_lock_strength"),
        "FOR SHARE",
    ),
    ("authority_checks_twice", ("authority_check", "check_count"), 2),
    ("authority_internal_only", ("authority_check", "internal_only"), True),
    ("public_openapi_unchanged", ("api_boundary", "public_openapi_changed"), False),
    ("graphql_read_only", ("api_boundary", "graphql_read_only"), True),
    (
        "events_are_hints",
        ("api_boundary", "events_non_authoritative_acceleration_hints"),
        True,
    ),
    (
        "no_public_private_fields",
        ("api_boundary", "private_fields_publicly_mapped"),
        False,
    ),
    (
        "no_public_response_edit",
        ("api_boundary", "public_response_schema_edit_authorized"),
        False,
    ),
    ("no_route", ("forbidden", "route_edited_mounted_or_called"), False),
    ("no_migration_execution", ("forbidden", "migration_or_database_executed"), False),
    ("no_real_lock", ("forbidden", "real_lock_acquired"), False),
    ("no_provider", ("forbidden", "provider_adc_or_credentials_used"), False),
    ("no_product_data", ("forbidden", "product_or_patient_data_used"), False),
    ("no_watcher_authority", ("forbidden", "watcher_or_event_authority_added"), False),
    ("no_product_command", ("forbidden", "product_command_executed"), False),
    ("no_release", ("forbidden", "deployment_release_or_pages_opened"), False),
    (
        "next_parse_catalogue",
        ("next_candidate",),
        "provider_free_disposable_postgresql_delete_confirm_scaffold_parse_catalogue_rehearsal",
    ),
)


def _value_at(candidate: Any, path: tuple[str, ...]) -> Any:
    value = candidate
    for component in path:
        value = value[component]
    return value


def _contract_semantic_errors(candidate: Any) -> list[str]:
    errors: list[str] = []
    for label, path, expected in CONTRACT_SEMANTIC_REQUIREMENTS:
        try:
            observed = _value_at(candidate, path)
        except (KeyError, TypeError):
            errors.append(f"contract_semantic_missing:{label}")
            continue
        if type(observed) is not type(expected) or observed != expected:
            errors.append(f"contract_semantic_mismatch:{label}")
    return errors


def _verify_source_bindings(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for group in ("input_bindings", "implementation_bindings"):
        for binding in contract[group]:
            path = ROOT / binding["path"]
            if not path.is_file():
                errors.append(f"missing:{binding['path']}")
            elif _sha256(path) != binding["sha256"]:
                errors.append(f"hash_mismatch:{binding['path']}")
    return errors


STATIC_SOURCE_PATHS = {
    "tenancy": "app/models/tenancy.py",
    "appointments": "app/models/appointments.py",
    "migration": "alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py",
    "service": "app/services/appointment_delete_physical.py",
}

SOURCE_MUTATION_TARGETS: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "tenancy_authority_type",
        "tenancy",
        "authority_generation = Column(BigInteger, nullable=False",
        "authority_generation = Column(BigInteger, nullable=True",
        "tenancy_token_missing:",
    ),
    (
        "tenancy_grant_class",
        "tenancy",
        "class UserCapabilityGrant(Base):",
        "class UserCapabilityClaim(Base):",
        "tenancy_token_missing:",
    ),
    (
        "tenancy_grant_primary_key",
        "tenancy",
        "pk_user_capability_grants",
        "pk_user_capability_claims",
        "tenancy_token_missing:",
    ),
    (
        "tenancy_grant_foreign_key",
        "tenancy",
        "fk_user_capability_grants_user",
        "fk_user_capability_claims_user",
        "tenancy_token_missing:",
    ),
    (
        "tenancy_closed_capability",
        "tenancy",
        "capability_code IN ('appointment.cancel.confirm', 'appointment.read')",
        "capability_code IN ('appointment.cancel.request', 'appointment.read')",
        "tenancy_token_missing:",
    ),
    (
        "receipt_authority_generation",
        "appointments",
        "authority_generation = Column(BigInteger, nullable=True)",
        "authority_generation = Column(String, nullable=True)",
        "appointments_token_missing:",
    ),
    (
        "audit_contract_version",
        "appointments",
        "audit_contract_version = Column(SmallInteger, nullable=True)",
        "audit_contract_version = Column(BigInteger, nullable=True)",
        "appointments_token_missing:",
    ),
    (
        "receipt_family_constraint",
        "appointments",
        "ck_appt_cmd_idem_status_receipt_v1_complete",
        "ck_appt_cmd_idem_open_receipt_v1_complete",
        "appointments_token_missing:",
    ),
    (
        "delete_audit_constraint",
        "appointments",
        "ck_appt_audit_log_delete_v1_complete",
        "ck_appt_audit_log_delete_v1_optional",
        "appointments_token_missing:",
    ),
    (
        "delete_operation_identity",
        "appointments",
        "confirmAppointmentDeleteProposal",
        "deleteAppointmentDirectly",
        "appointments_token_missing:",
    ),
    (
        "migration_revision",
        "migration",
        'revision: str = "x3y4z5a6b7c8"',
        'revision: str = "hostile"',
        "migration_marker_missing:",
    ),
    (
        "migration_parent",
        "migration",
        'down_revision: Union[str, Sequence[str], None] = "w2x3y4z5a6b7"',
        'down_revision: Union[str, Sequence[str], None] = "hostile"',
        "migration_marker_missing:",
    ),
    (
        "migration_backfill_baseline",
        "migration",
        "UPDATE public.users SET authority_generation = 1",
        "UPDATE public.users SET authority_generation = 2",
        "migration_marker_missing:",
    ),
    (
        "migration_user_guard_identity",
        "migration",
        "public.emr4_user_authority_generation_guard",
        "public.emr4_user_authority_generation_open",
        "migration_marker_missing:",
    ),
    (
        "migration_capability_guard_identity",
        "migration",
        "public.emr4_user_capability_grant_generation_guard",
        "public.emr4_user_capability_grant_generation_open",
        "migration_marker_missing:",
    ),
    (
        "migration_capability_trigger_identity",
        "migration",
        "trg_user_capability_grants_generation",
        "trg_user_capability_grants_open",
        "migration_marker_missing:",
    ),
    (
        "migration_trigger_depth",
        "migration",
        "pg_trigger_depth() = 2",
        "pg_trigger_depth() = 3",
        "migration_invariant_missing:",
    ),
    (
        "migration_nested_exact_advance",
        "migration",
        "v_submitted = OLD.authority_generation + 1",
        "v_submitted > OLD.authority_generation",
        "migration_invariant_missing:",
    ),
    (
        "migration_duplicate_exact_row",
        "migration",
        "FROM public.user_capability_grants",
        "FROM public.hostile_user_capability_grants",
        "migration_invariant_missing:",
    ),
    (
        "migration_nested_user_writer",
        "migration",
        "UPDATE public.users",
        "UPDATE public.hostile_users",
        "migration_invariant_missing:",
    ),
    (
        "migration_downgrade_grant_guard",
        "migration",
        "user capability grant exists; forward recovery required",
        "user capability grant ignored during downgrade",
        "migration_invariant_missing:",
    ),
    (
        "migration_capability_function_interpolation",
        "migration",
        'f"""\n        CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()',
        '"""\n        CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()',
        "migration_invariant_missing:",
    ),
    (
        "transaction_scope",
        "service",
        "with db.begin():",
        "with db.begin_nested():",
        "transaction_order_missing:",
    ),
    (
        "transaction_isolation",
        "service",
        "SET TRANSACTION ISOLATION LEVEL READ COMMITTED",
        "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ",
        "transaction_order_missing:",
    ),
    (
        "transaction_lock_timeout",
        "service",
        'select(func.set_config("lock_timeout"',
        'select(func.set_config("statement_timeout"',
        "transaction_order_missing:",
    ),
    (
        "transaction_user_lock",
        "service",
        "db.query(User)",
        "db.query(UserCapabilityGrant)",
        "transaction_order_missing:",
    ),
    (
        "transaction_appointment_lock",
        "service",
        "db.query(Appointment)",
        "db.query(AppointmentAuditLog)",
        "transaction_order_missing:",
    ),
    (
        "transaction_receipt_lock",
        "service",
        "db.query(AppointmentCommandIdempotency)",
        "db.query(HostileIdempotency)",
        "transaction_order_missing:",
    ),
    (
        "transaction_authority_checks",
        "service",
        "if not _authority_valid(",
        "if not _authority_valid_hostile(",
        "transaction_order_missing:",
    ),
    (
        "transaction_cross_artifact_actor",
        "service",
        "audit.confirmed_by_user_id == actor_user_id",
        "audit.confirmed_by_user_id != actor_user_id",
        "cross_artifact_guard_missing:",
    ),
)


def _read_static_sources() -> dict[str, str]:
    return {
        label: (ROOT / relative_path).read_text(encoding="utf-8")
        for label, relative_path in STATIC_SOURCE_PATHS.items()
    }


def _verify_closed_world_authority_writers(migration_source: str) -> list[str]:
    errors: list[str] = []
    writer_paths: list[str] = []
    for path in sorted((ROOT / "alembic/versions").glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if "authority_generation" in source:
            writer_paths.append(path.relative_to(ROOT).as_posix())
    if writer_paths != [STATIC_SOURCE_PATHS["migration"]]:
        errors.append(
            "closed_world_authority_writer_inventory_mismatch:" + ",".join(writer_paths)
        )
    for token in (
        "CREATE FUNCTION public.emr4_user_authority_generation_guard()",
        "CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()",
        "BEFORE INSERT OR UPDATE ON public.users",
        "BEFORE INSERT OR DELETE ON public.user_capability_grants",
        "EXECUTE FUNCTION public.emr4_user_authority_generation_guard()",
        "EXECUTE FUNCTION public.emr4_user_capability_grant_generation_guard()",
        "pg_trigger_depth() = 2",
        'f"""\n        CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()',
    ):
        if token not in migration_source:
            errors.append(f"closed_world_identity_missing:{token}")
    grant_function_start = migration_source.find(
        "CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()"
    )
    grant_function_end = migration_source.find(
        "CREATE TRIGGER trg_user_capability_grants_generation",
        grant_function_start,
    )
    grant_function_source = migration_source[grant_function_start:grant_function_end]
    if grant_function_source.count("UPDATE public.users") != 2:
        errors.append("closed_world_nested_user_writer_count_invalid")
    if migration_source.count("pg_trigger_depth() = 2") != 1:
        errors.append("closed_world_trigger_depth_guard_count_invalid")
    return errors


def _verify_static_lowering(
    sources: dict[str, str] | None = None,
    *,
    check_closed_world_inventory: bool = True,
) -> list[str]:
    errors: list[str] = []
    source_map = _read_static_sources() if sources is None else sources
    tenancy_source = source_map["tenancy"]
    appointments_source = source_map["appointments"]
    migration_source = source_map["migration"]
    service_source = source_map["service"]

    for token in (
        "authority_generation = Column(BigInteger, nullable=False",
        "ck_users_authority_generation_positive",
        "uq_users_practice_id_id",
        "class UserCapabilityGrant(Base):",
        "pk_user_capability_grants",
        "fk_user_capability_grants_user",
        "capability_code IN ('appointment.cancel.confirm', 'appointment.read')",
    ):
        if token not in tenancy_source:
            errors.append(f"tenancy_token_missing:{token}")

    for token in (
        "authority_generation = Column(BigInteger, nullable=True)",
        "audit_contract_version = Column(SmallInteger, nullable=True)",
        "pre_state_version = Column(BigInteger, nullable=True)",
        "post_state_version = Column(BigInteger, nullable=True)",
        "waiting_area_before_id = Column(UUID(as_uuid=True), nullable=True)",
        "waiting_area_after_id = Column(UUID(as_uuid=True), nullable=True)",
        "audit_evidence_codes = Column(JSONB, nullable=True)",
        "ck_appt_cmd_idem_status_receipt_v1_complete",
        "ck_appt_audit_log_delete_v1_complete",
        "confirmAppointmentDeleteProposal",
    ):
        if token not in appointments_source:
            errors.append(f"appointments_token_missing:{token}")

    migration_markers = (
        'revision: str = "x3y4z5a6b7c8"',
        'down_revision: Union[str, Sequence[str], None] = "w2x3y4z5a6b7"',
        'sa.Column("authority_generation", sa.BigInteger(), nullable=True)',
        'server_default=sa.text("1")',
        "UPDATE public.users SET authority_generation = 1",
        "CHECK (authority_generation >= 1) NOT VALID",
        'op.alter_column("users", "authority_generation", nullable=False)',
        "ALTER TABLE public.users ADD CONSTRAINT uq_users_practice_id_id",
        "op.create_table(",
        "CREATE FUNCTION public.emr4_user_authority_generation_guard()",
        "CREATE TRIGGER trg_users_authority_generation_guard",
        "CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()",
        "CREATE TRIGGER trg_user_capability_grants_generation",
        "CREATE FUNCTION public.emr4_reject_user_capability_grant_update()",
        "CREATE TRIGGER trg_user_capability_grants_reject_update",
        "invalid authority_generation after cutover",
    )
    positions: list[int] = []
    for marker in migration_markers:
        try:
            positions.append(migration_source.index(marker))
        except ValueError:
            errors.append(f"migration_marker_missing:{marker}")
    if positions and positions != sorted(positions):
        errors.append("migration_phase_order_invalid")
    for token in (
        "BEFORE INSERT OR UPDATE ON public.users",
        "BEFORE INSERT OR DELETE ON public.user_capability_grants",
        "BEFORE UPDATE ON public.user_capability_grants",
        "v_submitted := NEW.authority_generation",
        "NEW.authority_generation := OLD.authority_generation",
        "NEW.authority_generation := 1",
        "pg_trigger_depth() = 2",
        "v_submitted = OLD.authority_generation + 1",
        "authority_generation overflow",
        "authority_generation = users.authority_generation + 1",
        "user capability grant update is rejected",
        "user capability grant parent user missing",
        "FROM public.user_capability_grants",
        "UPDATE public.users",
        "user capability grant exists; forward recovery required",
        "delete-confirm receipt v1 exists; forward recovery required",
        "delete audit v1 exists; forward recovery required",
        'f"""\n        CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()',
    ):
        if token not in migration_source:
            errors.append(f"migration_invariant_missing:{token}")
    for forbidden in ("pg_notify", "diary_committed"):
        if forbidden in migration_source.lower():
            errors.append(f"migration_forbidden_token:{forbidden}")

    tree = ast.parse(service_source)
    transaction = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "delete_confirm_locked_transaction"
        ),
        None,
    )
    if transaction is None:
        errors.append("transaction_seam_missing")
    else:
        transaction_source = ast.get_source_segment(service_source, transaction) or ""
        ordered = (
            "with db.begin():",
            "SET TRANSACTION ISOLATION LEVEL READ COMMITTED",
            'select(func.set_config("lock_timeout"',
            "db.query(User)",
            ".with_for_update(read=True)",
            "db.query(Appointment)",
            ".with_for_update()",
            "if not _authority_valid(",
            "db.query(AppointmentCommandIdempotency)",
            ".with_for_update()",
            "postgresql_insert(AppointmentCommandIdempotency)",
            "db.query(AppointmentCommandIdempotency)",
            ".with_for_update()",
            "if not _authority_valid(",
            "if inserted:",
        )
        cursor = -1
        for marker in ordered:
            try:
                cursor = transaction_source.index(marker, cursor + 1)
            except ValueError:
                errors.append(f"transaction_order_missing:{marker}")
        if transaction_source.count("if not _authority_valid(") != 2:
            errors.append("authority_check_count_invalid")
        if (
            transaction_source.count("\n        _apply_lock_budget()")
            + transaction_source.count("\n            _apply_lock_budget()")
        ) != 7:
            errors.append("lock_budget_application_count_invalid")
        if "DELETE_CONFIRM_LOCK_WAIT_DEADLINE_MS = 2000" not in service_source:
            errors.append("cumulative_deadline_constant_missing")
        if "time.monotonic()" not in transaction_source:
            errors.append("monotonic_deadline_missing")
        for required in (
            "authority_generation=signed_authority_generation",
            "actor_user_id=str(actor_uuid)",
            "record.authority_generation == signed_authority_generation",
            "not isinstance(session_binding_digest, bytes)",
        ):
            if required not in transaction_source and required not in service_source:
                errors.append(f"transaction_binding_guard_missing:{required}")
        for forbidden in (
            "emr4.authority_advance_target",
            "current_setting(",
            "SET LOCAL lock_timeout = :timeout",
            "record.authority_generation is None",
        ):
            if forbidden in migration_source or forbidden in service_source:
                errors.append(f"spoofable_or_weak_binding_present:{forbidden}")
        for forbidden in (
            "nowait",
            "skip_locked",
            "advisory",
            "appointment.status =",
            "current_authority",
            "practice_is_active",
        ):
            if forbidden in transaction_source.lower():
                errors.append(f"transaction_forbidden_token:{forbidden}")
    if "@router" in service_source or "FastAPI" in service_source:
        errors.append("service_route_surface_present")
    if (
        "AppointmentAuditLog(" in service_source
        or 'record.state = "completed"' in service_source
    ):
        errors.append("service_product_write_staged")
    for token in (
        'record.state == "completed"',
        "db.query(AppointmentAuditLog)",
        "def _delete_write_set_complete(",
        "audit.command_id == record.id",
        "audit.practice_id == practice_id",
        "audit.appointment_id == target_appointment_id",
        "audit.confirmed_by_user_id == actor_user_id",
        "audit.authority_generation == signed_authority_generation",
        "audit.pre_state_version == pre_state_version",
        "audit.post_state_version == post_state_version",
        "audit.status_reason_code == appointment.status_reason_code",
        "audit.cancellation_reason == appointment.cancellation_reason",
        "audit.waiting_area_before_id == waiting_area_before_id",
        "audit.waiting_area_after_id is None",
        "appointment.appointment_state_version == post_state_version",
        "appointment.waiting_area_id is None",
        "record.response_body_canonical_bytes == expected_response",
        "record.response_body_json == expected_json",
        "record.idempotency_key_hash == idempotency_key_hash",
        "record.request_body_canonicalization_version == 1",
    ):
        if token not in service_source:
            errors.append(f"cross_artifact_guard_missing:{token}")
    if check_closed_world_inventory:
        errors.extend(_verify_closed_world_authority_writers(migration_source))
    return errors


def validate_hostile_mutations(
    contract: dict[str, Any], schema: dict[str, Any]
) -> tuple[int, int, list[str]]:
    """Exercise declared semantic mutations through the real validators."""
    attempted = 0
    rejected = 0
    admitted: list[str] = []

    for label, path, _expected in CONTRACT_SEMANTIC_REQUIREMENTS:
        attempted += 1
        mutated = copy.deepcopy(contract)
        _mutate_at(mutated, path)
        schema_errors = list(Draft202012Validator(schema).iter_errors(mutated))
        semantic_errors = _contract_semantic_errors(mutated)
        expected_error = f"contract_semantic_mismatch:{label}"
        if expected_error in semantic_errors:
            rejected += 1
        else:
            admitted.append(
                f"contract:{label}:schema_errors={len(schema_errors)}:"
                f"semantic_errors={semantic_errors}"
            )

    sources = _read_static_sources()
    for label, source_id, old, new, expected_prefix in SOURCE_MUTATION_TARGETS:
        attempted += 1
        if old not in sources[source_id]:
            admitted.append(f"source:{label}:baseline_token_missing")
            continue
        mutated_sources = dict(sources)
        mutated_sources[source_id] = sources[source_id].replace(old, new)
        static_errors = _verify_static_lowering(
            mutated_sources,
            check_closed_world_inventory=False,
        )
        if any(error.startswith(expected_prefix) for error in static_errors):
            rejected += 1
        else:
            admitted.append(f"source:{label}:errors={static_errors}")

    return attempted, rejected, admitted


def validate(output_path: Path | None = None) -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = _contract_errors(contract, schema)
    errors.extend(_contract_semantic_errors(contract))
    errors.extend(_verify_source_bindings(contract))
    errors.extend(_verify_static_lowering())
    hostile_attempted, hostile_rejected, hostile_admitted = validate_hostile_mutations(
        contract, schema
    )
    if hostile_attempted < HOSTILE_MUTATION_TARGET:
        errors.append("insufficient_hostile_mutation_surface")
    errors.extend(f"hostile_mutation_admitted:{item}" for item in hostile_admitted)

    evidence = {
        "schema_version": (
            "raisa.delete_confirm_physical_schema_transaction_scaffold.evidence.v1"
        ),
        "result": (
            "raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold_pass"
            if not errors
            else "revision_required"
        ),
        "source_head": contract["source_head"],
        "contract_sha256": _sha256(CONTRACT_PATH),
        "source_bindings_checked": len(contract["input_bindings"])
        + len(contract["implementation_bindings"]),
        "hostile_mutations_attempted": hostile_attempted,
        "hostile_mutations_rejected": hostile_rejected,
        "semantic_mutation_catalogue": True,
        "closed_world_writer_inventory_checked": True,
        "focused_test_file_bound": True,
        "focused_test_execution_reported_by_validator": False,
        "migration_executed": False,
        "database_contacted": False,
        "real_lock_acquired": False,
        "route_mounted_or_called": False,
        "provider_adc_or_credentials_used": False,
        "product_or_patient_data_used": False,
        "errors": errors,
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence = validate(args.output)
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    return 0 if evidence["result"].endswith("_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
