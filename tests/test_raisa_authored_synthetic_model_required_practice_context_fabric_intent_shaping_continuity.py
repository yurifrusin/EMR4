import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-authored-synthetic-model-required-practice-context-fabric-"
    "intent-shaping"
)
SOURCE_HEAD = "44f341481b55f99a18a47838da0f2b7e43a2f73e"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_model_intent_shaping_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 221
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 203
    assert compass["source_graph_revision"] == 221
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "one source-reviewed Sydney Vertex call" in compass[
        "orientation_statement"
    ]


def test_consumed_provider_authority_and_closed_real_data_boundaries():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = graph["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    assert "no correction or post-success call remains open" in notes
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "clinical",
        "product-derived",
        "financial",
        "real databases",
        "watchers/feeds",
        "persistence",
        "operational retention",
        "external evidence",
        "product runtime",
        "prescribing",
        "referral",
        "billing",
        "commands",
        "writes",
        "deployment",
        "production",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_compass_next_candidate_is_provider_free_and_unmounted():
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "provider-free",
        "existing authorised current operational read shape",
        "unmounted",
        "real data",
        "runtime",
    ):
        assert phrase in joined


def test_context_fabric_horizon_records_occupied_evidence():
    compass = load("orchestration/continuity/emr4-compass.json")
    horizon = next(
        item
        for item in compass["programme_support_horizon"]
        if item["id"] == "raisa-practice-context-fabric"
    )
    joined = " ".join(horizon["prerequisites"] + horizon["evidence"]).lower()
    for phrase in (
        "occupied authored-synthetic model-required intent path",
        "occupied-rehearsal-evidence.json",
        "occupied-rehearsal-cost-ledger.json",
        "intent-shaping-rehearsal-closeout.md",
    ):
        assert phrase in joined
