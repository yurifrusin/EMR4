from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture"
PARENT = "raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review"
SOURCE_HEAD = "b9cc57b6e607e5896e822abc7b632442df2f907e"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_architecture_is_the_accepted_current_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 259
    assert compass["map_revision"] >= 241
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_architecture_opens_no_runtime_or_implementation_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "implementation_authorized is false",
        "physical version storage",
        "migration/backfill",
        "route integration",
        "database execution",
        "providers",
        "product/patient",
        "commands",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_contract_acceptance_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert {
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.json",
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/convergence-architecture-contract.schema.json",
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture/provider-free-architecture-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/human_inbox/yuri/2026-08-12--status-confirm-runtime-convergence-architecture.md"
        in node["evidence"]["closeouts"]
    )


def test_next_direction_is_an_unmounted_rehearsal() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free unmounted in-memory convergence rehearsal",
        "without a route or database",
        "physical version storage",
        "mounted route behavior",
        "postgresql locking/concurrency",
        "raw compatibility-route",
        "provider/credential",
        "patient/product",
        "product commands",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
