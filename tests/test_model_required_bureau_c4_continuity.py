import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "model-required-bureau-c4-allowlisted-actuator-simulator"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_c4_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 214
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["coordinates"]["source_head"] == (
        "955b6a566f7097f58929dcb2fa9c4ed0aaad8b29"
    )
    assert compass["map_revision"] >= 196
    assert compass["source_graph_revision"] >= 214
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    assert "exact disposable C5 planning is next" in journey["outcome"]


def test_c4_node_preserves_every_live_effect_boundary():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "c5",
        "disposable non-phi target",
        "provider/model",
        "human authority",
        "real databases",
        "cloud/iam",
        "product routes",
        "patient",
        "clinical",
        "update",
        "production",
        "deployment",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_c4_compass_preserves_context_fabric_as_candidate_horizon():
    compass = load("orchestration/continuity/emr4-compass.json")
    fabric = next(
        item
        for item in compass["programme_support_horizon"]
        if item["id"] == "raisa-practice-context-fabric"
    )
    assert fabric["status"] == "candidate"
    assert fabric["boundary_changes"] == []
    assert "C5" in compass["current_position"]["unlocks"][0]
