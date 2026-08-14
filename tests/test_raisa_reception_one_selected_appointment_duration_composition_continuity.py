from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-selected-appointment-duration-composition"
SOURCE_HEAD = "f397a3706f3b870b8436eb3993bd90c6c0c742a8"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_duration_composition_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 287
    assert compass["map_revision"] >= 269
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_binds_three_worker_lanes_fresh_truth_and_closed_command() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "review/test_reception_one_duration_action.py",
        "orchestration/agent_inbox/deepseek/raisa-reception-one-duration-test-worker-receipt.json",
        "orchestration/agent_inbox/antigravity/raisa-reception-one-duration-composition-gemini-review-receipt.json",
        "docs/ariadne-mandatory-parallelism-efficacy-control.md",
        "docs/raisa-reception-one-selected-appointment-duration-composition-closeout.md",
    } <= evidence
    joined = " ".join(node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]).lower()
    for phrase in ("start delta at zero", "no raw fallback", "practitioner-only", "another command", "watcher/runtime", "deployment"):
        assert phrase in joined


def test_compass_records_practitioner_only_descendant() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    assert "practitioner-only" in unlocks
    assert "Continuity 287 / Compass 269" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-selected-appointment-duration-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-duration-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-duration-composition.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head
