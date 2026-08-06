import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-practice-context-fabric-patient-free-temporal-weave"
SOURCE_HEAD = "f32004a2f39ac769ba746afe2663813f7c422d8a"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_patient_free_temporal_weave_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 219
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 201
    assert compass["source_graph_revision"] == 219
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "patient-free temporal weave" in compass["orientation_statement"]
    assert "intent-shaped temporal retrieval rehearsal" in compass["orientation_statement"]


def test_context_fabric_horizon_records_temporal_acceptance_and_next_dependency():
    compass = load("orchestration/continuity/emr4-compass.json")
    horizon = next(
        item
        for item in compass["programme_support_horizon"]
        if item["id"] == "raisa-practice-context-fabric"
    )
    assert horizon["status"] == "active"
    joined = " ".join(horizon["prerequisites"] + horizon["evidence"]).lower()
    for phrase in (
        "patient-free temporal weave",
        "intent-shaped retrieval rehearsal",
        "temporal-weave-contract.schema.json",
        "review-1-receipt.json",
        "review-evidence-reconciliation-receipt.json",
        "temporal-weave-closeout.md",
    ):
        assert phrase in joined


def test_next_descendant_keeps_live_and_future_bureau_boundaries_closed():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = graph["nodes"][-1]
    opening = node["authority"]["authorized_openings"][0]
    assert "provider-free patient-free unmounted" in opening["scope"]
    assert "no patient/product data" in opening["scope"]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "clinical",
        "product-derived",
        "real databases",
        "event transport",
        "watchers",
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
        "requests/referrals",
        "prescribing/medicines",
        "billing/claims",
    ):
        assert phrase in unresolved


def test_branded_workspaces_do_not_become_authority_boundaries():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    notes = " ".join(graph["nodes"][-1]["authority"]["notes"])
    assert "Reception One and Clinician One are branded workspace families" in notes
    assert "atomic Bureau grants remain backend-owned" in notes
