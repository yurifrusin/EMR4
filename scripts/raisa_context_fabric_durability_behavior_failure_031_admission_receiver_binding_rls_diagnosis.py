"""Diagnose behavior failure 031 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-031.json"
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
SOURCE_HEAD = "75160f4497798665f83c31ca08079a760aed1136"
EXPECTED_FAILURE_SHA256 = (
    "09b7f4e3915198f8c0d0c7c86824fb7197f1d5be368deb85cd02df21e6f30bbc"
)
EXPECTED_ARTIFACT_SHA256 = (
    "934237c4525bf193999039aa1ad00ca815081152d32a6105f3cf730310695461"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "b43ea059a3f424e268631228aa9606d30f1c9f082bc805e550788b01e7bd8e76"
)
EXPECTED_STRUCTURAL_SOURCE_SHA256 = (
    "6b2ec35d7be7cd33f683173f5ac12ef4c95b0d1bbf05bccf50d10e74c9ca00bc"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "9b57d9d28f216e494da91715fcf7dfc7f49c80bbbe836fe0c685cd1dd4929268"
)
EXPECTED_STRUCTURAL_CONTRACT_SHA256 = (
    "00a4102ff0e884038e4a25f814dab84f5500b5e597058e30012b3a6d0be6514b"
)
PROGRAM_ID = "emr4_context_fabric.admit_proofread_observation_v1"
BINDING_RELATION = "emr4_context_fabric.context_service_practice_binding"
BINDING_NODE_ID = PROGRAM_ID + ".binding.select"
RECEIVER_ROLE = "emr4_context_fabric.context_admission_receiver"
OLD_POLICY_SQL = (
    "current_user = 'context_schema_owner'::name AND "
    "database_login = session_user AND "
    "active_from <= transaction_timestamp() AND "
    "(active_until IS NULL OR active_until > transaction_timestamp())"
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
    return result.stdout.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _exact(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    matches = [item for item in items if item.get(key) == value]
    if len(matches) != 1:
        raise RuntimeError(f"{value}_population")
    return matches[0]


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_031_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and detail.get("scenario_id") == "BTR-E03"
        and detail.get("sqlstate") == "CF004"
        and detail.get("function_id") == PROGRAM_ID
        and detail.get("function_line") == 26
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_031_not_closed")

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
    if not (
        "INTO STRICT binding FROM " + BINDING_RELATION in function_lines[21]
        and function_lines[23].strip() == "WHEN NO_DATA_FOUND THEN"
        and function_lines[24].strip().startswith(
            "RAISE EXCEPTION USING ERRCODE = 'CF004'"
        )
        and function_lines[25].strip() == "WHEN TOO_MANY_ROWS THEN"
        and function_lines[26].strip().startswith(
            "RAISE EXCEPTION USING ERRCODE = 'CF004'"
        )
    ):
        raise RuntimeError("function_line_26_not_binding_cardinality_handler")

    policy_fragment = (
        "CREATE POLICY pol_cf_17_select ON "
        + BINDING_RELATION
        + " FOR SELECT TO PUBLIC\n    USING ("
        + OLD_POLICY_SQL
        + ");"
    )
    if policy_fragment not in artifact:
        raise RuntimeError("artifact_binding_policy_not_exact")
    receiver_grant = "GRANT SELECT ON TABLE " + BINDING_RELATION + (
        " TO context_admission_receiver;"
    )
    if artifact.count(receiver_grant) != 1:
        raise RuntimeError("artifact_receiver_binding_grant_population")

    body_bytes = _git_source_bytes(BODY_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    body = json.loads(body_bytes)
    if _canonical_digest(body) != EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    program = _exact(body["body_programs"], "id", PROGRAM_ID)
    binding_select = _exact(program["ast"]["nodes"], "node_id", BINDING_NODE_ID)
    operands = binding_select["operands"]
    if not (
        binding_select.get("op") == "SELECT_EXACT"
        and operands.get("relation") == BINDING_RELATION
        and operands.get("cardinality") == "EXACTLY_ONE"
        and operands.get("output_symbol") == "binding"
        and '"field":"SESSION_USER"' in json.dumps(operands, separators=(",", ":"))
    ):
        raise RuntimeError("binding_select_contract_missing")
    receiver = _exact(
        body["effective_parent_summary"]["effective_roles"],
        "role",
        RECEIVER_ROLE,
    )
    if not (
        receiver.get("login") is False
        and receiver.get("runtime_role") is False
        and receiver.get("noinherit") is True
        and receiver.get("nobypassrls") is True
        and receiver.get("owns_functions") == [PROGRAM_ID]
        and BINDING_RELATION in receiver.get("direct_table_select", [])
        and receiver.get("direct_table_dml")
        == [
            {
                "relation": (
                    "emr4_context_fabric.context_proofread_observation_admission"
                ),
                "privileges": ["INSERT"],
            }
        ]
    ):
        raise RuntimeError("receiver_effective_authority_not_exact")

    structural_bytes = _git_source_bytes(STRUCTURAL_PATH)
    if _sha256(structural_bytes) != EXPECTED_STRUCTURAL_SOURCE_SHA256:
        raise RuntimeError("structural_source_sha256")
    structural = json.loads(structural_bytes)
    if _canonical_digest(structural) != EXPECTED_STRUCTURAL_CONTRACT_SHA256:
        raise RuntimeError("structural_contract_sha256")
    policy = _exact(
        structural["rls_policy_catalogue"]["policies"], "id", "pol_cf_17_select"
    )
    relation = _exact(
        structural["relation_catalogue"]["relations"],
        "name",
        "context_service_practice_binding",
    )
    entry = _exact(structural["entry_points"], "name", PROGRAM_ID.rsplit(".", 1)[1])
    if not (
        relation.get("rls_enabled") is True
        and relation.get("rls_forced") is True
        and relation.get("rls_policy_ids") == ["pol_cf_17_select"]
        and policy
        == {
            "id": "pol_cf_17_select",
            "relation": "context_service_practice_binding",
            "command": "SELECT",
            "roles": ["PUBLIC"],
            "permissive": True,
            "using_sql": OLD_POLICY_SQL,
            "with_check_sql": None,
        }
        and entry.get("owner") == "context_admission_receiver"
        and entry.get("security_definer") is True
    ):
        raise RuntimeError("receiver_binding_rls_mismatch_not_proven")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-031-admission-receiver-binding-rls-diagnosis.v1",
        "status": "deterministic_admission_receiver_binding_rls_visibility_gap_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 31,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E03",
            "sqlstate": "CF004",
            "function_id": PROGRAM_ID,
            "function_line": 26,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "binding_node_id": BINDING_NODE_ID,
            "relation": BINDING_RELATION,
            "rls_forced": True,
            "entry_point_security_definer": True,
            "entry_point_owner": RECEIVER_ROLE,
            "entry_point_owner_login": False,
            "receiver_binding_select_granted": True,
            "policy_current_user_allowlist": [
                "emr4_context_fabric.context_schema_owner"
            ],
            "required_current_user_missing": RECEIVER_ROLE,
            "database_login_equals_session_user_retained": True,
            "active_interval_fence_retained": True,
            "artifact_sha256": "sha256:" + EXPECTED_ARTIFACT_SHA256,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "structural_source_sha256": "sha256:"
            + EXPECTED_STRUCTURAL_SOURCE_SHA256,
            "structural_contract_sha256": "sha256:"
            + EXPECTED_STRUCTURAL_CONTRACT_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "policy_change": "allow_exact_nonlogin_owner_pair_while_retaining_session_bound_active_row_filter",
            "current_user_allowlist": [
                "emr4_context_fabric.context_schema_owner",
                RECEIVER_ROLE,
            ],
            "policy_roles_change": False,
            "direct_table_grant_change": False,
            "role_or_membership_change": False,
            "bypassrls_change": False,
            "body_program_change": False,
            "scenario_change": False,
            "new_authority": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
