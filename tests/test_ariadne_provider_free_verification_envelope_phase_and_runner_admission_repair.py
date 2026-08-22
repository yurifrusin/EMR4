from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator

from scripts.ariadne_provider_free_verification_envelope_phase_and_runner_admission_repair import (
    CONTRACT_PATH,
    CONTRACT_SCHEMA_PATH,
    EVIDENCE_PATH,
    EVIDENCE_SCHEMA_PATH,
    REPORT_PATH,
    build_evidence,
)


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_and_canonical_evidence_are_schema_valid_and_exact() -> None:
    contract = _json(CONTRACT_PATH)
    evidence = _json(EVIDENCE_PATH)

    Draft202012Validator(_json(CONTRACT_SCHEMA_PATH)).validate(contract)
    Draft202012Validator(_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    assert build_evidence(evidence["source_head"]) == evidence
    assert evidence["hostile_rejection_count"] == 8
    assert evidence["subprocess_launch_count"] == 0
    assert evidence["phase_partition"]["cross_phase_execution_count"] == 0
    assert all(value is False for value in evidence["closed_boundaries"].values())


def test_direct_cli_check_passes_and_report_names_bounded_result() -> None:
    source = _json(EVIDENCE_PATH)["source_head"]
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.ariadne_provider_free_verification_envelope_phase_and_runner_admission_repair",
            "--check",
            "--source",
            source,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert "8 hostile" in report
    assert "subprocess launches in this" in report
