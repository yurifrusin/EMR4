from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c0"
SOURCE_HEAD = "01d355f42df5981341196f3aa0caec2cccce7a2d"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_aes_c0_remains_accepted_in_the_descendant_lineage() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    nodes = {node["id"]: node for node in graph["nodes"]}
    journeys = {item["node_id"]: item for item in compass["journey"]}

    assert graph["graph_revision"] >= 237
    assert nodes[NODE_ID]["coordinates"]["source_head"] == SOURCE_HEAD
    assert nodes[NODE_ID]["status"] == "accepted"
    assert compass["map_revision"] >= 219
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert NODE_ID in journeys
    assert "aes-c1 provider-free admission rehearsal is next" in journeys[NODE_ID][
        "outcome"
    ].lower()


def test_aes_c0_continuity_opens_no_runtime_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert node["kind"] == "foundation"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "no capability broker",
        "work-cell",
        "provider",
        "product context",
        "database/source",
        "tool",
        "command",
        "protected evidence",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_aes_c0_contract_and_user_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert node["contract_evidence"] == []
    assert {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json"
        ,
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/authored-synthetic-contract-examples.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/provider-free-acceptance-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--aes-c0-architecture-contract.md"
        in node["evidence"]["closeouts"]
    )
    assert node["status"] == "accepted"


def test_aes_c0_historical_handoff_was_provider_free_admission_only() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
        + [journey["outcome"]]
    ).lower()

    for phrase in (
        "provider-free admission rehearsal",
        "no capability broker",
        "patient/clinical/product",
        "provider",
        "database/source",
        "tool",
        "command",
        "protected refs",
    ):
        assert phrase in joined
