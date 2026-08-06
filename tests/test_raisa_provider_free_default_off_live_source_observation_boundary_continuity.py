import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-default-off-live-source-observation-boundary"
SOURCE_HEAD = "fdbda21b28371778f5e50b0bc2cbd870bbf40e42"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_live_source_observation_continuity_and_compass_are_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 225
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 207
    assert compass["source_graph_revision"] == 225
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "unmounted authored-synthetic observation-to-signal" in (
        compass["orientation_statement"]
    )


def test_observer_authority_and_impact_remain_closed() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "observer is not truth",
        "no returned-data",
        "backend impact floors",
        "bounded full invalidation",
        "default-off",
        "zero-effect",
        "live sources",
    ):
        assert phrase in notes


def test_unresolved_live_and_real_data_gates_remain_explicit() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "product-derived",
        "historical-phi",
        "source/event family",
        "transport principal",
        "database/outbox/feed/watcher/listener",
        "checkpoint",
        "product reads",
        "persistence",
        "live runtime",
        "provider calls",
        "clinical",
        "command/write",
        "deployment",
        "production",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_next_candidate_is_synthetic_and_unmounted_only() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "pure typed observation",
        "authored-synthetic",
        "without a live source",
        "real patient/product data",
        "live observation/feed/watcher",
        "database/event transport",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
