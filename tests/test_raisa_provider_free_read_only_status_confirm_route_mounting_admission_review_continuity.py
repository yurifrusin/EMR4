from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-read-only-status-confirm-route-mounting-admission-review"
)
PARENT = (
    "raisa-provider-free-disposable-postgresql-status-confirm-behavior-"
    "transaction-rehearsal"
)
SOURCE_HEAD = "fb3772dea0c27a7572df00e1b9d5153f9165ccf3"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_route_mounting_review_is_the_accepted_current_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 266
    assert compass["map_revision"] >= 248
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_review_opens_no_runtime_or_product_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "read-only",
        "implementation authority remains false",
        "literally mounted",
        "seven composition gaps",
        "product command",
        "providers",
        "protected integration",
    ):
        assert phrase in joined


def test_review_evidence_acceptance_receipts_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    evidence = node["evidence"]

    assert any(item.endswith("route-mounting-review-evidence.json") for item in evidence["findings"])
    assert any("sol-acceptance" in item for item in evidence["acceptances"])
    assert any("human_inbox/yuri" in item for item in evidence["closeouts"])
    assert any("preplanning-receipt" in item for item in evidence["receipts"])
    assert any("preacceptance-receipt" in item for item in evidence["receipts"])


def test_next_direction_is_test_hygiene_then_unmounted_composition() -> None:
    current = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "stale sprint-138 test expectation",
        "provider-free unmounted",
        "status-only adapter",
        "server authority/session",
        "physical seam",
        "route execution",
        "unknown commit",
        "protected-ref",
    ):
        assert phrase in joined
