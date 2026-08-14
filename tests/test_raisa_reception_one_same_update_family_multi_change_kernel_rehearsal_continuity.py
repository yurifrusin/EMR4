from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-same-update-family-multi-change-kernel-rehearsal"
SOURCE_HEAD = "3dd5f3b39ed98a2d562685d1d1567a359930c693"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_combined_update_kernel_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 292
    assert compass["map_revision"] >= 274
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_binds_atomic_commit_denial_replay_and_rollback() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py",
        "orchestration/agent_inbox/antigravity/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-gemini-review-receipt.json",
        "docs/ariadne-agent-error-correction-register-revision-272.md",
        "docs/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-closeout.md",
    } <= evidence
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "one closed command",
        "current appointment truth",
        "without retained effects",
        "fresh-session exact replay",
        "rolls every effect back",
        "provider_free_live_local_backend_postgresql_authored_synthetic",
    ):
        assert phrase in joined


def test_compass_names_combined_editor_composition_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    assert "one progressive reception one draft" in unlocks
    assert "existing canonical route" in unlocks
    assert "Continuity 292 / Compass 274" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-15--reception-one-same-update-family-multi-change-kernel-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-15" in head
        assert "Timestamp: 2026-08-15T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_handover_and_plan_keep_wider_runtime_closed() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = (ROOT / "implementation_plan.md").read_text(encoding="utf-8")
    assert "Continuity 292 / Compass 274" in handover
    assert "same_update_family_multi_change_editor_composition" in handover
    assert "Status remains distinct" in handover
    assert "same-update-family multi-change kernel rehearsal" in plan
    assert "No watcher runtime" in plan


def test_register_revision_272_binds_latest_contained_incident() -> None:
    register = _load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert register["register_revision"] == 272
    incident = register["incidents"][-1]
    assert incident["incident_id"] == "AER-0311"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
