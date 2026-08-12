from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-status-confirm-physical-design-architecture"
PARENT = "raisa-provider-free-read-only-status-confirm-physical-representability-review"
SOURCE_HEAD = "826aad11c29007b13eaa377e3f7ea494cc82ce70"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_physical_design_is_the_accepted_current_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 262
    assert compass["map_revision"] >= 244
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_architecture_opens_no_implementation_or_runtime_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "implementation_authorized is false",
        "database-owned",
        "legacy rows are never inferred",
        "exact stored canonical bytes",
        "application edits",
        "executable ddl",
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
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-design-architecture/physical-design-contract.json",
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-design-architecture/physical-design-contract.schema.json",
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-physical-design-architecture/provider-free-unmounted-architecture-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/agent_inbox/codex/raisa-status-confirm-physical-design-architecture-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-12--status-confirm-physical-design-architecture.md"
        in node["evidence"]["closeouts"]
    )


def test_next_direction_is_unmounted_schema_and_transaction_scaffold() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free unmounted status-confirm physical schema-and-transaction scaffold",
        "model",
        "inert migration",
        "unmounted helper",
        "database and route execution",
        "postgresql catalogue",
        "lock-wait",
        "mounted-route behavior",
        "provider/credential",
        "patient/product",
        "product commands",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
