import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract"
PARENT = "raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal"
SOURCE_HEAD = "30a49015d23bfcf069be0af838df7091032a40be"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_adapter_remains_an_accepted_continuity_ancestor() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 257
    assert compass["map_revision"] >= 239
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])
    node = _node(graph)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_adapter_remains_unmounted_and_status_only() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "authored-synthetic",
        "unmounted",
        "update_appointment_status",
        "waiting-area union",
        "eight mappings",
        "thirty-seven hostile",
        "canonical stored receipt",
        "may not edit or execute the route or database",
    ):
        assert phrase in joined


def test_adapter_preserves_its_read_only_runtime_gap_handoff() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = _node(graph)
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    joined = " ".join(
        [journey["strategic_role"], journey["outcome"]]
        + node["unresolved_gates"]
    ).lower()
    assert "read-only status-confirm runtime-gap admission review is next" in joined
    assert "lock order" in joined
    assert "server session ingress" in joined
    assert "terminal behavior" in joined
    assert "stored-receipt delivery" in joined


def test_evidence_binds_adapter_packet_acceptance_and_yuri_summary() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    root = "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract"
    assert node["contract_evidence"] == []
    assert f"{root}/adapter-contract.json" in node["evidence"]["artifacts"]
    assert f"{root}/adapter-evidence.json" in node["evidence"]["artifacts"]
    assert (
        "orchestration/agent_inbox/codex/raisa-status-confirm-kernel-adapter-contract-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-12--status-confirm-kernel-adapter-contract.md"
        in node["evidence"]["closeouts"]
    )
