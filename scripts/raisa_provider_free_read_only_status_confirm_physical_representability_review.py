"""Validate the exact-file status-confirm physical representability review."""

from __future__ import annotations

import ast
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
    / "orchestration/continuity/raisa-provider-free-read-only-status-confirm-"
    "physical-representability-review"
)
CONTRACT_PATH = BASE / "physical-representability-review-contract.json"
SCHEMA_PATH = BASE / "physical-representability-review-contract.schema.json"
EVIDENCE_PATH = BASE / "provider-free-read-only-review-evidence.json"

EXPECTED_SOURCE_BINDINGS = {
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal-closeout.md": "2b379cbaefeac83a79a3776f78c58b48a94b4695de3356d56a57318a5ab594e7",
    "orchestration/agent_inbox/codex/raisa-status-confirm-runtime-convergence-rehearsal-sol-acceptance.md": "5aa5cfb2bc7690904fbebcb8ff053b176bb9cb0bea12650a766b8391278a48f5",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.json": "6f2c970a4ab9234e72d6ffb08b2aa9b8738b779b94cee1885dbf262bfb5306ce",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal/rehearsal-packet.json": "18c5bf4f6b6c22ab310e1571f794598a4317ff32f9103445b9d23edc5d112918",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal/provider-free-rehearsal-evidence.json": "503b8ea4fcd92fa8043ff5caf8fd8440e038470530a90fde9509d7ff126d1e06",
    "docs/api-spine/openapi/appointment-commands.yaml": "c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6",
    "app/models/appointments.py": "af00f7318da3f19732843c75b56721db89a3fa0c94b6e0feeb12a614850c4952",
    "app/services/appointment_idempotency.py": "c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410",
    "alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py": "a77be7e159614a579eb2dec2d3d8e5b401f1c1d1722f5f740367ae74e6a8a59a",
    "alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py": "da6493f60b8a8d39186c273db0b9615758b3927cc913d1117d12df0003f245fd",
    "alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py": "78d730ddf07051f5595c268fc031dea7d454c166a930250255de6aa26e2938ae",
}

PHYSICAL_SOURCE_PATHS = {
    "docs/api-spine/openapi/appointment-commands.yaml",
    "app/models/appointments.py",
    "app/services/appointment_idempotency.py",
    "alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py",
    "alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py",
    "alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py",
}

EXPECTED_DOMAIN_IDS = [
    "locked_state_version",
    "private_completed_receipt",
    "ordered_lock_boundary",
]
EXPECTED_ADDITIVE_REQUIREMENTS = {
    "locked_state_version": {
        "explicit positive monotonic appointment state identity",
        "locked read of the identity",
        "advance on every committed appointment state change",
        "safe migration and backfill contract",
    },
    "private_completed_receipt": {
        "pre-state version",
        "post-state version",
        "opaque session-binding digest semantics",
        "stored canonical public response bytes or an exactly equivalent byte-preserving representation",
        "completed-status constraints covering the full private receipt",
    },
    "ordered_lock_boundary": {
        "one caller-owned transaction boundary",
        "practice lock before appointment lock",
        "target absence stop before idempotency access",
        "idempotency lock after appointment lock",
        "current authority recheck before conflict/replay classification",
        "no insert or receipt disclosure before the accepted preconditions",
    },
}
EXPECTED_ACCEPTED_REQUIREMENTS = {
    "locked_state_version": (
        "A positive monotonic appointment_state_version is read under the appointment "
        "lock and advances on every committed appointment state change."
    ),
    "private_completed_receipt": (
        "The completed private receipt binds operation, practice, target, actor, opaque "
        "session digest, idempotency identity, request digest, audit identity, pre/post "
        "state versions and canonical public response digest/bytes."
    ),
    "ordered_lock_boundary": (
        "One backend transaction holds practice then appointment then idempotency-record "
        "locks, validates target and current authority, and only then classifies or "
        "discloses replay/conflict."
    ),
}

