from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-default-off-canonical-check-in-route-adapter-"
    "convergence-rehearsal"
)
PARENT = (
    "raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
    "extraction-rehearsal"
)
SOURCE_HEAD = "c82c3a741053a9c8da260aa62e1a968af22bb54e"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_default_off_check_in_route_convergence_is_current() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 317
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 299
    assert compass["source_graph_revision"] == 317
    assert compass["current_position"]["node_id"] == NODE_ID
    node = graph["nodes"][-1]
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []


def test_compass_keeps_product_admission_closed_and_names_harness_successor() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert "native DeepSeek Harness" in current["outcome"]
    assert "without changing A5.1 admission" in current["outcome"]
    assert "No ordinary practice" in " ".join(current["does_not_solve"])
    assert "Continuity 317 / Compass 299" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--default-off-canonical-check-in-route-adapter-convergence-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
