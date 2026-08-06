import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "fresh-generation-rehearsal"
)
SOURCE_HEAD = "9516b85542a4de1fcef305423ec15fd34f7731aa"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_rayleen_fresh_generation_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 224
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 206
    assert compass["source_graph_revision"] == 224
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "live-source observation boundary is next" in (
        compass["orientation_statement"]
    )


def test_fresh_generation_authority_remains_unmounted_and_atomic():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = graph["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "independently authored synthetic",
        "either expiry blocks",
        "observer",
        "atomic bureau grants",
    ):
        assert phrase in notes


def test_fresh_generation_unresolved_gates_remain_explicit():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    unresolved = " ".join(graph["nodes"][-1]["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "product-derived",
        "financial",
        "real databases",
        "live observation",
        "event transport",
        "watchers/feeds",
        "product reads",
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


def test_compass_next_candidate_is_architecture_only_and_not_live():
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "architecture-only",
        "default-off",
        "payload-free",
        "separately authorised fresh-read",
        "live observation",
        "real data",
    ):
        assert phrase in joined
