import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-context-fabric-source-owned-truth-conditional-command-reorientation"
PARENT = "ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair"
SOURCE_HEAD = "037eed060d4519f2f3d6721135143ecb6f70e358"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_reorientation_remains_accepted_after_descendant_advances() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] >= 276
    assert compass["map_revision"] >= 258
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == (
        "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
    )
    node = _node(graph)
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_reorientation_opens_no_runtime_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "repository-only architecture",
        "read-only and expiring",
        "one logical watcher",
        "cf-d2",
        "patient/product/clinical",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_names_inert_ddl_next_and_runtime_durability_later() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()

    assert "inert relational representation passes" in joined
    assert "inert-ddl lowering" in joined
    assert "persistent operational state" in joined
    assert "no database, watcher" in compass["orientation_statement"].lower()


def test_accepted_evidence_binds_review_and_human_summary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    evidence = _node(graph)["evidence"]

    assert (
        "orchestration/agent_inbox/codex/"
        "raisa-context-fabric-source-owned-truth-reorientation-vertex-review-receipt.json"
        in evidence["receipts"]
    )
    assert (
        "orchestration/human_inbox/yuri/"
        "2026-08-12--context-fabric-source-owned-truth-conditional-command-reorientation.md"
        in evidence["closeouts"]
    )
