from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "model-required-bureau-gate-minus-one"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_gate_minus_one_remains_an_accepted_review_node() -> None:
    graph = _json(GRAPH)

    assert graph["graph_revision"] >= 207
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["id"] == NODE_ID
    assert node["kind"] == "review"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == (
        "2b62f040bcc1c300dca6fb730e0f986d22f3be85"
    )
    assert node["relationships"] == [
        {
            "node_id": "raisa-provider-free-default-off-office-consumer-adapter",
            "relation": "builds_on",
        }
    ]
    assert node["contract_evidence"] == []
    assert any("Gate zero requires fresh Yuri authority" in gate for gate in node["unresolved_gates"])


def test_compass_preserves_gate_minus_one_and_records_gate_zero_decision() -> None:
    compass = _json(COMPASS)

    assert compass["map_revision"] >= 188
    assert compass["source_graph_revision"] >= 207
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])
    decision = next(
        item
        for item in compass["user_owned_decisions"]
        if item["id"] == "authorize-model-required-bureau-gate-zero"
    )
    assert decision["required_before"]


def test_rendered_compass_names_gate_and_claim_limit() -> None:
    report = REPORT.read_text(encoding="utf-8")

    assert "Model-Required Bureau Gate -1 Adversarial Architecture Review" in report
    assert "not implemented" in report
