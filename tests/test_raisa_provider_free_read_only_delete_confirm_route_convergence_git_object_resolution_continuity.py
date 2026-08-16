from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution"
PARENT = "raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal"
SOURCE_HEAD = "1cc75672abba6e011e0de03f26a3ad2ba9bae396"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_route_review_is_the_accepted_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] == 304
    assert compass["map_revision"] == 286
    assert compass["source_graph_revision"] == 304
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_route_review_opens_no_runtime_authority() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "no product runtime authority",
        "unmounted_adapter_and_response_transition_required",
        "six-field",
        "canonical-lf",
        "dispatch false",
        "no route edit/call",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_failed_and_passing_reviews_are_both_preserved() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    receipts = set(node["evidence"]["receipts"])

    assert "orchestration/agent_inbox/antigravity/raisa-delete-confirm-route-convergence-git-object-resolution-gemini37-review-receipt.json" in receipts
    assert "orchestration/agent_inbox/antigravity/raisa-delete-confirm-route-convergence-git-object-resolution-corrected-gemini37-review-receipt.json" in receipts
    assert "orchestration/human_inbox/yuri/2026-08-16--delete-confirm-route-convergence-and-ariadne-git-object-resolution.md" in node["evidence"]["closeouts"]


def test_next_candidate_remains_unmounted_architecture_only() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free unmounted",
        "response-compatibility",
        "server-owned authority",
        "byte-exact",
        "route editing",
        "product execution",
        "provider/credential",
        "protected-ref",
    ):
        assert phrase in joined
