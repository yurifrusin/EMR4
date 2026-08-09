"""Diagnose behavior failure 027 without opening another PostgreSQL runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BEHAVIOR_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal"
)
FAILURE_PATH = (
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-027.json"
)
ARTIFACT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
    / "durability-schema.sql.inert"
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
SOURCE_HEAD = "1452147b67e641d2e25a267eca52c263cf669be0"
EXPECTED_FAILURE_SHA256 = (
    "6a19f12f87b98675ca12a580dc5113824e0312485b1663e3cd02a0a5e4642d43"
)
EXPECTED_ARTIFACT_SHA256 = (
    "f4479c772f144973c1a1f373e16e0bcb3543fea6128c8054a282316ce5d02714"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "78721338810c87df825bdf3a9d1e010cb3cdd04dcb7898badd127b76fec174d2"
)
EXPECTED_STRUCTURAL_SOURCE_SHA256 = (
    "648acf79c86d16bf7fcd9ad1f88dcab5bc4aded01c4e0084f66c6c36b4adeca1"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "6c4230c2d6c245087a789fbabb058dce4f6a42b747429ec8256ef0d994e5ad1b"
)
EXPECTED_STRUCTURAL_CONTRACT_SHA256 = (
    "a79be2598a3e3c5a8636ab8a1c16c06523ce9716d2387764cfecc1004ff5d14e"
)
PROGRAM_ID = "emr4_context_fabric.project_update_confirm_reschedule_v1"
LOCK_NODE_ID = PROGRAM_ID + ".p15"
ALIAS_RELATION = "diary_context_aggregate_aliases_v1"


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
    return result.stdout.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _exact(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    matches = [item for item in items if item.get(key) == value]
    if len(matches) != 1:
        raise RuntimeError(f"{value}_population")
    return matches[0]


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_027_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and detail.get("scenario_id") == "BTR-E02"
        and detail.get("sqlstate") == "CF004"
        and detail.get("function_id") == PROGRAM_ID
        and detail.get("function_line") == 107
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_027_not_closed")

    artifact_bytes = _git_source_bytes(ARTIFACT_PATH)
    if _sha256(artifact_bytes) != EXPECTED_ARTIFACT_SHA256:
        raise RuntimeError("artifact_sha256")
    artifact = artifact_bytes.decode("utf-8")
    function_start = artifact.index("CREATE FUNCTION " + PROGRAM_ID)
    function_end = artifact.index("$durability_inert$\nLANGUAGE", function_start)
    body_source = artifact[function_start:function_end].split(
        "AS $durability_inert$\n", 1
    )[1]
    function_lines = body_source.splitlines()
    if function_lines[105].strip() != (
        "RAISE EXCEPTION USING ERRCODE = 'CF004', "
        "MESSAGE = 'required_row_missing_or_ambiguous';"
    ):
        raise RuntimeError("function_line_107_not_cardinality_raise")
    lock_statement = function_lines[102]
    if not (
        "diary_context_aggregate_aliases_v1" in lock_statement
        and "INTO STRICT locked_alias" in lock_statement
        and lock_statement.endswith("FOR KEY SHARE;")
    ):
        raise RuntimeError("function_line_107_not_alias_lock_handler")

    body_bytes = _git_source_bytes(BODY_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    body = json.loads(body_bytes)
    if _canonical_digest(body) != EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    program = _exact(body["body_programs"], "id", PROGRAM_ID)
    lock = _exact(program["ast"]["nodes"], "node_id", LOCK_NODE_ID)
    if not (
        lock.get("op") == "LOCK_EXACT"
        and lock["operands"].get("relation") == "emr4_context_fabric." + ALIAS_RELATION
        and lock["operands"].get("mode") == "FOR_KEY_SHARE"
        and lock["operands"].get("ordinal") == 1
    ):
        raise RuntimeError("alias_lock_contract_missing")

    structural_bytes = _git_source_bytes(STRUCTURAL_PATH)
    if _sha256(structural_bytes) != EXPECTED_STRUCTURAL_SOURCE_SHA256:
        raise RuntimeError("structural_source_sha256")
    structural = json.loads(structural_bytes)
    if _canonical_digest(structural) != EXPECTED_STRUCTURAL_CONTRACT_SHA256:
        raise RuntimeError("structural_contract_sha256")
    alias = _exact(
        structural["relation_catalogue"]["relations"], "name", ALIAS_RELATION
    )
    policies = {
        policy["id"]: policy
        for policy in structural["rls_policy_catalogue"]["policies"]
    }
    alias_policies = [policies[policy_id] for policy_id in alias["rls_policy_ids"]]
    if not (
        alias["rls_forced"] is True
        and [policy["command"] for policy in alias_policies] == ["SELECT", "INSERT"]
        and not any(
            policy["relation"] == ALIAS_RELATION and policy["command"] == "UPDATE"
            for policy in policies.values()
        )
    ):
        raise RuntimeError("alias_update_visibility_gap_not_proven")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-027-alias-lock-visibility-diagnosis.v1",
        "status": "deterministic_alias_lock_update_policy_gap_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 27,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E02",
            "sqlstate": "CF004",
            "function_id": PROGRAM_ID,
            "function_line": 107,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "lock_node_id": LOCK_NODE_ID,
            "relation": "emr4_context_fabric." + ALIAS_RELATION,
            "row_lock_mode": "FOR_KEY_SHARE",
            "rls_forced": True,
            "existing_policy_commands": ["SELECT", "INSERT"],
            "applicable_update_using_policy_present": False,
            "postgresql_rule": "row_locking_select_requires_select_and_update_using_visibility",
            "artifact_sha256": "sha256:" + EXPECTED_ARTIFACT_SHA256,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "structural_source_sha256": "sha256:" + EXPECTED_STRUCTURAL_SOURCE_SHA256,
            "structural_contract_sha256": "sha256:"
            + EXPECTED_STRUCTURAL_CONTRACT_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "policy_change": "add_producer_scoped_alias_update_using_visibility_with_permanently_false_write_check",
            "direct_table_grant_change": False,
            "immutable_guard_change": False,
            "body_program_change": False,
            "scenario_change": False,
            "authority_change": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
