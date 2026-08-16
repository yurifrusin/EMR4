from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-delete-confirm-behavior-"
    "transaction-rehearsal"
)
PARENT = (
    "raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-"
    "parse-catalogue-rehearsal"
)
SOURCE_HEAD = "49dd2aaa72877adb844da4d0d5d5bb28039c90c8"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_behavior_rehearsal_is_the_accepted_current_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 303
    assert compass["map_revision"] >= 285
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_behavior_rehearsal_opens_no_runtime_or_product_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "runtime authority remains false",
        "serial",
        "mounted routes",
        "product command",
        "concurrency",
        "patient/product",
        "providers",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_pass_review_recoveries_acceptance_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    evidence = node["evidence"]

    assert any(
        item.endswith("behavior-transaction-evidence.json")
        for item in evidence["findings"]
    )
    assert any(item.endswith("failure-evidence.json") for item in evidence["findings"])
    assert any(
        "release-accounting-recovery-addendum" in item for item in evidence["plans"]
    )
    assert any("gemini37-final-review-receipt" in item for item in evidence["receipts"])
    assert any("revision-309" in item for item in evidence["findings"])
    assert any("sol-acceptance" in item for item in evidence["acceptances"])
    assert any("human_inbox/yuri" in item for item in evidence["closeouts"])


def test_next_direction_is_read_only_route_convergence_admission() -> None:
    current = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free read-only",
        "route-convergence admission",
        "route, dependency, adapter, kernel and transaction",
        "without editing, mounting or calling",
        "product-database",
        "concurrency",
        "unknown commit",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
