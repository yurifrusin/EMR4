from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
PARENT = "raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation"
SOURCE_HEAD = "da03039f637d3808c8785a6d6fc95309650044d9"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_readiness_review_is_the_accepted_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] == 307
    assert compass["map_revision"] == 289
    assert compass["source_graph_revision"] == 307
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_readiness_claim_is_exact_and_read_only() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "seven satisfied",
        "five route-transition gaps",
        "zero blocking gaps",
        "167 hostile",
        "private six-field receipt",
        "412-test",
        "eight-command gemini 3.7",
        "raw compatibility delete",
    ):
        assert phrase in joined


def test_failure_corrections_and_clean_veto_are_preserved() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    receipts = set(node["evidence"]["receipts"])
    findings = set(node["evidence"]["findings"])

    assert "orchestration/agent_inbox/codex/raisa-delete-confirm-route-mounting-readiness-review-pre-verifier-acceptance-receipt.json" in receipts
    assert "orchestration/agent_inbox/codex/raisa-delete-confirm-route-mounting-readiness-review-pre-verifier-acceptance-v2-receipt.json" in receipts
    assert "orchestration/agent_inbox/antigravity/raisa-delete-confirm-route-mounting-readiness-review-gemini37-review-receipt.json" in receipts
    assert "docs/ariadne-agent-error-correction-register-revision-316.md" in findings
    assert "orchestration/human_inbox/yuri/2026-08-17--delete-confirm-route-mounting-readiness-review.md" in node["evidence"]["closeouts"]


def test_next_candidate_is_provider_free_http_route_convergence() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free delete-confirm http route-convergence",
        "canonical/hidden-alias",
        "mounted route behavior",
        "database execution",
        "product data",
        "provider/credential",
        "protected refs",
    ):
        assert phrase in joined
