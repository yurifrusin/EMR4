from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "model-required-bureau-standing-programme-authority"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_standing_authority_remains_an_accepted_maintenance_node() -> None:
    graph = _json(GRAPH)

    assert graph["graph_revision"] >= 208
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["id"] == NODE_ID
    assert node["kind"] == "maintenance"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == (
        "ba6a96d55002ee7713c3a12867e57b41ce972150"
    )
    assert node["relationships"] == [
        {
            "node_id": "model-required-bureau-gate-minus-one",
            "relation": "builds_on",
        }
    ]
    assert node["contract_evidence"] == []
    assert node["authority"]["authorized_openings"][0]["boundary"] == (
        "autonomous-action"
    )
    assert node["evidence"]["acceptances"] == [
        "orchestration/agent_inbox/codex/"
        "model-required-bureau-standing-programme-authority-sol-acceptance.md"
    ]
    assert any("Gate zero must pass" in gate for gate in node["unresolved_gates"])


def test_compass_binds_standing_authority_and_satisfies_gate_zero_decision() -> None:
    compass = _json(COMPASS)

    assert compass["map_revision"] >= 189
    assert compass["source_graph_revision"] >= 208
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])
    decision = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"] == "authorize-model-required-bureau-gate-zero"
    )
    assert "Satisfied" in decision["required_before"]
    assert "Satisfied" in decision["required_before"]


def test_rendered_compass_names_standing_authority_and_claim_limit() -> None:
    report = REPORT.read_text(encoding="utf-8")

    assert "Standing Programme Continuation Authority" in report
    assert "Continuity 209 / Compass 190" in report
    assert "does not infer or erase an unresolved material boundary" in report
