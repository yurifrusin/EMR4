"""Diagnose behavior attempt 045 without opening another PostgreSQL runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
BEHAVIOR_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-behavior-transaction-rehearsal"
)
FAILURE_PATH = (
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-045.json"
)
STRUCTURAL_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "migration-transaction-architecture/migration-transaction-architecture-contract.json"
)
BODY_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "function-trigger-body-architecture/function-trigger-body-architecture-contract.json"
)
INERT_SQL_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "inert-ddl-rehearsal/durability-schema.sql.inert"
)

EXPECTED_FAILURE_SHA256 = (
    "e4af201491241a904d337650a7dbd7c3e8a36daf8bb0ea85aaae462da1045d67"
)
EXPECTED_STRUCTURAL_SHA256 = (
    "6c82c5a288c43ad2d8784f6eeb0c1f1efe1afea9a2b63721aebfc4371b63fe5e"
)
EXPECTED_BODY_SHA256 = (
    "21087e25e087c1865865d5f1cd24f192451f62658243420134deb903687e46bb"
)
EXPECTED_INERT_SQL_SHA256 = (
    "bfd8fd924a1771ea03a2395fbd1f154253f098a3e488188a2f77778c197d7f38"
)
SOURCE_HEAD = "6b00f067348b7810336286fdf335609327251557"
ADMISSION = "context_proofread_observation_admission"
PROGRAM = "emr4_context_fabric.admit_proofread_observation_v1"
CONFLICT_NODES = {
    PROGRAM + ".insert_mismatch",
    PROGRAM + ".insert_reuse",
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _walk(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _git_source_bytes(path: Path) -> bytes:
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"{SOURCE_HEAD}:{relative}"],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        raise RuntimeError("bound_git_source_unavailable")
    return result.stdout


def diagnose() -> dict[str, Any]:
    inputs = {
        "failure": (FAILURE_PATH, EXPECTED_FAILURE_SHA256),
        "structural": (STRUCTURAL_PATH, EXPECTED_STRUCTURAL_SHA256),
        "body": (BODY_PATH, EXPECTED_BODY_SHA256),
        "inert_sql": (INERT_SQL_PATH, EXPECTED_INERT_SQL_SHA256),
    }
    loaded: dict[str, Any] = {}
    raw: dict[str, bytes] = {}
    for name, (path, expected) in inputs.items():
        raw[name] = path.read_bytes() if name == "failure" else _git_source_bytes(path)
        if _sha256(raw[name]) != expected:
            raise RuntimeError(name + "_sha256")
        if path.suffix == ".json":
            loaded[name] = json.loads(raw[name])

    failure = loaded["failure"]
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "67070f55e5bc3898e906bb64"
        and detail
        == {
            "code": "unexpected_rejection",
            "coordinate_status": "missing",
            "detail_digest": "sha256:9af71346e8b5412ba86c47471b5e19f5b23c0b5c7869d7647a10eaf6ba2a1b6b",
            "scenario_id": "BTR-I02",
            "sqlstate": "23502",
            "stage": "scenario",
        }
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("removed") is True
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_045_not_closed")

    structural = loaded["structural"]
    domains = {row["name"]: row for row in structural["type_catalogue"]["domains"]}
    frame_mask = domains.get("frame_mask")
    if not frame_mask or frame_mask.get("not_null_values") is not True:
        raise RuntimeError("frame_mask_domain_not_null")
    relations = {
        row["name"]: row for row in structural["relation_catalogue"]["relations"]
    }
    admission = relations.get(ADMISSION)
    if admission is None:
        raise RuntimeError("admission_relation")
    affected = [
        row for row in admission["columns"] if row.get("name") == "affected_frame_mask"
    ]
    if len(affected) != 1 or affected[0] != {
        "name": "affected_frame_mask",
        "data_type": "frame_mask",
        "nullable": True,
        "default_sql": None,
    }:
        raise RuntimeError("nullable_admission_frame_mask")
    checks = [row["expression_sql"] for row in admission["check_constraints"]]
    conflict_check = [value for value in checks if "entry_kind = 'CONFLICT'" in value]
    if (
        len(conflict_check) != 1
        or "affected_frame_mask IS NULL" not in conflict_check[0]
    ):
        raise RuntimeError("conflict_shape_requires_null")

    body = loaded["body"]
    programs = [row for row in body["body_programs"] if row.get("id") == PROGRAM]
    if len(programs) != 1:
        raise RuntimeError("admission_program")
    nodes = {
        row["node_id"]: row
        for row in _walk(programs[0]["ast"])
        if row.get("node_id") in CONFLICT_NODES
    }
    if set(nodes) != CONFLICT_NODES:
        raise RuntimeError("conflict_node_population")
    for node in nodes.values():
        bindings = {row["column"]: row["value"] for row in node["operands"]["bindings"]}
        if bindings.get("affected_frame_mask") != {
            "op": "CONST",
            "type": "emr4_context_fabric.frame_mask",
            "value": None,
        }:
            raise RuntimeError("conflict_frame_mask_binding")

    inert = raw["inert_sql"].decode("utf-8")
    if not (
        "CREATE DOMAIN emr4_context_fabric.frame_mask AS pg_catalog.int2\n    NOT NULL"
        in inert
        and inert.count("NULL::emr4_context_fabric.frame_mask") >= 2
    ):
        raise RuntimeError("inert_domain_null_contradiction")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-045-frame-mask-domain-diagnosis.v1",
        "status": "deterministic_frame_mask_domain_nullable_conflict_row_contradiction_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 45,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-I02",
            "sqlstate": "23502",
            "coordinate_status": "missing",
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "domain": "emr4_context_fabric.frame_mask",
            "domain_not_null": True,
            "nullable_relation_column": "emr4_context_fabric.context_proofread_observation_admission.affected_frame_mask",
            "conflict_shape_requires_null": True,
            "conflict_body_nodes_emit_typed_null": sorted(CONFLICT_NODES),
            "inert_sql_contains_typed_null": True,
            "postgresql_failure_class": "not_null_violation_before_table_column_coordinate",
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "effective_frame_mask_domain_not_null": False,
            "frame_mask_range_check_preserved": True,
            "required_column_not_null_constraints_preserved": True,
            "nullable_conflict_column_and_shape_preserved": True,
            "structural_parent_changed": False,
            "body_parent_changed": False,
            "runtime_authority_changed": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
