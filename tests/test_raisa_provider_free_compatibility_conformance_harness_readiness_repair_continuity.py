import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair"
PARENT = "raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review"
SOURCE_HEAD = "48c1821af79f9d22b7c029fdbba8c4f984d239e5"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_compatibility_harness_repair_is_current() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 255
    assert compass["map_revision"] == 237
    assert compass["source_graph_revision"] == 255
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_node_keeps_the_repair_test_only() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "test-only",
        "application tree",
        "311 of 311",
        "exactly eight changed test files",
        "status-code assertions",
        "no status route",
        "external consumer",
        "create schedule fencing",
    ):
        assert phrase in joined


def test_compass_names_unmounted_status_protocol_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()
    assert "status protocol next" in joined
    assert "unmounted authored-synthetic protocol" in joined
    assert "atomic mutation, audit and completed-receipt" in joined
    assert "continuity 255 / compass 237" in compass["orientation_statement"].lower()


def test_evidence_binds_structural_acceptance_and_yuri_summary() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    structural = "orchestration/continuity/raisa-provider-free-compatibility-conformance-harness-readiness-repair/structural-repair-evidence.json"
    assert node["contract_evidence"] == []
    assert structural in node["evidence"]["artifacts"]
    assert "orchestration/agent_inbox/codex/raisa-compatibility-conformance-harness-readiness-repair-sol-acceptance.md" in node["evidence"]["acceptances"]
    assert "orchestration/human_inbox/yuri/2026-08-12--compatibility-conformance-harness-readiness-repair.md" in node["evidence"]["closeouts"]
