from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-delete-confirm-http-route-convergence"
PARENT = "raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
SOURCE_HEAD = "c7a01edd96ebabf3ea2c07be89a5b405c9629853"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_http_route_convergence_is_the_accepted_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] == 308
    assert compass["map_revision"] == 290
    assert compass["source_graph_revision"] == 308
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_http_route_claim_and_closed_boundaries_are_exact() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "canonical and hidden historical",
        "private stored receipt bytes",
        "twelve",
        "149 hostile",
        "27 focused",
        "78 api spine",
        "274 tests",
        "439 tests",
        "eight-command gemini 3.7",
        "postgresql remain unproved",
        "raw compatibility delete",
    ):
        assert phrase in joined


def test_recovery_and_clean_veto_evidence_are_preserved() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    receipts = set(node["evidence"]["receipts"])
    findings = set(node["evidence"]["findings"])

    assert "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-deepseek-mechanical-correction-failure-receipt.json" in receipts
    assert "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-pre-verifier-acceptance-receipt.json" in receipts
    assert "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-pre-verifier-acceptance-v2-receipt.json" in receipts
    assert "orchestration/agent_inbox/antigravity/raisa-provider-free-delete-confirm-http-route-convergence-gemini37-review-receipt.json" in receipts
    assert "docs/ariadne-agent-error-correction-register-revision-319.md" in findings
    assert "orchestration/human_inbox/yuri/2026-08-17--delete-confirm-http-route-convergence.md" in node["evidence"]["closeouts"]


def test_next_candidate_is_disposable_postgresql_http_integration() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free disposable postgresql delete-confirm http integration",
        "committed, replay, denial, rollback and cleanup",
        "raw compatibility delete",
        "visible reception one",
        "product/patient data",
        "provider access",
        "protected refs",
    ):
        assert phrase in joined
