from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c2"
SOURCE_HEAD = "d54f0476448f1218cd55477d42b958721359eae8"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    return next(node for node in graph["nodes"] if node["id"] == NODE_ID)


def test_aes_c2_remains_bound_after_aes_c3_acceptance() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] >= 239
    assert _node(graph)["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] >= 221
    assert compass["source_graph_revision"] >= 239
    journey = next(row for row in compass["journey"] if row["node_id"] == NODE_ID)
    assert journey["lineage_parent"] == (
        "raisa-agent-execution-surface-containment-gate-aes-c1"
    )
    assert "aes-c3 hostile containment is next" in journey["outcome"].lower()


def test_aes_c2_continuity_opens_no_runtime_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["kind"] == "foundation"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "pure in-process function",
        "no real runtime broker",
        "work-cell process",
        "provider",
        "product context",
        "database/source",
        "filesystem",
        "network",
        "executable tool",
        "command",
        "protected evidence",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_aes_c2_exact_evidence_and_user_mailbox_are_bound() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["contract_evidence"] == []
    assert {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.schema.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/authored-synthetic-broker-simulator-scenarios.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/provider-free-broker-simulator-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/agent_inbox/antigravity/raisa-aes-c2-provider-free-broker-simulator-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--aes-c2-provider-free-broker-simulator.md"
        in node["evidence"]["closeouts"]
    )
    assert node["status"] == "accepted"


def test_aes_c2_handoff_preserves_closed_runtime_surfaces() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    joined = " ".join(node["claim_scope"] + node["unresolved_gates"]).lower()

    for phrase in (
        "aes-c3 provider-free hostile containment rehearsal",
        "real runtime broker",
        "patient/clinical/product",
        "provider",
        "database/source",
        "filesystem",
        "network",
        "executable tool",
        "command",
        "protected refs",
    ):
        assert phrase in joined
