from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c3"
SOURCE_HEAD = "c45ff191af420b801e9917a7efc69c17aeb5698b"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_aes_c3_remains_accepted_in_the_aes_c4_lineage() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["status"] == "accepted"
    assert any(row["node_id"] == NODE_ID for row in compass["journey"])
    assert compass["source_graph_revision"] == graph["graph_revision"]


def test_aes_c3_continuity_opens_no_runtime_authority() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)

    assert node["kind"] == "foundation"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "pure python function",
        "no real runtime",
        "work-cell process",
        "provider",
        "product context",
        "database/source",
        "filesystem",
        "network",
        "credential",
        "executable tool",
        "command",
        "protected evidence",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_aes_c3_exact_evidence_recovery_and_mailbox_are_bound() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)

    assert node["contract_evidence"] == []
    assert {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.schema.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/authored-synthetic-hostile-containment-scenarios.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/provider-free-hostile-containment-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/agent_inbox/antigravity/raisa-aes-c3-provider-free-hostile-containment-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/agent_inbox/codex/raisa-aes-c3-sol-recovery.md"
        in node["evidence"]["artifacts"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--aes-c3-provider-free-hostile-containment.md"
        in node["evidence"]["closeouts"]
    )
    assert node["status"] == "accepted"


def test_aes_c3_journey_names_exact_occupied_provider_fork() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    journey = next(row for row in compass["journey"] if row["node_id"] == NODE_ID)
    joined = (journey["strategic_role"] + " " + journey["outcome"]).lower()

    for phrase in (
        "authored-synthetic",
        "hostile-content",
        "cumulative-stop",
        "stale-authority",
        "occupied provider",
    ):
        assert phrase in joined
