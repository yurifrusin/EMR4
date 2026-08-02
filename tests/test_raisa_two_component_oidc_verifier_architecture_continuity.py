from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass
from scripts.raisa_two_component_oidc_verifier_architecture_continuity_update import NODE


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_bind_the_revision() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert graph["graph_revision"] == 193
    assert graph["nodes"][-1]["id"] == NODE
    assert compass["map_revision"] == 174
    assert compass["source_graph_revision"] == 193
    assert compass["current_position"]["node_id"] == NODE
    assert graph["nodes"][-1]["relationships"] == [{"node_id": "raisa-maintained-oidc-verifier-session-bridge-architecture", "relation": "builds_on"}]


def test_rendered_compass_validates_and_keeps_runtime_closed() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    text = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 174; continuity graph revision 193" in text
    assert "provider-free runtime adapter" in json.dumps(compass)
