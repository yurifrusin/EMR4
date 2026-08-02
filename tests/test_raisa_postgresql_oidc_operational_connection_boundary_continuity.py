from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass
from scripts.raisa_postgresql_oidc_operational_connection_boundary_continuity_update import (
    NODE,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_bind_oidc_operational_boundary() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert graph["graph_revision"] == 196
    assert graph["nodes"][-1]["id"] == NODE
    assert graph["nodes"][-1]["relationships"] == [
        {
            "node_id": "raisa-postgresql-oidc-authorization-attempt-store",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] == 177
    assert compass["source_graph_revision"] == 196
    assert compass["current_position"]["node_id"] == NODE


def test_rendered_compass_validates_and_preserves_closed_runtime_edges() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    rendered = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 177; continuity graph revision 196" in rendered
    serialized = json.dumps(compass)
    assert "PASSWORD NULL" in serialized
    assert "mounted OIDC start/callback" in serialized
    assert "live Microsoft" in serialized
    assert "product reads remain closed" in serialized
    assert "process-local and not deployable distributed persistence" not in serialized


def test_user_decision_consumes_operational_gate_and_names_next_gate() -> None:
    compass = _json(COMPASS)
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions[
        "authorize-postgresql-oidc-attempt-store-operational-connection-boundary"
    ]
    assert "Satisfied on 2026-08-02" in completed["required_before"]
    assert completed["evidence"]
    next_decision = decisions[
        "authorize-provider-free-oidc-start-callback-transport-boundary"
    ]
    assert "mounted OIDC start/callback route" in next_decision["required_before"]
    assert "Live Microsoft" in next_decision["required_before"]


def test_graph_evidence_excludes_branding_and_live_identity_claims() -> None:
    graph = _json(GRAPH)
    node = graph["nodes"][-1]
    paths = [path for group in node["evidence"].values() for path in group]
    assert not any(path.startswith("docs/branding/") for path in paths)
    serialized = json.dumps(node)
    assert "No persistent credential" in serialized
    assert "Live Microsoft" in serialized
    assert "product reads remain closed" in serialized
