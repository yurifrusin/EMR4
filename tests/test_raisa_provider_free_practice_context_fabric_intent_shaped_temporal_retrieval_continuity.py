import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval"
)
SOURCE_HEAD = "b24b56bda296f3713b5e2c0e52545c749e71540a"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_intent_shaped_retrieval_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    assert graph["graph_revision"] >= 220
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] >= 202
    assert compass["source_graph_revision"] >= 220
    assert compass["current_position"]["node_id"] == (
        "raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping"
    )
    assert "model-required Practice Context Fabric intent-shaping" in compass[
        "orientation_statement"
    ]


def test_context_fabric_horizon_records_retrieval_acceptance_and_next_dependency():
    compass = load("orchestration/continuity/emr4-compass.json")
    horizon = next(
        item
        for item in compass["programme_support_horizon"]
        if item["id"] == "raisa-practice-context-fabric"
    )
    joined = " ".join(horizon["prerequisites"] + horizon["evidence"]).lower()
    for phrase in (
        "intent-shaped retrieval rehearsal",
        "occupied-rehearsal-evidence.json",
        "provider-free adapter",
        "intent-shaped-temporal-retrieval-contract.schema.json",
        "temporal-retrieval-review-receipt.json",
        "temporal-retrieval-rehearsal-closeout.md",
    ):
        assert phrase in joined


def test_next_model_required_descendant_is_exactly_bounded():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    opening = node["authority"]["authorized_openings"][0]
    scope = opening["scope"].lower()
    for phrase in (
        "authored-synthetic",
        "gemini-2.5-flash",
        "bernie vertex development project",
        "australia-southeast1",
        "thinking budget",
        "closed schema",
        "deterministic proofreader",
        "call/cost ledger",
        "no fallback",
        "no patient/product/runtime/command",
    ):
        assert phrase in scope


def test_live_clinical_command_and_protected_boundaries_remain_closed():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "clinical",
        "product-derived",
        "financial",
        "real sources",
        "databases",
        "watchers",
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


def test_branded_workspaces_and_future_bureaus_have_no_inherited_authority():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    notes = " ".join(node["authority"]["notes"])
    assert "Reception One and Clinician One are branded workspace families" in notes
    assert "atomic Bureau grants remain backend-owned" in notes
    assert "requests/referrals" in notes
    assert "medicines/prescribing" in notes
    assert "billing/claims" in notes
