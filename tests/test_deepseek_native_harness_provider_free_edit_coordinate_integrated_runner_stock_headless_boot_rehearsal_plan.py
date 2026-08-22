from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-edit-coordinate-integrated-runner-"
    "stock-headless-boot-rehearsal"
)
PLAN = ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT = ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"


def test_plan_freezes_one_provider_free_stock_headless_loading_proof() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Timestamp:" in text and "Australia/Brisbane" in text
    assert "Status: frozen for provider-free implementation" in text
    assert "one native rc.7 process" in text
    assert "integrated_runner_post_hmr_pre_request_hold" in text
    assert "preflightEditArguments" in text
    assert "classifyEditArgumentResult" in text
    assert "before `agents.create`" in text
    assert "No DeepSeek worker" in text
    assert "ordinary-practice enablement" in text
    assert "docs/branding/" in text
    assert "git add ." in text and "git add -A" in text


def test_plan_and_threat_own_no_product_or_api_spine_surface() -> None:
    text = PLAN.read_text(encoding="utf-8")
    owned = text[text.index("## Owned paths") : text.index("## Acceptance")]
    assert "app/" not in owned
    assert "docs/api-spine/" not in owned
    threat = THREAT.read_text(encoding="utf-8")
    assert "A probe shim becomes a substitute runner" in threat
    assert "discard stdout/stderr" in threat.lower()
    assert "does not prove agent creation" in threat


def test_preplanning_receipt_has_five_sources_and_parallelism() -> None:
    receipt = json.loads(
        (
            ROOT
            / "orchestration/agent_inbox/codex/deepseek-native-harness-provider-free-edit-coordinate-integrated-runner-stock-headless-boot-rehearsal-preplanning-receipt.json"
        ).read_bytes()
    )
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert {
        row["lane_id"]: row["disposition"]
        for row in receipt["parallelism_assessment"]["lanes"]
    } == {
        "deepseek_flash": "declined",
        "gemini_verifier": "reserved",
        "native_subagents": "declined",
    }


def test_active_latch_is_the_exact_in_progress_operation() -> None:
    latch = json.loads(
        (
            ROOT
            / "orchestration/continuity/ariadne-active-operation-latch/current.json"
        ).read_bytes()
    )
    assert latch["operation_id"] == OPERATION_ID
    assert latch["status"] == "in_progress"
    assert latch["user_attention"]["required"] is False
    assert latch["terminal_response"]["permitted"] is False
