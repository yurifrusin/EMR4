from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from scripts.bernie_lc4v2_exit_gap_reassessment import (
    INPUTS,
    REPORT_PATH,
    _accepted,
    _load_inputs,
    _report_hash,
    build_report,
)


def test_exact_frozen_evidence_requires_no_r3() -> None:
    report = build_report()
    assert report["decision"] == "no_r3_authorized"
    assert report["r3_authorized"] is False
    assert report["development_repair_exit_reached"] is True
    assert report["certification_status"] == "unresolved_user_decision"
    assert report["next_gate"] == "fresh_holdout_or_reviewed_reuse_policy"
    assert report["new_surface_count"] == 0
    assert report["supported_gap_count"] == 0
    assert all(report["assertions"].values())


def test_only_six_explicit_non_protected_inputs_are_configured() -> None:
    assert len(INPUTS) == 6
    assert all("holdout" not in path.lower() for path, _digest in INPUTS.values())
    assert not any("*" in path for path, _digest in INPUTS.values())


def test_file_hash_drift_fails_closed() -> None:
    documents, hashes = _load_inputs()
    mutated = dict(hashes)
    mutated["r1_acceptance"] = "0" * 64
    report = build_report(documents, mutated)
    assert report["decision"] == "reassessment_invalid"
    assert report["development_repair_exit_reached"] is False
    assert _accepted(report) is False


def test_repair_failure_drift_fails_closed() -> None:
    documents, hashes = _load_inputs()
    mutated = deepcopy(documents)
    mutated["r2_report"]["failed_case_count"] = 1
    report = build_report(mutated, hashes)
    assert report["decision"] == "reassessment_invalid"
    assert report["assertions"]["r2_zero_failure_contract_passes"] is False


def test_ordinary_count_drift_fails_closed() -> None:
    documents, hashes = _load_inputs()
    mutated = deepcopy(documents)
    mutated["r10_report"]["development_baseline"]["semantic_pass_counts_single_repeat"]["entity_semantics"] += 1
    report = build_report(mutated, hashes)
    assert report["decision"] == "reassessment_invalid"
    assert report["assertions"]["ordinary_development_baseline_passes"] is False


def test_unexpected_input_fails_closed() -> None:
    documents, hashes = _load_inputs()
    mutated = dict(documents)
    mutated["unexpected"] = {}
    assert build_report(mutated, hashes)["decision"] == "reassessment_invalid"


def test_unexpected_report_key_fails_closed() -> None:
    documents, hashes = _load_inputs()
    mutated = deepcopy(documents)
    mutated["r1_report"]["unexpected"] = True
    report = build_report(mutated, hashes)
    assert report["decision"] == "reassessment_invalid"
    assert report["assertions"]["all_input_schemas_exact"] is False


def test_report_hash_mutation_fails_closed() -> None:
    report = build_report()
    assert report["report_hash"] == _report_hash(report)
    report["report_hash"] = "sha256:" + "0" * 64
    assert _accepted(report) is False


def test_build_is_deterministic() -> None:
    assert build_report() == build_report()


def test_check_mode_is_exact_and_non_mutating() -> None:
    before = REPORT_PATH.read_bytes()
    completed = subprocess.run(
        [sys.executable, "scripts/bernie_lc4v2_exit_gap_reassessment.py", "--check"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert REPORT_PATH.read_bytes() == before
