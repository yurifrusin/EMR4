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
    assert graph["graph_revision"] >= 193
    nodes = {item["id"]: item for item in graph["nodes"]}
    assert nodes[NODE]["relationships"] == [
        {
            "node_id": "raisa-maintained-oidc-verifier-session-bridge-architecture",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] >= 174
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert NODE in {item["node_id"] for item in compass["journey"]}


def test_rendered_compass_validates_and_preserves_runtime_revision() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    text = REPORT.read_text(encoding="utf-8")
    assert f"Compass map revision {compass['map_revision']}; continuity graph revision {graph['graph_revision']}" in text
    assert "two-component" in json.dumps(compass).lower()
