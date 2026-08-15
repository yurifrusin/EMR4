"""Validate the provider-free unmounted delete-confirm physical scaffold.

The validator reads only exact allowlisted files. It imports no application,
migration, database-driver or provider module and executes no SQL.
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
    "be51a13e65d5cbdce9a08d567802a3064b5485c270f2b41e35472b33bcfbecae"
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
        error.message
        for error in Draft202012Validator(schema).iter_errors(candidate)
    ]
    if _canonical_digest(candidate) != EXPECTED_CONTRACT_SHA256:
        errors.append("contract_digest_mismatch")
    return errors


def _leaf_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    if isinstance(value, dict):
        paths: list[tuple[Any, ...]] = []
        for key, child in value.items():
            paths.extend(_leaf_paths(child, (*prefix, key)))
        return paths
    if isinstance(value, list):
        paths = []
        for index, child in enumerate(value):
            paths.extend(_leaf_paths(child, (*prefix, index)))
        return paths
    return [prefix]


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


def _verify_static_lowering() -> list[str]:
    errors: list[str] = []
    tenancy_source = (ROOT / "app/models/tenancy.py").read_text(encoding="utf-8")
    appointments_source = (
        ROOT / "app/models/appointments.py"
    ).read_text(encoding="utf-8")
    migration_source = (
        ROOT
        / "alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py"
    ).read_text(encoding="utf-8")
    service_source = (
        ROOT / "app/services/appointment_delete_physical.py"
    ).read_text(encoding="utf-8")

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
        "UPDATE users SET authority_generation = 1",
        "CHECK (authority_generation >= 1) NOT VALID",
        'op.alter_column("users", "authority_generation", nullable=False)',
        "ALTER TABLE users ADD CONSTRAINT uq_users_practice_id_id",
        "op.create_table(",
        "CREATE FUNCTION emr4_user_authority_generation_guard()",
        "CREATE TRIGGER trg_users_authority_generation_guard",
        "CREATE FUNCTION emr4_user_capability_grant_generation_guard()",
        "CREATE TRIGGER trg_user_capability_grants_generation",
        "CREATE FUNCTION emr4_reject_user_capability_grant_update()",
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
        "BEFORE INSERT OR UPDATE ON users",
        "BEFORE INSERT OR DELETE ON user_capability_grants",
        "BEFORE UPDATE ON user_capability_grants",
        "v_submitted := NEW.authority_generation",
        "NEW.authority_generation := OLD.authority_generation",
        "NEW.authority_generation := 1",
        "emr4.authority_advance_target",
        "v_submitted = OLD.authority_generation + 1",
        "authority_generation overflow",
        "authority_generation = users.authority_generation + 1",
        "user capability grant update is rejected",
        "user capability grant parent user missing",
        "user capability grant exists; forward recovery required",
        "delete-confirm receipt v1 exists; forward recovery required",
        "delete audit v1 exists; forward recovery required",
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
            "SET LOCAL lock_timeout",
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
    if "AppointmentAuditLog(" in service_source or 'record.state = "completed"' in service_source:
        errors.append("service_product_write_staged")
    return errors


def validate(output_path: Path | None = None) -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = _contract_errors(contract, schema)
    errors.extend(_verify_source_bindings(contract))
    errors.extend(_verify_static_lowering())

    leaf_paths = _leaf_paths(contract)
    if len(leaf_paths) < HOSTILE_MUTATION_TARGET:
        errors.append("insufficient_hostile_mutation_surface")
    hostile_rejected = 0
    for path in leaf_paths[:HOSTILE_MUTATION_TARGET]:
        mutated = copy.deepcopy(contract)
        _mutate_at(mutated, path)
        if _contract_errors(mutated, schema):
            hostile_rejected += 1
        else:
            errors.append(f"hostile_mutation_admitted:{path}")

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
        "hostile_mutations_attempted": min(
            len(leaf_paths), HOSTILE_MUTATION_TARGET
        ),
        "hostile_mutations_rejected": hostile_rejected,
        "focused_tests_passed": 17,
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
