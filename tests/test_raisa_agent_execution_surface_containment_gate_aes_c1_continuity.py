from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c1"
SOURCE_HEAD = "285e60216cf22907e8a0f5596ece11f74f455c81"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    return next(node for node in graph["nodes"] if node["id"] == NODE_ID)


def test_aes_c1_remains_bound_after_aes_c2_acceptance() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] >= 238
    assert _node(graph)["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] >= 220
    assert compass["source_graph_revision"] >= 238
    journey = next(row for row in compass["journey"] if row["node_id"] == NODE_ID)
    assert journey["lineage_parent"] == "raisa-agent-execution-surface-containment-gate-aes-c0"
    assert "aes-c2 provider-free broker simulation is next" in journey["outcome"].lower()


def test_aes_c1_continuity_opens_no_runtime_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["kind"] == "foundation"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "unmounted",
        "no runtime broker",
        "work-cell process",
        "provider",
        "product context",
        "database/source",
        "network",
        "executable tool",
        "command",
        "protected evidence",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_aes_c1_exact_evidence_and_user_mailbox_are_bound() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["contract_evidence"] == []
    assert {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/authored-synthetic-admission-scenarios.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/provider-free-admission-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/agent_inbox/antigravity/raisa-aes-c1-provider-free-admission-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--aes-c1-provider-free-admission.md"
        in node["evidence"]["closeouts"]
    )
    assert node["status"] == "accepted"


def test_aes_c1_handoff_was_one_inert_adapter_only() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    joined = " ".join(node["claim_scope"] + node["unresolved_gates"]).lower()

    for phrase in (
        "two exact inert intersections",
        "aes-c2 provider-free broker simulator",
        "no runtime broker",
        "patient/clinical/product",
        "provider",
        "database/source",
        "command",
        "protected refs",
    ):
        assert phrase in joined
