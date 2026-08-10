#!/usr/bin/env python3
"""Diagnose behavior attempt 039 without another PostgreSQL execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-behavior-transaction-rehearsal"
)
FAILURE_PATH = (
    EVIDENCE_DIR / "provider-free-behavior-transaction-failure-evidence-039.json"
)
DIAGNOSIS_PATH = (
    EVIDENCE_DIR / "provider-free-behavior-transaction-diagnosis-evidence-039.json"
)
EXPECTED_FAILURE_SHA256 = (
    "4e0d7142187e64aa4516d115d444236b3b67582ef7a239bc37c00b00e0038f27"
)
EXPECTED_SCENARIO_ID = "BTR-E04"


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def diagnose() -> dict[str, Any]:
    raw = FAILURE_PATH.read_bytes()
    if _sha256(raw) != EXPECTED_FAILURE_SHA256:
        raise ValueError("failure_039_sha256")
    evidence = json.loads(raw)
    failure = evidence.get("environment", {}).get("failure", {})
    if evidence.get("attempt_id") != "5dcf0e6427694521e3a2ca26":
        raise ValueError("failure_039_attempt")
    if failure.get("stage") != "readback" or failure.get("code") != "scenario_probe":
        raise ValueError("failure_039_identity")
    scenario_digest = "sha256:" + _sha256(EXPECTED_SCENARIO_ID.encode("utf-8"))
    if failure.get("detail_digest") != scenario_digest:
        raise ValueError("failure_039_scenario_digest")
    cleanup = evidence.get("cleanup", {})
    if (
        cleanup.get("absence_verified") is not True
        or cleanup.get("removed") is not True
    ):
        raise ValueError("failure_039_cleanup")
    if evidence.get("scenario_reconciliation") != {
        "expected": 20,
        "observed": 0,
        "passed": 0,
    }:
        raise ValueError("failure_039_reconciliation")
    return {
        "schema_version": (
            "emr4.raisa-context-fabric-durability-failure-039-probe-index-diagnosis.v1"
        ),
        "status": (
            "deterministic_e04_probe_mismatch_proven_"
            "probe_index_not_released_cleanup_verified"
        ),
        "parent_failure": {
            "run_sequence": 39,
            "internal_attempt_id": "5dcf0e6427694521e3a2ca26",
            "evidence_sha256": "sha256:" + EXPECTED_FAILURE_SHA256,
            "scenario_id": EXPECTED_SCENARIO_ID,
            "failure_stage": "readback",
            "failure_code": "scenario_probe",
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "additional_container_runs": 0,
            "scenario_recovered_from_bounded_digest": True,
            "transition_result_marker_admitted_before_probe": True,
            "relation_delta_admitted_before_probe": True,
            "probe_count": 7,
            "failed_probe_index_released": False,
            "raw_postgresql_values_persisted": False,
        },
        "bounded_repair": {
            "new_external_authority": False,
            "behavior_contract_unchanged": True,
            "database_artifact_unchanged": True,
            "allowed_digest_changes_unchanged": True,
            "failure_schema_adds_bounded_probe_indexes_only": True,
            "probe_shape_must_be_exact_boolean_array": True,
            "fresh_exact_head_veto_before_characterization": True,
            "next_run_must_be_single_owned_disposable_attempt": True,
        },
        "authority_boundary": (
            "provider_free_repository_diagnosis_and_bounded_harness_evidence_"
            "repair_only_no_runtime_product_provider_command_deployment_or_"
            "protected_ref_authority"
        ),
    }


def main() -> int:
    observed = diagnose()
    expected = json.loads(DIAGNOSIS_PATH.read_text(encoding="utf-8"))
    if observed != expected:
        raise ValueError("failure_039_diagnosis_drift")
    print(json.dumps(observed, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
