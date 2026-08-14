from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-selected-appointment-practitioner-reassignment-composition"
SOURCE_HEAD = "f085fc98ead21a3e7929ee9adbda81abfc7542c9"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_practitioner_composition_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 288
    assert compass["map_revision"] >= 270
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_binds_workers_active_truth_and_closed_command() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "review/test_reception_one_practitioner_reassignment_action.py",
        "orchestration/agent_inbox/codex/raisa-reception-one-practitioner-reassignment-deepseek-worker-output.json",
        "orchestration/agent_inbox/antigravity/raisa-reception-one-practitioner-reassignment-gemini-review-receipt.json",
        "docs/ariadne-mandatory-parallelism-efficacy-control.md",
        "docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-closeout.md",
    } <= evidence
    joined = " ".join(node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]).lower()
    for phrase in ("both deltas at zero", "active", "no raw fallback", "another command", "watcher/runtime", "deployment"):
        assert phrase in joined


def test_compass_records_compact_action_orientation_descendant() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    assert "compact" in unlocks
    assert "Continuity 288 / Compass 270" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-practitioner-reassignment.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head
