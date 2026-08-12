import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-conditional-command-admission-rehearsal"
PARENT = "raisa-context-fabric-source-owned-truth-conditional-command-reorientation"
SOURCE_HEAD = "f465d6a6536ea2e69eec8df2ed1c2f9f65c24f6c"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_rehearsal_is_the_accepted_continuity_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 246
    assert compass["map_revision"] == 228
    assert compass["source_graph_revision"] == 246
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_rehearsal_opens_no_runtime_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "provider-free",
        "no route or database",
        "thirty-seven",
        "thirty-two",
        "patient/product data",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_names_common_kernel_design_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()

    assert "common kernel" in joined
    assert "raw compatibility routes" in joined
    assert "37 canonical cases" in compass["orientation_statement"]
    assert "32 hostile mutations" in compass["orientation_statement"]


def test_evidence_binds_failure_receipt_and_human_summary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    evidence = _node(graph)["evidence"]

    assert (
        "orchestration/agent_inbox/codex/"
        "raisa-conditional-command-admission-rehearsal-source-head-draft-failure-receipt.json"
        in evidence["receipts"]
    )
    assert (
        "orchestration/human_inbox/yuri/"
        "2026-08-12--provider-free-unmounted-conditional-command-admission-rehearsal.md"
        in evidence["closeouts"]
    )
