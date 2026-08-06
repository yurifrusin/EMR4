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
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    assert graph["graph_revision"] >= 224
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] >= 206
    assert compass["source_graph_revision"] >= 224
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])


def test_fresh_generation_authority_remains_unmounted_and_atomic():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
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
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    unresolved = " ".join(node["unresolved_gates"]).lower()
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


def test_accepted_architecture_descendant_still_opens_no_live_source():
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "authored-synthetic",
        "without a live source",
        "live observation",
        "real patient/product data",
    ):
        assert phrase in joined
