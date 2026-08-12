from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-status-confirm-preflight-idempotency-expectation-repair"
PARENT = (
    "raisa-provider-free-read-only-status-confirm-route-mounting-admission-review"
)
SOURCE_HEAD = "ec9aa1b1d2813b3e864b37f331ac6b587816610a"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_preflight_repair_is_the_accepted_current_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 267
    assert compass["map_revision"] >= 249
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_preflight_repair_opens_no_runtime_authority() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "test expectation only",
        "application source remain unchanged",
        "125 status-confirm lineage",
        "product command",
        "providers",
        "protected integration",
    ):
        assert phrase in joined


def test_next_direction_is_unmounted_composition() -> None:
    current = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free unmounted",
        "status-only adapter",
        "server authority/session",
        "physical seam",
        "closed response mapper",
        "route execution",
        "unknown commit",
        "protected-ref",
    ):
        assert phrase in joined
