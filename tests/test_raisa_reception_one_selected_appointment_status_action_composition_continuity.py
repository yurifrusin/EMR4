from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-selected-appointment-status-action-composition"
SOURCE_HEAD = "b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_status_action_node_is_accepted_at_exact_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    nodes = {node["id"]: node for node in graph["nodes"]}
    assert graph["graph_revision"] >= 283
    assert compass["map_revision"] >= 265
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert nodes[NODE_ID]["status"] == "accepted"
    assert nodes[NODE_ID]["kind"] == "implementation"
    assert nodes[NODE_ID]["coordinates"]["source_head"] == SOURCE_HEAD
    assert nodes[NODE_ID]["authority"]["authorized_openings"] == []


def test_continuity_binds_exact_evidence_and_closed_authority() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "review/test_reception_one_status_action.py",
        "orchestration/continuity/raisa-reception-one-selected-appointment-status-action-composition/selected-appointment-status-action-evidence.json",
        "docs/raisa-reception-one-selected-appointment-status-action-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-status-action-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--reception-one-selected-appointment-status-action-composition.md",
    } <= evidence
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "graphql remains read-only",
        "raw fallback",
        "another command family",
        "patient channel",
        "watcher/runtime",
        "deployment",
    ):
        assert phrase in joined


def test_compass_records_completion_and_read_only_orientation_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    limits = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "read-only compass and baton orientation" in unlocks
    assert "without inferring another command" in unlocks
    assert "no additional appointment command family" in limits
    assert "continuity 283 / compass 265" in compass["orientation_statement"].lower()


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-selected-appointment-status-action-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-status-action-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--reception-one-selected-appointment-status-action-composition.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head
