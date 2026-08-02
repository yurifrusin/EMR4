from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass
from scripts.raisa_provider_free_oidc_binding_admission_grant_boundary_continuity_update import (
    NODE,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_bind_binding_admission_boundary() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert graph["graph_revision"] == 198
    assert graph["nodes"][-1]["id"] == NODE
    assert graph["nodes"][-1]["relationships"] == [
        {
            "node_id": "raisa-provider-free-oidc-start-callback-transport-boundary",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] == 179
    assert compass["source_graph_revision"] == 198
    assert compass["current_position"]["node_id"] == NODE


def test_rendered_compass_validates_and_keeps_session_product_closed() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    rendered = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 179; continuity graph revision 198" in rendered
    serialized = json.dumps(compass)
    assert "four-component HMAC resolution" in serialized
    assert "60-second" in serialized
    assert "application session" in serialized
    assert "product" in serialized


def test_user_decision_consumes_grant_gate_and_names_preauthorised_redeem() -> None:
    decisions = {
        item["id"]: item for item in _json(COMPASS)["user_owned_decisions"]
    }
    completed = decisions[
        "authorize-provider-free-oidc-binding-admission-grant-boundary"
    ]
    assert "Satisfied on 2026-08-02" in completed["required_before"]
    assert completed["evidence"]
    following = decisions[
        "authorize-provider-free-oidc-admission-grant-redemption-bridge"
    ]
    assert "Preauthorised by Yuri" in following["required_before"]
    assert "fresh five-source tranche rehydration" in following["required_before"]


def test_graph_evidence_excludes_branding_and_live_identity_claims() -> None:
    node = _json(GRAPH)["nodes"][-1]
    paths = [path for group in node["evidence"].values() for path in group]
    assert not any(path.startswith("docs/branding/") for path in paths)
    serialized = json.dumps(node)
    assert "No live Microsoft call" in serialized
    assert "application sessions" in serialized
    assert "product reads remain zero" in serialized
