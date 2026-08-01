from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass, ariadne_continuity


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
AGENTS = ROOT / "AGENTS.md"
NODE = "raisa-maintained-oidc-verifier-session-bridge-architecture"
PARENT = "raisa-microsoft-federation-postgresql-persistence"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_graph_accepts_architecture_descendant() -> None:
    graph = _json(GRAPH)
    node = graph["nodes"][-1]
    assert graph["graph_revision"] == 192
    assert node["id"] == NODE
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {"node_id": PARENT, "relation": "builds_on"}
    ]
    assert ariadne_continuity.validate_graph(graph, repo_root=ROOT) == []


def test_graph_evidence_excludes_branding_and_runtime_wiring() -> None:
    node = _json(GRAPH)["nodes"][-1]
    evidence_paths = [
        path for paths in node["evidence"].values() for path in paths
    ]
    serialized = json.dumps(node, sort_keys=True)
    assert not any(path.startswith("docs/branding/") for path in evidence_paths)
    assert "No dependency" in serialized
    assert "real identity" in serialized
    assert "product read" in serialized
    assert "Protected integration" in serialized


def test_compass_and_report_bind_revisions_192_and_173() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert compass["map_revision"] == 173
    assert compass["source_graph_revision"] == 192
    assert compass["current_position"]["node_id"] == NODE
    assert compass["journey"][-1]["node_id"] == NODE
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert report["status"] == "passed"
    rendered = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 173" in rendered
    assert "continuity graph revision 192" in rendered


def test_completed_architecture_decision_leaves_dependency_gate_closed() -> None:
    decisions = {
        item["id"]: item for item in _json(COMPASS)["user_owned_decisions"]
    }
    completed = decisions[
        "authorize-maintained-oidc-verifier-session-bridge-architecture"
    ]
    assert "Satisfied on 2026-08-02" in completed["required_before"]
    next_gate = decisions["authorize-msal-offline-adapter-dependency-tranche"]
    assert "package/dependency addition" in next_gate["required_before"]
    assert "Live network" in next_gate["required_before"]


def test_live_handover_records_exact_result_and_closed_gates() -> None:
    handover = AGENTS.read_text(encoding="utf-8")
    for marker in (
        "Maintained OIDC verifier and session-bridge architecture acceptance",
        "raisa_maintained_oidc_verifier_session_bridge_architecture_pass",
        "Continuity graph revision 192",
        "Compass map revision 173",
        "provider-free maintained-verifier dependency and offline adapter-admission",
        "No further Pages rebuild is authorised",
    ):
        assert marker in handover
    assert "Yuri's branding permission covers future UI renders only" in handover

