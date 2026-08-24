from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-read-only-waiting-area-movement-command-family-readiness-review-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-read-only-waiting-area-movement-command-family-readiness-review-threat-model-delta.md"
BASE = ROOT / "orchestration/continuity/raisa-provider-free-read-only-waiting-area-movement-command-family-readiness-review"


def test_plan_and_threat_delta_freeze_read_only_non_authority() -> None:
    text = " ".join(
        (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8"))
        .lower()
        .split()
    )
    for phrase in (
        "read-only",
        "implementation_authorized: false",
        "no repository-wide search",
        "historical diary data",
        "no product source",
        "docs/branding/",
        "explicit paths only",
    ):
        assert phrase in text


def test_contract_schema_and_exact_frozen_shape() -> None:
    contract = json.loads((BASE / "readiness-review-contract.json").read_text(encoding="utf-8"))
    schema = json.loads((BASE / "readiness-review-contract.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)

    assert len(contract["inputs"]) == 16
    assert len(contract["dimensions"]) == 12
    assert contract["acceptance"]["expected_counts"] == {
        "satisfied": 5,
        "blocking_gap": 7,
    }
    assert contract["acceptance"]["expected_next_tranche"].endswith(
        "waiting-area-confirm-command-family-architecture"
    )


def test_plan_records_explicit_parallelism_dispositions() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "DeepSeek is declined" in text
    assert "Gemini is not" in text
    assert "Native subagents" in text
    assert "GPT Sol serially owns" in text
