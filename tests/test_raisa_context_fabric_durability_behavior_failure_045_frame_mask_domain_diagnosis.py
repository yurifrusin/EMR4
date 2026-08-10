from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts import (
    raisa_context_fabric_durability_behavior_failure_045_frame_mask_domain_diagnosis as diagnosis,
)


ROOT = Path(__file__).resolve().parents[1]


def test_failure_045_frame_mask_domain_contradiction_is_exact_and_bounded() -> None:
    evidence = diagnosis.diagnose()
    assert evidence["status"] == (
        "deterministic_frame_mask_domain_nullable_conflict_row_contradiction_"
        "proven_cleanup_verified"
    )
    assert evidence["parent_failure"] == {
        "run_sequence": 45,
        "internal_attempt_id": "67070f55e5bc3898e906bb64",
        "evidence_sha256": "sha256:e4af201491241a904d337650a7dbd7c3e8a36daf8bb0ea85aaae462da1045d67",
        "scenario_id": "BTR-I02",
        "sqlstate": "23502",
        "coordinate_status": "missing",
        "cleanup_absence_verified": True,
    }
    assert evidence["diagnosis"]["domain_not_null"] is True
    assert evidence["diagnosis"]["conflict_shape_requires_null"] is True
    assert evidence["diagnosis"]["additional_container_runs"] == 0
    assert evidence["bounded_repair"]["effective_frame_mask_domain_not_null"] is False
    assert evidence["bounded_repair"]["structural_parent_changed"] is False
    assert evidence["bounded_repair"]["body_parent_changed"] is False


def test_failure_045_diagnosis_cli_is_deterministic() -> None:
    command = [
        sys.executable,
        "-m",
        "scripts.raisa_context_fabric_durability_behavior_failure_045_frame_mask_domain_diagnosis",
    ]
    first = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
    second = subprocess.run(command, cwd=ROOT, check=True, capture_output=True).stdout
    assert first == second
    assert json.loads(first)["diagnosis"]["raw_postgresql_error_persisted"] is False
