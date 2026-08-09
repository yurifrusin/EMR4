"""Diagnose behavior failure 026 without opening another PostgreSQL runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Iterator

from scripts import (
    raisa_provider_free_unmounted_durability_inert_ddl_rehearsal as renderer,
)


ROOT = Path(__file__).resolve().parents[1]
BEHAVIOR_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal"
)
FAILURE_PATH = (
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-026.json"
)
BODY_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-function-trigger-body-architecture"
    / "function-trigger-body-architecture-contract.json"
)
ARTIFACT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
    / "durability-schema.sql.inert"
)
EXPECTED_FAILURE_SHA256 = (
    "6365e2f52a08f45a564764a280b2fe83ac3cae8bd2dd0af31708a1696231c56a"
)
EXPECTED_ARTIFACT_SHA256 = (
    "eeabfc39bf0b0c1073f57e97835440b394391161bec3ddc62be6e186fd7af6d8"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "78721338810c87df825bdf3a9d1e010cb3cdd04dcb7898badd127b76fec174d2"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "6c4230c2d6c245087a789fbabb058dce4f6a42b747429ec8256ef0d994e5ad1b"
)
ARTIFACT_SOURCE_HEAD = "c97ea3eb935997ace3586aa2ff52cf33dabbfd6a"
BODY_SOURCE_HEAD = "987f64a9f68c8dec2b99d5d39aa74e28411a82fa"
PREDECESSOR_RENDERER_VERSION = "2.0.12"
PROGRAM_ID = "emr4_context_fabric.project_update_confirm_reschedule_v1"
ASSERT_NODE_ID = PROGRAM_ID + ".p12"


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


def _git_source_bytes(source_head: str, path: Path) -> bytes:
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"{source_head}:{relative}"],
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


def _program(body: dict[str, Any]) -> dict[str, Any]:
    matches = [item for item in body["body_programs"] if item.get("id") == PROGRAM_ID]
    if len(matches) != 1:
        raise RuntimeError("producer_program_population")
    return matches[0]


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_026_sha256")
    failure = json.loads(failure_bytes)
    failure_detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure_detail.get("scenario_id") == "BTR-E02"
        and failure_detail.get("sqlstate") == "CF103"
        and failure_detail.get("function_id") == PROGRAM_ID
        and failure_detail.get("function_line") == 85
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_026_not_closed")

    artifact_bytes = _git_source_bytes(ARTIFACT_SOURCE_HEAD, ARTIFACT_PATH)
    if _sha256(artifact_bytes) != EXPECTED_ARTIFACT_SHA256:
        raise RuntimeError("artifact_sha256")
    artifact = artifact_bytes.decode("utf-8")
    function_start = artifact.index("CREATE FUNCTION " + PROGRAM_ID)
    function_end = artifact.index("$durability_inert$\nLANGUAGE", function_start)
    function_text = artifact[function_start:function_end]
    body_source = function_text.split("AS $durability_inert$\n", 1)[1]
    function_lines = body_source.splitlines()
    # PostgreSQL counts the newline immediately after the dollar-quote opener
    # as line one; the decoded body below starts at DECLARE.
    if function_lines[83].strip() != (
        "RAISE EXCEPTION USING ERRCODE = 'CF103', "
        "MESSAGE = 'producer_membership_mismatch';"
    ):
        raise RuntimeError("function_line_85_not_membership_raise")
    if "pg_catalog.jsonb_object_keys(event.payload)" not in function_lines[82]:
        raise RuntimeError("function_line_85_not_json_membership_assertion")

    body_bytes = _git_source_bytes(BODY_SOURCE_HEAD, BODY_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    body = json.loads(body_bytes)
    if renderer.canonical_digest(body) != "sha256:" + EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    program = _program(body)
    assertions = [
        node
        for node in program["ast"]["nodes"]
        if node.get("node_id") == ASSERT_NODE_ID
    ]
    if (
        len(assertions) != 1
        or assertions[0].get("operands", {}).get("failure_id") != "F_MEMBERSHIP"
    ):
        raise RuntimeError("producer_event_assertion_population")
    key_checks = [
        node for node in _walk(assertions[0]) if node.get("op") == "JSON_KEYS_EXACT"
    ]
    if len(key_checks) != 1:
        raise RuntimeError("json_keys_exact_population")
    key_check = key_checks[0]
    declared_keys = key_check["keys"]
    sorted_keys = sorted(declared_keys)
    rendered = function_lines[82]
    declared_sql = "ARRAY[" + ", ".join(repr(key) for key in declared_keys) + "]"
    sorted_sql = "ARRAY[" + ", ".join(repr(key) for key in sorted_keys) + "]"
    if not (
        "pg_catalog.array_agg(k.k ORDER BY k.k)" in rendered
        and declared_keys != sorted_keys
        and declared_sql in rendered
        and sorted_sql not in rendered
    ):
        raise RuntimeError("json_keys_order_mismatch_not_proven")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-026-json-keys-order-diagnosis.v1",
        "status": "deterministic_json_key_order_mismatch_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 26,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E02",
            "sqlstate": "CF103",
            "function_id": PROGRAM_ID,
            "function_line": 85,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "assert_node_id": ASSERT_NODE_ID,
            "failure_id": "F_MEMBERSHIP",
            "expression_opcode": "JSON_KEYS_EXACT",
            "actual_key_order_rule": "lexicographic_ascending",
            "declared_expected_keys": declared_keys,
            "actual_ordered_keys": sorted_keys,
            "orders_equal": False,
            "renderer_version": PREDECESSOR_RENDERER_VERSION,
            "artifact_sha256": "sha256:" + EXPECTED_ARTIFACT_SHA256,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "renderer_change": "canonicalize_fixed_expected_json_keys_to_lexicographic_order",
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
