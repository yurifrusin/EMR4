import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "model-required-bureau-c3-d3"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_c3_d3_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 211
    assert any(node["id"] == NODE_ID for node in graph["nodes"])
    assert compass["map_revision"] >= 192
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])


def test_c3_d3_node_preserves_every_material_gate():
    node = next(
        item
        for item in load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
        if item["id"] == NODE_ID
    )
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "provider/model",
        "product read",
        "writes",
        "actuator",
        "imports",
        "migrations",
        "activation",
        "deployment",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_compass_preserves_c3_d3_material_boundary_history():
    compass = load("orchestration/continuity/emr4-compass.json")
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    assert "C3/D3 pass" in journey["outcome"]
