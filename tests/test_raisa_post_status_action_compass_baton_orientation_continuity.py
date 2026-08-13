from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-post-status-action-compass-baton-orientation"
SOURCE_HEAD = "4b6a060c6b1aab42e1062c41d48d109f683abe00"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_orientation_is_current_at_exact_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 284
    assert compass["map_revision"] >= 266
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_compass_names_truth_parity_rehearsal_and_limits() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "truth-parity conformance rehearsal" in compass["current_position"]["outcome"]
    assert "Feature parity" in " ".join(compass["current_position"]["does_not_solve"])
    assert "Continuity 284 / Compass 266" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-post-status-action-compass-baton-orientation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-post-status-action-compass-baton-orientation-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--post-status-action-truth-parity-orientation.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head
