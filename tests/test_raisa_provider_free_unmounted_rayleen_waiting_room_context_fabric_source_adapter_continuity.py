import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "source-adapter"
)
SOURCE_HEAD = "12fbab157551954018e781810e4b100f05698dfb"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_rayleen_source_adapter_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 222
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 204
    assert compass["source_graph_revision"] == 222
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "source adapter passes at exact reviewed HEAD" in compass[
        "orientation_statement"
    ]


def test_source_adapter_authority_is_closed_and_atomic_bureau_grants_remain():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = graph["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "cannot invoke or refresh",
        "recomputes the complete result",
        "live database/feed watcher",
        "atomic bureau grants",
    ):
        assert phrase in notes


def test_source_adapter_unresolved_gates_remain_explicit():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    unresolved = " ".join(graph["nodes"][-1]["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "product-derived",
        "financial",
        "real databases",
        "live watchers/feeds",
        "persistence",
        "external evidence",
        "provider calls",
        "requests/referrals",
        "prescribing/medicines",
        "billing/claims",
        "commands/writes",
        "deployment",
        "production",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_compass_next_candidate_is_provider_free_and_not_a_live_watcher():
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "provider-free",
        "invalidation/reassembly",
        "authored-synthetic",
        "live watchers",
        "real data",
    ):
        assert phrase in joined
