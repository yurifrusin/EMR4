from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-post-cf-d2-compass-baton-orientation"
SOURCE_HEAD = "edba8f57380a48fd98decc332608349f2d9012e6"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_orientation_node_is_accepted_at_exact_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    nodes = {node["id"]: node for node in graph["nodes"]}
    journeys = {item["node_id"]: item for item in compass["journey"]}
    assert graph["graph_revision"] >= 282
    assert compass["map_revision"] >= 264
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert nodes[NODE_ID]["status"] == "accepted"
    assert nodes[NODE_ID]["kind"] == "review"
    assert nodes[NODE_ID]["coordinates"]["source_head"] == SOURCE_HEAD
    assert nodes[NODE_ID]["authority"]["authorized_openings"] == []
    assert NODE_ID in journeys


def test_orientation_evidence_and_closed_alternatives_are_bound() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    assert {
        "docs/raisa-post-cf-d2-compass-baton-orientation.md",
        "docs/raisa-post-cf-d2-compass-baton-orientation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-post-cf-d2-compass-baton-orientation-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--post-cf-d2-compass-baton-orientation.md",
    } <= evidence
    for phrase in (
        "status proposal/confirm",
        "raw fallback",
        "stage 3b",
        "patient channels",
        "another event",
        "watcher/runtime",
        "deployment",
    ):
        assert phrase in joined


def test_compass_points_to_selected_visible_successor() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    limits = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "selected-appointment status-action composition" in unlocks
    assert "existing status vocabulary" in unlocks
    assert "not yet implemented" in limits
    assert "continuity 282 / compass 264" in compass["orientation_statement"].lower()


def test_orientation_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-post-cf-d2-compass-baton-orientation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-post-cf-d2-compass-baton-orientation-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--post-cf-d2-compass-baton-orientation.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head
