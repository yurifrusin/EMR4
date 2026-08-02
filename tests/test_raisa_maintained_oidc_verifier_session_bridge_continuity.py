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
    node = next(item for item in graph["nodes"] if item["id"] == NODE)
    assert graph["graph_revision"] >= 192
    assert node["id"] == NODE
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {"node_id": PARENT, "relation": "builds_on"}
    ]
    assert ariadne_continuity.validate_graph(graph, repo_root=ROOT) == []


def test_graph_evidence_excludes_branding_and_runtime_wiring() -> None:
    node = next(item for item in _json(GRAPH)["nodes"] if item["id"] == NODE)
    evidence_paths = [
        path for paths in node["evidence"].values() for path in paths
    ]
    serialized = json.dumps(node, sort_keys=True)
    assert not any(path.startswith("docs/branding/") for path in evidence_paths)
    assert "No dependency" in serialized
    assert "real identity" in serialized
    assert "product read" in serialized
    assert "Protected integration" in serialized


def test_compass_and_report_preserve_parent_journey_after_revision_192() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert compass["map_revision"] >= 173
    assert compass["source_graph_revision"] >= 192
    assert any(item["node_id"] == NODE for item in compass["journey"])
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert report["status"] == "passed"
    rendered = REPORT.read_text(encoding="utf-8")
    assert f"Compass map revision {compass['map_revision']}" in rendered
    assert f"continuity graph revision {graph['graph_revision']}" in rendered


def test_completed_architecture_adapter_and_attempt_store_leave_runtime_edges_closed() -> None:
    decisions = {
        item["id"]: item for item in _json(COMPASS)["user_owned_decisions"]
    }
    completed = decisions[
        "authorize-maintained-oidc-verifier-session-bridge-architecture"
    ]
    assert "Satisfied on 2026-08-02" in completed["required_before"]
    next_gate = decisions["authorize-msal-offline-adapter-dependency-tranche"]
    assert "Satisfied on 2026-08-02" in next_gate["required_before"]
    adapter_gate = decisions["authorize-two-component-oidc-runtime-adapter"]
    assert "Satisfied on 2026-08-02" in adapter_gate["required_before"]
    database_gate = decisions[
        "authorize-provider-free-postgresql-authorization-attempt-store"
    ]
    assert "Satisfied on 2026-08-02" in database_gate["required_before"]
    assert "live Microsoft" in database_gate["required_before"]
    operational_gate = decisions[
        "authorize-postgresql-oidc-attempt-store-operational-connection-boundary"
    ]
    assert "Satisfied on 2026-08-02" in operational_gate["required_before"]
    assert "live Microsoft" in operational_gate["required_before"]
    transport_gate = decisions[
        "authorize-provider-free-oidc-start-callback-transport-boundary"
    ]
    assert "mounted OIDC start/callback route" in transport_gate["required_before"]


def test_live_handover_records_exact_result_and_closed_gates() -> None:
    handover = AGENTS.read_text(encoding="utf-8")
    for marker in (
        "Maintained OIDC verifier and session-bridge architecture acceptance",
        "Two-component OIDC verifier architecture revision acceptance",
        "Two-component OIDC runtime adapter acceptance",
        "PostgreSQL OIDC authorization-attempt store acceptance",
        "postgresql_oidc_operational_connection_boundary_pass",
        "Continuity graph revision 196",
        "Compass map revision 177",
        "PostgreSQL OIDC operational connection boundary acceptance",
        "any further Pages rebuild remain closed",
    ):
        assert marker in handover
    assert "Yuri's branding permission covers future UI renders only" in handover
