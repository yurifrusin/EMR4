"""Diagnose behavior failure 038 without opening another PostgreSQL runtime."""

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
FAILURE_PATH = BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-038.json"
RECEIPT_PATH = BEHAVIOR_DIR / "provider-free-behavior-transaction-diagnosis-evidence-038.json"
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

SOURCE_HEAD = "810a9dc11bdb39f76f70a6b65cb8afe10732e612"
EXPECTED_FAILURE_SHA256 = "68ebd0c6973c65048b8d1c73bc86573e4b6614587001b81b3ab2f396fd7f2f2d"
EXPECTED_FAILURE_DETAIL_SHA256 = (
    "a5a65d0eb099d7e6c2d72aaa2f3a58bc27f445b2def058cf1419e0a087d5a78f"
)
EXPECTED_BODY_SOURCE_SHA256 = "d9c7b60fa13c02d4b04f8cf68c73ae43dc0acc820a51b4a96ae8a2aed9c137c7"
EXPECTED_BODY_CONTRACT_SHA256 = "8124957e32657076c3befc96a7b5e8770dcd37fcb5b91e33c136f01cbf2dd5ea"
EXPECTED_STRUCTURAL_SOURCE_SHA256 = "1e127029e120879ec10031ffbb07d14ab386f4ce6861571f2d113e7f9fa7ef9c"
EXPECTED_STRUCTURAL_CONTRACT_SHA256 = "80d5b57eadef0e6ede54c48fc842fe5567723c0a9cdebe288efbf63048c4b3ac"
EXPECTED_INERT_SQL_SHA256 = "1ab976d0555021aa6ec41778b2c3de6ef27105f17f8d1d941b714006da93b1d5"
SCENARIO_ID = "BTR-E04"
SOURCE_SELECT_NODE_ID = (
    "emr4_context_fabric.apply_durability_transition_v1.source_position_set"
)
SOURCE_BRANCH_NODE_ID = (
    "emr4_context_fabric.apply_durability_transition_v1.source_position_exact"
)
REBASE_MUTATION_NODE_ID = (
    "emr4_context_fabric.apply_durability_transition_v1."
    "rebase_generation.source_ambiguous"
)
REBASE_RESULT_NODE_ID = (
    "emr4_context_fabric.apply_durability_transition_v1."
    "rebase_result.source_ambiguous"
)
OUTBOX_RELATION = "emr4_context_fabric.diary_context_observation_outbox_v1"
OUTBOX_RELATION_SHORT = "diary_context_observation_outbox_v1"
OUTBOX_SELECT_POLICY_ID = "pol_cf_03_select"
CURRENT_SELECT_CAPABILITIES = ["PRODUCER", "OBSERVER", "RETENTION"]
REPAIRED_SELECT_CAPABILITIES = ["PRODUCER", "OBSERVER", "COORDINATOR", "RETENTION"]


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


