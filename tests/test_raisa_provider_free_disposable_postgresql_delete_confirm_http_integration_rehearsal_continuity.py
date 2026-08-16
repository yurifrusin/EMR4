from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-delete-confirm-http-"
    "integration-rehearsal"
)
PARENT = "raisa-provider-free-delete-confirm-http-route-convergence"
SOURCE_HEAD = "fe5dbcb31b06b027285aa84ee3cafb4fbbffb9db"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_http_postgresql_integration_is_the_accepted_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] == 309
    assert compass["map_revision"] == 291
    assert compass["source_graph_revision"] == 309
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_claim_and_closed_boundaries_are_exact() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "twelve dhi",
        "135 hostile",
        "non-bypassrls",
        "forced rls on eight",
        "public/private bytes",
        "40-test integration/plan",
        "58-test route/physical",
        "286-test register",
        "37-test api spine/diary",
        "130-test maintenance",
        "eight-command gemini 3.7",
        "raw compatibility delete",
        "visible reception one",
        "product data",
        "protected-ref",
    ):
        assert phrase in joined


def test_negative_and_independent_evidence_are_preserved() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    receipts = set(node["evidence"]["receipts"])
    findings = set(node["evidence"]["findings"])

    assert "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal/provider-free-http-postgresql-failure-evidence.json" in findings
    assert "docs/ariadne-agent-error-correction-register-revision-329.md" in findings
    assert "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-pre-verifier-receipt.json" in receipts
    assert "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-pre-verifier-v2-receipt.json" in receipts
    assert "orchestration/agent_inbox/antigravity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-gemini37-review-receipt.json" in receipts


def test_next_work_is_the_bounded_ariadne_review() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "recent ariadne incidents",
        "deepseek harness primary sources",
        "authentication, cost, control and switching",
        "highest-leverage workflow repairs",
        "raw compatibility delete",
        "visible reception one",
        "product/patient data",
        "protected refs",
    ):
        assert phrase in joined
