from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-status-confirm-scaffold-"
    "parse-catalogue-rehearsal"
)
PARENT = (
    "raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-"
    "scaffold"
)
SOURCE_HEAD = "bccc64f87eb0c1ae755b642fb6c4eb082298051d"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_catalogue_rehearsal_is_the_accepted_current_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 264
    assert compass["map_revision"] >= 246
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_catalogue_rehearsal_opens_no_runtime_or_product_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "runtime authority remains false",
        "rolled-back",
        "existing/product databases",
        "mounted route",
        "product command",
        "patient/product",
        "providers",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_evidence_acceptance_receipts_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    evidence = node["evidence"]

    assert any(item.endswith("provider-free-disposable-postgresql-evidence.json") for item in evidence["findings"])
    assert any(item.endswith("failure-evidence.json") for item in evidence["findings"])
    assert any("sol-acceptance" in item for item in evidence["acceptances"])
    assert any("human_inbox/yuri" in item for item in evidence["closeouts"])
    assert any("preplanning-receipt" in item for item in evidence["receipts"])
    assert any("precommit-receipt" in item for item in evidence["receipts"])
    assert any("prepush-receipt" in item for item in evidence["receipts"])


def test_next_direction_is_disposable_behavior_transaction_rehearsal() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free disposable postgresql",
        "behavior/transaction",
        "current-authority",
        "lock order",
        "appointment/audit/v1-receipt",
        "stored replay",
        "response-loss",
        "outer rollback",
        "mounted-route",
        "concurrency",
        "product-data",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
