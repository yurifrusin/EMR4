from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "orchestration/continuity/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review"
)
SCHEMA = (
    EVIDENCE_ROOT
    / "ordinary-diary-cancellation-compatibility-consumer-convergence-review-evidence.schema.json"
)
EVIDENCE = (
    EVIDENCE_ROOT
    / "ordinary-diary-cancellation-compatibility-consumer-convergence-review-evidence.json"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_review_evidence_is_schema_valid_and_exact_candidate_bound() -> None:
    schema = _json(SCHEMA)
    evidence = _json(EVIDENCE)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(evidence)
    assert evidence["reviewed_candidate"] == (
        "0f3b0c73fef0a2a52186a8f86bae8cf351d1a8df"
    )


def test_review_freezes_one_client_only_fail_closed_convergence() -> None:
    evidence = _json(EVIDENCE)
    convergence = evidence["frozen_later_convergence"]
    assert convergence["dedicated_delete_proposal_only"] is True
    assert convergence["canonical_delete_confirm_only"] is True
    assert convergence["status_or_raw_delete_fallbacks"] == 0
    assert convergence["appointment_read_model_required"] is False
    assert convergence["backend_api_schema_migration_or_database_changes"] == 0


def test_review_claim_and_authority_remain_static_only() -> None:
    evidence = _json(EVIDENCE)
    assert not any(evidence["authority_counts"].values())
    assert evidence["findings"]["product_source_changed"] is False
    assert evidence["legacy_test_containment"] == {
        "suite": "tests/test_api_spine_delete_confirm_idempotency_route_contract.py",
        "status": "contained_as_stale_pre_adapter_test_debt",
        "attempted_reason_only_change_reverted": True,
        "failed_packets_used_for_acceptance": False,
        "incident": "AER-0387",
    }
