from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts import (
    raisa_context_fabric_durability_behavior_failure_046_admission_replay_diagnosis as diagnosis,
)


ROOT = Path(__file__).resolve().parents[1]


def test_failure_046_timestamp_replay_contradiction_is_exact_and_bounded() -> None:
    evidence = diagnosis.diagnose()
    assert evidence["status"] == (
        "deterministic_server_authored_timestamp_replay_comparison_"
        "contradiction_proven_cleanup_verified"
    )
    assert evidence["parent_failure"] == {
        "run_sequence": 46,
        "internal_attempt_id": "e4db8cf23eb421e40744ea25",
        "evidence_sha256": "sha256:ea2fc7f55121604b8f68b5bbacc55b97c98ead76a5793b6d7c766f2269b311c0",
        "scenario_id": "BTR-I02",
        "sqlstate": "CF004",
        "function_id": "emr4_context_fabric.admit_proofread_observation_v1",
        "function_line": 72,
        "cleanup_absence_verified": True,
    }
    assert evidence["diagnosis"]["failed_path"].endswith(
        ".insert_mismatch.reload_compare"
    )
    assert len(evidence["diagnosis"]["unstable_timestamp_winner_comparison_nodes"]) == 3
    assert evidence["diagnosis"]["additional_container_runs"] == 0
    assert evidence["bounded_repair"] == {
        "remove_only_admitted_at_from_winner_predicate": True,
        "preserve_admitted_at_insert_and_return_column": True,
        "affected_nodes": [
            "emr4_context_fabric.admit_proofread_observation_v1.insert_mismatch",
            "emr4_context_fabric.admit_proofread_observation_v1.insert_primary",
            "emr4_context_fabric.admit_proofread_observation_v1.insert_reuse",
        ],
        "conflict_key_unchanged": True,
        "immutable_body_parent_changed": False,
        "runtime_authority_changed": False,
    }


def test_failure_046_diagnosis_cli_is_deterministic() -> None:
    command = [
        sys.executable,
        "-m",
        "scripts.raisa_context_fabric_durability_behavior_failure_046_admission_replay_diagnosis",
    ]
    first = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
    second = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
    assert first == second
    assert json.loads(first)["diagnosis"]["raw_postgresql_error_persisted"] is False
