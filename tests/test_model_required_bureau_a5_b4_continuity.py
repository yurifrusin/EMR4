import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "model-required-bureau-a5-b4-command-runtime"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_a5_b4_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 213
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 194
    assert compass["source_graph_revision"] == 213
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "C4 allowlisted-actuator simulator next" in compass["orientation_statement"]


def test_a5_b4_node_preserves_closed_effect_boundaries():
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
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


def test_compass_consumes_superseded_a3_b3_material_fork():
    compass = load("orchestration/continuity/emr4-compass.json")
    decision_ids = {item["id"] for item in compass["user_owned_decisions"]}
    assert "select-model-required-bureau-post-a3-b3-material-gate" not in decision_ids
    assert "provider-free C4" in compass["current_position"]["unlocks"][0]
