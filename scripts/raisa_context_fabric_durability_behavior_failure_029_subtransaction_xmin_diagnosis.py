"""Diagnose behavior failure 029 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-029.json"
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
SOURCE_HEAD = "09c3e445f6514293d1ee27011b687c402605bd47"
EXPECTED_FAILURE_SHA256 = (
    "09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b"
)
EXPECTED_ARTIFACT_SHA256 = (
    "b2e476995848b64d819ae6c545d5b8c9b93707288993a0120d09d19c503230dc"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "b43ea059a3f424e268631228aa9606d30f1c9f082bc805e550788b01e7bd8e76"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "9b57d9d28f216e494da91715fcf7dfc7f49c80bbbe836fe0c685cd1dd4929268"
)
EXPECTED_RENDERER_SHA256 = (
    "d4e52e333e70c58bbbd671851cf2014f0b2f34bca1cbf0d855a8a06c946a584a"
)
PROGRAM_ID = "emr4_context_fabric.project_update_confirm_reschedule_v1"
UPDATE_NODE_ID = PROGRAM_ID + ".p20"
HEAD_RELATION = "emr4_context_fabric.context_observation_stream_head"
HEAD_KEY_COLUMNS = ["practice_id", "source_contract_id", "stream_id"]
POSTGRESQL_REFERENCES = [
    "https://www.postgresql.org/docs/16/plpgsql-structure.html",
    "https://www.postgresql.org/docs/16/subxacts.html",
    "https://www.postgresql.org/docs/16/functions-info.html",
    "https://www.postgresql.org/docs/16/ddl-system-columns.html",
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def _walk(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for node in nodes:
        found.append(node)
        operands = node.get("operands", {})
        for name in ("then", "else", "nodes"):
            child = operands.get(name)
            if isinstance(child, list):
                found.extend(_walk(child))
        for arm in operands.get("arms", []):
            if isinstance(arm, dict) and isinstance(arm.get("nodes"), list):
                found.extend(_walk(arm["nodes"]))
    return found


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_029_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and detail.get("scenario_id") == "BTR-E02"
        and detail.get("sqlstate") == "CF603"
        and "function_id" not in detail
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_029_not_closed")

    artifact_bytes = _git_source_bytes(ARTIFACT_PATH)
    if _sha256(artifact_bytes) != EXPECTED_ARTIFACT_SHA256:
        raise RuntimeError("artifact_sha256")
    artifact = artifact_bytes.decode("utf-8")
    function_start = artifact.index("CREATE FUNCTION " + PROGRAM_ID)
    function_end = artifact.index("$durability_inert$\nLANGUAGE", function_start)
    function_sql = artifact[function_start:function_end]
    head_update = (
        "    BEGIN\nUPDATE emr4_context_fabric.context_observation_stream_head SET "
    )
    update_start = function_sql.index(head_update)
    update_end = function_sql.index("    END;", update_start) + len("    END;")
    update_block = function_sql[update_start:update_end]
    if not (
        " RETURNING " + HEAD_RELATION + ".practice_id" in update_block
        and " INTO STRICT updated_head;" in update_block
        and "\n    EXCEPTION\n" in update_block
        and "WHEN NO_DATA_FOUND THEN" in update_block
        and "WHEN TOO_MANY_ROWS THEN" in update_block
    ):
        raise RuntimeError("head_update_exception_subtransaction_not_proven")
    if (
        "ALTER TABLE "
        + HEAD_RELATION
        + " ADD CONSTRAINT pk_cf_01 PRIMARY KEY (practice_id, source_contract_id, stream_id);"
        not in artifact
    ):
        raise RuntimeError("head_update_unique_key_not_proven")
    if not (
        "cf_body.head.xmin = ((((pg_catalog.pg_current_xact_id()::pg_catalog.text)"
        in artifact
        and "ERRCODE = 'CF603', MESSAGE = 'temporal_bijection_invalid'" in artifact
    ):
        raise RuntimeError("top_level_xid_fence_not_proven")

    body_bytes = _git_source_bytes(BODY_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    body = json.loads(body_bytes)
    if body.get("contract_sha256") != "sha256:" + EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    program = _exact(body["body_programs"], "id", PROGRAM_ID)
    update = _exact(_walk(program["ast"]["nodes"]), "node_id", UPDATE_NODE_ID)
    if not (
        update.get("op") == "UPDATE"
        and update["operands"].get("relation") == HEAD_RELATION
        and update["operands"].get("key_columns") == HEAD_KEY_COLUMNS
        and update["operands"].get("affected_cardinality") == "EXACTLY_ONE"
        and update["operands"].get("output_symbol") == "updated_head"
    ):
        raise RuntimeError("head_update_contract_not_proven")

    renderer_bytes = _git_source_bytes(RENDERER_PATH)
    if _sha256(renderer_bytes) != EXPECTED_RENDERER_SHA256:
        raise RuntimeError("renderer_sha256")
    renderer = renderer_bytes.decode("utf-8")
    emit_start = renderer.index("def _emit_update(")
    emit_end = renderer.index("\ndef _emit_delete_source(", emit_start)
    update_renderer = renderer[emit_start:emit_end]
    exact_start = renderer.index("def _exactly_one_block(")
    exact_end = renderer.index("\ndef _emit_select_exact(", exact_start)
    exactly_one_renderer = renderer[exact_start:exact_end]
    if not (
        "INTO STRICT " in update_renderer
        and 'return [_exactly_one_block(body, indent) + ";"]' in update_renderer
        and ' + "EXCEPTION\\n"' in exactly_one_renderer
    ):
        raise RuntimeError("renderer_update_subtransaction_lowering_not_proven")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-029-subtransaction-xmin-diagnosis.v1",
        "status": "deterministic_update_subtransaction_xmin_mismatch_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 29,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E02",
            "sqlstate": "CF603",
            "completed_scenarios": 0,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "program_id": PROGRAM_ID,
            "update_node_id": UPDATE_NODE_ID,
            "relation": HEAD_RELATION,
            "unique_key_columns": HEAD_KEY_COLUMNS,
            "write_inside_exception_block": True,
            "exception_block_forms_subtransaction": True,
            "writing_subtransaction_receives_subxid": True,
            "row_version_xmin_records_writing_subxid": True,
            "pg_current_xact_id_returns_top_level_xid": True,
            "deferred_fence_requires_head_xmin_equal_top_level_xid": True,
            "artifact_sha256": "sha256:" + EXPECTED_ARTIFACT_SHA256,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "renderer_source_sha256": "sha256:" + EXPECTED_RENDERER_SHA256,
            "postgresql_primary_references": POSTGRESQL_REFERENCES,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "update_rendering": "direct_uniquely_keyed_update_returning_into_without_exception_subtransaction",
            "zero_row_mapping": "found_check_to_cf004",
            "multiple_row_prevention": "renderer_verified_primary_or_unique_key",
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
