from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass
from scripts.raisa_two_component_oidc_runtime_adapter_continuity_update import NODE


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_bind_runtime_adapter() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert graph["graph_revision"] >= 194
    node = next(item for item in graph["nodes"] if item["id"] == NODE)
    assert compass["map_revision"] >= 175
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert node["relationships"] == [
        {
            "node_id": "raisa-two-component-oidc-verifier-architecture-revision",
            "relation": "builds_on",
        }
    ]


def test_rendered_compass_validates_and_keeps_later_authority_closed() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    text = REPORT.read_text(encoding="utf-8")
    assert (
        f"Compass map revision {compass['map_revision']}; "
        f"continuity graph revision {graph['graph_revision']}"
    ) in text
    assert "provider-free PostgreSQL authorization-attempt store" in json.dumps(compass)
    assert "live Microsoft" in json.dumps(compass)
