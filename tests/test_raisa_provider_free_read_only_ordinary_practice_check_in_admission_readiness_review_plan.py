from __future__ import annotations

import json
import re
from pathlib import Path

from scripts import (
    raisa_provider_free_read_only_ordinary_practice_check_in_admission_readiness_review
    as review,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-threat-model-delta.md"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
RECEIPT = ROOT / "orchestration/agent_inbox/codex/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-preplanning-receipt.json"


def test_plan_freezes_exact_source_and_timestamp() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in text
    assert f"Source HEAD: `{review.SOURCE_HEAD}`" in text
    assert "Timestamp: 2026-08-18T" in text
    assert "+10:00 (Australia/Brisbane)" in text
    assert "Accepted route source: `c82c3a741053a9c8da260aa62e1a968af22bb54e`" in text


def test_plan_and_contract_bind_all_28_exact_inputs() -> None:
    text = PLAN.read_text(encoding="utf-8")
    contract = review.load_contract(ROOT)
    assert len(contract["inputs"]) == 28
    for item in contract["inputs"]:
        assert f"`{item['path']}`" in text
        assert f"`{item['sha256']}`" in text
        assert re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
        assert review.canonical_sha256(ROOT / item["path"]) == item["sha256"]


def test_plan_freezes_not_ready_verdict_and_architecture_only_successor() -> None:
    text = PLAN.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    contract = review.load_contract(ROOT)
    assert contract["acceptance"] == review.EXPECTED_ACCEPTANCE
    assert "`not_ready_for_ordinary_practice_admission`" in text
    assert f"`{review.NEXT_TRANCHE}`" in text
    assert "may not edit product code/configuration or enable a practice" in flat


def test_threat_delta_preserves_separate_synthetic_and_ordinary_controls() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "Date: 2026-08-18" in text
    assert "+10:00 (Australia/Brisbane)" in text
    assert "Reusing the synthetic allowlist for an ordinary practice" in text
    assert "non-owner/NOBYPASS" in text
    assert "Audit/event evidence" not in text
    assert "aggregate non-PHI attempts" in text


def test_current_latch_and_five_source_receipt_are_exact() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert latch["operation_id"] == (
        "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
        "admission-readiness-review"
    )
    assert latch["status"] == "complete"
    assert latch["source_head"] == "27101faa86b5aa3850e90bc4ded8600e5f8d7dc9"
    assert latch["terminal_response"]["permitted"] is True
    assert receipt["status"] == "passed"
    assert receipt["active_operation"]["status"] == "in_progress"
    assert receipt["active_operation"]["terminal_handback_permitted"] is False
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert [lane["lane_id"] for lane in receipt["parallelism_assessment"]["lanes"]] == [
        "deepseek_flash",
        "gemini_verifier",
        "native_subagents",
    ]
    assert all(
        lane["disposition"] == "declined"
        for lane in receipt["parallelism_assessment"]["lanes"]
    )


def test_plan_forbids_every_requested_surface() -> None:
    text = PLAN.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    for phrase in (
        "No ordinary-practice enablement",
        "product code/configuration/live-route/database",
        "generic-status `Arrived`",
        "action grammar",
        "first-party client",
        "waiting-area movement",
        "product/patient/clinical/historical/protected data",
        "provider/Harness retry",
        "production runtime",
        "deployment",
        "release",
        "Pages",
        "protected-ref movement",
        "Preserve `docs/branding/`",
        "stage explicit paths only",
    ):
        assert phrase in flat
