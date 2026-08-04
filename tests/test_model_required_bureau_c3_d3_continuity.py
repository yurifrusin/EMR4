import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "model-required-bureau-c3-d3"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_c3_d3_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 211
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 192
    assert compass["source_graph_revision"] == 211
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "genuine material choice" in compass["orientation_statement"]


def test_c3_d3_node_preserves_every_material_gate():
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
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


def test_compass_records_the_real_next_user_decision_without_opening_it():
    compass = load("orchestration/continuity/emr4-compass.json")
    decision = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"] == "select-model-required-bureau-next-material-gate"
    )
    assert "paired A3/B3" in decision["question"]
    assert "Yuri must select" in decision["required_before"]
    current = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "provider" in current
    assert "actuator" in current
