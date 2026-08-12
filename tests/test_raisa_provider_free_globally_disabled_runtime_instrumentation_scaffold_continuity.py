import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold"
PARENT = "raisa-provider-free-default-off-runtime-instrumentation-architecture"
SOURCE_HEAD = "410ea6dbbe28b94cfaa83ac5f6b586910c77aa6a"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_globally_disabled_scaffold_is_current() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 252
    assert compass["map_revision"] == 234
    assert compass["source_graph_revision"] == 252
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_node_opens_no_runtime_observer_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "provider-free",
        "globally-disabled",
        "empty allowlists",
        "no context provider",
        "four raw routes",
        "zero context",
        "170 focused",
        "ordinary and fallback",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_names_client_parity_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()
    assert "client proposal-confirm parity next" in joined
    assert "keeping compatibility routes mounted" in joined
    assert "continuity 252 / compass 234" in compass["orientation_statement"].lower()
    assert "zero disabled-path projection or handoff work" in compass["orientation_statement"]


def test_evidence_binds_receipts_acceptance_and_yuri_summary() -> None:
    evidence = _node(
        _load("orchestration/continuity/emr4-continuity-graph.json")
    )["evidence"]
    assert "orchestration/agent_inbox/codex/raisa-globally-disabled-runtime-instrumentation-scaffold-preplanning-receipt.json" in evidence["receipts"]
    assert "orchestration/agent_inbox/codex/raisa-globally-disabled-runtime-instrumentation-scaffold-precommit-receipt.json" in evidence["receipts"]
    assert "orchestration/agent_inbox/codex/raisa-globally-disabled-runtime-instrumentation-scaffold-sol-acceptance.md" in evidence["acceptances"]
    assert "orchestration/human_inbox/yuri/2026-08-12--globally-disabled-runtime-instrumentation-scaffold.md" in evidence["closeouts"]
