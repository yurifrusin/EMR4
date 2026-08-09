"""Diagnose behavior failure 033 without opening another PostgreSQL runtime."""

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
    BEHAVIOR_DIR / "provider-free-behavior-transaction-failure-evidence-033.json"
)
BODY_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-durability-function-trigger-body-architecture"
    / "function-trigger-body-architecture-contract.json"
)
HARNESS_PATH = (
    ROOT
    / "scripts"
    / "raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py"
)
CONTRACT_PATH = BEHAVIOR_DIR / "behavior-transaction-rehearsal-contract.json"
SCHEMA_PATH = BEHAVIOR_DIR / "behavior-transaction-rehearsal-contract.schema.json"
PLAN_PATH = ROOT / (
    "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "transaction-rehearsal-plan.md"
)
DESIGN_PATH = ROOT / (
    "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "transaction-rehearsal-design.md"
)
SOURCE_HEAD = "b980fe2d0b4dc9a318c820f388a0e9fad34cfa6f"
EXPECTED_FAILURE_SHA256 = (
    "5a6d5bcc18cd23f0fa528e5cdd33e53e9f0b90c0415a8f86ca326cf47980c8ad"
)
EXPECTED_BODY_SOURCE_SHA256 = (
    "01f92356def997b96adb3115cfb4b82afc29a27e72cab5823c81a6b5f2e2a7f1"
)
EXPECTED_BODY_CONTRACT_SHA256 = (
    "edbc7f2361f8b5a2812dcff2a7cdf81bef7bd2a6d280be5a9023571c5121508e"
)
EXPECTED_HARNESS_SHA256 = (
    "8f6c5ede1e701cd4bb474002603b66952f6edbb1de848bf1181c5b7d47dae2b9"
)
EXPECTED_CONTRACT_SOURCE_SHA256 = (
    "eead570eac1d4418b80ff1b6f1097e0df08200375343912326682b8190b8e5a9"
)
EXPECTED_SCHEMA_SOURCE_SHA256 = (
    "8dbdf948403bf30d79c589879372e74eceb2d56402886d5fe47f988dd4903499"
)
EXPECTED_PLAN_SHA256 = (
    "49081f2694a78e5664e2673526771e53e56b85ac6caf9b7f612fea00d0a83130"
)
EXPECTED_DESIGN_SHA256 = (
    "cd53575ddfc788144e1caceed6e2fa45082d82444592d1670264c52bdae09bfb"
)
EXPECTED_BEHAVIOR_CONTRACT_SHA256 = (
    "65984c17f1d93ac44ad45059c1ea30a41131dec8844475c9801b5bb440dcc0a8"
)
PROGRAM_ID = "emr4_context_fabric.admit_proofread_observation_v1"
DIGEST_PROFILE = "emr4_context_fabric.source_membership_digest_v1"
OUTBOX_RELATION = "emr4_context_fabric.diary_context_observation_outbox_v1"
EXPECTED_SOURCE_FIELDS = [
    "practice_id",
    "source_contract_id",
    "stream_id",
    "stream_epoch",
    "transaction_position",
    "predecessor_position",
    "raw_event_uuid",
    "opaque_aggregate_alias",
    "aggregate_revision",
    "source_contract_digest",
    "transaction_authored_at",
]
STALE_RULE = "read_exact_outbox_source_contract_digest_for_same_locator"


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


def _source_digest_node(body: dict[str, Any]) -> dict[str, Any]:
    programs = [row for row in body["body_programs"] if row.get("id") == PROGRAM_ID]
    if len(programs) != 1:
        raise RuntimeError("admission_program_population")
    matches = [
        node
        for node in _walk(programs[0]["ast"])
        if node.get("op") == "CANONICAL_DIGEST"
        and node.get("profile") == DIGEST_PROFILE
    ]
    if len(matches) != 1:
        raise RuntimeError("source_membership_digest_population")
    return matches[0]


