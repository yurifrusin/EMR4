import json
from pathlib import Path


PLAN = Path(
    "docs/raisa-local-only-historical-diary-document-story-time-coordinate-bounded-measurement-recovery-rehearsal-plan.md"
)
THREAT = Path(
    "docs/security/raisa-local-only-historical-diary-document-story-time-coordinate-bounded-measurement-recovery-rehearsal-threat-model-delta.md"
)
CONTRACT = Path(
    "orchestration/continuity/raisa-provider-free-authored-synthetic-historical-diary-word-coordinate-timeout-containment-throughput-recovery/next-tranche-contract.json"
)


def test_plan_contract_and_threat_freeze_one_new_terminal_measurement():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert "2026-08-24-story-coordinate-v2" in plan
    assert "first-use gate" in threat.casefold()
    assert contract["source_boundary"]["new_attempt_root"].endswith(
        "2026-08-24-story-coordinate-v2"
    )
    assert contract["execution"] == {
        "metadata_bind_attempts": 1,
        "content_runs": 1,
        "content_retry_authorized": False,
        "controller_timeout_seconds": 1800,
        "exact_parent_word_cleanup": True,
        "count_only_progress": True,
        "prior_attempt_reuse_or_retry": False,
    }
    assert contract["first_use_gate"] == {
        "status": "closed_pending_candidate_specific_evaluation",
        "opened_by_measurement_success": False,
        "reusable_artifact_created": False,
    }


def test_consumed_v2_plan_and_contract_remain_exact_historical_evidence():
    plan = PLAN.read_text(encoding="utf-8")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert "2026-08-24-story-coordinate-v2" in plan
    assert contract["source_boundary"]["new_attempt_root"].endswith(
        "2026-08-24-story-coordinate-v2"
    )
