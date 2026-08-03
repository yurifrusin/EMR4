from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODES = [
    "raisa-provider-free-office-reload-terminal-reconciliation",
    "raisa-provider-free-office-session-loss-reconciliation",
    "raisa-provider-free-office-cross-surface-replay-isolation",
    "raisa-provider-free-office-lifecycle-observability",
    "raisa-provider-free-default-off-office-consumer-adapter",
]


def test_five_lifecycle_nodes_are_terminal_accepted_lineage() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    assert graph["graph_revision"] == 206
    nodes = graph["nodes"][-5:]
    assert [node["id"] for node in nodes] == NODES
    parent = "raisa-provider-free-office-practitioner-directory-consumer"
    for node in nodes:
        assert node["status"] == "accepted"
        assert node["relationships"] == [
            {"node_id": parent, "relation": "builds_on"}
        ]
        assert len(node["contract_evidence"]) == 2
        assert all(item["status"] == "satisfied" for item in node["contract_evidence"])
        parent = node["id"]


def test_compass_binds_five_results_and_requires_fresh_next_authority() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    assert compass["map_revision"] == 187
    assert compass["source_graph_revision"] == 206
    assert compass["current_position"]["node_id"] == NODES[-1]
    assert all(
        node_id in {item["node_id"] for item in compass["journey"]}
        for node_id in NODES
    )
    decision = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"]
        == "authorize-provider-free-native-diary-directory-composition-review"
    )
    assert "Fresh Yuri authority" in decision["required_before"]


def test_rendered_compass_names_lifecycle_adapter_and_limits() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert "Provider-free default-off Office consumer lifecycle adapter" in report
    assert "Continuity 206 / Compass 187" in report
    assert "Fresh authority" in report
