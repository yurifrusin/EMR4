from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-selected-action-console-progressive-disclosure-composition"
SOURCE_HEAD = "1d9e58fd2624f87b8b3def538297054999e7bef3"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_action_console_composition_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 290
    assert compass["map_revision"] >= 272
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_binds_presentation_safety_and_independent_review() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "docs/diary/meta-grid.js",
        "review/test_reception_one_selected_action_console.py",
        "orchestration/continuity/raisa-reception-one-selected-action-console-progressive-disclosure-composition/selected-action-console-composition-evidence.json",
        "orchestration/agent_inbox/antigravity/raisa-reception-one-selected-action-console-progressive-disclosure-composition-gemini-review-receipt.json",
        "docs/raisa-reception-one-selected-action-console-progressive-disclosure-composition-closeout.md",
    } <= evidence
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "zero-or-one",
        "route-inert",
        "discard",
        "no generic dispatcher",
        "automatic sequencing",
        "route_intercepted_browser",
        "compound",
    ):
        assert phrase in joined


def test_compass_names_multi_change_atomicity_orientation_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    assert "several appointment changes" in unlocks
    assert "Continuity 290 / Compass 272" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-selected-action-console-progressive-disclosure-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-action-console-progressive-disclosure.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_handover_and_plan_keep_compound_execution_closed() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = (ROOT / "implementation_plan.md").read_text(encoding="utf-8")
    assert "Continuity 290 / Compass 272" in handover
    assert "multi-change request atomicity orientation" in handover
    assert "Automatic sequencing of single-field commands" in handover
    assert "read-only multi-change request atomicity" in plan
    assert "No watcher runtime" in plan
