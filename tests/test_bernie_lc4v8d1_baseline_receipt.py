"""Bind the frozen LC4V8D1 aggregate receipt to recovered ordinary evidence."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.bernie.lc4v8d1_development_evidence import run_lc4v8d1_evidence


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "docs" / "bernie-lc4v8d1-development-baseline.json"


def test_frozen_baseline_receipt_matches_recovered_evidence() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    evidence = run_lc4v8d1_evidence()
    assert receipt["schema_version"] == "bernie.lc4v8d1.baseline_receipt.v1"
    assert receipt["decision"] == (
        "development_diagnostic_pass_empty_selection_no_remediation_authorized"
    )
    assert receipt["source_commit"] == "8823bf0d"
    assert receipt["fixture_raw_hash"] == evidence["fixture_raw_hash"]
    assert receipt["fixture_canonical_hash"] == evidence["fixture_hash"]
    assert receipt["report_hash"] == evidence["report_hash"]
    assert receipt["selection"] == evidence["selection"]
    assert receipt["aggregate"] == evidence["aggregate"]
    assert receipt["classifications"] == evidence["classifications"]
    assert receipt["family_counts"] == evidence["family_counts"]
    assert receipt["repeat_observations"] == 48
    assert receipt["protected_source_used"] is False
    assert receipt["product_runtime_files_changed"] == []
