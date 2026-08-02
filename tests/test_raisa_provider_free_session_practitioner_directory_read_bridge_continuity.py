from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass
from scripts.raisa_provider_free_session_practitioner_directory_read_bridge_continuity_update import (
    NODE,
)


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_bind_provider_free_product_read() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert graph["graph_revision"] == 200
    assert graph["nodes"][-1]["id"] == NODE
    assert graph["nodes"][-1]["relationships"] == [
        {
            "node_id": "raisa-provider-free-oidc-admission-grant-redemption-bridge",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] == 181
    assert compass["source_graph_revision"] == 200
    assert compass["current_position"]["node_id"] == NODE


def test_rendered_compass_validates_and_keeps_sensitive_authority_closed() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    result = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert result["status"] == "passed", result["reasons"]
    rendered = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 181; continuity graph revision 200" in rendered
    serialized = json.dumps(compass)
    assert "active-practitioner-directory" in serialized
    assert "required authorization audit" in serialized
    assert "patient/clinical" in serialized
    assert "unmounted" in serialized


def test_user_decision_records_selected_product_direction_and_next_gate() -> None:
    decisions = {
        item["id"]: item for item in _json(COMPASS)["user_owned_decisions"]
    }
    completed = decisions["choose-post-redemption-identity-or-product-direction"]
    assert "Satisfied on 2026-08-02" in completed["required_before"]
    assert "product-authorization" in completed["required_before"]
    assert completed["evidence"]
    following = decisions["authorize-provider-free-office-directory-consumer"]
    assert "taskpane consumer" in following["required_before"]


def test_graph_evidence_excludes_branding_provider_and_sensitive_claims() -> None:
    node = _json(GRAPH)["nodes"][-1]
    paths = [path for group in node["evidence"].values() for path in group]
    assert not any(path.startswith("docs/branding/") for path in paths)
    serialized = json.dumps(node)
    assert "No patient/clinical data" in serialized
    assert "Provider calls, real identities, patient/clinical reads" in serialized
