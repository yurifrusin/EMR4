from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c3"
SOURCE_HEAD = "c45ff191af420b801e9917a7efc69c17aeb5698b"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_aes_c3_is_current_and_aes_c4_requires_an_exact_envelope() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 240
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 222
    assert compass["source_graph_revision"] == 240
    assert compass["current_position"]["node_id"] == NODE_ID
    orientation = compass["orientation_statement"].lower()
    assert "aes-c3 passes" in orientation
    assert "aes-c4 remains closed" in orientation
    assert "yuri" in orientation


def test_aes_c3_continuity_opens_no_runtime_authority() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

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
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

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


def test_compass_handoff_names_exact_occupied_provider_fork() -> None:
    position = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(position["unlocks"] + position["does_not_solve"]).lower()

    for phrase in (
        "provider/model",
        "region",
        "identity",
        "authored-synthetic",
        "call",
        "cost",
        "isolation",
        "proofreader",
        "cleanup",
        "no-fallback",
        "semantic prompt-injection",
        "patient/product/clinical",
        "database/source",
        "command",
        "protected-ref",
    ):
        assert phrase in joined
