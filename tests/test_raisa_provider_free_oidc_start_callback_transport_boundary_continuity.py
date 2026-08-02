from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass
from scripts.raisa_provider_free_oidc_start_callback_transport_boundary_continuity_update import (
    NODE,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_bind_oidc_transport_boundary() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert graph["graph_revision"] == 197
    assert graph["nodes"][-1]["id"] == NODE
    assert graph["nodes"][-1]["relationships"] == [
        {
            "node_id": "raisa-postgresql-oidc-operational-connection-boundary",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] == 178
    assert compass["source_graph_revision"] == 197
    assert compass["current_position"]["node_id"] == NODE


def test_rendered_compass_validates_and_preserves_closed_authority() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    rendered = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 178; continuity graph revision 197" in rendered
    serialized = json.dumps(compass)
    assert "strict form_post" in serialized
    assert "Live Microsoft" in serialized
    assert "application session" in serialized
    assert "product reads remain closed" in serialized


def test_user_decision_consumes_transport_gate_and_names_preauthorised_next() -> None:
    compass = _json(COMPASS)
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions[
        "authorize-provider-free-oidc-start-callback-transport-boundary"
    ]
    assert "Satisfied on 2026-08-02" in completed["required_before"]
    assert completed["evidence"]
    next_decision = decisions[
        "authorize-provider-free-oidc-binding-admission-grant-boundary"
    ]
    assert "Preauthorised by Yuri" in next_decision["required_before"]
    assert "five-source tranche rehydration" in next_decision["required_before"]


def test_graph_evidence_excludes_branding_and_live_identity_claims() -> None:
    node = _json(GRAPH)["nodes"][-1]
    paths = [path for group in node["evidence"].values() for path in group]
    assert not any(path.startswith("docs/branding/") for path in paths)
    serialized = json.dumps(node)
    assert "No live Microsoft call" in serialized
    assert "admission-grant" in serialized
    assert "product counts remain zero" in serialized
