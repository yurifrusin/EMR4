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
    assert graph["graph_revision"] >= 191
    ids = [item["id"] for item in graph["nodes"]]
    start = ids.index(NODE_IDS[0])
    sequence = graph["nodes"][start : start + 3]
    assert [item["id"] for item in sequence] == NODE_IDS
    assert sequence[0]["relationships"] == [
        {
            "node_id": (
                "raisa-shared-application-auth-postgresql-office-host-compatibility"
            ),
            "relation": "builds_on",
        }
    ]
    assert sequence[1]["relationships"] == [
        {"node_id": NODE_IDS[0], "relation": "builds_on"}
    ]
    assert sequence[2]["relationships"] == [
        {"node_id": NODE_IDS[1], "relation": "builds_on"}
    ]
    assert all(item["status"] == "accepted" for item in sequence)
    assert ariadne_continuity.validate_graph(graph, repo_root=ROOT) == []


def test_compass_journey_preserves_revision_172_federation_sequence() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    assert compass["map_revision"] >= 172
    assert compass["source_graph_revision"] >= 191
    journey_ids = [item["node_id"] for item in compass["journey"]]
    start = journey_ids.index(NODE_IDS[0])
    assert journey_ids[start : start + 3] == NODE_IDS
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    assert report["status"] == "passed"
    rendered = REPORT.read_text(encoding="utf-8")
    assert f"Compass map revision {compass['map_revision']}" in rendered
    assert f"continuity graph revision {graph['graph_revision']}" in rendered


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
    architecture_gate = decisions[
        "authorize-maintained-oidc-verifier-session-bridge-architecture"
    ]
    assert "Satisfied on 2026-08-02" in architecture_gate["required_before"]
    next_gate = decisions["authorize-msal-offline-adapter-dependency-tranche"]
    assert "package/dependency addition" in next_gate["required_before"]
    assert "Live network" in next_gate["required_before"]


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
        "Continuity graph revision 192",
        "Compass map revision 173",
        "provider-free maintained-verifier dependency and offline adapter-admission",
        "09a661cfa83559b13c438f45734403f33d1e3bbb",
        "No further Pages rebuild is authorised",
    ):
        assert result in handover
    assert "Yuri's branding permission covers future UI renders only" in handover
