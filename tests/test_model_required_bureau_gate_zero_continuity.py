from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "model-required-bureau-gate-zero"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_gate_zero_remains_an_accepted_foundation_node() -> None:
    graph = _json(GRAPH)

    assert graph["graph_revision"] >= 209
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["id"] == NODE_ID
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == (
        "3727ee83d03d310bbb2f0d52c2ce70d0430ab65d"
    )
    assert node["relationships"] == [
        {
            "node_id": "model-required-bureau-standing-programme-authority",
            "relation": "builds_on",
        }
    ]
    assert node["contract_evidence"] == []
    assert node["authority"]["authorized_openings"][0]["boundary"] == (
        "autonomous-action"
    )
    assert node["evidence"]["acceptances"] == [
        "orchestration/agent_inbox/codex/"
        "model-required-bureau-gate-zero-sol-acceptance.md"
    ]
    assert (
        "orchestration/agent_inbox/antigravity/"
        "model-required-bureau-gate-zero-review-receipt.json"
        in node["evidence"]["receipts"]
    )


def test_gate_zero_compass_activates_exact_provider_free_successors() -> None:
    compass = _json(COMPASS)

    assert compass["map_revision"] >= 190
    assert compass["source_graph_revision"] >= 209
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    unlocks = journey["outcome"]
    for lane in ("A1/A2", "B1/B2", "C1/C2"):
        assert lane in unlocks
    decision = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"] == "authorize-model-required-bureau-gate-zero"
    )
    assert "Satisfied and consumed on 2026-08-04" in decision["required_before"]


def test_rendered_compass_names_gate_zero_and_runtime_claim_limit() -> None:
    report = REPORT.read_text(encoding="utf-8")

    assert "Model-Required Bureau Gate Zero Shared Contract" in report
    assert "Continuity 209 / Compass 190" in report
    assert "do not prove an operating cell" in report
