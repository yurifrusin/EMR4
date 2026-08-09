"""Diagnose behavior failure 034 without opening another PostgreSQL runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
BEHAVIOR_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal"
)
FAILURE_PATH = (
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-034.json"
)
BODY_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-function-trigger-body-architecture"
    / "function-trigger-body-architecture-contract.json"
)
STRUCTURAL_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-migration-transaction-architecture"
    / "migration-transaction-architecture-contract.json"
)
ENTRY_PROGRAMS_PATH = (
    ROOT
    / "scripts"
    / "raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py"
)
INERT_SQL_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
    / "durability-schema.sql.inert"
)

SOURCE_HEAD = "df5352fb6964cad6e15195cfe8c9e17346a061b4"
EXPECTED_FAILURE_SHA256 = (
    "68d61a9c55c800ca1670c6e0e7cde3e720486a82e2125649f64375844c09262a"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "01f92356def997b96adb3115cfb4b82afc29a27e72cab5823c81a6b5f2e2a7f1"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "edbc7f2361f8b5a2812dcff2a7cdf81bef7bd2a6d280be5a9023571c5121508e"
)
EXPECTED_STRUCTURAL_SOURCE_SHA256 = (
    "5b5e3bc3108dc1105017f57ceade03c4bce33b898d7b71f0ede0640ce0bc83c7"
)
EXPECTED_ENTRY_PROGRAMS_SHA256 = (
    "81247961312f5d59965c67aa6ee2956de088675b531d1e5aa6a8d877b3b2ecf1"
)
EXPECTED_INERT_SQL_SHA256 = (
    "8756f315a3f1112551550141c1fff83d047ff24103b357e97ddb17b0c805e470"
)
PROGRAM_ID = "emr4_context_fabric.admit_proofread_observation_v1"
PRIMARY_NODE = PROGRAM_ID + ".insert_primary"
CONFLICT_NODES = [PROGRAM_ID + ".insert_mismatch", PROGRAM_ID + ".insert_reuse"]
PRIMARY_OUTCOME_FIELDS = [
    "observation_digest",
    "decision",
    "reason_code",
    "affected_frame_mask",
    "checkpoint_disposition",
]
CHECK_EXPRESSION = (
    "((entry_kind = 'PRIMARY'::emr4_context_fabric.admission_entry_kind AND "
    "observation_digest IS NOT NULL AND decision IS NOT NULL AND reason_code IS NOT NULL AND "
    "affected_frame_mask IS NOT NULL AND checkpoint_disposition IS NOT NULL AND "
    "attempted_admission_digest IS NULL AND conflict_reason IS NULL) OR "
    "(entry_kind = 'CONFLICT'::emr4_context_fabric.admission_entry_kind AND "
    "observation_digest IS NULL AND decision IS NULL AND reason_code IS NULL AND "
    "affected_frame_mask IS NULL AND checkpoint_disposition IS NULL AND "
    "attempted_admission_digest IS NOT NULL AND conflict_reason IS NOT NULL))"
)
EXPECTED_NULL_EQ_WINNERS = {
    "emr4_context_fabric.admit_proofread_observation_v1.insert_primary": [
        "conflict_reason"
    ],
    "emr4_context_fabric.register_observer_generation_v1.diary_frame": ["retired_at"],
    "emr4_context_fabric.register_observer_generation_v1.generation_insert": [
        "consumed_at",
        "terminal_reason",
    ],
    "emr4_context_fabric.register_observer_generation_v1.waiting_frame": ["retired_at"],
    "emr4_context_fabric.rotate_observation_key_v1.lifecycle_insert": [
        "source_position"
    ],
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_digest(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("contract_sha256", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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


def _walk(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _node(body: dict[str, Any], node_id: str) -> dict[str, Any]:
    matches = [node for node in _walk(body) if node.get("node_id") == node_id]
    if len(matches) != 1:
        raise RuntimeError("body_node_population:" + node_id)
    return matches[0]


def _bindings(node: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["column"]: row["value"]
        for row in node.get("operands", {}).get("bindings", [])
    }


def _null_eq_winners(body: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for node in _walk(body):
        if node.get("op") != "INSERT_OR_RELOAD_COMPARE":
            continue
        columns = sorted(
            predicate.get("left", {}).get("column")
            for predicate in _walk(node.get("operands", {}).get("winner_predicate", {}))
            if predicate.get("op") == "EQ"
            and predicate.get("right", {}).get("op") == "CONST"
            and predicate.get("right", {}).get("value") is None
        )
        if columns:
            result[node["node_id"]] = columns
    return result


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_034_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "ef5776640bc23a0ff88c9167"
        and detail.get("scenario_id") == "BTR-E03"
        and detail.get("sqlstate") == "23514"
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_034_not_closed")

    body_bytes = _git_source_bytes(BODY_PATH)
    structural_bytes = _git_source_bytes(STRUCTURAL_PATH)
    entry_programs_bytes = _git_source_bytes(ENTRY_PROGRAMS_PATH)
    inert_sql_bytes = _git_source_bytes(INERT_SQL_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    if _sha256(structural_bytes) != EXPECTED_STRUCTURAL_SOURCE_SHA256:
        raise RuntimeError("structural_source_sha256")
    if _sha256(entry_programs_bytes) != EXPECTED_ENTRY_PROGRAMS_SHA256:
        raise RuntimeError("entry_programs_sha256")
    if _sha256(inert_sql_bytes) != EXPECTED_INERT_SQL_SHA256:
        raise RuntimeError("inert_sql_sha256")

    body = json.loads(body_bytes)
    structural = json.loads(structural_bytes)
    if _canonical_digest(body) != EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    checks = [row for row in _walk(structural) if row.get("name") == "ck_cf_04_02"]
    if len(checks) != 1 or checks[0].get("expression_sql") != CHECK_EXPRESSION:
        raise RuntimeError("admission_shape_check_definition")

    primary = _bindings(_node(body, PRIMARY_NODE))
    if not (
        primary["entry_kind"].get("value") == "PRIMARY"
        and all(primary[field].get("op") == "FIELD" for field in PRIMARY_OUTCOME_FIELDS)
        and primary["attempted_admission_digest"].get("op") == "CANONICAL_DIGEST"
        and primary["conflict_reason"].get("op") == "CONST"
        and primary["conflict_reason"].get("value") is None
    ):
        raise RuntimeError("primary_shape_contradiction_not_proven")

    for node_id in CONFLICT_NODES:
        conflict = _bindings(_node(body, node_id))
        if not (
            conflict["entry_kind"].get("value") == "CONFLICT"
            and all(
                conflict[field].get("op") == "FIELD" for field in PRIMARY_OUTCOME_FIELDS
            )
            and conflict["attempted_admission_digest"].get("op") == "CANONICAL_DIGEST"
            and conflict["conflict_reason"].get("value") is not None
        ):
            raise RuntimeError("conflict_shape_contradiction_not_proven:" + node_id)

    null_eq_winners = _null_eq_winners(body)
    if null_eq_winners != EXPECTED_NULL_EQ_WINNERS:
        raise RuntimeError("null_equality_reload_population")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-034-admission-row-shape-diagnosis.v1",
        "status": "deterministic_body_to_admission_check_contradiction_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 34,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E03",
            "sqlstate": "23514",
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "constraint": "ck_cf_04_02",
            "primary_violation": "attempted_admission_digest_populated_but_must_be_null",
            "latent_conflict_violation": "primary_outcome_fields_populated_but_must_be_null",
            "latent_reload_violation": "ordinary_equality_used_against_null_in_five_winner_predicates",
            "null_equality_winners": null_eq_winners,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "structural_source_sha256": "sha256:" + EXPECTED_STRUCTURAL_SOURCE_SHA256,
            "entry_programs_source_sha256": "sha256:" + EXPECTED_ENTRY_PROGRAMS_SHA256,
            "inert_sql_source_sha256": "sha256:" + EXPECTED_INERT_SQL_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "primary_row_shape": "outcome_fields_present_attempted_digest_null_conflict_reason_null",
            "conflict_row_shape": "outcome_fields_null_attempted_digest_present_conflict_reason_present",
            "null_reload_comparison": "is_null_for_typed_null_bindings",
            "body_program_change": True,
            "inert_artifact_regeneration": True,
            "parse_catalogue_rebind_required": True,
            "behavior_parent_rebind_required": True,
            "scenario_population_change": False,
            "principal_or_sqlstate_change": False,
            "authority_change": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
