"""Diagnose behavior failure 037 without opening another PostgreSQL runtime."""

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
FAILURE_PATH = BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-037.json"
RECEIPT_PATH = BEHAVIOR_DIR / "provider-free-behavior-transaction-diagnosis-evidence-037.json"
RESTORED_MUTABLE_ANCHOR_PATH = (
    BEHAVIOR_DIR / "provider-free-behavior-transaction-diagnosis-evidence-029.json"
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

SOURCE_HEAD = "3b9be4ff669eeeacb0eacf02042a72368aff57f3"
EXPECTED_FAILURE_SHA256 = "a5767ddcc04643a949ea465abadd94fdb8dbc28c272bdf19808abc3e7759b852"
EXPECTED_RESTORED_MUTABLE_ANCHOR_SHA256 = (
    "1e5c22aa6098acfa0764161af4f1f27c292fa249faac96aa699a20aa1f700214"
)
EXPECTED_RESTORED_MUTABLE_EVIDENCE_SHA256 = (
    "09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b"
)
EXPECTED_RESTORED_MUTABLE_ATTEMPT_ID = "fce9773c076f3ede41a4875c"
EXPECTED_BODY_SOURCE_SHA256 = "34d3febf2a5fe02214102ccbabe93d600a5178c3ad050c154dd73837ec06996e"
EXPECTED_BODY_CONTRACT_SHA256 = "b54b2e6800b4484f84b2c7ba57566ecfe8c04b9a8c8e91ac6bd67be8f22b5840"
EXPECTED_STRUCTURAL_SOURCE_SHA256 = "7508a124b68db4c46dd1b91a4591065a0f0238911491ba9db9b6011e8c6259dc"
EXPECTED_STRUCTURAL_CONTRACT_SHA256 = "6802a7355e62d9d29f735a4c0703e90f2c9bcfaa4606d694070fa62380dc741c"
EXPECTED_INERT_SQL_SHA256 = "550336e145eac6ac004447d05ea3e72d970f6d8283d3af2689aed62cfff92bc6"
SELECT_NODE_ID = "emr4_context_fabric.apply_durability_transition_v1.primary_set"
BRANCH_NODE_ID = "emr4_context_fabric.apply_durability_transition_v1.has_primary"
FAILING_LOCK_NODE_ID = "emr4_context_fabric.apply_durability_transition_v1.lock_primary"
SELECT_POLICY_ID = "pol_cf_04_select"
INSERT_POLICY_ID = "pol_cf_04_insert"
PROPOSED_LOCK_POLICY_ID = "pol_cf_04_update_lock"
ANCHOR_LOCK_POLICY_ID = "pol_cf_08_update_lock"
ADMISSION_RELATION = "emr4_context_fabric.context_proofread_observation_admission"
ADMISSION_RELATION_SHORT = "context_proofread_observation_admission"
LOCK_CAPABILITIES = ["COORDINATOR"]
LOCK_USING_SQL = (
    "emr4_context_fabric.session_binding_allows_v1(session_user, "
    "ARRAY['COORDINATOR'::emr4_context_fabric.logical_capability], practice_id, "
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
        raise RuntimeError("failure_037_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "d38e0bd5b2621bcea59d5397"
        and detail.get("scenario_id") == "BTR-E04"
        and detail.get("sqlstate") == "CF004"
        and detail.get("function_id")
        == "emr4_context_fabric.apply_durability_transition_v1"
        and detail.get("function_line") == 307
        and failure.get("scenario_reconciliation", {}).get("expected") == 20
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_037_not_closed")

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
        "admission_select_node",
    )
    branch_node = _one(
        [node for node in _walk(body) if node.get("node_id") == BRANCH_NODE_ID],
        "admission_branch_node",
    )
    failing_lock = _one(
        [node for node in _walk(body) if node.get("node_id") == FAILING_LOCK_NODE_ID],
        "admission_lock_node",
    )
    if not (
        select_node.get("op") == "SELECT_SET"
        and select_node.get("operands", {}).get("relation") == ADMISSION_RELATION
        and select_node.get("operands", {}).get("output_symbol") == "primary_set"
        and branch_node.get("op") == "IF"
        and failing_lock.get("op") == "LOCK_EXACT"
        and failing_lock.get("operands", {}).get("relation") == ADMISSION_RELATION
        and failing_lock.get("operands", {}).get("mode") == "FOR_UPDATE"
        and failing_lock.get("operands", {}).get("ordinal") == 5
        and failing_lock.get("operands", {}).get("output_symbol") == "primary"
    ):
        raise RuntimeError("admission_read_then_lock_contract")

    admission_locks = [
        node
        for node in _walk(body)
        if node.get("op") == "LOCK_EXACT"
        and node.get("operands", {}).get("relation") == ADMISSION_RELATION
    ]
    if not (
        len(admission_locks) == 3
        and sum(node["operands"].get("mode") == "FOR_UPDATE" for node in admission_locks)
        == 2
        and sum(node["operands"].get("mode") == "FOR_SHARE" for node in admission_locks)
        == 1
        and all(
            str(node.get("node_id", "")).startswith(
                "emr4_context_fabric.apply_durability_transition_v1."
            )
            for node in admission_locks
        )
    ):
        raise RuntimeError("admission_lock_population")

    policies = structural["rls_policy_catalogue"]["policies"]
    policy_ids = [row["id"] for row in policies]
    select_policy = _one(
        [row for row in policies if row.get("id") == SELECT_POLICY_ID],
        "admission_select_policy",
    )
    anchor_lock_policy = _one(
        [row for row in policies if row.get("id") == ANCHOR_LOCK_POLICY_ID],
        "anchor_lock_policy",
    )
    if not (
        select_policy.get("relation") == ADMISSION_RELATION_SHORT
        and select_policy.get("command") == "SELECT"
        and "'COORDINATOR'::" in select_policy.get("using_sql", "")
        and PROPOSED_LOCK_POLICY_ID not in policy_ids
        and anchor_lock_policy.get("command") == "UPDATE"
        and anchor_lock_policy.get("with_check_sql", "").endswith(" AND FALSE")
    ):
        raise RuntimeError("admission_lock_policy_gap")

    admission_relation = _one(
        [
            row
            for row in structural["relation_catalogue"]["relations"]
            if row.get("name") == ADMISSION_RELATION_SHORT
        ],
        "admission_relation",
    )
    if admission_relation.get("rls_policy_ids") != [
        SELECT_POLICY_ID,
        INSERT_POLICY_ID,
    ]:
        raise RuntimeError("admission_relation_policy_population")

    coordinator = _one(
        [row for row in structural["role_matrix"] if row.get("role") == "context_coordinator"],
        "coordinator_role",
    )
    if not (
        "apply_durability_transition_v1" in coordinator.get("execute_entry_points", [])
        and coordinator.get("direct_table_dml") == []
        and coordinator.get("nobypassrls") is True
    ):
        raise RuntimeError("coordinator_authority_boundary")

    sql_lines = inert_sql_bytes.decode("utf-8").splitlines()
    if not (
        sql_lines[956].startswith(
            "CREATE FUNCTION emr4_context_fabric.apply_durability_transition_v1"
        )
        and sql_lines[958] == "AS $durability_inert$"
        and "FROM emr4_context_fabric.context_proofread_observation_admission"
        in sql_lines[1261]
        and sql_lines[1261].endswith(" FOR UPDATE;")
        and "ERRCODE = 'CF004'" in sql_lines[1264]
        and 1262 - 956 + 1 == 307
    ):
        raise RuntimeError("postgresql_function_line_map")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-037-admission-lock-rls-diagnosis.v1",
        "status": "deterministic_admission_for_update_policy_gap_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 37,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E04",
            "sqlstate": "CF004",
            "function_line": 307,
            "mapped_sql_line": 1262,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "entry_point": "apply_durability_transition_v1",
            "principal": "context_coordinator",
            "plain_select_before_lock": SELECT_NODE_ID,
            "branch_before_lock": BRANCH_NODE_ID,
            "failing_lock": FAILING_LOCK_NODE_ID,
            "locked_relation": ADMISSION_RELATION,
            "lock_mode": "FOR_UPDATE",
            "admission_lock_node_count": len(admission_locks),
            "present_admission_policy_ids": [SELECT_POLICY_ID, INSERT_POLICY_ID],
            "missing_lock_policy_id": PROPOSED_LOCK_POLICY_ID,
            "append_only_lock_policy_precedent": ANCHOR_LOCK_POLICY_ID,
            "coordinator_direct_table_dml": [],
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "structural_source_sha256": "sha256:" + EXPECTED_STRUCTURAL_SOURCE_SHA256,
            "structural_contract_sha256": "sha256:" + EXPECTED_STRUCTURAL_CONTRACT_SHA256,
            "inert_sql_source_sha256": "sha256:" + EXPECTED_INERT_SQL_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "new_policy_id": PROPOSED_LOCK_POLICY_ID,
            "relation": ADMISSION_RELATION_SHORT,
            "command": "UPDATE",
            "using_capabilities": LOCK_CAPABILITIES,
            "using_sql": LOCK_USING_SQL,
            "with_check_sql": LOCK_USING_SQL + " AND FALSE",
            "coordinator_direct_table_dml_remains_empty": True,
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
