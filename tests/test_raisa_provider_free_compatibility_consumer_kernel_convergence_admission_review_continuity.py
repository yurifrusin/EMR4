import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review"
PARENT = "raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity"
SOURCE_HEAD = "9c7444ecce69b51ca5cac80818e8997724a11f13"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_compatibility_admission_is_current() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 254
    assert compass["map_revision"] == 236
    assert compass["source_graph_revision"] == 254
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_node_holds_routes_and_external_conclusion_closed() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]).lower()
    for phrase in (
        "zero committed product/runtime",
        "126 conformance",
        "four direct database fixture",
        "external consumers remain unknown",
        "routes remain mounted",
        "status confirm-first",
        "forty-five stale tests",
        "create schedule fencing",
    ):
        assert phrase in joined


def test_compass_names_test_only_repair_then_status_protocol() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()
    assert "conformance readiness next" in joined
    assert "stale test clocks and proposal idempotency headers" in joined
    assert "status transaction-kernel" in joined
    assert "continuity 254 / compass 236" in compass["orientation_statement"].lower()


def test_evidence_binds_inventory_acceptance_and_yuri_summary() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    evidence = node["evidence"]
    assert node["contract_evidence"] == []
    assert "orchestration/continuity/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review/consumer-and-preservation-inventory.json" in evidence["artifacts"]
    assert "orchestration/agent_inbox/codex/raisa-compatibility-consumer-kernel-convergence-admission-review-sol-acceptance.md" in evidence["acceptances"]
    assert "orchestration/human_inbox/yuri/2026-08-12--compatibility-consumer-kernel-convergence-admission-review.md" in evidence["closeouts"]
