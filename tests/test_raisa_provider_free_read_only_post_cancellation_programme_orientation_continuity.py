from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-read-only-post-cancellation-programme-orientation"
SOURCE_HEAD = "74da22d5372299eb2d2e38bb2266b76c89a97035"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_orientation_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 314
    assert compass["map_revision"] >= 296
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_compass_selects_read_only_arrival_convergence_without_product_meaning() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "arrival/check-in command-family convergence review" in compass[
        "current_position"
    ]["outcome"]
    assert "No A5.1 feature flag" in " ".join(
        compass["current_position"]["does_not_solve"]
    )
    assert "Continuity 314 / Compass 296" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-read-only-post-cancellation-programme-orientation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-provider-free-read-only-post-cancellation-programme-orientation-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--post-cancellation-programme-orientation.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
