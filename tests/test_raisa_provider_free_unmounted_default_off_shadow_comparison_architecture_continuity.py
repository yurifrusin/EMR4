import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-default-off-shadow-comparison-architecture"
PARENT = "raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal"
SOURCE_HEAD = "e1dca1c6dc5d3f3e241548f80a226e5bb776417f"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_shadow_architecture_is_the_accepted_continuity_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 249
    assert compass["map_revision"] == 231
    assert compass["source_graph_revision"] == 249
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_shadow_architecture_opens_no_runtime_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]).lower()
    for phrase in ("provider-free", "no application route", "four raw", "24-field", "15-field", "twelve", "forty-six", "no product hashing", "patient/product data", "protected refs"):
        assert phrase in joined


def test_compass_names_authored_synthetic_shadow_rehearsal_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join([current["strategic_role"], current["why_now"], current["outcome"]] + current["unlocks"] + current["does_not_solve"]).lower()
    assert "authored-synthetic inputs" in joined
    assert "byte-for-byte unchanged" in joined
    assert "at most one minimized diagnostic record" in joined
    assert "continuity 249 / compass 231" in compass["orientation_statement"].lower()
    assert "46 hostile mutations" in compass["orientation_statement"]


def test_evidence_binds_receipts_acceptance_and_human_summary() -> None:
    evidence = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))["evidence"]
    assert "orchestration/agent_inbox/codex/raisa-default-off-shadow-comparison-architecture-preplanning-receipt.json" in evidence["receipts"]
    assert "orchestration/agent_inbox/codex/raisa-default-off-shadow-comparison-architecture-candidate-precommit-receipt.json" in evidence["receipts"]
    assert "orchestration/human_inbox/yuri/2026-08-12--default-off-shadow-comparison-architecture.md" in evidence["closeouts"]
