from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-"
    "scaffold"
)
PARENT = "raisa-provider-free-unmounted-status-confirm-physical-design-architecture"
SOURCE_HEAD = "b36b8a455b70d8bc3e99b5e5dd84a8237375ff3c"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_physical_scaffold_remains_an_accepted_ancestor() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 263
    assert compass["map_revision"] >= 245
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert NODE_ID in {item["node_id"] for item in compass["journey"]}
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_scaffold_opens_no_runtime_or_product_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "runtime authority false",
        "inert ddl",
        "database/SQL execution".lower(),
        "real locks",
        "routes",
        "providers",
        "product/patient",
        "commands",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_source_receipts_acceptance_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert {
        "app/models/appointments.py",
        "app/services/appointment_status_physical.py",
        "alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py",
    } <= set(node["evidence"]["artifacts"])
    assert (
        "orchestration/agent_inbox/codex/raisa-status-confirm-physical-schema-transaction-scaffold-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-12--status-confirm-physical-schema-transaction-scaffold.md"
        in node["evidence"]["closeouts"]
    )
    receipts = set(node["evidence"]["receipts"])
    assert any("preacceptance-receipt" in item for item in receipts)
    assert any("precommit-receipt" in item for item in receipts)


def test_scaffold_handed_off_to_disposable_postgresql_parse_catalogue() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    descendant = next(
        item for item in compass["journey"] if item.get("lineage_parent") == NODE_ID
    )
    joined = " ".join(
        [descendant["node_id"], descendant["strategic_role"], descendant["outcome"]]
    ).lower()
    for phrase in (
        "disposable-postgresql",
        "migration and catalogue",
        "postgresql 16",
        "nine rolled-back",
        "container is absent",
    ):
        assert phrase in joined
