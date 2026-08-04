import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_successor_lane_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 210
    assert graph["nodes"][-1]["id"] == "model-required-bureau-provider-free-successor-lanes"
    assert compass["map_revision"] == 191
    assert compass["source_graph_revision"] == 210
    assert compass["current_position"]["node_id"] == graph["nodes"][-1]["id"]
    assert "C3/D3 proceed" in compass["orientation_statement"]


def test_successor_node_preserves_closed_material_boundaries():
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    unresolved = " ".join(node["unresolved_gates"])
    for phrase in ("occupied model", "product read", "writes", "actuator", "Deployment", "Pages", "protected"):
        assert phrase.lower() in unresolved.lower()
