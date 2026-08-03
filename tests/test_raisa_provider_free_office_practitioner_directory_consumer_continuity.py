from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
NODE = "raisa-provider-free-office-practitioner-directory-consumer"


def test_office_consumer_is_terminal_accepted_continuity_node() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    assert graph["graph_revision"] == 201
    node = graph["nodes"][-1]
    assert node["id"] == NODE
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "raisa-provider-free-session-practitioner-directory-read-bridge",
            "relation": "builds_on",
        }
    ]
    assert any(
        "live-office-backend-postgres-evidence.json" in path
        for path in node["evidence"]["findings"]
    )


def test_office_consumer_is_current_compass_position() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    assert compass["map_revision"] == 182
    assert compass["source_graph_revision"] == 201
    assert compass["current_position"]["node_id"] == NODE
    assert "installed Word and Word Online" in compass["orientation_statement"]
    decision = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"]
        == "authorize-provider-free-office-directory-reload-reconciliation"
    )
    assert "Satisfied" in decision["required_before"]


def test_rendered_compass_names_the_office_consumer_and_limits() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert "Provider-free Office practitioner-directory consumer" in report
    assert "Real identity" in report
    assert "provider-free" in report
