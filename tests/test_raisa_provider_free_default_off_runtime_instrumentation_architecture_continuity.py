import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-default-off-runtime-instrumentation-architecture"
PARENT = "raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal"
SOURCE_HEAD = "ed52950f451af88892a8f469157ecf8c8567da81"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_runtime_instrumentation_architecture_remains_accepted() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 251
    assert compass["map_revision"] >= 233
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(row["node_id"] == NODE_ID for row in compass["journey"])
    node = _node(graph)
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_node_opens_no_runtime_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "provider-free", "no application route", "missing safe server-owned",
        "exactly four raw", "not serialized response", "single-assignment",
        "twenty-four", "sixty hostile", "no request context", "protected refs",
    ):
        assert phrase in joined


def test_compass_records_globally_disabled_scaffold_as_architecture_descendant() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    journey = next(row for row in compass["journey"] if row["node_id"] == NODE_ID)
    joined = " ".join(
        [journey["strategic_role"], journey["outcome"]]
    ).lower()
    assert "default-off mounting seam" in joined
    assert "globally-disabled typed scaffold is next" in joined


def test_evidence_binds_receipts_acceptance_and_yuri_summary() -> None:
    evidence = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))["evidence"]
    assert "orchestration/agent_inbox/codex/raisa-default-off-runtime-instrumentation-architecture-preplanning-receipt.json" in evidence["receipts"]
    assert "orchestration/agent_inbox/codex/raisa-default-off-runtime-instrumentation-architecture-candidate-precommit-receipt.json" in evidence["receipts"]
    assert "orchestration/agent_inbox/codex/raisa-default-off-runtime-instrumentation-architecture-sol-acceptance.md" in evidence["acceptances"]
    assert "orchestration/human_inbox/yuri/2026-08-12--default-off-runtime-instrumentation-architecture.md" in evidence["closeouts"]
