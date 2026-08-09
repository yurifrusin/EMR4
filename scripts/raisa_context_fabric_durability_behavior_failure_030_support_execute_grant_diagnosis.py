"""Diagnose behavior failure 030 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-030.json"
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
SOURCE_HEAD = "8088b65be06c3a50fbc359012bc0f2f9eb45377f"
EXPECTED_FAILURE_SHA256 = (
    "deb7a568a80aee0b70264989fe362e214555573ed7a169d58cb32436ce490ec1"
)
EXPECTED_ARTIFACT_SHA256 = (
    "03150dfec61944df8f26ca2473200afa49e88ddcf9d9fce950320a2a98bd96e0"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "b43ea059a3f424e268631228aa9606d30f1c9f082bc805e550788b01e7bd8e76"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "9b57d9d28f216e494da91715fcf7dfc7f49c80bbbe836fe0c685cd1dd4929268"
)
EXPECTED_RENDERER_SHA256 = (
    "06a34953259c83be3e9d026e1a10115122be8fc5c35ea0c579d9b47eaade351f"
)
SUPPORT_ID = "emr4_context_fabric.session_binding_allows_v1"
ADMISSION_ID = "emr4_context_fabric.admit_proofread_observation_v1"
EXPECTED_EXECUTOR_ROLES = [
    "emr4_context_fabric.context_schema_owner",
    "emr4_context_fabric.context_admission_receiver",
    "emr4_context_fabric.context_observer",
    "emr4_context_fabric.context_producer",
    "emr4_context_fabric.context_coordinator",
    "emr4_context_fabric.context_lifecycle",
    "emr4_context_fabric.context_retention",
    "emr4_context_fabric.context_application_read",
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


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_030_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and detail.get("stage") == "scenario"
        and detail.get("code") == "unexpected_rejection"
        and detail.get("scenario_id") == "BTR-E03"
        and detail.get("sqlstate") == "42501"
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_030_not_closed")

    artifact_bytes = _git_source_bytes(ARTIFACT_PATH)
    if _sha256(artifact_bytes) != EXPECTED_ARTIFACT_SHA256:
        raise RuntimeError("artifact_sha256")
    artifact = artifact_bytes.decode("utf-8")
    support_signature = (
        "authenticated_login pg_catalog.name, allowed_capabilities "
        "emr4_context_fabric.logical_capability[], requested_practice_id "
        "pg_catalog.uuid, requested_source_contract_id "
        "emr4_context_fabric.source_contract_code, requested_stream_id "
        "pg_catalog.uuid, observed_at pg_catalog.timestamptz"
    )
    revoke = f"REVOKE ALL ON FUNCTION {SUPPORT_ID}({support_signature}) FROM PUBLIC;"
    grant_prefix = f"GRANT EXECUTE ON FUNCTION {SUPPORT_ID}({support_signature}) TO "
    if artifact.count(revoke) != 1 or grant_prefix in artifact:
        raise RuntimeError("support_public_revoke_without_runtime_grants_not_proven")

    admission_start = artifact.index("CREATE FUNCTION " + ADMISSION_ID)
    admission_end = artifact.index("CREATE FUNCTION ", admission_start + 16)
    admission_sql = artifact[admission_start:admission_end]
    if not (
        f"binding_allowed := {SUPPORT_ID}(session_user" in admission_sql
        and "'OBSERVER'::emr4_context_fabric.logical_capability" in admission_sql
        and f"ALTER FUNCTION {ADMISSION_ID}" in admission_sql
        and "OWNER TO context_admission_receiver;" in admission_sql
    ):
        raise RuntimeError("admission_receiver_support_call_not_proven")

    body_bytes = _git_source_bytes(BODY_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    body = json.loads(body_bytes)
    if body.get("contract_sha256") != "sha256:" + EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    signatures = body["effective_parent_summary"]["effective_signatures"]
    support = signatures["support"]
    admission = _exact(signatures["entry_points"], "id", ADMISSION_ID)
    if not (
        support.get("id") == SUPPORT_ID
        and support.get("executor_roles") == EXPECTED_EXECUTOR_ROLES
        and support.get("public_execute") is False
        and admission.get("owner") == "emr4_context_fabric.context_admission_receiver"
        and admission.get("executor") == "emr4_context_fabric.context_observer"
    ):
        raise RuntimeError("accepted_support_execute_contract_not_proven")

    renderer_bytes = _git_source_bytes(RENDERER_PATH)
    if _sha256(renderer_bytes) != EXPECTED_RENDERER_SHA256:
        raise RuntimeError("renderer_sha256")
    renderer = renderer_bytes.decode("utf-8")
    render_start = renderer.index("def _render_revokes_grants(")
    render_end = renderer.index("\ndef _signature_by_id(", render_start)
    grant_renderer = renderer[render_start:render_end]
    if not (
        'for role in support.get("execute_roles", []):' in grant_renderer
        and 'support.get("executor_roles"' not in grant_renderer
        and "name = _role_name(role)" in grant_renderer
    ):
        raise RuntimeError("renderer_field_name_mismatch_not_proven")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-030-support-execute-grant-diagnosis.v1",
        "status": "deterministic_support_execute_grant_omission_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 30,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E03",
            "sqlstate": "42501",
            "completed_scenarios": 0,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "support_function_id": SUPPORT_ID,
            "admission_function_id": ADMISSION_ID,
            "admission_owner": "context_admission_receiver",
            "admission_executor": "context_observer",
            "contract_executor_roles": EXPECTED_EXECUTOR_ROLES,
            "contract_executor_field": "executor_roles",
            "renderer_lookup_field": "execute_roles",
            "public_execute_revoked": True,
            "support_execute_grants_emitted": 0,
            "artifact_sha256": "sha256:" + EXPECTED_ARTIFACT_SHA256,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "renderer_source_sha256": "sha256:" + EXPECTED_RENDERER_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "renderer_lookup_field": "executor_roles",
            "exact_grantee_roles": EXPECTED_EXECUTOR_ROLES,
            "structural_contract_change": False,
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
