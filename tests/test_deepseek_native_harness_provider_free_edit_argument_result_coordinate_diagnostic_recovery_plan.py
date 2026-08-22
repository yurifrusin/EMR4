from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-edit-argument-result-coordinate-"
    "diagnostic-recovery"
)
SUCCESSOR_OPERATION_ID = (
    "deepseek-native-harness-provider-free-edit-coordinate-future-runner-"
    "integration-rehearsal"
)
PLAN = ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT = ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"


def test_plan_freezes_the_narrow_provider_free_real_edit_diagnostic() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Timestamp:" in text and "Australia/Brisbane" in text
    assert "Status: frozen for provider-free implementation" in text
    assert "internal orchestration/Harness diagnostic" in text
    assert "provider_free_authored_synthetic_real_edit_argument_result_fixture" in text
    assert "all nine variants" in text
    assert "real accepted rc.7 `edit` tool" in text
    assert "No native Harness worker" in text
    assert "ordinary-practice enablement" in text
    assert "docs/branding/" in text
    assert "git add ." in text and "git add -A" in text


def test_plan_owns_no_product_or_api_spine_surface() -> None:
    text = PLAN.read_text(encoding="utf-8")
    owned = text[text.index("## Owned paths") : text.index("## Acceptance")]
    assert "app/" not in owned
    assert "docs/api-spine/" not in owned
    assert "migration" not in owned.lower()
    assert "No EMR4 API Spine" in text


def test_threat_delta_forbids_prose_routing_and_runtime_escalation() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "Human-readable error prose becomes a routing interface" in text
    assert "never parse or retain error text" in text
    assert "Native Harness, worker, model, provider and broker counts are fixed at zero" in text
    assert "cannot recover the occupied model's" in text


def test_preplanning_receipt_has_five_sources_and_lane_dispositions() -> None:
    receipt = json.loads(
        (
            ROOT
            / "orchestration/agent_inbox/codex/deepseek-native-harness-provider-free-edit-argument-result-coordinate-diagnostic-recovery-preplanning-receipt.json"
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
    assert receipt["parallelism_assessment"]["parallel_work_packages"] == []


def test_active_latch_is_the_operation_or_its_exact_in_progress_successor() -> None:
    latch = json.loads(
        (
            ROOT
            / "orchestration/continuity/ariadne-active-operation-latch/current.json"
        ).read_bytes()
    )
    assert latch["operation_id"] in {OPERATION_ID, SUCCESSOR_OPERATION_ID}
    assert latch["status"] == "in_progress"
    assert latch["user_attention"]["required"] is False
    assert latch["terminal_response"]["permitted"] is False


def test_manual_git_prose_rejection_is_preserved_beside_corrected_receipt() -> None:
    root = ROOT / "orchestration" / "agent_inbox" / "codex"
    stem = (
        "deepseek-native-harness-provider-free-edit-argument-result-coordinate-"
        "diagnostic-recovery-implementation-precommit"
    )
    rejected = json.loads(
        (root / f"{stem}-attempt-001-rejected-receipt.json").read_bytes()
    )
    corrected = json.loads((root / f"{stem}-receipt.json").read_bytes())
    assert rejected["status"] == "revision_required"
    assert "git_refs_evidence_manual_object_id_forbidden" in rejected["reasons"]
    assert corrected["status"] == "passed"
    assert corrected["git_ref_evidence_binding"]["manually_supplied_object_id_count"] == 0
