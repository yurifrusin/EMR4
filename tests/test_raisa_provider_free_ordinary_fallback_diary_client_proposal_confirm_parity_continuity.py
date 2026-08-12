import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity"
PARENT = "raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold"
SOURCE_HEAD = "78cbcca756476fddfd0fda4b4d1241f195b21ab6"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_diary_client_parity_is_current() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 253
    assert compass["map_revision"] == 235
    assert compass["source_graph_revision"] == 253
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_node_accepts_zero_native_raw_calls_without_route_retirement() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "provider-free",
        "seven source-bound",
        "zero remain",
        "idempotency header",
        "fresh blocks",
        "signed status confirmation",
        "compatibility routes remain mounted",
        "external",
        "create schedule fencing",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_names_consumer_and_convergence_admission_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()
    assert "compatibility-consumer admission next" in joined
    assert "all backend compatibility routes remain mounted" in joined
    assert "without changing a route" in joined
    assert "continuity 253 / compass 235" in compass["orientation_statement"].lower()
    assert "seven raw appointment mutation call sites reduced to zero" in compass["orientation_statement"]


def test_evidence_binds_inventory_receipts_acceptance_and_yuri_summary() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    evidence = node["evidence"]
    assert node["contract_evidence"] == []
    assert "orchestration/continuity/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity/native-diary-raw-call-site-inventory.json" in evidence["artifacts"]
    assert "orchestration/agent_inbox/codex/raisa-provider-free-ordinary-fallback-client-proposal-confirm-parity-preplanning-receipt.json" in evidence["receipts"]
    assert "orchestration/agent_inbox/codex/raisa-provider-free-ordinary-fallback-client-proposal-confirm-parity-precommit-receipt.json" in evidence["receipts"]
    assert "orchestration/agent_inbox/codex/raisa-ordinary-fallback-diary-client-proposal-confirm-parity-sol-acceptance.md" in evidence["acceptances"]
    assert "orchestration/human_inbox/yuri/2026-08-12--ordinary-fallback-diary-client-proposal-confirm-parity.md" in evidence["closeouts"]
