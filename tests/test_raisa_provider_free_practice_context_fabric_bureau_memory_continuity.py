import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-practice-context-fabric-bureau-memory-contract"
SOURCE_HEAD = "cb1b0a712f8ee5340e73d8adde19103af0d9ed97"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_context_fabric_contract_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert graph["graph_revision"] >= 217
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] >= 199
    assert compass["source_graph_revision"] >= 217
    assert "Context Fabric" in compass["orientation_statement"]
    assert "provider-free one-source adapter" in compass["orientation_statement"]


def test_context_fabric_horizon_is_active_and_bound_to_acceptance():
    compass = load("orchestration/continuity/emr4-compass.json")
    horizon = next(
        item
        for item in compass["programme_support_horizon"]
        if item["id"] == "raisa-practice-context-fabric"
    )
    assert horizon["status"] == "active"
    joined = " ".join(horizon["prerequisites"] + horizon["evidence"]).lower()
    for phrase in (
        "current operational weave",
        "patient-free temporal weave",
        "provider-free-acceptance-evidence.json",
        "repair-review-receipt.json",
        "contract-closeout.md",
    ):
        assert phrase in joined


def test_next_descendant_keeps_closed_boundaries_closed():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    opening = node["authority"]["authorized_openings"][0]
    assert opening["boundary"] == "api-change"
    assert "existing authorised" in opening["scope"]
    assert "no new product route or source" in opening["scope"]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "clinical",
        "product-derived",
        "real databases",
        "persistence",
        "retention",
        "provider calls",
        "external retrieval",
        "commands",
        "writes",
        "deployment",
        "production",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved
