import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_successor_lane_remains_accepted_history_after_c3_d3():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "model-required-bureau-provider-free-successor-lanes"
    )
    journey = next(
        item for item in compass["journey"] if item["node_id"] == node["id"]
    )
    assert graph["graph_revision"] >= 210
    assert node["status"] == "accepted"
    assert compass["map_revision"] >= 191
    assert compass["source_graph_revision"] >= 210
    assert "C3/D3 are active" in journey["outcome"]


def test_successor_node_preserves_closed_material_boundaries():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "model-required-bureau-provider-free-successor-lanes"
    )
    unresolved = " ".join(node["unresolved_gates"])
    for phrase in ("occupied model", "product read", "writes", "actuator", "Deployment", "Pages", "protected"):
        assert phrase.lower() in unresolved.lower()
