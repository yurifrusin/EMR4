"""Deterministic checks for bounded behavior attempt 047 diagnosis."""

from __future__ import annotations

import json
import subprocess

from scripts import (
    raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis as diagnosis,
)


def test_attempt_047_diagnosis_is_exact_and_repository_only() -> None:
    value = diagnosis.build_diagnosis()
    assert value["status"] == "diagnosed_repository_only"
    assert value["attempt"] == {
        "id": "2be135bb50da12e457e64eb6",
        "evidence_sha256": "sha256:bc577de88b7acafac72828bb2ddae898181886d08676c8802acf84ef925ebd63",
        "scenario_id": "BTR-B03",
        "expected_sqlstate": "P0001",
        "observed_sqlstate": "22012",
        "cleanup_verified": True,
    }
    assert value["classification"] == (
        "harness_fixture_noncontiguous_position_not_artifact_defect"
    )
    assert value["recovery"] == {
        "scope": "behavior_harness_only",
        "precommit_primary_position": 1,
        "transition_position": 1,
        "probe_position": 1,
        "expected_transition_result": "RECEIPT_APPLIED",
        "expected_terminal_sqlstate": "P0001",
        "artifact_changed": False,
        "behavior_contract_changed": False,
    }


def test_attempt_047_diagnosis_cli_is_byte_stable() -> None:
    result = subprocess.run(
        [str(diagnosis.ROOT / ".venv/Scripts/python.exe"), str(diagnosis.__file__)],
        cwd=diagnosis.ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
        shell=False,
    )
    assert result.returncode == 0
    assert result.stderr == b""
    assert json.loads(result.stdout) == diagnosis.build_diagnosis()
