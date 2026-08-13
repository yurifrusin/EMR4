from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal-threat-model-delta.md"
RECEIPT = ROOT / "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal-preplanning-receipt.json"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
EXPECTED_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


def test_plan_and_threat_delta_are_timestamped_and_fail_closed() -> None:
    for path in (PLAN, THREAT):
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-13" in text
        assert "Timestamp: 2026-08-13T" in text
        assert "+10:00 (Australia/Brisbane)" in text
    plan = PLAN.read_text(encoding="utf-8")
    for phrase in (
        "Revision: 3",
        "transaction-local",
        "normalize that already-admitted target text to an exact UUID",
        "Exactly twelve",
        "at least 100 hostile",
        "No route edit/mount/call",
        "protected-ref movement",
    ):
        assert phrase in plan


def test_rehydration_receipt_names_all_five_sources() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == EXPECTED_SOURCES
    assert set(receipt["source_evidence"]) == EXPECTED_SOURCES
    assert receipt["terminal_handback_permitted"] is False


def test_active_latch_tracks_the_same_unfinished_operation() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    assert latch["operation_id"] == "raisa-status-confirm-product-adapter-postgresql-integration"
    assert latch["status"] == "in_progress"
    assert latch["terminal_response"]["permitted"] is False
    assert latch["user_attention"]["required"] is False
