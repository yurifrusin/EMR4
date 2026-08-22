from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / (
    "raisa-provider-free-read-only-check-in-server-start-attach-created-state-"
    "failure-coordinate-diagnosis-plan.md"
)
THREAT = ROOT / "docs" / "security" / (
    "raisa-provider-free-read-only-check-in-server-start-attach-created-state-"
    "failure-coordinate-diagnosis-threat-model-delta.md"
)
RECEIPT = ROOT / "orchestration" / "agent_inbox" / "codex" / (
    "raisa-check-in-server-start-attach-created-state-diagnosis-preplanning-"
    "receipt.json"
)


def test_plan_freezes_object_noncreating_read_only_diagnosis() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Status: `frozen`" in text
    assert "docker.exe start --help" in text
    assert "docker.exe version" in text
    assert "may not name a container, network, image or volume" in normalized
    assert "must not implement the repair or authorise an occupied run" in normalized
    assert "No attempt 007 may begin" in text
    assert "`cli_option_surface_mismatch`" in text


def test_threat_delta_denies_hidden_execution_and_attribution() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "adds no Docker object" in text
    assert "One closed coordinate vocabulary" in text
    assert "Stop before subprocess" in text
    assert "cannot prove" in text


def test_five_source_receipt_and_parallelism_assessment_pass() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert [lane["disposition"] for lane in receipt["parallelism_assessment"]["lanes"]] == [
        "declined",
        "declined",
        "declined",
    ]
