import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-source-specific-durability-architecture"
SOURCE_HEAD = "14e8d3257b9531601260bef094c73e08a9c7b92d"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_durability_architecture_continuity_and_compass_are_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 227
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 209
    assert compass["source_graph_revision"] == 227
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "durability state-machine rehearsal" in compass["orientation_statement"]


def test_durability_architecture_authority_remains_closed() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "provider-free",
        "unmounted",
        "payload-free",
        "principals remain distinct",
        "specifications",
        "no database",
        "no source",
        "no product read",
        "no provider",
        "no command",
        "no runtime",
    ):
        assert phrase in notes


def test_unresolved_live_and_real_data_gates_remain_explicit() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "product-derived",
        "historical-phi",
        "database/outbox/feed/watcher/listener/source",
        "operational credentials",
        "migrations",
        "checkpoint persistence",
        "product reads",
        "providers",
        "clinical",
        "command/write",
        "deployment",
        "production",
        "release",
        "pages",
        "protected refs",
    ):
        assert phrase in unresolved


def test_next_candidate_is_pure_in_memory_rehearsal_only() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "pure in-memory",
        "provider-free",
        "redelivery",
        "gaps",
        "restart",
        "without mounting a source",
        "migrations",
        "live database/outbox/feed/watcher/listener/source",
        "operational credentials",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
