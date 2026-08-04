import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "model-required-bureau-a3-b3-request-contract-recovery"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_a3_b3_recovery_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 212
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 193
    assert compass["source_graph_revision"] == 212
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "planned block is complete" in compass["orientation_statement"]


def test_a3_b3_recovery_node_preserves_every_material_gate():
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "product read",
        "commands",
        "writes",
        "actuator",
        "import",
        "migration",
        "patient",
        "clinical",
        "deployment",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_compass_consumes_a3_b3_choice_and_records_next_material_fork():
    compass = load("orchestration/continuity/emr4-compass.json")
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    assert "select-model-required-bureau-next-material-gate" not in decisions
    decision = decisions["select-model-required-bureau-post-a3-b3-material-gate"]
    assert "A4 product read" in decision["question"]
    assert "Yuri must select" in decision["required_before"]
    current = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "product" in current
    assert "actuator" in current
