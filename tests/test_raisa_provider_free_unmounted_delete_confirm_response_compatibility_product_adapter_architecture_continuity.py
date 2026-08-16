from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture"
PARENT = "raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution"
SOURCE_HEAD = "9f0c166be2276d4e236dbdb4ed5657074ffbd0aa"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_response_architecture_is_the_accepted_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] == 305
    assert compass["map_revision"] == 287
    assert compass["source_graph_revision"] == 305
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_response_architecture_opens_no_runtime_authority() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "six-field private canonical bytes",
        "pure deterministic projection",
        "136 contract and 20 evidence",
        "python 3.11 runtime validation is unclaimed",
        "aer-0358",
        "no route/schema edit",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_worker_correction_and_clean_veto_are_preserved() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    receipts = set(node["evidence"]["receipts"])

    assert "orchestration/agent_inbox/deepseek/raisa-delete-confirm-response-compatibility-product-adapter-architecture-worker-result.json" in receipts
    assert "orchestration/agent_inbox/deepseek/raisa-delete-confirm-response-compatibility-product-adapter-architecture-correction-worker-result.json" in receipts
    assert "orchestration/agent_inbox/antigravity/raisa-delete-confirm-response-compatibility-product-adapter-architecture-gemini37-review-receipt.json" in receipts
    assert "orchestration/human_inbox/yuri/2026-08-16--delete-confirm-response-compatibility-product-adapter-architecture.md" in node["evidence"]["closeouts"]


def test_next_candidate_remains_unmounted_implementation_only() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free unmounted",
        "pure projection",
        "server-owned ingress",
        "locked re-admission",
        "route or schema editing",
        "product execution",
        "provider/credential",
        "protected-ref",
    ):
        assert phrase in joined
