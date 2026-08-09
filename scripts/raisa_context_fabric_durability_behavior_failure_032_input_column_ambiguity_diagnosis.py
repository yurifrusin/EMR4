"""Diagnose behavior failure 032 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-032.json"
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
SOURCE_HEAD = "0619300b106c0b9bfec0833a666bc1a5ff325f80"
EXPECTED_FAILURE_SHA256 = (
    "8eb6932691a2ed26780b49f22ca760f8760b54a0befa86bb4f4bf4d68d4392fc"
)
EXPECTED_ARTIFACT_SHA256 = (
    "1d53c7ac1cd9a9fb19faafcca0ebcf8dacadf238f62df873d2d3fc78c657b407"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "01f92356def997b96adb3115cfb4b82afc29a27e72cab5823c81a6b5f2e2a7f1"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "edbc7f2361f8b5a2812dcff2a7cdf81bef7bd2a6d280be5a9023571c5121508e"
)
EXPECTED_RENDERER_SHA256 = (
    "99ffd457f73f9517777f1565b4ab18baa0828434eb661aa7722fed3283cb1a2b"
)
PROGRAM_ID = "emr4_context_fabric.admit_proofread_observation_v1"
INPUT_ID = "source_position"
EXPECTED_COLLISION_NODES = [
    PROGRAM_ID + ".conflict_set",
    PROGRAM_ID + ".primary_set",
    PROGRAM_ID + ".receipt_set",
]


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


def _walk(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _has_input_column_collision(node: dict[str, Any]) -> bool:
    for candidate in _walk(node.get("operands", {}).get("predicate", {})):
        if candidate.get("op") != "EQ":
            continue
        pair = [candidate.get("left", {}), candidate.get("right", {})]
        source = next(
            (
                item
                for item in pair
                if item.get("op") == "REF"
                and item.get("kind") == "SOURCE_COLUMN"
                and item.get("column") == INPUT_ID
            ),
            None,
        )
        input_ref = next(
            (
                item
                for item in pair
                if item.get("op") == "REF"
                and item.get("kind") == "INPUT"
                and item.get("symbol") == INPUT_ID
            ),
            None,
        )
        if source is not None and input_ref is not None:
            return True
    return False


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_032_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "38f0540820e100bf9cd9c239"
        and detail.get("scenario_id") == "BTR-E03"
        and detail.get("sqlstate") == "42702"
        and detail.get("function_id") == PROGRAM_ID
        and detail.get("function_line") == 35
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_032_not_closed")

    artifact_bytes = _git_source_bytes(ARTIFACT_PATH)
    if _sha256(artifact_bytes) != EXPECTED_ARTIFACT_SHA256:
        raise RuntimeError("artifact_sha256")
    artifact = artifact_bytes.decode("utf-8")
    function_start = artifact.index("CREATE FUNCTION " + PROGRAM_ID)
    function_end = artifact.index("$durability_inert$\nLANGUAGE", function_start)
    function_lines = (
        artifact[function_start:function_end]
        .split("AS $durability_inert$\n", 1)[1]
        .splitlines()
    )
    ambiguous_predicates = {
        str(line_no): function_lines[line_no - 1].count(
            ".source_position = source_position"
        )
        for line_no in (36, 39, 42)
    }
    if not (
        function_lines[33].lstrip().startswith("SELECT COALESCE(")
        and ambiguous_predicates == {"36": 1, "39": 1, "42": 1}
    ):
        raise RuntimeError("function_line_35_select_ambiguity_not_proven")

    body_bytes = _git_source_bytes(BODY_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    body = json.loads(body_bytes)
    if _canonical_digest(body) != EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    program = _exact(body["body_programs"], "id", PROGRAM_ID)
    input_symbol = _exact(program["symbols"], "id", INPUT_ID)
    if input_symbol.get("source") != {"kind": "INPUT"}:
        raise RuntimeError("source_position_not_input")
    collision_nodes = sorted(
        node["node_id"]
        for node in program["ast"]["nodes"]
        if node.get("op") == "SELECT_SET" and _has_input_column_collision(node)
    )
    if collision_nodes != EXPECTED_COLLISION_NODES:
        raise RuntimeError("exact_select_input_column_collisions_not_proven")

    renderer_bytes = _git_source_bytes(RENDERER_PATH)
    if _sha256(renderer_bytes) != EXPECTED_RENDERER_SHA256:
        raise RuntimeError("renderer_sha256")
    renderer = renderer_bytes.decode("utf-8")
    if not (
        'if kind == "INPUT":\n        return _symbol_ident(ref["symbol"])' in renderer
        and 'if kind == "INPUT":\n        return _symbol_ident(expr["symbol"])'
        in renderer
        and '_symbol_ident(item["name"]) + " " + _type_sql(item["type"])' in renderer
    ):
        raise RuntimeError("unqualified_input_lowering_not_proven")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-032-input-column-ambiguity-diagnosis.v1",
        "status": "deterministic_select_input_column_ambiguity_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 32,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E03",
            "sqlstate": "42702",
            "function_id": PROGRAM_ID,
            "function_line": 35,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "input_symbol": INPUT_ID,
            "input_physical_spelling": INPUT_ID,
            "colliding_source_column": INPUT_ID,
            "collision_nodes": collision_nodes,
            "artifact_body_predicate_lines": ambiguous_predicates,
            "artifact_sha256": "sha256:" + EXPECTED_ARTIFACT_SHA256,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "renderer_source_sha256": "sha256:" + EXPECTED_RENDERER_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "input_parameter_physical_prefix": "cf_arg_",
            "input_reference_rendering": "same_prefixed_physical_parameter",
            "support_function_input_change": False,
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