def _policy_capabilities(using_sql: str) -> list[str]:
    return [
        name
        for name in (
            "PRODUCER",
            "OBSERVER",
            "COORDINATOR",
            "LIFECYCLE",
            "RETENTION",
            "APPLICATION_READ",
        )
        if f"'{name}'::emr4_context_fabric.logical_capability" in using_sql
    ]


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_038_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    expected_detail = f"{SCENARIO_ID}:{OUTBOX_RELATION.replace('diary_context_observation_outbox_v1', 'context_observer_generation')}"
    if _sha256(expected_detail.encode("utf-8")) != EXPECTED_FAILURE_DETAIL_SHA256:
        raise RuntimeError("failure_038_detail_binding")
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "2171447fafa976485041ae03"
        and detail.get("stage") == "readback"
        and detail.get("code") == "forbidden_relation_change"
        and detail.get("detail_digest")
        == "sha256:" + EXPECTED_FAILURE_DETAIL_SHA256
        and failure.get("scenario_reconciliation", {}).get("expected") == 20
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("removed") is True
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_038_not_closed")

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

    source_select = _one(
        [node for node in _walk(body) if node.get("node_id") == SOURCE_SELECT_NODE_ID],
        "source_select_node",
    )
    source_branch = _one(
        [node for node in _walk(body) if node.get("node_id") == SOURCE_BRANCH_NODE_ID],
        "source_branch_node",
    )
    rebase_mutation = _one(
        [node for node in _walk(body) if node.get("node_id") == REBASE_MUTATION_NODE_ID],
        "source_rebase_mutation_node",
    )
    rebase_result = _one(
        [node for node in _walk(body) if node.get("node_id") == REBASE_RESULT_NODE_ID],
        "source_rebase_result_node",
    )
    result_bytes = json.dumps(rebase_result, sort_keys=True).encode("utf-8")
    if not (
        source_select.get("op") == "SELECT_SET"
        and source_select.get("operands", {}).get("relation") == OUTBOX_RELATION
        and source_select.get("operands", {}).get("output_symbol")
        == "source_position_set"
        and source_branch.get("op") == "IF"
        and rebase_mutation.get("op") == "UPDATE"
        and rebase_mutation.get("operands", {}).get("relation")
        == "emr4_context_fabric.context_observer_generation"
        and b'"REBASE_APPLIED"' in result_bytes
    ):
        raise RuntimeError("source_visibility_rebase_path")

    relation = _one(
        [
            row
            for row in structural["relation_catalogue"]["relations"]
            if row.get("name") == OUTBOX_RELATION_SHORT
        ],
        "outbox_relation",
    )
    policy = _one(
        [
            row
            for row in structural["rls_policy_catalogue"]["policies"]
            if row.get("id") == OUTBOX_SELECT_POLICY_ID
        ],
        "outbox_select_policy",
    )
    present_capabilities = _policy_capabilities(policy.get("using_sql", ""))
    if not (
        relation.get("rls_enabled") is True
        and relation.get("rls_forced") is True
        and policy.get("relation") == OUTBOX_RELATION_SHORT
        and policy.get("command") == "SELECT"
        and policy.get("roles") == ["PUBLIC"]
        and policy.get("permissive") is True
        and present_capabilities == CURRENT_SELECT_CAPABILITIES
        and "'COORDINATOR'::" not in policy.get("using_sql", "")
    ):
        raise RuntimeError("outbox_coordinator_select_policy_gap")

    coordinator = _one(
        [row for row in structural["role_matrix"] if row.get("role") == "context_coordinator"],
        "coordinator_role",
    )
    if not (
        "apply_durability_transition_v1" in coordinator.get("execute_entry_points", [])
        and coordinator.get("direct_table_select") == []
        and coordinator.get("direct_table_dml") == []
        and coordinator.get("nobypassrls") is True
    ):
        raise RuntimeError("coordinator_authority_boundary")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-038-outbox-rls-diagnosis.v1",
        "status": "deterministic_coordinator_outbox_select_policy_gap_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 38,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": SCENARIO_ID,
            "failure_code": "forbidden_relation_change",
            "changed_relation": "emr4_context_fabric.context_observer_generation",
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "entry_point": "apply_durability_transition_v1",
            "principal": "context_coordinator",
            "source_select_node": SOURCE_SELECT_NODE_ID,
            "source_exactness_branch": SOURCE_BRANCH_NODE_ID,
            "forced_rls_relation": OUTBOX_RELATION,
            "select_policy_id": OUTBOX_SELECT_POLICY_ID,
            "present_select_capabilities": present_capabilities,
            "missing_required_capability": "COORDINATOR",
            "resulting_mutation_node": REBASE_MUTATION_NODE_ID,
            "resulting_transition_kind": "REBASE_APPLIED",
            "coordinator_direct_table_select": [],
            "coordinator_direct_table_dml": [],
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "structural_source_sha256": "sha256:" + EXPECTED_STRUCTURAL_SOURCE_SHA256,
            "structural_contract_sha256": "sha256:" + EXPECTED_STRUCTURAL_CONTRACT_SHA256,
            "inert_sql_source_sha256": "sha256:" + EXPECTED_INERT_SQL_SHA256,
            "raw_postgresql_values_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "policy_id": OUTBOX_SELECT_POLICY_ID,
            "relation": OUTBOX_RELATION_SHORT,
            "command": "SELECT",
            "present_capabilities": CURRENT_SELECT_CAPABILITIES,
            "repaired_capabilities": REPAIRED_SELECT_CAPABILITIES,
            "direct_relation_grants_unchanged": True,
            "runtime_role_dml_unchanged": True,
            "forced_rls_unchanged": True,
            "function_body_semantics_unchanged": True,
            "statement_population_unchanged": True,
            "exact_result_kind_assertion_required": {
                "BTR-E04": "RECEIPT_APPLIED",
                "BTR-I03": "RECEIPT_REPLAYED",
            },
            "inert_artifact_regeneration": True,
            "parse_catalogue_rebind_required": True,
            "behavior_parent_rebind_required": True,
            "scenario_population_change": False,
            "new_external_authority": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


if __name__ == "__main__":
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
