from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-tool-result-conclusion-coordinate-"
    "diagnostic-recovery"
)
PLAN = ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT = ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"


def test_plan_freezes_the_narrow_provider_free_diagnostic() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Timestamp:" in text and "Australia/Brisbane" in text
    assert "Status: frozen for provider-free implementation" in text
    assert "internal orchestration/Harness diagnostic" in text
    assert "provider_free_authored_synthetic_tool_lifecycle_fixture" in text
    assert "all five authored-synthetic variants" in text
    assert "one bounded local" in text and "Node fixture" in text
    assert "No native Harness worker, DeepSeek/provider request" in text
    assert "ordinary-practice enablement" in text
    assert "docs/branding/" in text
    assert "git add ." in text and "git add -A" in text


def test_plan_owns_no_product_or_api_spine_surface() -> None:
    text = PLAN.read_text(encoding="utf-8")
    owned = text[text.index("## Owned paths") : text.index("## Acceptance")]
    assert "app/" not in owned
    assert "docs/api-spine/" not in owned
    assert "migration" not in owned.lower()
    assert "API Spine remains unchanged" in text


def test_threat_delta_forbids_free_form_and_runtime_escalation() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "Free-form diagnostic prose becomes a decision surface" in text
    assert "schema-valid closed enums and counts" in text
    assert (
        "Native Harness worker, provider, broker and model-request counts are fixed at zero"
        in text
    )
    assert "do not prove a" in text and "future occupied DeepSeek call" in text


def test_preplanning_receipt_has_five_sources_and_serial_lane_dispositions() -> None:
    path = (
        ROOT
        / "orchestration/agent_inbox/codex/deepseek-native-harness-tool-result-coordinate-recovery-preplanning-receipt.json"
    )
    receipt = json.loads(path.read_bytes())
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
        "gemini_verifier": "declined",
        "native_subagents": "declined",
    }


def test_rejected_manual_git_prose_receipt_is_preserved_beside_correction() -> None:
    root = ROOT / "orchestration/agent_inbox/codex"
    rejected = json.loads(
        (
            root
            / "deepseek-native-harness-tool-result-coordinate-recovery-postcompaction-attempt-001-rejected-receipt.json"
        ).read_bytes()
    )
    corrected = json.loads(
        (
            root
            / "deepseek-native-harness-tool-result-coordinate-recovery-postcompaction-receipt.json"
        ).read_bytes()
    )
    assert rejected["status"] == "revision_required"
    assert "git_refs_evidence_manual_object_id_forbidden" in rejected["reasons"]
    assert corrected["status"] == "passed"


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
