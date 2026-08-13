from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-status-confirm-http-route-convergence"
SOURCE_HEAD = "b414eb256853c301099d9cf7797a69cd3ec077c5"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_status_confirm_http_convergence_remains_accepted() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    nodes = {node["id"]: node for node in graph["nodes"]}
    journeys = {item["node_id"]: item for item in compass["journey"]}

    assert graph["graph_revision"] >= 273
    assert compass["map_revision"] >= 255
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert nodes[NODE_ID]["status"] == "accepted"
    assert nodes[NODE_ID]["coordinates"]["source_head"] == SOURCE_HEAD
    assert NODE_ID in journeys


def test_status_confirm_http_convergence_preserves_closed_boundaries() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()

    for phrase in (
        "waiting-area-only",
        "other command families",
        "cf-d2",
        "product/patient data",
        "providers",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_status_confirm_http_evidence_and_next_ui_direction_are_bound() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {
        item
        for values in node["evidence"].values()
        for item in values
    }

    assert {
        "docs/raisa-provider-free-status-confirm-http-route-convergence-closeout.md",
        "orchestration/agent_inbox/codex/raisa-status-confirm-http-route-convergence-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--status-confirm-http-route-convergence.md",
        "orchestration/continuity/raisa-provider-free-status-confirm-http-route-convergence/provider-free-http-postgresql-evidence.json",
    } <= evidence
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "visible native diary" in " ".join(
        compass["current_position"]["unlocks"]
    ).lower()
    assert "paused" in compass["current_position"]["strategic_role"].lower()
    assert "observability-first" in compass["orientation_statement"].lower()
