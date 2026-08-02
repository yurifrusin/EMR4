from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass
from scripts.raisa_postgresql_oidc_authorization_attempt_store_continuity_update import (
    NODE,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_bind_postgresql_attempt_store() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert graph["graph_revision"] == 195
    assert graph["nodes"][-1]["id"] == NODE
    assert graph["nodes"][-1]["relationships"] == [
        {
            "node_id": "raisa-two-component-oidc-runtime-adapter",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] == 176
    assert compass["source_graph_revision"] == 195
    assert compass["current_position"]["node_id"] == NODE


def test_rendered_compass_validates_and_keeps_runtime_edges_closed() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    rendered = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 176; continuity graph revision 195" in rendered
    serialized = json.dumps(compass)
    assert "finite LOGIN/pool" in serialized
    assert "live Microsoft" in serialized
    assert "application session" in serialized


def test_user_decision_marks_this_tranche_satisfied_and_next_gate_fresh() -> None:
    compass = _json(COMPASS)
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions["authorize-provider-free-postgresql-authorization-attempt-store"]
    assert "Satisfied on 2026-08-02" in completed["required_before"]
    assert completed["evidence"]
    next_decision = decisions[
        "authorize-postgresql-oidc-attempt-store-operational-connection-boundary"
    ]
    assert "required_before" in next_decision
    assert "Routes" in next_decision["required_before"]
