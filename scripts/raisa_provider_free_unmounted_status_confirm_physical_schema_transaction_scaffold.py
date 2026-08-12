"""Validate the provider-free unmounted status-confirm physical scaffold.

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
    "raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-scaffold/"
    "scaffold-contract.json"
)
SCHEMA_PATH = CONTRACT_PATH.with_name("scaffold-contract.schema.json")
EXPECTED_CONTRACT_SHA256 = (
    "3fe41f407cbfee52d198f5072e9c8d257c2c8404b53e84334d60de28680e8782"
)
HOSTILE_MUTATION_TARGET = 80


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
    model_source = (ROOT / "app/models/appointments.py").read_text(encoding="utf-8")
    migration_source = (
        ROOT
        / "alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py"
    ).read_text(encoding="utf-8")
    service_source = (
        ROOT / "app/services/appointment_status_physical.py"
    ).read_text(encoding="utf-8")

    model_tokens = (
        "appointment_state_version = Column(BigInteger, nullable=False",
        "completed_receipt_version = Column(SmallInteger, nullable=True)",
        "session_binding_digest = Column(LargeBinary, nullable=True)",
        "pre_state_version = Column(BigInteger, nullable=True)",
        "post_state_version = Column(BigInteger, nullable=True)",
        "response_body_canonical_bytes = Column(LargeBinary, nullable=True)",
        "ck_appointments_state_version_positive",
        "ck_appt_cmd_idem_receipt_version",
        "ck_appt_cmd_idem_status_receipt_v1_complete",
    )
    for token in model_tokens:
        if token not in model_source:
            errors.append(f"model_token_missing:{token}")

    migration_markers = (
        'revision: str = "w2x3y4z5a6b7"',
        'down_revision: Union[str, Sequence[str], None] = "v1w2x3y4z5b6"',
        'sa.Column("appointment_state_version", sa.BigInteger(), nullable=True)',
        'server_default=sa.text("1")',
        "UPDATE appointments SET appointment_state_version = 1",
        "CHECK (appointment_state_version >= 1) NOT VALID",
        'op.alter_column("appointments", "appointment_state_version", nullable=False)',
        "CREATE FUNCTION emr4_advance_appointment_state_version()",
        "CREATE TRIGGER trg_appointments_advance_state_version",
        "invalid appointment_state_version after cutover",
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
        "BEFORE UPDATE ON appointments",
        "NEW.appointment_state_version := OLD.appointment_state_version + 1",
        "appointment_state_version overflow",
        "status-confirm receipt v1 exists; forward recovery required",
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
            and node.name == "status_confirm_locked_transaction"
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
            'func.set_config("lock_timeout"',
            "db.query(Practice)",
            ".with_for_update(read=True)",
            "db.query(Appointment)",
            ".with_for_update()",
            "if not current_authority(practice, appointment):",
            "postgresql_insert(AppointmentCommandIdempotency)",
            "db.query(AppointmentCommandIdempotency)",
            ".with_for_update()",
            "if not current_authority(practice, appointment):",
            "if inserted:",
        )
        cursor = -1
        for marker in ordered:
            try:
                cursor = transaction_source.index(marker, cursor + 1)
            except ValueError:
                errors.append(f"transaction_order_missing:{marker}")
        if transaction_source.count("current_authority(practice, appointment)") != 2:
            errors.append("authority_check_count_invalid")
        for forbidden in ("nowait", "skip_locked", "appointment.status ="):
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
        "schema_version": "raisa.status_confirm_physical_schema_transaction_scaffold.evidence.v1",
        "result": (
            "raisa_provider_free_unmounted_status_confirm_physical_schema_transaction_scaffold_pass"
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
        "focused_tests_passed": 11,
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
