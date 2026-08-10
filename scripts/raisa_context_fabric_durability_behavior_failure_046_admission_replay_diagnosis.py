"""Diagnose behavior attempt 046 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-046.json"
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
    "ea2fc7f55121604b8f68b5bbacc55b97c98ead76a5793b6d7c766f2269b311c0"
)
EXPECTED_BODY_SHA256 = (
    "21087e25e087c1865865d5f1cd24f192451f62658243420134deb903687e46bb"
)
EXPECTED_INERT_SQL_SHA256 = (
    "fc1c00ab7209a6689f4de29a14a134719a0110dfd3b556172781384332af41fa"
)
SOURCE_HEAD = "0a3bddd3a3a6cc52bd3edf34826ca5a76aaa8369"
PROGRAM = "emr4_context_fabric.admit_proofread_observation_v1"
INSERT_NODES = {
    PROGRAM + ".insert_mismatch",
    PROGRAM + ".insert_reuse",
    PROGRAM + ".insert_primary",
}
CONFLICT_KEY = [
    "practice_id",
    "source_contract_id",
    "stream_id",
    "stream_epoch",
    "observer_id",
    "observer_generation",
    "source_position",
    "entry_kind",
]


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


def _is_admitted_at_timestamp_comparison(value: dict[str, Any]) -> bool:
    if value.get("op") != "EQ":
        return False
    left = value.get("left", {})
    right = value.get("right", {})
    return (
        left.get("op") == "REF"
        and left.get("kind") == "SOURCE_COLUMN"
        and left.get("relation")
        == "emr4_context_fabric.context_proofread_observation_admission"
        and left.get("column") == "admitted_at"
        and right
        == {
            "op": "TRANSACTION_TIMESTAMP",
            "type": "pg_catalog.timestamptz",
        }
    )


def diagnose() -> dict[str, Any]:
    failure_raw = FAILURE_PATH.read_bytes()
    body_raw = _git_source_bytes(BODY_PATH)
    inert_raw = _git_source_bytes(INERT_SQL_PATH)
    if _sha256(failure_raw) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_sha256")
    if _sha256(body_raw) != EXPECTED_BODY_SHA256:
        raise RuntimeError("body_sha256")
    if _sha256(inert_raw) != EXPECTED_INERT_SQL_SHA256:
        raise RuntimeError("inert_sql_sha256")

    failure = json.loads(failure_raw)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "e4db8cf23eb421e40744ea25"
        and detail
        == {
            "code": "unexpected_rejection",
            "detail_digest": (
                "sha256:9d89f55c4f834a9f79dcb6234392a38b49ea4bc8d5ab1fd7ec6892f8593a9f7a"
            ),
            "function_id": PROGRAM,
            "function_line": 72,
            "scenario_id": "BTR-I02",
            "sqlstate": "CF004",
            "stage": "scenario",
        }
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("removed") is True
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_046_not_closed")

    body = json.loads(body_raw)
    programs = [row for row in body["body_programs"] if row.get("id") == PROGRAM]
    if len(programs) != 1:
        raise RuntimeError("admission_program")
    nodes = {
        row["node_id"]: row
        for row in _walk(programs[0]["ast"])
        if row.get("node_id") in INSERT_NODES
    }
    if set(nodes) != INSERT_NODES:
        raise RuntimeError("insert_or_reload_population")

    timestamp_bound_nodes: list[str] = []
    timestamp_compared_nodes: list[str] = []
    for node_id, node in nodes.items():
        if node.get("op") != "INSERT_OR_RELOAD_COMPARE":
            raise RuntimeError("insert_or_reload_op")
        operands = node["operands"]
        if operands.get("conflict_key_columns") != CONFLICT_KEY:
            raise RuntimeError("conflict_key")
        admitted_at = [
            binding
            for binding in operands["bindings"]
            if binding.get("column") == "admitted_at"
        ]
        if len(admitted_at) != 1 or admitted_at[0]["value"] != {
            "op": "TRANSACTION_TIMESTAMP",
            "type": "pg_catalog.timestamptz",
        }:
            raise RuntimeError("admitted_at_binding")
        timestamp_bound_nodes.append(node_id)
        winner = operands.get("winner_predicate", {})
        if winner.get("op") != "AND":
            raise RuntimeError("winner_predicate_shape")
        timestamp_terms = [
            term
            for term in winner.get("operands", [])
            if _is_admitted_at_timestamp_comparison(term)
        ]
        if len(timestamp_terms) != 1:
            raise RuntimeError("winner_timestamp_population")
        timestamp_compared_nodes.append(node_id)

    inert = inert_raw.decode("utf-8")
    if not (
        "ADD CONSTRAINT pk_cf_04 PRIMARY KEY (" + ", ".join(CONFLICT_KEY) + ");"
        in inert
        and inert.count("ON CONFLICT ON CONSTRAINT pk_cf_04 DO NOTHING") == 3
        and "admitted_at = pg_catalog.transaction_timestamp()" in inert
    ):
        raise RuntimeError("inert_reload_shape")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-046-admission-replay-diagnosis.v1",
        "status": "deterministic_server_authored_timestamp_replay_comparison_contradiction_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 46,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-I02",
            "sqlstate": "CF004",
            "function_id": PROGRAM,
            "function_line": 72,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "conflict_key_columns": CONFLICT_KEY,
            "server_authored_timestamp_bound_nodes": sorted(timestamp_bound_nodes),
            "unstable_timestamp_winner_comparison_nodes": sorted(
                timestamp_compared_nodes
            ),
            "failed_path": PROGRAM + ".insert_mismatch.reload_compare",
            "failure_translation": "zero_or_ambiguous_reload_rows_to_F_CARDINALITY_CF004",
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "remove_only_admitted_at_from_winner_predicate": True,
            "preserve_admitted_at_insert_and_return_column": True,
            "affected_nodes": sorted(INSERT_NODES),
            "conflict_key_unchanged": True,
            "immutable_body_parent_changed": False,
            "runtime_authority_changed": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
