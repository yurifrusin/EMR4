from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
    "extraction-rehearsal"
)
PARENT = (
    "raisa-provider-free-read-only-arrival-check-in-command-family-"
    "convergence-review"
)
SOURCE_HEAD = "8de886c5148b3259428c8c517674f10ea92d937e"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_check_in_adapter_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 316
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 298
    assert compass["source_graph_revision"] == 316
    assert compass["current_position"]["node_id"] == NODE_ID
    node = graph["nodes"][-1]
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []


def test_compass_keeps_runtime_closed_and_names_fresh_task_successor() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert "default-off A5.1 route" in current["outcome"]
    assert "fresh task" in current["outcome"]
    assert "No practice" in " ".join(current["does_not_solve"])
    assert "Continuity 316 / Compass 298" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/raisa-canonical-check-in-product-adapter-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--canonical-check-in-product-adapter-extraction-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