def diagnose() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != EXPECTED_FAILURE_SHA256:
        raise RuntimeError("failure_033_sha256")
    failure = json.loads(failure_bytes)
    detail = failure.get("environment", {}).get("failure", {})
    cleanup = failure.get("cleanup", {})
    if not (
        failure.get("result") == "rehearsal_failed"
        and failure.get("attempt_id") == "ca31e812992de9b2cba982cc"
        and detail.get("scenario_id") == "BTR-E03"
        and detail.get("sqlstate") == "CF201"
        and detail.get("function_id") == PROGRAM_ID
        and detail.get("function_line") == 100
        and failure.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_033_not_closed")

    body_bytes = _git_source_bytes(BODY_PATH)
    if _sha256(body_bytes) != EXPECTED_BODY_SOURCE_SHA256:
        raise RuntimeError("body_source_sha256")
    body = json.loads(body_bytes)
    if _canonical_digest(body) != EXPECTED_BODY_CONTRACT_SHA256:
        raise RuntimeError("body_contract_sha256")
    digest_node = _source_digest_node(body)
    operands = digest_node.get("operands", [])
    source_fields = [operand.get("column") for operand in operands]
    if source_fields != EXPECTED_SOURCE_FIELDS or any(
        operand.get("op") != "REF"
        or operand.get("kind") != "ROW_COLUMN"
        or operand.get("symbol") != "source"
        or operand.get("relation") != OUTBOX_RELATION
        for operand in operands
    ):
        raise RuntimeError("body_source_membership_definition")

    harness_bytes = _git_source_bytes(HARNESS_PATH)
    if _sha256(harness_bytes) != EXPECTED_HARNESS_SHA256:
        raise RuntimeError("harness_source_sha256")
    harness = harness_bytes.decode("utf-8")
    if not (
        '"(SELECT source_contract_digest FROM "' in harness
        and "a.source_membership_digest=o.source_contract_digest" in harness
        and DIGEST_PROFILE not in harness
    ):
        raise RuntimeError("stale_harness_fixture_not_proven")

    contract_bytes = _git_source_bytes(CONTRACT_PATH)
    schema_bytes = _git_source_bytes(SCHEMA_PATH)
    if _sha256(contract_bytes) != EXPECTED_CONTRACT_SOURCE_SHA256:
        raise RuntimeError("behavior_contract_source_sha256")
    if _sha256(schema_bytes) != EXPECTED_SCHEMA_SOURCE_SHA256:
        raise RuntimeError("behavior_contract_schema_sha256")
    contract = json.loads(contract_bytes)
    if _canonical_digest(contract) != EXPECTED_BEHAVIOR_CONTRACT_SHA256:
        raise RuntimeError("behavior_contract_sha256")
    if contract["fixture_namespace"].get("source_membership_digest_rule") != STALE_RULE:
        raise RuntimeError("stale_fixture_rule_not_proven")
    if STALE_RULE not in schema_bytes.decode("utf-8"):
        raise RuntimeError("stale_fixture_schema_not_proven")

    plan_bytes = _git_source_bytes(PLAN_PATH)
    design_bytes = _git_source_bytes(DESIGN_PATH)
    if _sha256(plan_bytes) != EXPECTED_PLAN_SHA256:
        raise RuntimeError("plan_sha256")
    if _sha256(design_bytes) != EXPECTED_DESIGN_SHA256:
        raise RuntimeError("design_sha256")
    plan = plan_bytes.decode("utf-8")
    design = design_bytes.decode("utf-8")
    if not (
        "same-locator outbox source-contract digest" in plan
        and "source-membership digest is copied only from the" in design
    ):
        raise RuntimeError("stale_documented_fixture_rule_not_proven")

    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-033-source-membership-fixture-diagnosis.v1",
        "status": "deterministic_fixture_to_body_source_membership_contradiction_proven_cleanup_verified",
        "parent_failure": {
            "run_sequence": 33,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": "BTR-E03",
            "sqlstate": "CF201",
            "function_id": PROGRAM_ID,
            "function_line": 100,
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "accepted_body_digest_profile": DIGEST_PROFILE,
            "accepted_body_source_relation": OUTBOX_RELATION,
            "accepted_body_source_fields": source_fields,
            "fixture_supplied_value": "same_locator_outbox.source_contract_digest",
            "fixture_readback_compared_value": "admission.source_membership_digest_equals_outbox.source_contract_digest",
            "contract_rule": STALE_RULE,
            "body_source_sha256": "sha256:" + EXPECTED_BODY_SOURCE_SHA256,
            "body_contract_sha256": "sha256:" + EXPECTED_BODY_CONTRACT_SHA256,
            "harness_source_sha256": "sha256:" + EXPECTED_HARNESS_SHA256,
            "behavior_contract_sha256": "sha256:" + EXPECTED_BEHAVIOR_CONTRACT_SHA256,
            "raw_postgresql_error_persisted": False,
            "additional_container_runs": 0,
        },
        "bounded_repair": {
            "packet_value": "canonical_digest_of_complete_same_locator_outbox_row",
            "readback": "admission_digest_equals_independent_same_locator_full_row_recomputation",
            "contract_and_schema_rule_change": True,
            "plan_and_design_correction": True,
            "body_program_change": False,
            "inert_artifact_change": False,
            "scenario_population_change": False,
            "principal_or_sqlstate_change": False,
            "authority_change": False,
        },
        "authority_boundary": "provider_free_repository_diagnosis_only_no_runtime_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
