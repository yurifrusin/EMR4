from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-delete-confirm-physical-design-architecture"
PARENT = (
    "raisa-provider-free-read-only-unmounted-delete-confirm-"
    "physical-representability-review"
)
SOURCE_HEAD = "3fd22ba69f96c0378538ea27c6bea444fcb81936"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_delete_physical_design_is_the_accepted_paused_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 298
    assert compass["map_revision"] >= 280
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
        "implementation_authorized remains false",
        "database-owned monotonic authority fence",
        "normalized exact cancellation/read grants",
        "family-qualified private receipt",
        "readback is separately authorised",
        "application/migration/route implementation",
        "executable ddl",
        "database execution",
        "product providers/data/commands",
        "pages",
        "protected refs",
        "paused",
    ):
        assert phrase in joined


def test_contract_review_acceptance_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert {
        "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture/physical-design-contract.json",
        "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture/physical-design-contract.schema.json",
        "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture/provider-free-physical-design-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/agent_inbox/antigravity/raisa-delete-confirm-physical-design-gemini37-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-design-architecture-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-15--delete-confirm-physical-design-architecture.md"
        in node["evidence"]["closeouts"]
    )


def test_next_scaffold_is_planned_but_not_opened() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "after yuri resumes",
        "provider-free unmounted delete-confirm physical schema-and-transaction scaffold",
        "product authority fence",
        "normalized grants",
        "database and route execution",
        "postgresql catalogue",
        "capability provisioning",
        "response/route compatibility transition",
        "provider/credential",
        "patient/product",
        "product commands",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
