from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass
from scripts.raisa_provider_free_oidc_admission_grant_redemption_bridge_continuity_update import (
    NODE,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_bind_atomic_redemption_bridge() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert graph["graph_revision"] == 199
    assert graph["nodes"][-1]["id"] == NODE
    assert graph["nodes"][-1]["relationships"] == [
        {
            "node_id": "raisa-provider-free-oidc-binding-admission-grant-boundary",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] == 180
    assert compass["source_graph_revision"] == 199
    assert compass["current_position"]["node_id"] == NODE


def test_rendered_compass_validates_and_keeps_real_product_authority_closed() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    rendered = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 180; continuity graph revision 199" in rendered
    serialized = json.dumps(compass)
    assert "atomic grant consumption" in serialized
    assert "post-commit cookies" in serialized
    assert "real identity" in serialized
    assert "product authorization" in serialized


def test_user_decision_consumes_redeem_gate_and_stops_at_material_fork() -> None:
    decisions = {
        item["id"]: item for item in _json(COMPASS)["user_owned_decisions"]
    }
    completed = decisions[
        "authorize-provider-free-oidc-admission-grant-redemption-bridge"
    ]
    assert "Satisfied on 2026-08-02" in completed["required_before"]
    assert completed["evidence"]
    following = decisions[
        "choose-post-redemption-identity-or-product-direction"
    ]
    assert "material direction choice" in following["required_before"]


def test_graph_evidence_excludes_branding_provider_and_product_claims() -> None:
    node = _json(GRAPH)["nodes"][-1]
    paths = [path for group in node["evidence"].values() for path in group]
    assert not any(path.startswith("docs/branding/") for path in paths)
    serialized = json.dumps(node)
    assert "No live Microsoft call" in serialized
    assert "Provider calls, real identities and product reads remain zero" in serialized
