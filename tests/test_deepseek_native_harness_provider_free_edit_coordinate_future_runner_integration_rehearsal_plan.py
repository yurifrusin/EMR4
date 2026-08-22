from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-edit-coordinate-future-runner-"
    "integration-rehearsal"
)
PLAN = ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT = ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"


def test_plan_freezes_the_narrow_provider_free_runner_integration() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Timestamp:" in text and "Australia/Brisbane" in text
    assert "Status: frozen for provider-free implementation" in text
    assert "provider_free_authored_synthetic_real_edit_future_runner_integration" in text
    assert "six real tool executions" in text
    assert "three typed pre-dispatch denials" in normalized
    assert "JavaScript and accepted Python classification agree" in text
    assert "No native Harness worker" in text
    assert "ordinary-practice enablement" in text
    assert "docs/branding/" in text
    assert "git add ." in text and "git add -A" in text


def test_plan_and_threat_own_no_product_or_api_spine_surface() -> None:
    text = PLAN.read_text(encoding="utf-8")
    owned = text[text.index("## Owned paths") : text.index("## Acceptance")]
    assert "app/" not in owned
    assert "docs/api-spine/" not in owned
    assert "No EMR4 API Spine" in text
    threat = THREAT.read_text(encoding="utf-8")
    assert "Human-readable rc.7 semantic errors remain a routing interface" in threat
    assert "Count real `ToolRuntime.execute` calls per variant" in threat
    assert "Cross-check every JavaScript release" in threat
    assert "cannot prove that a future" in threat


def test_preplanning_receipt_has_five_sources_and_lane_dispositions() -> None:
    receipt = json.loads(
        (
            ROOT
            / "orchestration/agent_inbox/codex/deepseek-native-harness-provider-free-edit-coordinate-future-runner-integration-rehearsal-preplanning-receipt.json"
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


def test_operation_is_active_or_durably_accepted_before_the_current_latch() -> None:
    latch = json.loads(
        (
            ROOT
            / "orchestration/continuity/ariadne-active-operation-latch/current.json"
        ).read_bytes()
    )
    assert latch["status"] == "in_progress"
    assert latch["user_attention"]["required"] is False
    assert latch["terminal_response"]["permitted"] is False
    if latch["operation_id"] != OPERATION_ID:
        graph = json.loads(
            (
                ROOT / "orchestration/continuity/emr4-continuity-graph.json"
            ).read_bytes()
        )
        assert OPERATION_ID in {node["id"] for node in graph["nodes"]}


def test_first_binding_failure_is_preserved_and_had_no_external_effect() -> None:
    value = json.loads(
        (
            ROOT
            / "orchestration/continuity/deepseek-native-harness-provider-free-edit-coordinate-future-runner-integration-rehearsal/preflight-attempt-001-failure-terminal.json"
        ).read_bytes()
    )
    assert value["status"] == "failed_closed"
    assert value["failure_coordinate"] == "input_binding_rejected"
    assert value["worker_model_provider_request_count"] == 0
    assert value["retry_count"] == 0
    assert value["disposable_root_absent"] is True
