from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-read-only-status-confirm-physical-representability-review"
PARENT = "raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal"
SOURCE_HEAD = "530a1d479a48242df6985886acdbb796550e9093"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_representability_review_remains_an_accepted_ancestor() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 261
    assert compass["map_revision"] >= 243
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_review_opens_no_implementation_or_runtime_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "implementation_not_admitted",
        "representable only with additive change",
        "physical design",
        "migration/backfill",
        "database execution",
        "providers",
        "product/patient",
        "commands",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_contract_incident_acceptance_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert {
        "orchestration/continuity/raisa-provider-free-read-only-status-confirm-physical-representability-review/physical-representability-review-contract.json",
        "orchestration/continuity/raisa-provider-free-read-only-status-confirm-physical-representability-review/physical-representability-review-contract.schema.json",
        "orchestration/continuity/raisa-provider-free-read-only-status-confirm-physical-representability-review/provider-free-read-only-review-evidence.json",
        "orchestration/agent_inbox/codex/raisa-status-confirm-physical-representability-protected-metadata-scope-incident.json",
        "docs/ariadne-agent-error-correction-register-revision-259.md",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/human_inbox/yuri/2026-08-12--status-confirm-physical-representability-review.md"
        in node["evidence"]["closeouts"]
    )


def test_physical_design_descendant_builds_on_the_review() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    child = next(
        item
        for item in graph["nodes"]
        if item["id"]
        == "raisa-provider-free-unmounted-status-confirm-physical-design-architecture"
    )
    assert child["relationships"] == [{"node_id": NODE_ID, "relation": "builds_on"}]
