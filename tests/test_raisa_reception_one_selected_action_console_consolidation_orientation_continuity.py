from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-selected-action-console-consolidation-orientation"
SOURCE_HEAD = "2d602cfd822235977676bfe9ee8d8dc0a14714fe"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_console_orientation_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 289
    assert compass["map_revision"] >= 271
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_binds_parallel_review_and_distinct_authority() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-native-analysis.md",
        "orchestration/agent_inbox/antigravity/raisa-reception-one-selected-action-console-consolidation-orientation-gemini-review-receipt.json",
        "orchestration/continuity/raisa-reception-one-selected-action-console-consolidation-orientation/selected-action-console-orientation-contract.json",
        "docs/raisa-reception-one-selected-action-console-consolidation-orientation-closeout.md",
    } <= evidence
    joined = " ".join(node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]).lower()
    for phrase in (
        "at most one",
        "distinct",
        "no generic dispatcher",
        "fresh reconciliation",
        "product data",
        "deployment",
    ):
        assert phrase in joined


def test_compass_names_progressive_disclosure_implementation_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    assert "progressive-disclosure" in unlocks
    assert "Continuity 289 / Compass 271" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-selected-action-console-consolidation-orientation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-action-console-orientation.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head