EXPECTED_MODEL_RECEIPT_FIELDS = {
    "practice_id",
    "actor_user_id",
    "actor_role",
    "operation_id",
    "route_family",
    "idempotency_key_hash",
    "request_body_hash",
    "response_status_code",
    "response_body_hash",
    "response_body_json",
    "target_appointment_id",
    "audit_log_id",
    "bernie_session_id",
}
MISSING_MODEL_RECEIPT_FIELDS = {
    "pre_state_version",
    "post_state_version",
    "canonical_response_bytes",
    "session_binding_digest",
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
            raise ValueError(f"missing source binding: {relative_path}")
        digest = _sha256(path)
        if digest != expected_hash:
            raise ValueError(f"source hash mismatch: {relative_path}")
        observed[relative_path] = digest
    return observed


def _class_assignment_names(tree: ast.Module, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names: set[str] = set()
            for child in node.body:
                if isinstance(child, (ast.Assign, ast.AnnAssign)):
                    targets = child.targets if isinstance(child, ast.Assign) else [child.target]
                    for target in targets:
                        if isinstance(target, ast.Name):
                            names.add(target.id)
            return names
    raise ValueError(f"missing class: {class_name}")


def _block(text: str, start: str, end: str) -> str:
    if start not in text or end not in text:
        raise ValueError(f"missing block delimiter: {start} / {end}")
    return text.split(start, 1)[1].split(end, 1)[0]


def verify_physical_observations() -> dict[str, Any]:
    model_text = (ROOT / "app/models/appointments.py").read_text(encoding="utf-8")
    model_tree = ast.parse(model_text)
    appointment_fields = _class_assignment_names(model_tree, "Appointment")
    audit_fields = _class_assignment_names(model_tree, "AppointmentAuditLog")
    receipt_fields = _class_assignment_names(
        model_tree, "AppointmentCommandIdempotency"
    )
    if "appointment_state_version" in appointment_fields or "state_version" in appointment_fields:
        raise ValueError("appointment state version is no longer absent")
    if "created_at" not in appointment_fields:
        raise ValueError("appointment created_at observation changed")
    if not EXPECTED_MODEL_RECEIPT_FIELDS.issubset(receipt_fields):
        raise ValueError("existing receipt primitive set changed")
    if not MISSING_MODEL_RECEIPT_FIELDS.isdisjoint(receipt_fields):
        raise ValueError("reviewed additive receipt gap changed")
    if not {"confirmed_warnings", "command_id", "bernie_session_id"}.issubset(
        audit_fields
    ):
        raise ValueError("audit correlation primitives changed")

    service_text = (ROOT / "app/services/appointment_idempotency.py").read_text(
        encoding="utf-8"
    )
    service_tree = ast.parse(service_text)
    imported_models: set[str] = set()
    for node in ast.walk(service_tree):
        if isinstance(node, ast.ImportFrom) and node.module == "app.models.appointments":
            imported_models.update(alias.name for alias in node.names)
    if imported_models != {"AppointmentCommandIdempotency"}:
        raise ValueError("idempotency service model scope changed")
    insert_position = service_text.index("postgresql_insert(AppointmentCommandIdempotency)")
    lock_position = service_text.index(".with_for_update()")
    conflict_position = service_text.index("if record.request_body_hash != request_body_hash")
    replay_position = service_text.index('if record.state == "completed"')
    if not insert_position < lock_position < conflict_position < replay_position:
        raise ValueError("current idempotency ordering observation changed")
    if service_text.count(".with_for_update()") != 1:
        raise ValueError("reviewed row-lock count changed")
    for exact in (
        "record.response_body_json = response_body",
        "record.response_body_hash = sha256_canonical_json(response_body)",
        "db.flush()",
    ):
        if exact not in service_text:
            raise ValueError(f"missing completion observation: {exact}")

    audit_migration = (
        ROOT / "alembic/versions/h8i9j0k1l2m3_add_appointment_audit_log.py"
    ).read_text(encoding="utf-8")
    warning_migration = (
        ROOT
        / "alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py"
    ).read_text(encoding="utf-8")
    receipt_migration = (
        ROOT
        / "alembic/versions/l1m2n3o4p5q6_add_appointment_command_idempotency.py"
    ).read_text(encoding="utf-8")
    for exact in (
        'op.create_table(\n        "appointment_audit_log"',
        'sa.Column(\n            "practice_id"',
        'sa.Column(\n            "appointment_id"',
    ):
        if exact not in audit_migration:
            raise ValueError("audit migration observation changed")
    if 'op.add_column(\n        "appointment_audit_log"' not in warning_migration:
        raise ValueError("additive migration primitive changed")
    for exact in (
        '"appointment_command_idempotency"',
        'sa.Column("response_body_hash"',
        'sa.Column("response_body_json"',
        "sa.UniqueConstraint(",
        "sa.CheckConstraint(",
    ):
        if exact not in receipt_migration:
            raise ValueError("idempotency migration observation changed")

    openapi_text = (
        ROOT / "docs/api-spine/openapi/appointment-commands.yaml"
    ).read_text(encoding="utf-8")
    status_path = _block(
        openapi_text,
        "  /appointments/proposals/status/confirm:\n",
        "  /appointments/proposals/check-in/{appointment_id}:\n",
    )
    status_schema = _block(
        openapi_text,
        "    AppointmentStatusConfirmationCommand:\n",
        "    AppointmentCheckInProposalCommand:\n",
    )
    result_schema = _block(
        openapi_text,
        "    AppointmentConfirmResultEnvelope:\n",
        "    SlotSearchNormalizeCommand:\n",
    )
    if "#/components/parameters/IdempotencyKey" not in status_path:
        raise ValueError("status idempotency API boundary changed")
    if "additionalProperties: false" not in status_schema:
        raise ValueError("status confirmation schema is no longer closed")
    if "additionalProperties: false" not in result_schema:
        raise ValueError("public result schema is no longer closed")

    return {
        "appointment_state_version_absent": True,
        "appointment_created_at_not_used_as_version": True,
        "receipt_existing_field_count": len(
            EXPECTED_MODEL_RECEIPT_FIELDS.intersection(receipt_fields)
        ),
        "receipt_additive_gap_count": len(MISSING_MODEL_RECEIPT_FIELDS),
        "audit_correlation_primitives_present": True,
        "idempotency_insert_precedes_only_row_lock": True,
        "idempotency_lock_precedes_conflict_and_replay": True,
        "response_json_and_canonical_hash_stored": True,
        "additive_migration_primitive_present": True,
        "status_idempotency_parameter_present": True,
        "public_status_and_result_schemas_closed": True,
    }


def validate_contract_semantics(contract: dict[str, Any]) -> None:
    if contract["source_head"] != "3af1af85cc3e6ee646f856a1ce6f306495741894":
        raise ValueError("source head changed")
    if contract["overall_verdict"] != "implementation_not_admitted":
        raise ValueError("implementation verdict changed")
    if [item["id"] for item in contract["domains"]] != EXPECTED_DOMAIN_IDS:
        raise ValueError("domain identity or order changed")
    for domain in contract["domains"]:
        if domain["verdict"] != "representable_with_additive_change":
            raise ValueError(f"domain verdict changed: {domain['id']}")
        if domain["accepted_requirement"] != EXPECTED_ACCEPTED_REQUIREMENTS[
            domain["id"]
        ]:
            raise ValueError(f"accepted requirement changed: {domain['id']}")
        if set(domain["additive_requirements"]) != EXPECTED_ADDITIVE_REQUIREMENTS[
            domain["id"]
        ]:
            raise ValueError(f"additive requirements changed: {domain['id']}")
        for observation in domain["current_observations"]:
            if observation["path"] not in PHYSICAL_SOURCE_PATHS:
                raise ValueError("observation escaped physical/API allowlist")
            lines = (ROOT / observation["path"]).read_text(encoding="utf-8").splitlines()
            if not 1 <= observation["line_start"] <= observation["line_end"] <= len(lines):
                raise ValueError("observation line range is invalid")
    if len(contract["cross_domain_findings"]) != 5:
        raise ValueError("cross-domain finding set changed")
    joined = " ".join(contract["cross_domain_findings"]).lower()
    for phrase in (
        "additive schema/service architecture",
        "timestamps",
        "stored canonical-byte replay",
        "with_for_update",
        "exact additive migration",
    ):
        if phrase not in joined:
            raise ValueError(f"missing cross-domain boundary: {phrase}")
    if set(contract["forbidden"].values()) != {False}:
        raise ValueError("every forbidden effect must remain false")
    if contract["next_candidate"] != (
        "provider_free_unmounted_status_confirm_physical_design_architecture"
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


def _remove(path: tuple[Any, ...]) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        target = path[-1]
        if isinstance(cursor, list):
            cursor.pop(target)
        else:
            cursor.pop(target)

    return mutate


def hostile_mutations() -> list[tuple[str, Mutation]]:
    mutations: list[tuple[str, Mutation]] = [
        ("source_head", _set(("source_head",), "0" * 40)),
        ("evidence_label", _set(("evidence_label",), "runtime")),
        ("overall_verdict", _set(("overall_verdict",), "implementation_admitted")),
        ("domain_removed", _remove(("domains", 2))),
        (
            "next_candidate",
            _set(("next_candidate",), "mounted_route_implementation"),
        ),
    ]
    for index in range(11):
        mutations.append(
            (
                f"source_hash_{index}",
                _set(("source_bindings", index, "sha256"), "0" * 64),
            )
        )
    for index, domain_id in enumerate(EXPECTED_DOMAIN_IDS):
        mutations.extend(
            [
                (
                    f"verdict_{domain_id}",
                    _set(("domains", index, "verdict"), "already_represented"),
                ),
                (
                    f"requirement_{domain_id}",
                    _set(("domains", index, "accepted_requirement"), "weakened"),
                ),
                (
                    f"additive_{domain_id}",
                    _set(("domains", index, "additive_requirements", 0), "removed"),
                ),
                (
                    f"observation_path_{domain_id}",
                    _set(("domains", index, "current_observations", 0, "path"), "app/routers/appointments.py"),
                ),
                (
                    f"observation_line_{domain_id}",
                    _set(("domains", index, "current_observations", 0, "line_end"), 99999),
                ),
            ]
        )
    for index in range(5):
        mutations.append(
            (
                f"cross_finding_{index}",
                _set(("cross_domain_findings", index), "weakened"),
            )
        )
    for key in (
        "protected_path_content_or_metadata_used",
        "application_or_migration_edited",
        "application_or_database_imported",
        "route_or_database_executed",
        "physical_design_selected",
        "migration_or_backfill_selected",
        "provider_or_credential_used",
        "product_or_patient_data_used",
        "command_or_deployment_executed",
        "protected_ref_moved",
    ):
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
            verify_physical_observations()
        except (AssertionError, KeyError, TypeError, ValidationError, ValueError):
            rejected += 1
            continue
        raise ValueError(f"hostile mutation admitted: {mutation_id}")
    if rejected < 30:
        raise ValueError("fewer than 30 hostile mutations were rejected")
    return {"attempted": len(mutations), "rejected": rejected}


def build_evidence() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    validate_schema(contract, schema)
    validate_contract_semantics(contract)
    source_hashes = verify_source_bindings(contract)
    physical_observations = verify_physical_observations()
    hostile = reject_hostile_mutations(contract, schema)
    return {
        "schema_version": "raisa.status_confirm_physical_representability_review_evidence.v1",
        "result": contract["result"],
        "source_head": contract["source_head"],
        "evidence_label": contract["evidence_label"],
        "overall_verdict": contract["overall_verdict"],
        "source_hashes": source_hashes,
        "domain_verdicts": {
            domain["id"]: domain["verdict"] for domain in contract["domains"]
        },
        "physical_observations": physical_observations,
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
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
