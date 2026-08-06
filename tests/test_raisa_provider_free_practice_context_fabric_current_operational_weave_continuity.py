import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-practice-context-fabric-current-operational-weave"
SOURCE_HEAD = "d8bc059212e65a6ed2d7ac8d57734096d14b9139"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_current_operational_weave_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 218
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 200
    assert compass["source_graph_revision"] == 218
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "Current operational weave" in compass["orientation_statement"]
    assert "patient-free temporal weave" in compass["orientation_statement"]


def test_context_fabric_horizon_records_acceptance_and_next_dependency():
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
        "review-1-receipt.json",
        "review-count-reconciliation-receipt.json",
        "operational-weave-closeout.md",
    ):
        assert phrase in joined


def test_temporal_descendant_keeps_closed_boundaries_closed():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = graph["nodes"][-1]
    opening = node["authority"]["authorized_openings"][0]
    assert "patient-free" in opening["scope"]
    assert "no real event transport" in opening["scope"]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "clinical",
        "product-derived",
        "real databases",
        "event transport",
        "persistence",
        "operational retention",
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
