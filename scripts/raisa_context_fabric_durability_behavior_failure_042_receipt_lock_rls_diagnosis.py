"""Diagnose behavior failure 042 without opening another PostgreSQL runtime."""

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
FAILURE_PATH = BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-042.json"
EVIDENCE_PATH = BEHAVIOR_DIR / "provider-free-behavior-transaction-diagnosis-evidence-042.json"
MUTABLE_PATH = BEHAVIOR_DIR / "provider-free-behavior-transaction-evidence.json"
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

SOURCE_HEAD = "1b77505f8c6c20c8b37a4f8430f15649ecd13492"
EXPECTED_FAILURE_SHA256 = "88cd6fb34ffb07895dc9bc11c4712f64dedc24394e6befa04b70b09a7d3184d7"
EXPECTED_MUTABLE_SHA256 = "09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b"
EXPECTED_BODY_SOURCE_SHA256 = "c88653b1db1e379e9d067dbe444a1c2cbdf0dd1dd148fe838bce274741f7c455"
EXPECTED_BODY_CONTRACT_SHA256 = "9b079af00e46b5e18f464cc39f9283ce400ee7b2621d875a127af19cb908ee62"
EXPECTED_STRUCTURAL_SOURCE_SHA256 = "d333ad3ef75725a8a85e7d45a072bca02a087ea869d395459140c405919814c6"
EXPECTED_STRUCTURAL_CONTRACT_SHA256 = "30401808c97e45ad0ecf23242a21c1b7be35bc7d37343bb2f1ab4ef139e83a5f"
EXPECTED_INERT_SQL_SHA256 = "265ce41ec4c3b318cc42c544ab06ebb0fcc67904072b0f8406af4ec8ddec6b0a"

SELECT_NODE_ID = "emr4_context_fabric.apply_durability_transition_v1.receipt_set"
BRANCH_NODE_ID = "emr4_context_fabric.apply_durability_transition_v1.has_receipt"
LOCK_NODE_ID = "emr4_context_fabric.apply_durability_transition_v1.lock_receipt"
RELATION = "emr4_context_fabric.context_classified_observation_receipt"
RELATION_SHORT = "context_classified_observation_receipt"
SELECT_POLICY_ID = "pol_cf_09_select"
INSERT_POLICY_ID = "pol_cf_09_insert"
PROPOSED_LOCK_POLICY_ID = "pol_cf_09_update_lock"
PRECEDENT_POLICY_ID = "pol_cf_04_update_lock"
LOCK_POLICY_SQL = (
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
    result = subprocess.run(
        ["git", "show", f"{SOURCE_HEAD}:{path.relative_to(ROOT).as_posix()}"],
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


def build_evidence() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_042_sha256")
    if _sha256(MUTABLE_PATH.read_bytes()) != EXPECTED_MUTABLE_SHA256:
        raise RuntimeError("protected_mutable_evidence_not_restored")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "34bd47975bfc0ec2049dc7a9"
        and detail.get("scenario_id") == "BTR-I03"
        and detail.get("code") == "unexpected_rejection"
        and detail.get("sqlstate") == "CF004"
        and detail.get("function_id")
        == "emr4_context_fabric.apply_durability_transition_v1"
        and detail.get("function_line") == 210
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_042_not_closed")

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

    nodes = list(_walk(body))
    select_node = _one(
        [node for node in nodes if node.get("node_id") == SELECT_NODE_ID],
        "receipt_select_node",
    )
    branch_node = _one(
        [node for node in nodes if node.get("node_id") == BRANCH_NODE_ID],
        "receipt_branch_node",
    )
    lock_node = _one(
        [node for node in nodes if node.get("node_id") == LOCK_NODE_ID],
        "receipt_lock_node",
    )
    receipt_locks = [
        node
        for node in nodes
        if node.get("op") == "LOCK_EXACT"
        and node.get("operands", {}).get("relation") == RELATION
    ]
    if not (
        select_node.get("op") == "SELECT_SET"
        and select_node.get("operands", {}).get("relation") == RELATION
        and select_node.get("operands", {}).get("output_symbol") == "receipt_set"
        and branch_node.get("op") == "IF"
        and lock_node.get("op") == "LOCK_EXACT"
        and lock_node.get("operands", {}).get("relation") == RELATION
        and lock_node.get("operands", {}).get("mode") == "FOR_UPDATE"
        and lock_node.get("operands", {}).get("output_symbol") == "stored_receipt"
        and len(receipt_locks) == 1
    ):
        raise RuntimeError("receipt_read_then_lock_contract")

    policies = structural["rls_policy_catalogue"]["policies"]
    policy_ids = [row["id"] for row in policies]
    select_policy = _one(
        [row for row in policies if row.get("id") == SELECT_POLICY_ID],
        "receipt_select_policy",
    )
    precedent = _one(
        [row for row in policies if row.get("id") == PRECEDENT_POLICY_ID],
        "lock_policy_precedent",
    )
    if not (
        select_policy.get("relation") == RELATION_SHORT
        and select_policy.get("command") == "SELECT"
        and "'COORDINATOR'::" in select_policy.get("using_sql", "")
        and PROPOSED_LOCK_POLICY_ID not in policy_ids
        and precedent.get("command") == "UPDATE"
        and precedent.get("with_check_sql", "").endswith(" AND FALSE")
    ):
        raise RuntimeError("receipt_lock_policy_gap")

    relation = _one(
        [
            row
            for row in structural["relation_catalogue"]["relations"]
            if row.get("name") == RELATION_SHORT
        ],
        "receipt_relation",
    )
    if relation.get("rls_policy_ids") != [SELECT_POLICY_ID, INSERT_POLICY_ID]:
        raise RuntimeError("receipt_relation_policy_population")

    coordinator = _one(
        [
            row
            for row in structural["role_matrix"]
            if row.get("role") == "context_coordinator"
        ],
        "coordinator_role",
    )
    if not (
        "apply_durability_transition_v1"
        in coordinator.get("execute_entry_points", [])
        and coordinator.get("direct_table_dml") == []
        and coordinator.get("nobypassrls") is True
    ):
        raise RuntimeError("coordinator_authority_boundary")

    sql_lines = inert_sql_bytes.decode("utf-8").splitlines()
    mapped_line = sql_lines[1170]
    if not (
        "ERRCODE = 'CF004'" in mapped_line
        and 1171 - 962 + 1 == 210
        and "context_classified_observation_receipt" in sql_lines[1167]
        and sql_lines[1167].endswith(" FOR UPDATE;")
    ):
        raise RuntimeError("postgresql_function_line_map")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-042-receipt-lock-rls-diagnosis.v1",
        "status": "deterministic_receipt_for_update_policy_gap_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 42,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-I03",
            "sqlstate": "CF004",
            "function_line": 210,
            "mapped_sql_line": 1171,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "entry_point": "apply_durability_transition_v1",
            "principal": "context_coordinator",
            "plain_select_before_lock": SELECT_NODE_ID,
            "branch_before_lock": BRANCH_NODE_ID,
            "failing_lock": LOCK_NODE_ID,
            "locked_relation": RELATION,
            "lock_mode": "FOR_UPDATE",
            "present_receipt_policy_ids": [SELECT_POLICY_ID, INSERT_POLICY_ID],
            "missing_lock_policy_id": PROPOSED_LOCK_POLICY_ID,
            "append_only_lock_policy_precedent": PRECEDENT_POLICY_ID,
            "coordinator_direct_table_dml": [],
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "structural_source_sha256": "sha256:" + EXPECTED_STRUCTURAL_SOURCE_SHA256,
            "structural_contract_sha256": "sha256:" + EXPECTED_STRUCTURAL_CONTRACT_SHA256,
            "inert_sql_source_sha256": "sha256:" + EXPECTED_INERT_SQL_SHA256,
            "additional_container_runs": 0,
            "raw_postgresql_error_persisted": False,
        },
        "bounded_repair": {
            "new_policy_id": PROPOSED_LOCK_POLICY_ID,
            "relation": RELATION_SHORT,
            "command": "UPDATE",
            "using_capabilities": ["COORDINATOR"],
            "using_sql": LOCK_POLICY_SQL,
            "with_check_sql": LOCK_POLICY_SQL + " AND FALSE",
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


def write_json_lf(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    evidence = build_evidence()
    write_json_lf(EVIDENCE_PATH, evidence)
    print(json.dumps(evidence, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
