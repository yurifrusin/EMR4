from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold"
)
PARENT = "raisa-provider-free-unmounted-delete-confirm-physical-design-architecture"
SOURCE_HEAD = "843769b415597f4545663d78044eaaad303c7692"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_delete_scaffold_is_the_accepted_paused_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] == 300
    assert compass["map_revision"] == 282
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_scaffold_opens_no_runtime_database_or_route_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "runtime authority remains false",
        "database-owned",
        "normalized default-deny grants",
        "inert migration",
        "no migration or sql ran",
        "no database or route opened",
        "capability provisioning",
        "product/patient",
        "pages",
        "protected refs",
        "paused",
    ):
        assert phrase in joined


def test_scaffold_source_review_acceptance_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert {
        "app/models/tenancy.py",
        "app/models/appointments.py",
        "app/services/appointment_delete_physical.py",
        "alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py",
    } <= set(node["evidence"]["artifacts"])
    assert (
        "orchestration/agent_inbox/antigravity/raisa-delete-confirm-physical-scaffold-gemini37-retry-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-schema-transaction-scaffold-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-16--delete-confirm-physical-schema-transaction-scaffold.md"
        in node["evidence"]["closeouts"]
    )


def test_next_parse_catalogue_is_planned_but_paused() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "after yuri resumes",
        "provider-free disposable postgresql",
        "parse/catalogue",
        "empty-instance installation",
        "behavior and route execution",
        "capability provisioning",
        "patient/product",
        "product commands",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
