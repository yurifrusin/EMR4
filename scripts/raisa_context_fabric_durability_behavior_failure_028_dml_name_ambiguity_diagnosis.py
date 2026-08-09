"""Diagnose behavior failure 028 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-028.json"
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
RENDERER_PATH = (
    ROOT / "scripts/raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py"
)
SOURCE_HEAD = "ec79e095165d08354c946eb3c3f6202f491f522a"
EXPECTED_FAILURE_SHA256 = (
    "45ff02e01f9a05e46916617a6845cf8ad143a71ff1fff4a97bfc440c98e3d76c"
)
EXPECTED_ARTIFACT_SHA256 = (
    "64cbc2b0e17276387c6815af02a2d0635fc538e3408995c1054ecbc708b5cbae"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "b43ea059a3f424e268631228aa9606d30f1c9f082bc805e550788b01e7bd8e76"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "9b57d9d28f216e494da91715fcf7dfc7f49c80bbbe836fe0c685cd1dd4929268"
)
EXPECTED_RENDERER_SHA256 = (
    "367654e4e8822685c610cecc9efdc0335200e2d5f40fe2261b7716585c45b9ef"
)
PROGRAM_ID = "emr4_context_fabric.project_update_confirm_reschedule_v1"
INSERT_NODE_ID = PROGRAM_ID + ".p19"
OUTBOX_RELATION = "emr4_context_fabric.diary_context_observation_outbox_v1"
EXPECTED_COLLISIONS = ["aggregate_revision", "source_contract_digest"]


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
        raise RuntimeError("failure_028_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and detail.get("scenario_id") == "BTR-E02"
        and detail.get("sqlstate") == "42702"
        and detail.get("function_id") == PROGRAM_ID
        and detail.get("function_line") == 124
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_028_not_closed")

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
    statement = function_lines[122]
    returning = function_lines[123]
    if not (
        statement.startswith("    INSERT INTO " + OUTBOX_RELATION)
        and ", aggregate_revision, source_contract_digest, " in statement
        and returning.startswith("        RETURNING practice_id")
        and ", aggregate_revision, source_contract_digest, " in returning
    ):
        raise RuntimeError("function_line_124_not_unqualified_outbox_insert")

    body_bytes = _git_source_bytes(BODY_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    body = json.loads(body_bytes)
    if _canonical_digest(body) != EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    program = _exact(body["body_programs"], "id", PROGRAM_ID)
    insert = _exact(program["ast"]["nodes"], "node_id", INSERT_NODE_ID)
    if not (
        insert.get("op") == "INSERT"
        and insert["operands"].get("relation") == OUTBOX_RELATION
    ):
        raise RuntimeError("outbox_insert_contract_missing")
    local_ids = {symbol["id"] for symbol in program["symbols"]}
    value_collisions = sorted(
        binding["column"]
        for binding in insert["operands"]["bindings"]
        if binding["value"].get("op") == "REF"
        and binding["value"].get("kind") == "LOCAL"
        and binding["column"] == binding["value"].get("symbol")
    )
    returning_collisions = sorted(
        set(insert["operands"]["returning_columns"]) & local_ids
    )
    if not (
        value_collisions == EXPECTED_COLLISIONS
        and returning_collisions == EXPECTED_COLLISIONS
    ):
        raise RuntimeError("exact_dml_name_collisions_not_proven")

    renderer_bytes = _git_source_bytes(RENDERER_PATH)
    if _sha256(renderer_bytes) != EXPECTED_RENDERER_SHA256:
        raise RuntimeError("renderer_sha256")
    renderer = renderer_bytes.decode("utf-8")
    if not (
        'if kind in ("LOCAL", "INPUT"):\n        return _symbol_ident(expr["symbol"])'
        in renderer
        and 'returning = ", ".join(_ident(c) for c in ops["returning_columns"])'
        in renderer
    ):
        raise RuntimeError("unqualified_renderer_lowering_not_proven")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-028-dml-name-ambiguity-diagnosis.v1",
        "status": "deterministic_dml_local_column_ambiguity_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 28,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E02",
            "sqlstate": "42702",
            "function_id": PROGRAM_ID,
            "function_line": 124,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "insert_node_id": INSERT_NODE_ID,
            "relation": OUTBOX_RELATION,
            "value_name_collisions": value_collisions,
            "returning_name_collisions": returning_collisions,
            "local_references_block_qualified": False,
            "dml_returning_columns_target_qualified": False,
            "artifact_sha256": "sha256:" + EXPECTED_ARTIFACT_SHA256,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "renderer_source_sha256": "sha256:" + EXPECTED_RENDERER_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "outer_block_label": "cf_body",
            "local_reference_rendering": "block_qualified",
            "dml_returning_rendering": "target_relation_qualified",
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
