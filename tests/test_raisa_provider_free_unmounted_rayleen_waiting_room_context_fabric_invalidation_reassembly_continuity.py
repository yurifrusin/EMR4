import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "invalidation-reassembly"
)
SOURCE_HEAD = "72b5f46146393c644ee8fbfa1bb9ee0869d8d994"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_rayleen_invalidation_reassembly_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 223
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 205
    assert compass["source_graph_revision"] == 223
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "fresh-generation rehearsal is next" in compass["orientation_statement"]


def test_invalidation_authority_is_inert_and_atomic_bureau_grants_remain():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = graph["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "cannot listen",
        "inert",
        "no replacement frame set",
        "atomic bureau grants",
    ):
        assert phrase in notes


def test_invalidation_unresolved_gates_remain_explicit():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    unresolved = " ".join(graph["nodes"][-1]["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "product-derived",
        "financial",
        "real databases",
        "event transport",
        "live watchers/feeds",
        "persistence",
        "fresh product reads",
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


def test_compass_next_candidate_is_provider_free_and_not_a_live_source():
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "provider-free",
        "fresh-generation",
        "older asynchronous results",
        "live source",
        "real data",
    ):
        assert phrase in joined
