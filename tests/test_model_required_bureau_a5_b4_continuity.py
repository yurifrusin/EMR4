import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "model-required-bureau-a5-b4-command-runtime"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_a5_b4_continuity_remains_preserved_after_c4():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 214
    assert any(node["id"] == NODE_ID for node in graph["nodes"])
    assert compass["map_revision"] == 196
    assert compass["source_graph_revision"] == 214
    assert compass["current_position"]["node_id"] == (
        "model-required-bureau-c4-allowlisted-actuator-simulator"
    )
    assert "C4's provider-free" in compass["orientation_statement"]


def test_a5_b4_node_preserves_closed_effect_boundaries():
    node = next(
        item
        for item in load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
        if item["id"] == NODE_ID
    )
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "c4",
        "no real target",
        "c5",
        "patient-facing",
        "product/clinical data",
        "external event",
        "production",
        "deployment",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_compass_consumes_superseded_a3_b3_material_fork_and_records_c4_journey():
    compass = load("orchestration/continuity/emr4-compass.json")
    decision_ids = {item["id"] for item in compass["user_owned_decisions"]}
    assert "select-model-required-bureau-post-a3-b3-material-gate" not in decision_ids
    journey_ids = {item["node_id"] for item in compass["journey"]}
    assert "model-required-bureau-c4-allowlisted-actuator-simulator" in journey_ids
    assert "C5" in compass["current_position"]["unlocks"][0]
