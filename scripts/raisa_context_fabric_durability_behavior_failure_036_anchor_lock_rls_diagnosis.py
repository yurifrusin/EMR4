"""Diagnose behavior failure 036 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-036.json"
)
RECEIPT_PATH = (
    BEHAVIOR_DIR / "provider-free-behavior-transaction-diagnosis-evidence-036.json"
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
INERT_SQL_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
    / "durability-schema.sql.inert"
)

SOURCE_HEAD = "978f54205966d412a9a5ead03b1c2c16ca46c5e0"
EXPECTED_FAILURE_SHA256 = (
    "662022a5d0d3744a91397b6a6b8d89e0bfc488631e88691053a7536d914de75c"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "67817da7faafd6019c7d7f573dedef2b2a28d5cda2be6ce340f5b3e8997b51ef"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "32edb340c490d509015bcafe9fecddb1057400a14c537f5d3fdb4bbfee6d3e9c"
)
EXPECTED_STRUCTURAL_SOURCE_SHA256 = (
    "58920ed1bf24ce1a8372b6ae46e50250e2fe053ae881e7992e2856f6648fc8ba"
)
EXPECTED_STRUCTURAL_CONTRACT_SHA256 = (
    "3ce317803da9cbd1a38a1f922627784467b3e8cc7e34dac924c09c4be6bf6a16"
)
EXPECTED_INERT_SQL_SHA256 = (
    "aa26f92671a18d927e423f9d7df80973a19a87f32d49d85cc3f3d55f6808e8e9"
)
SELECT_NODE_ID = (
    "emr4_context_fabric.apply_durability_transition_v1.current_anchor_set"
)
CARDINALITY_NODE_ID = (
    "emr4_context_fabric.apply_durability_transition_v1.primary_anchor_cardinality"
)
FAILING_LOCK_NODE_ID = (
    "emr4_context_fabric.apply_durability_transition_v1.lock_anchor_for_proof"
)
SELECT_POLICY_ID = "pol_cf_08_select"
INSERT_POLICY_ID = "pol_cf_08_insert"
PROPOSED_LOCK_POLICY_ID = "pol_cf_08_update_lock"
ALIAS_LOCK_POLICY_ID = "pol_cf_02_update_lock"
ANCHOR_RELATION = "emr4_context_fabric.context_recovery_anchor"
ANCHOR_RELATION_SHORT = "context_recovery_anchor"
LOCK_CAPABILITIES = ["COORDINATOR", "LIFECYCLE"]
LOCK_USING_SQL = (
    "emr4_context_fabric.session_binding_allows_v1(session_user, "
    "ARRAY['COORDINATOR'::emr4_context_fabric.logical_capability, "
    "'LIFECYCLE'::emr4_context_fabric.logical_capability], practice_id, "
    "source_contract_id, transaction_timestamp())"
)


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


def _one(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
    if len(rows) != 1:
        raise RuntimeError(label + "_population")
    return rows[0]


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_036_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "701e15b874bd1c79f95466b5"
        and detail.get("scenario_id") == "BTR-E04"
        and detail.get("sqlstate") == "CF004"
        and detail.get("function_id")
        == "emr4_context_fabric.apply_durability_transition_v1"
        and detail.get("function_line") == 299
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_036_not_closed")

    body_bytes = _git_source_bytes(BODY_PATH)
    structural_bytes = _git_source_bytes(STRUCTURAL_PATH)
    inert_sql_bytes = _git_source_bytes(INERT_SQL_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    if _sha256(structural_bytes) != EXPECTED_STRUCTURAL_SOURCE_SHA256:
        raise RuntimeError("structural_source_sha256")
    if _sha256(inert_sql_bytes) != EXPECTED_INERT_SQL_SHA256:
        raise RuntimeError("inert_sql_sha256")

    body = json.loads(body_bytes)
    structural = json.loads(structural_bytes)
    if _canonical_digest(body) != EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    if _canonical_digest(structural) != EXPECTED_STRUCTURAL_CONTRACT_SHA256:
        raise RuntimeError("structural_contract_sha256")

    select_node = _one(
        [node for node in _walk(body) if node.get("node_id") == SELECT_NODE_ID],
        "anchor_select_node",
    )
    cardinality_node = _one(
        [node for node in _walk(body) if node.get("node_id") == CARDINALITY_NODE_ID],
        "anchor_cardinality_node",
    )
    failing_lock = _one(
        [node for node in _walk(body) if node.get("node_id") == FAILING_LOCK_NODE_ID],
        "anchor_lock_node",
    )
    if not (
        select_node.get("op") == "SELECT_SET"
        and select_node.get("operands", {}).get("relation") == ANCHOR_RELATION
        and select_node.get("operands", {}).get("output_symbol")
        == "current_anchor_set"
        and cardinality_node.get("op") == "ASSERT"
        and cardinality_node.get("operands", {}).get("failure_id") == "F_STATE"
        and failing_lock.get("op") == "LOCK_EXACT"
        and failing_lock.get("operands", {}).get("relation") == ANCHOR_RELATION
        and failing_lock.get("operands", {}).get("mode") == "FOR_SHARE"
        and failing_lock.get("operands", {}).get("ordinal") == 4
    ):
        raise RuntimeError("anchor_read_then_lock_contract")

    anchor_locks = [
        node
        for node in _walk(body)
        if node.get("op") == "LOCK_EXACT"
        and node.get("operands", {}).get("relation") == ANCHOR_RELATION
    ]
    if not (
        len(anchor_locks) == 5
        and all(node["operands"].get("mode") == "FOR_SHARE" for node in anchor_locks)
        and sum(
            str(node.get("node_id", "")).startswith(
                "emr4_context_fabric.apply_durability_transition_v1."
            )
            for node in anchor_locks
        )
        == 4
        and sum(
            str(node.get("node_id", "")).startswith(
                "emr4_context_fabric.rotate_observation_key_v1."
            )
            for node in anchor_locks
        )
        == 1
    ):
        raise RuntimeError("anchor_lock_population")

    policies = structural["rls_policy_catalogue"]["policies"]
    policy_ids = [row["id"] for row in policies]
    select_policy = _one(
        [row for row in policies if row.get("id") == SELECT_POLICY_ID],
        "anchor_select_policy",
    )
    alias_lock_policy = _one(
        [row for row in policies if row.get("id") == ALIAS_LOCK_POLICY_ID],
        "alias_lock_policy",
    )
    if not (
        select_policy.get("relation") == ANCHOR_RELATION_SHORT
        and select_policy.get("command") == "SELECT"
        and "'COORDINATOR'::" in select_policy.get("using_sql", "")
        and "'LIFECYCLE'::" in select_policy.get("using_sql", "")
        and PROPOSED_LOCK_POLICY_ID not in policy_ids
        and alias_lock_policy.get("command") == "UPDATE"
        and alias_lock_policy.get("with_check_sql", "").endswith(" AND FALSE")
    ):
        raise RuntimeError("anchor_lock_policy_gap")

    anchor_relation = _one(
        [
            row
            for row in structural["relation_catalogue"]["relations"]
            if row.get("name") == ANCHOR_RELATION_SHORT
        ],
        "anchor_relation",
    )
    if anchor_relation.get("rls_policy_ids") != [SELECT_POLICY_ID, INSERT_POLICY_ID]:
        raise RuntimeError("anchor_relation_policy_population")

    roles = {row["role"]: row for row in structural["role_matrix"]}
    for role_id, entry_point in (
        ("context_coordinator", "apply_durability_transition_v1"),
        ("context_lifecycle", "rotate_observation_key_v1"),
    ):
        role = roles[role_id]
        if not (
            entry_point in role.get("execute_entry_points", [])
            and role.get("direct_table_dml") == []
            and role.get("nobypassrls") is True
        ):
            raise RuntimeError(role_id + "_authority_boundary")

    sql_lines = inert_sql_bytes.decode("utf-8").splitlines()
    if not (
        sql_lines[953].startswith(
            "CREATE FUNCTION emr4_context_fabric.apply_durability_transition_v1"
        )
        and sql_lines[955] == "AS $durability_inert$"
        and "FROM emr4_context_fabric.context_recovery_anchor"
        in sql_lines[1250]
        and sql_lines[1250].endswith(" FOR SHARE;")
        and "ERRCODE = 'CF004'" in sql_lines[1253]
        and 1254 - 956 + 1 == 299
    ):
        raise RuntimeError("postgresql_function_line_map")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-036-anchor-lock-rls-diagnosis.v1",
        "status": "deterministic_anchor_for_share_policy_gap_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 36,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E04",
            "sqlstate": "CF004",
            "function_line": 299,
            "mapped_sql_line": 1254,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "entry_point": "apply_durability_transition_v1",
            "principal": "context_coordinator",
            "plain_select_before_lock": SELECT_NODE_ID,
            "exact_cardinality_before_lock": CARDINALITY_NODE_ID,
            "failing_lock": FAILING_LOCK_NODE_ID,
            "locked_relation": ANCHOR_RELATION,
            "lock_mode": "FOR_SHARE",
            "anchor_lock_node_count": len(anchor_locks),
            "coordinator_anchor_lock_node_count": 4,
            "lifecycle_anchor_lock_node_count": 1,
            "present_anchor_policy_ids": [SELECT_POLICY_ID, INSERT_POLICY_ID],
            "missing_lock_policy_id": PROPOSED_LOCK_POLICY_ID,
            "append_only_lock_policy_precedent": ALIAS_LOCK_POLICY_ID,
            "coordinator_direct_table_dml": [],
            "lifecycle_direct_table_dml": [],
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "structural_source_sha256": "sha256:"
            + EXPECTED_STRUCTURAL_SOURCE_SHA256,
            "structural_contract_sha256": "sha256:"
            + EXPECTED_STRUCTURAL_CONTRACT_SHA256,
            "inert_sql_source_sha256": "sha256:" + EXPECTED_INERT_SQL_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "new_policy_id": PROPOSED_LOCK_POLICY_ID,
            "relation": ANCHOR_RELATION_SHORT,
            "command": "UPDATE",
            "using_capabilities": LOCK_CAPABILITIES,
            "using_sql": LOCK_USING_SQL,
            "with_check_sql": LOCK_USING_SQL + " AND FALSE",
            "coordinator_direct_table_dml_remains_empty": True,
            "lifecycle_direct_table_dml_remains_empty": True,
            "append_only_invariant_unchanged": True,
            "entry_point_execute_grants_unchanged": True,
            "body_program_change": False,
            "inert_artifact_regeneration": True,
            "parse_catalogue_rebind_required": True,
            "behavior_parent_rebind_required": True,
            "scenario_population_change": False,
            "new_external_authority": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    result = diagnose()
    RECEIPT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
