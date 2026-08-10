"""Diagnose behavior failure 035 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-035.json"
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

SOURCE_HEAD = "4385dfcb926109b6e8c310e075a2e1c5e5c543cc"
EXPECTED_FAILURE_SHA256 = (
    "9ee9265487f0c14ea7987f979166e6b900241cbb820a9faa522eab14aea0d7d5"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "985120aaa63ed665b6cf7acebf57dfa9feebe1bfeb74add3b025c17b9149f7f7"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "d60eb4bd018a5f9180985db10f9b18c92d797b45844fbba345871085da4834c3"
)
EXPECTED_STRUCTURAL_SOURCE_SHA256 = (
    "5b5e3bc3108dc1105017f57ceade03c4bce33b898d7b71f0ede0640ce0bc83c7"
)
EXPECTED_INERT_SQL_SHA256 = (
    "ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb"
)
LOCK_NODE_ID = "emr4_context_fabric.apply_durability_transition_v1.lock_generation"
UPDATE_POLICY_ID = "pol_cf_06_update"
LIFECYCLE_ONLY_SQL = (
    "emr4_context_fabric.session_binding_allows_v1(session_user, "
    "ARRAY['LIFECYCLE'::emr4_context_fabric.logical_capability], practice_id, "
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
        raise RuntimeError("failure_035_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "3456f41a72c5cb413f9dcb06"
        and detail.get("scenario_id") == "BTR-E04"
        and detail.get("sqlstate") == "CF004"
        and detail.get("function_id")
        == "emr4_context_fabric.apply_durability_transition_v1"
        and detail.get("function_line") == 143
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_035_not_closed")

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

    lock_node = _one(
        [node for node in _walk(body) if node.get("node_id") == LOCK_NODE_ID],
        "lock_node",
    )
    lock_operands = lock_node.get("operands", {})
    if not (
        lock_node.get("op") == "LOCK_EXACT"
        and lock_operands.get("relation")
        == "emr4_context_fabric.context_observer_generation"
        and lock_operands.get("mode") == "FOR_UPDATE"
        and lock_operands.get("ordinal") == 2
    ):
        raise RuntimeError("generation_lock_contract")

    policy = _one(
        [
            row
            for row in structural["rls_policy_catalogue"]["policies"]
            if row.get("id") == UPDATE_POLICY_ID
        ],
        "generation_update_policy",
    )
    if not (
        policy.get("relation") == "context_observer_generation"
        and policy.get("command") == "UPDATE"
        and policy.get("using_sql") == LIFECYCLE_ONLY_SQL
        and policy.get("with_check_sql") == LIFECYCLE_ONLY_SQL
    ):
        raise RuntimeError("generation_update_policy_definition")

    coordinator = _one(
        [
            row
            for row in structural["role_matrix"]
            if row.get("role") == "context_coordinator"
        ],
        "coordinator_role",
    )
    if not (
        "apply_durability_transition_v1" in coordinator.get("execute_entry_points", [])
        and coordinator.get("direct_table_dml") == []
        and coordinator.get("nobypassrls") is True
    ):
        raise RuntimeError("coordinator_authority_boundary")

    inert_sql = inert_sql_bytes.decode("utf-8")
    generation_lock_lines = [
        line
        for line in inert_sql.splitlines()
        if line.startswith("SELECT ")
        and "FROM emr4_context_fabric.context_observer_generation" in line
        and line.rstrip().endswith("FOR UPDATE;")
    ]
    if len(generation_lock_lines) < 3:
        raise RuntimeError("generation_for_update_population")
    generation_updates = [
        node
        for node in _walk(body)
        if node.get("op") == "UPDATE"
        and "context_observer_generation" in json.dumps(node, sort_keys=True)
        and str(node.get("node_id", "")).startswith(
            "emr4_context_fabric.apply_durability_transition_v1."
        )
    ]
    if len(generation_updates) != 10:
        raise RuntimeError("coordinator_generation_update_population")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-035-generation-lock-rls-diagnosis.v1",
        "status": "deterministic_coordinator_generation_update_policy_mismatch_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 35,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E04",
            "sqlstate": "CF004",
            "function_line": 143,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "entry_point": "apply_durability_transition_v1",
            "principal": "context_coordinator",
            "locked_relation": "context_observer_generation",
            "lock_mode": "FOR_UPDATE",
            "lock_node": LOCK_NODE_ID,
            "generation_update_policy": UPDATE_POLICY_ID,
            "policy_using_capabilities": ["LIFECYCLE"],
            "policy_with_check_capabilities": ["LIFECYCLE"],
            "required_existing_capability": "COORDINATOR",
            "coordinator_generation_update_node_count": len(generation_updates),
            "coordinator_direct_table_dml": [],
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "structural_source_sha256": "sha256:" + EXPECTED_STRUCTURAL_SOURCE_SHA256,
            "inert_sql_source_sha256": "sha256:" + EXPECTED_INERT_SQL_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "generation_update_policy_using_capabilities": [
                "COORDINATOR",
                "LIFECYCLE",
            ],
            "generation_update_policy_with_check_capabilities": [
                "COORDINATOR",
                "LIFECYCLE",
            ],
            "coordinator_direct_table_dml_remains_empty": True,
            "entry_point_execute_grant_unchanged": True,
            "body_program_change": False,
            "inert_artifact_regeneration": True,
            "parse_catalogue_rebind_required": True,
            "behavior_parent_rebind_required": True,
            "scenario_population_change": False,
            "principal_or_sqlstate_change": False,
            "new_external_authority": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
