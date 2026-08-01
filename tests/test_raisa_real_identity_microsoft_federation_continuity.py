from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass, ariadne_continuity


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
AGENTS = ROOT / "AGENTS.md"
NODE_IDS = [
    "raisa-real-identity-microsoft-federation-boundary",
    "raisa-microsoft-federation-admission-runtime",
    "raisa-microsoft-federation-postgresql-persistence",
]


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_graph_accepts_exact_three_node_sequence() -> None:
    graph = _json(GRAPH)
    assert graph["graph_revision"] == 191
    assert [item["id"] for item in graph["nodes"][-3:]] == NODE_IDS
    assert graph["nodes"][-3]["relationships"] == [
        {
            "node_id": (
                "raisa-shared-application-auth-postgresql-office-host-compatibility"
            ),
            "relation": "builds_on",
        }
    ]
    assert graph["nodes"][-2]["relationships"] == [
        {"node_id": NODE_IDS[0], "relation": "builds_on"}
    ]
    assert graph["nodes"][-1]["relationships"] == [
        {"node_id": NODE_IDS[1], "relation": "builds_on"}
    ]
    assert all(item["status"] == "accepted" for item in graph["nodes"][-3:])
    assert ariadne_continuity.validate_graph(graph, repo_root=ROOT) == []


def test_compass_current_position_and_report_bind_revision_172() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert compass["map_revision"] == 172
    assert compass["source_graph_revision"] == 191
    assert compass["current_position"]["node_id"] == NODE_IDS[-1]
    assert [item["node_id"] for item in compass["journey"][-3:]] == NODE_IDS
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert report["status"] == "passed"
    rendered = REPORT.read_text(encoding="utf-8")
    assert "Compass map revision 172" in rendered
    assert "continuity graph revision 191" in rendered


def test_user_decisions_consume_three_tranches_and_leave_next_gate_closed() -> None:
    decisions = {
        item["id"]: item for item in _json(COMPASS)["user_owned_decisions"]
    }
    assert "Satisfied on 2026-08-01" in decisions[
        "authorize-real-identity-federation-architecture"
    ]["required_before"]
    assert "Satisfied on 2026-08-01" in decisions[
        "authorize-microsoft-federation-synthetic-admission-runtime"
    ]["required_before"]
    assert "Satisfied on 2026-08-01" in decisions[
        "authorize-microsoft-federation-postgresql-persistence"
    ]["required_before"]
    next_gate = decisions[
        "authorize-maintained-oidc-verifier-session-bridge-architecture"
    ]
    assert "Any live Microsoft" in next_gate["required_before"]
    assert "session issuance" in next_gate["required_before"]


def test_graph_evidence_preserves_branding_and_live_identity_exclusions() -> None:
    graph = _json(GRAPH)
    nodes = {item["id"]: item for item in graph["nodes"]}
    serialized = json.dumps([nodes[item] for item in NODE_IDS], sort_keys=True)
    evidence_paths = [
        path
        for node_id in NODE_IDS
        for paths in nodes[node_id]["evidence"].values()
        for path in paths
    ]
    assert not any(path.startswith("docs/branding/") for path in evidence_paths)
    for node_id in NODE_IDS:
        node = nodes[node_id]
        assert node["authority"]["authorized_openings"][0]["boundary"] == "api-change"
        assert node["evidence"]["acceptances"]
        assert node["unresolved_gates"]
    assert "Live Microsoft" in serialized
    assert "product" in serialized
    assert "deployment" in serialized


def test_live_handover_names_results_and_next_authority_gate() -> None:
    handover = AGENTS.read_text(encoding="utf-8")
    for result in (
        "Real-identity and Microsoft-federation three-tranche acceptance",
        "docs/raisa-microsoft-federation-admission-runtime-closeout.md",
        "docs/raisa-microsoft-federation-postgresql-persistence-closeout.md",
        "Continuity graph revision 191",
        "Compass map revision 172",
        "architecture-only maintained OIDC library verifier",
        "new public GitHub Pages deployment",
    ):
        assert result in handover
    assert "Yuri's branding permission covers future UI renders only" in handover
